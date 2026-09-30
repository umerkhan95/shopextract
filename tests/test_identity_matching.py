"""Epic #21: stable identities, conservative reports and snapshot continuity."""
import importlib
import json
from dataclasses import asdict
from decimal import Decimal
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from shopextract import (
    ExtractionResult, Product, Variant, assign_identity, classify_match,
    match_products, migrate_snapshot_identities, normalize, price_history, changes,
)
from shopextract.compare.catalog import _diff_catalogs
from shopextract.compare.evaluation import evaluate_matching
from shopextract.compare.identity_match import MatchRelation as R
from shopextract.identity import identify_records
from shopextract.monitor.snapshot import _get_connection


def test_ids_survive_rename_and_scope_skus():
    a = assign_identity(Product(title="Old", external_id="123", sku="LOCAL", variants=[Variant(variant_id="8")]), "https://SHOP.example/")
    b = assign_identity(Product(title="New", external_id="123", sku="LOCAL", variants=[Variant(variant_id="8", title="New option")]), "shop.example")
    assert a.canonical_product_id == b.canonical_product_id
    assert a.variants[0].canonical_variant_id == b.variants[0].canonical_variant_id
    assert a.canonical_product_id != assign_identity(Product(sku="LOCAL", external_id="123"), "other.example").canonical_product_id
    assert assign_identity(Product(sku="LOCAL"), "shop.example").canonical_product_id != assign_identity(Product(sku="LOCAL"), "other.example").canonical_product_id


def test_identifier_free_records_are_not_hashed_by_title():
    a = assign_identity(Product(title="Same"), "shop.example")
    b = assign_identity(Product(title="Same"), "shop.example")
    assert a.canonical_product_id != b.canonical_product_id


def test_variant_source_ids_are_scoped_by_parent():
    a = assign_identity(Product(external_id="a", variants=[Variant(variant_id="1")]), "shop.example")
    b = assign_identity(Product(external_id="b", variants=[Variant(variant_id="1")]), "shop.example")
    assert a.variants[0].canonical_variant_id != b.variants[0].canonical_variant_id


def test_url_identity_preserves_variant_query_ignores_tracking():
    a = assign_identity(Product(product_url="https://s.example/p?variant=8&utm_source=x"))
    b = assign_identity(Product(product_url="https://s.example/p?variant=8&utm_source=y"))
    c = assign_identity(Product(product_url="https://s.example/p?variant=16"))
    assert a.canonical_product_id == b.canonical_product_id
    assert a.canonical_product_id != c.canonical_product_id


def test_normalize_assigns_identity_and_attributes():
    a = normalize({"title": "Old", "id": "1", "price": "10", "attributes": {"memory": "8 GB"}}, shop_url="https://s.example")
    b = normalize({"title": "New", "id": "1", "price": "15"}, shop_url="https://s.example")
    assert a.canonical_product_id == b.canonical_product_id
    assert a.attributes == {"memory": "8 GB"}


@pytest.mark.parametrize("a,b,relation", [
    ({"title": "Laptop 8GB", "gtin": "4006381333931"}, {"title": "Laptop 16GB", "gtin": "4006381333931"}, R.VARIANT),
    ({"title": "Soap single", "gtin": "4006381333931"}, {"title": "Soap 6-pack", "gtin": "4006381333931"}, R.BUNDLE),
    ({"title": "Widget", "pack_quantity": 1}, {"title": "Widget", "pack_quantity": 6}, R.BUNDLE),
    ({"title": "Widget", "sku": "123", "supplier_id": "a"}, {"title": "Widget", "sku": "123", "supplier_id": "b"}, R.UNCERTAIN),
    ({"title": "Renamed", "gtin": "4006381333931"}, {"title": "Original", "gtin": "4006381333931"}, R.EXACT),
    ({"title": "Widget", "gtin": "4006381333932"}, {"title": "Widget", "gtin": "4006381333932"}, R.UNCERTAIN),
    ({"title": "Widget", "gtin": "4006381333931", "attributes": {"color": "Blue"}}, {"title": "Widget", "gtin": "4006381333931"}, R.UNCERTAIN),
    ({"title": ""}, {"title": ""}, R.UNMATCHED),
    ({"title": "Apples", "product_type": "Food", "attributes": {"purpose": "snack"}}, {"title": "Oranges", "product_type": "Food", "attributes": {"purpose": "snack"}}, R.SUBSTITUTE),
])
def test_classification_guards(a, b, relation):
    d = classify_match(a, b)
    assert d.relation == relation
    assert d.needs_review == (relation not in {R.EXACT, R.UNMATCHED})


def test_parent_variant_sets_prevent_false_exact():
    a = Product(title="Laptop", gtin="4006381333931", variants=[Variant(title="8GB"), Variant(title="16GB")])
    b = Product(title="Laptop", gtin="4006381333931", variants=[Variant(title="8GB")])
    assert classify_match(a, b).relation != R.EXACT


def test_exact_before_semantics_and_ambiguity_review():
    calls = []
    def semantic(a, bs):
        calls.append(a)
        return [0]
    report = match_products([{"title": "A", "gtin": "4006381333931"}], [{"title": "B", "gtin": "4006381333931"}], semantic_candidates=semantic)
    assert report[0].relation == R.EXACT and calls == []
    report = match_products([{"title": "A", "gtin": "4006381333931"}] * 2, [{"title": "B", "gtin": "4006381333931"}])
    assert all(d.needs_review and d.relation == R.UNCERTAIN for d in report)
    report = match_products([{"title": "Apple"}], [{"title": "Drill"}], semantic_candidates=semantic)
    assert report[0].candidate_method == "semantic" and report[0].needs_review
    assert len(calls) == 1


def test_catalog_only_prices_exact_and_same_currency():
    a = Product(title="Laptop 8GB", gtin="4006381333931", price=Decimal("10"))
    b = Product(title="Laptop 16GB", gtin="4006381333931", price=Decimal("20"))
    diff = _diff_catalogs("a", "b", [a], [b], 0.8)
    assert not diff.in_both and diff.match_report[0].relation == R.VARIANT
    b.title = a.title
    b.currency = "EUR"
    diff = _diff_catalogs("a", "b", [a], [b], 0.8)
    assert len(diff.in_both) == 1 and not diff.cheaper_in_a


def _insert(conn, products, ts):
    conn.execute("INSERT INTO snapshots(domain,products_json,created_at) VALUES(?,?,?)", ("s.example", json.dumps(products), ts))
    conn.commit()


def test_legacy_rename_migration_is_idempotent_and_history_uses_both_titles(tmp_path):
    path = str(tmp_path / "snapshots.db")
    conn = _get_connection(path)
    _insert(conn, [{"title": "Old", "external_id": "1", "price": "10"}], "2026-01-01")
    _insert(conn, [{"title": "New", "external_id": "1", "price": "15"}], "2026-01-02")
    with conn:
        assert migrate_snapshot_identities(conn) == 2
    with conn:
        assert migrate_snapshot_identities(conn) == 0
    records = [json.loads(row[0])[0] for row in conn.execute("SELECT products_json FROM snapshots ORDER BY id")]
    assert records[0]["canonical_product_id"] == records[1]["canonical_product_id"]
    conn.close()
    detected = changes("s.example", db_path=path)
    assert len(detected) == 1 and detected[0].title == "New"
    for title in ("Old", "New"):
        assert [price for _, price in price_history("s.example", title, db_path=path)] == [10, 15]
    assert len(price_history("s.example", canonical_product_id=records[0]["canonical_product_id"], db_path=path)) == 2


def test_ambiguous_title_requires_id_and_duplicates_rollback(tmp_path):
    path = str(tmp_path / "snapshots.db")
    conn = _get_connection(path)
    _insert(conn, [{"title": "Same", "external_id": "1", "price": "10"}, {"title": "Same", "external_id": "2", "price": "20"}], "2026-01-01")
    conn.close()
    with pytest.raises(ValueError, match="Ambiguous"):
        price_history("s.example", "Same", db_path=path)
    conn = _get_connection(path)
    with pytest.raises(ValueError, match="Duplicate"), conn:
        identify_records(conn, [{"external_id": "3"}, {"external_id": "3"}], "s.example")
    assert not conn.execute("SELECT * FROM identity_aliases WHERE value='3'").fetchall()
    conn.close()


def test_conflicting_aliases_stop_migration(tmp_path):
    conn = _get_connection(str(tmp_path / "s.db"))
    with conn:
        identify_records(conn, [{"external_id": "1", "sku": "a"}, {"external_id": "2", "sku": "b"}], "s.example")
    with pytest.raises(ValueError, match="Conflicting"), conn:
        identify_records(conn, [{"external_id": "1", "sku": "b"}], "s.example")
    conn.close()


@pytest.mark.asyncio
async def test_end_to_end_normalize_snapshot_rename_and_history(tmp_path, monkeypatch):
    module = importlib.import_module("shopextract.monitor.snapshot")
    path = str(tmp_path / "s.db")
    old = normalize({"title": "Laptop 8GB", "id": "1", "price": "10"}, shop_url="https://s.example")
    new = normalize({"title": "Renamed laptop 8GB", "id": "1", "price": "15"}, shop_url="https://s.example")
    monkeypatch.setattr(module, "extract", AsyncMock(side_effect=[ExtractionResult(products=[old]), ExtractionResult(products=[new])]))
    assert await module.snapshot("https://s.example", db_path=path) == 1
    assert await module.snapshot("https://s.example", db_path=path) == 1
    assert len(changes("s.example", db_path=path)) == 1
    assert [p for _, p in price_history("s.example", "Renamed laptop 8GB", db_path=path)] == [10, 15]


def test_labeled_evaluation_acceptance():
    rows = json.loads((Path(__file__).parent / "fixtures/matching_evaluation.json").read_text())
    report = evaluate_matching(rows)
    assert report["passed"], report
    assert report["false_exact"] == 0
    assert report["precision"] == 1.0 and report["coverage"] >= 0.8
    assert report["total_pairs"] >= 30


def test_legacy_candidates_do_not_match_conflicting_variants_or_packs():
    from shopextract import fuzzy_match
    from shopextract.compare.price import _collect_matches
    assert not fuzzy_match([{"title": "Laptop 8GB"}], [{"title": "Laptop 16GB"}], threshold=0.6)
    assert not fuzzy_match([{"title": "Soap", "pack_quantity": 1}], [{"title": "Soap", "pack_quantity": 6}])
    result = ExtractionResult(products=[Product(title="Laptop 16GB", price=Decimal("10"))])
    assert not _collect_matches("Laptop 8GB", ["s.example"], [result], 0.6)


def test_exact_targets_are_ambiguous_and_invalid_semantic_indices_rejected():
    a = {"gtin": "4006381333931"}
    decisions = match_products([a], [a, a])
    assert len(decisions) == 2 and all(d.needs_review for d in decisions)
    with pytest.raises(ValueError, match="index"):
        match_products([{"title": "Apple"}], [{"title": "Drill"}], semantic_candidates=lambda a, bs: [7])


def test_legacy_title_bridge_only_for_identifier_free_records(tmp_path):
    conn = _get_connection(str(tmp_path / "s.db"))
    records = [{"title": "Widget"}]
    with conn:
        identify_records(conn, records, "s.example", legacy_titles=True)
    promoted = [{"title": "Widget", "external_id": "42"}]
    with conn:
        identify_records(conn, promoted, "s.example", legacy_titles=True)
    assert records[0]["canonical_product_id"] == promoted[0]["canonical_product_id"]
    renamed = [{"title": "New", "external_id": "42"}]
    with conn:
        identify_records(conn, renamed, "s.example")
    assert renamed[0]["canonical_product_id"] == records[0]["canonical_product_id"]
    conn.close()


def test_platform_enum_and_serialized_record_share_identity(tmp_path):
    from shopextract import Platform
    p = assign_identity(Product(external_id="42", platform=Platform.SHOPIFY), "s.example")
    conn = _get_connection(str(tmp_path / "s.db"))
    record = {"external_id": "42", "platform": "shopify"}
    with conn:
        identify_records(conn, [record], "s.example")
    assert p.canonical_product_id == record["canonical_product_id"]
    conn.close()


def test_capacity_roles_are_not_interchangeable():
    a = {"title": "Laptop 8GB RAM 16GB SSD", "gtin": "4006381333931"}
    b = {"title": "Laptop 16GB RAM 8GB SSD", "gtin": "4006381333931"}
    assert classify_match(a, b).relation == R.VARIANT


def test_same_title_different_products_do_not_collapse_in_monitoring(tmp_path):
    path = str(tmp_path / "s.db")
    conn = _get_connection(path)
    _insert(conn, [{"title": "Same", "external_id": "1", "price": "10"}, {"title": "Same", "external_id": "2", "price": "20"}], "2026-01-01")
    _insert(conn, [{"title": "Same", "external_id": "1", "price": "12"}, {"title": "Same", "external_id": "2", "price": "20"}], "2026-01-02")
    conn.close()
    events = changes("s.example", db_path=path)
    assert len(events) == 1 and events[0].old_price == Decimal("10") and events[0].new_price == Decimal("12")


def test_semantic_callback_not_called_for_attribute_candidates():
    report = match_products([{"title": "Laptop 8GB"}], [{"title": "Laptop 16GB"}], semantic_candidates=lambda a, bs: pytest.fail("unnecessary semantic call"))
    assert report[0].relation == R.VARIANT


def test_generic_title_search_still_returns_variant_candidates():
    from shopextract.compare.price import _collect_matches
    result = ExtractionResult(products=[Product(title="Laptop 8GB", attributes={"memory": "8GB"})])
    assert len(_collect_matches("Laptop", ["s.example"], [result], 0.6)) == 1


def test_promoted_legacy_title_cannot_attach_a_new_source_record(tmp_path):
    conn = _get_connection(str(tmp_path / "s.db"))
    old = [{"title": "Widget"}]
    promoted = [{"title": "Widget", "external_id": "1"}]
    replacement = [{"title": "Widget", "external_id": "2"}]
    with conn:
        identify_records(conn, old, "s.example", legacy_titles=True)
        identify_records(conn, promoted, "s.example", legacy_titles=True)
        identify_records(conn, replacement, "s.example", legacy_titles=True)
    assert old[0]["canonical_product_id"] == promoted[0]["canonical_product_id"]
    assert replacement[0]["canonical_product_id"] != old[0]["canonical_product_id"]
    conn.close()
