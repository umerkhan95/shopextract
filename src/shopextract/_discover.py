"""Bounded URL discovery: native API probes and robots-aware HTTP sitemaps.

Default public calls own an isolated worker. Explicit private browser discovery
remains separate from the bounded profile and imports browser dependencies lazily.
"""

from __future__ import annotations

import asyncio
import logging
import time
from urllib.parse import urlparse, urljoin, urlsplit, urlunsplit
from bs4 import BeautifulSoup

import defusedxml.ElementTree as ET
from defusedxml.common import DefusedXmlException
import httpx
from ._filters import PLATFORM_PRODUCT_SITEMAPS, is_non_product_url
from ._models import Platform
from ._execution import browser_allowed, current_state
from ._discovery_sitemaps import discover_sitemap_urls
from ._url_safety import async_client, require_guarded_client

logger = logging.getLogger(__name__)

# Max response size for sitemaps (10MB)
_MAX_RESPONSE_SIZE = 10 * 1024 * 1024

# XML namespace used in standard sitemaps
_SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

# Keywords for BestFirst scorer
PRODUCT_KEYWORDS = [
    "product", "price", "buy", "shop", "item", "cart", "add-to-cart",
    "sku", "inventory", "catalog", "collection",
]


_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


async def discover(url: str, *, platform: Platform | None = None,
                   max_urls: int = 100, timeout: float = 30.0,
                   client: httpx.AsyncClient | None = None) -> list[str]:
    """Bounded public discovery; borrowed transports have cooperative deadlines."""
    from ._discovery_runtime import run_discovery_worker
    if type(max_urls) is not int or not 1 <= max_urls <= 1000 or isinstance(timeout,bool) or not 0 < timeout <= 300:
        raise ValueError('Discovery requires max_urls 1..1000 and positive timeout <=300')
    state=current_state()
    if state is not None:
        timeout=min(timeout,state.deadline-time.monotonic())
        if timeout<=0:
            from ._discovery_runtime import DiscoveryURLs
            return DiscoveryURLs(reasons=['discovery_timeout'])
    if client is not None:
        require_guarded_client(client)
        return await _discover_local(url,platform=platform,max_urls=max_urls,timeout=min(timeout,30),client=client)
    return await run_discovery_worker({'url':url,'platform':platform.value if platform else None,
                                       'max_urls':max_urls,'timeout':min(timeout,30)})


async def _discover_local(url, *, platform=None, max_urls=100, timeout=30, client=None):
    from ._discovery_runtime import DiscoveryClient, DiscoveryURLs
    if client is not None:
        require_guarded_client(client)
    own=client is None
    raw=client or async_client(timeout=timeout,follow_redirects=False)
    guarded=raw if isinstance(raw,DiscoveryClient) else DiscoveryClient(raw)
    async def operation():
        nonlocal platform
        if platform is None:
            from ._detect import detect
            platform=(await detect(url,client=guarded)).platform
        urls=await _discover_for_platform(url,platform,timeout,guarded,max_urls=max_urls)
        allowed=[]
        for item in urls[:5000]:
            if isinstance(item,str) and await guarded.allowed(item):allowed.append(item)
        return sorted(set(allowed))[:max_urls]
    try:
        urls=await asyncio.wait_for(operation(),min(timeout,30))
    except asyncio.TimeoutError:
        guarded.note('discovery_timeout');urls=[]
    except Exception:
        guarded.note('discovery_source_error');urls=[]
    finally:
        if own:await raw.aclose()
    return DiscoveryURLs(urls,reasons=guarded.reasons,request_count=guarded.request_count)


async def _discover_for_platform(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None,
    max_urls: int = 100,
) -> list[str]:
    # The listing is fetched exactly as requested: /airconditioners/ and
    # /airconditioners are different resources on some stores (mega.pk 404s
    # the latter). Store-level endpoints are joined onto the stripped base.
    page_url, base_url = base_url, base_url.rstrip("/")
    if _is_listing_scope(base_url, platform):
        listed = await _discover_category_listing(page_url, timeout, client, max_urls=max_urls)
        if listed is not None:
            return listed
        # The page is not a listing we can read. Platform discovery may still
        # cover the scope (a store mounted under a base path), but only URLs
        # under the requested path are kept: never whole-store products.
        urls = await _discover_for_store(base_url, platform, timeout, client, max_urls=max_urls)
        scoped = [url for url in urls if _under_path(url, base_url)]
        if not scoped:
            _note(client, "category_scope_unavailable")
        return scoped
    return await _discover_for_store(base_url, platform, timeout, client, max_urls=max_urls)


async def _discover_for_store(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None,
    max_urls: int = 100,
) -> list[str]:
    if platform == Platform.SHOPIFY:
        return await _discover_shopify(base_url, platform, timeout, client, max_urls=max_urls)
    elif platform == Platform.WOOCOMMERCE:
        return await _discover_woocommerce(base_url, platform, timeout, client, max_urls=max_urls)
    elif platform == Platform.MAGENTO:
        return await _discover_magento(base_url, platform, timeout, client, max_urls=max_urls)
    elif platform == Platform.BIGCOMMERCE:
        return await _discover_bigcommerce(base_url, platform, timeout, client, max_urls=max_urls)
    else:
        return await _discover_generic(base_url, platform, timeout, client, max_urls=max_urls)


_MAX_CATEGORY_PAGES = 5
_MAX_LISTING_BYTES = 8 * 1024 * 1024


def _is_listing_scope(url: str, platform: Platform) -> bool:
    """A non-root path names a category, search or brand page, not the store.

    Shopify collections keep native /products.json discovery; every other page
    is read itself, because SEO category paths such as /groceries-pets/dairy
    carry no fixed marker.
    """
    from ._scope import is_store_root, shopify_catalog_base
    if is_store_root(url):
        return False
    return platform != Platform.SHOPIFY or shopify_catalog_base(url) is None


def _under_path(url: str, scope_url: str) -> bool:
    scope = urlsplit(scope_url).path.rstrip("/")
    path = urlsplit(url).path
    return path == scope or path.startswith(scope + "/")


def _note(client, code: str) -> None:
    note = getattr(client, "note", None)
    if callable(note):
        note(code)


async def _discover_category_listing(
    category_url: str, timeout: float, client, *, max_urls: int,
) -> list[str] | None:
    """Return product links from a bounded listing and its next pages.

    Returns None when the first page is not a readable listing, so the caller
    can try scoped platform discovery. A product page returns itself.
    """
    from ._discovery_runtime import DiscoveryClient
    from ._listing import parse_listing

    guarded = client if isinstance(client, DiscoveryClient) else DiscoveryClient(client)
    next_url = category_url
    seen_pages: set[str] = set()
    products: list[str] = []
    total = None
    for _ in range(_MAX_CATEGORY_PAGES):
        if not next_url or next_url in seen_pages or not await guarded.allowed(next_url):
            break
        seen_pages.add(next_url)
        try:
            response = await guarded.get(next_url)
        except (httpx.HTTPError, ValueError):
            guarded.note("category_listing_source_error")
            break
        if response.status_code != 200 or len(response.content) > _MAX_LISTING_BYTES:
            guarded.note("category_listing_unavailable")
            # The status decides the cause: a throttled or refused listing is
            # retryable or blocked, not a missing category.
            if response.status_code == 429:
                guarded.note("rate_limited")
            elif response.status_code in (401, 403):
                guarded.note("blocked")
            elif response.status_code != 200:
                guarded.note(f"category_listing_http_{response.status_code}")
            break
        try:
            page = parse_listing(response.text, str(response.url))
        except Exception as error:
            # A theme the parser cannot read must not abort extraction; the
            # reason is kept and the stack names only where it failed.
            from ._failure_origin import failure_origin
            logger.warning("Listing parse failed for %s: %s", next_url, failure_origin(error))
            guarded.note("category_listing_parse_error")
            break
        if not seen_pages - {category_url} and page.is_product_page:
            return [category_url]
        total = page.total if page.total is not None else total
        added = 0
        for candidate in page.product_urls:
            if candidate in products or not await guarded.allowed(candidate):
                continue
            products.append(candidate)
            added += 1
            if len(products) >= max_urls:
                return products
        if not added or (total is not None and len(products) >= total):
            break
        next_url = page.next_url
    if not products:
        return None
    if total is not None and len(products) < min(total, max_urls):
        guarded.note("category_listing_truncated")
    return products


async def _discover_shopify(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None,
    max_urls: int = 100,
) -> list[str]:
    api_url = f"{base_url}/products.json?limit=250&page=1"

    own_client = client is None
    c = client or async_client(timeout=timeout, follow_redirects=True)
    try:
        response = await c.get(api_url)
        response.raise_for_status()
        data = response.json()
        products = data.get("products", [])
        product_count = len(products)

        urls = [f"{base_url}/products.json?limit=250&page=1"]
        if product_count == 250:
            for page in range(2, 11):
                urls.append(f"{base_url}/products.json?limit=250&page={page}")

        return urls
    except Exception as e:
        logger.debug("Shopify /products.json failed for %s: %s, falling back to sitemap", base_url, e)
        return await _discover_via_sitemap(base_url, platform, timeout, client, max_urls=max_urls)
    finally:
        if own_client:
            await c.aclose()


async def _discover_woocommerce(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None,
    max_urls: int = 100,
) -> list[str]:
    api_url = f"{base_url}/wp-json/wc/store/v1/products"

    own_client = client is None
    c = client or async_client(timeout=timeout, follow_redirects=True)
    try:
        response = await c.get(api_url)
        response.raise_for_status()
        return [api_url]
    except Exception as e:
        logger.debug("WooCommerce Store API not available for %s: %s", base_url, e)
    finally:
        if own_client:
            await c.aclose()

    urls = await _discover_via_sitemap(base_url, platform, timeout, client, max_urls=max_urls)
    if urls:
        return _filter_woocommerce_urls(urls)

    client.note('browser_discovery_unassessed')
    return []


async def _discover_magento(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None,
    max_urls: int = 100,
) -> list[str]:
    api_url = f"{base_url}/rest/V1/products?searchCriteria[pageSize]=100"

    own_client = client is None
    c = client or async_client(timeout=timeout, follow_redirects=True)
    try:
        response = await c.get(api_url)
        response.raise_for_status()
        return [api_url]
    except Exception as e:
        logger.debug("Magento REST API not available for %s: %s", base_url, e)
    finally:
        if own_client:
            await c.aclose()

    urls = await _discover_via_sitemap(base_url, platform, timeout, client, max_urls=max_urls)
    if urls:
        return urls

    client.note('browser_discovery_unassessed')
    return []


async def _discover_bigcommerce(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None,
    max_urls: int = 100,
) -> list[str]:
    # Stencil cards identify actual product links, avoiding a browser catalog walk
    # when the storefront token is absent and only a small sample was requested.
    from .extractors._storefront import storefront_client, request
    try:
        async with storefront_client(client, timeout) as c:
            response = await request(c, 'GET', base_url, headers={'User-Agent':_USER_AGENT})
            soup = BeautifulSoup(response.text, 'html.parser')
            domain = urlparse(str(response.url)).netloc
            cards = []
            for anchor in soup.select('.card-title a[href]'):
                url = urljoin(str(response.url), anchor['href']).split('#', 1)[0]
                if urlparse(url).netloc == domain and not is_non_product_url(url) and url not in cards:
                    cards.append(url)
                    if len(cards) >= max_urls:
                        break
            if cards:
                return cards
    except Exception as e:
        logger.debug('BigCommerce public card discovery unavailable: %s', type(e).__name__)
    urls = await _discover_via_sitemap(base_url, platform, timeout, client, max_urls=max_urls)
    if urls:
        return urls
    client.note('browser_discovery_unassessed')
    return []


async def _discover_generic(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None,
    max_urls: int = 100,
) -> list[str]:
    urls = await _discover_via_sitemap(base_url, platform, timeout, client, max_urls=max_urls)
    if urls:
        return urls

    client.note('browser_discovery_unassessed')
    return []


# -- Sitemap discovery -------------------------------------------------------

async def _discover_via_sitemap(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None,
    max_urls: int = 100,
) -> list[str]:
    from ._discovery_runtime import DiscoveryClient, bounded_sitemaps
    own=client is None
    raw=client or async_client(timeout=timeout,follow_redirects=False)
    guarded=raw if isinstance(raw,DiscoveryClient) else DiscoveryClient(raw)
    try:
        native=await discover_sitemap_urls(base_url,max_urls=max_urls,timeout=timeout,client=guarded)
        if native.stop_fallback:
            guarded.note(native.stop_reason or 'native_sitemap_incomplete')
        if native.urls:return list(native.urls)
        if native.stop_fallback:return []
        return await bounded_sitemaps(base_url,platform,guarded,max_urls=max_urls)
    finally:
        if own:await raw.aclose()


async def _try_product_sitemaps(
    base_url: str, paths: list[str], timeout: float, client: httpx.AsyncClient | None
) -> list[str]:
    urls: list[str] = []
    own_client = client is None
    c = client or async_client(timeout=timeout, follow_redirects=True)
    try:
        for path in paths:
            sitemap_url = f"{base_url}{path}"
            try:
                resp = await c.get(sitemap_url)
                if resp.status_code != 200:
                    continue
                content_length = int(resp.headers.get("content-length", 0))
                if content_length > _MAX_RESPONSE_SIZE:
                    continue
                xml_text = resp.text
                if len(xml_text) > _MAX_RESPONSE_SIZE:
                    continue
                parsed_urls = _parse_sitemap_xml(xml_text)
                if parsed_urls:
                    urls.extend(parsed_urls)
            except Exception as e:
                logger.debug("Failed to fetch %s: %s", sitemap_url, e)
    finally:
        if own_client:
            await c.aclose()
    return urls


def _parse_sitemap_xml(xml_text: str) -> list[str]:
    try:
        root = ET.fromstring(xml_text)
    except (DefusedXmlException, ET.ParseError) as e:
        logger.debug("Failed to parse sitemap XML: %s", e)
        return []

    urls: list[str] = []
    if root.tag.endswith("sitemapindex"):
        return []

    loc_elements = root.findall(".//sm:url/sm:loc", _SITEMAP_NS)
    if not loc_elements:
        loc_elements = root.findall(".//url/loc")
    for loc in loc_elements:
        if loc.text:
            urls.append(loc.text.strip())
    return urls


def _filter_woocommerce_urls(urls: list[str]) -> list[str]:
    product_urls = [u for u in urls if "/product/" in u.lower()]
    if len(product_urls) >= len(urls) * 0.3:
        return product_urls
    return urls


# -- Browser-based discovery -------------------------------------------------

async def _discover_via_crawl4ai(base_url: str, max_pages: int = 100) -> list[str]:
    from crawl4ai import AsyncWebCrawler, CacheMode
    from crawl4ai.deep_crawling import BestFirstCrawlingStrategy, DomainFilter, FilterChain, URLPatternFilter
    from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
    from .extractors._browser import StealthLevel, get_browser_config, get_crawl_config, get_crawler_strategy
    from ._url_safety import ValidatingProxy, operator_allows_private_urls, validate_url_target
    try:
        from crawl4ai.deep_crawling import ContentTypeFilter
        _HAS_CONTENT_TYPE_FILTER=True
    except ImportError:
        _HAS_CONTENT_TYPE_FILTER=False
    if not browser_allowed():
        return []
    await validate_url_target(base_url, allow_private=operator_allows_private_urls())
    parsed = urlparse(base_url)
    domain = parsed.netloc

    filters = [
        DomainFilter(allowed_domains=[domain]),
        URLPatternFilter(
            patterns=[
                "*/cart*", "*/checkout*", "*/account*", "*/login*",
                "*/register*", "*/search*", "*/blog/*", "*/faq*",
                "*/privacy*", "*/terms*", "*/sitemap*", "*/basket*",
                "*/help*", "*/support*", "*/careers*", "*/press*",
                "*/wishlist*", "*/compare*",
            ],
            reverse=True,
        ),
    ]
    if _HAS_CONTENT_TYPE_FILTER:
        filters.append(ContentTypeFilter(
            allowed_types=["text/html", "application/xhtml+xml"],
        ))
    filter_chain = FilterChain(filters)

    scorer = KeywordRelevanceScorer(keywords=PRODUCT_KEYWORDS, weight=0.7)

    strategy = BestFirstCrawlingStrategy(
        max_depth=3,
        max_pages=max_pages,
        filter_chain=filter_chain,
        url_scorer=scorer,
        include_external=False,
    )

    stealth_level = StealthLevel.STANDARD
    found_urls: set[str] = set()
    try:
        async with ValidatingProxy() as proxy:
            browser_config = get_browser_config(stealth_level)
            crawl_config = get_crawl_config(
                stealth_level=stealth_level,
                deep_crawl_strategy=strategy,
                wait_until="domcontentloaded",
                wait_for=None,
                proxy_config=proxy.crawl4ai_config,
            )
            crawl_config.cache_mode = CacheMode.ENABLED
            crawl_config.only_text = True
            crawler_strategy = get_crawler_strategy(stealth_level, browser_config)
            async with AsyncWebCrawler(
                config=browser_config,
                crawler_strategy=crawler_strategy,
            ) as crawler:
                results = await crawler.arun(url=base_url, config=crawl_config)
                if isinstance(results, list):
                    for result in results:
                        if result.success and not is_non_product_url(result.url):
                            found_urls.add(result.url)
                elif hasattr(results, "success") and results.success:
                    if not is_non_product_url(results.url):
                        found_urls.add(results.url)
    except Exception as e:
        logger.error("Deep crawl discovery failed for %s: %s", base_url, e)

    if found_urls:
        logger.info("BestFirst crawl discovered %d candidate product URLs", len(found_urls))

    return list(found_urls)
