"""Controlled captured Shopware C07/C10/C11/C12/C13/C22 cases; no HTTP."""
from datetime import datetime, timezone

import pytest

from shopextract._capture import capture
from shopextract._evidence import SupportState
from shopextract._models import Platform
from shopextract._normalize import normalize
from shopextract.categories.adapters.shopware import observe_categories
from shopextract.categories.contracts import AdapterContext, CategoryLimits, CategoryScope

SCOPE = CategoryScope(Platform.SHOPWARE, 'https://supplier.test/shop/a', catalog='retail', channel='de', locale='de-DE')
IDS = tuple(f'{i:032x}' for i in range(1, 10))


def captured(**fields):
    return capture({'id': 'f' * 32, 'name': 'Synthetic boot', 'calculatedPrice': {'unitPrice': 99}, **fields},
        'https://api.supplier.test/store-api/product', 'shopware_store_api',
        observed_at=datetime(2026, 10, 17, tzinfo=timezone.utc))


def observations(raw, scope=SCOPE, limits=CategoryLimits()):
    return observe_categories(raw, context=AdapterContext(scope, limits))


def test_c07_four_memberships_nine_index_ids_never_path():
    raw = captured(categoryIds=list(IDS[-4:]), categoryTree=list(IDS), categories=None)
    members, index, association = observations(raw)
    assert {t.ref.native_id for t in members.terms} == set(IDS[-4:])
    assert len(index.terms) == 9 and index.relation == 'index'
    assert index.completeness == 'unknown'
    assert members.completeness == 'complete'
    assert association.source_state == 'null'
    assert all(o.relation != 'ordered_path' and not o.parent_edges for o in (members, index, association))
    assert normalize(raw, platform=Platform.SHOPWARE, shop_url=SCOPE.store_url).category_path == []


@pytest.mark.parametrize(('fields', 'state', 'complete'), [
    ({}, 'missing', 'unknown'), ({'categoryIds': None}, 'null', 'unknown'),
    ({'categoryIds': []}, 'empty', 'complete'),
    ({'categoryIds': {'bad': 1}}, 'malformed', 'unknown'),
])
def test_c10_source_states(fields, state, complete):
    member = observations(captured(**fields))[0]
    assert (member.source_state, member.completeness) == (state, complete)
    assert not member.terms


def test_c11_captured_label_does_not_borrow_changed_id_support():
    raw = captured(categories=[{'id': IDS[0], 'name': 'Boots > Sale',
                                'translated': {'name': 'Stiefel > Sale / Été'}}])
    raw['categories'][0]['id'] = IDS[1]
    term = observations(raw)[2].terms[0]
    assert term.label == 'Stiefel > Sale / Été'
    id_fact, label_fact = term.facts
    assert id_fact.support != SupportState.OBSERVED
    assert label_fact.support == SupportState.OBSERVED
    assert label_fact.binding.term == term.ref
    assert label_fact.pointer == '/categories/0/translated/name'


def test_c12_store_basepath_catalog_identity_and_assignment_locale():
    raw = captured(categoryIds=[IDS[0]])
    first = observations(raw)[0]
    other_store = observations(raw, CategoryScope(Platform.SHOPWARE, 'https://supplier.test/shop/b', catalog='retail'))[0]
    other_locale = observations(raw, CategoryScope(Platform.SHOPWARE, SCOPE.store_url, catalog='retail'))[0]
    assert first.terms[0].ref != other_store.terms[0].ref
    assert first.terms[0].ref == other_locale.terms[0].ref
    assert first.scope.channel == 'de' and first.scope.locale == 'de-DE'
    assert other_locale.scope.channel is None and other_locale.scope.locale is None


def test_c07_duplicate_memberships_stable_and_pointer_support_retained():
    first = observations(captured(categoryIds=[IDS[0], IDS[1]]))[0]
    second = observations(captured(categoryIds=[IDS[1], IDS[0], IDS[0]]))[0]
    assert {t.ref for t in first.terms} == {t.ref for t in second.terms}
    duplicate = next(t for t in second.terms if t.ref.native_id == IDS[0])
    assert {f.pointer for f in duplicate.facts} == {'/categoryIds/1', '/categoryIds/2'}


@pytest.mark.parametrize('limits', [CategoryLimits(terms=0), CategoryLimits(terms=2), CategoryLimits(relation_refs=2)])
def test_c22_shared_relation_budget_and_zero(limits):
    result = observations(captured(categoryIds=list(IDS[:4]), categoryTree=list(IDS)), limits=limits)
    assert sum(len(o.terms) for o in result) <= limits.terms
    assert sum(len(o.terms) + 2 * len(o.parent_edges) for o in result) <= limits.relation_refs
    assert result[0].completeness == 'partial'
    assert result[0].reason == 'category_budget_reached'


def test_c13_actual_parent_endpoints_only_and_cycle_bounded():
    raw = captured(categories=[{'id': IDS[0], 'parentId': IDS[1], 'name': 'Boots'},
                               {'id': IDS[1], 'parentId': IDS[0], 'name': 'Sale'}])
    association = observations(raw)[2]
    assert len(association.parent_edges) == 2
    assert association.reason == 'category_ancestry_invalid'
    assert association.completeness == 'partial'
    facets = [f for f in association.facts if f.binding.edge]
    assert {f.binding.facet for f in facets} == {'parent_id', 'child_id'}
    assert all(f.support == SupportState.OBSERVED for f in facets)
    assert all(f.binding.edge in association.parent_edges for f in facets)
    assert association.relation != 'ordered_path'


def test_c22_malformed_ids_preserve_valid_sibling_and_parent_reference_budget():
    result = observations(captured(categoryIds=[False, {}, IDS[0]],
        categories=[{'id': IDS[1], 'parentId': IDS[0], 'name': 'Boots'}]),
        limits=CategoryLimits(relation_refs=2))
    assert result[0].reason == 'category_budget_reached'
    assert not result[0].terms  # First two entries malformed; bounded parser does not scan beyond cap.
    assert sum(len(o.terms) + 2 * len(o.parent_edges) for o in result) <= 2


def test_c24_legacy_shopware_category_projection_unchanged():
    raw = capture({'id': 'legacy', 'name': 'Legacy boot', 'price': '9.99',
                   'categories': ['Boots', 'Sale']}, 'https://supplier.test/legacy', 'shopware_api')
    assert normalize(raw, platform=Platform.SHOPWARE, shop_url=SCOPE.store_url).category_path == ['Boots', 'Sale']
    terms = observations(raw)[2].terms
    assert [t.label for t in terms] == ['Boots', 'Sale']
    assert all(t.ref.native_id is None for t in terms)
