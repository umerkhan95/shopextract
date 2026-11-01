"""Distinct category/source/recovery interactions through native production paths."""
import asyncio
from datetime import timedelta
import time
import httpx
import pytest
from shopextract.maintenance import Budgets, MaintenanceError
from tests.test_maintenance_acceptance import Harness, baseline, goal, NOW, ORIGIN, parsed_supplier, supplier_html


@pytest.mark.asyncio
@pytest.mark.parametrize('category,field,before,after,comparison', [
    ('hardware-v1','attributes/ram','8 GB','16 GB','different'),
    ('hardware-v1','attributes/material','steel','aluminium','different'),
    ('footwear-v1','attributes/size','9','10','different'),
    ('footwear-v1','attributes/material','leather','textile','different'),
    ('hardware-v1','attributes/weight','1000 g','1 kg','equal'),
    ('footwear-v1','attributes/weight','1000 g','1 kg','equal')])
async def test_category_specs_remain_visible_without_overriding_matcher(tmp_path, category, field, before, after, comparison):
    name = field.split('/')[1]
    left_attributes, right_attributes = {name: before}, {name: after}
    if field == 'attributes/size':
        left_attributes['size_system'] = right_attributes['size_system'] = 'UK'
    h = Harness(tmp_path / 'jobs.db', attributes=right_attributes)
    _, report = await h.run(goal(baseline=(baseline(attributes=left_attributes),),
        fields=(field,), profiles={'S1': category}))
    finding, = report['findings']
    assert finding['before'] == before and finding['after'] == after
    assert finding['comparison'] == comparison
    assert finding['status'] == 'needs_review'
    assert finding['reason'] == 'identity_unresolved'
    assert finding['evidence_ids']
    if comparison == 'equal':
        assert finding['normalized_before'] == finding['normalized_after'] == '1'
        assert finding['trace']


@pytest.mark.asyncio
async def test_captured_baseline_preserves_evidence_instead_of_defaults(tmp_path):
    from shopextract._portable import product_to_record
    captured = product_to_record(parsed_supplier())
    h = Harness(tmp_path / 'jobs.db')
    _, report = await h.run(goal(baseline=(captured,), baseline_mode='captured'))
    finding, = report['findings']
    assert finding['status'] == 'unchanged'
    assert finding['baseline_support']['kind'] == 'captured'
    assert finding['baseline_support']['evidence_ids']
    assert finding['baseline_support']['observed_at'] == NOW.isoformat()


@pytest.mark.asyncio
async def test_real_source_category_conflict_vetoes_identifier_match(tmp_path):
    _, report = await Harness(tmp_path / 'jobs.db', category='Boots').run()
    assert report['findings'][0]['status'] == 'needs_review'
    assert report['findings'][0]['reason'] == 'category_mismatch'


@pytest.mark.asyncio
async def test_cancel_active_wire_releases_owner_before_ack(tmp_path):
    h = Harness(tmp_path / 'jobs.db')
    entered = asyncio.Event()
    async def waiting(request):
        entered.set()
        await asyncio.Event().wait()
    h.engine.wire_transport = httpx.MockTransport(waiting)
    key = h.store.create(goal())
    task = asyncio.create_task(h.engine.run(key))
    await asyncio.wait_for(entered.wait(), 2)
    status = await h.engine.cancel(key)
    result = await asyncio.wait_for(task, 2)
    assert status['state'] == result['state'] == 'cancelled'
    assert result['findings'] == []
    assert h.store._lock is None


@pytest.mark.asyncio
async def test_same_store_second_engine_cannot_release_active_owner(tmp_path):
    from shopextract.maintenance import MaintenanceEngine
    h = Harness(tmp_path / 'jobs.db')
    entered = asyncio.Event()
    async def waiting(request):
        entered.set()
        await asyncio.Event().wait()
    h.engine.wire_transport = httpx.MockTransport(waiting)
    key = h.store.create(goal())
    task = asyncio.create_task(h.engine.run(key))
    await asyncio.wait_for(entered.wait(), 2)
    other = MaintenanceEngine(h.store, tool_config=h.engine.tool_config, utc_now=lambda: NOW)
    with pytest.raises(MaintenanceError, match='owner_busy'):
        await other.run(key)
    assert h.store._lock is not None
    await h.engine.cancel(key)
    await task


@pytest.mark.asyncio
async def test_redirect_requests_cannot_escape_cumulative_budget(tmp_path):
    h = Harness(tmp_path / 'jobs.db')
    requests = []
    def redirect(request):
        requests.append(str(request.url))
        return httpx.Response(302, headers={'location': '/products/second'})
    h.engine.wire_transport = httpx.MockTransport(redirect)
    _, report = await h.run(goal(budgets=Budgets(requests=1)))
    assert len(requests) == 1
    assert report['usage']['requests'] == 1
    assert report['state'] == 'partial' and report['stop_reason'] == 'request_budget'


@pytest.mark.asyncio
async def test_cache_exact_expiry_misses_but_report_evidence_survives_eviction(tmp_path):
    h = Harness(tmp_path / 'jobs.db')
    key, report = await h.run(goal(freshness_seconds=1))
    count = len(h.requests)
    h.engine.utc_now = lambda: NOW + timedelta(seconds=1)
    await h.run(goal(freshness_seconds=1))
    assert len(h.requests) > count
    h.store.acquire()
    h.store.cache_put('evict-all', {'complete': True}, expires=NOW + timedelta(days=1), byte_limit=32)
    h.store.release()
    evidence_id = report['findings'][0]['evidence_ids'][0]
    assert h.store.evidence(key, evidence_id)['source_url'].startswith(ORIGIN)


@pytest.mark.asyncio
async def test_known_transient_transport_failure_retries_once_with_charged_attempts(tmp_path):
    h = Harness(tmp_path / 'jobs.db')
    requests = []
    start = time.monotonic()
    h.engine.utc_now = lambda: NOW + timedelta(seconds=time.monotonic() - start)
    def transient(request):
        requests.append(str(request.url))
        if len(requests) == 1:
            raise httpx.ConnectError('synthetic connection failure')
        return httpx.Response(200, text=supplier_html(), headers={'content-type': 'text/html'})
    h.engine.wire_transport = httpx.MockTransport(transient)
    _, report = await h.run()
    assert report['findings'][0]['status'] == 'proposed_correction'
    assert report['usage']['requests'] == len(requests)
    assert len(requests) <= 4


@pytest.mark.asyncio
async def test_unknown_retry_is_explicit_new_charge_and_resolves_pending_comparison(tmp_path):
    class Crash(BaseException):
        pass
    def crash(event, payload):
        if event == 'after_dispatch':
            raise Crash()
    h = Harness(tmp_path / 'jobs.db', failure_hook=crash)
    key = h.store.create(goal())
    with pytest.raises(Crash):
        await h.engine.run(key)
    reopened = Harness(tmp_path / 'jobs.db')
    partial = await reopened.engine.resume(key)
    assert partial['state'] == 'partial' and not reopened.requests
    source = next(row['id'] for row in reopened.store.steps(key) if row['kind'] == 'extract')
    report = await reopened.engine.retry_unknown(key, source)
    assert report['findings'][0]['status'] == 'proposed_correction'
    assert report['usage']['unknown_requests'] == 1
    assert report['usage']['requests'] == len(reopened.requests) + 1


@pytest.mark.asyncio
async def test_native_sitemap_discovery_then_guarded_extraction(tmp_path):
    h = Harness(tmp_path / 'jobs.db')
    requests = []
    def native(request):
        requests.append(str(request.url))
        if request.url.path == '/robots.txt':return httpx.Response(404)
        if request.url.path == '/sitemap.xml':
            return httpx.Response(200, text='<urlset><url><loc>' + ORIGIN + '/products/p1</loc></url></urlset>')
        return httpx.Response(200, text=supplier_html())
    h.engine.wire_transport = httpx.MockTransport(native)
    _, report = await h.run(goal(product_urls=()))
    assert requests[:2]==[ORIGIN+'/robots.txt',ORIGIN+'/sitemap.xml']
    assert requests.count(ORIGIN+'/robots.txt')==1
    assert report['findings'][0]['status'] == 'proposed_correction'
    assert report['usage']['requests'] == len(requests)
