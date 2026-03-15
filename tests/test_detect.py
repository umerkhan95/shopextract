"""Tests for platform detection."""

from __future__ import annotations

import pytest
import httpx

from shopextract._detect import (
    detect,
    _analyze_meta_tags,
    _analyze_cdn_sources,
    _determine_platform,
)
from shopextract._models import Platform


# -- Unit tests for internal helpers -----------------------------------------

class TestAnalyzeMetaTags:
    def test_shopify_generator(self):
        signals = {p: [] for p in Platform if p != Platform.GENERIC}
        html = '<meta name="generator" content="Shopify">'
        _analyze_meta_tags(html.lower(), signals)
        assert "meta:generator=shopify" in signals[Platform.SHOPIFY]

    def test_wordpress_generator(self):
        signals = {p: [] for p in Platform if p != Platform.GENERIC}
        html = '<meta name="generator" content="WordPress 6.5">'
        _analyze_meta_tags(html.lower(), signals)
        assert "meta:generator=wordpress" in signals[Platform.WOOCOMMERCE]

    def test_bigcommerce_platform(self):
        signals = {p: [] for p in Platform if p != Platform.GENERIC}
        html = '<meta name="platform" content="BigCommerce">'
        _analyze_meta_tags(html.lower(), signals)
        assert "meta:platform=bigcommerce" in signals[Platform.BIGCOMMERCE]

    def test_shopware_generator(self):
        signals = {p: [] for p in Platform if p != Platform.GENERIC}
        html = '<meta name="generator" content="Shopware 6">'
        _analyze_meta_tags(html.lower(), signals)
        assert "meta:generator=shopware" in signals[Platform.SHOPWARE]

    def test_no_match(self):
        signals = {p: [] for p in Platform if p != Platform.GENERIC}
        html = "<html><body>Hello</body></html>"
        _analyze_meta_tags(html.lower(), signals)
        assert all(len(s) == 0 for s in signals.values())


class TestAnalyzeCdnSources:
    def test_shopify_cdn(self):
        signals = {p: [] for p in Platform if p != Platform.GENERIC}
        html = '<script src="https://cdn.shopify.com/s/files/1/shop.js"></script>'
        _analyze_cdn_sources(html.lower(), signals)
        assert "cdn:cdn.shopify.com" in signals[Platform.SHOPIFY]

    def test_bigcommerce_cdn(self):
        signals = {p: [] for p in Platform if p != Platform.GENERIC}
        html = '<link rel="stylesheet" href="https://cdn11.bigcommerce.com/styles.css">'
        _analyze_cdn_sources(html.lower(), signals)
        assert "cdn:cdn.bigcommerce.com" in signals[Platform.BIGCOMMERCE]

    def test_woocommerce_plugin(self):
        signals = {p: [] for p in Platform if p != Platform.GENERIC}
        html = '<script src="/wp-content/plugins/woocommerce/assets/js/frontend.js"></script>'
        _analyze_cdn_sources(html.lower(), signals)
        assert "cdn:woocommerce-plugin" in signals[Platform.WOOCOMMERCE]

    def test_shopware_storefront(self):
        signals = {p: [] for p in Platform if p != Platform.GENERIC}
        html = '<link href="/bundles/storefront/assets/css/base.css">'
        _analyze_cdn_sources(html.lower(), signals)
        assert "cdn:shopware_storefront" in signals[Platform.SHOPWARE]


class TestDeterminePlatform:
    def test_shopify_wins_by_count(self):
        signals = {p: [] for p in Platform if p != Platform.GENERIC}
        signals[Platform.SHOPIFY] = ["header:x-shopify", "cdn:cdn.shopify.com"]
        signals[Platform.WOOCOMMERCE] = ["cdn:woocommerce-plugin"]
        platform, sigs = _determine_platform(signals)
        assert platform == Platform.SHOPIFY
        assert len(sigs) == 2

    def test_generic_fallback(self):
        signals = {p: [] for p in Platform if p != Platform.GENERIC}
        platform, sigs = _determine_platform(signals)
        assert platform == Platform.GENERIC
        assert "fallback:no-signals-detected" in sigs

    def test_single_signal_wins(self):
        signals = {p: [] for p in Platform if p != Platform.GENERIC}
        signals[Platform.MAGENTO] = ["header:x-magento"]
        platform, sigs = _determine_platform(signals)
        assert platform == Platform.MAGENTO


# -- Async integration tests with mocked HTTP --------------------------------

@pytest.mark.asyncio
async def test_detect_shopify():
    """Detect Shopify via header + API probe."""
    transport = httpx.MockTransport(lambda req: _shopify_mock_handler(req))
    client = httpx.AsyncClient(transport=transport, follow_redirects=True)
    result = await detect("https://shop.example.com", client=client)
    await client.aclose()
    assert result.platform == Platform.SHOPIFY
    assert result.confidence > 0


@pytest.mark.asyncio
async def test_detect_woocommerce():
    """Detect WooCommerce via header + API probe."""
    transport = httpx.MockTransport(lambda req: _woocommerce_mock_handler(req))
    client = httpx.AsyncClient(transport=transport, follow_redirects=True)
    result = await detect("https://woo.example.com", client=client)
    await client.aclose()
    assert result.platform == Platform.WOOCOMMERCE
    assert result.confidence > 0


@pytest.mark.asyncio
async def test_detect_magento():
    """Detect Magento via header + API probe."""
    transport = httpx.MockTransport(lambda req: _magento_mock_handler(req))
    client = httpx.AsyncClient(transport=transport, follow_redirects=True)
    result = await detect("https://magento.example.com", client=client)
    await client.aclose()
    assert result.platform == Platform.MAGENTO
    assert result.confidence > 0


@pytest.mark.asyncio
async def test_detect_bigcommerce():
    """Detect BigCommerce via HTML meta tag."""
    transport = httpx.MockTransport(lambda req: _bigcommerce_mock_handler(req))
    client = httpx.AsyncClient(transport=transport, follow_redirects=True)
    result = await detect("https://bc.example.com", client=client)
    await client.aclose()
    assert result.platform == Platform.BIGCOMMERCE


@pytest.mark.asyncio
async def test_detect_shopware():
    """Detect Shopware via header + API probe."""
    transport = httpx.MockTransport(lambda req: _shopware_mock_handler(req))
    client = httpx.AsyncClient(transport=transport, follow_redirects=True)
    result = await detect("https://sw.example.com", client=client)
    await client.aclose()
    assert result.platform == Platform.SHOPWARE


@pytest.mark.asyncio
async def test_detect_generic_fallback():
    """Fall back to GENERIC when nothing matches."""
    def handler(req: httpx.Request) -> httpx.Response:
        url = str(req.url)
        if req.method == "HEAD":
            return httpx.Response(200)
        # API probes should return 404 so no platform is detected
        if any(p in url for p in ["/products.json", "/wp-json/", "/rest/V1/", "/api/_info/"]):
            return httpx.Response(404)
        return httpx.Response(200, text="<html><body>Hello</body></html>")

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport, follow_redirects=True)
    result = await detect("https://plain.example.com", client=client)
    await client.aclose()
    assert result.platform == Platform.GENERIC


@pytest.mark.asyncio
async def test_detect_handles_connection_errors():
    """Detection should not crash on connection errors."""
    transport = httpx.MockTransport(lambda req: (_ for _ in ()).throw(httpx.ConnectError("refused")))
    client = httpx.AsyncClient(transport=transport, follow_redirects=True)
    result = await detect("https://down.example.com", client=client)
    await client.aclose()
    assert result.platform == Platform.GENERIC


# -- Mock handlers -----------------------------------------------------------

def _shopify_mock_handler(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    if request.method == "HEAD":
        return httpx.Response(200, headers={"X-ShopId": "12345"})
    if "/products.json" in url:
        return httpx.Response(200, json={"products": [{"id": 1, "title": "Test"}]})
    return httpx.Response(200, text='<html><head><meta name="generator" content="Shopify"></head><body></body></html>')


def _woocommerce_mock_handler(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    if request.method == "HEAD":
        return httpx.Response(200, headers={"Link": '<https://woo.example.com/wp-json/>; rel="https://api.w.org/"'})
    if "/wp-json/" in url and "/wc/" not in url:
        return httpx.Response(200, json={"namespaces": ["wc/store/v1"]})
    return httpx.Response(200, text='<html><script src="/wp-content/plugins/woocommerce/js/frontend.js"></script></html>')


def _magento_mock_handler(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    if request.method == "HEAD":
        return httpx.Response(200, headers={"X-Magento-Cache-Control": "public"})
    if "/rest/V1/store/storeConfigs" in url:
        return httpx.Response(200, json=[{"id": 1}])
    return httpx.Response(200, text="<html><body></body></html>")


def _bigcommerce_mock_handler(request: httpx.Request) -> httpx.Response:
    if request.method == "HEAD":
        return httpx.Response(200)
    return httpx.Response(200, text='<html><head><meta name="platform" content="BigCommerce"></head><script src="https://cdn11.bigcommerce.com/app.js"></script></html>')


def _shopware_mock_handler(request: httpx.Request) -> httpx.Response:
    url = str(request.url)
    if request.method == "HEAD":
        return httpx.Response(200, headers={"sw-version-id": "abc123"})
    if "/api/_info/config" in url:
        return httpx.Response(200, json={"version": "6.5"})
    return httpx.Response(200, text='<html><head><meta name="generator" content="Shopware 6"></head></html>')
