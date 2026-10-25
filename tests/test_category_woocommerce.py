"""Controlled Woo source cases C02/C10/C11/C12/C22; no remote HTTP."""
from datetime import datetime, timezone

import pytest

from shopextract._capture import capture
from shopextract._evidence import SupportState
from shopextract._models import Platform
from shopextract._normalize import normalize
from shopextract.categories.adapters.woocommerce import observe_categories
from shopextract.categories.contracts import AdapterContext, CategoryLimits, CategoryScope


SCOPE = CategoryScope(Platform.WOOCOMMERCE, 'https://supplier.test/shop/a', catalog='retail')


def captured(**fields):
    raw = {'id': 501, 'name': 'Synthetic boot', 'prices': {'price': '9900',
           'currency_code': 'EUR', 'currency_minor_unit': 2}, **fields}
    return capture(raw, 'https://supplier.test/shop/a/wp-json/wc/store/v1/products?page=1',
                   'woocommerce_api', observed_at=datetime(2026, 10, 17, tzinfo=timezone.utc))


def observation(raw, scope=SCOPE, limits=CategoryLimits()):
    result = observe_categories(raw, context=AdapterContext(scope, limits))
    assert len(result) == 1
    return result[0]


def test_c02_siblings_permutations_and_duplicate_source_support():
    entries = [{'id': 7, 'name': 'Boots'}, {'id': 9, 'name': 'Sale'}]
    first = observation(captured(categories=entries))
    reordered = observation(captured(categories=[entries[1], entries[0], entries[0]]))
    assert first.relation == reordered.relation == 'memberships'
    assert first.completeness == reordered.completeness == 'complete'
    assert {(t.ref, t.label) for t in first.terms} == {(t.ref, t.label) for t in reordered.terms}
    assert len(reordered.terms) == 2
    assert first.parent_edges == reordered.parent_edges == ()
    boots = next(t for t in reordered.terms if t.ref.native_id == '7')
    assert {'/categories/1/id', '/categories/2/id'} <= {f.pointer for f in boots.facts}
    assert all(f.support == SupportState.OBSERVED for t in first.terms for f in t.facts)
    assert normalize(captured(categories=entries), platform=Platform.WOOCOMMERCE,
                     shop_url=SCOPE.store_url).category_path == ['Boots', 'Sale']


@pytest.mark.parametrize(('fields', 'state', 'complete'), [
    ({}, 'missing', 'unknown'), ({'categories': None}, 'null', 'unknown'),
    ({'categories': []}, 'empty', 'complete'),
    ({'categories': ''}, 'malformed', 'unknown'),
    ({'categories': {'id': 7}}, 'malformed', 'unknown'),
])
def test_c10_source_states(fields, state, complete):
    value = observation(captured(**fields))
    assert value.source_state == state
    assert value.completeness == complete
    assert value.terms == ()
    assert value.facts[0].binding.facet == 'source_state'
    if state == 'empty':
        assert value.facts[0].support == SupportState.OBSERVED
        assert value.facts[0].raw_value == []


def test_c11_id_and_label_facets_are_independent_and_verbatim():
    value = observation(captured(categories=[{'id': 7}, {'name': 'Boots > Sale / Été'},
                                             {'id': True, 'name': 'Label survives'}]))
    assert [(t.ref.native_id, t.label) for t in value.terms] == [
        ('7', None), (None, 'Boots > Sale / Été'), (None, 'Label survives')]
    assert value.parent_edges == ()
    rejected = next(f for f in value.terms[2].facts if f.binding.facet == 'native_id')
    assert rejected.support != SupportState.OBSERVED
    assert not rejected.outcome.accepted
    label = next(f for f in value.terms[2].facts if f.binding.facet == 'label')
    assert label.support == SupportState.OBSERVED
    assert label.binding.term == value.terms[2].ref


def test_c11_changed_native_id_cannot_borrow_label_support():
    raw = captured(categories=[{'id': 7, 'name': 'Boots'}])
    raw['categories'][0]['id'] = 8
    term = observation(raw).terms[0]
    facts = {f.binding.facet: f for f in term.facts}
    assert facts['native_id'].support != SupportState.OBSERVED
    assert facts['label'].support == SupportState.OBSERVED
    assert facts['native_id'].binding.term == facts['label'].binding.term == term.ref


def test_c12_store_basepath_catalog_and_assignment_context():
    raw = captured(categories=[{'id': 7, 'name': 'Boots', 'slug': 'boots'}])
    a = observation(raw)
    b = observation(raw, CategoryScope(Platform.WOOCOMMERCE, 'https://supplier.test/shop/b', catalog='retail'))
    catalog = observation(raw, CategoryScope(Platform.WOOCOMMERCE, SCOPE.store_url, catalog='trade'))
    localized = observation(raw, CategoryScope(Platform.WOOCOMMERCE, SCOPE.store_url,
                                             catalog='retail', channel='1', locale='de'))
    assert a.terms[0].ref != b.terms[0].ref
    assert a.terms[0].ref != catalog.terms[0].ref
    assert a.terms[0].ref == localized.terms[0].ref
    assert a.scope != localized.scope
    assert a.terms[0].ref.namespace == 'woocommerce:product_cat'
    assert not any(f.binding.facet == 'code_context' for f in a.terms[0].facts)


def test_c22_limits_retain_supported_membership_without_false_empty():
    raw = captured(categories=[{'id': 7, 'name': 'Boots'}, {'id': 9, 'name': 'Sale'}])
    value = observation(raw, limits=CategoryLimits(terms=1))
    assert [t.ref.native_id for t in value.terms] == ['7']
    assert value.completeness == 'partial'
    assert value.reason == 'category_budget_reached'
    zero = observation(raw, limits=CategoryLimits(terms=0))
    assert zero.terms == ()
    assert zero.source_state == 'present'
    assert zero.completeness == 'partial'


def test_c02_legacy_labels_and_competing_same_id_labels_remain_source_data():
    value = observation(captured(categories=['Boots > Sale', {'id': 7, 'name': 'Boots'},
                                             {'id': 7, 'name': 'Stiefel'}]))
    assert [(t.ref.native_id, t.label) for t in value.terms] == [
        (None, 'Boots > Sale'), ('7', 'Boots'), ('7', 'Stiefel')]
    assert value.terms[1].ref == value.terms[2].ref
    assert value.parent_edges == ()


def test_c10_malformed_member_does_not_erase_valid_sibling():
    value = observation(captured(categories=[{'id': 7, 'name': 'Boots'}, False]))
    assert [t.ref.native_id for t in value.terms] == ['7']
    assert value.completeness == 'partial'
    assert value.reason == 'category_source_malformed'
