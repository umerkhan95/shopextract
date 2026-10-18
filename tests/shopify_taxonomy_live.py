"""One explicitly authorized public product + tokenless category probe, <=2 HTTP/30s."""
import asyncio,json,time
from pathlib import Path
import httpx
from shopextract._capture import capture
from shopextract._models import Platform
from shopextract.extractors._storefront import request
from shopextract.extractors.shopify_taxonomy import ShopifyStorefrontConfig,supplement_categories
from shopextract.taxonomies.shopify import load_shopify_taxonomy,normalize_with_shopify_taxonomy
from shopextract.categories import categorized_product_to_record

STORE='https://www.boardgamebliss.com'
HANDLE='eternal-decks-french-edition-minor-damage'
OUT=Path('artifacts/shopify-taxonomy')

class BoundedWire(httpx.AsyncBaseTransport):
    def __init__(self):self.wire=httpx.AsyncHTTPTransport(retries=0);self.requests=[]
    async def handle_async_request(self,req):
        if len(self.requests)>=2:raise ValueError('live_request_budget')
        # Never follow to a different merchant/credential destination.
        if req.url.scheme!='https' or req.url.host!='www.boardgamebliss.com':raise ValueError('live_origin_denied')
        record={'method':req.method,'url':str(req.url)};self.requests.append(record)
        (OUT/'merchant-live-requests.json').write_text(json.dumps(self.requests))
        response=await self.wire.handle_async_request(req);record['status']=response.status_code
        (OUT/'merchant-live-requests.json').write_text(json.dumps(self.requests))
        return response
    async def aclose(self):await self.wire.aclose()

async def probe(result):
    started=time.monotonic();wire=BoundedWire()
    result.update({'state':'blocked','merchant':STORE,'product_handle':HANDLE,'http_requests':wire.requests,
        'limits':{'requests':2,'seconds':30,'request_seconds':10,'products':2,'retries':0},
        'merchant_products_observed':0,'merchant_category_assignments_observed':0,'llm_calls':0,'browser_calls':0,
        'note':'Single authorized merchant product probe; never all merchant category assignments'})
    try:
        catalog=load_shopify_taxonomy(catalog_root=Path('build/shopify-taxonomy/catalogs'))
        result['catalog_fingerprint']=catalog.fingerprint
        async with httpx.AsyncClient(transport=wire,timeout=10,trust_env=False,follow_redirects=False,headers={'User-Agent':'ShopExtract/0.1.2'}) as client:
            response=await request(client,'GET',STORE+'/products/'+HANDLE+'.json')
            product=response.json().get('product')
            if not isinstance(product,dict):raise ValueError('public_product_unavailable')
            raw=capture(product,str(response.url),'shopify_product_api')
            result['merchant_products_observed']=1
            await supplement_categories([raw],ShopifyStorefrontConfig(STORE+'/api/2026-10/graphql.json',auth_mode='tokenless'),client=client)
        value=normalize_with_shopify_taxonomy(raw,platform=Platform.SHOPIFY,shop_url=STORE,taxonomy=catalog,allow_unknown_source_version=True)
        if value is None:raise ValueError('normalization_unavailable')
        record=categorized_product_to_record(value);schema=catalog.schema_for(value)
        projection={k:raw[k] for k in ('id','title','handle','product_type','category','_category_diagnostics','_capture','_field_sources') if k in raw}
        retained={'raw_projection':projection,'companion':record}
        encoded=json.dumps(retained,ensure_ascii=False).encode()
        if len(encoded)>1024*1024:raise ValueError('live_retained_byte_cap')
        (OUT/'merchant-live-capture.json').write_bytes(encoded)
        observed=[t for o in value.observations if o.taxonomy_kind=='standard' for t in o.terms if any(f.binding.facet=='native_id' and f.support.value=='observed' and f.outcome.accepted for f in t.facts)]
        result.update(state='passed' if schema.resolved else 'blocked',reason=None if schema.resolved else 'category_null_denied_or_unmapped',
            merchant_category_assignments_observed=len(observed),resolved_ids=[s.category.id for s in schema.resolved],
            category_states=[{'state':o.source_state,'completeness':o.completeness,'reason':o.reason} for o in value.observations if o.taxonomy_kind=='standard'],
            retained_bytes=len(encoded),raw_category=raw.get('category'))
    except (ValueError,httpx.HTTPError,KeyError) as error:result['reason']=type(error).__name__+':'+str(error)[:160]
    finally:result['seconds']=round(time.monotonic()-started,3)
    return result

async def main():
    result={}
    try:await asyncio.wait_for(probe(result),30)
    except asyncio.TimeoutError:result.update(state='blocked',reason='aggregate_timeout',seconds_limit=30,note='No successful category acquisition claimed')
    (OUT/'merchant-live-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':asyncio.run(main())
