"""A#49 job/store mechanism cases; fake domain only, lifecycle remains real."""
import asyncio
import pytest
from shopextract.tools import Limits
from shopextract.tools.state import SessionStore, RetainedGraph
from shopextract.tools.jobs import JobManager
from shopextract.tools.contracts import ToolError


def graph(count=3):
    return RetainedGraph({'urls': [str(i) for i in range(count)]}, {}, 'complete')


def test_immutable_pages_cursor_binding_expiry_and_release():
    now = [0.0]
    store = SessionStore(Limits(retention_seconds=2), clock=lambda: now[0])
    g = graph()
    g.owners['known_owner']={'evidence':{},'availability':[]}
    store.publish('j_one', g)
    first = store.page('j_one', 'urls', 2, None)
    assert first['items'] == ['0', '1']
    last = store.page('j_one', 'urls', 2, first['next_cursor'])
    assert last['items'] == ['2'] and last['next_cursor'] is None
    assert store.page('j_one', 'urls', 2, None) == first
    with pytest.raises(ToolError, match='invalid_argument'):
        store.page('j_one', 'urls', 1, first['next_cursor'])
    assert store.used_bytes > 0
    now[0] = 2
    with pytest.raises(ToolError, match='expired'):
        store.page('j_one', 'urls', 2, first['next_cursor'])
    assert store.used_bytes == 0
    with pytest.raises(ToolError, match='expired'):store.lookup('known_owner','owner')


def test_aggregate_rejection_and_eviction_releases_graph():
    size = graph().size
    store = SessionStore(Limits(graph_bytes=size, session_graph_bytes=size, terminal_jobs=1))
    store.publish('j_one', graph())
    store.publish('j_two', graph())
    assert store.used_bytes == size
    with pytest.raises(ToolError, match='expired'):
        store.get('j_one')
    with pytest.raises(ToolError, match='resource_limit'):
        store.publish('j_big', graph(100))
    assert store.used_bytes == size
    store.close()
    assert store.used_bytes == 0


@pytest.mark.asyncio
async def test_cancel_queue_and_completed_cancel_winner():
    store = SessionStore(Limits())
    jobs = JobManager(store, Limits())
    entered = asyncio.Event()
    async def slow(context):
        entered.set()
        await asyncio.Event().wait()
    first = jobs.submit(slow, 1)
    await entered.wait()
    second = jobs.submit(slow, 1)
    await jobs.cancel(second['job_id'])
    assert jobs.status(second['job_id'])['state'] == 'cancelled'
    await jobs.cancel(first['job_id'])
    async def ready(context):
        return graph()
    final = jobs.submit(ready, 1)
    for _ in range(20):
        if jobs.status(final['job_id'])['state'] == 'succeeded':
            break
        await asyncio.sleep(.01)
    await jobs.cancel(final['job_id'])
    assert jobs.status(final['job_id'])['state'] == 'succeeded'
    assert store.page(final['job_id'], 'urls', 2, None)['items'] == ['0', '1']
    await jobs.close()


def test_retained_charge_includes_products_and_each_real_payload_copy():
    from shopextract.tools.contracts import encoded
    repeated = {'retained_data': {'value': 'x' * 300}}
    value = RetainedGraph({'products': [repeated]}, {}, 'complete',
                          products=[repeated], owners={'owner': repeated})
    complete = {'collections': value.collections, 'metadata': value.metadata,
        'completeness': value.completeness, 'products': value.products,
        'owners': value.owners, 'dependencies': list(value.dependencies)}
    assert value.size == len(encoded(complete))
    store = SessionStore(Limits(graph_bytes=value.size - 1))
    with pytest.raises(ToolError, match='resource_limit'):
        store.publish('j_copies', value)
    assert store.used_bytes == 0


@pytest.mark.asyncio
async def test_running_graph_reservation_counts_and_cancel_releases():
    limits = Limits(graph_bytes=1000, session_graph_bytes=1000)
    store = SessionStore(limits)
    jobs = JobManager(store, limits)
    entered = asyncio.Event()
    async def slow(context):
        entered.set()
        await asyncio.Event().wait()
    job = jobs.submit(slow, 1)
    await entered.wait()
    assert store.used_bytes == 1000
    await jobs.cancel(job['job_id'])
    assert store.used_bytes == 0
    await jobs.close()
