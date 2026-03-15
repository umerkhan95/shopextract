"""Tests for URL discovery."""

from __future__ import annotations

import pytest
import httpx

from shopextract._discover import (
    discover,
    _parse_sitemap_xml,
    _filter_woocommerce_urls,
)
from shopextract._models import Platform


class TestParseSitemapXml:
    def test_valid_sitemap(self):
        xml = """<?xml version="1.0"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc>https://example.com/product/a</loc></url>
            <url><loc>https://example.com/product/b</loc></url>
        </urlset>"""
        urls = _parse_sitemap_xml(xml)
        assert len(urls) == 2
        assert "https://example.com/product/a" in urls

    def test_sitemap_without_namespace(self):
        xml = """<?xml version="1.0"?>
        <urlset>
            <url><loc>https://example.com/product/x</loc></url>
        </urlset>"""
        urls = _parse_sitemap_xml(xml)
        assert len(urls) == 1

    def test_sitemap_index_returns_empty(self):
        xml = """<?xml version="1.0"?>
        <sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <sitemap><loc>https://example.com/sitemap-products.xml</loc></sitemap>
        </sitemapindex>"""
        urls = _parse_sitemap_xml(xml)
        assert urls == []

    def test_invalid_xml(self):
        urls = _parse_sitemap_xml("not xml at all")
        assert urls == []

    def test_empty_loc_elements(self):
        xml = """<?xml version="1.0"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            <url><loc></loc></url>
            <url><loc>https://example.com/product/a</loc></url>
        </urlset>"""
        urls = _parse_sitemap_xml(xml)
        assert len(urls) == 1


class TestFilterWoocommerceUrls:
    def test_filters_when_enough_product_urls(self):
        urls = [
            "https://example.com/product/a",
            "https://example.com/product/b",
            "https://example.com/product/c",
            "https://example.com/about",
        ]
        result = _filter_woocommerce_urls(urls)
        assert len(result) == 3
        assert all("/product/" in u for u in result)

    def test_returns_all_when_few_product_urls(self):
        urls = [
            "https://example.com/product/a",
            "https://example.com/shop/b",
            "https://example.com/shop/c",
            "https://example.com/about",
        ]
        result = _filter_woocommerce_urls(urls)
        assert len(result) == 4


@pytest.mark.asyncio
async def test_discover_shopify_api():
    """Discover Shopify URLs via /products.json."""
    def handler(req: httpx.Request) -> httpx.Response:
        url = str(req.url)
        if "/products.json" in url:
            products = [{"id": i, "title": f"Product {i}"} for i in range(10)]
            return httpx.Response(200, json={"products": products})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport, follow_redirects=True)
    urls = await discover(
        "https://shop.example.com",
        platform=Platform.SHOPIFY,
        client=client,
    )
    await client.aclose()
    assert len(urls) == 1
    assert "/products.json" in urls[0]


@pytest.mark.asyncio
async def test_discover_shopify_api_paginated():
    """When Shopify returns 250 products, should generate pagination URLs."""
    def handler(req: httpx.Request) -> httpx.Response:
        url = str(req.url)
        if "/products.json" in url:
            products = [{"id": i, "title": f"Product {i}"} for i in range(250)]
            return httpx.Response(200, json={"products": products})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport, follow_redirects=True)
    urls = await discover(
        "https://shop.example.com",
        platform=Platform.SHOPIFY,
        client=client,
    )
    await client.aclose()
    assert len(urls) > 1
    assert any("page=2" in u for u in urls)


@pytest.mark.asyncio
async def test_discover_woocommerce_api():
    """Discover WooCommerce URLs via Store API."""
    def handler(req: httpx.Request) -> httpx.Response:
        url = str(req.url)
        if "/wp-json/wc/store/v1/products" in url:
            return httpx.Response(200, json=[{"id": 1}])
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport, follow_redirects=True)
    urls = await discover(
        "https://woo.example.com",
        platform=Platform.WOOCOMMERCE,
        client=client,
    )
    await client.aclose()
    assert len(urls) >= 1
    assert "/wp-json/wc/store/v1/products" in urls[0]


@pytest.mark.asyncio
async def test_discover_magento_api():
    """Discover Magento URLs via REST API."""
    def handler(req: httpx.Request) -> httpx.Response:
        url = str(req.url)
        if "/rest/V1/products" in url:
            return httpx.Response(200, json={"items": [{"id": 1}]})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport, follow_redirects=True)
    urls = await discover(
        "https://magento.example.com",
        platform=Platform.MAGENTO,
        client=client,
    )
    await client.aclose()
    assert len(urls) >= 1


@pytest.mark.asyncio
async def test_discover_max_urls_limit():
    """max_urls parameter should cap the returned list."""
    def handler(req: httpx.Request) -> httpx.Response:
        url = str(req.url)
        if "/products.json" in url:
            products = [{"id": i, "title": f"Product {i}"} for i in range(250)]
            return httpx.Response(200, json={"products": products})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    client = httpx.AsyncClient(transport=transport, follow_redirects=True)
    urls = await discover(
        "https://shop.example.com",
        platform=Platform.SHOPIFY,
        max_urls=3,
        client=client,
    )
    await client.aclose()
    assert len(urls) <= 3
