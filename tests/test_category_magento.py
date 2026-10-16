"""Bounded Magento category mechanisms using real extraction and captured facts."""
from datetime import datetime, timezone

import httpx
import pytest

from shopextract._capture import capture
from shopextract._evidence import SupportState
from shopextract._models import Platform
from shopextract._normalize import normalize
from shopextract.categories.adapters.magento import observe_categories
from shopextract.categories.contracts import (
    AdapterContext, CategoryLimits, CategoryScope, NativeCategoryError,
)
from shopextract.categories.native import CATEGORY_DIAGNOSTICS_KEY
from shopextract.extractors.magento_graphql import (
    MagentoGraphQLExtractor, _QUERY, _QUERY_WITH_CATEGORIES,
)


SCOPE = CategoryScope(Platform.MAGENTO, 'https://supplier.test/shop', catalog='retail')


def product(sku='A', **fields):
    return {'sku': sku, 'name': 'Synthetic product ' + sku, 'url_key': sku,
            'description': {'html': 'Synthetic'}, 'stock_status': 'IN_STOCK',
            'price_range': {'minimum_price': {'final_price': {'value': 10, 'currency': 'EUR'}}},
            **fields}


def captured(**fields):
    return capture(product(**fields), 'https://supplier.test/graphql', 'magento_graphql',
                   observed_at=datetime(2026, 10, 17, tzinfo=timezone.utc))


def observation(raw, scope=SCOPE, limits=CategoryLimits(), errors=()):
    return observe_categories(raw, context=AdapterContext(scope, limits, errors))[0]


def test_magento_memberships_opaque_ids_dedup_and_no_ancestry():
    entries = [{'uid': 'Nw==', 'name': 'Boots > Sale / Été'}, {'uid': '9', 'name': 'Sale'}]
    first = observation(captured(categories=entries))
    other = observation(captured(categories=[entries[1], entries[0], entries[0]]))
    assert first.relation == 'memberships'
    assert first.parent_edges == other.parent_edges == ()
    assert {(t.ref, t.label) for t in first.terms} == {(t.ref, t.label) for t in other.terms}
    assert len(other.terms) == 2
    term = next(t for t in other.terms if t.ref.native_id == 'Nw==')
    assert len(term.facts) == 4
    assert all(f.support == SupportState.OBSERVED for f in term.facts)
    assert normalize(captured(categories=entries), Platform.MAGENTO, SCOPE.store_url).category_path == []


@pytest.mark.parametrize(('fields', 'state', 'completeness'), [
    ({}, 'missing', 'unknown'), ({'categories': None}, 'null', 'unknown'),
    ({'categories': []}, 'empty', 'complete'),
    ({'categories': 'Boots'}, 'malformed', 'unknown'),
    ({'categories': [None]}, 'present', 'partial'),
])
def test_magento_source_states_do_not_fabricate_empty(fields, state, completeness):
    result = observation(captured(**fields))
    assert (result.source_state, result.completeness) == (state, completeness)
    assert result.terms == ()


def test_magento_uid_and_label_support_are_independent():
    result = observation(captured(categories=[{'uid': 7, 'name': 'Label survives'},
                                             {'uid': 'Nw==', 'name': None}]))
    assert [(t.ref.native_id, t.label) for t in result.terms] == [(None, 'Label survives'), ('Nw==', None)]
    first, second = [{f.binding.facet: f for f in t.facts} for t in result.terms]
    assert first['native_id'].support != SupportState.OBSERVED
    assert first['label'].support == SupportState.OBSERVED
    assert second['native_id'].support == SupportState.OBSERVED
    assert second['label'].support != SupportState.OBSERVED
    assert all(f.binding.term == t.ref for t in result.terms for f in t.facts)
    raw = captured(categories=[{'uid': 'Nw==', 'name': 'Boots'}])
    raw['categories'][0]['uid'] = 'changed'
    term = observation(raw).terms[0]
    assert term.facts[0].support != SupportState.OBSERVED
    assert term.facts[1].support == SupportState.OBSERVED


def test_magento_conflicting_labels_scope_and_bounded_memberships():
    raw = captured(categories=[{'uid': '7', 'name': 'Boots'}, {'uid': '7', 'name': 'Sale'}])
    result = observation(raw)
    assert len(result.terms) == 2  # Competing label claims must survive.
    other = observation(raw, CategoryScope(Platform.MAGENTO, 'https://supplier.test/other', catalog='retail'))
    assert result.terms[0].ref != other.terms[0].ref
    localized = observation(raw, CategoryScope(Platform.MAGENTO, SCOPE.store_url, catalog='retail', locale='de'))
    assert result.terms[0].ref == localized.terms[0].ref
    assert result.scope != localized.scope
    clipped = observation(raw, limits=CategoryLimits(terms=1))
    assert len(clipped.terms) == 1 and clipped.completeness == 'partial'
    assert clipped.reason == 'category_budget_reached'
    zero = observation(raw, limits=CategoryLimits(terms=0))
    assert zero.terms == () and zero.source_state == 'present' and zero.completeness == 'partial'


def test_magento_category_errors_downgrade_but_other_field_errors_do_not():
    raw = captured(categories=[])
    assert observation(raw, errors=(NativeCategoryError(('name',), 'failure'),)).completeness == 'complete'
    failed = observation(raw, errors=(NativeCategoryError(('categories',), 'failure'),))
    assert failed.source_state != 'empty' and failed.completeness == 'unknown'
    assert failed.terms == ()
    assert observation(raw, errors=(NativeCategoryError(None, 'failure'),)).source_state != 'empty'


@pytest.mark.asyncio
async def test_magento_native_query_opt_in_and_default_response_compatibility():
    queries = []
    def respond(req):
        queries.append(req.url.params['query'])
        assert req.method == 'GET'
        assert 'Store' not in req.headers
        item = product(categories=[{'uid': 'Nw==', 'name': 'Boots'}])
        return httpx.Response(200, json={'data': {'products': {
            'items': [item], 'total_count': 1, 'page_info': {'total_pages': 1}}}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        extractor = MagentoGraphQLExtractor(http_client=client)
        default = await extractor.extract(SCOPE.store_url, max_products=1)
        enabled = await extractor.extract(SCOPE.store_url, max_products=1, include_categories=True)
    assert queries == [_QUERY, _QUERY_WITH_CATEGORIES]
    assert 'categories' not in _QUERY
    assert 'categories { uid name }' in _QUERY_WITH_CATEGORIES
    assert default.complete and enabled.complete
    assert observation(enabled.products[0]).terms[0].facts[0].support == SupportState.OBSERVED


@pytest.mark.asyncio
async def test_magento_nonzero_product_error_localization_retains_valid_siblings():
    calls = []
    def respond(req):
        calls.append(req)
        return httpx.Response(200, json={
            'data': {'products': {'items': [
                product('A', categories=[{'uid': 'A', 'name': 'Boots'}]),
                product('B', categories=[{'uid': 'B', 'name': None}]),
                product('C', categories=[{'uid': 'C', 'name': 'Sale'}]),
            ], 'total_count': 3, 'page_info': {'total_pages': 1}}},
            'errors': [{'path': ['products', 'items', 1, 'categories', 0, 'name'],
                        'message': 'secret must not persist'}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result = await MagentoGraphQLExtractor(http_client=client).extract(
            SCOPE.store_url, max_products=3, include_categories=True)
    assert len(calls) == 1 and len(result.products) == 3
    assert not result.complete and result.completeness_reason == 'source_error'
    assert CATEGORY_DIAGNOSTICS_KEY not in result.products[0]
    assert CATEGORY_DIAGNOSTICS_KEY not in result.products[2]
    middle = result.products[1]
    diagnostics = middle[CATEGORY_DIAGNOSTICS_KEY]
    assert diagnostics[0]['path'] == ['categories', 0, 'name']
    assert 'secret' not in str(diagnostics)
    errors = tuple(NativeCategoryError(tuple(d['path']) if d['path'] else None, d['code']) for d in diagnostics)
    observed = observation(middle, errors=errors)
    assert observed.completeness == 'partial' and observed.terms[0].ref.native_id == 'B'
    assert observed.terms[0].facts[0].support == SupportState.OBSERVED
    assert observed.terms[0].facts[1].support != SupportState.OBSERVED
    assert observation(result.products[0]).completeness == 'complete'
    assert observation(result.products[2]).completeness == 'complete'


@pytest.mark.asyncio
async def test_magento_default_still_rejects_partial_graphql_without_retry():
    calls = []
    def respond(req):
        calls.append(req)
        return httpx.Response(200, json={'data': {'products': {'items': [product()], 'total_count': 1}},
                                        'errors': [{'path': ['products', 'items', 0, 'name']}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result = await MagentoGraphQLExtractor(http_client=client).extract(SCOPE.store_url, max_products=1)
    assert result.products == [] and not result.complete and result.error
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_magento_failed_product_does_not_discard_later_valid_product_or_fetch_again():
    calls = []
    def respond(req):
        calls.append(req)
        return httpx.Response(200, json={
            'data': {'products': {'items': [None, product('B', categories=[{'uid': 'B', 'name': 'Boots'}])],
                                 'total_count': 2, 'page_info': {'total_pages': 1}}},
            'errors': [{'path': ['products', 'items', 0], 'message': 'Failed product'}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result = await MagentoGraphQLExtractor(http_client=client).extract(
            SCOPE.store_url, max_products=2, include_categories=True)
    assert len(calls) == 1
    assert [p['sku'] for p in result.products] == ['B']
    assert not result.complete and result.completeness_reason == 'source_error'
    assert CATEGORY_DIAGNOSTICS_KEY not in result.products[0]
    assert observation(result.products[0]).completeness == 'complete'
