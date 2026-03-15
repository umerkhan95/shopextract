"""URL discovery for e-commerce stores.

Uses platform-specific product sitemaps, crawl4ai AsyncUrlSeeder for generic
sitemap discovery, and BestFirstCrawlingStrategy for browser-based link
discovery when API and sitemap strategies fail.
"""

from __future__ import annotations

import asyncio
import logging
from urllib.parse import urlparse

import defusedxml.ElementTree as ET
from defusedxml.common import DefusedXmlException
import httpx
from crawl4ai import AsyncUrlSeeder, AsyncWebCrawler, CacheMode, SeedingConfig
from crawl4ai.deep_crawling import (
    BestFirstCrawlingStrategy,
    DomainFilter,
    FilterChain,
    URLPatternFilter,
)
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer

try:
    from crawl4ai.deep_crawling import ContentTypeFilter
    _HAS_CONTENT_TYPE_FILTER = True
except ImportError:
    _HAS_CONTENT_TYPE_FILTER = False

from ._filters import PLATFORM_PRODUCT_SITEMAPS, is_non_product_url
from ._models import Platform
from .extractors._browser import (
    StealthLevel,
    get_browser_config,
    get_crawl_config,
    get_crawler_strategy,
)

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

# Overall discovery timeout (5 minutes)
_DISCOVERY_TIMEOUT = 300

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


async def discover(
    url: str,
    *,
    platform: Platform | None = None,
    max_urls: int = 100,
    timeout: float = 30.0,
    client: httpx.AsyncClient | None = None,
) -> list[str]:
    """Discover product URLs for the given store.

    Args:
        url: The merchant's website URL.
        platform: Detected platform (auto-detected if None).
        max_urls: Maximum URLs to return.
        timeout: HTTP request timeout in seconds.
        client: Optional shared httpx.AsyncClient.

    Returns:
        List of discovered product URLs.
    """
    if platform is None:
        from ._detect import detect as detect_platform
        result = await detect_platform(url, client=client)
        platform = result.platform

    base_url = url.rstrip("/")
    logger.info("Discovering URLs for %s (platform: %s)", base_url, platform)

    try:
        coro = _discover_for_platform(base_url, platform, timeout, client)
        urls = await asyncio.wait_for(coro, timeout=_DISCOVERY_TIMEOUT)
    except asyncio.TimeoutError:
        logger.error("URL discovery timed out after %ds for %s", _DISCOVERY_TIMEOUT, base_url)
        return []
    except Exception as e:
        logger.error("Error discovering URLs for %s: %s", base_url, e)
        return []

    if max_urls and len(urls) > max_urls:
        urls = urls[:max_urls]

    return urls


async def _discover_for_platform(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None
) -> list[str]:
    if platform == Platform.SHOPIFY:
        return await _discover_shopify(base_url, platform, timeout, client)
    elif platform == Platform.WOOCOMMERCE:
        return await _discover_woocommerce(base_url, platform, timeout, client)
    elif platform == Platform.MAGENTO:
        return await _discover_magento(base_url, platform, timeout, client)
    elif platform == Platform.BIGCOMMERCE:
        return await _discover_bigcommerce(base_url, platform, timeout, client)
    else:
        return await _discover_generic(base_url, platform, timeout, client)


async def _discover_shopify(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None
) -> list[str]:
    api_url = f"{base_url}/products.json?limit=250&page=1"

    own_client = client is None
    c = client or httpx.AsyncClient(timeout=timeout, follow_redirects=True)
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
    except Exception:
        return await _discover_via_sitemap(base_url, platform, timeout, client)
    finally:
        if own_client:
            await c.aclose()


async def _discover_woocommerce(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None
) -> list[str]:
    api_url = f"{base_url}/wp-json/wc/store/v1/products"

    own_client = client is None
    c = client or httpx.AsyncClient(timeout=timeout, follow_redirects=True)
    try:
        response = await c.get(api_url)
        response.raise_for_status()
        return [api_url]
    except Exception:
        pass
    finally:
        if own_client:
            await c.aclose()

    urls = await _discover_via_sitemap(base_url, platform, timeout, client)
    if urls:
        return _filter_woocommerce_urls(urls)

    return await _discover_via_crawl4ai(base_url)


async def _discover_magento(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None
) -> list[str]:
    api_url = f"{base_url}/rest/V1/products?searchCriteria[pageSize]=100"

    own_client = client is None
    c = client or httpx.AsyncClient(timeout=timeout, follow_redirects=True)
    try:
        response = await c.get(api_url)
        response.raise_for_status()
        return [api_url]
    except Exception:
        pass
    finally:
        if own_client:
            await c.aclose()

    urls = await _discover_via_sitemap(base_url, platform, timeout, client)
    if urls:
        return urls

    return await _discover_via_crawl4ai(base_url)


async def _discover_bigcommerce(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None
) -> list[str]:
    urls = await _discover_via_sitemap(base_url, platform, timeout, client)
    if urls:
        return urls
    return await _discover_via_crawl4ai(base_url)


async def _discover_generic(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None
) -> list[str]:
    urls = await _discover_via_sitemap(base_url, platform, timeout, client)
    if urls:
        return urls

    urls = await _discover_via_crawl4ai(base_url)
    if urls:
        return urls

    return [base_url]


# -- Sitemap discovery -------------------------------------------------------

async def _discover_via_sitemap(
    base_url: str, platform: Platform, timeout: float, client: httpx.AsyncClient | None
) -> list[str]:
    base_url = base_url.rstrip("/")
    domain = urlparse(base_url).netloc

    # Phase 1: platform-specific product sitemaps
    product_sitemap_paths = PLATFORM_PRODUCT_SITEMAPS.get(platform.value, [])
    if product_sitemap_paths:
        product_urls = await _try_product_sitemaps(base_url, product_sitemap_paths, timeout, client)
        if product_urls:
            filtered = [u for u in product_urls if not is_non_product_url(u)]
            logger.info(
                "Product sitemaps yielded %d URLs (%d after filtering)",
                len(product_urls), len(filtered),
            )
            return filtered

    # Phase 2: generic sitemap via AsyncUrlSeeder
    config = SeedingConfig(
        source="sitemap",
        pattern="*",
        filter_nonsense_urls=True,
        max_urls=5000,
        force=False,
    )
    urls: list[str] = []
    try:
        async with AsyncUrlSeeder() as seeder:
            results = await seeder.urls(domain, config)
        urls = [r["url"] for r in results if r.get("status") != "not_valid"]
    except Exception as e:
        logger.warning("AsyncUrlSeeder failed for %s: %s", domain, e)

    # Phase 3: denylist filter
    filtered = [u for u in urls if not is_non_product_url(u)]
    if filtered:
        logger.info("Sitemap discovery: %d URLs, %d after filtering", len(urls), len(filtered))
    return filtered


async def _try_product_sitemaps(
    base_url: str, paths: list[str], timeout: float, client: httpx.AsyncClient | None
) -> list[str]:
    urls: list[str] = []
    own_client = client is None
    c = client or httpx.AsyncClient(timeout=timeout, follow_redirects=True)
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
    except (DefusedXmlException, ET.ParseError):
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
    browser_config = get_browser_config(stealth_level)
    crawl_config = get_crawl_config(
        stealth_level=stealth_level,
        deep_crawl_strategy=strategy,
        wait_until="domcontentloaded",
        wait_for=None,
    )
    crawl_config.cache_mode = CacheMode.ENABLED
    crawl_config.only_text = True

    found_urls: set[str] = set()
    try:
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
