"""Platform detection for e-commerce stores.

Detects platform using multiple strategies:
1. HTTP header probes (fastest)
2. API endpoint probes
3. HTML meta tag analysis
4. CDN/script source analysis
"""

from __future__ import annotations

import asyncio
import logging
import re
import time

import httpx

from ._models import Platform, PlatformResult

logger = logging.getLogger(__name__)

# Detection timeouts
PROBE_TIMEOUT = 10.0
TOTAL_TIMEOUT = 30.0

# Max response size for HTML probe (10MB)
_MAX_RESPONSE_SIZE = 10 * 1024 * 1024

# Max possible signals for confidence calculation
_MAX_SIGNALS = {
    Platform.SHOPIFY: 4,
    Platform.WOOCOMMERCE: 4,
    Platform.MAGENTO: 3,
    Platform.BIGCOMMERCE: 3,
    Platform.SHOPWARE: 4,
    Platform.GENERIC: 1,
}

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


async def _run_all_probes(client, url, signals):
    await _probe_headers(client, url, signals)
    await _probe_api_endpoints(client, url, signals)
    await _probe_html_content(client, url, signals)


async def detect(url: str, *, client: httpx.AsyncClient | None = None) -> PlatformResult:
    """Detect the e-commerce platform for the given URL.

    Args:
        url: The merchant's website URL.
        client: Optional shared httpx.AsyncClient.

    Returns:
        PlatformResult with detected platform, confidence score, and signals.
    """
    start_time = time.time()
    logger.info("Starting platform detection for %s", url)

    signals: dict[Platform, list[str]] = {
        Platform.SHOPIFY: [],
        Platform.WOOCOMMERCE: [],
        Platform.MAGENTO: [],
        Platform.BIGCOMMERCE: [],
        Platform.SHOPWARE: [],
    }

    own_client = client is None
    if own_client:
        client = httpx.AsyncClient(
            timeout=httpx.Timeout(PROBE_TIMEOUT),
            follow_redirects=True,
            headers={"User-Agent": _USER_AGENT},
        )

    try:
        await asyncio.wait_for(
            _run_all_probes(client, url, signals),
            timeout=TOTAL_TIMEOUT,
        )
    except asyncio.TimeoutError:
        logger.warning("Platform detection timed out after %ss for %s", TOTAL_TIMEOUT, url)
    except Exception as e:
        logger.error("Error during platform detection for %s: %s", url, e)
    finally:
        if own_client:
            await client.aclose()

    platform, platform_signals = _determine_platform(signals)
    max_sigs = _MAX_SIGNALS.get(platform, 1)
    confidence = min(len(platform_signals) / max_sigs, 1.0)

    elapsed = time.time() - start_time
    logger.info(
        "Platform detection complete for %s: %s (confidence: %.2f, signals: %d, time: %.2fs)",
        url, platform, confidence, len(platform_signals), elapsed,
    )

    return PlatformResult(platform=platform, confidence=confidence, signals=platform_signals)


# -- Header probes -----------------------------------------------------------

async def _probe_headers(
    client: httpx.AsyncClient, url: str, signals: dict[Platform, list[str]]
) -> None:
    try:
        response = await client.head(url)
        headers = response.headers

        if "x-shopid" in headers or "x-shopify-stage" in headers:
            signals[Platform.SHOPIFY].append("header:x-shopify")

        if any(key.lower().startswith("x-magento") for key in headers):
            signals[Platform.MAGENTO].append("header:x-magento")

        link_header = headers.get("link", "")
        if "wp-json" in link_header.lower() and "api.w.org" in link_header.lower():
            signals[Platform.WOOCOMMERCE].append("header:wp-json-link")

        headers_lower = {k.lower(): v for k, v in headers.items()}
        if "sw-version-id" in headers_lower or "sw-context-token" in headers_lower:
            signals[Platform.SHOPWARE].append("header:shopware")

    except Exception as e:
        logger.debug("Header probe failed for %s: %s", url, e)


# -- API endpoint probes -----------------------------------------------------

async def _probe_api_endpoints(
    client: httpx.AsyncClient, url: str, signals: dict[Platform, list[str]]
) -> None:
    base_url = url.rstrip("/")
    await asyncio.gather(
        _probe_shopify_api(client, base_url, signals),
        _probe_woocommerce_api(client, base_url, signals),
        _probe_magento_api(client, base_url, signals),
        _probe_shopware_api(client, base_url, signals),
        return_exceptions=True,
    )


async def _probe_shopify_api(
    client: httpx.AsyncClient, base_url: str, signals: dict[Platform, list[str]]
) -> None:
    try:
        response = await client.get(f"{base_url}/products.json", timeout=PROBE_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if "products" in data:
                signals[Platform.SHOPIFY].append("api:/products.json")
    except Exception as e:
        logger.debug("Shopify API probe failed for %s: %s", base_url, e)


async def _probe_woocommerce_api(
    client: httpx.AsyncClient, base_url: str, signals: dict[Platform, list[str]]
) -> None:
    try:
        response = await client.get(f"{base_url}/wp-json/", timeout=PROBE_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if "namespaces" in data:
                signals[Platform.WOOCOMMERCE].append("api:/wp-json/")
    except Exception as e:
        logger.debug("WooCommerce API probe failed for %s: %s", base_url, e)


async def _probe_magento_api(
    client: httpx.AsyncClient, base_url: str, signals: dict[Platform, list[str]]
) -> None:
    try:
        response = await client.get(f"{base_url}/rest/V1/store/storeConfigs", timeout=PROBE_TIMEOUT)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                signals[Platform.MAGENTO].append("api:/rest/V1/store/storeConfigs")
    except Exception as e:
        logger.debug("Magento API probe failed for %s: %s", base_url, e)


async def _probe_shopware_api(
    client: httpx.AsyncClient, base_url: str, signals: dict[Platform, list[str]]
) -> None:
    try:
        response = await client.get(f"{base_url}/api/_info/config", timeout=PROBE_TIMEOUT)
        if response.status_code == 200:
            signals[Platform.SHOPWARE].append("api:/api/_info/config")
    except Exception as e:
        logger.debug("Shopware API probe failed for %s: %s", base_url, e)


# -- HTML content probes -----------------------------------------------------

async def _probe_html_content(
    client: httpx.AsyncClient, url: str, signals: dict[Platform, list[str]]
) -> None:
    try:
        response = await client.get(url, timeout=PROBE_TIMEOUT)
        if response.status_code != 200:
            return

        content_length = int(response.headers.get("content-length", 0))
        if content_length > _MAX_RESPONSE_SIZE:
            return

        raw_html = response.text
        if len(raw_html) > _MAX_RESPONSE_SIZE:
            return

        html = raw_html.lower()
        _analyze_meta_tags(html, signals)
        _analyze_cdn_sources(html, signals)

    except Exception as e:
        logger.debug("HTML probe failed for %s: %s", url, e)


def _analyze_meta_tags(html: str, signals: dict[Platform, list[str]]) -> None:
    if re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']shopify', html):
        signals[Platform.SHOPIFY].append("meta:generator=shopify")

    if re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\']wordpress', html):
        signals[Platform.WOOCOMMERCE].append("meta:generator=wordpress")

    if re.search(r'<meta[^>]+name=["\']platform["\'][^>]+content=["\']bigcommerce', html):
        signals[Platform.BIGCOMMERCE].append("meta:platform=bigcommerce")

    if re.search(r'<meta[^>]+name=["\']generator["\'][^>]+content=["\'][^"\']*[Ss]hopware', html, re.IGNORECASE):
        signals[Platform.SHOPWARE].append("meta:generator=shopware")


def _analyze_cdn_sources(html: str, signals: dict[Platform, list[str]]) -> None:
    if "cdn.shopify.com" in html:
        signals[Platform.SHOPIFY].append("cdn:cdn.shopify.com")

    if "cdn.bigcommerce.com" in html or "cdn11.bigcommerce.com" in html:
        signals[Platform.BIGCOMMERCE].append("cdn:cdn.bigcommerce.com")

    if "/wp-content/plugins/woocommerce/" in html:
        signals[Platform.WOOCOMMERCE].append("cdn:woocommerce-plugin")

    if "/bundles/storefront/" in html or "shopware-storefront" in html:
        signals[Platform.SHOPWARE].append("cdn:shopware_storefront")


def _determine_platform(signals: dict[Platform, list[str]]) -> tuple[Platform, list[str]]:
    platform_counts = {plat: len(sigs) for plat, sigs in signals.items()}
    max_count = max(platform_counts.values()) if platform_counts else 0

    if max_count == 0:
        return Platform.GENERIC, ["fallback:no-signals-detected"]

    for platform, count in platform_counts.items():
        if count == max_count:
            return platform, signals[platform]

    return Platform.GENERIC, ["fallback:unexpected-path"]
