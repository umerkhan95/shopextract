"""Approved read-only Bliss run: <=2 items,3 physical attempts/phase,6 total."""
import asyncio
from dataclasses import asdict
from datetime import datetime,timedelta,timezone
import json
from pathlib import Path
import time
from shopextract.tools import Limits,ToolConfig,ToolRuntime
from shopextract.tools.context import OperationBudget,OperationContext
from shopextract.tools.contracts import ToolError
from shopextract.maintenance import Budgets,Goal,MaintenanceEngine,MaintenanceStore
from shopextract.maintenance.engine import _Accounting,json_value
from shopextract._portable import product_from_record
from shopextract._evidence import trust_view

ROOT=Path(__file__).resolve().parent
ORIGIN='https://www.blissworld.com'
CONFIG=ToolConfig(allowed_origins=(ORIGIN,),limits=Limits(item_count=2,requests=3,response_bytes=2*1024*1024,timeout_seconds=10))
PHASE1=[];PHASE2=[]


def save(name,value):
    (ROOT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2))


class Recorder:
    def before_request(self,method,url):
        if len(PHASE1)>=3:raise ToolError('resource_limit')
        PHASE1.append({'method':method,'url':url,'started_at':datetime.now(timezone.utc).isoformat()})
        return str(len(PHASE1))
    def after_request(self,method,url,status):PHASE1[-1]['status']=status


async def main():
    started=time.monotonic()
    save('config.json',{'origin':ORIGIN,'items':2,'physical_attempts_per_phase':3,'physical_attempts_total':6,
        'logical_source_attempts_per_phase':2,'attempt_seconds':10,'phase_seconds':30,'total_seconds':60,
        'llm_tokens':0,'llm_cost_micros':0,'response_bytes':2*1024*1024})
    runtime=ToolRuntime(CONFIG)
    try:
        now=datetime.now(timezone.utc)
        context=OperationContext('actual-live-smoke',time.monotonic()+10,asyncio.Event(),OperationBudget(CONFIG.limits),runtime.auxiliary,now,Recorder())
        capture=await asyncio.wait_for(runtime.sources.execute('extract',ORIGIN,2,context),30)
        assert 1<=len(capture['products'])<=2
        products=[product_from_record(record) for record in capture['products']]
        assert all(trust_view(product,product.evidence_contract)['/title']['state']=='observed' for product in products)
        save('phase1-capture.json',capture)
        save('phase1-smoke.json',{'state':'passed','products':len(products),'complete':capture['complete'],
            'physical_requests':PHASE1,'seconds':time.monotonic()-started,'provenance':'actual-live'})
    except Exception as error:
        save('phase1-smoke.json',{'state':'blocked','error':getattr(error,'code',type(error).__name__),
            'message':str(error),'physical_requests':PHASE1,'seconds':time.monotonic()-started,'provenance':'actual-live'})
        raise
    finally:await runtime.aclose()
    # Barrier: actual first smoke/capture are durable before phase2 starts.
    assert time.monotonic()-started<30
    baseline=tuple(json_value(asdict(product)) for product in products)
    profiles={str(product.external_id or product.canonical_product_id or i):'generic-v1' for i,product in enumerate(products)}
    store=MaintenanceStore(ROOT/'jobs.db')
    configured=Goal(baseline=baseline,supplier_origin=ORIGIN,product_urls=(ORIGIN,),fields=('title',),
        profiles=profiles,deadline=(datetime.now(timezone.utc)+timedelta(seconds=30)).isoformat(),
        budgets=Budgets(requests=3,products=2,tokens=0,cost_micros=0,attempt_seconds=10))
    original=_Accounting.before_request
    def record(self,method,url):
        attempt=original(self,method,url)
        PHASE2.append({'method':method,'url':url,'started_at':datetime.now(timezone.utc).isoformat()})
        assert len(PHASE2)<=3 and len(PHASE1)+len(PHASE2)<=6
        return attempt
    _Accounting.before_request=record
    engine=MaintenanceEngine(store,tool_config=CONFIG)
    try:
        job=store.create(configured)
        report=await asyncio.wait_for(engine.run(job),min(30,60-(time.monotonic()-started)))
        save('phase2-report.json',report)
        assert report['findings'] and report['usage']['tokens']==report['usage']['cost_micros']==0
        assert report['usage']['requests']==len(PHASE2)
        assert all(finding['evidence_ids'] for finding in report['findings'])
        actual_evidence={key:store.evidence(job,key) for finding in report['findings'] for key in finding['evidence_ids']}
        save('phase2-evidence.json',actual_evidence)
        await engine.close()
        before=len(PHASE2)
        reopened=MaintenanceEngine(MaintenanceStore(ROOT/'jobs.db'),tool_config=CONFIG)
        try:resumed=await asyncio.wait_for(reopened.resume(job),min(10,60-(time.monotonic()-started)))
        finally:await reopened.close()
        assert len(PHASE2)==before and resumed['findings']==report['findings']
        elapsed=time.monotonic()-started
        assert elapsed<=60
        save('summary.json',{'state':'passed','provenance':'actual-live','physical_requests_phase1':PHASE1,
            'physical_requests_phase2':PHASE2,'physical_requests_total':len(PHASE1)+len(PHASE2),
            'report_state':report['state'],'report_stop_reason':report['stop_reason'],'findings':len(report['findings']),
            'statuses':[finding['status'] for finding in report['findings']], 'restart_extra_requests':len(PHASE2)-before,
            'llm_tokens':report['usage']['tokens'],'seconds':elapsed,
            'commercial_specification_change':'inconclusive unless actually observed; no induced live change'})
    except Exception as error:
        save('summary.json',{'state':'blocked','provenance':'actual-live','error':getattr(error,'code',type(error).__name__),
            'message':str(error),'physical_requests_phase1':PHASE1,'physical_requests_phase2':PHASE2,
            'seconds':time.monotonic()-started})
        raise
    finally:
        _Accounting.before_request=original
        await engine.close()


if __name__=='__main__':asyncio.run(main())
