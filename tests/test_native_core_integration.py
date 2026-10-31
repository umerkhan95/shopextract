"""Controlled external boundaries; native fallback/parser/binder code remains real."""
import json
from types import SimpleNamespace

import httpx
import pytest

from shopextract._evidence import SupportState
from shopextract._execution import ExecutionPolicy, execution_policy
from shopextract._extract import extract
from shopextract._models import ExtractionTier, Platform
from shopextract.categories.api import extract_with_categories
from shopextract.categories.contracts import CategoryError, CategoryOptions, CategoryScope, CategorySelector, MappingRule, TargetRegistry

URL = 'https://merchant.test/product/book'
SHOP = 'https://merchant.test'
JSONLD = '<script type="application/ld+json">'+json.dumps({'@type':'Product','name':'Book','category':'Books',
    'image':'https://merchant.test/book.jpg','offers':{'price':'25','priceCurrency':'PKR'},'description':'A book','sku':'B1'})+'</script>'
OG = '<meta property="og:type" content="product"><meta property="og:title" content="Book"><meta property="og:image" content="https://merchant.test/book.jpg"><meta property="product:price:amount" content="25"><meta property="product:price:currency" content="PKR"><meta property="product:category" content="Books">'
CSS = '<div class="product"><h1>Book</h1><span class="price">25</span><span itemprop="category">Books</span><img class="product-image" src="/book.jpg"></div>'


def options(namespace='schema.org:category'):
    return CategoryOptions(CategoryScope(Platform.GENERIC, SHOP), TargetRegistry('test:target','1',('books',)),
        (MappingRule('reviewed','1',CategorySelector(namespace,None,raw_label='Books',allow_unknown_version=True),('books',)),))


@pytest.fixture
def boundaries(monkeypatch):
    """Replace network/browser services only, retaining native discovery and parsers."""
    import crawl4ai
    import shopextract._discover as discovery
    import shopextract.extractors.css as css
    real_client = httpx.AsyncClient
    state = {'http_status':403,'http_html':'','browser_html':JSONLD,'http':[],'browser':[],'css':[]}
    def respond(request):
        state['http'].append(str(request.url))
        if 'api_json' in state and request.url.path == '/products.json':
            return httpx.Response(200,json=state['api_json'])
        return httpx.Response(state['http_status'], text=state['http_html'])
    def client(*args, **kwargs):
        kwargs['transport'] = httpx.MockTransport(respond)
        return real_client(*args, **kwargs)
    monkeypatch.setattr(httpx,'AsyncClient',client)
    class Seeder:
        async def __aenter__(self): return self
        async def __aexit__(self,*args): pass
        async def urls(self,*args): return [{'url':URL,'status':'valid'}]
    class Browser:
        def __init__(self,*args,**kwargs): pass
        async def __aenter__(self): return self
        async def __aexit__(self,*args): pass
        async def arun(self, url, config):
            state['browser'].append(url)
            return SimpleNamespace(success=True, url=url, html=state['browser_html'], metadata={},markdown='',media={})
        async def arun_many(self, urls, config, **kwargs):
            state['css'].extend(urls)
            results=[]
            for url in urls:
                rows=config.extraction_strategy.extract(url,state['browser_html'])
                results.append(SimpleNamespace(success=True,url=url,html=state['browser_html'],extracted_content=json.dumps(rows)))
            return results
    monkeypatch.setattr(discovery,'AsyncUrlSeeder',Seeder)
    monkeypatch.setattr(crawl4ai,'AsyncWebCrawler',Browser)
    monkeypatch.setattr(css,'AsyncWebCrawler',Browser)
    return state


@pytest.mark.asyncio
@pytest.mark.parametrize('body,namespace',[(JSONLD,'schema.org:category'),(OG,'opengraph:product_category'),(CSS,'generic:product_type')])
async def test_production_categories_use_native_fallbacks_and_observed_facts(boundaries,body,namespace):
    boundaries['browser_html']=body
    with execution_policy(ExecutionPolicy(browser=True)):
        result = await extract_with_categories(SHOP, category_options=options(namespace), source_mode='production', max_urls=1)
    assert boundaries['http'] and boundaries['browser']
    assert result.result.tier == (ExtractionTier.CSS if body==CSS else ExtractionTier.UNIFIED_CRAWL)
    if body==CSS: assert boundaries['css']==[URL]
    assert result.result.raw_products[0]['_capture']['url']==URL
    assert any(mapping.status=='mapped' for mapping in result.products[0].mappings)
    facts=[fact for observation in result.products[0].observations for term in observation.terms for fact in term.facts]
    assert facts and all(fact.support==SupportState.OBSERVED for fact in facts)
    assert all(e.source_url==URL for fact in facts for e in fact.evidence)


@pytest.mark.asyncio
async def test_production_http_success_does_not_force_browser(boundaries):
    boundaries.update(http_status=200,http_html=OG)
    with execution_policy(ExecutionPolicy(browser=True)):
        result=await extract(SHOP,platform=Platform.GENERIC,max_urls=1,include_categories=True)
    assert result.tier==ExtractionTier.UNIFIED_CRAWL and not boundaries['browser']
    assert result.raw_products[0]['category_declarations']['product:category']==['Books']


@pytest.mark.asyncio
async def test_category_production_scope_rejects_before_network(boundaries):
    with pytest.raises(CategoryError):
        await extract_with_categories(SHOP,category_options=options(),source_mode='production',shop_url='https://other.test')
    assert not boundaries['http'] and not boundaries['browser']


@pytest.mark.asyncio
async def test_invalid_source_mode_rejects_before_network(boundaries):
    with pytest.raises(CategoryError):
        await extract_with_categories(SHOP,category_options=options(),source_mode='unknown')
    assert not boundaries['http']


@pytest.mark.asyncio
async def test_production_missing_category_does_not_infer_from_title(boundaries):
    boundaries['browser_html']=JSONLD.replace('"category": "Books", ','')
    with execution_policy(ExecutionPolicy(browser=True)):
        result=await extract_with_categories(SHOP,category_options=options(),source_mode='production',max_urls=1)
    assert result.products and not any(m.status=='mapped' for m in result.products[0].mappings)


@pytest.mark.parametrize('level',['standard','stealth','undetected'])
def test_browser_tiers_preserve_configured_proxy(monkeypatch,level):
    from shopextract.extractors._browser import get_browser_config,StealthLevel
    for key in ('HTTPS_PROXY','https_proxy','HTTP_PROXY','http_proxy','ALL_PROXY','all_proxy'):
        monkeypatch.delenv(key,raising=False)
    value='http://alice:private-password@proxy.test:8080'
    monkeypatch.setenv('HTTPS_PROXY',value)
    config=get_browser_config(StealthLevel(level))
    assert config.proxy_config is not None
    assert config.proxy_config.server=='http://proxy.test:8080'
    assert config.proxy_config.username=='alice' and config.proxy_config.password=='private-password'
    assert __import__('os').environ['HTTPS_PROXY']==value


@pytest.mark.parametrize('value',['not-a-proxy','http://proxy.test:bad','http://proxy.test\nsecret'])
def test_browser_invalid_proxy_is_redacted_and_never_direct(monkeypatch,value):
    from shopextract.extractors._browser import get_browser_config
    monkeypatch.setenv('HTTPS_PROXY',value)
    with pytest.raises(ValueError) as caught:
        get_browser_config()
    assert value not in str(caught.value) and 'secret' not in str(caught.value)


@pytest.mark.asyncio
async def test_production_shopify_api_retains_native_category_and_short_circuits(boundaries):
    boundaries['api_json']={'products':[{'id':1,'title':'Book','handle':'book','product_type':'Books',
        'vendor':'Publisher','body_html':'A book','images':[{'src':SHOP+'/book.jpg'}],
        'variants':[{'id':10,'price':'25','sku':'B1','available':True}]}]}
    scope=CategoryScope(Platform.SHOPIFY,SHOP)
    config=CategoryOptions(scope,TargetRegistry('test:target','1',('books',)),
        (MappingRule('reviewed','1',CategorySelector('shopify:product_type',None,raw_label='Books',allow_unknown_version=True),('books',)),))
    with execution_policy(ExecutionPolicy(browser=True)):
        result=await extract_with_categories(SHOP,category_options=config,source_mode='production',max_urls=1)
    assert result.result.tier==ExtractionTier.API and not boundaries['browser'] and not boundaries['css']
    assert len(boundaries['http'])==1
    assert result.result.raw_products[0]['_capture']['method']=='shopify_api'
    assert any(mapping.status=='mapped' for mapping in result.products[0].mappings)
    assert any(f.support==SupportState.OBSERVED for o in result.products[0].observations for t in o.terms for f in t.facts)


@pytest.mark.asyncio
@pytest.mark.parametrize('restore,barcode,expected',[(False,'29877030712',None),(True,'29877030712','0029877030712'),(True,'29877030713',None)])
async def test_shopify_short_gtin_policy_survives_unified_fallback(boundaries,restore,barcode,expected):
    raw={'@type':'Product','name':'Book','image':SHOP+'/book.jpg','offers':{'price':'25','priceCurrency':'PKR'},
         'variants':[{'id':10,'barcode':barcode}]}
    boundaries['browser_html']='<script type="application/ld+json">'+json.dumps(raw)+'</script>'
    with execution_policy(ExecutionPolicy(browser=True)):
        result=await extract(SHOP,platform=Platform.SHOPIFY,max_urls=1,restore_short_gtin=restore)
    assert result.tier==ExtractionTier.UNIFIED_CRAWL and boundaries['browser']
    assert result.products[0].gtin==expected


@pytest.mark.asyncio
@pytest.mark.parametrize('source',[
    'https://other.test/catalog/book',
    'https://merchant.test/catalog-other/book',
    'https://merchant.test/catalog/../outside',
    'https://merchant.test/catalog/%2e%2e/outside',
    'https://merchant.test/catalog/%252e%252e/outside',
])
async def test_production_source_cannot_escape_declared_store(boundaries,source):
    from dataclasses import replace
    config=replace(options(),scope=CategoryScope(Platform.GENERIC,SHOP+'/catalog'))
    with pytest.raises(CategoryError):
        await extract_with_categories(source,category_options=config,source_mode='production',max_urls=1)
    assert not boundaries['http'] and not boundaries['browser'] and not boundaries['css']


def test_browser_proxy_precedence_and_lowercase_fallback_preserves_environment(monkeypatch):
    import os
    from shopextract.extractors._browser import get_browser_config
    for key in ('HTTPS_PROXY','https_proxy','HTTP_PROXY','http_proxy','ALL_PROXY','all_proxy'):
        monkeypatch.delenv(key,raising=False)
    monkeypatch.setenv('HTTPS_PROXY','http://secure-proxy.test:8443')
    monkeypatch.setenv('HTTP_PROXY','http://other-proxy.test:8080')
    monkeypatch.setenv('NO_PROXY','merchant.test,localhost')
    assert get_browser_config().proxy_config.server=='http://secure-proxy.test:8443'
    monkeypatch.delenv('HTTPS_PROXY')
    monkeypatch.setenv('https_proxy','http://lower-proxy.test:8443')
    assert get_browser_config().proxy_config.server=='http://lower-proxy.test:8443'
    assert os.environ['HTTP_PROXY']=='http://other-proxy.test:8080'
    assert os.environ['NO_PROXY']=='merchant.test,localhost'


@pytest.mark.asyncio
async def test_production_source_accepts_descendant_of_declared_store(boundaries):
    from dataclasses import replace
    config=replace(options(),scope=CategoryScope(Platform.GENERIC,SHOP+'/product'))
    with execution_policy(ExecutionPolicy(browser=True)):
        result=await extract_with_categories(URL,category_options=config,source_mode='production',max_urls=1)
    assert result.products and boundaries['http'] and boundaries['browser']
    assert any(m.status=='mapped' for m in result.products[0].mappings)
