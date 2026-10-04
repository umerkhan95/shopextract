"""Storefront protocol selection, bounded pagination, real pipeline and evidence fixtures."""
import gzip
import json
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from shopextract import extract, normalize, Platform, ExtractionTier
from shopextract._capture import capture
from shopextract._detect import detect
from shopextract._models import ExtractorResult
from shopextract.extractors._storefront import public_config, request, resolve_config
from shopextract.extractors.magento_graphql import MagentoGraphQLExtractor
from shopextract.extractors.shopware import ShopwareExtractor
from shopextract.extractors.bigcommerce import BigCommerceExtractor

SHOP='https://shop.test'


def magento_item(sku='p'):
    return {'sku':sku, 'name':'Product '+sku, 'url_key':sku, 'url_suffix':'.htm',
            'stock_status':'OUT_OF_STOCK', 'image':{'url':'https://image.test/p.jpg'},
            'description':{'html':'<p>Description</p>'},
            'price_range':{'minimum_price':{'final_price':{'value':0,'currency':'EUR'}}}}


def bigcommerce_item(id=1):
    return {'entityId':id,'name':'Product','sku':'p','path':'/p/',
            'prices':{'price':{'value':0,'currencyCode':'GBP'}},
            'inventory':{'isInStock':False},'defaultImage':{'urlOriginal':'https://image.test/p.jpg'},
            'variants':{'pageInfo':{'hasNextPage':False},'edges':[{'node':{'entityId':2,'sku':'v',
              'prices':{'price':{'value':0,'currencyCode':'GBP'}},'inventory':{'isInStock':False}}}]}}


def audit(p):
    p.evidence_contract.validate()
    view=p.trust_view()
    for k in ['/title','/price','/currency','/in_stock','/product_url']:
        assert view[k]['state']=='observed', (k,view[k])
    assert p.price==0 and p.in_stock is False
    return view


@pytest.mark.asyncio
async def test_magento_fixed_offset_pagination_and_configurable_variant_sources():
    requests=[]
    def respond(req):
        variables=json.loads(req.url.params['variables']);requests.append(variables)
        start=(variables['page']-1)*variables['size']
        items=[magento_item(str(i)) for i in range(start,min(start+variables['size'],3))]
        if start==0:
            items[0]['variants']=[{'product':magento_item('v'),'attributes':[{'code':'size','value_index':7}]}]
        return httpx.Response(200,json={'data':{'products':{'items':items,'total_count':3,
                 'page_info':{'current_page':variables['page'],'total_pages':2}}}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result=await MagentoGraphQLExtractor(page_size=2,http_client=client).extract(SHOP,max_products=3)
    assert result.complete and [p['sku'] for p in result.products]==['0','1','2']
    assert requests==[{'size':2,'page':1},{'size':2,'page':2}]
    p=normalize(result.products[0],Platform.MAGENTO,SHOP);v=audit(p)
    assert p.product_url==SHOP+'/0.htm'
    assert p.variants[0].attributes=={'size':'7'}
    assert v['/variants/0/price']['state']=='observed'
    obs=next(o for o in p.evidence_contract.observations if o.field_path=='/variants/0/price')
    e=next(e for e in p.evidence_contract.evidence if e.evidence_id in obs.evidence_ids)
    assert e.retained_data['source_pointer']=='/variants/0/product/price_range/minimum_price/final_price/value'


@pytest.mark.asyncio
async def test_graphql_error_does_not_accept_partial_data():
    def respond(req):return httpx.Response(200,json={'errors':[{'message':'secret-token'}],
       'data':{'products':{'items':[magento_item()], 'total_count':1}}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result=await MagentoGraphQLExtractor(http_client=client).extract(SHOP)
    assert not result.products and not result.complete and 'secret-token' not in result.error


@pytest.mark.asyncio
async def test_shopware_runtime_configuration_context_and_false_variant_stock():
    requests=[]
    def respond(req):
        requests.append(req)
        if req.url.path=='/':
            return httpx.Response(200,text='<script>window.__NUXT__.config={public:{shopware:{accessToken:"public-key",endpoint:"https://api.test/store-api/"}}}</script>')
        assert req.headers['sw-access-key']=='public-key'
        if req.url.path.endswith('/context'):
            return httpx.Response(200,json={'currency':{'isoCode':'EUR'}},headers={'sw-context-token':'session'})
        assert req.headers['sw-context-token']=='session'
        item={'id':'p','name':'Product','productNumber':'SW1','available':False,'stock':9,
              'calculatedPrice':{'unitPrice':0},'seoUrls':[{'seoPathInfo':'product'}],
              'children':[{'id':'v','name':'Variant','available':False,'stock':9,'calculatedPrice':{'unitPrice':0}}]}
        return httpx.Response(200,json={'elements':[item],'total':1})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result=await ShopwareExtractor(http_client=client).extract(SHOP)
    assert result.complete and len(requests)==3
    p=normalize(result.products[0],Platform.SHOPWARE,SHOP);v=audit(p)
    assert not p.variants[0].in_stock and v['/variants/0/in_stock']['state']=='observed'
    obs=next(o for o in p.evidence_contract.observations if o.field_path=='/currency')
    e=next(e for e in p.evidence_contract.evidence if e.evidence_id in obs.evidence_ids)
    assert e.source_url=='https://api.test/store-api/context'
    assert e.retained_data['source_pointer']=='/currency/isoCode'


@pytest.mark.asyncio
async def test_bigcommerce_token_cursor_and_nested_zero_false():
    cursors=[]
    def respond(req):
        if req.url.path=='/':return httpx.Response(200,text='<script>var jsContext={"storefrontAPIToken":"public-token"}</script>')
        assert req.headers['authorization']=='Bearer public-token'
        assert req.headers['origin']==SHOP
        cursor=json.loads(req.content)['variables']['after'];cursors.append(cursor)
        item=bigcommerce_item(1 if cursor is None else 3)
        return httpx.Response(200,json={'data':{'site':{'products':{'edges':[{'node':item}],
            'pageInfo':{'hasNextPage':cursor is None,'endCursor':'next'}}}}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result=await BigCommerceExtractor(page_size=1,http_client=client).extract(SHOP,max_products=2)
    assert result.complete and cursors==[None,'next']
    p=normalize(result.products[0],Platform.BIGCOMMERCE,SHOP);v=audit(p)
    assert v['/variants/0/price']['state']=='observed' and not p.variants[0].in_stock
    assert all('public-token' not in e.source_url for e in p.evidence_contract.evidence)


@pytest.mark.asyncio
async def test_repeated_bigcommerce_cursor_is_incomplete():
    count=0
    def respond(req):
        nonlocal count
        count+=1
        return httpx.Response(200,json={'data':{'site':{'products':{'edges':[{'node':bigcommerce_item(count)}],
                 'pageInfo':{'hasNextPage':True,'endCursor':'same'}}}}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result=await BigCommerceExtractor(http_client=client).extract(SHOP,endpoint=SHOP+'/graphql',access_token='token')
    assert not result.complete and result.error and len(result.products)==2 and count==2


@pytest.mark.parametrize('platform', ['shopware','bigcommerce'])
@pytest.mark.asyncio
async def test_missing_public_config_never_probes_admin_keys(platform):
    visited=[]
    def respond(req):visited.append(str(req.url));return httpx.Response(200,text='<script>{adminApiToken:"secret",accessToken:"admin"}</script>')
    cls=ShopwareExtractor if platform=='shopware' else BigCommerceExtractor
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result=await cls(http_client=client).extract(SHOP)
    assert not result.products and not result.complete
    assert visited==[SHOP]


@pytest.mark.asyncio
async def test_published_token_is_not_reused_for_an_unrelated_endpoint_override():
    def respond(req):return httpx.Response(200,text='<script>{storefrontApiToken:"public"}</script>')
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        endpoint,token=await resolve_config(client,SHOP,'bigcommerce',endpoint='https://other.test/graphql')
    assert endpoint=='https://other.test/graphql' and token is None


@pytest.mark.asyncio
async def test_transport_handles_compressed_body_without_double_decoding():
    def respond(req):return httpx.Response(200,content=gzip.compress(b'{"a":1}'),headers={'content-encoding':'gzip'})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        response=await request(client,'GET',SHOP)
    assert response.json()=={'a':1}


@pytest.mark.asyncio
async def test_keyed_api_redirect_cannot_replay_key_to_other_origin():
    visited=[]
    def respond(req):visited.append(str(req.url));return httpx.Response(307,headers={'location':'https://other.test/graphql'})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        with pytest.raises(ValueError,match='origin'):
            await request(client,'POST',SHOP,headers={'sw-access-key':'key'},json={})
    assert visited==[SHOP]


@pytest.mark.parametrize('platform', [Platform.SHOPIFY,Platform.WOOCOMMERCE,Platform.MAGENTO,Platform.SHOPWARE,Platform.BIGCOMMERCE])
def test_html_source_uses_generic_normalizer_even_when_platform_is_detected(platform):
    raw=capture({'@type':'Product','name':'Product','offers':{'price':'9','priceCurrency':'EUR'}},SHOP+'/p','json_ld')
    p=normalize(raw,platform,SHOP)
    assert p.price==9 and p.currency=='EUR' and p.trust_view()['/price']['state']=='observed'


@pytest.mark.asyncio
async def test_graphql_only_magento_detection():
    def respond(req):
        if req.url.path=='/graphql':return httpx.Response(200,json={'data':{'storeConfig':{'store_code':'default'}}})
        return httpx.Response(401)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result=await detect(SHOP,client=client)
    assert result.platform==Platform.MAGENTO and 'api:/graphql:storeConfig' in result.signals


@pytest.mark.parametrize('platform,cls', [(Platform.MAGENTO,MagentoGraphQLExtractor),
                                          (Platform.SHOPWARE,ShopwareExtractor),
                                          (Platform.BIGCOMMERCE,BigCommerceExtractor)])
@pytest.mark.asyncio
async def test_public_extract_dispatches_native_adapter_with_budget(platform,cls):
    raw=magento_item() if platform==Platform.MAGENTO else bigcommerce_item() if platform==Platform.BIGCOMMERCE else {
        'name':'Product','id':'p','calculatedPrice':{'unitPrice':0},'available':False,'currency':'EUR'}
    capture(raw,SHOP+'/api','api')
    with patch.object(cls,'extract',AsyncMock(return_value=ExtractorResult(products=[raw],complete=True))) as api:
        result=await extract(SHOP,platform=platform,max_urls=2,api_options={'endpoint':SHOP+'/api','access_token':'key'})
    assert result.tier==ExtractionTier.API and len(result.products)==1
    assert api.call_args.kwargs['max_products']==2
    assert api.call_args.kwargs['endpoint']==SHOP+'/api'
    assert result.catalog_complete is None


@pytest.mark.asyncio
async def test_unavailable_api_falls_through_public_pipeline_with_inspectable_reason():
    from shopextract.extractors.unified import UnifiedCrawlExtractor
    raw=capture({'@type':'Product','name':'Product','offers':{'price':'9','priceCurrency':'GBP'}},SHOP+'/p','json_ld')
    with patch.object(BigCommerceExtractor,'extract',AsyncMock(return_value=ExtractorResult(complete=False,error='Public storefront token unavailable'))), \
         patch('shopextract._discover.discover',AsyncMock(return_value=[SHOP+'/p'])), \
         patch.object(UnifiedCrawlExtractor,'extract',AsyncMock(return_value=ExtractorResult(products=[raw]))):
        result=await extract(SHOP,platform=Platform.BIGCOMMERCE,max_urls=1)
    assert result.tier==ExtractionTier.UNIFIED_CRAWL and result.products[0].price==9
    assert result.errors==['Public storefront token unavailable']
    assert result.products[0].trust_view()['/price']['state']=='observed'


@pytest.mark.asyncio
async def test_empty_known_graphql_catalog_does_not_trigger_crawling():
    with patch.object(MagentoGraphQLExtractor,'extract',AsyncMock(return_value=ExtractorResult(products=[],complete=True))), \
         patch('shopextract._discover.discover',AsyncMock()) as discovery:
        result=await extract(SHOP,platform=Platform.MAGENTO,max_urls=1)
    assert result.tier==ExtractionTier.API and not result.products
    discovery.assert_not_called()


@pytest.mark.asyncio
async def test_explicit_legacy_rest_mode_preserves_endpoint_and_authentication():
    from shopextract.extractors.magento import MagentoExtractor
    raw=capture({'name':'Product','sku':'p','price':1},SHOP+'/products','magento_api')
    with patch.object(MagentoExtractor,'extract',AsyncMock(return_value=ExtractorResult(products=[raw]))) as api:
        result=await extract(SHOP,platform=Platform.MAGENTO,max_urls=2,
                             api_options={'protocol':'rest','endpoint':SHOP+'/products','access_token':'key'})
    assert result.tier==ExtractionTier.API
    assert api.call_args.kwargs=={'max_products':2,'endpoint':SHOP+'/products','access_token':'key'}


@pytest.mark.asyncio
async def test_incomplete_variant_connection_cannot_report_complete_catalog():
    def respond(req):
        item=bigcommerce_item();item['variants']['pageInfo']['hasNextPage']=True
        return httpx.Response(200,json={'data':{'site':{'products':{'edges':[{'node':item}],
                         'pageInfo':{'hasNextPage':False,'endCursor':None}}}}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result=await BigCommerceExtractor(http_client=client).extract(SHOP,endpoint=SHOP+'/graphql',access_token='key')
    assert not result.complete and result.completeness_reason=='variant_budget_reached'


@pytest.mark.asyncio
async def test_anonymous_page_redirect_retains_final_response_url():
    def respond(req):
        if req.url.host=='shop.test':return httpx.Response(302,headers={'location':'https://canonical.test/'})
        return httpx.Response(200,text='Public page')
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        response=await request(client,'GET',SHOP)
    assert str(response.url)=='https://canonical.test/' and response.text=='Public page'


@pytest.mark.asyncio
async def test_bigcommerce_missing_token_uses_bounded_native_card_discovery():
    from shopextract._discover import discover
    def respond(req):
        return httpx.Response(200,text='<a href="/category/">Browse</a>'
           '<h3 class="card-title"><a href="/all/a/">A</a></h3>'
           '<h3 class="card-title"><a href="https://evil.test/p">Outside</a></h3>'
           '<h3 class="card-title"><a href="/all/b/">B</a></h3>')
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        with patch('shopextract._discover._discover_via_crawl4ai',AsyncMock()) as browser:
            urls=await discover(SHOP,platform=Platform.BIGCOMMERCE,max_urls=1,client=client)
    assert urls==[SHOP+'/all/a/']
    browser.assert_not_called()


@pytest.mark.parametrize('cls', [ShopwareExtractor,BigCommerceExtractor,MagentoGraphQLExtractor])
@pytest.mark.parametrize('limit', [0,-1,True])
@pytest.mark.asyncio
async def test_invalid_direct_adapter_budget_fails_before_any_requests(cls,limit):
    with pytest.raises(ValueError):await cls().extract(SHOP,max_products=limit)


@pytest.mark.asyncio
async def test_bigcommerce_published_token_uses_canonical_storefront_origin_after_redirect():
    def respond(req):
        if req.url.host=='shop.test':return httpx.Response(302,headers={'location':'https://canonical.test/'})
        if req.url.path=='/':return httpx.Response(200,text='<script>{storefrontApiToken:"published"}</script>')
        assert req.headers['origin']=='https://canonical.test'
        return httpx.Response(200,json={'data':{'site':{'products':{'edges':[{'node':bigcommerce_item()}],
                       'pageInfo':{'hasNextPage':False,'endCursor':None}}}}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result=await BigCommerceExtractor(http_client=client).extract(SHOP,max_products=1)
    assert result.complete and result.products[0]['_capture']['url']=='https://canonical.test/graphql'


@pytest.mark.parametrize('reported_total', [5, None])
@pytest.mark.asyncio
async def test_last_graphql_page_clipped_by_budget_cannot_report_complete(reported_total):
    def respond(req):
        v=json.loads(req.url.params['variables'])
        start=(v['page']-1)*v['size']
        items=[magento_item(str(i)) for i in range(start,min(start+v['size'],5))]
        return httpx.Response(200,json={'data':{'products':{'items':items,'total_count':reported_total,
                           'page_info':{'current_page':v['page'],'total_pages':2}}}})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result=await MagentoGraphQLExtractor(page_size=3,http_client=client).extract(SHOP,max_products=4)
    assert len(result.products)==4
    assert result.complete is False and result.completeness_reason=='product_or_page_budget_reached'
