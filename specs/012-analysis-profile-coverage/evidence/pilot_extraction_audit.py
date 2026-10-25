"""APC07 synthetic source-path audit; only HTTP transport is controlled."""
import argparse,asyncio,json,tempfile,time
from datetime import datetime,timedelta,timezone
from pathlib import Path
import httpx
from shopextract._capture import capture
from shopextract._evidence import trust_view
from shopextract._models import Platform
from shopextract._normalize import normalize
from shopextract._portable import product_to_record,product_from_record
from shopextract.maintenance import Goal,MaintenanceStore,MaintenanceEngine
from shopextract.tools import ToolConfig
from shopextract.extractors._schema_org import SchemaOrgExtractor

ROOT=Path(__file__).resolve().parent
URL='https://synthetic-audit.invalid'
FIELDS=('capacity','width','height','depth','model')


def inspect(raw,platform):
    product=normalize(raw,platform,URL);assert product is not None
    record=product_to_record(product);restored=product_from_record(json.loads(json.dumps(record)))
    assert product_to_record(restored)==record
    now=datetime.now(timezone.utc)
    with tempfile.TemporaryDirectory(prefix='profile-audit-') as temp:
        path=Path(temp)/'jobs.db';store=MaintenanceStore(path)
        job=store.create(Goal(baseline=(record,),supplier_origin=URL,product_urls=(URL+'/product',),baseline_mode='captured',fields=('title',),profiles={product.external_id:'generic-v1'},deadline=(now+timedelta(minutes=2)).isoformat()))
        store.acquire();assert store.begin(job,now=now);store.add_steps(job,[('audit','audit')]);store.checkpoint(job,'audit',record);store.finish(job,'completed');store.close()
        store=MaintenanceStore(path);again=product_from_record(store.steps(job)[0]['result'])
        engine=MaintenanceEngine(store,tool_config=ToolConfig(),utc_now=lambda:now)
        support={field:engine._supported(again,'attributes/'+field,{'freshness_seconds':3600})[1]['state'] for field in FIELDS}
        title=engine._supported(again,'title',{'freshness_seconds':3600})[1]['state']
        store.close()
    assert title=='observed'
    return {'platform':platform.value,'provenance':'synthetic-controlled-offline','method':raw['_capture']['method'],'source_quantity_pointers':[key for key in raw['_capture']['values'] if any(token in key.lower() for token in ('capacity','width','height','depth','additionalproperty','model'))][:24],'attributes':restored.attributes,'field_support':support,'title_support':title,'portable_roundtrip':True,'sqlite_checkpoint_reopen':True}


def smoke():
    payload={'@context':'https://schema.org','@type':'Product','name':'Synthetic refrigerator','sku':'FX1','model':'FX-250','offers':{'price':'250','priceCurrency':'EUR'},'additionalProperty':[{'@type':'PropertyValue','name':'Total capacity','value':'250 L'},{'@type':'PropertyValue','name':'Product width','value':'60 cm'}]}
    html='<script type="application/ld+json">'+json.dumps(payload)+'</script>'
    raw=SchemaOrgExtractor.extract_from_html(html,URL+'/product')[0]
    result=inspect(raw,Platform.GENERIC)
    assert result['attributes']=={} and set(result['field_support'].values())=={'unsupported'}
    result['retained_total_capacity']=raw['additionalProperty'][0]['value'];result['retained_model']=raw['model']
    (ROOT/'pilot-audit-smoke.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Generic source smoke saved: retained properties, unsupported normalized fields',flush=True)
    return result


async def native(*, retain_raw=False):
    from shopextract.extractors.shopify import ShopifyExtractor
    from shopextract.extractors.woocommerce import WooCommerceExtractor
    from shopextract.extractors.magento_graphql import MagentoGraphQLExtractor
    from shopextract.extractors.shopware import ShopwareExtractor
    from shopextract.extractors.bigcommerce import BigCommerceExtractor
    cases=[
      (Platform.SHOPIFY,ShopifyExtractor,{'id':1,'title':'Synthetic refrigerator','handle':'fx1','variants':[{'id':1,'sku':'FX1','price':'250','available':True}]},{}),
      (Platform.WOOCOMMERCE,WooCommerceExtractor,{'id':1,'name':'Synthetic refrigerator','sku':'FX1','prices':{'price':'25000','currency_code':'EUR','currency_minor_unit':2},'attributes':[{'name':'Total capacity','terms':[{'name':'250 L'}]}]},{}),
      (Platform.MAGENTO,MagentoGraphQLExtractor,{'sku':'FX1','name':'Synthetic refrigerator','url_key':'fx1','stock_status':'IN_STOCK','price_range':{'minimum_price':{'final_price':{'value':250,'currency':'EUR'}}},'custom_attributes':[{'attribute_code':'total_capacity','value':'250 L'}]}, {'endpoint':URL+'/graphql','access_token':'synthetic'}),
      (Platform.SHOPWARE,ShopwareExtractor,{'id':'f'*32,'name':'Synthetic refrigerator','productNumber':'FX1','calculatedPrice':{'unitPrice':250},'width':600,'height':1800,'length':650,'customFields':{'total_capacity':'250 L'}},{'endpoint':URL+'/store-api','access_token':'synthetic'}),
      (Platform.BIGCOMMERCE,BigCommerceExtractor,{'entityId':1,'name':'Synthetic refrigerator','sku':'FX1','path':'/fx1','prices':{'price':{'value':250,'currencyCode':'EUR'}},'variants':{'pageInfo':{'hasNextPage':False},'edges':[]}}, {'endpoint':URL+'/graphql','access_token':'synthetic'}),
    ]
    results=[];requests=[]
    for platform,cls,item,options in cases:
        def transport(request):
            requests.append({'platform':platform.value,'method':request.method,'path':request.url.path})
            assert len(requests)<=10
            if platform==Platform.SHOPIFY:body={'products':[item]}
            elif platform==Platform.WOOCOMMERCE:return httpx.Response(200,json=[item],headers={'x-wp-totalpages':'1'})
            elif platform==Platform.MAGENTO:body={'data':{'products':{'items':[item],'total_count':1,'page_info':{'current_page':1,'total_pages':1}}}}
            elif platform==Platform.BIGCOMMERCE:body={'data':{'site':{'products':{'edges':[{'node':item}],'pageInfo':{'hasNextPage':False,'endCursor':None}}}}}
            else:body={'currency':{'isoCode':'EUR'}} if request.url.path.endswith('/context') else {'elements':[item],'total':1}
            return httpx.Response(200,json=body)
        async with httpx.AsyncClient(transport=httpx.MockTransport(transport)) as client:
            extractor=cls(http_client=client,max_pages=1)
            result=await extractor.extract(URL,**options,**({} if platform==Platform.WOOCOMMERCE else {'max_products':1}))
        assert len(result.products)==1,(platform,result.error)
        row=inspect(result.products[0],platform);assert set(row['field_support'].values())=={'unsupported'}
        row['extractor_complete']=result.complete
        if retain_raw:row['_raw']=result.products[0]
        results.append(row)
    return results,requests


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--all',action='store_true');args=parser.parse_args();start=time.monotonic()
    if args.all:
        assert (ROOT/'pilot-audit-smoke.json').is_file(),'Save smoke first'
        native_rows,requests=asyncio.run(asyncio.wait_for(native(),timeout=60))
        data={'provenance':'synthetic-controlled-offline','rows':[json.loads((ROOT/'pilot-audit-smoke.json').read_text()),*native_rows],'controlled_requests':requests,'real_network_requests':0,'model_calls':0,'elapsed_seconds':round(time.monotonic()-start,3)}
        (ROOT/'pilot-audit-six-lanes.json').write_text(json.dumps(data,indent=2)+'\n');print(json.dumps({'lanes':len(data['rows']),'controlled_requests':len(requests),'elapsed_seconds':data['elapsed_seconds']}))
    else:smoke()


if __name__=='__main__':main()
