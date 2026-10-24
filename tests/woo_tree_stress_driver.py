"""Reviewed-before-execution deterministic feature009 driver; no live network.

Run: PYTHONPATH=src .venv/bin/python tests/woo_tree_stress_driver.py
One sequential process, seed00920261024, 24 predeclared cases, 60s total.
"""
import asyncio
from dataclasses import replace
import json
from pathlib import Path
import resource
import sys
import time

import httpx

from test_woo_tree_acceptance import entry, page, acquire, SCOPE, NOW
from test_woo_tree_mechanisms import BlockingStream
from shopextract._capture import capture
from shopextract.categories.adapters.woocommerce import observe_categories
from shopextract.categories.contracts import AdapterContext
from shopextract.categories._codec import canonical
from shopextract.categories.woo_tree import (
    WooTreeLimits, link_tree_memberships, woo_tree_to_record, woo_tree_from_record,
)

ROOT = Path(__file__).resolve().parents[1] / 'specs/009-woocommerce-category-tree/evidence'
SEED = '00920261024'
CASES = (
    'topology_orphan', 'topology_self', 'topology_cycle', 'depth_7', 'depth_8', 'depth_9',
    'pagination_repeat', 'pagination_conflict', 'pagination_reorder', 'pagination_drift', 'terminal_fit', 'later_failure',
    'requests_fit', 'requests_exhausted', 'items_1000_fit', 'items_above_cap',
    'body_exact_fit', 'body_one_over', 'retained_fit', 'retained_overhead_over',
    'duplicate_and_bytes', 'partial_replay', 'two_scopes_same_id', 'cancel_after_redirect',
)


def peak_bytes():
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return peak if sys.platform == 'darwin' else peak * 1024


async def execute(name):
    if name.startswith('topology_') or name.startswith('depth_'):
        if name == 'topology_orphan':
            rows, code = [entry(1, 99)], 'missing_parent'
        elif name == 'topology_self':
            rows, code = [entry(1, 1)], 'self_parent'
        elif name == 'topology_cycle':
            rows, code = [entry(1, 2), entry(2, 1)], 'cycle'
        else:
            depth = int(name[-1])
            rows = [entry(1)] + [entry(i, i - 1) for i in range(2, depth + 2)]
            code = 'depth_limit' if depth == 9 else None
        tree, calls = await acquire([page(rows, len(rows), 1)], limits=WooTreeLimits(per_page=len(rows)))
        codes = {i.code for i in tree.issues}
        assert (code in codes) if code else not codes
        if name.startswith('depth_'):
            assert len(tree.parent_edges) == min(int(name[-1]), 8)
    elif name == 'pagination_repeat':
        rows = [entry(1), entry(2)]
        tree, calls = await acquire([page(rows, 4, 2), page(rows, 4, 2)])
        assert tree.outcome == 'partial' and 'repeated_page' in tree.reasons
    elif name == 'pagination_conflict':
        tree, calls = await acquire([page([entry(1), entry(1, name='Changed')], 2, 1)])
        assert tree.outcome == 'partial' and tree.nodes[0].conflicted
        assert len(tree.nodes[0].declarations) == 2
    elif name == 'pagination_reorder':
        first, _ = await acquire([page([entry(1), entry(2, 1)], 2, 1)])
        tree, calls = await acquire([page([entry(2, 1), entry(1)], 2, 1)])
        assert first.parent_edges == tree.parent_edges == (('2', '1'),)
        assert [n.native_id for n in first.nodes] == [n.native_id for n in tree.nodes]
    elif name == 'pagination_drift':
        tree, calls = await acquire([page([entry(1), entry(2)], 3, 2), page([entry(3)], 4, 2)])
        assert tree.outcome == 'partial' and 'totals_changed' in tree.reasons
    elif name in ('terminal_fit', 'requests_fit', 'requests_exhausted', 'partial_replay'):
        if name == 'terminal_fit':
            tree, calls = await acquire([page([entry(1), entry(2)], 2, 1)],
                limits=WooTreeLimits(per_page=2, categories=2, requests=1))
            assert tree.outcome == 'complete' and len(calls) == 1
        else:
            count = 2 if name == 'requests_fit' else 1
            tree, calls = await acquire([page([entry(1), entry(2)], 3, 2), page([entry(3)], 3, 2)],
                limits=WooTreeLimits(per_page=2, requests=count))
            assert len(calls) == count
            assert tree.outcome == ('complete' if count == 2 else 'partial')
            if name == 'partial_replay':
                assert woo_tree_from_record(woo_tree_to_record(tree)) == tree
                assert not tree.confirmed_empty
    elif name == 'later_failure':
        tree, calls = await acquire([page([entry(1), entry(2)], 3, 2), page({}, status=503)])
        assert tree.outcome == 'partial' and len(tree.nodes) == 2 and len(calls) == 2
    elif name == 'items_1000_fit':
        responses = [page([entry(i) for i in range(start, start + 100)], 1000, 10) for start in range(1, 1001, 100)]
        tree, calls = await acquire(responses, limits=WooTreeLimits())
        assert tree.outcome == 'complete' and len(tree.nodes) == 1000 and len(calls) == 10
    elif name == 'items_above_cap':
        # Reduced cap isolates item exhaustion from the independent 10-request cap.
        tree, calls = await acquire([page([entry(1), entry(2)], 4, 2), page([entry(3), entry(4)], 4, 2)],
            limits=WooTreeLimits(per_page=2, categories=3))
        assert tree.outcome == 'partial' and 'category_limit' in tree.reasons
        assert len(tree.nodes) == 2 and len(tree.pages) == 1  # page atomicity
    elif name in ('body_exact_fit', 'body_one_over'):
        source = page([entry(1)], 1, 1)
        cap = len(source.content) - (name == 'body_one_over')
        tree, calls = await acquire([source], limits=WooTreeLimits(response_bytes=cap))
        assert tree.outcome == ('unavailable' if name == 'body_one_over' else 'complete')
    elif name in ('retained_fit', 'retained_overhead_over', 'duplicate_and_bytes'):
        row = entry(1, name='x' * (3000 if name != 'retained_fit' else 32))
        rows = [row, row] if name == 'duplicate_and_bytes' else [row]
        source = page(rows, len(rows), 1)
        assert len(source.content) < 8192  # Only full evidence overhead crosses cap.
        tree, calls = await acquire([source], limits=WooTreeLimits(retained_bytes=8192, per_page=2))
        assert tree.outcome == ('complete' if name == 'retained_fit' else 'unavailable')
        if name != 'retained_fit':
            assert tree.pages == () and 'retention_limit' in tree.reasons
    elif name == 'two_scopes_same_id':
        tree, calls = await acquire([page([entry(1)], 1, 1)])
        foreign = replace(SCOPE, store_url='https://foreign.example')
        second, _ = await acquire([page([entry(1)], 1, 1)], scope=foreign)
        raw = capture({'categories': [{'id': 1, 'name': 'One'}]},
            SCOPE.store_url + '/wp-json/wc/store/v1/products/7', 'woocommerce_api', observed_at=NOW)
        observations = observe_categories(raw, context=AdapterContext(SCOPE))
        assert link_tree_memberships(tree, observations)[0].status == 'linked'
        assert link_tree_memberships(second, observations)[0].status == 'scope_mismatch'
    elif name == 'cancel_after_redirect':
        event, stream = asyncio.Event(), BlockingStream()
        target = SCOPE.store_url + '/wp-json/wc/store/v1/products/categories?page=1&per_page=2&hide_empty=false&orderby=slug&order=asc'
        task = asyncio.create_task(acquire([httpx.Response(302, headers={'Location': target}), httpx.Response(200, stream=stream)], cancelled=event))
        await asyncio.wait_for(stream.started.wait(), 1)
        event.set()
        tree, calls = await task
        assert tree.outcome == 'unavailable' and len(calls) == 2 and stream.closed
        assert 'cancelled' in tree.reasons
    else:
        raise AssertionError('Undeclared case')
    assert len(calls) <= tree.limits.requests
    assert sum(len(json.loads(p.body)) for p in tree.pages) <= tree.limits.categories
    assert len(canonical(woo_tree_to_record(tree)).encode()) <= tree.limits.retained_bytes
    assert woo_tree_from_record(woo_tree_to_record(tree)) == tree
    return {'case': name, 'outcome': tree.outcome, 'nodes': len(tree.nodes), 'attempts': len(tree.attempts), 'passed': True}


async def run_all():
    ROOT.mkdir(exist_ok=True)
    output = {'provenance': 'deterministic_synthetic_controlled_http', 'seed': SEED,
        'workers': 1, 'deadline_seconds': 60, 'rss_limit_bytes': 256 * 1024 * 1024,
        'rss_enforcement': 'observed peak check after each case; not OS memory reservation',
        'planned_count': len(CASES), 'results': [], 'complete': False}
    start = time.monotonic()
    for name in CASES:
        try:
            remaining = 60 - (time.monotonic() - start)
            result = await asyncio.wait_for(execute(name), max(0, remaining))
            if time.monotonic() - start > 60:
                raise RuntimeError('Driver deadline exceeded during synchronous case work')
            if peak_bytes() > output['rss_limit_bytes']:
                raise RuntimeError('Observed peak RSS exceeded 256 MiB')
            output['results'].append(result)
        except Exception as error:
            output['failure'] = {'case': name, 'type': type(error).__name__, 'message': str(error)[:160]}
            break
        finally:
            output['elapsed_seconds'] = round(time.monotonic() - start, 3)
            output['peak_rss_bytes'] = peak_bytes()
            (ROOT / 'stress-results.json').write_text(json.dumps(output, indent=2) + '\n')
    output['complete'] = len(output['results']) == len(CASES)
    (ROOT / 'stress-results.json').write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps({k: output[k] for k in ('complete', 'planned_count', 'elapsed_seconds', 'peak_rss_bytes')}))
    return output['complete']


if __name__ == '__main__':
    raise SystemExit(0 if asyncio.run(run_all()) else 1)
