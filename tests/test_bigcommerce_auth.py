"""Docs-based request authentication and an executable catalog schema mock.

Synthetic rejection bodies exercise documented response envelopes, not JWT crypto
or a promise that each BigCommerce installation uses an identical status/message.
"""
import json
from pathlib import Path
from unittest.mock import patch

from graphql import build_schema, graphql_sync, parse, validate
import httpx
import pytest

from shopextract import Platform, extract, normalize
from shopextract._capture import capture
from shopextract.extractors.bigcommerce import BigCommerceExtractor, _QUERY

SHOP = 'https://shop.test'
SCHEMA = build_schema((Path(__file__).parent/'fixtures/bigcommerce/catalog.graphql').read_text())


def product(id=1):
    return {'entityId':id, 'name':'Catalog product', 'sku':f'p{id}', 'path':f'/p{id}/',
            'description':'Description', 'upc':None, 'defaultImage':{'urlOriginal':SHOP+'/p.jpg'},
            'brand':None, 'prices':{'price':{'value':0,'currencyCode':'EUR'}},
            'inventory':{'isInStock':False},
            'variants':{'pageInfo':{'hasNextPage':False,'endCursor':None},'edges':[
                {'node':{'entityId':10+id,'sku':'v','upc':None,'prices':None,'inventory':None}}]}}


class StorefrontMock:
    """Validate headers and execute the real adapter query; no fixed success JSON."""
    def __init__(self, token_type, customer=None, customer_id=None, rejection=None):
        self.token_type=token_type;self.customer=customer;self.customer_id=customer_id
        self.rejection=rejection;self.calls=[]

    def __call__(self, req):
        self.calls.append(req)
        assert req.method=='POST' and str(req.url)==SHOP+'/graphql'
        assert req.headers['authorization']=='Bearer credential'
        assert req.headers['accept']=='application/json'
        assert req.headers['content-type'].startswith('application/json')
        assert not req.headers.get('x-auth-token')
        if self.token_type=='storefront':assert req.headers['origin']==SHOP
        else:assert 'origin' not in req.headers
        if self.customer:
            assert req.headers['x-bc-customer-access-token']==self.customer
            assert req.headers['x-bc-error-on-invalid-customer-access-token']=='true'
        else:assert 'x-bc-customer-access-token' not in req.headers
        if self.customer_id:assert req.headers['x-bc-customer-id']==self.customer_id
        else:assert 'x-bc-customer-id' not in req.headers
        body=json.loads(req.content)
        assert body['query']==_QUERY
        assert body['variables']['size']>0
        if self.rejection:
            status,message=self.rejection
            return httpx.Response(status,json={'errors':[{'message':message}]})
        offset=0 if body['variables']['after'] is None else int(body['variables']['after'])
        items=[product(i) for i in range(1,4)][offset:offset+body['variables']['size']]
        end=offset+len(items)
        root={'site':{'products':{'edges':[{'node':p} for p in items],
              'pageInfo':{'hasNextPage':end<3,'endCursor':str(end)}}}}
        result=graphql_sync(SCHEMA,body['query'],root_value=root,variable_values=body['variables'])
        assert not result.errors,result.errors
        return httpx.Response(200,json={'data':result.data})


@pytest.mark.parametrize('mode,customer,customer_id',[
    ('storefront',None,None),('private',None,None),('private','customer-secret',None),
    ('impersonation',None,'42')])
@pytest.mark.asyncio
async def test_documented_auth_modes_execute_actual_query_and_paginate(mode,customer,customer_id):
    server=StorefrontMock(mode,customer,customer_id)
    async with httpx.AsyncClient(transport=httpx.MockTransport(server)) as client:
        result=await BigCommerceExtractor(page_size=2,http_client=client).extract(
            SHOP,endpoint=SHOP+'/graphql',access_token='credential',token_type=mode,
            customer_access_token=customer,customer_id=customer_id,max_products=3)
    assert result.complete and not result.error and len(result.products)==3
    assert len(server.calls)==2
    for raw in result.products:
        p=normalize(raw,Platform.BIGCOMMERCE,SHOP)
        p.evidence_contract.validate()
        assert p.price==0 and p.in_stock is False
        view=p.trust_view()
        assert view['/variants/0/price']['state']=='unsupported'
        assert view['/variants/0/in_stock']['state']=='unsupported'
        encoded=json.dumps(p.evidence_contract.to_dict(),default=str)
        assert 'credential' not in encoded and 'customer-secret' not in encoded


@pytest.mark.parametrize('mode', ['storefront','private','impersonation'])
@pytest.mark.parametrize('status,message',[(401,'expired credential'),(401,'revoked credential'),
    (403,'origin denied credential'),(403,'channel denied credential'),
    (200,'unauthorized credential'),(429,'rate limit credential'),(500,'server credential')])
@pytest.mark.asyncio
async def test_rejections_are_incomplete_redacted_and_do_not_retry(mode,status,message):
    cid='42' if mode=='impersonation' else None
    server=StorefrontMock(mode,customer_id=cid,rejection=(status,message))
    async with httpx.AsyncClient(transport=httpx.MockTransport(server)) as client:
        result=await BigCommerceExtractor(http_client=client).extract(
            SHOP,endpoint=SHOP+'/graphql',access_token='credential',token_type=mode,customer_id=cid)
    assert not result.products and not result.complete and result.error
    assert result.completeness_reason=='source_error' and len(server.calls)==1
    assert 'credential' not in result.error
    if status!=200:assert f'HTTP {status}' in result.error


@pytest.mark.parametrize('options',[
    {'token_type':'unknown'}, {'token_type':'private'}, {'token_type':'impersonation'},
    {'access_token':''}, {'access_token':'bad\nvalue'},
    {'customer_access_token':'customer-secret'},
    {'token_type':'private','access_token':'credential','customer_id':'42'},
    {'token_type':'impersonation','access_token':'credential'},
    {'token_type':'impersonation','access_token':'credential','customer_id':'0'},
    {'token_type':'impersonation','access_token':'credential','customer_id':'abc'},
    {'token_type':'impersonation','access_token':'credential','customer_id':'42','customer_access_token':'secret'},
])
@pytest.mark.asyncio
async def test_invalid_config_is_rejected_before_network(options):
    def network(req):raise AssertionError('Invalid config must not make network calls')
    async with httpx.AsyncClient(transport=httpx.MockTransport(network)) as client:
        with pytest.raises(ValueError):
            await BigCommerceExtractor(http_client=client).extract(SHOP,**options)


@pytest.mark.asyncio
async def test_private_token_infers_graphql_endpoint_without_public_html_discovery():
    server=StorefrontMock('private')
    async with httpx.AsyncClient(transport=httpx.MockTransport(server)) as client:
        result=await BigCommerceExtractor(http_client=client).extract(SHOP,token_type='private',access_token='credential')
    assert result.complete and len(server.calls)==1


@pytest.mark.parametrize('credential_header', ['Authorization','X-Bc-Customer-Access-Token','X-Bc-Customer-Id'])
@pytest.mark.asyncio
async def test_cross_origin_redirect_cannot_replay_any_auth_context(credential_header):
    from shopextract.extractors._storefront import request
    visited=[]
    def server(req):
        visited.append(str(req.url));return httpx.Response(307,headers={'location':'https://other.test/graphql'})
    async with httpx.AsyncClient(transport=httpx.MockTransport(server)) as client:
        with pytest.raises(ValueError,match='origin'):
            await request(client,'GET',SHOP+'/graphql',headers={credential_header:'secret'})
    assert visited==[SHOP+'/graphql']


@pytest.mark.asyncio
async def test_customer_failure_never_falls_back_to_anonymous_html_and_scope_is_isolated():
    server=StorefrontMock('private',customer='customer-secret',rejection=(200,'invalid customer-secret'))
    async with httpx.AsyncClient(transport=httpx.MockTransport(server)) as client:
        adapter=BigCommerceExtractor(http_client=client)
        with patch('shopextract.extractors.bigcommerce.BigCommerceExtractor',return_value=adapter), \
             patch('shopextract._discover.discover',side_effect=AssertionError('Anonymous fallback forbidden')):
            result=await extract(SHOP,platform=Platform.BIGCOMMERCE,api_options={
                'endpoint':SHOP+'/graphql','access_token':'credential','token_type':'private',
                'customer_access_token':'customer-secret'})
    assert not result.products and result.errors and result.catalog_complete is False
    assert ':customer:' in result.observation_scope and 'customer-secret' not in result.observation_scope


@pytest.mark.parametrize('prices', [None,{}])
def test_optional_product_prices_preserve_native_identifiers_image_path_and_stock(prices):
    raw=product();raw['prices']=prices
    p=normalize(capture(raw,SHOP+'/graphql','bigcommerce_graphql'),Platform.BIGCOMMERCE,SHOP)
    assert p.external_id=='1' and p.image_url==SHOP+'/p.jpg' and p.product_url==SHOP+'/p1/'
    assert p.in_stock is False and p.trust_view()['/in_stock']['state']=='observed'
    assert p.trust_view()['/price']['state']=='unsupported'


def test_query_is_validated_against_frozen_documented_catalog_subset():
    assert not validate(SCHEMA,parse(_QUERY))
    assert validate(SCHEMA,parse(_QUERY.replace('entityId name sku','invalidField name sku')))
    assert validate(SCHEMA,parse(_QUERY.replace('first:$size','unknownArgument:$size')))


@pytest.mark.parametrize('options',[
    {'token_type':'private','access_token':'credential','customer_access_token':'customer-secret'},
    {'token_type':'impersonation','access_token':'credential','customer_id':'42'}])
@pytest.mark.asyncio
async def test_public_pipeline_dispatch_keeps_customer_context_and_support(options):
    server=StorefrontMock(options['token_type'],options.get('customer_access_token'),options.get('customer_id'))
    async with httpx.AsyncClient(transport=httpx.MockTransport(server)) as client:
        adapter=BigCommerceExtractor(http_client=client)
        with patch('shopextract.extractors.bigcommerce.BigCommerceExtractor',return_value=adapter), \
             patch('shopextract._discover.discover',side_effect=AssertionError('Must use API')):
            result=await extract(SHOP,platform=Platform.BIGCOMMERCE,max_urls=2,api_options=options)
    assert len(result.products)==2 and not result.errors
    assert ':customer:' in result.observation_scope
    assert result.products[0].trust_view()['/price']['state']=='observed'


@pytest.mark.asyncio
async def test_anonymous_auth_failure_continues_html_and_retains_redacted_status():
    from shopextract._models import ExtractorResult
    from unittest.mock import AsyncMock
    server=StorefrontMock('private',rejection=(401,'credential rejected'))
    html=capture({'@type':'Product','name':'HTML product','sku':'sku','image':SHOP+'/image',
                  'url':SHOP+'/p','offers':{'price':12,'priceCurrency':'EUR'}},SHOP+'/p','json_ld')
    async with httpx.AsyncClient(transport=httpx.MockTransport(server)) as client:
        adapter=BigCommerceExtractor(http_client=client)
        with patch('shopextract.extractors.bigcommerce.BigCommerceExtractor',return_value=adapter), \
             patch('shopextract._discover.discover',AsyncMock(return_value=[SHOP+'/p'])), \
             patch('shopextract.extractors.unified.UnifiedCrawlExtractor.extract',AsyncMock(return_value=ExtractorResult(products=[html]))):
            result=await extract(SHOP,platform=Platform.BIGCOMMERCE,max_urls=1,
                api_options={'token_type':'private','access_token':'credential'})
    assert len(result.products)==1 and result.products[0].price==12
    assert result.errors==['BigCommerce GraphQL unavailable: HTTP 401']


@pytest.mark.asyncio
async def test_failure_after_first_page_retains_only_successful_captured_products():
    server=StorefrontMock('private');count=0
    def respond(req):
        nonlocal count
        count+=1
        if count==2:return httpx.Response(401,json={'errors':[{'message':'revoked credential'}]})
        return server(req)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result=await BigCommerceExtractor(page_size=1,http_client=client).extract(
            SHOP,token_type='private',access_token='credential',max_products=3)
    assert len(result.products)==1 and not result.complete and result.error.endswith('HTTP 401')
    assert result.products[0]['_capture']['url']==SHOP+'/graphql'


@pytest.mark.asyncio
async def test_explicit_tokens_and_context_never_enter_urls_or_request_body():
    server=StorefrontMock('private',customer='customer-secret')
    async with httpx.AsyncClient(transport=httpx.MockTransport(server)) as client:
        await BigCommerceExtractor(http_client=client).extract(
            SHOP+'/collection/',token_type='private',access_token='credential',customer_access_token='customer-secret')
    for req in server.calls:
        assert 'credential' not in str(req.url) and 'customer-secret' not in str(req.url)
        assert b'credential' not in req.content and b'customer-secret' not in req.content


@pytest.mark.asyncio
async def test_network_timeout_is_redacted_and_incomplete():
    def respond(req):raise httpx.ReadTimeout('credential customer-secret',request=req)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result=await BigCommerceExtractor(http_client=client).extract(SHOP,token_type='private',access_token='credential')
    assert not result.complete and not result.products and result.error.endswith('ReadTimeout')
    assert 'credential' not in result.error


@pytest.mark.asyncio
async def test_bigcommerce_graphql_partial_data_is_never_accepted():
    def respond(req):return httpx.Response(200,json={'data':{'site':{'products':{'edges':[{'node':product()}]}}},
                                                   'errors':[{'message':'unauthorized credential'}]})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result=await BigCommerceExtractor(http_client=client).extract(SHOP,token_type='private',access_token='credential')
    assert not result.products and not result.complete and 'credential' not in result.error


def test_frozen_schema_matches_saved_official_field_types_and_nullability():
    snapshot=json.loads((Path(__file__).parent/'fixtures/bigcommerce/documented-field-types.json').read_text())
    for type_name,fields in snapshot.items():
        for name,expected in fields.items():
            assert str(SCHEMA.get_type(type_name).fields[name].type)==expected


@pytest.mark.asyncio
async def test_bigcommerce_auth_options_cannot_be_silently_used_on_other_platforms():
    with pytest.raises(ValueError,match='BIGCOMMERCE'):
        await extract(SHOP,platform=Platform.SHOPWARE,api_options={'token_type':'private','access_token':'credential'})


@pytest.mark.asyncio
async def test_published_stencil_token_is_rediscovered_after_rotation():
    generation=0;seen=[]
    def respond(req):
        nonlocal generation
        if req.method=='GET':
            generation+=1
            return httpx.Response(200,text=f'<script>{{storefrontApiToken:"rotated-{generation}"}}</script>')
        assert req.headers['authorization']==f'Bearer rotated-{generation}'
        seen.append(req.headers['authorization'])
        body=json.loads(req.content)
        root={'site':{'products':{'edges':[{'node':product()}],
                                 'pageInfo':{'hasNextPage':False,'endCursor':None}}}}
        result=graphql_sync(SCHEMA,body['query'],root_value=root,variable_values=body['variables'])
        assert not result.errors
        return httpx.Response(200,json={'data':result.data})
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        adapter=BigCommerceExtractor(http_client=client)
        for _ in range(2):
            result=await adapter.extract(SHOP)
            assert result.complete and not result.error
    assert seen==['Bearer rotated-1','Bearer rotated-2']
