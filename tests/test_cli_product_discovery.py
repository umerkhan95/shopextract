"""Controlled sources exercise native public discovery and CLI, never live HTTP."""
import json

from click.testing import CliRunner
import httpx
import pytest

from shopextract._discover import discover
from shopextract._models import Platform
from shopextract.cli import main

SHOP = 'https://merchant.test'


def index(*urls):
    return '<sitemapindex>' + ''.join(f'<sitemap><loc>{u}</loc></sitemap>' for u in urls) + '</sitemapindex>'


def urlset(*urls):
    return '<urlset>' + ''.join(f'<url><loc>{u}</loc></url>' for u in urls) + '</urlset>'


def source_handler(count, calls):
    def respond(request):
        calls.append(str(request.url))
        path = request.url.path
        if path == '/robots.txt':
            return httpx.Response(200, text=f'User-agent: *\nAllow: /\nSitemap: {SHOP}/maps/index.xml\nSitemap: {SHOP}/maps/sitemap_category.xml')
        if path == '/maps/index.xml':
            return httpx.Response(200, text=index(SHOP+'/maps/001.xml', SHOP+'/maps/later.xml'))
        if path == '/maps/sitemap_category.xml':
            return httpx.Response(200, text=urlset(SHOP+'/health-beauty'))
        if path == '/maps/001.xml':
            return httpx.Response(200, text=urlset(SHOP+'/health-beauty', *(SHOP+f'/item-{i}' for i in range(count))))
        if path.startswith('/item-'):
            number=int(path.split('-')[-1])
            body={'@type':'Product','name':f'Product {number}','sku':f'SKU{number}',
                  'image':SHOP+'/image.jpg','offers':{'price':str(25+number),'priceCurrency':'PKR'}}
            return httpx.Response(200, text='<script type="application/ld+json">'+json.dumps(body)+'</script>')
        return httpx.Response(404)
    return respond


@pytest.fixture
def no_browser_or_seeder(monkeypatch):
    import shopextract._discover as module
    from shopextract.extractors.unified import UnifiedCrawlExtractor
    class Seeder:
        def __init__(self,*args,**kwargs):
            raise AssertionError('A successful native sitemap path must not start the seeder')
    async def browser(*args,**kwargs):
        raise AssertionError('A successful native sitemap path must not start a browser')
    monkeypatch.setattr(module,'AsyncUrlSeeder',Seeder)
    monkeypatch.setattr(module,'_discover_via_crawl4ai',browser)
    monkeypatch.setattr(UnifiedCrawlExtractor,'_extract_with_browser',browser)


@pytest.mark.asyncio
async def test_native_three_product_smoke(no_browser_or_seeder):
    calls=[]
    async with httpx.AsyncClient(transport=httpx.MockTransport(source_handler(4,calls))) as client:
        urls=await discover(SHOP,platform=Platform.GENERIC,max_urls=3,client=client)
    assert urls == [SHOP+f'/item-{i}' for i in range(3)]
    assert SHOP+'/maps/later.xml' not in calls
    assert SHOP+'/health-beauty' not in urls


def test_actual_cli_fifty_products_no_category_crawl(monkeypatch,no_browser_or_seeder,tmp_path):
    calls=[];real=httpx.AsyncClient
    def client(*args,**kwargs):
        kwargs['transport']=httpx.MockTransport(source_handler(51,calls))
        return real(*args,**kwargs)
    monkeypatch.setattr(httpx,'AsyncClient',client)
    # The native CLI performs detection, discovery, extraction and normalization.
    # Browser preflight is an external availability boundary, never an extraction fake.
    monkeypatch.setattr('shopextract._cli_extract._browser_preflight',lambda:None)
    path=tmp_path/'products.json'
    result=CliRunner().invoke(main,['--output-format','json','extract',SHOP,'--max','50',
        '--browser','--timeout','30','--format','json','--output',str(path)])
    assert result.exit_code == 0, result.output
    value=json.loads(path.read_text());data=value['data']
    assert value['ok'] and len(data['products']) == len(data['raw_products']) == 50
    assert data['catalog_complete'] is not True
    assert data['urls_attempted'] == 50
    products=[record['product'] for record in data['products']]
    assert {p['title'] for p in products} == {f'Product {i}' for i in range(50)}
    assert all(p['currency']=='PKR' for p in products)
    assert all(r['_capture']['url'].startswith(SHOP+'/item-') for r in data['raw_products'])
    assert SHOP+'/health-beauty' not in calls and SHOP+'/maps/later.xml' not in calls
    assert sum('/item-' in url for url in calls) == 50
