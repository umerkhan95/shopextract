"""Google child intended-red acceptance; all catalog/feed paths stay real."""
from hashlib import sha256
import importlib

import pytest

from shopextract._models import Platform
from shopextract.categories import categorized_product_from_record, categorized_product_to_record
from shopextract.categories.contracts import CategoryScope
from shopextract.extractors.feed import GoogleFeedExtractor


TEXT = """# Google_Product_Taxonomy_Version: 2021-09-21
1 - Animals
2 - Animals > Cats
3 - Animals > Dogs
4 - Electronics
5 - Electronics > Computers
6 - Electronics > Computers > Laptops
7 - Electronics > Computers > Desktops
"""
SHOP = "https://merchant.test/catalog"


def api():
    try:
        value = importlib.import_module("shopextract.taxonomies.google")
    except ModuleNotFoundError as error:
        if error.name != "shopextract.taxonomies.google":
            raise
        pytest.fail("Google taxonomy public integration is not implemented", pytrace=False)
    assert callable(getattr(value, "parse_google_taxonomy", None)), "Google source parser is missing"
    return value


def catalog():
    return api().parse_google_taxonomy(TEXT)


def feed(value):
    return GoogleFeedExtractor._parse_csv(
        "id,title,price,google_product_category\nP1,Laptop,10 EUR," + value + "\n",
        SHOP + "/feed.csv", include_categories=True,
    )[0]


def test_google_complete_structural_contract_and_exact_path():
    taxonomy = catalog()
    assert taxonomy.manifest.counts.categories == 7
    assert taxonomy.manifest.counts.roots == 2
    assert taxonomy.manifest.counts.leaves == 4
    assert taxonomy.manifest.counts.parent_links == 5
    node = taxonomy.category("6")
    assert node == taxonomy.resolve_path("Electronics > Computers > Laptops")
    assert node.parent_id == "5" and node.child_ids == ()
    assert tuple(n.id for n in taxonomy.ancestors("6")) == ("4", "5")
    assert {n.id for n in taxonomy.children("5")} == {"6", "7"}
    assert {n.id for n in taxonomy.iter_categories()} == {str(i) for i in range(1, 8)}


@pytest.mark.parametrize("bad", [
    TEXT + "6 - Other\n",
    TEXT + "8 - Animals > Cats\n",
    TEXT + "8 - Missing > Parent > Leaf\n",
])
def test_google_invalid_source_rejected_before_index(bad):
    with pytest.raises(ValueError):
        api().parse_google_taxonomy(bad)


def test_google_source_digest_is_checked_not_inferred():
    with pytest.raises(ValueError):
        api().parse_google_taxonomy(TEXT, expected_sha256="0" * 64)
    value = api().parse_google_taxonomy(TEXT, expected_sha256=sha256(TEXT.encode()).hexdigest())
    assert value.manifest.source_sha256 == sha256(TEXT.encode()).hexdigest()
    assert value.category("999") is None
    assert value.resolve_path("Computers > Laptops") is None


@pytest.mark.parametrize("declaration", ["6", "Electronics > Computers > Laptops"])
def test_google_supported_feed_id_and_path_reuse_native_portable(declaration):
    taxonomy = catalog()
    wrapped = api().normalize_with_google_taxonomy(
        feed(declaration), platform=Platform.GENERIC, shop_url=SHOP,
        taxonomy=taxonomy, allow_unknown_source_version=True,
    )
    assert wrapped is not None
    standard = next(o for o in wrapped.observations if o.taxonomy_kind == "standard")
    assert standard.terms[0].ref.taxonomy_version is None
    mapped = [m for m in wrapped.mappings if m.status == "mapped"]
    assert len(mapped) == 1 and mapped[0].target_ids == ("6",)
    assert mapped[0].target_namespace == "google:product_category"
    assert mapped[0].target_version == taxonomy.registry_version
    assert mapped[0].source_pointers
    restored = categorized_product_from_record(categorized_product_to_record(wrapped))
    assert restored.observations == wrapped.observations
    assert restored.mappings == wrapped.mappings


def test_google_unknown_source_version_requires_explicit_permission():
    wrapped = api().normalize_with_google_taxonomy(
        feed("6"), platform=Platform.GENERIC, shop_url=SHOP,
        taxonomy=catalog(), allow_unknown_source_version=False,
    )
    assert wrapped is not None
    assert not any(m.status == "mapped" for m in wrapped.mappings)
    assert wrapped.observations[0].terms[0].ref.taxonomy_version is None


def test_google_selected_options_keep_native_limits():
    rows = "\n".join(f"{i} - Category{i}" for i in range(1, 1002))
    taxonomy = api().parse_google_taxonomy("# Google_Product_Taxonomy_Version: 2021-09-21\n" + rows + "\n")
    scope = CategoryScope(Platform.GENERIC, SHOP)
    options = api().google_taxonomy_options(scope, category_ids=[str(i) for i in range(1, 1001)], taxonomy=taxonomy)
    assert len(options.registry.target_ids) == 1000
    with pytest.raises(ValueError):
        api().google_taxonomy_options(scope, category_ids=[str(i) for i in range(1, 1002)], taxonomy=taxonomy)


def test_google_prepared_catalog_is_offline_and_hash_bound(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text(TEXT)
    root = tmp_path / "catalogs"
    directory = api().prepare_google_taxonomy(source, root)
    taxonomy = api().load_google_taxonomy(catalog_root=root)
    assert directory.is_dir() and taxonomy.category("6").name == "Laptops"
    assert taxonomy.manifest.source_sha256 == sha256(TEXT.encode()).hexdigest()
    assert len(taxonomy.manifest.fingerprint) == 64
    assert api().load_google_taxonomy(catalog_root=root, fingerprint=taxonomy.manifest.fingerprint).category("6") == taxonomy.category("6")


def test_google_invalid_prepare_preserves_prior_catalog(tmp_path):
    source = tmp_path / "source.txt"
    source.write_text(TEXT)
    root = tmp_path / "catalogs"
    api().prepare_google_taxonomy(source, root)
    previous = api().load_google_taxonomy(catalog_root=root)
    source.write_text(TEXT + "6 - Conflicting duplicate\n")
    with pytest.raises(ValueError):
        api().prepare_google_taxonomy(source, root)
    loaded = api().load_google_taxonomy(catalog_root=root)
    assert loaded.manifest.fingerprint == previous.manifest.fingerprint
    assert loaded.category("6") == previous.category("6")
