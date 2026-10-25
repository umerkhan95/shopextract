"""Seed11025 synthetic P3 adverse cases using real native services."""
import asyncio
import importlib
import json
import sqlite3
from copy import deepcopy
from decimal import Decimal
from pathlib import Path

import pytest

from tests.test_cli_monitor import invoke,payload
from tests.test_reliable_changes import product,save,DOMAIN,graph,T0,variant
from shopextract._portable import product_to_record,product_from_record
from shopextract._evidence import decode_value
from shopextract._models import ExtractionResult,ExtractionTier,Platform
from shopextract.monitor.evidence import load_snapshot


def write_products(tmp_path,products,name='products.json'):
    file=tmp_path/name; file.write_text(json.dumps([product_to_record(p) for p in products]));return file


def reliable(db,a,b,c=None,domain=DOMAIN):
    args=['changes',domain,'--db',db,'--reliable','--previous',a,'--current',b]
    if c:args+=['--recheck',c]
    return invoke(*args)


@pytest.mark.parametrize('price,state,events',[('100','confirmed',1),('10','rejected',0)])
def test_suspicious_recheck_replay(tmp_path,price,state,events):
    db=str(tmp_path/'s.db');a=save(db,[product()],0);b=save(db,[product('100',tick=1)],1);c=save(db,[product(price,tick=2)],2)
    pending=payload(reliable(db,a,b));assert pending['candidates'][0]['state']=='pending' and pending['new_events']==[]
    report=payload(reliable(db,a,b,c));assert report['candidates'][0]['state']==state and len(report['new_events'])==events
    assert payload(reliable(db,a,b,c))['new_events']==[]


def test_partial_replay_no_removal(tmp_path):
    db=str(tmp_path/'s.db');a=save(db,[product(),product(key='b')],0);b=save(db,[product('11',tick=1)],1,complete=False)
    report=payload(reliable(db,a,b));assert [e['field_path'] for e in report['events']]==['/price']
    assert all(e['kind']!='product_removed' for e in report['events'])
    assert payload(reliable(db,a,b))['new_events']==[]


@pytest.mark.parametrize('kind',['scope','foreign','order','missing'])
def test_reliable_invalid_selection_no_writes(tmp_path,kind):
    db=str(tmp_path/'s.db');a=save(db,[product()],0);b=save(db,[product('11',tick=1)],1,scope='other' if kind=='scope' else 'catalog:shop.example:all')
    before=Path(db).read_bytes()
    result=reliable(db,b if kind=='order' else a,999 if kind=='missing' else a if kind=='order' else b,domain='foreign.example' if kind=='foreign' else DOMAIN)
    assert result.exit_code==2,result.output
    assert Path(db).read_bytes()==before


def test_reliable_transaction_fault_restart(tmp_path,monkeypatch):
    module=importlib.import_module('shopextract.monitor.reliable');db=str(tmp_path/'s.db');a=save(db,[product()],0);b=save(db,[product('11',tick=1)],1)
    original=module._before_commit
    def fault(conn):raise sqlite3.OperationalError('synthetic persistence fault')
    monkeypatch.setattr(module,'_before_commit',fault)
    assert reliable(db,a,b).exit_code==1
    with sqlite3.connect(db) as conn:assert not conn.execute("SELECT name FROM sqlite_master WHERE name='reliable_reports'").fetchall()
    monkeypatch.setattr(module,'_before_commit',original)
    assert len(payload(reliable(db,a,b))['new_events'])==1


@pytest.mark.parametrize('meta',[
    {'schema_version':2,'metadata':{}}, {'schema_version':True,'metadata':{}},
    {'schema_version':1,'metadata':{'max_urls':False}}, {'schema_version':1,'metadata':{'max_urls':1001}},
    {'schema_version':1,'metadata':{'catalog_complete':'true'}}, {'schema_version':1,'metadata':{'incompleteness_reasons':None}},
    {'schema_version':1,'metadata':{'observation_scope':3}}, {'schema_version':1,'metadata':{'unknown':0}},
])
def test_metadata_invalid_before_database_creation(tmp_path,meta):
    source=write_products(tmp_path,[product()]);policy=tmp_path/'meta.json';policy.write_text(json.dumps(meta));db=tmp_path/'new.db'
    result=invoke('snapshot-save',source,'--domain',DOMAIN,'--metadata',policy,'--db',db)
    assert result.exit_code==2,result.output
    assert not db.exists()


def test_snapshot_save_rollback_then_restart(tmp_path,monkeypatch):
    module=importlib.import_module('shopextract.monitor.evidence');db=tmp_path/'s.db';source=write_products(tmp_path,[product()]);original=module._persist_snapshot
    def fault(*args,**kwargs):original(*args,**kwargs);raise sqlite3.OperationalError('synthetic failure')
    monkeypatch.setattr(module,'_persist_snapshot',fault)
    assert invoke('snapshot-save',source,'--domain',DOMAIN,'--db',db).exit_code==1
    with sqlite3.connect(db) as conn:assert not conn.execute("SELECT name FROM sqlite_master WHERE name='snapshots'").fetchall()
    monkeypatch.setattr(module,'_persist_snapshot',original)
    assert payload(invoke('snapshot-save',source,'--domain',DOMAIN,'--db',db))['snapshot_id']==1


def test_prune_expiry_load_bundle_recheck(tmp_path):
    db=str(tmp_path/'s.db');a=save(db,[product()],0);b=save(db,[product('100',tick=1)],1);c=save(db,[product('100',tick=2)],2)
    before=Path(db).read_bytes();args=['evidence','prune','--before','2026-10-17T00:00:00Z','--db',db,'--unprotect-references']
    report=payload(invoke(*args));assert report['expired']==6 and report['payloads_deleted']>0 and Path(db).read_bytes()==before
    assert payload(invoke(*args,'--apply'))['expired']==6
    eid=product_to_record(product())['evidence_contract']['evidence'][0]['evidence_id']
    assert payload(invoke('evidence','get',eid,'--snapshot',c,'--record-key','product/0','--db',db))['status']=='expired'
    records=payload(invoke('snapshot-load',c,'--db',db))['products'];p=product_from_record(records[0]);assert p.evidence_contract.observations[0].state.value=='expired'
    source=tmp_path/'expired.json';source.write_text(json.dumps(records));bundle=payload(invoke('evidence','bundle','create',source));file=tmp_path/'bundle.json';file.write_text(json.dumps(bundle))
    restored=payload(invoke('evidence','bundle','load',file))['products'];assert restored==records
    report=payload(reliable(db,a,b,c));assert report['events']==[]


def test_prune_legacy_schema_is_readonly(tmp_path):
    db=tmp_path/'legacy.db'
    with sqlite3.connect(db) as conn:
        conn.execute('CREATE TABLE snapshots(id INTEGER PRIMARY KEY,domain TEXT,products_json TEXT,created_at TEXT)')
        conn.execute('INSERT INTO snapshots VALUES(1,?,?,?)',(DOMAIN,'[]',T0.isoformat()))
    before=db.read_bytes();report=payload(invoke('evidence','prune','--before','2026-10-17T00:00:00Z','--db',db))
    assert report['examined']==0 and db.read_bytes()==before


def test_legacy_identity_prerequisite_then_apply_exact_read(tmp_path):
    db=tmp_path/'legacy.db'
    with sqlite3.connect(db) as conn:
        conn.execute('CREATE TABLE snapshots(id INTEGER PRIMARY KEY,domain TEXT,products_json TEXT,created_at TEXT)')
        conn.execute('INSERT INTO snapshots VALUES(1,?,?,?)',(DOMAIN,json.dumps([{'title':'Widget','price':'10.000000000000000001'}]),T0.isoformat()))
    before=db.read_bytes();result=invoke('history',DOMAIN,'Widget','--db',db)
    assert result.exit_code==1 and 'migration' in result.output and db.read_bytes()==before
    assert payload(invoke('identity','migrate','--db',db,'--apply'))['updated']==1
    before=db.read_bytes();history=payload(invoke('history',DOMAIN,'Widget','--db',db))
    assert decode_value(history['entries'][0]['price'])==Decimal('10.000000000000000001') and db.read_bytes()==before


@pytest.mark.parametrize('args',[
    ['snapshot-load','1'], ['evidence','get','e_missing','--snapshot','1','--record-key','product/0'],
    ['evidence','prune','--before','2026-10-16T00:00:00Z'], ['history',DOMAIN,'Widget'], ['changes',DOMAIN],
    ['identity','migrate','--apply'],
])
def test_missing_db_no_creation(tmp_path,args):
    db=tmp_path/'missing'/'s.db';result=invoke(*args,'--db',db)
    assert result.exit_code==2,result.output
    assert not db.parent.exists()


@pytest.mark.parametrize('seconds,state',[(86400,'observed'),(86401,'expired'),(-1,'unknown')])
def test_resolve_freshness_cutoffs(tmp_path,seconds,state):
    from datetime import timedelta
    source=write_products(tmp_path,[product()]);when=(T0+timedelta(seconds=seconds)).isoformat()
    data=payload(invoke('resolve',source,'--as-of',when))
    assert data['references'][0]['product']['/price']['state']==state
    assert data['products'][0]['product']['price']==product_to_record(product())['product']['price']


def test_resolve_conflict_variant_refs_and_inspect(tmp_path):
    p=product(variants=[variant('x','3')]);p.evidence_contract=graph({'/price':Decimal('10')})
    competing=graph({'/price':Decimal('11')},start=10);p.evidence_contract.evidence+=competing.evidence;p.evidence_contract.observations+=competing.observations
    source=write_products(tmp_path,[p]);result=payload(invoke('resolve',source,'--as-of',T0.isoformat()))
    assert result['references'][0]['product']['/price']['state']=='conflicting'
    assert result['references'][0]['variants'][0]['/price']['state']=='observed'
    for view in ('trust','paths'):
        data=payload(invoke('evidence','inspect',source,'--view',view));assert len(data['views'][0]['variants'])==1


@pytest.mark.parametrize('policy',[
    {'schema_version':'1'}, {'schema_version':1,'offer_max_age_seconds':None},
    {'schema_version':1,'offer_max_age_seconds':True}, {'schema_version':1,'offer_max_age_seconds':0},
    {'schema_version':1,'offer_max_age_seconds':31536001}, {'schema_version':1,'extra':1},
])
def test_policy_rejects_bad_types(tmp_path,policy):
    source=write_products(tmp_path,[product()]);file=tmp_path/'policy.json';file.write_text(json.dumps(policy))
    assert invoke('resolve',source,'--as-of',T0.isoformat(),'--policy',file).exit_code==2


def test_bundle_duplicate_order_atomic_and_sidecar_tamper(tmp_path,monkeypatch):
    from shopextract.export import to_csv
    source=write_products(tmp_path,[product(),product('12')]);file=tmp_path/'bundle.json'
    payload(invoke('evidence','bundle','create',source,'-o',file));records=payload(invoke('evidence','bundle','load',file))['products']
    assert [decode_value(r['product']['price']) for r in records]==[Decimal('10'),Decimal('12')]
    projection=tmp_path/'p.csv';to_csv([product(),product('12')],str(projection));side=tmp_path/'side.json'
    payload(invoke('evidence','sidecar','create',source,'--payload',projection,'--format','csv','-o',side));projection.write_bytes(projection.read_bytes()+b'\n')
    destination=tmp_path/'keep.json';destination.write_text('keep')
    assert invoke('evidence','sidecar','load',side,'--payload',projection,'-o',destination).exit_code==2 and destination.read_text()=='keep'
    module=importlib.import_module('shopextract._cli_monitor')
    def fault(*args):raise OSError('synthetic publish failure')
    monkeypatch.setattr(module.os,'replace',fault)
    assert invoke('evidence','bundle','create',source,'-o',destination).exit_code==1 and destination.read_text()=='keep'
    assert not list(tmp_path.glob('.keep.json.*'))


def test_watch_initial_failure_and_truncated_events(tmp_path,monkeypatch):
    module=importlib.import_module('shopextract.monitor.snapshot')
    async def failed(*args,**kwargs):raise OSError('synthetic unavailable transport')
    monkeypatch.setattr(module,'extract',failed)
    args=['watch','https://shop.example','--interval','0.001','--max-events','1','--timeout','1','--max','1','--db',tmp_path/'s.db']
    result=invoke(*args);assert result.exit_code==1 and json.loads(result.output)['ok'] is False and not (tmp_path/'s.db').exists()
    calls=[]
    async def oversized(*args,**kwargs):
        tick=len(calls);calls.append(tick)
        return ExtractionResult(products=[product('10' if tick==0 else '11',tick=tick),product(key='extra')],platform=Platform.SHOPIFY,tier=ExtractionTier.API,catalog_complete=True,observation_scope='catalog:shop.example:all')
    monkeypatch.setattr(module,'extract',oversized)
    result=invoke(*args);assert result.exit_code==0,result.output
    rows=[json.loads(row)['data'] for row in result.output.splitlines()]
    assert rows[0]['verification']=='unverified_scalar_comparison' and rows[-1]['initialized'] is True
    with sqlite3.connect(tmp_path/'s.db') as conn:assert conn.execute('SELECT sum(catalog_complete) FROM snapshots').fetchone()[0]==0


def test_watch_empty_failed_result_no_baseline(tmp_path,monkeypatch):
    module=importlib.import_module('shopextract.monitor.snapshot')
    async def extraction(*args,**kwargs):
        return ExtractionResult(products=[],errors=['synthetic transport failure'],platform=Platform.SHOPIFY,tier=ExtractionTier.API)
    monkeypatch.setattr(module,'extract',extraction)
    db=tmp_path/'no.db';result=invoke('watch','https://shop.example','--interval','0.001','--max-events','1','--timeout','0.03','--db',db)
    assert result.exit_code==1,result.output
    assert json.loads(result.output)['error']['code']=='E_OPERATION' and not db.exists()


def test_artifact_same_input_output_rejected(tmp_path):
    source=write_products(tmp_path,[product()]);before=source.read_bytes()
    result=invoke('evidence','bundle','create',source,'-o',source)
    assert result.exit_code==2,result.output
    assert source.read_bytes()==before


def test_read_json_byte_record_depth_boundaries(tmp_path):
    from shopextract._cli_data import read_json_file, products_from_value,bounded_tree
    from shopextract._cli_core import CliFailure
    file=tmp_path/'bounded.json'
    for size in (1048575,1048576):
        file.write_bytes(b'[]'+b' '*(size-2));assert read_json_file(file)==[]
    file.write_bytes(b'[]'+b' '*1048575)
    with pytest.raises(CliFailure):read_json_file(file)
    for count in (999,1000):assert len(products_from_value([product_to_record(product())]*count))==count
    with pytest.raises(CliFailure):products_from_value([product_to_record(product())]*1001)
    for depth in (63,64):
        value=None
        for _ in range(depth):value=[value]
        bounded_tree(value)
    with pytest.raises(ValueError):bounded_tree([value])


def test_nonempty_source_errors_incomplete(tmp_path,monkeypatch):
    module=importlib.import_module('shopextract.monitor.snapshot')
    async def extraction(*args,**kwargs):
        return ExtractionResult(products=[product()],errors=['synthetic partial failure'],catalog_complete=True,platform=Platform.SHOPIFY,tier=ExtractionTier.API)
    monkeypatch.setattr(module,'extract',extraction)
    db=tmp_path/'s.db';payload(invoke('snapshot','https://shop.example','--db',db,'--max','2'))
    with sqlite3.connect(db) as conn:row=conn.execute('SELECT catalog_complete,incompleteness_reasons_json FROM snapshots').fetchone()
    assert row[0]==0 and 'source_errors' in json.loads(row[1])


@pytest.mark.parametrize('alias',['symlink','hardlink'])
@pytest.mark.parametrize('mode',['create','load'])
def test_sidecar_payload_output_alias_rejected(tmp_path,alias,mode):
    from shopextract.export import to_csv
    from shopextract.export._bundle import create_evidence_sidecar
    import os
    products=[product()];source=write_products(tmp_path,products);projection=tmp_path/'p.csv';to_csv(products,str(projection));side=tmp_path/'side.json';side.write_text(json.dumps(create_evidence_sidecar(products,projection.read_bytes(),format='csv')))
    target=tmp_path/'alias';os.symlink(projection,target) if alias=='symlink' else os.link(projection,target)
    before=projection.read_bytes();args=['evidence','sidecar',mode,source if mode=='create' else side,'--payload',projection,'-o',target]
    if mode=='create':args+=['--format','csv']
    assert invoke(*args).exit_code==2 and projection.read_bytes()==before


def test_lookup_missing_unsupported_corrupt_statuses(tmp_path):
    from shopextract._models import Product
    db=str(tmp_path/'s.db');a=save(db,[product()],0);b=save(db,[Product(title='legacy scalar')],1)
    assert payload(invoke('evidence','get','missing','--snapshot',a,'--record-key','product/0','--db',db))['status']=='missing'
    assert payload(invoke('evidence','get','missing','--snapshot',b,'--record-key','product/0','--db',db))['status']=='unsupported'
    eid=product_to_record(product())['evidence_contract']['evidence'][0]['evidence_id']
    with sqlite3.connect(db) as conn:conn.execute("UPDATE evidence_payloads SET encoded_payload='{}'")
    result=invoke('evidence','get',eid,'--snapshot',a,'--record-key','product/0','--db',db)
    assert result.exit_code==1 and json.loads(result.output)['error']['code']=='E_OPERATION'


@pytest.mark.parametrize('family',['bundle','sidecar'])
@pytest.mark.parametrize('malformed',['version','truncated'])
def test_malformed_artifacts_preserve_output(tmp_path,family,malformed):
    from shopextract.export import to_csv
    from shopextract.export._bundle import create_evidence_bundle,create_evidence_sidecar
    projection=tmp_path/'p.csv';to_csv([product()],str(projection))
    value=create_evidence_bundle([product()]) if family=='bundle' else create_evidence_sidecar([product()],projection.read_bytes(),format='csv')
    value['schema_version']=999
    source=tmp_path/'input.json';source.write_text('{' if malformed=='truncated' else json.dumps(value));target=tmp_path/'keep';target.write_text('keep')
    args=['evidence',family,'load',source,'-o',target]
    if family=='sidecar':args+=['--payload',projection]
    assert invoke(*args).exit_code==2 and target.read_text()=='keep'


def test_sqlite_connections_close_deterministically(tmp_path,monkeypatch):
    db=str(tmp_path/'s.db');save(db,[product()],0);opened=[];closed=[];connect=sqlite3.connect
    class Tracked(sqlite3.Connection):
        def close(self):closed.append(id(self));return super().close()
    def tracked(*args,**kwargs):
        kwargs['factory']=Tracked;conn=connect(*args,**kwargs);opened.append(id(conn));return conn
    monkeypatch.setattr(sqlite3,'connect',tracked)
    payload(invoke('history',DOMAIN,'Widget','--db',db));payload(invoke('identity','migrate','--db',db,'--apply'))
    assert len(opened)==4 and sorted(opened)==sorted(closed)


def test_bundle_output_growth_rejected_before_publication(tmp_path):
    from shopextract._cli_data import MAX_BYTES
    p=product();p.raw_data={'pad':''};record=product_to_record(p)
    overhead=len(json.dumps([record]).encode());p.raw_data={'pad':'x'*(MAX_BYTES-overhead-10)}
    source=write_products(tmp_path,[p]);assert source.stat().st_size<=MAX_BYTES
    target=tmp_path/'keep';target.write_text('keep')
    result=invoke('evidence','bundle','create',source,'-o',target)
    assert result.exit_code==2 and target.read_text()=='keep'


def test_watch_sigint_closes_transport_and_exits130(tmp_path):
    import os,signal,subprocess,sys,time
    ready=tmp_path/'ready';closed=tmp_path/'closed';db=tmp_path/'s.db'
    script=tmp_path/'interrupt.py'
    script.write_text('''import asyncio,importlib
from pathlib import Path
from tests.test_reliable_changes import product
from shopextract._models import ExtractionResult,Platform,ExtractionTier
from shopextract.cli import main
module=importlib.import_module('shopextract.monitor.snapshot')
calls=[]
async def extraction(*args,**kwargs):
    calls.append(1)
    if len(calls)>1:
        Path(READY).write_text('ready')
        try:await asyncio.sleep(10)
        finally:Path(CLOSED).write_text('closed')
    return ExtractionResult(products=[product()],platform=Platform.SHOPIFY,tier=ExtractionTier.API)
module.extract=extraction
main(['--output-format','json','watch','https://shop.example','--db',DB,'--interval','0.001','--max-events','1','--timeout','20'])
'''.replace('READY',repr(str(ready))).replace('CLOSED',repr(str(closed))).replace('DB',repr(str(db))))
    env=dict(os.environ,PYTHONPATH='src:.',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',TOKENIZERS_PARALLELISM='false')
    process=subprocess.Popen([sys.executable,str(script)],stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
    try:
        deadline=time.monotonic()+5
        while not ready.exists() and process.poll() is None and time.monotonic()<deadline:time.sleep(.01)
        assert ready.exists(),'controlled second transport did not start'
        process.send_signal(signal.SIGINT);stdout,stderr=process.communicate(timeout=5)
        assert process.returncode==130,(stdout,stderr)
        assert closed.exists() and json.loads(stdout)['error']['code']=='E_CANCELLED'
    finally:
        if process.poll() is None:process.kill();process.communicate(timeout=2)


@pytest.mark.parametrize('delta',[-1,0,1])
def test_prune_preview_logical_size_bound_and_cleanup(tmp_path,monkeypatch,delta):
    module=importlib.import_module('shopextract.monitor.evidence');db=str(tmp_path/'s.db');save(db,[product()],0)
    with sqlite3.connect(db) as conn:size=conn.execute('PRAGMA page_count').fetchone()[0]*conn.execute('PRAGMA page_size').fetchone()[0]
    monkeypatch.setattr(module,'MAX_PREVIEW_DB_BYTES',size+delta,raising=False)
    before=Path(db).read_bytes();connect=sqlite3.connect;opened=[];closed=[];backups=[]
    class Tracked(sqlite3.Connection):
        def close(self):closed.append(id(self));return super().close()
        def backup(self,*args,**kwargs):backups.append(True);return super().backup(*args,**kwargs)
    def tracked(*args,**kwargs):
        kwargs['factory']=Tracked;conn=connect(*args,**kwargs);opened.append(id(conn));return conn
    monkeypatch.setattr(sqlite3,'connect',tracked)
    result=invoke('evidence','prune','--before','2026-10-17T00:00:00Z','--db',db)
    if delta<0:
        assert result.exit_code==1 and json.loads(result.output)['error']['code']=='E_OPERATION',result.output
        assert '64 MiB' in result.output and backups==[]
    else:
        assert payload(result)['dry_run'] is True and backups==[True]
    assert sorted(opened)==sorted(closed) and Path(db).read_bytes()==before


def test_prune_preview_deadline_closes_real_backup(tmp_path,monkeypatch):
    module=importlib.import_module('shopextract.monitor.evidence');db=str(tmp_path/'s.db');save(db,[product()],0);before=Path(db).read_bytes()
    ticks=iter([0.,6.]);monkeypatch.setattr(module,'_preview_clock',lambda:next(ticks),raising=False)
    connect=sqlite3.connect;opened=[];closed=[]
    class Tracked(sqlite3.Connection):
        def close(self):closed.append(id(self));return super().close()
    def tracked(*args,**kwargs):
        kwargs['factory']=Tracked;conn=connect(*args,**kwargs);opened.append(id(conn));return conn
    monkeypatch.setattr(sqlite3,'connect',tracked)
    result=invoke('evidence','prune','--before','2026-10-17T00:00:00Z','--db',db)
    assert result.exit_code==1 and '5 seconds' in result.output,result.output
    assert sorted(opened)==sorted(closed) and Path(db).read_bytes()==before


def test_prune_preview_growth_progress_uses_actual_total(tmp_path,monkeypatch):
    module=importlib.import_module('shopextract.monitor.evidence');db=str(tmp_path/'s.db');save(db,[product()],0);before=Path(db).read_bytes()
    connect=sqlite3.connect;closed=[];opened=[]
    class Growing(sqlite3.Connection):
        def close(self):closed.append(id(self));return super().close()
        def backup(self,target,**kwargs):
            # Inject only the nondeterministic growth signal at real SQLite progress.
            actual=kwargs['progress']
            def progress(status,remaining,total):actual(status,remaining,module.MAX_PREVIEW_DB_BYTES//4096+1)
            return super().backup(target,**dict(kwargs,progress=progress))
    def tracked(*args,**kwargs):
        kwargs['factory']=Growing;conn=connect(*args,**kwargs);opened.append(id(conn));return conn
    monkeypatch.setattr(sqlite3,'connect',tracked)
    result=invoke('evidence','prune','--before','2026-10-17T00:00:00Z','--db',db)
    assert result.exit_code==1 and '64 MiB' in result.output,result.output
    assert sorted(opened)==sorted(closed) and Path(db).read_bytes()==before


def test_prune_preview_schema_fault_closes_copy(tmp_path,monkeypatch):
    db=str(tmp_path/'s.db');save(db,[product()],0)
    with sqlite3.connect(db) as conn:conn.execute('UPDATE evidence_schema SET version=999')
    before=Path(db).read_bytes();connect=sqlite3.connect;opened=[];closed=[]
    class Tracked(sqlite3.Connection):
        def close(self):closed.append(id(self));return super().close()
    def tracked(*args,**kwargs):
        kwargs['factory']=Tracked;conn=connect(*args,**kwargs);opened.append(id(conn));return conn
    monkeypatch.setattr(sqlite3,'connect',tracked)
    result=invoke('evidence','prune','--before','2026-10-17T00:00:00Z','--db',db)
    assert result.exit_code==1 and json.loads(result.output)['error']['code']=='E_OPERATION'
    assert sorted(opened)==sorted(closed) and Path(db).read_bytes()==before


@pytest.mark.parametrize('family',['bundle','sidecar'])
def test_artifact_load_file_portable_pipeline_single_read(tmp_path,monkeypatch,family):
    from shopextract.export import to_csv
    from shopextract.export._bundle import create_evidence_bundle,create_evidence_sidecar
    module=importlib.import_module('shopextract.export._bundle');projection=tmp_path/'p.csv';to_csv([product()],str(projection))
    value=create_evidence_bundle([product()]) if family=='bundle' else create_evidence_sidecar([product()],projection.read_bytes(),format='csv')
    source=tmp_path/'bundle.json';source.write_text(json.dumps(value));target=tmp_path/'portable.json'
    def no_reread(path):raise AssertionError('original input must not be read after bounded validation')
    monkeypatch.setattr(module,'read_evidence_bundle',no_reread)
    args=['evidence',family,'load',source,'-o',target]
    if family=='sidecar':args+=['--payload',projection]
    payload(invoke(*args));assert isinstance(json.loads(target.read_text()),list)
    db=tmp_path/'s.db';sid=payload(invoke('snapshot-save',target,'--domain',DOMAIN,'--db',db))['snapshot_id']
    assert decode_value(payload(invoke('snapshot-load',sid,'--db',db))['products'][0]['product']['price'])==Decimal('10')
