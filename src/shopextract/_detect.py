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
import math
import re
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import urlsplit

import httpx
from ._url_safety import async_client, require_guarded_client

from ._models import DetectionContext, Platform, PlatformResult

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
    Platform.DEMANDWARE: 2,
    Platform.GENERIC: 1,
}

_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)


async def _run_all_probes(client, url, signals):
    base_url = _origin(url)
    await _probe_api_endpoints(client, base_url, signals)
    if getattr(client, "rate_limited", False):
        return
    # A successful public product catalog is strong enough to stop probing.
    if signals[Platform.SHOPIFY]:
        return
    await _probe_headers(client, url, signals)
    await _probe_html_content(client, url, signals)


async def detect(url: str, *, client: httpx.AsyncClient | None = None) -> PlatformResult:
    """Detect the e-commerce platform for the given URL.

    Args:
        url: The merchant's website URL.
        client: Optional shared httpx.AsyncClient.

    Returns:
        PlatformResult with detected platform, confidence score, and signals.
    """
    return (await detect_context(url, client=client)).result


def _origin(url: str) -> str:
    parsed = urlsplit(url)
    return f"{parsed.scheme}://{parsed.netloc}"


class _ProbeObserver:
    def __init__(self, client):
        self.client = client
        self.errors = []
        self.retry_after_seconds = None
        self.rate_limited = False

    async def _request(self, method, url, **kwargs):
        try:
            response = await getattr(self.client, method)(url, **kwargs)
        except Exception as error:
            self.errors.append(f"{url}: {type(error).__name__}: {error}")
            raise
        if response.status_code >= 400:
            self.errors.append(f"HTTP {response.status_code} {url}")
        if response.status_code == 429:
            self.rate_limited = True
            self.retry_after_seconds = _retry_after(response.headers.get("retry-after"))
        return response

    async def get(self, url, **kwargs):
        return await self._request("get", url, **kwargs)

    async def head(self, url, **kwargs):
        return await self._request("head", url, **kwargs)


def _retry_after(value):
    if not value:
        return None
    try:
        delay = float(value)
        return delay if math.isfinite(delay) and delay >= 0 else None
    except (ValueError, TypeError):
        try:
            at = parsedate_to_datetime(value)
            if at.tzinfo is None:
                at = at.replace(tzinfo=timezone.utc)
            return max(0.0, (at - datetime.now(timezone.utc)).total_seconds())
        except (ValueError, TypeError, OverflowError, AttributeError):
            return None


async def detect_context(url: str, *, client: httpx.AsyncClient | None = None) -> DetectionContext:
    """Detect a platform and retain probe errors and server retry guidance."""
    if client is not None:
        require_guarded_client(client)
    start_time = time.time()
    logger.info("Starting platform detection for %s", url)

    signals: dict[Platform, list[str]] = {
        Platform.SHOPIFY: [],
        Platform.WOOCOMMERCE: [],
        Platform.MAGENTO: [],
        Platform.BIGCOMMERCE: [],
        Platform.SHOPWARE: [],
        Platform.DEMANDWARE: [],
    }

    own_client = client is None
    if own_client:
        client = async_client(
            timeout=httpx.Timeout(PROBE_TIMEOUT),
            follow_redirects=True,
            headers={"User-Agent": _USER_AGENT},
        )

    observer = _ProbeObserver(client)
    try:
        await asyncio.wait_for(
            _run_all_probes(observer, url, signals),
            timeout=TOTAL_TIMEOUT,
        )
    except asyncio.TimeoutError:
        logger.warning("Platform detection timed out after %ss for %s", TOTAL_TIMEOUT, url)
        observer.errors.append(f"detection_timeout: exceeded {TOTAL_TIMEOUT:g}s")
    except Exception as e:
        logger.error("Error during platform detection for %s: %s", url, e)
    finally:
        if own_client:
            await client.aclose()

    platform, platform_signals = _determine_platform(signals)
    max_sigs = _MAX_SIGNALS.get(platform, 1)
    confidence = 0.0 if platform == Platform.GENERIC else min(len(platform_signals) / max_sigs, 1.0)

    elapsed = time.time() - start_time
    logger.info(
        "Platform detection complete for %s: %s (confidence: %.2f, signals: %d, time: %.2fs)",
        url, platform, confidence, len(platform_signals), elapsed,
    )

    result = PlatformResult(platform=platform, confidence=confidence, signals=platform_signals)
    return DetectionContext(result=result, errors=observer.errors,
                            retry_after_seconds=observer.retry_after_seconds)


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
    for probe in (_probe_shopify_api, _probe_woocommerce_api, _probe_magento_api,
                  _probe_shopware_api, _probe_magento_graphql):
        await probe(client, url, signals)
        if getattr(client, "rate_limited", False):
            return
        if any(signals[platform] for platform in (Platform.SHOPIFY, Platform.WOOCOMMERCE,
                Platform.MAGENTO, Platform.SHOPWARE)):
            return


async def _probe_shopify_api(
    client: httpx.AsyncClient, base_url: str, signals: dict[Platform, list[str]]
) -> None:
    try:
        response = await client.get(f"{base_url}/products.json", timeout=PROBE_TIMEOUT)
        if response.status_code == 200 and not response.history:
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
            if "wc/v3" in data.get("namespaces", []):
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


async def _probe_magento_graphql(client, base_url, signals):
    try:
        response = await client.get(base_url + '/graphql',
            params={'query':'{storeConfig{store_code}}'}, timeout=PROBE_TIMEOUT)
        if response.status_code == 200:
            config = response.json().get('data', {}).get('storeConfig')
            if isinstance(config, dict) and config.get('store_code'):
                signals[Platform.MAGENTO].append('api:/graphql:storeConfig')
    except Exception as e:
        logger.debug('Magento GraphQL probe failed: %s', type(e).__name__)


async def _probe_shopware_api(
    client: httpx.AsyncClient, base_url: str, signals: dict[Platform, list[str]]
) -> None:
    try:
        response = await client.get(f"{base_url}/api/_info/config", timeout=PROBE_TIMEOUT)
        if response.status_code == 200 and "json" in response.headers.get("content-type", "").lower():
            data = response.json()
            if isinstance(data, dict) and any(key in data for key in ("version", "shopId", "edition")):
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
        if 'text/x-magento-init' in html or 'data-mage-init=' in html:signals[Platform.MAGENTO].append('html:magento-init')
        _analyze_meta_tags(html, signals)
        _analyze_cdn_sources(html, signals)
        if "dwsid" in html and ("/static/default/" in html or "demandware" in html):
            signals[Platform.DEMANDWARE].append("html:demandware-session-and-assets")
        _analyze_magento_html(raw_html, signals)
        from .extractors._storefront import public_config
        endpoint, token = public_config(raw_html, 'shopware', str(response.url))
        if endpoint and token:
            signals[Platform.SHOPWARE].append('html:public-shopware-store-api')

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


def _analyze_magento_html(html: str, signals: dict[Platform, list[str]]) -> None:
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")
    for node in soup.find_all(["script", "link"]):
        source = str(node.get("src") or node.get("href") or "").lower()
        if re.search(r"(?:^|/)magento_[a-z]+/", source):
            signals[Platform.MAGENTO].append("html:magento-module-asset")
            break
    for node in soup.find_all("script"):
        text = node.get_text()
        if re.search(r"[\"']mage/[a-z]", text, re.IGNORECASE):
            signals[Platform.MAGENTO].append("html:mage-requirejs")
            break


def _determine_platform(signals: dict[Platform, list[str]]) -> tuple[Platform, list[str]]:
    strong = {plat: [signal for signal in sigs if not signal.startswith("cdn:")]
              for plat, sigs in signals.items()}
    has_strong = any(strong.values())
    platform_signals = strong if has_strong else signals
    if not has_strong:
        if not any(signals.values()):
            return Platform.GENERIC, ["fallback:no-signals-detected"]
        return Platform.GENERIC, ["fallback:weak-signals-only"]
    platform_counts = {plat: len(sigs) for plat, sigs in platform_signals.items()}
    max_count = max(platform_counts.values()) if platform_counts else 0

    if max_count == 0:
        return Platform.GENERIC, ["fallback:no-signals-detected"]

    for platform, count in platform_counts.items():
        if count == max_count:
            return platform, signals[platform]

    return Platform.GENERIC, ["fallback:unexpected-path"]
