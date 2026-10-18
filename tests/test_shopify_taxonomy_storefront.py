"""Supplement category without discarding public observations or relaxing the guard."""
import asyncio,json,time
from datetime import datetime,timezone
import httpx,pytest
from shopextract._capture import capture
from shopextract._models import Platform
from shopextract.categories import normalize_with_categories
from shopextract.categories.contracts import CategoryScope
from tests.test_shopify_taxonomy_pipeline import catalog
from shopextract.taxonomies.shopify import shopify_taxonomy_options

STORE='https://merchant.test'

def public():
    return capture({'id':101,'title':'Laptop','handle':'laptop','variants':[{'id':201,'price':'20','sku':'SKU-1'}]},STORE+'/products.json','shopify_api')

async def test_supplement_preserves_variants_and_actual_category_source(catalog):
    from shopextract.extractors.shopify_taxonomy import ShopifyStorefrontConfig,supplement_categories,SHOPIFY_TAXONOMY_QUERY
    sent=[]
    def wire(request):
        sent.append(request)
        return httpx.Response(200,json={'data':{'product':{'id':'gid://shopify/Product/101','handle':'laptop',
            'category':{'id':'gid://shopify/TaxonomyCategory/el-6-6','name':'Laptops'}}}})
    raw=public()
    async with httpx.AsyncClient(transport=httpx.MockTransport(wire)) as client:
        await supplement_categories([raw],ShopifyStorefrontConfig(STORE+'/api/2026-10/graphql.json',auth_mode='tokenless'),client=client)
    assert raw['variants'][0]['sku']=='SKU-1' and raw['_capture']['method']=='shopify_api'
    assert len(sent)==1 and json.loads(sent[0].content)['query']==SHOPIFY_TAXONOMY_QUERY
    assert 'x-shopify-storefront-access-token' not in sent[0].headers
    options=shopify_taxonomy_options(CategoryScope(Platform.SHOPIFY,STORE),category_ids=['el-6-6'],taxonomy=catalog,allow_unknown_source_version=True)
    value=normalize_with_categories(raw,Platform.SHOPIFY,STORE,category_options=options)
    assert any(m.status=='mapped' for m in value.mappings)
    facts=next(o for o in value.observations if o.taxonomy_kind=='standard').terms[0].facts
    assert facts[0].evidence[0].source_url==STORE+'/api/2026-10/graphql.json'

@pytest.mark.parametrize('mode,token',[('token',None),('tokenless','bad'),('other',None)])
def test_auth_modes_fail_closed(mode,token):
    from shopextract.extractors.shopify_taxonomy import ShopifyStorefrontConfig
    with pytest.raises(ValueError):ShopifyStorefrontConfig(STORE+'/api/2026-10/graphql.json',token,auth_mode=mode)

@pytest.mark.parametrize('fault',['mismatch','null','denied','failed_id'])
async def test_failed_supplement_cannot_map(catalog,fault):
    from shopextract.extractors.shopify_taxonomy import ShopifyStorefrontConfig,supplement_categories
    node={'id':'gid://shopify/Product/101','handle':'laptop','category':{'id':'gid://shopify/TaxonomyCategory/el-6-6','name':'Laptops'}}
    body={'data':{'product':node}};status=200
    if fault=='mismatch':node['id']='gid://shopify/Product/999'
    if fault=='null':body['data']['product']=None
    if fault=='denied':status=403
    if fault=='failed_id':body['errors']=[{'path':['product','category','id']}]
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r:httpx.Response(status,json=body))) as client:
        raw=public();await supplement_categories([raw],ShopifyStorefrontConfig(STORE+'/api/2026-10/graphql.json',auth_mode='tokenless'),client=client)
    options=shopify_taxonomy_options(CategoryScope(Platform.SHOPIFY,STORE),category_ids=['el-6-6'],taxonomy=catalog,allow_unknown_source_version=True)
    value=normalize_with_categories(raw,Platform.SHOPIFY,STORE,category_options=options)
    assert not any(m.status=='mapped' for m in value.mappings)
    assert raw['variants'][0]['price']=='20'

@pytest.mark.parametrize('path',[None,['product'],['product','id'],['product','handle']])
async def test_join_errors_do_not_taint_independent_public_facts(catalog,path):
    from shopextract.extractors.shopify_taxonomy import ShopifyStorefrontConfig,supplement_categories
    from shopextract._evidence import SupportState
    body={'data':{'product':{'id':'gid://shopify/Product/101','handle':'laptop','category':{'id':'gid://shopify/TaxonomyCategory/el-6-6','name':'Laptops'}}},'errors':[{'path':path}]}
    raw=public();raw['product_type']='Independent merchant type'
    raw['collections']={'edges':[{'node':{'id':'gid://shopify/Collection/7','title':'Independent collection'}}],'pageInfo':{'hasNextPage':False}}
    capture(raw,STORE+'/products.json','shopify_api')
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r:httpx.Response(200,json=body))) as client:
        await supplement_categories([raw],ShopifyStorefrontConfig(STORE+'/api/2026-10/graphql.json',auth_mode='tokenless'),client=client)
    options=shopify_taxonomy_options(CategoryScope(Platform.SHOPIFY,STORE),category_ids=['el-6-6'],taxonomy=catalog,allow_unknown_source_version=True)
    value=normalize_with_categories(raw,Platform.SHOPIFY,STORE,category_options=options)
    custom=next(o for o in value.observations if o.taxonomy_kind=='custom_type')
    assert custom.terms[0].facts[0].support==SupportState.OBSERVED
    collection=next(o for o in value.observations if o.taxonomy_kind=='merchandising')
    assert collection.terms[0].facts[0].support==SupportState.OBSERVED
    assert not any(m.status=='mapped' for m in value.mappings)

async def test_owned_supplement_drops_response_cookies_between_products(monkeypatch):
    from shopextract.extractors.shopify_taxonomy import ShopifyStorefrontConfig,supplement_categories
    sent=[]
    def wire(request):
        sent.append(request);assert 'cookie' not in request.headers
        return httpx.Response(200,headers={'set-cookie':'native=fixture; Path=/'},json={'data':{'product':{'id':'gid://shopify/Product/101','handle':'laptop','category':None}}})
    original=httpx.AsyncClient
    monkeypatch.setattr(httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(wire),**kw))
    await supplement_categories([public(),public()],ShopifyStorefrontConfig(STORE+'/api/2026-10/graphql.json',auth_mode='tokenless'))
    assert len(sent)==2

async def test_explicit_inherited_cookie_is_still_rejected():
    from shopextract.extractors.shopify_taxonomy import ShopifyStorefrontConfig,supplement_categories
    async with httpx.AsyncClient(cookies={'session':'fixture'},transport=httpx.MockTransport(lambda r:pytest.fail('no wire'))) as client:
        with pytest.raises(ValueError,match='inherited'):
            await supplement_categories([public()],ShopifyStorefrontConfig(STORE+'/api/2026-10/graphql.json',auth_mode='tokenless'),client=client)
