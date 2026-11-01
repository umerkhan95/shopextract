"""Child01 acceptance, designed before implementation; synthetic external sources."""
import asyncio
import json
import sys
from types import SimpleNamespace
from unittest.mock import patch

import httpx
import pytest
from click.testing import CliRunner

from shopextract._models import ExtractionResult, Product, Platform
from shopextract.cli import main
from shopextract.extractors.unified import UnifiedCrawlExtractor
from shopextract.extractors.woocommerce import WooCommerceExtractor
from shopextract._normalize import _normalize_opengraph

URL = 'https://fixture.invalid'
PRODUCT = '<script type="application/ld+json">{"@type":"Product","name":"Free widget","image":"https://fixture.invalid/i.png","description":"Source product description","sku":"P1","offers":{"price":"0","priceCurrency":"PKR"}}</script>'
POLICY = '<meta property="og:title" content="Returns policy"><meta property="og:type" content="website"><meta property="og:image" content="https://fixture.invalid/logo.png">'


@pytest.mark.parametrize('count,coverage,errors,reasons,expected', [
    (0,None,[],[],'failed'), (0,False,[],[],'failed'), (0,True,[],[],'failed'),
    (1,None,[],[],'partial'), (1,False,[],[],'partial'), (1,True,[],[],'complete'),
    (1,True,['failed page'],[],'partial'), (1,True,[],['capped'],'partial'),
])
def test_python_outcome(count,coverage,errors,reasons,expected):
    r=ExtractionResult(products=[Product(title='P')]*count,catalog_complete=coverage,
                       errors=errors,incompleteness_reasons=reasons)
    assert r.outcome == expected


@pytest.mark.parametrize('raw,accepted', [
    ({'og:title':'Returns policy','og:type':'website','og:image':'logo'},False),
    ({'og:title':'Free widget','og:type':'product','product:price:amount':'0'},True),
    ({'og:title':'Widget','product:retailer_item_id':'P1'},True),
    ({'og:title':'Widget','og:price:amount':'0'},True),
    ({'og:title':'   ','og:type':'product'},False),
])
def test_og_normalizer_admission(raw,accepted):
    assert (_normalize_opengraph(raw,URL) is not None) is accepted


def test_static_policy_rejected_and_free_schema_preserved():
    assert UnifiedCrawlExtractor._extract_structured_from_html(POLICY,URL) == []
    assert UnifiedCrawlExtractor._extract_structured_from_html(PRODUCT,URL)[0]['name']=='Free widget'


@pytest.fixture
def crawl_boundary(monkeypatch):
    """Only crawler/config boundaries replaced: real single/batch/parsing execute."""
    import shopextract.extractors.unified as module
    results=[]
    class Crawler:
        def __init__(self,**kw): pass
        async def __aenter__(self): return self
        async def __aexit__(self,*a): pass
        async def arun(self,**kw): return results[0]
        async def arun_many(self,**kw): return results
    monkeypatch.setitem(sys.modules,'crawl4ai',SimpleNamespace(AsyncWebCrawler=Crawler))
    monkeypatch.setitem(sys.modules,'crawl4ai.async_dispatcher',SimpleNamespace(MemoryAdaptiveDispatcher=lambda **kw:None))
    for name in ('get_browser_config','get_crawl_config','get_crawler_strategy'):
        monkeypatch.setattr(module,name,lambda *a,**k:None)
    return results


def crawl_result(status=200,success=True,html=PRODUCT):
    return SimpleNamespace(status_code=status,success=success,url=URL,html=html,
                           metadata={},markdown='',media={})


@pytest.mark.asyncio
@pytest.mark.parametrize('mode,status,success,accepted',[
    ('single',200,True,True),('single',404,True,False),
    ('single',None,True,False),('single',200,False,False),
    ('batch',200,True,True),('batch',404,True,False),('batch',None,True,False)])
async def test_browser_http_admission(crawl_boundary,mode,status,success,accepted):
    crawl_boundary.append(crawl_result(status,success))
    e=UnifiedCrawlExtractor()
    value=await e._extract_with_browser(URL) if mode=='single' else (await e.extract_batch([URL])).products
    assert bool(value) is accepted


@pytest.mark.asyncio
async def test_browser_mixed_batch_retains_good_and_marks_partial(crawl_boundary):
    crawl_boundary.extend([crawl_result(),crawl_result(404)])
    r=await UnifiedCrawlExtractor().extract_batch([URL,URL+'/missing'])
    assert len(r.products)==1
    assert r.complete is False and r.error


@pytest.mark.asyncio
async def test_browser_policy_markdown_not_product(crawl_boundary):
    r=crawl_result(html=POLICY);r.markdown='# Returns policy\nPrice: $21.00'
    crawl_boundary.append(r)
    assert await UnifiedCrawlExtractor()._extract_with_browser(URL)==[]


@pytest.mark.asyncio
@pytest.mark.parametrize('statuses,sizes,expected', [([200,404],[100,0],False),
    ([404],[0],False),([200],[99],True),([200,200],[100,0],True)])
async def test_woo_page_transitions(statuses,sizes,expected):
    calls=[]
    def respond(req):
        i=len(calls);calls.append(req)
        return httpx.Response(statuses[i],json=[{'id':j,'name':'Widget'} for j in range(sizes[i])])
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        r=await WooCommerceExtractor(http_client=client,max_pages=2).extract(URL)
    assert r.complete is expected
    assert len(r.products)==sizes[0]
    if not expected: assert '404' in r.error
    if len(statuses)>1 and not expected: assert '2' in r.error


@pytest.fixture
def cli_transport(monkeypatch):
    original=httpx.AsyncClient
    mode={'kind':'html','status':200}
    from tests._discovery_boundary import borrow_worker_network
    borrow_worker_network(monkeypatch)
    def respond(req):
        if req.url.path=='/robots.txt':return httpx.Response(404)
        if mode['kind']=='empty_discovery':
            return httpx.Response(404,text='No source here')
        if req.url.path.endswith('.xml'):
            return httpx.Response(200,text='<urlset><url><loc>'+URL+'/products/widget</loc></url></urlset>')
        if req.url.path=='/products.json':
            ps=[] if mode['kind']=='empty' else [{'id':1,'title':'Widget','handle':'widget',
                'body_html':'Source description','images':[{'src':URL+'/i.png'}],
                'variants':[{'id':2,'price':'0','available':True}]}]
            return httpx.Response(200,json={'products':ps})
        return httpx.Response(mode['status'],text=PRODUCT)
    def factory(*a,**kw):
        kw['transport']=httpx.MockTransport(respond)
        return original(*a,**kw)
    monkeypatch.setattr(httpx,'AsyncClient',factory)
    return mode


def invoke(*args):
    return CliRunner().invoke(main,['--output-format','json',*args])


@pytest.mark.parametrize('kind,platform,expected',[('empty','shopify',1),('html','generic',3),('html','shopify',0)])
def test_real_cli_extract_outcomes(cli_transport,kind,platform,expected):
    cli_transport['kind']=kind
    r=invoke('extract',URL,'--platform',platform,'--max','2')
    assert r.exit_code==expected,r.output[:300]
    v=json.loads(r.stdout)
    assert v['completeness']=={1:'unavailable',3:'partial',0:'complete'}[expected]
    if expected==3: assert v['data']['products']


@pytest.mark.parametrize('empty',[False,True])
def test_cli_discovery_unknown_coverage(cli_transport,monkeypatch,empty):
    if empty: cli_transport['kind']='empty_discovery'
    r=invoke('discover',URL,'--platform','woocommerce' if empty else 'generic','--max','2')
    assert r.exit_code==3,r.output[:300]
    v=json.loads(r.stdout)
    assert v['data']['catalog_complete'] is None
    assert bool(v['data']['urls']) is (not empty)


@pytest.mark.parametrize('status,accepted',[(200,True),(404,False)])
@pytest.mark.asyncio
async def test_static_http_status(status,accepted):
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda r:httpx.Response(status,text=PRODUCT))) as client:
        e=UnifiedCrawlExtractor(http_client=client)
        html=await e._fetch_html_httpx(URL)
        assert bool(html) is accepted


@pytest.mark.asyncio
@pytest.mark.parametrize('kind',['html','policy','empty_shopify','discover'])
async def test_native_tool_real_source_domain_outcomes(kind):
    from shopextract.tools import ToolConfig,ToolRuntime
    from tests.tool_api_fixtures import ORIGIN,resolver
    def respond(req):
        if req.url.path.endswith('.xml'):
            return httpx.Response(200,text='<urlset></urlset>')
        if req.url.path=='/products.json':return httpx.Response(200,json={'products':[]})
        if req.url.path=='/graphql':return httpx.Response(404)
        body=POLICY if kind=='policy' else ('<meta name="generator" content="shopify">' if kind=='empty_shopify' else PRODUCT)
        return httpx.Response(200,text=body,headers={'content-type':'text/html'})
    engine=ToolRuntime(ToolConfig(allowed_origins=(ORIGIN,)),resolver=resolver,wire_transport=httpx.MockTransport(respond))
    try:
        submit=await engine.call('discover' if kind=='discover' else 'extract',{'schema_version':'1.0','url':ORIGIN,'max_items':2})
        jid=submit['data']['job_id']
        for _ in range(500):
            v=await engine.call('job_status',{'schema_version':'1.0','job_id':jid})
            if v['data']['state'] not in ('queued','running'):break
            await asyncio.sleep(.02)
        assert v['data']['state'] in ('succeeded','failed'),v
        if kind in ('policy','empty_shopify'):
            assert v['data']['state']=='failed',v
            assert v['data']['error']['code']=='source_error'
        else:
            assert v['data']['state']=='succeeded',v
            result=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'urls' if kind=='discover' else 'products'})
            assert result['data']['completeness']=='partial',result
    finally:await engine.aclose()


@pytest.mark.parametrize('kind,platform,expected',[('empty','shopify',1),('html','generic',3),('html','shopify',0)])
def test_cli_atomic_outcome(cli_transport,tmp_path,kind,platform,expected):
    cli_transport['kind']=kind
    target=tmp_path/'out.json';target.write_text('sentinel')
    r=invoke('extract',URL,'--platform',platform,'--max','2','-o',str(target))
    assert r.exit_code==expected,r.output[:300]
    if expected==1:assert target.read_text()=='sentinel'
    else:assert json.loads(target.read_text())==json.loads(r.stdout)


@pytest.mark.parametrize('rows,expected',[(0,1),(1,3),(2,3)])
def test_feed_own_outcome_projection(monkeypatch,rows,expected):
    original=httpx.AsyncClient
    body='id,title,description,price,link,image_link\n'+''.join(
        f'{i},Widget,Source description,10 PKR,{URL}/p{i},{URL}/i.png\n' for i in range(rows))
    def factory(*a,**kw):
        kw['transport']=httpx.MockTransport(lambda req:httpx.Response(200,text=body,headers={'content-type':'text/csv'}))
        return original(*a,**kw)
    monkeypatch.setattr(httpx,'AsyncClient',factory)
    result=invoke('feed',URL+'/feed.csv','--max','1')
    assert result.exit_code==expected,result.output[:400]
    value=json.loads(result.stdout)
    if rows==0:
        assert value['error']['code']=='E_OPERATION' and value['data'] is None
    else:
        assert value['completeness']=='partial' and value['data']['product_count']==1
        assert len(value['data']['raw_products'])==1
        if rows==2:
            assert value['data']['catalog_complete'] is False
            assert 'product_budget_reached' in value['data']['incompleteness_reasons']
        else:assert value['data']['catalog_complete'] is None


@pytest.mark.parametrize('later_status',[404,200])
def test_woo_later_page_pipeline_cli_retention(monkeypatch,later_status):
    original=httpx.AsyncClient
    requests=[]
    def respond(req):
        requests.append(str(req.url))
        assert req.url.path=='/wp-json/wc/store/v1/products'
        if int(req.url.params.get('offset',(int(req.url.params.get('page','1'))-1)*int(req.url.params.get('per_page','100'))))==0:
            products=[{'id':i,'name':f'Widget{i}','description':'Source product description',
                'sku':f'SKU{i}','permalink':URL+f'/product/{i}',
                'images':[{'src':URL+'/i.png'}],
                'prices':{'price':'1000','currency_code':'PKR','currency_minor_unit':2}}
                for i in range(100)]
            return httpx.Response(200,json=products)
        return httpx.Response(later_status,json=[])
    def factory(*a,**kw):
        kw['transport']=httpx.MockTransport(respond)
        return original(*a,**kw)
    monkeypatch.setattr(httpx,'AsyncClient',factory)
    result=invoke('extract',URL,'--platform','woocommerce','--max','101')
    assert result.exit_code==3,result.output[:400]
    data=json.loads(result.stdout)['data']
    assert data['product_count']==100 and len(data['products'])==100
    assert len(data['raw_products'])==100 and len(requests)==2
    assert {r['product']['external_id'] for r in data['products']}=={str(i) for i in range(100)}
    if later_status==404:
        assert data['catalog_complete'] is False
        assert any('404' in error and '2' in error for error in data['errors'])
    else:
        assert data['catalog_complete'] is None and data['errors']==[]


@pytest.mark.parametrize('type_value',['ProductGroup',['Thing','ProductGroup'],'https://schema.org/ProductGroup'])
@pytest.mark.parametrize('mode',['static','browser'])
def test_product_group_compatibility(type_value,mode):
    raw={'@type':type_value,'name':'Widget group','hasVariant':[
        {'@type':'Product','name':'Widget','offers':{'price':'10','priceCurrency':'PKR'}}]}
    html='<script type="application/ld+json">'+json.dumps(raw)+'</script>'
    e=UnifiedCrawlExtractor()
    if mode=='static':products=e._extract_structured_from_html(html,URL)
    else:products=e._extract_from_crawl_result(crawl_result(html=html),URL)
    assert len(products)==1 and products[0]['name']=='Widget group'


def test_product_group_substring_not_type():
    html='<script type="application/ld+json">{"@type":"NotProductGroup","name":"Policy"}</script>'
    assert UnifiedCrawlExtractor._extract_structured_from_html(html,URL)==[]


@pytest.mark.parametrize('records,dropped',[([],[]),([{}],[0])])
def test_normalize_empty_compatibility(records,dropped):
    result=CliRunner().invoke(main,['--output-format','json','normalize','-','--platform','shopify'],input=json.dumps(records))
    assert result.exit_code==0,result.output[:300]
    assert json.loads(result.stdout)['data']=={'products':[],'product_count':0,'dropped_indices':dropped}


@pytest.mark.asyncio
@pytest.mark.parametrize('bad_html',[POLICY,'<script type="application/ld+json">{"@type":"Product","name":" "}</script>'])
async def test_browser_200_metadata_rejection_incomplete(crawl_boundary,bad_html):
    crawl_boundary.extend([crawl_result(),crawl_result(html=bad_html)])
    result=await UnifiedCrawlExtractor().extract_batch([URL,URL+'/policy'])
    assert len(result.products)==1
    assert result.complete is False and result.error
