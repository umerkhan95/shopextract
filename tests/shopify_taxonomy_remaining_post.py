"""One remaining authorized POST; no GET/retry. Old retained source stays dated."""
import asyncio,hashlib,json,time
from pathlib import Path
import httpx
from shopextract._capture import capture
from shopextract._models import Platform
from shopextract.categories import categorized_product_from_record,categorized_product_to_record
from shopextract.extractors.shopify_taxonomy import ShopifyStorefrontConfig,supplement_categories
from shopextract.extractors._storefront import stateless_cookies
from shopextract.taxonomies.shopify import load_shopify_taxonomy,normalize_with_shopify_taxonomy

OUT=Path('artifacts/shopify-taxonomy');STORE='https://www.boardgamebliss.com';HANDLE='eternal-decks-french-edition-minor-damage'
SOURCE=Path('/Users/umerkhan/code/shopextract/artifacts/category-mapping/live/shopify-companions.json')


def projection():
    rows=json.loads(SOURCE.read_text())
    original=next(categorized_product_from_record(r) for r in rows if r['product']['product']['product_url'].endswith('/'+HANDLE))
    evidence=original.product.evidence_contract.evidence
    fields={}
    for pointer in ('/id','/handle','/title'):
        item=next(e for e in evidence if e.retained_data.get('source_pointer')==pointer and e.method=='shopify_api')
        fields[pointer[1:]]=item.retained_data['value']
    assert fields['handle']==HANDLE and str(fields['id'])==original.product.external_id
    raw=capture(fields,item.source_url,item.method,observed_at=item.observed_at)
    record={'raw':raw,'retained_source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'retained_source':str(SOURCE),
        'original_acquired_at':item.observed_at.isoformat(),'note':'Projection of exact retained006source leaves; not a new008GET ID capture'}
    (OUT/'merchant-live-historical-projection.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    return raw,record


class RemainingWire(httpx.AsyncBaseTransport):
    def __init__(self):
        self.wire=httpx.AsyncHTTPTransport(retries=0)
        self.ledger=json.loads((OUT/'merchant-live-requests.json').read_text())
        assert len(self.ledger)==1 and self.ledger[0]['method']=='GET' and self.ledger[0]['status']==200
    def save(self):(OUT/'merchant-live-requests.json').write_text(json.dumps(self.ledger,indent=2)+'\n')
    async def handle_async_request(self,request):
        if len(self.ledger)!=1 or request.method!='POST' or str(request.url)!=STORE+'/api/2026-10/graphql.json':
            raise ValueError('combined_live_request_budget_or_route')
        row={'method':'POST','url':str(request.url),'phase':'reserved_before_wire'}
        self.ledger.append(row);self.save()
        response=await self.wire.handle_async_request(request);row.update(status=response.status_code,phase='response_headers');self.save()
        data=bytearray()
        try:
            async for chunk in response.aiter_bytes(chunk_size=65536):
                if len(data)+len(chunk)>1024*1024:raise ValueError('live_response_byte_cap')
                data.extend(chunk)
        finally:await response.aclose()
        (OUT/'merchant-live-post-response.bin').write_bytes(data)
        row.update(response_bytes=len(data),response_sha256=hashlib.sha256(data).hexdigest(),phase='response_retained');self.save()
        return httpx.Response(response.status_code,headers={k:v for k,v in response.headers.items() if k.lower() not in ('content-encoding','content-length')},content=bytes(data))
    async def aclose(self):await self.wire.aclose()


async def main():
    started=time.monotonic()
    # Exclusive lifetime marker; this file is never removed to restart a request.
    with (OUT/'remaining-post-attempt.json').open('x') as output:
        json.dump({'state':'reserved','limit_remaining_requests':1,'combined_limit':2},output);output.flush();__import__('os').fsync(output.fileno())
    raw,history=projection();wire=RemainingWire()
    result={'state':'blocked','historical_public_acquired_at':history['original_acquired_at'],'fresh_public_id_claim':False,
        'merchant_category_assignments_observed':0,'llm_calls':0,'browser_calls':0,'new_get_requests':0}
    try:
        catalog=load_shopify_taxonomy(catalog_root=Path('build/shopify-taxonomy/catalogs'))
        async with httpx.AsyncClient(transport=wire,timeout=10,trust_env=False,follow_redirects=False,cookies=stateless_cookies()) as client:
            await asyncio.wait_for(supplement_categories([raw],ShopifyStorefrontConfig(STORE+'/api/2026-10/graphql.json',auth_mode='tokenless'),client=client),10)
        value=normalize_with_shopify_taxonomy(raw,platform=Platform.SHOPIFY,shop_url=STORE,taxonomy=catalog,allow_unknown_source_version=True)
        if value is None:raise ValueError('normalization_unavailable')
        schema=catalog.schema_for(value)
        retained={'raw':raw,'companion':categorized_product_to_record(value),'historical_public_acquired_at':history['original_acquired_at']}
        encoded=json.dumps(retained,ensure_ascii=False).encode();assert len(encoded)<=1024*1024
        (OUT/'merchant-live-supplement-capture.json').write_bytes(encoded)
        facts=[f for o in value.observations if o.taxonomy_kind=='standard' for t in o.terms for f in t.facts if f.binding.facet=='native_id' and f.support.value=='observed' and f.outcome.accepted]
        result.update(state='passed' if schema.resolved else 'blocked',reason=None if schema.resolved else 'category_null_denied_or_unmapped',
            merchant_category_assignments_observed=len(facts),resolved_ids=[s.category.id for s in schema.resolved],raw_category=raw.get('category'),
            native_observed_at=next((f.evidence[0].observed_at.isoformat() for f in facts if f.evidence),None),
            category_states=[{'state':o.source_state,'completeness':o.completeness,'reason':o.reason} for o in value.observations if o.taxonomy_kind=='standard'])
    except (ValueError,httpx.HTTPError,asyncio.TimeoutError) as error:result['reason']=type(error).__name__+':'+str(error)[:160]
    finally:
        result.update(seconds=round(time.monotonic()-started,3),combined_http_ledger=wire.ledger,combined_requests_spent=len(wire.ledger),remaining_requests=2-len(wire.ledger))
        (OUT/'merchant-live-final-result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print(json.dumps(result,ensure_ascii=False))

if __name__=='__main__':asyncio.run(asyncio.wait_for(main(),30))
