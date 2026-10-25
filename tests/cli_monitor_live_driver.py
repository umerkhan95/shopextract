"""P3 one authorized bounded merchant extraction->temporary SQLite->CLI lookup smoke.
Real transport <=5 GET attempts, no repeated URL/retry, max2 products,30s total.
Expected: nonempty native captured products, portable valid; save/load exact money
and native evidence ID; scoped evidence lookup available, no additional HTTP sends.
This is extraction persistence integration, not a live source-price-change claim.
"""
import asyncio
import json
from pathlib import Path
import tempfile
import time

import httpx
from click.testing import CliRunner
from shopextract import extract,Platform
from shopextract.cli import main
from shopextract._execution import ExecutionPolicy,execution_policy
from shopextract._portable import product_to_record
from shopextract.monitor.evidence import save_snapshot

OUT=Path('specs/011-cli-feature-parity/p3/evidence/live');OUT.mkdir(parents=True,exist_ok=True)
HOST='www.boardgamebliss.com'
class LiveStop(BaseException):pass
original=httpx.AsyncHTTPTransport.handle_async_request
attempts=[];started=time.monotonic()
async def counted(self,request):
    if request.method!='GET' or request.url.host!=HOST or len(attempts)>=5 or any(r['url']==str(request.url) for r in attempts):
        raise LiveStop('undeclared host/method, request cap or retry stopped before send')
    if time.monotonic()-started>=30:raise LiveStop('deadline')
    record=dict(method=request.method,url=str(request.url));attempts.append(record)
    response=await original(self,request);record['status']=response.status_code
    if response.status_code>=400:raise LiveStop('source failure stops retry/fallback')
    return response
report=dict(target='https://'+HOST,path='explicit Shopify native extract -> save_snapshot temporary SQLite -> CLI snapshot-load/evidence get',limits=dict(actual_http_attempts=5,retained_products=2,wall_seconds=30,retries=0),attempts=attempts,actual_observation='pending',retained_products=0,source_price_change='unobserved; synthetic CLI-native reliable mechanism tested separately')
httpx.AsyncHTTPTransport.handle_async_request=counted
try:
    async def operation():
        with execution_policy(ExecutionPolicy(),30):
            return await asyncio.wait_for(extract('https://'+HOST,platform=Platform.SHOPIFY,max_urls=2),30)
    result=asyncio.run(operation());assert 0<len(result.products)<=2
    records=[product_to_record(p) for p in result.products];report['retained_products']=len(records)
    assert all(r['evidence_contract'] and r['product']['title'] for r in records)
    (OUT/'extraction-portable.json').write_text(json.dumps(records))
    with tempfile.TemporaryDirectory(prefix='shopextract-p3-live-') as directory:
        db=str(Path(directory)/'snapshots.db')
        sid=save_snapshot(result.products,HOST,db_path=db,metadata=dict(observation_scope=result.observation_scope,catalog_complete=result.catalog_complete,incompleteness_reasons=list(result.incompleteness_reasons),max_urls=2))
        sends=len(attempts)
        loaded=CliRunner().invoke(main,['snapshot-load',str(sid),'--db',db]);assert loaded.exit_code==0,loaded.output
        (OUT/'snapshot-load.json').write_text(loaded.output);products=json.loads(loaded.output)['data']['products']
        assert [p['product']['price'] for p in products]==[p['product']['price'] for p in records]
        eid=products[0]['evidence_contract']['evidence'][0]['evidence_id']
        lookup=CliRunner().invoke(main,['evidence','get',eid,'--snapshot',str(sid),'--record-key','product/0','--db',db]);assert lookup.exit_code==0,lookup.output
        (OUT/'evidence-get.json').write_text(lookup.output);evidence=json.loads(lookup.output)['data']
        assert evidence['status']=='available' and evidence['evidence_id']==eid and len(attempts)==sends
        report.update(snapshot_id=sid,evidence_status=evidence['status'],lookup_http_attempts=len(attempts)-sends,catalog_complete=result.catalog_complete,native_source_paths=[entry['url'] for entry in attempts],actual_observation='passed_bounded_persistence_smoke')
    assert time.monotonic()-started<=30
except (Exception,LiveStop) as exc:
    report['actual_observation']='failed_or_blocked';report['limitation']=str(exc)[:250]
finally:
    httpx.AsyncHTTPTransport.handle_async_request=original
    report['live_wall_seconds']=round(time.monotonic()-started,3);report['actual_http_attempts']=len(attempts)
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='attempts'}))
