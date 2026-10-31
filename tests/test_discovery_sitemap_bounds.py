"""Bounded adversarial checks for the production native sitemap walker.

All HTTP is controlled MockTransport; parsing, policy decisions, limits, and
discovery remain the production implementation.
"""
import asyncio
import gzip
from functools import wraps
import random

import httpx
import pytest

import shopextract._discovery_sitemaps as native
from shopextract._discover import discover
from shopextract._models import Platform


BASE = 'https://merchant.test/shop'
ORIGIN = 'https://merchant.test'


def async_test(function):
    """Keep this bounded suite runnable even if pytest-asyncio is unavailable."""
    @wraps(function)
    def run(*args, **kwargs):
        return asyncio.run(function(*args, **kwargs))
    return run


def index(*urls):
    return '<sitemapindex>' + ''.join(f'<sitemap><loc>{u}</loc></sitemap>' for u in urls) + '</sitemapindex>'


def urlset(*urls, extra=''):
    return '<urlset>' + ''.join(f'<url><loc>{u}</loc>{extra}</url>' for u in urls) + '</urlset>'


def robots(*sitemaps, rules='Allow: /'):
    return 'User-agent: *\n' + rules + '\n' + ''.join(f'Sitemap: {u}\n' for u in sitemaps)


async def resolve(routes, *, base=BASE, max_urls=50, timeout=5, client=None):
    calls = []

    def handle(request):
        calls.append(str(request.url))
        value = routes(request)
        return value

    owned = client is None
    client = client or httpx.AsyncClient(transport=httpx.MockTransport(handle), follow_redirects=False)
    if not owned:
        # Caller-supplied clients keep their own transport; the route closure
        # already owns call accounting via the supplied MockTransport.
        calls = None
    try:
        result = await native.discover_sitemap_urls(base, max_urls=max_urls, timeout=timeout, client=client)
        return result, calls
    finally:
        if owned:
            await client.aclose()


@pytest.mark.parametrize(('cap','n'), [(1, 1), (50, 50), (51, 51), (0, 0)])
@async_test
async def test_requested_caps_bound_returned_and_fetched_products(cap, n):
    calls = []
    candidates = [BASE + f'/item/{i}' for i in range(60)]

    def route(req):
        calls.append(req.url.path)
        if req.url.path == '/robots.txt':
            return httpx.Response(200, text=robots(ORIGIN + '/maps/products.xml'))
        if req.url.path == '/maps/products.xml':
            return httpx.Response(200, text=urlset(*candidates))
        return httpx.Response(200, text='page')

    async with httpx.AsyncClient(transport=httpx.MockTransport(route)) as client:
        result = await native.discover_sitemap_urls(BASE, max_urls=cap, client=client)
    assert len(result.urls) == n
    assert calls.count('/maps/products.xml') == (0 if cap == 0 else 1)
    # Product URLs are returned, not fetched during discovery. Only the single
    # advertised source request should occur, with no second leaf enumeration.
    assert len(calls) == (0 if cap == 0 else 2)


@async_test
async def test_cycle_duplicates_fragment_category_and_image_locations_are_suppressed():
    calls = []
    def route(req):
        calls.append(req.url.path)
        if req.url.path == '/robots.txt':
            return httpx.Response(200, text=robots(ORIGIN+'/a/index.xml', ORIGIN+'/maps/sitemap_categories.xml'))
        if req.url.path == '/a/index.xml':
            return httpx.Response(200, text=index(ORIGIN+'/a/index.xml', ORIGIN+'/maps/leaf.xml', ORIGIN+'/maps/leaf.xml'))
        if req.url.path == '/maps/sitemap_categories.xml':
            return httpx.Response(200, text=urlset(BASE+'/category'))
        if req.url.path == '/maps/leaf.xml':
            return httpx.Response(200, text=urlset(BASE+'/item#one', BASE+'/item#two', extra='<image><loc>https://cdn.test/i.jpg</loc></image>'))
        return httpx.Response(404)
    async with httpx.AsyncClient(transport=httpx.MockTransport(route)) as client:
        result = await native.discover_sitemap_urls(BASE, max_urls=10, client=client)
    assert result.urls == (BASE+'/item',)
    assert calls.count('/a/index.xml') == calls.count('/maps/leaf.xml') == 1
    assert BASE+'/category' not in result.urls


@async_test
async def test_foreign_pathprefix_collision_and_encoded_traversal_are_rejected():
    def route(req):
        if req.url.path == '/robots.txt': return httpx.Response(200, text=robots(ORIGIN+'/maps/list.xml'))
        if req.url.path == '/maps/list.xml':
            return httpx.Response(200, text=urlset('https://merchant.test/shopper/escape', BASE+'/../outside', BASE+'/%252e%252e/outside', 'https://other.test/shop/item'))
        return httpx.Response(404)
    async with httpx.AsyncClient(transport=httpx.MockTransport(route)) as client:
        result = await native.discover_sitemap_urls(BASE, client=client)
    assert result.urls == ()


@async_test
async def test_category_map_first_is_excluded_before_valid_product_map():
    calls = []
    def route(req):
        calls.append(req.url.path)
        if req.url.path == '/robots.txt':
            return httpx.Response(200, text=robots(ORIGIN+'/maps/sitemap_products.xml', ORIGIN+'/maps/sitemap_category.xml'))
        if req.url.path.endswith('sitemap_category.xml'):
            return httpx.Response(200, text=urlset(BASE+'/category/product-like-name'))
        if req.url.path.endswith('sitemap_products.xml'):
            return httpx.Response(200, text=urlset(BASE+'/item/real'))
        return httpx.Response(404)
    async with httpx.AsyncClient(transport=httpx.MockTransport(route)) as client:
        result = await native.discover_sitemap_urls(BASE, client=client)
    assert result.urls == (BASE+'/item/real',)
    assert calls.index('/maps/sitemap_category.xml') < calls.index('/maps/sitemap_products.xml')


@async_test
async def test_robots_denied_map_is_skipped_but_allowed_map_candidates_survive():
    calls = []
    def route(req):
        calls.append(req.url.path)
        if req.url.path == '/robots.txt': return httpx.Response(200, text=robots(ORIGIN+'/maps/private.xml', ORIGIN+'/maps/public.xml', rules='Disallow: /maps/private.xml'))
        if req.url.path == '/maps/public.xml': return httpx.Response(200, text=urlset(BASE+'/item/allowed'))
        return httpx.Response(200, text=urlset(BASE+'/item/forbidden'))
    async with httpx.AsyncClient(transport=httpx.MockTransport(route)) as client:
        result = await native.discover_sitemap_urls(BASE, client=client)
    assert result.urls == (BASE+'/item/allowed',)
    assert '/maps/private.xml' not in calls


@async_test
async def test_candidate_only_robots_denial_stops_legacy_fallback(monkeypatch):
    calls=[]
    def route(req):
        calls.append(req.url.path)
        if req.url.path == '/robots.txt': return httpx.Response(200, text=robots(ORIGIN+'/maps/products.xml', rules='Disallow: /shop/item'))
        if req.url.path == '/maps/products.xml': return httpx.Response(200, text=urlset(BASE+'/item/blocked'))
        return httpx.Response(404)
    import shopextract._discover as legacy
    async def forbidden(*a, **k): raise AssertionError('denied source must not fall through to browser crawl')
    monkeypatch.setattr(legacy, '_discover_via_crawl4ai', forbidden)
    monkeypatch.setattr(legacy, 'AsyncUrlSeeder', lambda *a, **k: (_ for _ in ()).throw(AssertionError('denied source must not seed')))
    async with httpx.AsyncClient(transport=httpx.MockTransport(route)) as client:
        urls = await discover(BASE, platform=Platform.GENERIC, client=client)
    assert urls == []
    assert '/shop/item/blocked' not in calls


@async_test
async def test_robots_longest_matching_disallow_overrides_allow():
    """RFC robots specificity: a longer Disallow beats a broad Allow."""
    def route(req):
        if req.url.path == '/robots.txt':
            return httpx.Response(200,text=robots(ORIGIN+'/maps/products.xml',rules='Allow: /\nDisallow: /shop/item'))
        if req.url.path == '/maps/products.xml': return httpx.Response(200,text=urlset(BASE+'/item/blocked'))
        return httpx.Response(404)
    async with httpx.AsyncClient(transport=httpx.MockTransport(route)) as client:
        result=await native.discover_sitemap_urls(BASE,client=client)
    assert result.urls == () and result.stop_fallback


@pytest.mark.parametrize('rules', [
    'Disallow: /shop/item\nAllow: /shop/item/allowed',
    'Disallow: /shop/item/allowed\nAllow: /shop/item/allowed',
])
@async_test
async def test_robots_specific_allow_exception_and_equal_tie(rules):
    """A narrow exception and an equal Allow must not suppress valid products."""
    def route(req):
        if req.url.path == '/robots.txt':
            return httpx.Response(200, text=robots(ORIGIN+'/maps/products.xml', rules=rules))
        return httpx.Response(200, text=urlset(BASE+'/item/allowed'))
    async with httpx.AsyncClient(transport=httpx.MockTransport(route)) as client:
        result = await native.discover_sitemap_urls(BASE, client=client)
    assert result.urls == (BASE+'/item/allowed',)


@async_test
async def test_store_root_denial_stops_browser_and_seeder(monkeypatch):
    import shopextract._discover as legacy
    async def forbidden(*a, **k): raise AssertionError('store denial must block fallback')
    monkeypatch.setattr(legacy, '_discover_via_crawl4ai', forbidden)
    monkeypatch.setattr(legacy, 'AsyncUrlSeeder', lambda *a, **k: (_ for _ in ()).throw(AssertionError('store denial must block seeder')))
    async with httpx.AsyncClient(transport=httpx.MockTransport(lambda req: httpx.Response(200, text='User-agent: *\nDisallow: /shop/'))) as client:
        urls = await discover(BASE, platform=Platform.GENERIC, client=client)
    assert urls == []


@async_test
async def test_redirect_hops_count_against_request_cap(monkeypatch):
    calls=[]
    monkeypatch.setattr(native, 'MAX_REQUESTS', 3)
    def route(req):
        calls.append(req.url.path)
        if req.url.path == '/robots.txt': return httpx.Response(200, text=robots(ORIGIN+'/maps/a.xml'))
        if req.url.path == '/maps/a.xml': return httpx.Response(302, headers={'location':'/maps/b.xml'})
        if req.url.path == '/maps/b.xml': return httpx.Response(302, headers={'location':'/maps/c.xml'})
        return httpx.Response(200, text=urlset(BASE+'/item'))
    async with httpx.AsyncClient(transport=httpx.MockTransport(route)) as client:
        result = await native.discover_sitemap_urls(BASE, client=client)
    assert len(calls) == 3 and result.urls == ()


@pytest.mark.parametrize(('limit','size','expected'), [(5,5,1),(4,5,0)])
@async_test
async def test_decoded_single_response_byte_limit(limit,size,expected,monkeypatch):
    body=urlset(BASE+'/item')
    # Keep robots below both limits; the sitemap body lands exactly at the
    # limit or one byte above it, exercising the inclusive boundary.
    limit = len(body) if expected else len(body) - 1
    monkeypatch.setattr(native, 'MAX_RESPONSE_BYTES', limit)
    monkeypatch.setattr(native, 'MAX_TOTAL_BYTES', 100)
    # A response stream is decoded by httpx before the walker counts bytes.
    def route(req):
        if req.url.path == '/robots.txt': return httpx.Response(200, text='User-agent: *\nAllow: /')
        if req.url.path == '/sitemap.xml': return httpx.Response(200, content=gzip.compress(body.encode()), headers={'content-encoding':'gzip'})
        return httpx.Response(200, text=body)
    async with httpx.AsyncClient(transport=httpx.MockTransport(route)) as client:
        result=await native.discover_sitemap_urls(BASE,client=client)
    assert len(result.urls)==expected


@async_test
async def test_aggregate_byte_cap_stops_at_boundary(monkeypatch):
    monkeypatch.setattr(native,'MAX_RESPONSE_BYTES',1000)
    robots_body=robots(ORIGIN+'/maps/a.xml',ORIGIN+'/maps/b.xml')
    first=urlset(BASE+'/item/first')
    second=urlset(BASE+'/item/second')
    monkeypatch.setattr(native,'MAX_TOTAL_BYTES',len(robots_body.encode())+len(first.encode())+len(second.encode())-1)
    def route(req):
        if req.url.path == '/robots.txt': return httpx.Response(200,text=robots_body)
        if req.url.path == '/maps/a.xml': return httpx.Response(200,text=first)
        if req.url.path == '/maps/b.xml': return httpx.Response(200,text=second)
        return httpx.Response(404)
    async with httpx.AsyncClient(transport=httpx.MockTransport(route)) as client:
        result=await native.discover_sitemap_urls(BASE,client=client)
    assert result.urls == (BASE+'/item/first',) and result.stop_fallback


@async_test
async def test_global_deadline_covers_slow_body(monkeypatch):
    monkeypatch.setattr(native,'MAX_SECONDS',0.03)
    # MockTransport returns a prebuilt response; inject the slow stream on the
    # sitemap response so timeout covers body iteration as well as headers.
    class Slow(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'<urlset>'
            await asyncio.sleep(0.2)
            yield b'</urlset>'
        async def aclose(self): pass
    def handler(req):
        if req.url.path == '/robots.txt': return httpx.Response(200,text=robots(ORIGIN+'/maps/slow.xml'))
        return httpx.Response(200,stream=Slow())
    async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
        with pytest.raises(asyncio.TimeoutError): await native.discover_sitemap_urls(BASE,client=client,timeout=1)


@async_test
async def test_cancellation_closes_owned_client_but_preserves_supplied_client(monkeypatch):
    created=[]
    real=httpx.AsyncClient
    class Tracked(real):
        def __init__(self,*a,**kw):
            kw.setdefault('transport', transport)
            super().__init__(*a,**kw); created.append(self)
    monkeypatch.setattr(native.httpx,'AsyncClient',Tracked)
    class Blocking(httpx.AsyncByteStream):
        async def __aiter__(self):
            yield b'User-agent: *\nSitemap: https://merchant.test/maps/a.xml\n'
            await asyncio.Event().wait()
        async def aclose(self): pass
    # The robots body itself blocks, making cancellation occur during streaming.
    transport=httpx.MockTransport(lambda req: httpx.Response(200,stream=Blocking()))
    task=asyncio.create_task(native.discover_sitemap_urls(BASE,timeout=5))
    await asyncio.sleep(0.02); task.cancel()
    with pytest.raises(asyncio.CancelledError): await task
    assert len(created)==1 and created[0].is_closed
    provided=Tracked(transport=transport)
    task=asyncio.create_task(native.discover_sitemap_urls(BASE,timeout=5,client=provided))
    await asyncio.sleep(0.02); task.cancel()
    with pytest.raises(asyncio.CancelledError): await task
    assert not provided.is_closed
    await provided.aclose()


@async_test
async def test_malformed_xml_and_dtd_are_rejected_then_legacy_fallback_remains(monkeypatch):
    calls=[]
    def route(req):
        calls.append(req.url.path)
        if req.url.path == '/robots.txt': return httpx.Response(200,text=robots(ORIGIN+'/maps/bad.xml'))
        if req.url.path == '/maps/bad.xml': return httpx.Response(200,text='<!DOCTYPE x [<!ENTITY e "boom">]><urlset>&e;</urlset>')
        return httpx.Response(404)
    import shopextract._discover as legacy
    class Seeder:
        async def __aenter__(self): return self
        async def __aexit__(self,*a): pass
        async def urls(self,domain,config): return [{'url':BASE+'/legacy-item','status':'valid'}]
    monkeypatch.setattr(legacy,'AsyncUrlSeeder',Seeder)
    monkeypatch.setattr(legacy,'_discover_via_crawl4ai',lambda *a,**k: asyncio.sleep(0,result=[]))
    async with httpx.AsyncClient(transport=httpx.MockTransport(route)) as client:
        urls=await discover(BASE,platform=Platform.GENERIC,client=client)
    assert urls == [BASE+'/legacy-item']
    assert '/maps/bad.xml' in calls


@async_test
async def test_seeded_5000_candidate_leaf_returns_exact_fifty_without_extra_http():
    rng=random.Random(0)
    numbers=list(range(5000)); rng.shuffle(numbers)
    candidates=[BASE+f'/item/{n}' for n in numbers]
    calls=[]
    def route(req):
        calls.append(req.url.path)
        if req.url.path == '/robots.txt': return httpx.Response(200,text=robots(ORIGIN+'/maps/large.xml'))
        if req.url.path == '/maps/large.xml': return httpx.Response(200,text=urlset(*candidates))
        return httpx.Response(404)
    async with httpx.AsyncClient(transport=httpx.MockTransport(route)) as client:
        result=await native.discover_sitemap_urls(BASE,max_urls=50,client=client)
    assert len(result.urls)==50 and result.urls==tuple(candidates[:50])
    assert len(calls)==2 and calls.count('/maps/large.xml')==1
