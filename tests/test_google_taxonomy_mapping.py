"""Real source capture and native mapping/effective-classification contracts."""
from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha256
import importlib
import json

import pytest

from shopextract._capture import capture
from shopextract._models import Platform
from shopextract.categories.contracts import CategorySelector, CategoryScope, MappingRule
from shopextract.categories.portable import bind_product
from shopextract.extractors.feed import GoogleFeedExtractor

from tests.test_google_crosswalk import source_catalog, document

SHOP = 'https://merchant.test/catalog'


def api():
    module = importlib.import_module('shopextract.taxonomies.google')
    assert callable(getattr(module, 'effective_google_category', None)), 'Effective Google classification is missing'
    return module


def taxonomy(module):
    return module.parse_google_taxonomy('# Google_Product_Taxonomy_Version: 2021-09-21\n1 - Animals\n2 - Electronics\n')


def feed():
    return GoogleFeedExtractor._parse_csv('id,title,price,google_product_category\nP1,Widget,1 EUR,1\n',
        SHOP + '/feed.csv', include_categories=True)[0]


def test_effective_direct_classification_and_corrupt_binding():
    module = api()
    catalog = taxonomy(module)
    wrapped = module.normalize_with_google_taxonomy(feed(), shop_url=SHOP, taxonomy=catalog,
        allow_unknown_source_version=True)
    result = module.effective_google_category(wrapped, taxonomy=catalog)
    assert (result.status, result.target_id, result.candidate_ids) == ('mapped', '1', ('1',))
    with pytest.raises(ValueError):
        module.effective_google_category(replace(wrapped, original_binding='0' * 64), taxonomy=catalog)


def test_effective_route_conflict_never_chooses_first():
    module = api()
    catalog = taxonomy(module)
    rule = MappingRule('operator', 'v1', CategorySelector('google:product_category', None,
        native_id='1', allow_unknown_version=True), ('2',))
    wrapped = module.normalize_with_google_taxonomy(feed(), shop_url=SHOP, taxonomy=catalog,
        mappings=(rule,), allow_unknown_source_version=True)
    result = module.effective_google_category(wrapped, taxonomy=catalog)
    assert result.status == 'ambiguous' and result.target_id is None
    assert result.candidate_ids == ('1', '2')


def test_effective_multiple_targets_and_partial_are_not_single_classification():
    module = api()
    catalog = taxonomy(module)
    rule = MappingRule('operator', 'v1', CategorySelector('google:product_category', None,
        native_id='1', allow_unknown_version=True), ('1', '2'))
    wrapped = module.normalize_with_google_taxonomy(feed(), shop_url=SHOP, taxonomy=catalog,
        mappings=(rule,))
    assert module.effective_google_category(wrapped, taxonomy=catalog).status == 'ambiguous'
    one = module.normalize_with_google_taxonomy(feed(), shop_url=SHOP, taxonomy=catalog,
        allow_unknown_source_version=True)
    partial = tuple(replace(value, partial=True) for value in one.mappings)
    rebound = bind_product(one.product, one.scope, one.observations, partial, one.config_digest)
    result = module.effective_google_category(rebound, taxonomy=catalog)
    assert result.status == 'ambiguous' and result.target_id is None


def test_unknown_permission_unsupported_capture_and_other_merchant_scope():
    module = api()
    catalog = taxonomy(module)
    denied = module.normalize_with_google_taxonomy(feed(), shop_url=SHOP, taxonomy=catalog)
    assert module.effective_google_category(denied, taxonomy=catalog).target_id is None
    raw = feed()
    raw['_capture']['method'] = 'llm_bounded'
    unsupported = module.normalize_with_google_taxonomy(raw, shop_url=SHOP, taxonomy=catalog,
        allow_unknown_source_version=True)
    assert module.effective_google_category(unsupported, taxonomy=catalog).status == 'unavailable'
    rule = MappingRule('wrong-store', 'v1', CategorySelector('google:product_category', None,
        scope=CategoryScope(Platform.GENERIC, 'https://other.test'),
        native_id='1', allow_unknown_version=True), ('2',))
    scoped = module.normalize_with_google_taxonomy(feed(), shop_url=SHOP, taxonomy=catalog,
        mappings=(rule,))
    assert module.effective_google_category(scoped, taxonomy=catalog).target_id is None


def test_effective_wrong_catalog_identity_rejected():
    module = api()
    catalog = taxonomy(module)
    wrapped = module.normalize_with_google_taxonomy(feed(), shop_url=SHOP, taxonomy=catalog,
        allow_unknown_source_version=True)
    different = module.parse_google_taxonomy('# Google_Product_Taxonomy_Version: 2021-09-21\n1 - Renamed\n2 - Electronics\n')
    with pytest.raises(ValueError):
        module.effective_google_category(wrapped, taxonomy=different)


def test_shopify_crosswalk_preserves_source_none_and_explicit_permission(tmp_path):
    module = api()
    catalog = taxonomy(module)
    data = json.dumps(document()).encode()
    path = tmp_path / 'crosswalk.json'
    path.write_bytes(data)
    crosswalk = module.load_shopify_google_crosswalk(path, source_catalog=source_catalog(),
        target_catalog=catalog, expected_sha256=sha256(data).hexdigest())
    raw = capture({'id': 1, 'title': 'Widget', 'variants': [],
                   'category': {'id': 'gid://shopify/TaxonomyCategory/a', 'name': 'Category A'}},
                  SHOP + '/products.json', 'synthetic_fixture',
                  observed_at=datetime(2026, 10, 31, tzinfo=timezone.utc))
    allowed = module.normalize_with_google_taxonomy(raw, platform=Platform.SHOPIFY,
        shop_url=SHOP, taxonomy=catalog, crosswalk=crosswalk,
        allow_unknown_source_version=True)
    standard = next(o for o in allowed.observations if o.terms and o.taxonomy_kind == 'standard')
    assert standard.terms[0].ref.taxonomy_version is None
    assert module.effective_google_category(allowed, taxonomy=catalog).target_id == '1'
    denied = module.normalize_with_google_taxonomy(raw, platform=Platform.SHOPIFY,
        shop_url=SHOP, taxonomy=catalog, crosswalk=crosswalk)
    assert module.effective_google_category(denied, taxonomy=catalog).target_id is None
    wrong = module.parse_google_taxonomy('# Google_Product_Taxonomy_Version: 2021-09-21\n1 - Changed\n2 - Electronics\n')
    with pytest.raises(ValueError):
        module.normalize_with_google_taxonomy(raw, platform=Platform.SHOPIFY,
            shop_url=SHOP, taxonomy=wrong, crosswalk=crosswalk,
            allow_unknown_source_version=True)
