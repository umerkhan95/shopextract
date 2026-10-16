"""C01/C10/C11/C12/C22 Shopify controlled captured-source variants.

Transport is not exercised: existing public extraction is unchanged, and captured
GraphQL-shaped declarations are synthetic supplied inputs, not live API proof.
"""
from datetime import datetime, timezone

import pytest

from shopextract._capture import capture
from shopextract._evidence import SupportState
from shopextract._models import Platform
from shopextract.categories import (AdapterContext, CategoryLimits, CategoryOptions,
    CategoryScope, TargetRegistry, normalize_with_categories)
from shopextract.categories.adapters.shopify import (COLLECTION, CUSTOM, STANDARD,
                                                    observe_categories)

AT = datetime(2026, 10, 17, tzinfo=timezone.utc)
STORE = 'https://supplier.test/shop'
SCOPE = CategoryScope(Platform.SHOPIFY, STORE)


def captured(**fields):
    raw = {'id': 101, 'title': 'Boots', 'variants': [], **fields}
    return capture(raw, STORE + '/products.json?limit=1&page=1',
                   'synthetic_fixture', observed_at=AT)


def observed(raw, scope=SCOPE, limits=CategoryLimits()):
    return observe_categories(raw, context=AdapterContext(scope, limits))


def test_c01_shopify_opaque_custom_label_and_legacy_normalize():
    raw = captured(product_type='Boots > Sale/Outdoor')
    wrapped = normalize_with_categories(raw, Platform.SHOPIFY, STORE,
        category_options=CategoryOptions(SCOPE, TargetRegistry('operator-category', 'v1', ('boots',))))
    assert wrapped.product.product_type == 'Boots > Sale/Outdoor'
    assert wrapped.product.category_path == ['Boots > Sale/Outdoor']
    custom, standard, collections = wrapped.observations
    assert custom.taxonomy_kind == 'custom_type'
    assert custom.relation == 'label'
    assert custom.terms[0].label == 'Boots > Sale/Outdoor'
    assert custom.terms[0].ref.namespace == CUSTOM
    assert custom.terms[0].ref.native_id is None
    assert custom.terms[0].facts[0].support == SupportState.OBSERVED
    assert custom.terms[0].facts[0].binding.facet == 'label'
    assert custom.terms[0].facts[0].binding.term == custom.terms[0].ref
    assert standard.source_state == collections.source_state == 'missing'
    assert not standard.terms and not collections.terms
    assert all(not o.parent_edges and o.relation != 'ordered_path' for o in wrapped.observations)


@pytest.mark.parametrize('fields,state,support', [
    ({}, 'missing', SupportState.UNSUPPORTED),
    ({'product_type': None}, 'null', SupportState.UNKNOWN),
    ({'product_type': ''}, 'empty', SupportState.UNKNOWN),
    ({'product_type': []}, 'malformed', SupportState.OBSERVED),
    ({'product_type': {}}, 'malformed', SupportState.OBSERVED),
])
def test_c10_shopify_raw_state_without_fabricated_terms(fields, state, support):
    custom = observed(captured(**fields))[0]
    assert custom.source_state == state
    assert custom.terms == ()
    assert custom.completeness == 'unknown'
    assert custom.facts[0].support == support
    assert custom.facts[0].binding.facet == 'source_state'
    if 'product_type' in fields:
        assert custom.facts[0].raw_value == fields['product_type']


def test_c01_shopify_standard_and_merchandising_have_distinct_namespaces():
    gid = 'gid://shopify/TaxonomyCategory/aa-1'
    raw = captured(product_type='Shoes', category={'id': gid, 'name': 'Footwear'},
        collections={'edges': [{'node': {'id': 'gid://shopify/Collection/7', 'title': 'Sale'}}],
                     'pageInfo': {'hasNextPage': False}})
    custom, standard, collections = observed(raw)
    assert [o.taxonomy_kind for o in (custom, standard, collections)] == [
        'custom_type', 'standard', 'merchandising']
    assert standard.terms[0].ref.namespace == STANDARD
    assert standard.terms[0].ref.native_id == gid
    assert standard.terms[0].ref.merchant_scope is None
    assert collections.terms[0].ref.namespace == COLLECTION
    assert collections.terms[0].ref.merchant_scope == custom.terms[0].ref.merchant_scope
    assert collections.terms[0].ref.merchant_scope is not None
    assert standard.terms[0].ref.taxonomy_version is None
    for observation in (custom, standard, collections):
        assert observation.parent_edges == ()
        for term in observation.terms:
            assert all(fact.binding.term == term.ref for fact in term.facts)
            assert all(fact.support == SupportState.OBSERVED for fact in term.facts)
            assert all(fact.evidence[0].source_url.endswith('/products.json?limit=1&page=1')
                       for fact in term.facts)


def test_c11_shopify_id_support_does_not_borrow_retained_label():
    raw = captured(category={'id': 'gid://shopify/TaxonomyCategory/aa-1', 'name': 'Footwear'})
    raw['category']['id'] = 'gid://shopify/TaxonomyCategory/changed'
    term = observed(raw)[1].terms[0]
    by_facet = {fact.binding.facet: fact for fact in term.facts}
    assert by_facet['native_id'].support == SupportState.UNSUPPORTED
    assert by_facet['label'].support == SupportState.OBSERVED
    assert by_facet['native_id'].binding.term == term.ref
    assert by_facet['native_id'].outcome.source_paths == ('/category/id',)
    assert by_facet['label'].outcome.source_paths == ('/category/name',)


@pytest.mark.parametrize('has_next,expected,reason', [
    (False, 'complete', ''),
    (True, 'partial', 'category_budget_reached'),
    ('false', 'unknown', 'completion_metadata_unavailable'),
])
def test_c01_shopify_captured_collections_completion(has_next, expected, reason):
    relation = observed(captured(collections={'edges': [], 'pageInfo': {'hasNextPage': has_next}}))[2]
    assert relation.source_state == 'empty'
    assert relation.completeness == expected
    assert relation.reason == reason
    assert relation.terms == ()
    assert relation.facts[0].raw_value['edges'] == []
    assert relation.facts[1].binding.facet == 'completion'


def test_c12_shopify_collection_order_duplicates_and_store_scope():
    def relation(ids, scope=SCOPE):
        return observed(captured(collections={'edges': [
            {'node': {'id': f'gid://shopify/Collection/{value}', 'title': f'Group {value}'}}
            for value in ids], 'pageInfo': {'hasNextPage': False}}), scope)[2]
    first, second = relation([2, 1, 2]), relation([1, 2])
    assert {(t.ref, t.label) for t in first.terms} == {(t.ref, t.label) for t in second.terms}
    assert len(first.terms) == 2
    duplicate = next(t for t in first.terms if t.ref.native_id.endswith('/2'))
    assert len(duplicate.facts) == 4
    assert {f.pointer for f in duplicate.facts} == {
        '/collections/edges/0/node/id', '/collections/edges/0/node/title',
        '/collections/edges/2/node/id', '/collections/edges/2/node/title'}
    other = relation([2], CategoryScope(Platform.SHOPIFY, 'https://supplier.test/other'))
    assert other.terms[0].ref != duplicate.ref
    assert first.parent_edges == ()


def test_c22_shopify_category_cap_never_claims_known_empty_or_complete():
    raw = captured(product_type='Boots', category={'id': 'gid://shopify/TaxonomyCategory/aa-1'},
        collections={'edges': [{'node': {'id': 'gid://shopify/Collection/1', 'title': 'Sale'}}],
                     'pageInfo': {'hasNextPage': False}})
    values = observed(raw, limits=CategoryLimits(terms=0))
    assert all(not o.terms for o in values)
    assert all(o.source_state == 'present' for o in values)
    assert all(o.completeness == 'partial' for o in values)
    assert all(o.reason == 'category_limit_reached' for o in values)


def test_c10_shopify_malformed_id_does_not_coerce_boolean_or_borrow_label():
    raw = captured(category={'id': True, 'name': 'Footwear'},
        collections={'edges': [{'node': {'id': 'gid://shopify/Collection/7', 'title': None}}],
                     'pageInfo': {'hasNextPage': False}})
    standard, merchandising = observed(raw)[1:]
    assert standard.source_state == 'malformed'
    assert standard.terms[0].ref.native_id is None
    assert standard.terms[0].label == 'Footwear'
    assert standard.terms[0].facts[0].support == SupportState.UNSUPPORTED
    assert standard.terms[0].facts[1].support == SupportState.OBSERVED
    assert merchandising.terms[0].ref.native_id == 'gid://shopify/Collection/7'
    assert merchandising.terms[0].label is None
    assert merchandising.terms[0].facts[0].support == SupportState.OBSERVED
    assert merchandising.terms[0].facts[1].support != SupportState.OBSERVED
