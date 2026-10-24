"""Final-review adverse cases designed before narrow local production repairs."""
import copy
from dataclasses import replace

import httpx
import pytest

from tests.test_woo_tree_acceptance import SCOPE, NOW, acquire, entry, page
from shopextract._capture import capture
from shopextract.categories.adapters.woocommerce import observe_categories
from shopextract.categories.contracts import AdapterContext
from shopextract.categories.woo_tree import link_tree_memberships, woo_tree_to_record, woo_tree_from_record


def captured_membership():
    raw = capture({'categories': [{'id': 1, 'name': 'One'}]},
                  SCOPE.store_url + '/wp-json/wc/store/v1/products/7', 'woocommerce_api', observed_at=NOW)
    return observe_categories(raw, context=AdapterContext(SCOPE))[0]


def altered_native(term, defect):
    native = next(f for f in term.facts if f.binding.facet == 'native_id')
    if defect == 'raw_value':
        broken = replace(native, raw_value=99)
    elif defect == 'source_values':
        broken = replace(native, outcome=replace(native.outcome, source_values=(99,)))
    else:
        evidence = copy.deepcopy(native.evidence[0])
        if defect == 'retained_value':
            evidence.retained_data['value'] = 99
            assert evidence.resolve_pointer() == 99
        elif defect == 'pointer':
            evidence.pointer = '/source_pointer'
            assert evidence.resolve_pointer() == '/categories/0/id'
        else:
            raise AssertionError('Unknown designed defect')
        broken = replace(native, evidence=(evidence,))
    return native, broken


@pytest.mark.parametrize('defect', ['raw_value', 'source_values', 'retained_value', 'pointer'])
async def test_membership_native_fact_raw_source_and_pointer_must_align(defect):
    tree, _ = await acquire([page([entry(1)], 1, 1)])
    observed = captured_membership()
    term = observed.terms[0]
    native, broken = altered_native(term, defect)
    bad_term = replace(term, facts=tuple(broken if f is native else f for f in term.facts))
    bad_observation = replace(observed, terms=(bad_term,))
    before = repr(bad_observation)
    links = link_tree_memberships(tree, (bad_observation,))
    assert len(links) == 1 and links[0].status == 'unsupported' and links[0].node_id is None
    assert repr(bad_observation) == before
    foreign = replace(bad_observation, scope=replace(SCOPE, store_url='https://foreign.example'))
    assert link_tree_memberships(tree, (foreign,))[0].status == 'scope_mismatch'


async def test_membership_independently_valid_native_fact_survives_bad_sibling():
    tree, _ = await acquire([page([entry(1)], 1, 1)])
    observed = captured_membership()
    term = observed.terms[0]
    native, broken = altered_native(term, 'raw_value')
    candidate = replace(term, facts=(broken,) + term.facts)
    assert link_tree_memberships(tree, (replace(observed, terms=(candidate,)),))[0].status == 'linked'
    label = next(f for f in term.facts if f.binding.facet == 'label')
    # The native-ID candidate remains supported despite an unrelated damaged label.
    other = replace(term, facts=(native, replace(label, raw_value=99)))
    assert link_tree_memberships(tree, (replace(observed, terms=(other,)),))[0].status == 'linked'


async def test_malformed_ipv6_initial_store_url_is_unavailable_without_io_and_replays():
    tree, calls = await acquire([], scope=replace(SCOPE, store_url='https://[broken'))
    assert tree.outcome == 'unavailable' and tree.reasons == ('unsafe_url',)
    assert calls == [] and tree.attempts == () and tree.pages == ()
    assert woo_tree_from_record(woo_tree_to_record(tree)) == tree


@pytest.mark.parametrize('later_page', [False, True])
async def test_escaped_lone_surrogate_is_malformed_json_and_retains_prior_pages(later_page):
    # Body bytes themselves are valid UTF-8; the JSON escape decodes to an
    # unpaired surrogate which cannot enter the canonical UTF-8 evidence model.
    body = b'[{"id":3,"name":"\\ud800","slug":"three","parent":1}]'
    assert body.decode('utf-8')
    broken = httpx.Response(200, content=body,
        headers={'X-WP-Total': '3' if later_page else '1', 'X-WP-TotalPages': '2' if later_page else '1'})
    responses = [page([entry(1), entry(2)], 3, 2), broken] if later_page else [broken]
    tree, calls = await acquire(responses)
    assert tree.outcome == ('partial' if later_page else 'malformed')
    assert 'malformed_json' in tree.reasons and not tree.confirmed_empty
    assert len(calls) == len(tree.attempts) == (2 if later_page else 1)
    assert len(tree.pages) == (1 if later_page else 0)
    assert {n.native_id for n in tree.nodes} == ({'1', '2'} if later_page else set())
    assert woo_tree_from_record(woo_tree_to_record(tree)) == tree
