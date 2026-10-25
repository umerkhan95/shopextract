"""P3 deterministic native mechanism acceptance; fixtures synthetic."""
import json
from decimal import Decimal
from pathlib import Path
from click.testing import CliRunner
from shopextract.cli import main
from shopextract._portable import product_to_record
from shopextract._models import Product


def invoke(*args):
    return CliRunner().invoke(main,['--output-format','json',*map(str,args)])


def test_snapshot_roundtrip_red(tmp_path):
    source=tmp_path/'products.json'; db=tmp_path/'snap.db'
    source.write_text(json.dumps([product_to_record(Product(title='synthetic',price=Decimal('10.010000000000000001'),external_id='a'))]))
    saved=invoke('snapshot-save',source,'--domain','shop.example','--db',db)
    assert saved.exit_code==0,saved.output
    sid=json.loads(saved.output)['data']['snapshot_id']
    loaded=invoke('snapshot-load',sid,'--db',db)
    assert loaded.exit_code==0,loaded.output
    assert json.loads(loaded.output)['data']['products'][0]['product']['price']==product_to_record(Product(price=Decimal('10.010000000000000001')))['product']['price']


def test_resolve_missing_contract_red(tmp_path):
    source=tmp_path/'products.json'
    source.write_text(json.dumps([product_to_record(Product(title='synthetic'))]))
    result=invoke('resolve',source,'--as-of','2026-10-16T10:00:00Z')
    assert result.exit_code==0,result.output
    assert json.loads(result.output)['data']['references']==[{'product':None,'variants':[]}]

import pytest

@pytest.mark.parametrize('args',[
    ['snapshot','https://shop.example','--db','unused.db','--max','2'],
    ['history','shop.example','title','--db','missing.db','--canonical-id','p_a'],
    ['changes','shop.example','--reliable','--previous','1','--current','2','--recheck','3','--db','missing.db'],
    ['watch','https://shop.example','--interval','1','--max-events','1','--timeout','0.01','--db','unused.db'],
    ['evidence','get','e_missing','--snapshot','1','--record-key','product/0','--db','missing.db'],
    ['evidence','prune','--before','2026-10-16T00:00:00Z','--db','missing.db'],
    ['evidence','bundle','create','missing.json'],
    ['evidence','sidecar','load','missing.json','--payload','missing.csv'],
    ['identity','migrate','--db','missing.db','--apply'],
])
def test_p3_binding_family_red(args):
    # Registration and arity must succeed before native file errors; no network runs.
    result=invoke(*args,'--help')
    assert result.exit_code==0,result.output
    assert 'Usage:' in result.output

from tests.test_reliable_changes import product, save, DOMAIN
from shopextract.monitor.evidence import save_snapshot


def payload(result):
    assert result.exit_code==0,result.output
    return json.loads(result.output)['data']


def test_history_exact_readonly_red(tmp_path):
    db=str(tmp_path/'snap.db')
    save(db,[product('10.010000000000000001')],0)
    before=Path(db).read_bytes()
    result=payload(invoke('history',DOMAIN,'Widget','--db',db))
    from shopextract._evidence import decode_value
    assert decode_value(result['entries'][0]['price'])==Decimal('10.010000000000000001')
    assert Path(db).read_bytes()==before


def test_reliable_replay_red(tmp_path):
    db=str(tmp_path/'snap.db'); a=save(db,[product()],0); b=save(db,[product('11',tick=1)],1)
    args=('changes',DOMAIN,'--reliable','--previous',a,'--current',b,'--db',db)
    assert len(payload(invoke(*args))['new_events'])==1
    assert len(payload(invoke(*args))['new_events'])==0


def test_watch_invalid_bound_red(tmp_path):
    db=tmp_path/'never.db'
    result=invoke('watch','https://shop.example','--interval','nan','--max-events','1','--timeout','0.01','--db',db)
    assert result.exit_code==2
    assert json.loads(result.output)['error']['code']=='E_USAGE'
    assert not db.exists()


def test_evidence_get_prune_readonly_red(tmp_path):
    db=str(tmp_path/'snap.db'); sid=save(db,[product()],0)
    from shopextract._portable import product_to_record
    eid=product_to_record(product())['evidence_contract']['evidence'][0]['evidence_id']
    before=Path(db).read_bytes()
    assert payload(invoke('evidence','get',eid,'--snapshot',sid,'--record-key','product/0','--db',db))['status']=='available'
    report=payload(invoke('evidence','prune','--before','2026-10-17T00:00:00Z','--db',db))
    assert report['dry_run'] is True and report['protected']==2
    assert Path(db).read_bytes()==before


def test_bundle_sidecar_runtime_red(tmp_path):
    from shopextract.export import to_csv
    source=tmp_path/'products.json'; bundle=tmp_path/'bundle.json'; sidecar=tmp_path/'sidecar.json'; csv=tmp_path/'products.csv'
    products=[product()]; source.write_text(json.dumps([product_to_record(p) for p in products])); to_csv(products,str(csv))
    payload(invoke('evidence','bundle','create',source,'-o',bundle))
    assert len(payload(invoke('evidence','bundle','load',bundle))['products'])==1
    payload(invoke('evidence','sidecar','create',source,'--payload',csv,'--format','csv','-o',sidecar))
    assert len(payload(invoke('evidence','sidecar','load',sidecar,'--payload',csv))['products'])==1


def test_identity_migration_apply_required_red(tmp_path):
    db=str(tmp_path/'snap.db'); save(db,[product()],0); before=Path(db).read_bytes()
    result=invoke('identity','migrate','--db',db)
    assert result.exit_code==2
    assert json.loads(result.output)['error']['code']=='E_USAGE'
    assert Path(db).read_bytes()==before
    assert payload(invoke('identity','migrate','--db',db,'--apply'))['applied'] is True


def test_watch_unchanged_deadline_red(tmp_path,monkeypatch):
    import importlib
    module=importlib.import_module('shopextract.monitor.snapshot')
    from shopextract._models import ExtractionResult, Platform, ExtractionTier
    calls=[]
    async def extraction(url,**kwargs):
        calls.append(kwargs)
        return ExtractionResult(products=[product()],platform=Platform.SHOPIFY,tier=ExtractionTier.API)
    monkeypatch.setattr(module,'extract',extraction)
    result=invoke('watch','https://shop.example','--interval','0.01','--max-events','1','--timeout','0.05','--max','2','--db',tmp_path/'snap.db')
    assert result.exit_code==3,result.output
    rows=[json.loads(line) for line in result.output.splitlines()]
    assert rows[-1]['data']=={'events':0,'reason':'timeout','initialized':True}
    assert calls and len(calls)<8


def test_prune_independent_red(tmp_path):
    db=str(tmp_path/'snap.db'); save(db,[product()],0); before=Path(db).read_bytes()
    report=payload(invoke('evidence','prune','--before','2026-10-17T00:00:00Z','--db',db))
    assert report['dry_run'] is True and report['protected']==2
    assert Path(db).read_bytes()==before


def test_sidecar_independent_red(tmp_path):
    from shopextract.export import to_csv
    from shopextract.export._bundle import create_evidence_sidecar
    products=[product()]; csv=tmp_path/'p.csv'; to_csv(products,str(csv))
    sidecar=tmp_path/'side.json'; sidecar.write_text(json.dumps(create_evidence_sidecar(products,csv.read_bytes(),format='csv')))
    assert len(payload(invoke('evidence','sidecar','load',sidecar,'--payload',csv))['products'])==1


def test_snapshot_explicit_bound_red(tmp_path,monkeypatch):
    import importlib
    module=importlib.import_module('shopextract.monitor.snapshot')
    from shopextract._models import ExtractionResult, Platform, ExtractionTier
    async def extraction(url,**kwargs):
        assert kwargs['max_urls']==2
        return ExtractionResult(products=[product(key=str(i)) for i in range(3)],platform=Platform.SHOPIFY,tier=ExtractionTier.API)
    monkeypatch.setattr(module,'extract',extraction)
    db=str(tmp_path/'snap.db')
    assert payload(invoke('snapshot','https://shop.example','--max','2','--timeout','1','--db',db))['stored_products']==2
    import sqlite3
    with sqlite3.connect(db) as conn:
        row=conn.execute('SELECT catalog_complete,incompleteness_reasons_json FROM snapshots').fetchone()
    assert row[0]==0 and 'product_budget_exhausted' in json.loads(row[1])


def test_watch_initial_timeout_state(tmp_path,monkeypatch):
    import importlib,asyncio
    module=importlib.import_module('shopextract.monitor.snapshot'); cancelled=[]
    async def extraction(*args,**kwargs):
        try:await asyncio.sleep(1)
        finally:cancelled.append(True)
    monkeypatch.setattr(module,'extract',extraction)
    db=tmp_path/'no.db'
    result=invoke('watch','https://shop.example','--interval','0.01','--max-events','1','--timeout','0.03','--db',db)
    assert result.exit_code==3,result.output
    assert json.loads(result.output)['data']=={'events':0,'reason':'timeout','initialized':False}
    assert cancelled==[True] and not db.exists()


def test_watch_partial_changes_are_unverified(tmp_path,monkeypatch):
    import importlib
    from shopextract._models import ExtractionResult,Platform,ExtractionTier
    module=importlib.import_module('shopextract.monitor.snapshot');calls=[]
    async def extraction(*args,**kwargs):
        tick=len(calls);calls.append(tick)
        return ExtractionResult(products=[product('10' if not tick else '11',tick=tick)],platform=Platform.SHOPIFY,tier=ExtractionTier.API,catalog_complete=False,observation_scope='catalog:shop.example:all')
    monkeypatch.setattr(module,'extract',extraction)
    result=invoke('watch','https://shop.example','--interval','0.001','--max-events','1','--timeout','1','--db',tmp_path/'s.db')
    assert result.exit_code==0,result.output
    rows=[json.loads(line)['data'] for line in result.output.splitlines()]
    assert rows[0]['verification']=='unverified_scalar_comparison'
    assert rows[0]['event']['type']=='PriceChange'
    assert rows[-1]=={'events':1,'reason':'max_events','initialized':True} and len(calls)==2
