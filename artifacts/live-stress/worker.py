"""One actual live case/process. Read-only requests, captured evidence, bounded exports."""
import os
for key in ('OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'):
    os.environ[key]='2'
os.environ['TOKENIZERS_PARALLELISM']='false'
import asyncio
import gc
import gzip
from collections import Counter
from datetime import datetime,timezone
import json
from pathlib import Path
import resource
import sys
import time
from unittest.mock import patch

import httpx
from shopextract import Platform,extract,normalize
from shopextract._capture import FRAGMENT_BYTES,PRODUCT_BYTES,_size,_plain
from shopextract._evidence import factual_paths
from shopextract.extractors.magento_graphql import MagentoGraphQLExtractor
from shopextract.extractors.shopware import ShopwareExtractor
from shopextract.extractors.shopify import ShopifyExtractor
from shopextract.extractors.woocommerce import WooCommerceExtractor

ROOT=Path(__file__).resolve().parent
CASE=json.loads(sys.argv[1])
NETWORK=[]
REMOTE_TOTALS=[]


class Client(httpx.AsyncClient):
    async def send(self,request,*args,**kwargs):
        started=time.monotonic()
        try:
            response=await super().send(request,*args,**kwargs)
            NETWORK.append({'method':request.method,'url':str(response.url),'status':response.status_code,
                            'header_seconds':round(time.monotonic()-started,3)})
            return response
        except Exception as e:
            NETWORK.append({'method':request.method,'url':str(request.url),'error':type(e).__name__})
            raise


def rss():
    v=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return round(v/(1024*1024 if sys.platform=='darwin' else 1024),2)


def audit(product,defects):
    c=product.evidence_contract
    c.validate()
    facts=factual_paths(product)
    if {o.field_path for o in c.observations}!=set(facts):defects.append('incomplete_field_coverage')
    states=Counter()
    for o in c.observations:
        states[o.state]+=1
        if o.state=='observed':
            if not o.evidence_ids or _plain(o.normalized_value)!=_plain(facts[o.field_path]):
                defects.append('observed_value_mismatch:'+o.field_path)
        elif not o.reason:defects.append('missing_reason:'+o.field_path)
        if o.validated_confidence is not None:defects.append('uncalibrated_confidence')
    for e in c.evidence:
        e.resolve_pointer()
        if _size(e.retained_data)>FRAGMENT_BYTES:defects.append('fragment_budget')
        if not e.observed_at.tzinfo:defects.append('timezone_missing')
        if not any(n.get('url')==e.source_url for n in NETWORK):defects.append('source_not_fetched:'+e.source_url)
    if sum(_size(e.retained_data) for e in c.evidence)>PRODUCT_BYTES:defects.append('contract_budget')
    context=product.raw_data.get('_capture',{})
    if sum(_size(x) for x in context.get('values',{}).values())>PRODUCT_BYTES:defects.append('capture_budget')
    view=product.trust_view()
    return {'id':product.external_id,'title':product.title,'price':str(product.price),'currency':product.currency,
            'stock':product.in_stock,'variants':len(product.variants),'states':dict(states),
            'key_states':{k:view[k]['state'] for k in ('/price','/currency','/in_stock','/product_url')},
            'truncated_evidence':sum(e.truncated for e in c.evidence),'retained_bytes':sum(_size(e.retained_data) for e in c.evidence)}


async def operation():
    kind=CASE['kind'];url=CASE['url'];limit=CASE['limit'];platform=Platform(CASE['platform'])
    if kind=='generic_css':
        from bs4 import BeautifulSoup
        from urllib.parse import urljoin
        from types import SimpleNamespace
        from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
        from shopextract.extractors.css import CSSExtractor
        schema={'name':'Book','baseSelector':'.product_page','fields':[
            {'name':'title','selector':'h1','type':'text'},
            {'name':'price','selector':'.price_color','type':'text'},
            {'name':'sku','selector':'table tr:first-child td','type':'text'},
            {'name':'image','selector':'.carousel-inner img','type':'attribute','attribute':'src'}]}
        rounds=[]
        async with httpx.AsyncClient(timeout=15,follow_redirects=True) as client:
            index=await client.get(url);index.raise_for_status()
            links=[urljoin(str(index.url),a['href']) for a in BeautifulSoup(index.text,'html.parser').select('article.product_pod h3 a')][:limit]
            for _ in range(CASE.get('repeats',1)):
                products=[];started=time.monotonic();issues=[]
                for link in links:
                    response=await client.get(link);response.raise_for_status()
                    at=datetime.now(timezone.utc).isoformat()
                    fetched=str(response.url)
                    data=JsonCssExtractionStrategy(schema).extract(fetched,response.text)
                    result=SimpleNamespace(success=True,url=fetched,html=response.text,extracted_content=json.dumps(data))
                    for raw in CSSExtractor(schema)._parse_extracted_content(fetched,result):
                        raw['_capture']['at']=at
                        product=normalize(raw,Platform.GENERIC,fetched)
                        if product:products.append(product)
                rounds.append({'seconds':round(time.monotonic()-started,2),'products':[audit(p,issues) for p in products],'defects':issues})
        return products,{'tier':'css_http','rounds':rounds,'errors':[],'complete':False,'reasons':['sample_only']}
    if kind=='pipeline':
        rounds=[]
        for _ in range(CASE.get('repeats',1)):
            start=time.monotonic()
            result=await extract(url,platform=platform,max_urls=limit,enrich_identifiers=CASE.get('enrich',False))
            issues=[]
            snapshots=[audit(p,issues) for p in result.products]
            gc.collect()
            try:
                import psutil
                current=round(psutil.Process().memory_info().rss/(1024*1024),2)
            except ImportError:current=None
            rounds.append({'seconds':round(time.monotonic()-start,2),'current_rss_mib':current,
                           'peak_rss_mib':rss(),'products':snapshots,'defects':issues})
        return result.products,{'tier':result.tier.value,'errors':result.errors,'complete':result.catalog_complete,
                                'reasons':result.incompleteness_reasons,'rounds':rounds}
    cls={'magento':MagentoGraphQLExtractor,'shopware':ShopwareExtractor,
         'shopify':ShopifyExtractor,'woo':WooCommerceExtractor}.get(kind)
    if kind=='magento_boundary':
        import shopextract.extractors.magento_graphql as module
        cls=MagentoGraphQLExtractor
        module._QUERY=module._QUERY.replace('filter:{}','filter:{sku:{in:'+json.dumps(CASE['skus'])+'}}')
    options={'timeout':15,'max_pages':CASE.get('max_pages',20)}
    if kind in ('magento','magento_boundary','shopware'):options['page_size']=CASE.get('page_size',5)
    adapter=cls(**options)
    # Record Magento response pagination metadata without altering transport or content.
    if kind in ('magento','magento_boundary'):
        import shopextract.extractors.magento_graphql as module
        original=module.json_body
        def inspect(response):
            d=original(response);REMOTE_TOTALS.append(d['data']['products'].get('total_count'));return d
        module.json_body=inspect
    if kind=='woo':result=await adapter.extract(url)
    elif kind=='shopify':result=await adapter.extract(url,max_products=limit,enrich_identifiers=CASE.get('enrich',False))
    else:result=await adapter.extract(url,max_products=limit)
    products=[normalize(item,platform,url) for item in result.products]
    return [p for p in products if p],{'complete':result.complete,'errors':[result.error] if result.error else [],
                                      'reasons':[result.completeness_reason] if result.completeness_reason else [],
                                      'raw_count':len(result.products),'remote_totals':REMOTE_TOTALS}


async def main():
    started=time.monotonic();baseline=rss();defects=[];products=[];metadata={}
    try:
        with patch('httpx.AsyncClient',Client):
            products,metadata=await asyncio.wait_for(operation(),CASE.get('timeout',60))
        rows=[audit(p,defects) for p in products]
        for r in metadata.get('rounds',[]):defects.extend(r['defects'])
        if metadata.get('errors') and CASE['platform']!='bigcommerce':
            defects.append('unexpected_source_error:'+'; '.join(metadata['errors']))
        if metadata.get('raw_count',len(products))!=len(products):defects.append('normalization_dropped_records')
        ids=[p.external_id for p in products if p.external_id]
        if len(set(ids))!=len(ids):defects.append('duplicate_product_ids')
        if CASE['kind']!='woo' and len(products)>CASE['limit']:defects.append('product_budget_exceeded')
        if metadata.get('complete') is True and REMOTE_TOTALS and len(products)<REMOTE_TOTALS[-1]:
            defects.append('false_catalog_complete')
        if not products:defects.append('no_products')
        output=ROOT/(CASE['name']+'.evidence.json.gz')
        with gzip.open(output,'wt',encoding='utf-8') as f:
            f.write('[')
            for i,p in enumerate(products):
                if i:f.write(',')
                json.dump({'raw':p.raw_data,'contract':p.evidence_contract.to_dict()},f,default=str,ensure_ascii=False)
            f.write(']')
        metadata['evidence_export_bytes']=output.stat().st_size
        if output.stat().st_size>24*1024*1024:defects.append('compressed_export_over_24_mib')
        status='fail' if defects else 'pass'
    except Exception as e:
        rows=[];status='error';defects.append(type(e).__name__+': '+str(e)[:200])
    result={'case':CASE,'at':datetime.now(timezone.utc).isoformat(),'status':status,
            'seconds':round(time.monotonic()-started,2),'baseline_rss_mib':baseline,'peak_rss_mib':rss(),
            'requests':len(NETWORK),'network':NETWORK,'metadata':metadata,'defects':defects,'products':rows,
            'product_count':len(products),'variant_count':sum(len(p.variants) for p in products)}
    (ROOT/(CASE['name']+'.json')).write_text(json.dumps(result,default=str,indent=2))
    print(json.dumps({k:result[k] for k in ['status','seconds','peak_rss_mib','requests','product_count','variant_count','defects']}),flush=True)

asyncio.run(main())
