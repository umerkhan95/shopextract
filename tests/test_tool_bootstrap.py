"""Reviewed B01–B08: actual SQLite capture loading, admission, owners and cleanup."""
import asyncio,json,sqlite3,time
from dataclasses import asdict
from pathlib import Path
import pytest
from shopextract.tools.runtime import ToolRuntime,ToolConfig,Limits,CaptureGrant
from shopextract.tools.contracts import ToolError
from shopextract.tools.state import RetainedGraph
from tests.test_reliable_changes import product,variant,save,DOMAIN


def capture_child(connection,kind,payload,maximum):
    """Observe/hold only real decoder boundary; execute original worker/domain logic."""
    from shopextract.monitor import evidence
    from shopextract.tools.execution import _child
    data=json.loads(payload)
    if data.get('operation')=='capture':
        original=evidence._iter_snapshot
        def observed(*args,**kwargs):
            Path(data['grant']['db_path']+'.decoded').write_text('decoder entered')
            if data['grant']['alias']=='hold':time.sleep(.4)
            yield from original(*args,**kwargs)
        evidence._iter_snapshot=observed
    _child(connection,kind,payload,maximum)


def engine_for(db,ids,limits=None,alias='capture'):
    engine=ToolRuntime(ToolConfig(captures=tuple(CaptureGrant(alias+str(i) if alias!='hold' else alias,str(db),sid,DOMAIN) for i,sid in enumerate(ids)),limits=limits or Limits()))
    engine.auxiliary.child_target=capture_child
    return engine


async def wait_worker(engine):
    for _ in range(300):
        if engine.auxiliary.process is not None:return
        await asyncio.sleep(.005)
    pytest.fail('Bootstrap never entered owned worker')


@pytest.mark.asyncio
async def test_B01_normal_grants_preserve_product_variant_evidence(tmp_path):
    db=tmp_path/'normal.db';sid=save(str(db),[product(variants=[variant('v','9',0)])],0)
    engine=engine_for(db,[sid])
    try:
        result=await engine.bootstrap();grant=result['captures'][0]
        assert grant['alias']=='capture0' and grant['capture_handle'] and grant['catalog_handle']
        jid,_=engine.store.lookup(grant['catalog_handle'],'catalog');record=engine.store.get(jid).collections['products'][0]
        for owner in [record,record['variants'][0]]:
            eid=owner['field_evidence']['/price'][0]
            reply=await engine.call('evidence',{'schema_version':'1.0','owner':owner['owner_handle'],'evidence_id':eid})
            assert reply['ok'] and str(reply['data']['evidence']['retained_data']['value']) in {'10','9'}
        assert await engine.bootstrap()==result
        result['captures'].clear();assert (await engine.bootstrap())['captures']
    finally:await engine.aclose()


@pytest.mark.asyncio
async def test_B02_all_stored_payload_preflight_before_decode(tmp_path):
    mutations=[('snapshots','products_json'),('evidence_products','record_json'),('evidence_owners','graph_json'),('evidence_records','metadata_json'),('evidence_payloads','encoded_payload'),('evidence_references','observation_id')]
    for index,(table,column) in enumerate(mutations):
        db=tmp_path/f'large{index}.db';sid=save(str(db),[product()],0)
        with sqlite3.connect(db) as conn:conn.execute(f'UPDATE {table} SET {column}=?',('x'*40000,))
        engine=engine_for(db,[sid],Limits(graph_bytes=32768))
        try:
            with pytest.raises(ToolError,match='resource_limit'):await engine.bootstrap()
            assert not Path(str(db)+'.decoded').exists()
            assert not engine.store.handles and engine.store.used_bytes==0 and engine.auxiliary.process is None
        finally:await engine.aclose()
        assert db.stat().st_size<256*1024


@pytest.mark.asyncio
async def test_B03_item_preflight_before_decode(tmp_path):
    db=tmp_path/'items.db';sid=save(str(db),[product(key=str(i)) for i in range(3)],0)
    engine=engine_for(db,[sid],Limits(item_count=2))
    try:
        with pytest.raises(ToolError,match='resource_limit'):await engine.bootstrap()
        assert not Path(str(db)+'.decoded').exists() and engine.store.used_bytes==0
    finally:await engine.aclose()


@pytest.mark.asyncio
async def test_B04_atomic_failure_never_evicts_unrelated_results(tmp_path):
    db=tmp_path/'atomic.db';sid=save(str(db),[product(title='A'*3000)],0)
    engine=engine_for(db,[sid,sid],Limits(graph_bytes=32768,session_graph_bytes=40000))
    unrelated=RetainedGraph({'urls':['retained']},{},'complete')
    engine.store.publish('unrelated',unrelated);before=engine.store.used_bytes
    try:
        with pytest.raises(ToolError,match='resource_limit'):await engine.bootstrap()
        assert engine.store.get('unrelated') is unrelated
        assert list(engine.store.graphs)==['unrelated'] and engine.store.used_bytes==before and not engine.store.handles
        assert engine.grants is None and engine.auxiliary.process is None
    finally:await engine.aclose()
    # Capacity pressure itself must not evict existing terminal results either.
    engine=engine_for(db,[sid],Limits(terminal_jobs=1));engine.store.publish('unrelated',unrelated)
    try:
        with pytest.raises(ToolError,match='resource_limit'):await engine.bootstrap()
        assert engine.store.get('unrelated') is unrelated
    finally:await engine.aclose()


@pytest.mark.asyncio
async def test_B05_busy_database_deadline_keeps_event_loop_responsive(tmp_path):
    db=tmp_path/'busy.db';sid=save(str(db),[product()],0)
    lock=sqlite3.connect(db);lock.execute('BEGIN EXCLUSIVE');engine=engine_for(db,[sid]);beats=[0]
    async def beat():
        while True:beats[0]+=1;await asyncio.sleep(.01)
    heartbeat=asyncio.create_task(beat());start=time.monotonic()
    try:
        with pytest.raises(ToolError,match='timeout'):await engine.bootstrap(timeout_seconds=1)
        assert beats[0]>=5 and time.monotonic()-start<2.5
        assert engine.auxiliary.process is None and not engine.store.handles and engine.store.used_bytes==0
    finally:heartbeat.cancel();lock.close();await engine.aclose()


@pytest.mark.asyncio
async def test_B06_cancel_and_close_reap_private_materialization(tmp_path):
    db=tmp_path/'cancel.db';sid=save(str(db),[product()],0)
    for close in (False,True):
        lock=sqlite3.connect(db);lock.execute('BEGIN EXCLUSIVE');engine=engine_for(db,[sid]);task=asyncio.create_task(engine.bootstrap())
        try:
            await wait_worker(engine)
            if close:await engine.aclose()
            else:task.cancel()
            with pytest.raises(asyncio.CancelledError):await task
            assert engine.auxiliary.process is None and engine.store.used_bytes==0 and not engine.store.handles and engine.grants is None
        finally:lock.close();await engine.aclose()


@pytest.mark.asyncio
async def test_B07_shared_admission_and_waiter_cancellation(tmp_path):
    db=tmp_path/'queue.db';sid=save(str(db),[product()],0);engine=engine_for(db,[sid]);release=asyncio.Event();entered=asyncio.Event()
    async def held(ctx):entered.set();await release.wait();return RetainedGraph({'urls':[]},{},'complete')
    engine.jobs.submit(held,10);await entered.wait()
    try:
        with pytest.raises(ToolError,match='timeout'):await engine.bootstrap(timeout_seconds=1)
        assert engine.auxiliary.process is None
        holder=asyncio.create_task(engine.bootstrap());await asyncio.sleep(.05)
        waiter=asyncio.create_task(engine.bootstrap());await asyncio.sleep(.05);waiter.cancel()
        with pytest.raises(asyncio.CancelledError):await waiter
        assert not holder.done();release.set()
        assert (await holder)['captures']
    finally:release.set();await engine.aclose()


@pytest.mark.asyncio
async def test_B08_legacy_and_consistent_transaction(tmp_path):
    from shopextract.tools.domain import json_value
    db=tmp_path/'legacy.db'
    with sqlite3.connect(db) as conn:
        conn.execute('CREATE TABLE snapshots (id INTEGER PRIMARY KEY,products_json TEXT)')
        conn.execute('INSERT INTO snapshots VALUES (1,?)',(json.dumps(json_value(asdict(product()))),))
        # Legacy snapshots contain arrays, as documented by the existing loader.
        conn.execute('UPDATE snapshots SET products_json=?',(json.dumps([json_value(asdict(product()))]),))
    engine=engine_for(db,[1],alias='hold');task=asyncio.create_task(engine.bootstrap())
    try:
        marker=Path(str(db)+'.decoded')
        for _ in range(300):
            if marker.exists():break
            await asyncio.sleep(.005)
        assert marker.exists()
        with sqlite3.connect(db,timeout=.01) as conn:
            with pytest.raises(sqlite3.OperationalError,match='locked'):
                conn.execute('BEGIN EXCLUSIVE')
        grants=await task;jid,_=engine.store.lookup(grants['captures'][0]['catalog_handle'],'catalog')
        record=engine.store.get(jid).collections['products'][0]
        assert record['price']=='10' and not record['evidence_ids']
    finally:await engine.aclose()
    with sqlite3.connect(db) as conn:conn.execute('UPDATE snapshots SET products_json=?',('x'*40000,))
    marker.unlink();engine=engine_for(db,[1],Limits(graph_bytes=32768))
    try:
        with pytest.raises(ToolError,match='resource_limit'):await engine.bootstrap()
        assert not marker.exists() and engine.store.used_bytes==0
    finally:await engine.aclose()
