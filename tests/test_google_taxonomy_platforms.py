"""Controlled synthetic six-family Google integration; no merchant/live claim."""
from datetime import datetime, timezone

import pytest

from shopextract._capture import capture
from shopextract._models import Platform
from shopextract.categories.contracts import CategoryScope, CategorySelector, MappingRule
from shopextract.categories.portable import categorized_product_to_record, categorized_product_from_record
from shopextract.extractors.feed import GoogleFeedExtractor
from shopextract.taxonomies.google import (parse_google_taxonomy,
    normalize_with_google_taxonomy, effective_google_category)
from tests.test_category_shopify import captured as shopify
from tests.test_category_woocommerce import captured as woo
from tests.test_category_magento import captured as magento
from tests.test_category_shopware import captured as shopware
from tests.test_category_bigcommerce import node as bigcommerce

STORE = 'https://supplier.test/shop'
AT = datetime(2026, 10, 31, tzinfo=timezone.utc)
SHOPWARE_ID = 'a' * 32
SHOPIFY_ID = 'gid://shopify/TaxonomyCategory/synthetic-merchant-category'
CATALOG = parse_google_taxonomy(
    '# Google_Product_Taxonomy_Version: 2021-09-21\n1 - Synthetic root\n2 - Synthetic root > Synthetic target\n')
CASES = [
    (Platform.SHOPIFY, 'shopify:standard_product_taxonomy', SHOPIFY_ID),
    (Platform.WOOCOMMERCE, 'woocommerce:product_cat', '7'),
    (Platform.MAGENTO, 'magento:category', 'Nw=='),
    (Platform.SHOPWARE, 'shopware:category', SHOPWARE_ID),
    (Platform.BIGCOMMERCE, 'bigcommerce:category', '7'),
    (Platform.GENERIC, 'google:product_category', '1'),
]


def source(platform, *, present=True):
    if platform == Platform.SHOPIFY:
        return shopify(**({'category': {'id': SHOPIFY_ID, 'name': 'Original merchant category'}} if present else {}))
    if platform == Platform.WOOCOMMERCE:
        return woo(**({'categories': [{'id': 7, 'name': 'Original merchant category'}]} if present else {}))
    if platform == Platform.MAGENTO:
        return magento(**({'categories': [{'uid': 'Nw==', 'name': 'Original merchant category'}]} if present else {}))
    if platform == Platform.SHOPWARE:
        return shopware(**({'categoryIds': [SHOPWARE_ID]} if present else {}))
    if platform == Platform.BIGCOMMERCE:
        value = bigcommerce({'pageInfo': {'hasNextPage': False}, 'edges': [
            {'node': {'entityId': 7, 'name': 'Original merchant category'}}]})
        if not present:
            value.pop('categories')
        return capture(value, STORE + '/graphql', 'bigcommerce_graphql', observed_at=AT)
    columns = 'id,title,price' + (',google_product_category' if present else '')
    row = 'P1,Synthetic product,10 EUR' + (',1' if present else '')
    return GoogleFeedExtractor._parse_csv(columns + '\n' + row + '\n', STORE + '/feed.csv',
        include_categories=True)[0]


def rule(platform, namespace, native, *, store=STORE):
    return MappingRule('synthetic-merchant-mapping', 'reviewed-fixture-v1',
        CategorySelector(namespace, None, scope=CategoryScope(platform, store),
                         native_id=native, allow_unknown_version=True), ('2',))


@pytest.mark.parametrize('platform,namespace,native', CASES)
def test_six_sources_actual_capture_mapping_portable_effective(platform, namespace, native):
    raw = source(platform)
    wrapped = normalize_with_google_taxonomy(raw, platform=platform, shop_url=STORE,
        taxonomy=CATALOG, mappings=(rule(platform, namespace, native),))
    assert wrapped is not None and wrapped.product.title
    observations = [o for o in wrapped.observations if any(t.ref.namespace == namespace for t in o.terms)]
    assert observations and all(t.ref.taxonomy_version is None for o in observations for t in o.terms)
    mapped = [d for d in wrapped.mappings if d.status == 'mapped']
    assert len(mapped) == 1 and mapped[0].target_ids == ('2',) and mapped[0].source_pointers
    assert all(f.evidence for o in observations for t in o.terms for f in t.facts
               if f.binding.facet == 'native_id' and f.outcome.accepted)
    restored = categorized_product_from_record(categorized_product_to_record(wrapped))
    assert restored.observations == wrapped.observations
    assert restored.mappings == wrapped.mappings
    result = effective_google_category(restored, taxonomy=CATALOG)
    assert (result.status, result.target_id) == ('mapped', '2')


@pytest.mark.parametrize('platform,namespace,native', CASES)
def test_missing_category_keeps_product_unavailable_not_empty_product(platform, namespace, native):
    wrapped = normalize_with_google_taxonomy(source(platform, present=False), platform=platform,
        shop_url=STORE, taxonomy=CATALOG, mappings=(rule(platform, namespace, native),))
    assert wrapped is not None and wrapped.product.title
    assert effective_google_category(wrapped, taxonomy=CATALOG).status == 'unavailable'
    assert not any(d.status == 'mapped' for d in wrapped.mappings)


@pytest.mark.parametrize('guard', ['wrong-store', 'wrong-platform'])
def test_same_merchant_numeric_id_does_not_bypass_scope(guard):
    mapping = rule(Platform.MAGENTO if guard == 'wrong-platform' else Platform.WOOCOMMERCE,
        'woocommerce:product_cat', '7', store='https://other.test/shop' if guard == 'wrong-store' else STORE)
    wrapped = normalize_with_google_taxonomy(source(Platform.WOOCOMMERCE), platform=Platform.WOOCOMMERCE,
        shop_url=STORE, taxonomy=CATALOG, mappings=(mapping,))
    assert effective_google_category(wrapped, taxonomy=CATALOG).status == 'unmapped'


def test_shopware_tree_index_never_becomes_product_membership():
    wrapped = normalize_with_google_taxonomy(shopware(categoryTree=[SHOPWARE_ID]),
        platform=Platform.SHOPWARE, shop_url=STORE, taxonomy=CATALOG,
        mappings=(rule(Platform.SHOPWARE, 'shopware:category', SHOPWARE_ID),))
    assert any(o.relation == 'index' and o.terms for o in wrapped.observations)
    assert effective_google_category(wrapped, taxonomy=CATALOG).target_id is None


def test_shopify_custom_type_cannot_borrow_standard_gid_rule():
    wrapped = normalize_with_google_taxonomy(shopify(product_type=SHOPIFY_ID),
        platform=Platform.SHOPIFY, shop_url=STORE, taxonomy=CATALOG,
        mappings=(rule(Platform.SHOPIFY, 'shopify:standard_product_taxonomy', SHOPIFY_ID),))
    assert effective_google_category(wrapped, taxonomy=CATALOG).target_id is None
