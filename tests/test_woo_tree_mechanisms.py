"""Predesigned feature009 security/cleanup/resource/replay cases; no commercial HTTP."""
import asyncio
from dataclasses import replace
from datetime import datetime, timezone
import json
from types import SimpleNamespace

import httpx
import pytest

from shopextract._models import Platform
from shopextract.categories._codec import canonical, digest
from shopextract.categories.contracts import CategoryError, CategoryScope
from shopextract.categories.woo_tree import WooTreeLimits, fetch_woocommerce_category_tree, woo_tree_from_record, woo_tree_to_record
from shopextract.tools.context import OperationBudget, OperationContext
from shopextract.tools.contracts import ToolError
from shopextract.tools.runtime import Limits, ToolConfig
from shopextract.tools.security import PinnedBackend, SourceGuard

NOW = datetime(2026, 10, 24, 12, tzinfo=timezone.utc)
SCOPE = CategoryScope(Platform.WOOCOMMERCE, 'https://merchant.example/shop')
ROW = {'id': 1, 'name': 'One', 'slug': 'one', 'parent': 0}


async def resolve(host, context):
    return ['93.184.216.34']


async def run(responses, limits=WooTreeLimits(per_page=2), *, scope=SCOPE, cancelled=None):
    calls = []
    async def wire(request):
        calls.append(request)
        return responses[len(calls) - 1]
    value = await fetch_woocommerce_category_tree(scope, limits=limits, resolver=resolve,
        wire_transport=httpx.MockTransport(wire), utc_now=lambda: NOW, cancelled=cancelled)
    return value, calls


def response(rows, total=1, pages=1):
    return httpx.Response(200, json=rows, headers={'X-WP-Total': str(total), 'X-WP-TotalPages': str(pages)})


async def test_real_pinned_backend_connects_checked_numeric_ip_and_rejects_rebinding():
    config = ToolConfig(allowed_origins=('https://merchant.example',))
    context = OperationContext('synthetic', asyncio.get_running_loop().time() + 1,
        asyncio.Event(), OperationBudget(Limits()), None, NOW)
    addresses = iter([['93.184.216.34'], ['1.1.1.1'], ['127.0.0.1']])
    async def changing(host, context):
        return next(addresses)
    guard = SourceGuard(config, resolver=changing)
    await guard.authorize(SCOPE.store_url, context)
    backend = PinnedBackend(context, guard, 'https')
    connected = []
    async def connect(host, port, **kwargs):
        connected.append((host, port))
        return 'controlled-socket'
    backend.backend = SimpleNamespace(connect_tcp=connect)
    assert await backend.connect_tcp('merchant.example', 443) == 'controlled-socket'
    assert connected == [('1.1.1.1', 443)]
    with pytest.raises(ToolError):
        await backend.connect_tcp('merchant.example', 443)
    assert len(connected) == 1


class BlockingStream(httpx.AsyncByteStream):
    def __init__(self):
        self.started = asyncio.Event()
        self.closed = False
    async def __aiter__(self):
        self.started.set()
        await asyncio.Event().wait()
        yield b''
    async def aclose(self):
        self.closed = True


@pytest.mark.parametrize('mode', ['event', 'deadline', 'external_task'])
async def test_blocked_body_cancel_deadline_and_external_task_cleanup(mode):
    stream = BlockingStream()
    event = asyncio.Event()
    task = asyncio.create_task(run([httpx.Response(200, stream=stream)],
        limits=WooTreeLimits(seconds=.05), cancelled=event))
    started = asyncio.create_task(stream.started.wait())
    done, _ = await asyncio.wait((task, started), timeout=.5, return_when=asyncio.FIRST_COMPLETED)
    if task in done:
        started.cancel()
        await task  # Explicit missing-operation red propagates before stream entry.
    assert started in done
    if mode == 'event':
        event.set()
    elif mode == 'external_task':
        task.cancel()
    if mode == 'external_task':
        with pytest.raises(asyncio.CancelledError):
            await task
    else:
        value, calls = await asyncio.wait_for(task, .5)
        assert value.outcome == 'unavailable' and len(calls) == 1
        assert ('cancelled' if mode == 'event' else 'deadline') in value.reasons
    assert stream.closed


@pytest.mark.parametrize('delta', [-1, 0, 1])
async def test_response_bytes_below_at_above_boundary(delta):
    source = response([ROW])
    size = len(source.content)
    value, calls = await run([source], limits=WooTreeLimits(response_bytes=size + delta))
    assert len(calls) == 1
    assert value.outcome == ('unavailable' if delta == -1 else 'complete')
    assert bool(value.pages) == (delta >= 0)


async def test_retained_envelope_overhead_exceeds_cap_with_fitting_raw_body():
    row = dict(ROW, name='x' * 3000)
    source = response([row])
    assert len(source.content) < 8192
    value, _ = await run([source], limits=WooTreeLimits(retained_bytes=8192))
    assert value.outcome == 'unavailable' and value.pages == ()
    assert 'retention_limit' in value.reasons
    # A diagnostic result still serializes when the minimal envelope fits.
    assert len(canonical(woo_tree_to_record(value)).encode()) <= 8192


@pytest.mark.parametrize('field', ['parent_edges', 'nodes', 'outcome'])
async def test_reload_rejects_tampered_projection_even_with_recomputed_digest(field):
    value, _ = await run([response([ROW])])
    record = woo_tree_to_record(value)
    if field == 'parent_edges':
        record['payload'][field] = [['1', '99']]
    elif field == 'nodes':
        record['payload'][field][0]['declarations'][0]['facts'][1]['value'] = 'Forged'
    else:
        record['payload'][field] = 'partial'
        record['payload']['confirmed_empty'] = True
    record['sha256'] = digest(record['payload'])
    with pytest.raises(CategoryError):
        woo_tree_from_record(record)


async def test_reload_partial_cannot_be_promoted_by_recomputed_digest():
    value, _ = await run([response([ROW, dict(ROW, id=2, slug='two')], total=3, pages=2)],
                         limits=WooTreeLimits(requests=1, per_page=2))
    record = woo_tree_to_record(value)
    record['payload']['outcome'] = 'complete'
    record['payload']['reasons'] = []
    record['sha256'] = digest(record['payload'])
    with pytest.raises(CategoryError):
        woo_tree_from_record(record)


async def test_base_path_and_metadata_limits():
    value, calls = await run([response([ROW])])
    assert calls[0].url.path == '/shop/wp-json/wc/store/v1/products/categories'
    assert value.pages[0].source_url.startswith(SCOPE.store_url)
    denied, calls = await run([], scope=replace(SCOPE, store_url='https://merchant.example/' + 'x' * 4096))
    assert denied.outcome == 'unavailable' and calls == []
    oversized = httpx.Response(200, json=[ROW], headers={'X-WP-Total': '9' * 21, 'X-WP-TotalPages': '1'})
    partial, calls = await run([oversized])
    assert partial.outcome == 'partial' and len(calls) == 1
    assert 'malformed_headers' in partial.reasons
    assert partial.pages[0].total is None  # invalid remote metadata is never retained unbounded


async def test_identity_reorder_and_duplicate_accounting():
    a = ROW
    b = dict(ROW, id=2, slug='two', parent=1)
    first, _ = await run([response([a, b], 2, 1)])
    other, _ = await run([response([b, a], 2, 1)])
    assert [(n.native_id, n.conflicted) for n in first.nodes] == [(n.native_id, n.conflicted) for n in other.nodes]
    assert first.parent_edges == other.parent_edges
    duplicate, _ = await run([response([a, a], 2, 1)], limits=WooTreeLimits(categories=1, per_page=2))
    assert duplicate.pages == () and 'category_limit' in duplicate.reasons


async def test_same_origin_redirect_charges_each_wire_attempt():
    value, calls = await run([httpx.Response(302, headers={'Location': SCOPE.store_url + '/wp-json/wc/store/v1/products/categories?page=1&per_page=2&hide_empty=false&orderby=slug&order=asc'}), response([ROW])])
    assert value.outcome == 'complete'
    assert len(calls) == len(value.attempts) == 2
    assert [a.status_code for a in value.attempts] == [302, 200]
    assert all(len(a.url_sha256) == 64 for a in value.attempts)


async def test_opaque_string_zero_parent_is_a_real_category_reference():
    zero = dict(ROW, id='0', slug='zero', parent=0)
    child = dict(ROW, id='x', slug='child', parent='0')
    value, _ = await run([response([zero, child], 2, 1)])
    assert value.outcome == 'complete'
    assert value.parent_edges == (('x', '0'),)
    assert woo_tree_from_record(woo_tree_to_record(value)) == value


@pytest.mark.parametrize('defect', ['path', 'query', 'success_attempt'])
async def test_reload_rejects_page_provenance_tamper_with_recomputed_digest(defect):
    value, _ = await run([response([ROW])])
    record = woo_tree_to_record(value)
    if defect in ('path', 'query'):
        url = record['payload']['pages'][0]['source_url']
        changed = url.replace('/products/categories', '/unrelated') if defect == 'path' else url.replace('hide_empty=false', 'hide_empty=true')
        record['payload']['pages'][0]['source_url'] = changed
        # Keep all derived fact URLs coherent; provenance validation must reject.
        for fact in record['payload']['nodes'][0]['declarations'][0]['facts']:
            fact['source_url'] = changed
    else:
        record['payload']['attempts'][0]['status_code'] = 503
    record['sha256'] = digest(record['payload'])
    with pytest.raises(CategoryError):
        woo_tree_from_record(record)


@pytest.mark.parametrize('bad_url', [None, 7, True, [], {}])
async def test_invalid_scope_store_url_types_reject_cleanly_before_io(bad_url):
    with pytest.raises(CategoryError):
        await run([], scope=replace(SCOPE, store_url=bad_url))


async def test_exact_canonical_retention_threshold_with_bounded_black_box_search():
    """Discover public admission threshold; never call the reservation implementation."""
    base = WooTreeLimits()
    invocations = 0
    async def probe(cap):
        nonlocal invocations
        invocations += 1
        assert invocations <= 17  # One upper probe + <=13 bisections + three edges.
        value, calls = await run([response([ROW])], limits=replace(base, retained_bytes=cap))
        assert len(calls) <= 1
        if value.outcome != 'complete':
            assert value.pages == () and 'retention_limit' in value.reasons
        return value
    lower, upper = 0, 8192
    assert (await probe(upper)).outcome == 'complete'
    while upper - lower > 1:
        middle = (upper + lower) // 2
        if (await probe(middle)).outcome == 'complete':
            upper = middle
        else:
            lower = middle
    threshold = upper
    states = []
    for delta in (-1, 0, 1):
        value = await probe(threshold + delta)
        assert value.outcome == ('unavailable' if delta < 0 else 'complete')
        assert bool(value.pages) == (delta >= 0)
        encoded_size = len(canonical(woo_tree_to_record(value)).encode())
        assert encoded_size <= threshold + delta
        states.append((delta, value.outcome, encoded_size))
    assert len(response([ROW]).content) < threshold - 1
    print(json.dumps({'retention_threshold': threshold, 'probes': invocations, 'edges': states}))


@pytest.mark.parametrize('defect', ['path', 'query'])
async def test_changed_category_route_or_query_redirect_denied_before_destination_wire(defect):
    target = SCOPE.store_url + '/wp-json/wc/store/v1/products/categories?page=1&per_page=2&hide_empty=false&orderby=slug&order=asc'
    target = target.replace('/products/categories', '/unrelated') if defect == 'path' else target.replace('hide_empty=false', 'hide_empty=true')
    value, calls = await run([httpx.Response(302, headers={'Location': target})])
    assert value.outcome == 'unavailable' and 'unsafe_url' in value.reasons
    assert len(calls) == len(value.attempts) == 1
    assert value.attempts[0].status_code == 302 and value.pages == ()


async def test_trailing_slash_redirect_retains_actual_guarded_hop_provenance():
    target = SCOPE.store_url + '/wp-json/wc/store/v1/products/categories/?page=1&per_page=2&hide_empty=false&orderby=slug&order=asc'
    value, calls = await run([httpx.Response(302, headers={'Location': target}), response([ROW])])
    assert value.outcome == 'complete' and len(calls) == 2
    assert value.pages[0].source_url == target
    assert all(f.source_url == target for f in value.nodes[0].declarations[0].facts)
    import hashlib
    assert value.attempts[-1].url_sha256 == hashlib.sha256(target.encode()).hexdigest()
    assert woo_tree_from_record(woo_tree_to_record(value)) == value


async def test_mixed_public_and_private_dns_answers_deny_before_wire():
    wire_calls = []
    async def mixed(host, context):
        return ['93.184.216.34', '127.0.0.1']
    async def wire(request):
        wire_calls.append(request)
        return response([ROW])
    value = await fetch_woocommerce_category_tree(SCOPE, resolver=mixed,
        wire_transport=httpx.MockTransport(wire), utc_now=lambda: NOW)
    assert value.outcome == 'unavailable' and 'unsafe_url' in value.reasons
    assert wire_calls == [] and value.attempts == ()
