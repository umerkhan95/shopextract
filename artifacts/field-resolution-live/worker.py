"""Live capture/resolution audit plus explicitly synthetic policy fault probes."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='2'
os.environ['TOKENIZERS_PARALLELISM']='false'
import asyncio
from copy import copy, deepcopy
from dataclasses import asdict
from datetime import datetime,timedelta,timezone
from decimal import Decimal
import gzip
import importlib.util
import json
from pathlib import Path
import random
import sys
import time
from unittest.mock import patch
from uuid import NAMESPACE_URL,uuid5

ROOT=Path(__file__).resolve().parent
CASE=json.loads(sys.argv[1])
spec=importlib.util.spec_from_file_location('live_capture_helpers',ROOT.parent/'live-stress/worker.py')
h=importlib.util.module_from_spec(spec);spec.loader.exec_module(h)
h.CASE=CASE
from shopextract import (Evidence,FieldObservation,Platform,TrustContract,classify_match,
                        normalize,resolve_fields,resolution_references)


def require(ok,label):
    if not ok:raise AssertionError(label)


def fault_probes(product,clock):
    """Altered fixtures are not observations from a live manufacturer/store."""
    seed=next(o for o in product.evidence_contract.observations if o.field_path=='/price' and o.state=='observed')
    source=next(e for e in product.evidence_contract.evidence if e.evidence_id in seed.evidence_ids)
    def sample(label,path,value,role,age=timedelta(0),state='observed'):
        e=Evidence('e_'+str(uuid5(NAMESPACE_URL,CASE['name']+label)),source.source_url,clock-age,
            'synthetic_fault_probe_from_live_seed',retained_data={'probe_value':value,
            'live_seed_evidence_id':source.evidence_id},pointer='/probe_value',source_role=role)
        o=FieldObservation('o_'+str(uuid5(NAMESPACE_URL,CASE['name']+label)),path,state,value,value,
            [e.evidence_id] if state=='observed' else [],reason='' if state=='observed' else 'Synthetic unsupported fault probe')
        return e,o
    def run(label,items,state,selected=None):
        c=TrustContract([x[0] for x in items],[x[1] for x in items])
        resolved=resolve_fields(c,as_of=clock);r=resolved.resolutions[0]
        require(r.state==state,label+':state')
        if selected is not None:require(r.selected_observation_id==items[selected][1].observation_id,label+':selection')
        else:require(r.selected_observation_id is None,label+':unresolved')
        require(len(r.observation_ids)==len(items),label+':preservation')
        return {'probe':label,'state':r.state.value,'candidate_count':len(items),'synthetic':True}
    price=seed.normalized_value
    probes=[]
    probes.append(run('offer-not-manufacturer-list',[sample('p1','/price',price,'supplier'),sample('p2','/price',price+Decimal(1),'verified_manufacturer')],'observed',0))
    probes.append(run('manufacturer-spec-authority',[sample('s1','/title',product.title,'supplier'),sample('s2','/title',product.title+' altered probe','verified_manufacturer')],'observed',1))
    probes.append(run('equal-authority-price-conflict',[sample('c1','/price',price,'supplier'),sample('c2','/price',price+Decimal(1),'supplier')],'conflicting'))
    probes.append(run('equivalent-price',[sample('e1','/price',price,'supplier'),sample('e2','/price',price,'supplier')],'observed',
        0 if 'o_'+str(uuid5(NAMESPACE_URL,CASE['name']+'e1'))<'o_'+str(uuid5(NAMESPACE_URL,CASE['name']+'e2')) else 1))
    probes.append(run('stale-offer',[sample('st','/price',price,'supplier',timedelta(days=2))],'expired'))
    probes.append(run('future-offer',[sample('fu','/price',price,'supplier',timedelta(seconds=-1))],'unknown'))
    probes.append(run('unsupported-offer',[sample('un','/price',price,'supplier',state='unsupported')],'unsupported'))
    probes.append(run('zero-is-not-false',[sample('b1','/in_stock',False,'supplier'),sample('b2','/in_stock',0,'supplier')],'conflicting'))
    return probes


async def main():
    started=time.monotonic();products=[];rows=[];probes=[];defects=[];metadata={};paired=[];paired_resolution=None
    try:
        with patch('httpx.AsyncClient',h.Client):
            products,metadata=await asyncio.wait_for(h.operation(),CASE.get('timeout',75))
            # Fetch actual product HTML for independent API/HTML observation comparison.
            if CASE.get('paired_html') and products:
                from shopextract.extractors.unified import UnifiedCrawlExtractor
                fetcher=UnifiedCrawlExtractor()
                p=products[0]
                html=await asyncio.wait_for(fetcher._fetch_html_httpx(p.product_url),35)
                if html:
                    raws=fetcher._extract_structured_from_html(html,html.source_url)
                    for raw in raws:
                        raw['_capture']['at']=html.observed_at.isoformat()
                        q=normalize(raw,Platform.GENERIC,html.source_url)
                        if q and q.product_url.rstrip('/')==p.product_url.rstrip('/'):
                            paired.append(q);break
        require(not metadata.get('errors') or CASE['platform']=='bigcommerce',
                'unexpected-source-error:'+str(metadata.get('errors')))
        clock=datetime.now(timezone.utc)
        for p in products+paired:
            issues=[];base=h.audit(p,issues);require(not issues,'capture-audit:'+str(issues))
            original=p.evidence_contract;before=original.to_dict()
            resolved=resolve_fields(original,as_of=clock)
            require(original.to_dict()==before,'input-mutated')
            require({o.observation_id:asdict(o) for o in original.observations}=={o.observation_id:asdict(o) for o in resolved.observations},'observations-changed')
            require({e.evidence_id:asdict(e) for e in original.evidence}=={e.evidence_id:asdict(e) for e in resolved.evidence},'evidence-changed')
            base_view=p.trust_view()
            legacy=copy(p);del legacy.evidence_contract
            baseline_decision=asdict(classify_match(legacy,legacy));baseline_decision.pop('field_support')
            p.evidence_contract=resolved
            view=p.trust_view()
            require(all(view[path]['value']==v['value'] and view[path]['state']==v['state'] for path,v in base_view.items()),'fresh-resolution-changed-facts')
            d=classify_match(p,p);comparison=asdict(d);support=comparison.pop('field_support')
            require(comparison==baseline_decision,'matching-semantics-changed')
            require(support['a']==resolution_references(resolved),'matching-references-missing')
            require(TrustContract.from_dict(json.loads(json.dumps(resolved.to_dict()))).to_dict()==resolved.to_dict(),'typed-roundtrip')
            shuffled=deepcopy(original);rng=random.Random(36)
            rng.shuffle(shuffled.evidence);rng.shuffle(shuffled.observations)
            require(resolve_fields(shuffled,as_of=clock).to_dict()==resolved.to_dict(),'nondeterministic-order')
            expired=resolve_fields(original,as_of=clock+timedelta(days=31))
            exp={r.field_path:r for r in expired.resolutions}
            require(all(exp[o.field_path].state=='expired' for o in original.observations if o.state=='observed'),'stale-still-selected')
            base['resolved_fields']=len(resolved.resolutions)
            base['observed_fields']=sum(r.state=='observed' for r in resolved.resolutions)
            rows.append(base)
        require(products,'no-products')
        probes=fault_probes(products[0],clock)
        if paired:
            # Only compare equal-meaning fields with explicitly same currency/context.
            a,b=products[0],paired[0]
            if a.currency==b.currency:
                paths={'/title','/price','/currency','/in_stock','/gtin','/vendor'}
                ao={o.field_path:o for o in a.evidence_contract.observations if o.field_path in paths}
                bo={o.field_path:o for o in b.evidence_contract.observations if o.field_path in paths}
                observations=[o for path in sorted(ao.keys() & bo.keys()) for o in (ao[path],bo[path])]
                ids={i for o in observations for i in o.evidence_ids}
                evidence=[e for p in (a,b) for e in p.evidence_contract.evidence if e.evidence_id in ids]
                joined=TrustContract(evidence,observations)
                paired_resolution=resolve_fields(joined,as_of=clock)
                require(all(len(r.observation_ids)==2 for r in paired_resolution.resolutions),'paired-alternatives-lost')
                # Source-channel differences are deliberately not made into a fake consensus.
                by_id={o.observation_id:o for o in observations}
                for r in paired_resolution.resolutions:
                    supported=[by_id[i] for i in r.observation_ids if by_id[i].state=='observed']
                    if len(supported)==2 and supported[0].normalized_value!=supported[1].normalized_value and r.field_path in ('/price','/currency','/in_stock'):
                        require(r.state=='conflicting','real-pair-conflict-discarded')
                (ROOT/(CASE['name']+'.paired.json')).write_text(json.dumps(paired_resolution.to_dict(),indent=2))
            paired_meta={'api_title':a.title,'html_title':b.title,'same_currency':a.currency==b.currency,
                         'price_equal':a.price==b.price,'aligned_by_url':True,
                         'note':'Independent live channels, not asserted equivalent product/variant pricing'}
        else:paired_meta=None
        out=ROOT/(CASE['name']+'.evidence.json.gz')
        with gzip.open(out,'wt',encoding='utf-8') as f:
            f.write('[')
            for i,p in enumerate(products+paired):
                if i:f.write(',')
                json.dump({'url':p.product_url,'contract':p.evidence_contract.to_dict()},f,default=str)
            f.write(']')
        status='pass'
    except Exception as e:
        status='fail';defects.append(type(e).__name__+': '+str(e)[:400]);paired_meta=None
    result={'case':CASE,'at':datetime.now(timezone.utc).isoformat(),'status':status,
            'seconds':round(time.monotonic()-started,2),'requests':len(h.NETWORK),
            'network':h.NETWORK,'metadata':metadata,'defects':defects,'products':rows,
            'product_count':len(products),'variant_count':sum(len(p.variants) for p in products),
            'paired_html_count':len(paired),'paired_comparison':paired_meta,
            'paired_resolutions':resolution_references(paired_resolution) if paired_resolution else {},'policy_probes':probes,'peak_rss_mib':h.rss()}
    (ROOT/(CASE['name']+'.json')).write_text(json.dumps(result,default=str,indent=2))
    print(json.dumps({k:result[k] for k in ['status','seconds','requests','product_count','variant_count','paired_html_count','defects']}),flush=True)

asyncio.run(main())
