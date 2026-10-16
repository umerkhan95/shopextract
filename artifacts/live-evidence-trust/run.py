"""Sequential live evidence acceptance; bounded network and subprocess timeouts."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='2'
os.environ['TOKENIZERS_PARALLELISM']='false'
# This harness never enables paid or local inference fallback.
os.environ.pop('SHOPEXTRACT_LLM_API_KEY',None)
os.environ.pop('OPENAI_API_KEY',None)
os.environ.pop('SHOPEXTRACT_LLM_MODEL',None)
import argparse, asyncio, copy, json, sqlite3, subprocess, sys, time
from collections import Counter
from datetime import datetime,timedelta,timezone
from pathlib import Path
from dataclasses import asdict
from shopextract import normalize,resolve_fields,Platform,save_snapshot,load_snapshot,get_evidence,prune_evidence
from shopextract._portable import product_to_record
from shopextract.export import write_evidence_bundle,read_evidence_bundle,to_csv,to_feed,load_evidence_sidecar
ROOT=Path(__file__).resolve().parent
CASES={'shopify':'https://www.boardgamebliss.com','woocommerce':'https://demo.athemes.com/botiga',
       'magento':'https://magento2-demo.magebit.com','shopware':'https://frontends-demo.vercel.app'}

def owners(products):
    for i,p in enumerate(products):
        yield p,f'product/{i}'
        for j,v in enumerate(p.variants):yield v,f'product/{i}/variant/{j}'

def audit(products,db,sid):
    counts=Counter();references=0
    for owner,key in owners(products):
        graph=getattr(owner,'evidence_contract',None)
        if graph:
            graph.validate()
            for e in graph.evidence:
                r=get_evidence(e.evidence_id,snapshot_id=sid,record_key=key,db_path=str(db))
                assert r.status=='available',r
                assert asdict(r.evidence)==asdict(e)
                if e.pointer is not None:e.resolve_pointer()
                references+=1
        for view in owner.trust_view().values():
            counts[view['state']]+=1
            if view['state']=='observed':assert view['evidence_ids']
            else:assert view['reason'] and view['value'] is None
    return {'field_states':dict(counts),'retrieved_captures':references}

def semantic(p):
    record=product_to_record(p)
    for graph in [record['evidence_contract']]+record['variant_contracts']:
        if graph:graph['evidence'].sort(key=lambda e:e['evidence_id'])
    return record

async def live(name):
    url=CASES[name]
    if name=='shopify':
        from shopextract.extractors.shopify import ShopifyExtractor
        result=await ShopifyExtractor(timeout=15,max_pages=1).extract(url,max_products=2)
    elif name=='woocommerce':
        from shopextract.extractors.woocommerce import WooCommerceExtractor
        result=await WooCommerceExtractor(timeout=15,max_pages=1).extract(url)
    elif name=='magento':
        from shopextract.extractors.magento_graphql import MagentoGraphQLExtractor
        result=await MagentoGraphQLExtractor(timeout=15,page_size=2,max_pages=1).extract(url,max_products=2)
    else:
        from shopextract.extractors.shopware import ShopwareExtractor
        result=await ShopwareExtractor(timeout=15,page_size=2,max_pages=1).extract(url,max_products=2)
    assert not result.error,result.error
    products=[normalize(raw,Platform(name),url) for raw in result.products[:2]]
    assert len(products)==2 and all(products),'Two normalized live products required'
    clock=datetime.now(timezone.utc)
    for owner,_ in owners(products):
        graph=getattr(owner,'evidence_contract',None)
        if graph:owner.evidence_contract=resolve_fields(graph,as_of=clock)
    directory=ROOT/name;directory.mkdir(exist_ok=True)
    db=directory/'snapshots.db'
    # A fresh run uses a new database; saved completed cases are skipped by driver.
    assert not db.exists(),'Remove only this harness case directory to intentionally repeat'
    sid=save_snapshot(products,url,db_path=str(db),metadata={'catalog_complete':False,'observation_scope':url,'incompleteness_reasons':['bounded_live_sample'],'max_urls':2})
    restored=load_snapshot(sid,db_path=str(db))
    for original,loaded in zip(products,restored):
        aligned=copy.deepcopy(original)
        aligned.canonical_product_id,aligned.supplier_id=loaded.canonical_product_id,loaded.supplier_id
        for v,w in zip(aligned.variants,loaded.variants):v.canonical_variant_id=w.canonical_variant_id
        assert semantic(aligned)==semantic(loaded),'Persistence changed typed product semantics'
    before=audit(restored,db,sid)
    assert before['field_states'].get('observed',0)>0
    write_evidence_bundle(restored,directory/'bundle.json')
    assert [semantic(p) for p in read_evidence_bundle(directory/'bundle.json')]==[semantic(p) for p in restored]
    # A genuinely separate process must reconstruct and retrieve the graph.
    child=subprocess.run([sys.executable,__file__,'--reopen',str(db),str(sid)],capture_output=True,text=True,timeout=30)
    (directory/'restart.log').write_text(child.stdout+child.stderr)
    assert child.returncode==0,'Separate-process restart failed: '+child.stderr[-500:]
    for fmt,suffix in [('csv','csv'),('google_shopping','xml'),('idealo','tsv')]:
        target=directory/('products.'+suffix);sidecar=directory/(fmt+'.sidecar.json')
        if fmt=='csv':to_csv(restored,str(target),evidence_path=str(sidecar))
        else:to_feed(restored,str(target),format=fmt,evidence_path=str(sidecar))
        content=target.read_bytes();mapping=json.loads(sidecar.read_text())
        assert [semantic(p) for p in load_evidence_sidecar(mapping,content)]==[semantic(p) for p in restored]
        try:load_evidence_sidecar(mapping,content+b' ')
        except ValueError:pass
        else:raise AssertionError('Modified projection accepted')
    cutoff=datetime.now(timezone.utc)+timedelta(seconds=1)
    protected=prune_evidence(db_path=str(db),before=cutoff,dry_run=False,batch_size=1000)
    assert protected.expired==0 and protected.protected>0
    assert audit(load_snapshot(sid,db_path=str(db)),db,sid)==before
    expired=prune_evidence(db_path=str(db),before=cutoff,protect_references=False,dry_run=False,batch_size=1000)
    assert expired.expired>0
    unavailable=load_snapshot(sid,db_path=str(db));tombstones=0
    for owner,key in owners(unavailable):
        for tombstone in getattr(owner,'evidence_availability',[]):
            assert get_evidence(tombstone['evidence_id'],snapshot_id=sid,record_key=key,db_path=str(db)).status=='expired'
            assert tombstone['evidence_id'] not in {e.evidence_id for e in owner.evidence_contract.evidence}
            tombstones+=1
    assert tombstones==expired.expired
    write_evidence_bundle(unavailable,directory/'expired-bundle.json')
    imported=read_evidence_bundle(directory/'expired-bundle.json')
    assert [semantic(p) for p in imported]==[semantic(p) for p in unavailable]
    sid2=save_snapshot(imported,url,db_path=str(db))
    for owner,key in owners(imported):
        for t in getattr(owner,'evidence_availability',[]):
            assert get_evidence(t['evidence_id'],snapshot_id=sid2,record_key=key,db_path=str(db)).status=='expired'
    with sqlite3.connect(db) as conn:
        assert conn.execute('PRAGMA integrity_check').fetchone()==('ok',)
        assert not conn.execute('PRAGMA foreign_key_check').fetchall()
    return {'status':'passed','url':url,'products':len(products),'variants':sum(len(p.variants) for p in products),**before,
            'expired_captures':tombstones,'source_complete':result.complete,'sample_only':True,
            'checks':['live normalization/resolution','atomic typed storage','separate-process restart/retrieval','lossless bundle',
                      'CSV/Google/Idealo companions and tamper rejection','protected prune','explicit expiry','expired bundle resave','SQLite integrity/FKs']}

def driver(names):
    for name in names:
        target=ROOT/(name+'.json')
        if target.exists() and json.loads(target.read_text()).get('status')=='passed':
            print(name+': saved pass reused',flush=True);continue
        log=ROOT/(name+'.log');start=time.monotonic()
        with log.open('w') as f:
            try:
                run=subprocess.run([sys.executable,__file__,'--worker',name],stdout=f,stderr=f,timeout=100)
                if run.returncode and not target.exists():target.write_text(json.dumps({'status':'failed','exit_code':run.returncode}))
            except subprocess.TimeoutExpired:target.write_text(json.dumps({'status':'timeout'}))
        print(name+': '+target.read_text()+' elapsed='+str(round(time.monotonic()-start,2)),flush=True)

if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--reopen':
        print(json.dumps(audit(load_snapshot(int(sys.argv[3]),db_path=sys.argv[2]),Path(sys.argv[2]),int(sys.argv[3]))))
    elif len(sys.argv)>1 and sys.argv[1]=='--worker':
        name=sys.argv[2]
        try:result=asyncio.run(asyncio.wait_for(live(name),85))
        except Exception as exc:
            result={'status':'failed','error':type(exc).__name__+': '+str(exc)}
            import traceback;traceback.print_exc()
        (ROOT/(name+'.json')).write_text(json.dumps(result,indent=2))
        if result['status']!='passed':sys.exit(1)
    else:driver(sys.argv[1:] or list(CASES))
