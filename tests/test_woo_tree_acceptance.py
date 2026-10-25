"""Feature 009 synthetic acceptance; real acquisition/parser/graph paths, controlled HTTP."""
import asyncio
from dataclasses import replace
from datetime import datetime, timedelta, timezone

import httpx
import pytest

from shopextract._capture import capture
from shopextract._evidence import SupportState
from shopextract._models import Platform
from shopextract.categories.adapters.woocommerce import observe_categories
from shopextract.categories.contracts import AdapterContext, CategoryError, CategoryScope
from shopextract.categories.woo_tree import (
    WooCategoryTree, WooTreeLimits, fetch_woocommerce_category_tree, link_tree_memberships,
    woo_tree_from_record, woo_tree_to_record,
)

SCOPE = CategoryScope(Platform.WOOCOMMERCE, 'https://merchant.example')
NOW = datetime(2026, 10, 24, 12, tzinfo=timezone.utc)


def entry(native, parent=0, name=None):
    return dict(id=native, name=name or f'Category {native}', slug=f'category-{native}', parent=parent)


def page(rows, total=None, pages=None, status=200):
    headers = {} if total is None else {'X-WP-Total': str(total), 'X-WP-TotalPages': str(pages)}
    return httpx.Response(status, json=rows, headers=headers)


async def acquire(responses, *, limits=None, scope=SCOPE, resolver=None, cancelled=None, utc_now=None):
    requests = []
    async def public_resolver(host, context):
        return ['93.184.216.34']
    async def wire(request):
        requests.append(request)
        assert request.url.params['hide_empty'] == 'false'
        assert request.url.params['orderby'] == 'slug'
        return responses[len(requests) - 1]
    result = await fetch_woocommerce_category_tree(
        scope, limits=limits or WooTreeLimits(per_page=2),
        resolver=resolver or public_resolver, wire_transport=httpx.MockTransport(wire),
        utc_now=utc_now or (lambda: NOW), cancelled=cancelled)
    return result, requests


async def test_tree_pages_preserve_scope_evidence():
    receipts = (NOW, NOW + timedelta(seconds=1))
    clock = iter(receipts)
    result, requests = await acquire([page([entry(1), entry(2, 1)], 3, 2), page([entry(3, 1)], 3, 2)],
                                     utc_now=lambda: next(clock))
    assert result.outcome == 'complete' and not result.confirmed_empty
    assert {n.native_id for n in result.nodes} == {'1', '2', '3'}
    assert set(result.parent_edges) == {('2', '1'), ('3', '1')}
    assert [p.number for p in result.pages] == [1, 2]
    assert [r.url.params['page'] for r in requests] == ['1', '2']
    fact = result.nodes[-1].declarations[0].facts[0]
    assert tuple(p.observed_at for p in result.pages) == receipts
    assert fact.pointer == '/0/id' and fact.observed_at == receipts[1]
    assert result.nodes[0].declarations[0].facts[0].observed_at == receipts[0]
    assert 'page=2' in fact.source_url


@pytest.mark.parametrize(('responses', 'outcome', 'empty', 'calls'), [
    ([page([], 0, 0)], 'complete', True, 1),
    ([page([]), page([], 0, 0)], 'complete', True, 2),
    ([page([entry(1)]), page([], 1, 1)], 'complete', False, 2),
    ([page([]), page([])], 'partial', False, 2),
    ([page([entry(1), entry(2)])], 'partial', False, 1),
    ([page([entry(1)]), page([entry(2)], 1, 1)], 'partial', False, 2),
    ([page([], 0, 1)], 'partial', False, 1),
])
async def test_empty_requires_coverage(responses, outcome, empty, calls):
    value, requests = await acquire(responses)
    assert (value.outcome, value.confirmed_empty, len(requests)) == (outcome, empty, calls)


async def test_tree_facet_states():
    rows = [entry(1), entry(2, None), entry(3, False), entry(True), entry('opaque')]
    rows[0].pop('parent')
    rows[1]['name'] = 'Boots &amp; Été'
    result, _ = await acquire([page(rows, 5, 1)], limits=WooTreeLimits(per_page=5))
    assert result.outcome == 'partial'
    nodes = {n.native_id: n for n in result.nodes}
    states = {i: {f.facet: f for f in n.declarations[0].facts} for i, n in nodes.items()}
    assert states['1']['parent'].state == 'missing'
    assert states['2']['parent'].state == 'null'
    assert states['3']['parent'].state == 'malformed'
    assert states['2']['name'].value == 'Boots &amp; Été'
    assert 'opaque' in nodes and len(result.rejected) == 1
    assert result.parent_edges == ()


@pytest.mark.parametrize(('rows', 'code'), [
    ([entry(1, 99)], 'missing_parent'),
    ([entry(1, 1)], 'self_parent'),
    ([entry(1, 2), entry(2, 1)], 'cycle'),
    ([entry(1)] + [entry(i, i - 1) for i in range(2, 11)], 'depth_limit'),
])
async def test_tree_topology_adversaries(rows, code):
    result, _ = await acquire([page(rows, len(rows), 1)], limits=WooTreeLimits(per_page=len(rows)))
    assert code in {i.code for i in result.issues}
    assert all(child != parent for child, parent in result.parent_edges)
    if code == 'cycle':
        assert result.parent_edges == ()
    if code == 'depth_limit':
        assert ('9', '8') in result.parent_edges and ('10', '9') not in result.parent_edges


@pytest.mark.parametrize(('responses', 'reason'), [
    ([page([entry(1), entry(2)], 4, 2), page([entry(1), entry(2)], 4, 2)], 'repeated_page'),
    ([page([entry(1), entry(2)], 3, 2), page([entry(3)], 4, 2)], 'totals_changed'),
    ([page([entry(1), entry(1, name='Other')], 2, 1)], 'conflicting_id'),
])
async def test_pagination_mutation_and_duplicates(responses, reason):
    result, requests = await acquire(responses)
    assert result.outcome == 'partial' and reason in result.reasons
    assert len(requests) == len(responses)
    if reason == 'conflicting_id':
        assert len(result.nodes) == 1 and result.nodes[0].conflicted
        assert len(result.nodes[0].declarations) == 2


@pytest.mark.parametrize(('responses', 'outcome', 'retained'), [
    ([page({}, status=403)], 'unavailable', 0),
    ([page({}, status=404)], 'unavailable', 0),
    ([httpx.Response(200, content=b'bad json')], 'malformed', 0),
    ([page({'id': 1})], 'malformed', 0),
    ([page([entry(1), entry(2)], 3, 2), page({}, status=503)], 'partial', 2),
])
async def test_tree_failure_retention(responses, outcome, retained):
    result, _ = await acquire(responses)
    assert result.outcome == outcome and len(result.nodes) == retained
    assert not result.confirmed_empty


@pytest.mark.parametrize('field', ['requests', 'categories', 'per_page', 'response_bytes', 'retained_bytes', 'seconds'])
async def test_zero_work_budget_performs_no_call(field):
    result, requests = await acquire([], limits=replace(WooTreeLimits(), **{field: 0}))
    assert requests == [] and result.outcome == 'unavailable'


@pytest.mark.parametrize(('field', 'value'), [('requests', True), ('categories', -1), ('per_page', 101), ('seconds', float('nan'))])
async def test_invalid_budget_rejects_before_io(field, value):
    with pytest.raises(CategoryError):
        await acquire([], limits=replace(WooTreeLimits(), **{field: value}))


async def test_tree_budget_page_atomic_and_terminal_fit():
    exact, _ = await acquire([page([entry(1), entry(2)], 2, 1)], limits=WooTreeLimits(per_page=2, categories=2, requests=1))
    assert exact.outcome == 'complete'
    limited, requests = await acquire([page([entry(1), entry(2)], 3, 2), page([entry(3)], 3, 2)], limits=WooTreeLimits(per_page=2, categories=2))
    assert limited.outcome == 'partial' and len(limited.nodes) == 2 and len(requests) == 1
    refused, _ = await acquire([page([entry(1), entry(2)], 2, 1)], limits=WooTreeLimits(per_page=2, categories=1))
    assert refused.pages == () and refused.nodes == ()


async def test_tree_guard_and_redirect():
    async def private(host, context):
        return ['127.0.0.1']
    denied, calls = await acquire([], resolver=private)
    assert denied.outcome == 'unavailable' and calls == []
    redirect, calls = await acquire([httpx.Response(302, headers={'Location': 'https://foreign.example/categories'})])
    assert redirect.outcome == 'unavailable' and len(calls) == 1
    assert len(redirect.attempts) == 1


class SingleChunk(httpx.AsyncByteStream):
    async def __aiter__(self):
        yield b'not-decoded'


async def test_tree_identity_encoding_only():
    result, requests = await acquire([httpx.Response(200, stream=SingleChunk(), headers={'Content-Encoding': 'gzip'})])
    assert len(requests) == 1 and result.outcome == 'unavailable'
    assert result.pages == ()


async def test_tree_pre_cancelled_performs_no_io():
    event = asyncio.Event()
    event.set()
    result, requests = await acquire([], cancelled=event)
    assert result.outcome == 'unavailable' and requests == []
    assert 'cancelled' in result.reasons


async def test_tree_codec_partial_replay_and_tamper():
    result, _ = await acquire([page([entry(1), entry(2)], 3, 2)], limits=WooTreeLimits(per_page=2, requests=1))
    record = woo_tree_to_record(result)
    assert woo_tree_from_record(record) == result
    record['payload']['outcome'] = 'complete'
    with pytest.raises(CategoryError):
        woo_tree_from_record(record)


async def test_tree_links_only_captured_memberships_without_mutation():
    result, _ = await acquire([page([entry(1), entry(2)], 2, 1)])
    raw = capture({'categories': [{'id': 1, 'name': 'One'}, {'id': 99, 'name': 'Unknown'}]},
                  SCOPE.store_url + '/wp-json/wc/store/v1/products/7', 'woocommerce_api', observed_at=NOW)
    observations = observe_categories(raw, context=AdapterContext(SCOPE))
    before = repr(observations)
    links = link_tree_memberships(result, observations)
    assert [(i.term.native_id, i.status) for i in links] == [('1', 'linked'), ('99', 'missing')]
    assert repr(observations) == before
    assert all(i.term.native_id != '2' for i in links)
    foreign = replace(observations[0], scope=replace(SCOPE, store_url='https://foreign.example'))
    assert all(i.status == 'scope_mismatch' for i in link_tree_memberships(result, (foreign,)))


def empty_tree():
    return WooCategoryTree(SCOPE, WooTreeLimits(), 'unavailable', False,
                           ('cancelled',), (), (), (), (), (), ())


def test_tree_codec_declared_empty_envelope_round_trip():
    value = empty_tree()
    record = woo_tree_to_record(value)
    assert set(record) == {'schema_version', 'payload', 'sha256'}
    assert woo_tree_from_record(record) == value


def test_tree_codec_rejects_missing_envelope_fields():
    with pytest.raises(CategoryError):
        woo_tree_from_record({})


def test_tree_membership_link_empty_observations():
    assert link_tree_memberships(empty_tree(), ()) == ()


@pytest.mark.parametrize('defect', ['missing', 'rejected', 'mismatched', 'no_evidence', 'unknown_support', 'wrong_binding'])
def test_tree_membership_requires_supported_native_id_fact(defect):
    raw = capture({'categories': [{'id': 1, 'name': 'One'}]},
                  SCOPE.store_url + '/wp-json/wc/store/v1/products/7', 'woocommerce_api', observed_at=NOW)
    observed = observe_categories(raw, context=AdapterContext(SCOPE))[0]
    term = observed.terms[0]
    native = next(f for f in term.facts if f.binding.facet == 'native_id')
    if defect == 'missing':
        facts = tuple(f for f in term.facts if f is not native)
    else:
        if defect == 'rejected':
            broken = replace(native, outcome=replace(native.outcome, accepted=False))
        elif defect == 'mismatched':
            broken = replace(native, outcome=replace(native.outcome, normalized_value='99'))
        elif defect == 'no_evidence':
            broken = replace(native, evidence=())
        elif defect == 'unknown_support':
            broken = replace(native, support=SupportState.UNKNOWN)
        else:
            broken = replace(native, binding=replace(native.binding, term=replace(term.ref, native_id='99')))
        facts = tuple(broken if f is native else f for f in term.facts)
    weakened = replace(observed, terms=(replace(term, facts=facts),))
    links = link_tree_memberships(empty_tree(), (weakened,))
    assert len(links) == 1 and links[0].status == 'unsupported'
    assert links[0].node_id is None
    foreign = replace(weakened, scope=replace(SCOPE, store_url='https://foreign.example'))
    assert link_tree_memberships(empty_tree(), (foreign,))[0].status == 'scope_mismatch'
