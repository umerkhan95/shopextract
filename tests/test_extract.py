"""Tests for extraction orchestrator."""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shopextract._extract import (
    extract,
    extract_one,
    from_feed,
    _normalize_batch,
    _get_generic_css_schema,
    _chunks,
)
from shopextract._models import (
    ExtractionResult,
    ExtractionTier,
    ExtractorResult,
    Platform,
    PlatformResult,
    Product,
)


class TestNormalizeBatch:
    def test_normalizes_valid_products(self):
        raw_products = [
            {"title": "Widget A", "price": "10.00", "sku": "WA"},
            {"title": "Widget B", "price": "20.00", "sku": "WB"},
        ]
        products = _normalize_batch(raw_products, Platform.GENERIC, "https://example.com")
        assert len(products) == 2
        assert all(isinstance(p, Product) for p in products)

    def test_skips_invalid_products(self):
        raw_products = [
            {"title": "Widget A", "price": "10.00", "sku": "WA"},
            {"some_field": "no title or id"},  # Invalid, no title
        ]
        products = _normalize_batch(raw_products, Platform.GENERIC, "https://example.com")
        assert len(products) == 1

    def test_empty_list(self):
        assert _normalize_batch([], Platform.GENERIC, "") == []


class TestGetGenericCssSchema:
    def test_has_required_keys(self):
        schema = _get_generic_css_schema()
        assert "name" in schema
        assert "baseSelector" in schema
        assert "fields" in schema
        assert len(schema["fields"]) >= 3


class TestChunks:
    def test_even_split(self):
        result = list(_chunks([1, 2, 3, 4], 2))
        assert result == [[1, 2], [3, 4]]

    def test_uneven_split(self):
        result = list(_chunks([1, 2, 3, 4, 5], 2))
        assert len(result) == 3
        assert result[-1] == [5]

    def test_empty_list(self):
        result = list(_chunks([], 5))
        assert result == []


@pytest.mark.asyncio
async def test_extract_api_tier():
    """When API extraction succeeds with good quality, return API tier."""
    api_products = [
        {
            "id": 1,
            "title": "Widget",
            "body_html": "A good widget",
            "handle": "widget",
            "vendor": "TestCo",
            "variants": [{"id": 1, "price": "10.00", "sku": "W1", "barcode": None, "inventory_quantity": 5}],
            "images": [{"src": "https://img.jpg"}],
        },
    ]

    with patch("shopextract._detect.detect", new_callable=AsyncMock) as mock_detect, \
         patch("shopextract._extract._try_api_extraction", new_callable=AsyncMock) as mock_api:
        mock_detect.return_value = PlatformResult(platform=Platform.SHOPIFY, confidence=0.9)
        mock_api.return_value = ExtractorResult(products=api_products)

        result = await extract("https://shop.example.com")

    assert result.tier == ExtractionTier.API
    assert result.platform == Platform.SHOPIFY
    assert result.product_count >= 1
    assert result.quality_score >= 0.3


@pytest.mark.asyncio
async def test_extract_unified_crawl_fallback():
    """When API fails, fall back to UnifiedCrawl."""
    crawl_products = [
        {"title": "Crawled Widget", "price": "20.00", "image_url": "https://img.jpg", "sku": "CW1", "description": "d"},
    ]

    with patch("shopextract._detect.detect", new_callable=AsyncMock) as mock_detect, \
         patch("shopextract._extract._try_api_extraction", new_callable=AsyncMock) as mock_api, \
         patch("shopextract._discover.discover", new_callable=AsyncMock) as mock_discover, \
         patch("shopextract.extractors.unified.UnifiedCrawlExtractor") as MockExtractor:

        mock_detect.return_value = PlatformResult(platform=Platform.GENERIC, confidence=0.5)
        mock_api.return_value = None

        mock_discover.return_value = ["https://example.com/product/1"]

        instance = MockExtractor.return_value
        instance.extract = AsyncMock(return_value=ExtractorResult(products=crawl_products))

        result = await extract("https://example.com")

    assert result.tier == ExtractionTier.UNIFIED_CRAWL
    assert result.product_count >= 1


@pytest.mark.asyncio
async def test_extract_no_urls_discovered():
    """When no URLs are discovered, return empty result with error."""
    with patch("shopextract._detect.detect", new_callable=AsyncMock) as mock_detect, \
         patch("shopextract._extract._try_api_extraction", new_callable=AsyncMock) as mock_api, \
         patch("shopextract._discover.discover", new_callable=AsyncMock) as mock_discover:

        mock_detect.return_value = PlatformResult(platform=Platform.GENERIC, confidence=0.5)
        mock_api.return_value = None
        mock_discover.return_value = []

        result = await extract("https://empty.example.com")

    assert result.product_count == 0
    assert len(result.errors) > 0


@pytest.mark.asyncio
async def test_extract_with_pre_detected_platform():
    """When platform is provided, skip detection."""
    api_products = [
        {"title": "W", "price": "10", "image_url": "i.jpg", "sku": "S", "description": "d"},
    ]

    with patch("shopextract._extract._try_api_extraction", new_callable=AsyncMock) as mock_api:
        mock_api.return_value = ExtractorResult(products=api_products)

        result = await extract("https://shop.example.com", platform=Platform.SHOPIFY)

    assert result.platform == Platform.SHOPIFY


@pytest.mark.asyncio
async def test_extract_one():
    """extract_one should return a single product dict."""
    product_dict = {"title": "Single Widget", "price": "29.99"}

    with patch("shopextract.extractors.unified.UnifiedCrawlExtractor") as MockExtractor:
        instance = MockExtractor.return_value
        instance.extract = AsyncMock(return_value=ExtractorResult(products=[product_dict]))

        result = await extract_one("https://example.com/product/widget")

    assert result["title"] == "Single Widget"


@pytest.mark.asyncio
async def test_extract_one_empty():
    """extract_one should return empty dict when extraction fails."""
    with patch("shopextract.extractors.unified.UnifiedCrawlExtractor") as MockExtractor:
        instance = MockExtractor.return_value
        instance.extract = AsyncMock(return_value=ExtractorResult(products=[]))

        result = await extract_one("https://example.com/product/missing")

    assert result == {}


@pytest.mark.asyncio
async def test_from_feed_success():
    """from_feed should parse and normalize feed products."""
    feed_products = [
        {
            "_source": "google_feed",
            "id": "F1",
            "title": "Feed Widget",
            "price": "19.99",
            "image_link": "https://example.com/feed.jpg",
            "link": "https://example.com/feed-widget",
            "description": "A feed widget.",
        },
    ]

    with patch("shopextract.extractors.feed.GoogleFeedExtractor") as MockExtractor:
        instance = MockExtractor.return_value
        instance.extract = AsyncMock(return_value=ExtractorResult(products=feed_products))

        result = await from_feed("https://example.com/feed.xml")

    assert result.tier == ExtractionTier.GOOGLE_FEED
    assert result.product_count >= 1


@pytest.mark.asyncio
async def test_from_feed_empty():
    """from_feed should return error when feed has no products."""
    with patch("shopextract.extractors.feed.GoogleFeedExtractor") as MockExtractor:
        instance = MockExtractor.return_value
        instance.extract = AsyncMock(return_value=ExtractorResult(products=[], error="Parse error"))

        result = await from_feed("https://example.com/empty-feed.xml")

    assert result.product_count == 0
    assert len(result.errors) > 0
