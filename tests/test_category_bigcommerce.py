"""Predesigned bounded BigCommerce native/guard mechanisms; external HTTP only controlled."""
import asyncio
from datetime import datetime, timezone
import json
from pathlib import Path
import time

from graphql import build_schema, parse, validate
import httpx
import pytest

from shopextract._capture import capture
from shopextract._evidence import SupportState
from shopextract._models import Platform
from shopextract.categories import (CategoryOptions, CategoryScope, TargetRegistry,
                                  normalize_with_categories)
from shopextract.extractors.bigcommerce import BigCommerceExtractor, _QUERY, _QUERY_WITH_CATEGORIES
from shopextract.tools import ToolConfig, Limits
from shopextract.tools.context import OperationContext, OperationBudget
from shopextract.tools.contracts import ToolError
from shopextract.tools.security import GuardedTransport, NativeReadPolicy, SourceGuard
from tests.test_bigcommerce_auth import product

STORE = 'https://shop.test'
OPTIONS = CategoryOptions(CategoryScope(Platform.BIGCOMMERCE,STORE),TargetRegistry('operator','1',('A',)))
AT = datetime(2026,10,17,tzinfo=timezone.utc)


def node(categories=None):
    result = product()
    result['categories'] = categories if categories is not None else {
        'pageInfo': {'hasNextPage':False,'endCursor':None},'edges':[
        {'node':{'entityId':7,'name':'Boots','path':'/boots/'}},
        {'node':{'entityId':9,'name':'Sale','path':'/sale/'}}]}
    return result


def envelope(items, errors=None):
    result = {'data':{'site':{'products':{'pageInfo':{'hasNextPage':False,'endCursor':None},
        'edges':[{'node':item} for item in items]}}}}
    if errors:
        result['errors'] = errors
    return result


def test_c03_reviewed_query_validates_against_saved_schema():
    schema = (Path(__file__).parent/'fixtures/bigcommerce/catalog.graphql').read_text()
    schema = schema.replace('type Product {','type Product { categories(first:Int,after:String):CategoryConnection!\n')
    schema += '\ntype CategoryConnection { pageInfo:PageInfo! edges:[CategoryEdge!] }\ntype CategoryEdge { node:Category! }\ntype Category { entityId:Int! name:String! path:String! }\n'
    assert validate(build_schema(schema),parse(_QUERY_WITH_CATEGORIES)) == []
    assert 'categories(first:20)' in _QUERY_WITH_CATEGORIES
    assert 'categories(' not in _QUERY


async def test_c03_native_mode_default_and_partial_error_keeps_siblings():
    sent = []
    body = envelope([node(),dict(node(),entityId=2)])
    body['errors'] = [{'path':['site','products','edges',1,'node','categories'],'extensions':{'code':'DENIED'}}]
    def wire(request):
        sent.append(json.loads(request.content))
        return httpx.Response(200,json=body)
    async with httpx.AsyncClient(transport=httpx.MockTransport(wire)) as client:
        extracted = await BigCommerceExtractor(http_client=client).extract(STORE,endpoint=STORE+'/graphql',access_token='fixture',include_categories=True)
    assert len(sent) == 1 and sent[0]['query'] == _QUERY_WITH_CATEGORIES
    assert len(extracted.products) == 2 and not extracted.complete
    first = normalize_with_categories(extracted.products[0],Platform.BIGCOMMERCE,STORE,category_options=OPTIONS)
    second = normalize_with_categories(extracted.products[1],Platform.BIGCOMMERCE,STORE,category_options=OPTIONS)
    assert first.observations[0].completeness == 'complete'
    assert second.observations[0].completeness == 'partial'
    assert second.observations[0].reason == 'category_source_error'
    assert all(f.support != SupportState.OBSERVED for t in second.observations[0].terms for f in t.facts)


@pytest.mark.parametrize('page_info,expected', [(None,'unknown'),({'hasNextPage':'false'},'unknown'),({'hasNextPage':True,'endCursor':'c1'},'partial')])
async def test_c04_missing_completion_or_next_page_retains_only_bounded_memberships(page_info,expected):
    categories = {'edges':[{'node':{'entityId':7,'name':'Boots','path':'/boots/'}}]}
    if page_info is not None:
        categories['pageInfo'] = page_info
    requests=[]
    def wire(request):
        requests.append(request)
        return httpx.Response(200,json=envelope([node(categories)]))
    async with httpx.AsyncClient(transport=httpx.MockTransport(wire)) as client:
        extracted = await BigCommerceExtractor(http_client=client).extract(STORE,endpoint=STORE+'/graphql',access_token='fixture',include_categories=True)
    value = normalize_with_categories(extracted.products[0],Platform.BIGCOMMERCE,STORE,category_options=OPTIONS)
    assert len(requests) == 1 and len(value.observations[0].terms) == 1
    assert value.observations[0].completeness == expected
    assert not value.observations[0].parent_edges


@pytest.mark.parametrize('status,body', [(200,{'errors':[{'message':'Unsupported categories'}]}),(403,{'errors':[{'message':'Denied'}]})])
async def test_c03_rejection_is_unavailable_without_retry(status,body):
    requests=[]
    def wire(request):
        requests.append(request)
        return httpx.Response(status,json=body)
    async with httpx.AsyncClient(transport=httpx.MockTransport(wire)) as client:
        result = await BigCommerceExtractor(http_client=client).extract(STORE,endpoint=STORE+'/graphql',access_token='fixture',include_categories=True)
    assert len(requests) == 1 and result.products == [] and not result.complete and result.error


async def test_c21_guard_uses_producer_constants_only_in_enabled_mode():
    sent=[]
    async def resolver(host,context):
        return ['93.184.216.34']
    def wire(request):
        sent.append(request)
        return httpx.Response(200,json={})
    config = ToolConfig(allowed_origins=(STORE,))
    guard = SourceGuard(config,resolver=resolver)
    def transport(mode):
        context = OperationContext('category-test',time.monotonic()+10,asyncio.Event(),OperationBudget(Limits()),None,AT)
        return GuardedTransport(config,context,guard,httpx.MockTransport(wire),policy=NativeReadPolicy(category_mode=mode))
    async with httpx.AsyncClient(transport=transport(False)) as client:
        with pytest.raises(ToolError) as denied:
            await client.post(STORE+'/graphql',json={'query':_QUERY_WITH_CATEGORIES,'variables':{'size':1,'after':None}})
    assert denied.value.code == 'permission_denied'
    assert denied.value.message == 'Only fixed native read queries are available'
    assert sent == []
    async with httpx.AsyncClient(transport=transport(True)) as client:
        response = await client.post(STORE+'/graphql',json={'query':_QUERY_WITH_CATEGORIES,'variables':{'size':1,'after':None}})
        assert response.status_code == 200
        with pytest.raises(ToolError):
            await client.post(STORE+'/graphql',json={'query':_QUERY_WITH_CATEGORIES+' mutation { write }','variables':{}})
    assert len(sent) == 1
