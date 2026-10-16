"""Bounded, offline production acceptance checks for #37–#39."""
from datetime import timedelta
from decimal import Decimal
import importlib.util
import json
from pathlib import Path
import socket

import pytest

from shopextract import Platform, Product, Variant
from shopextract._portable import product_to_record
from shopextract._evidence import ValidatedConfidence
from shopextract._resolution import resolve_fields
from shopextract.export._bundle import create_evidence_bundle, load_evidence_bundle
from shopextract.monitor.evidence import save_snapshot, load_snapshot, get_evidence, prune_evidence

_spec = importlib.util.spec_from_file_location('evidence_trust_example', Path(__file__).parents[1] / 'examples/evidence_trust.py')
demo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(demo)


@pytest.fixture(autouse=True)
def offline_only(monkeypatch):
    def fail(*args, **kwargs):
        raise AssertionError('The evidence acceptance workflow must stay offline')
    monkeypatch.setattr(socket, 'create_connection', fail)
    monkeypatch.setattr(socket.socket, 'connect', fail)


def round_trip(products, tmp_path):
    db = str(tmp_path / 'test.db')
    snapshot_id = save_snapshot(products, 'supplier.example', db_path=db)
    restored = load_snapshot(snapshot_id, db_path=db)
    imported = load_evidence_bundle(json.loads(json.dumps(create_evidence_bundle(restored), allow_nan=False)))
    assert [product_to_record(p) for p in products] == [product_to_record(p) for p in imported]
    return imported, db, snapshot_id


def test_trust_e2e_extract_restart_bundle(tmp_path):
    result = demo.run_demo(tmp_path)
    assert result['factual_paths'] == sum(result['states'].values())
    assert result['retrievable_observed'] == result['states']['observed'] > 0
    assert Path(result['bundle']).is_file()
    assert json.loads((tmp_path / 'report.json').read_text())['as_of'] == demo.AS_OF.isoformat()


def test_trust_e2e_missing_and_literal_values(tmp_path):
    products, _, _ = round_trip(demo.fixture_products(), tmp_path)
    zero, _, missing = products
    assert zero.trust_view()['/price']['value'] == Decimal('0')
    assert zero.trust_view()['/in_stock']['value'] is False
    for field in ('/price', '/currency', '/in_stock'):
        assert missing.trust_view()[field]['state'] in ('unsupported', 'unknown')
        assert missing.trust_view()[field]['value'] is None
        assert missing.trust_view()[field]['reason']


def test_trust_e2e_nested_and_transformed(tmp_path):
    products, _, _ = round_trip(demo.fixture_products(), tmp_path)
    product = products[1]
    assert isinstance(product, Product) and isinstance(product.platform, Platform)
    assert isinstance(product.variants[0], Variant)
    assert str(product.price) == '1.2300'
    assert product.scraped_at == demo.AS_OF and product.scraped_at.microsecond == 123456
    assert product.raw_data['literal'] == {'$type': 'decimal', 'value': 'literal text'}
    observation = next(o for o in product.evidence_contract.observations if o.field_path == '/variants/0/gtin')
    assert observation.raw_value == '29877030712'
    assert 'restore_upc_leading_zero' in observation.transformations
    assert product.variants[0].gtin == '0029877030712'
    escaped = [e for e in product.evidence_contract.evidence if e.pointer == '/a~1b~0c']
    assert {e.resolve_pointer() for e in escaped} == {'red', 'blue'}


def test_trust_e2e_conflicts(tmp_path):
    products = demo.fixture_products()
    before = products[1].evidence_contract.to_dict()
    imported, _, _ = round_trip(products, tmp_path)
    assert imported[1].evidence_contract.to_dict() == before
    field = imported[1].trust_view()['/attributes/a~1b~0c']
    assert field['value'] == 'blue' and len(field['observation_ids']) == 2
    assert 'authority' in field['reason']
    # Equal-role disagreements remain unresolved, with every candidate preserved.
    product = imported[1]
    for evidence in product.evidence_contract.evidence:
        evidence.source_role = 'supplier'
    product.evidence_contract = resolve_fields(product.evidence_contract, as_of=demo.AS_OF)
    tied = load_evidence_bundle(create_evidence_bundle([product]))[0].trust_view()['/attributes/a~1b~0c']
    assert tied['state'] == 'conflicting' and tied['value'] is None
    assert len(tied['observation_ids']) == 2


def test_trust_e2e_unverified_llm_score(tmp_path):
    products = demo.fixture_products()
    supported = next(o for o in products[0].evidence_contract.observations if o.field_path == '/price')
    supported.validated_confidence = ValidatedConfidence(0.8, 'synthetic-metadata', 'fixture-only', '1')
    imported, _, _ = round_trip(products, tmp_path)
    observation = next(o for o in imported[2].evidence_contract.observations if o.field_path == '/description')
    assert observation.state == 'unsupported'
    assert observation.score == 0.98 and observation.score_kind == 'model'
    assert observation.validated_confidence is None
    assert imported[2].trust_view()['/description']['value'] is None
    restored = next(o for o in imported[0].evidence_contract.observations if o.field_path == '/price')
    assert restored.validated_confidence == supported.validated_confidence


def test_trust_e2e_legacy_and_restricted_export(tmp_path):
    from dataclasses import asdict
    from shopextract.export import to_csv
    from shopextract.export._bundle import load_evidence_sidecar
    legacy = Product(title='Legacy', price=Decimal('7.00'), sku='legacy')
    db = str(tmp_path / 'legacy.db')
    sid = save_snapshot([legacy], 'legacy.example', db_path=db)
    restored = load_snapshot(sid, db_path=db)[0]
    assert restored.price == legacy.price
    assert restored.trust_view()['/price']['state'] == 'unsupported'
    products = demo.fixture_products()
    ordinary, paired = tmp_path / 'ordinary.csv', tmp_path / 'paired.csv'
    sidecar = tmp_path / 'paired.evidence.json'
    to_csv([asdict(p) for p in products], str(ordinary))
    to_csv(products, str(paired), evidence_path=str(sidecar))
    assert ordinary.read_bytes() == paired.read_bytes()
    loaded = load_evidence_sidecar(json.loads(sidecar.read_text()), paired.read_bytes())
    assert [product_to_record(p) for p in loaded] == [product_to_record(p) for p in products]
    with pytest.raises(ValueError):
        load_evidence_sidecar(json.loads(sidecar.read_text()), paired.read_bytes() + b'\n')


def test_trust_e2e_expiry_and_pruning(tmp_path):
    products = demo.fixture_products()
    db = str(tmp_path / 'expiry.db')
    snapshot_id = save_snapshot(products, 'supplier.example', db_path=db)
    evidence_id = products[0].evidence_contract.evidence[0].evidence_id
    before = demo.AS_OF + timedelta(days=1)
    prune_evidence(db_path=db, before=before, dry_run=True, protect_references=False)
    assert get_evidence(evidence_id, snapshot_id=snapshot_id, record_key='product/0', db_path=db).status == 'available'
    prune_evidence(db_path=db, before=before, dry_run=False)
    assert get_evidence(evidence_id, db_path=db).status == 'available'
    prune_evidence(db_path=db, before=before, dry_run=False, protect_references=False)
    assert get_evidence(evidence_id, db_path=db).status == 'expired'
    restored = load_snapshot(snapshot_id, db_path=db)
    imported = load_evidence_bundle(json.loads(json.dumps(create_evidence_bundle(restored))))
    assert [product_to_record(p) for p in restored] == [product_to_record(p) for p in imported]
    for index, product in enumerate(imported):
        assert all(field['state'] != 'observed' for field in product.trust_view().values())
        if index < 2:  # The third fixture never captured support to expire.
            assert getattr(product, 'evidence_availability', [])
    # Policy freshness is separately evaluated and does not delete retained data.
    fresh = demo.fixture_products()[0]
    at_limit = resolve_fields(fresh.evidence_contract, as_of=before)
    assert fresh.trust_view(at_limit)['/price']['state'] == 'observed'
    after_limit = resolve_fields(fresh.evidence_contract, as_of=before + timedelta(microseconds=1))
    assert fresh.trust_view(after_limit)['/price']['state'] == 'expired'


def test_trust_e2e_reject_corrupt_bundle():
    bundle = create_evidence_bundle(demo.fixture_products())
    bundle['schema_version'] = 999
    with pytest.raises(ValueError):
        load_evidence_bundle(bundle)
