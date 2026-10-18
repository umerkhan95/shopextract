"""Real public dispatch and guarded domain worker integration."""
import asyncio,json,time
from datetime import datetime,timezone
import httpx,pytest
from tests.test_shopify_taxonomy_pipeline import catalog
from tests.test_shopify_taxonomy_storefront import STORE,public
from shopextract._models import Platform
from shopextract.taxonomies.shopify import shopify_taxonomy_options,extract_with_shopify_taxonomy
from shopextract.categories.contracts import CategoryScope,CategoryRuntimeConfig
from shopextract.categories import categorized_product_from_record
from shopextract.tools.runtime import ToolConfig,ToolRuntime,Limits
from shopextract.tools.context import OperationContext,OperationBudget
from shopextract.tools.security import GuardedTransport,NativeReadPolicy
from shopextract.tools.contracts import ToolError
from shopextract.extractors.shopify_taxonomy import ShopifyStorefrontConfig,SHOPIFY_TAXONOMY_QUERY

async def resolver(host,context):return ['93.184.216.34']

def wire(sent):
 def handle(request):
    sent.append(request)
    if request.method=='POST':return httpx.Response(200,json={'data':{'product':{'id':'gid://shopify/Product/101','title':'Laptop','handle':'laptop','category':{'id':'gid://shopify/TaxonomyCategory/el-6-6','name':'Laptops'}}}})
    if request.url.path.endswith('/products.json'):return httpx.Response(200,json={'products':[public()]})
    return httpx.Response(200,text='<script src="https://cdn.shopify.com/a.js"></script>',headers={'x-shopify-stage':'production'})
 return handle

async def test_public_real_dispatch(catalog,monkeypatch):
    sent=[]
    original=httpx.AsyncClient
    monkeypatch.setattr(httpx,"AsyncClient",lambda **kw:original(transport=httpx.MockTransport(wire(sent)),**kw))
    value=await extract_with_shopify_taxonomy(STORE,taxonomy=catalog,allow_unknown_source_version=True,
        storefront=ShopifyStorefrontConfig(STORE+'/api/2026-10/graphql.json',auth_mode='tokenless'))
    assert len(value.products)==1 and catalog.schema_for(value.products[0]).resolved
    assert value.products[0].product.variants[0].sku=='SKU-1'
    assert sum(r.method=='POST' for r in sent)==1

async def test_tool_guard_worker_real_dispatch(catalog):
    sent=[]
    options=shopify_taxonomy_options(CategoryScope(Platform.SHOPIFY,STORE),category_ids=['el-6-6'],taxonomy=catalog,allow_unknown_source_version=True)
    runtime=ToolRuntime(ToolConfig(allowed_origins=(STORE,)),resolver=resolver,wire_transport=httpx.MockTransport(wire(sent)),
        category_config=CategoryRuntimeConfig(options),shopify_storefront=ShopifyStorefrontConfig(STORE+'/api/2026-10/graphql.json',auth_mode='tokenless'))
    try:
        context=OperationContext('taxonomy-test',time.monotonic()+15,asyncio.Event(),OperationBudget(Limits()),runtime.auxiliary,datetime.now(timezone.utc))
        result=await runtime.sources.execute('extract',STORE,2,context)
        value=categorized_product_from_record(result['products'][0])
        assert catalog.schema_for(value).resolved
        assert any(r.method=='POST' for r in sent)
    finally:await runtime.aclose()

@pytest.mark.parametrize('fault',['disabled','endpoint','query','variables'])
async def test_guard_rejects_wrong_contract_before_wire(catalog,fault):
    sent=[];config=ToolConfig(allowed_origins=(STORE,));runtime=ToolRuntime(config,resolver=resolver)
    context=OperationContext('guard',time.monotonic()+10,asyncio.Event(),OperationBudget(Limits()),runtime.auxiliary,datetime.now(timezone.utc))
    endpoint=STORE+'/api/2026-10/graphql.json'
    policy=NativeReadPolicy(category_mode=fault!='disabled',shopify_endpoint=endpoint if fault!='endpoint' else STORE+'/different')
    transport=GuardedTransport(config,context,runtime.guard,httpx.MockTransport(wire(sent)),policy=policy)
    body={'query':SHOPIFY_TAXONOMY_QUERY,'variables':{'handle':'laptop'}}
    if fault=='query':body['query']+=' mutation { bad }'
    if fault=='variables':body['variables']['extra']='x'
    try:
        async with httpx.AsyncClient(transport=transport) as client:
            with pytest.raises(ToolError):await client.post(endpoint,json=body)
        assert not sent
    finally:await runtime.aclose()

@pytest.mark.parametrize('method,suffix',[('GET',''),('HEAD',''),('GET','?query=wrong'),('HEAD','?query=wrong')])
async def test_configured_endpoint_wrong_methods_denied_before_wire(method,suffix):
    sent=[];config=ToolConfig(allowed_origins=(STORE,));runtime=ToolRuntime(config,resolver=resolver)
    endpoint=STORE+'/api/2026-10/graphql.json'
    context=OperationContext('guard',time.monotonic()+10,asyncio.Event(),OperationBudget(Limits()),runtime.auxiliary,datetime.now(timezone.utc))
    transport=GuardedTransport(config,context,runtime.guard,httpx.MockTransport(wire(sent)),policy=NativeReadPolicy(category_mode=True,shopify_endpoint=endpoint))
    try:
        async with httpx.AsyncClient(transport=transport) as client:
            with pytest.raises(ToolError):await client.request(method,endpoint+suffix)
        assert not sent
    finally:await runtime.aclose()

async def test_extract_preserves_configured_merchant_basepath(catalog,monkeypatch):
    sent=[];original=httpx.AsyncClient
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(wire(sent)),**kw))
    values=[]
    for path in ('/a','/b'):
        result=await extract_with_shopify_taxonomy(STORE+path,taxonomy=catalog,allow_unknown_source_version=True,
            storefront=ShopifyStorefrontConfig(STORE+'/api/2026-10/graphql.json',auth_mode='tokenless'))
        value=result.products[0];values.append(value)
        assert value.scope.store_url==STORE+path
        assert value.product.product_url==STORE+path+'/products/laptop'
    assert values[0].scope!=values[1].scope
    assert next(o for o in values[0].observations if o.taxonomy_kind=='standard').terms[0].ref==next(o for o in values[1].observations if o.taxonomy_kind=='standard').terms[0].ref

@pytest.mark.parametrize('mode',['tokenless','token'])
async def test_cookie_bearing_public_pages_use_clean_same_guard_client(catalog,mode):
    sent=[];base=wire(sent)
    def response(request):
        if request.method=='POST':
            assert 'cookie' not in request.headers and 'authorization' not in request.headers
            assert request.headers.get('x-shopify-storefront-access-token')==('fixture-token' if mode=='token' else None)
        result=base(request);result.headers['set-cookie']='session=fixture; Path=/'
        return result
    options=shopify_taxonomy_options(CategoryScope(Platform.SHOPIFY,STORE),category_ids=['el-6-6'],taxonomy=catalog,allow_unknown_source_version=True)
    config=ShopifyStorefrontConfig(STORE+'/api/2026-10/graphql.json','fixture-token' if mode=='token' else None,auth_mode=mode)
    runtime=ToolRuntime(ToolConfig(allowed_origins=(STORE,)),resolver=resolver,wire_transport=httpx.MockTransport(response),category_config=CategoryRuntimeConfig(options),shopify_storefront=config)
    try:
        context=OperationContext('cookie-test',time.monotonic()+15,asyncio.Event(),OperationBudget(Limits()),runtime.auxiliary,datetime.now(timezone.utc))
        result=await runtime.sources.execute('extract',STORE,2,context)
        assert catalog.schema_for(categorized_product_from_record(result['products'][0])).resolved
        assert [r.method for r in sent]==['GET','GET','POST'] and context.budget.requests_used==3
    finally:await runtime.aclose()
