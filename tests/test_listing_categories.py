"""Designed listing membership mechanisms using controlled HTTP, never live claims."""
import copy
import json
from pathlib import Path
from unittest.mock import patch

import httpx
import pytest
from click.testing import CliRunner

from shopextract._capture import capture
from shopextract._models import Platform
from shopextract.categories import (CategoryOptions, CategoryScope, CategorySelector,
    MappingRule, TargetRegistry, normalize_with_categories, categorized_product_to_record,
    categorized_product_from_record)
from shopextract.categories._codec import wire
from shopextract.cli import main

STORE = 'https://www.naheed.pk'
CATEGORY = STORE + '/health-beauty/setting-powders'
PRODUCT = STORE + '/max-factor-powder'


def listing(products=(PRODUCT,), label='Setting Powders', next_page=None):
    heading = '<h1 class="page-title"><span>' + label + '</span></h1>' if label is not None else ''
    cards = ''.join('<li class="product-item"><a class="product-item-link" href="'+url+'">Powder</a></li>' for url in products)
    pager = '<div class="pages"><a class="next" href="'+next_page+'">Next</a></div>' if next_page else ''
    return ('<main>'+heading+'<div class="products-grid"><ol>'+cards+'</ol></div>'+pager+
        '<div class="block related"><div class="products-grid"><li class="product-item"><a class="product-item-link" href="/recommended">Other</a></li></div></div>'
        '<nav><a class="product-item-link" href="/menu">Menu</a></nav></main>')


def options():
    return CategoryOptions(CategoryScope(Platform.MAGENTO, STORE), TargetRegistry('google:product_category','test-v1',('123',)),
        (MappingRule('powders','1', CategorySelector('merchant:listing_category',None,native_id=CATEGORY,allow_unknown_version=True),('123',)),))


def raw():
    return capture({'@type':'Product','name':'Powder','url':PRODUCT,'offers':{'price':10},'image':STORE+'/real.jpg'},PRODUCT,'json_ld')


@pytest.mark.asyncio
async def test_listing_index_retains_two_memberships_and_maps_with_evidence():
    from shopextract.categories.listings import build_listing_index, with_listing_categories
    other = STORE + '/makeup'
    pages = {CATEGORY:listing((PRODUCT, PRODUCT),next_page='?p=2'), CATEGORY+'?p=2':listing((PRODUCT,),next_page=CATEGORY), other:listing(label='Makeup')}
    requests=[]
    def handler(req):
        requests.append(str(req.url));return httpx.Response(200,text=pages[str(req.url)])
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        index = await build_listing_index([CATEGORY,other],STORE,client=client,max_pages=3)
    assert index['complete'] and index['pages_visited'] == 3 and len(index['memberships']) == 2
    assert set(requests) == set(pages)
    attached = with_listing_categories(raw(),index)
    result = normalize_with_categories(attached,Platform.MAGENTO,STORE,category_options=options())
    obs = next(o for o in result.observations if o.terms and o.terms[0].ref.namespace == 'merchant:listing_category')
    assert {t.ref.native_id for t in obs.terms} == {CATEGORY,other}
    assert obs.completeness == 'unknown' and not obs.parent_edges
    assert any(m.status == 'mapped' and m.target_ids == ('123',) for m in result.mappings)
    assert all(f.support.value == 'observed' for t in obs.terms for f in t.facts)
    assert {e.source_url for t in obs.terms for f in t.facts for e in f.evidence} == {CATEGORY,other}
    assert categorized_product_from_record(categorized_product_to_record(result)).observations == result.observations


@pytest.mark.asyncio
@pytest.mark.parametrize('kind', ['failed','oversize','cross-next','redirect','nonlisting'])
async def test_failed_or_unsafe_acquisition_is_partial_without_fabricated_membership(kind):
    from shopextract.categories.listings import build_listing_index
    def handler(req):
        if kind=='failed':return httpx.Response(403)
        if kind=='oversize':return httpx.Response(200,text='x'*1000)
        if kind=='redirect':return httpx.Response(302,headers={'location':'https://other.test/stolen'})
        if kind=='nonlisting':return httpx.Response(200,text='<html><h1>Access denied</h1></html>')
        return httpx.Response(200,text=listing(next_page='https://other.test/cat'))
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        index=await build_listing_index([CATEGORY],STORE,client=client,page_bytes=999 if kind=='oversize' else 1048576)
    assert index['complete'] is False and index['reasons']
    assert len(index['memberships']) == (1 if kind=='cross-next' else 0)


@pytest.mark.asyncio
async def test_missing_heading_is_url_only_and_budget_exhaustion_is_partial():
    from shopextract.categories.listings import build_listing_index, with_listing_categories
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda req:httpx.Response(200,text=listing((PRODUCT,STORE+'/second'),None,next_page='?p=2')))) as client:
        index=await build_listing_index([CATEGORY],STORE,client=client,max_memberships=1)
    assert not index['complete'] and len(index['memberships']) == 1
    assert index['memberships'][0]['label'] is None
    result=normalize_with_categories(with_listing_categories(raw(),index),Platform.MAGENTO,STORE,category_options=options())
    obs=next(o for o in result.observations if any(t.ref.namespace=='merchant:listing_category' for t in o.terms))
    assert obs.completeness=='partial' and obs.terms[0].label is None
    assert len(obs.terms[0].facts)==1


@pytest.mark.asyncio
async def test_index_validation_rejects_tamper_scope_and_exact_url_matching():
    from shopextract.categories.listings import build_listing_index, with_listing_categories, validate_listing_index
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda req:httpx.Response(200,text=listing()))) as client:
        index=await build_listing_index([CATEGORY],STORE,client=client)
    assert with_listing_categories({**raw(),'url':PRODUCT+'?different=1'},index)['listing_categories'] == []
    for mutate in [lambda v:v.update(schema_version=True), lambda v:v.update(store_url='https://other.test'),
                   lambda v:v['memberships'][0].update(label='Forged'),
                   lambda v:v['memberships'][0].update(product_url='https://other.test/product')]:
        invalid=copy.deepcopy(index);mutate(invalid)
        with pytest.raises(ValueError):validate_listing_index(invalid,STORE)
    for url in [STORE+'/../outside',STORE+'/%2e%2e/outside','https://other.test/cat']:
        with pytest.raises(ValueError):
            await build_listing_index([url],STORE)


@pytest.mark.asyncio
@pytest.mark.parametrize('limit,expected,complete', [(1,1,False),(2,2,False),(3,3,True)])
async def test_page_budget_boundaries_and_deterministic_100_card_stress(limit,expected,complete):
    from shopextract.categories.listings import build_listing_index
    requests=[]
    def handler(req):
        number=int(req.url.params.get('p','1'));requests.append(number)
        products=tuple(STORE+'/p'+str(i) for i in range((number-1)*34,min(number*34,100)))
        return httpx.Response(200,text=listing(products,next_page='?p='+str(number+1) if number<3 else CATEGORY))
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        index=await build_listing_index([CATEGORY],STORE,client=client,max_pages=limit,max_memberships=200)
    assert len(requests)==expected and index['complete'] is complete
    assert len(index['memberships'])==min(expected*34,100)


def test_saved_sitemap_urls_are_not_membership_observations():
    from shopextract.categories.listings import listing_urls
    source=Path('specs/018-cli-product-discovery-fix/evidence/category-reference.xml').read_bytes()
    assert len(listing_urls(source)) == 757
    assert listing_urls(json.dumps([CATEGORY]).encode()) == [CATEGORY]
    with pytest.raises(ValueError):listing_urls(b'{"not":"urls"}')


def test_cli_index_then_normalize_uses_existing_mapper(tmp_path):
    from shopextract.categories.listings import build_listing_index
    client_type=httpx.AsyncClient
    def factory(**kwargs):
        return client_type(transport=httpx.MockTransport(lambda req:httpx.Response(200,text=listing())),**kwargs)
    urls=tmp_path/'urls.json';urls.write_text(json.dumps([CATEGORY]))
    config=tmp_path/'options.json';config.write_text(json.dumps(wire(options())))
    source=tmp_path/'raw.json';source.write_text(json.dumps(raw()))
    index=tmp_path/'index.json'
    runner=CliRunner()
    with patch('httpx.AsyncClient',side_effect=factory):
        result=runner.invoke(main,['categories','index-listings',str(urls),'--options',str(config),'--output',str(index)])
    assert result.exit_code==0,(result.output,result.exception)
    result=runner.invoke(main,['categories','normalize',str(source),'--options',str(config),'--listing-index',str(index)])
    assert result.exit_code==0,(result.output,result.exception)
    data=json.loads(result.output)['data']
    assert any(m['status']=='mapped' and m['target_ids']==['123'] for m in data['categorized_products'][0]['mappings'])


@pytest.mark.asyncio
async def test_dripping_body_cannot_outlive_total_acquisition_deadline(monkeypatch):
    import asyncio
    import time
    import shopextract.categories.listings as module
    class Drip(httpx.AsyncByteStream):
        async def __aiter__(self):
            for chunk in [b'<main>']*100:
                await asyncio.sleep(.01)
                yield chunk
    monkeypatch.setattr(module,'_TOTAL_TIMEOUT',.02)
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda req:httpx.Response(200,stream=Drip()))) as client:
        start=time.monotonic()
        index=await module.build_listing_index([CATEGORY],STORE,client=client)
        elapsed=time.monotonic()-start
    assert elapsed<.25
    assert not index['complete'] and 'time_budget_reached' in index['reasons']
    assert index['memberships']==[]


@pytest.mark.asyncio
async def test_final_response_identity_and_store_base_path_are_checked():
    from shopextract.categories.listings import build_listing_index
    from contextlib import asynccontextmanager
    class MismatchedClient:
        @asynccontextmanager
        async def stream(self,*args,**kwargs):
            yield httpx.Response(200,text=listing(),request=httpx.Request('GET','https://outside.test/cat'))
    index=await build_listing_index([CATEGORY],STORE,client=MismatchedClient())
    assert not index['complete'] and not index['memberships']
    with pytest.raises(ValueError):await build_listing_index([STORE+'/outside'],STORE+'/shop')
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda req:httpx.Response(200,text=listing((STORE+'/outside',)))) ) as client:
        index=await build_listing_index([STORE+'/shop/category'],STORE+'/shop',client=client)
    assert not index['complete'] and not index['memberships']


@pytest.mark.asyncio
async def test_malformed_imported_capture_is_rejected():
    from shopextract.categories.listings import build_listing_index, validate_listing_index
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda req:httpx.Response(200,text=listing()))) as client:
        index=await build_listing_index([CATEGORY],STORE,client=client)
    for change in [('at','invalid'),('at','2026-10-31T00:00:00'),('values',[]),('truncated','no')]:
        invalid=copy.deepcopy(index)
        invalid['memberships'][0]['_capture'][change[0]]=change[1]
        with pytest.raises(ValueError):validate_listing_index(invalid,STORE)


@pytest.mark.parametrize('index', [[], {'schema_version':99}, {'schema_version':1,'store_url':'https://other.test','pages_visited':0,'complete':True,'reasons':[],'memberships':[]}])
def test_cli_rejects_invalid_listing_artifact(tmp_path,index):
    source=tmp_path/'raw.json';source.write_text(json.dumps(raw()))
    config=tmp_path/'options.json';config.write_text(json.dumps(wire(options())))
    artifact=tmp_path/'index.json';artifact.write_text(json.dumps(index))
    result=CliRunner().invoke(main,['categories','normalize',str(source),'--options',str(config),'--listing-index',str(artifact)])
    assert result.exit_code==2,(result.output,result.exception)
    assert json.loads(result.output)['error']['code']=='E_USAGE'


def test_listing_xml_entities_are_rejected_without_entity_resolution():
    from shopextract.categories.listings import listing_urls
    with pytest.raises(ValueError):
        listing_urls(b'<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/hosts">]><urlset><url><loc>&xxe;</loc></url></urlset>')


@pytest.mark.parametrize('index',[None,[],0])
def test_listing_helper_invalid_index_type_has_category_error(index):
    from shopextract.categories.listings import with_listing_categories
    from shopextract.categories import CategoryError
    with pytest.raises(CategoryError):with_listing_categories(raw(),index)
