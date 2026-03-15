"""Simplified extraction orchestrator.

Provides the main extract() and extract_one() functions that implement
the tiered fallback chain: API > UnifiedCrawl > CSS.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterator
from typing import Any

from ._models import (
    ExtractionResult,
    ExtractionTier,
    ExtractorResult,
    Platform,
    Product,
)
from ._normalize import normalize
from ._quality import QualityScorer

logger = logging.getLogger(__name__)

# Quality threshold for accepting probe results
_QUALITY_THRESHOLD = 0.3

# Concurrency for URL extraction
_EXTRACTION_CONCURRENCY = 10


async def extract(
    url: str,
    *,
    platform: Platform | None = None,
    max_urls: int = 20,
    shop_url: str | None = None,
) -> ExtractionResult:
    """Extract products from an e-commerce store.

    This is the main extraction function. It:
    1. Detects the platform (if not provided)
    2. Discovers product URLs
    3. Extracts products using tiered fallback (API > UnifiedCrawl > CSS)
    4. Normalizes to unified Product model

    Args:
        url: The merchant's website URL.
        platform: Pre-detected platform (auto-detected if None).
        max_urls: Maximum product URLs to process.
        shop_url: Base shop URL for normalization (defaults to url).

    Returns:
        ExtractionResult with products, tier used, quality score.
    """
    if shop_url is None:
        shop_url = url.rstrip("/")

    # Step 1: Detect platform
    if platform is None:
        from ._detect import detect
        result = await detect(url)
        platform = result.platform

    # Step 2: Try API extraction first
    api_result = await _try_api_extraction(url, platform)
    if api_result and api_result.products:
        scorer = QualityScorer()
        quality = scorer.score_batch(api_result.products)
        if quality >= _QUALITY_THRESHOLD:
            products = _normalize_batch(api_result.products, platform, shop_url)
            return ExtractionResult(
                products=products,
                raw_products=api_result.products,
                tier=ExtractionTier.API,
                quality_score=quality,
                platform=platform,
                urls_attempted=1,
                urls_succeeded=1,
            )

    # Step 3: Discover URLs for crawl-based extraction
    from ._discover import discover
    urls = await discover(url, platform=platform, max_urls=max_urls)

    if not urls:
        return ExtractionResult(
            platform=platform,
            errors=["No product URLs discovered"],
        )

    # Step 4: Try UnifiedCrawl on a sample URL
    from .extractors.unified import UnifiedCrawlExtractor

    unified = UnifiedCrawlExtractor()
    sample_url = urls[0]
    probe_result = await unified.extract(sample_url)

    scorer = QualityScorer()
    if probe_result.products:
        quality = scorer.score_batch(probe_result.products)
        if quality >= _QUALITY_THRESHOLD:
            # Commit to UnifiedCrawl for all URLs
            all_products = list(probe_result.products)
            remaining = urls[1:]

            if remaining:
                batch_result = await _extract_batch_concurrent(
                    unified, remaining, _EXTRACTION_CONCURRENCY
                )
                all_products.extend(batch_result.products)

            products = _normalize_batch(all_products, platform, shop_url)
            return ExtractionResult(
                products=products,
                raw_products=all_products,
                tier=ExtractionTier.UNIFIED_CRAWL,
                quality_score=scorer.score_batch(all_products),
                platform=platform,
                urls_attempted=len(urls),
                urls_succeeded=len(products),
            )

    # Step 5: CSS fallback with generic schema
    from .extractors.css import CSSExtractor

    generic_schema = _get_generic_css_schema()
    css = CSSExtractor(schema=generic_schema)

    all_products: list[dict] = []
    for batch_urls in _chunks(urls, _EXTRACTION_CONCURRENCY):
        batch_result = await css.extract_batch(batch_urls)
        all_products.extend(batch_result.products)

    products = _normalize_batch(all_products, platform, shop_url)
    return ExtractionResult(
        products=products,
        raw_products=all_products,
        tier=ExtractionTier.CSS,
        quality_score=scorer.score_batch(all_products) if all_products else 0.0,
        platform=platform,
        urls_attempted=len(urls),
        urls_succeeded=len(products),
    )


async def extract_one(url: str) -> dict:
    """Extract product data from a single product page URL.

    Returns raw product dict (not normalized). For quick single-page extraction.

    Args:
        url: Product page URL.

    Returns:
        Raw product dict or empty dict if extraction fails.
    """
    from .extractors.unified import UnifiedCrawlExtractor

    extractor = UnifiedCrawlExtractor()
    result = await extractor.extract(url)
    if result.products:
        return result.products[0]
    return {}


async def from_feed(feed_url: str, *, shop_url: str = "") -> ExtractionResult:
    """Extract products from a Google Shopping feed URL.

    Args:
        feed_url: Google Shopping feed URL (XML or CSV/TSV).
        shop_url: Base shop URL for normalization.

    Returns:
        ExtractionResult with parsed and normalized products.
    """
    from .extractors.feed import GoogleFeedExtractor

    extractor = GoogleFeedExtractor()
    result = await extractor.extract(feed_url)

    if not result.products:
        return ExtractionResult(
            tier=ExtractionTier.GOOGLE_FEED,
            platform=Platform.GENERIC,
            errors=[result.error] if result.error else ["No products found in feed"],
        )

    products = _normalize_batch(result.products, Platform.GENERIC, shop_url or feed_url)
    scorer = QualityScorer()

    return ExtractionResult(
        products=products,
        raw_products=result.products,
        tier=ExtractionTier.GOOGLE_FEED,
        quality_score=scorer.score_batch(result.products),
        platform=Platform.GENERIC,
        urls_attempted=1,
        urls_succeeded=1 if products else 0,
    )


# -- Internal helpers ---------------------------------------------------------

async def _try_api_extraction(url: str, platform: Platform) -> ExtractorResult | None:
    """Try platform-specific API extraction."""
    base_url = url.rstrip("/")

    if platform == Platform.SHOPIFY:
        from .extractors.shopify import ShopifyExtractor
        extractor = ShopifyExtractor()
        result = await extractor.extract(base_url)
        if result.products:
            return result

    elif platform == Platform.WOOCOMMERCE:
        from .extractors.woocommerce import WooCommerceExtractor
        extractor = WooCommerceExtractor()
        result = await extractor.extract(base_url)
        if result.products:
            return result

    elif platform == Platform.MAGENTO:
        from .extractors.magento import MagentoExtractor
        extractor = MagentoExtractor()
        result = await extractor.extract(base_url)
        if result.products:
            return result

    return None


async def _extract_batch_concurrent(
    extractor: Any, urls: list[str], concurrency: int
) -> ExtractorResult:
    """Extract from URLs with concurrency limit."""
    all_products: list[dict] = []
    errors: list[str] = []

    semaphore = asyncio.Semaphore(concurrency)

    async def _extract_single(u: str) -> None:
        async with semaphore:
            try:
                result = await extractor.extract(u)
                all_products.extend(result.products)
                if result.error:
                    errors.append(result.error)
            except Exception as e:
                errors.append(f"Error extracting {u}: {e}")

    results = await asyncio.gather(*[_extract_single(u) for u in urls], return_exceptions=True)
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.warning("Unhandled extraction error for URL %s: %s", urls[i], result)

    return ExtractorResult(
        products=all_products,
        complete=not errors,
        error="; ".join(errors) if errors else None,
    )


def _normalize_batch(
    raw_products: list[dict], platform: Platform, shop_url: str
) -> list[Product]:
    """Normalize a batch of raw product dicts."""
    products = []
    for raw in raw_products:
        product = normalize(raw, platform=platform, shop_url=shop_url)
        if product:
            products.append(product)
    return products


def _get_generic_css_schema() -> dict:
    """Return a generic CSS extraction schema."""
    return {
        "name": "products",
        "baseSelector": "[itemtype*='Product'], .product, [data-product]",
        "fields": [
            {"name": "title", "selector": "h1, h2, .product-title, [itemprop='name']", "type": "text"},
            {"name": "price", "selector": ".price, [itemprop='price'], [data-price]", "type": "text"},
            {"name": "image", "selector": "img.product-image, [itemprop='image'], .product img", "type": "attribute", "attribute": "src"},
            {"name": "description", "selector": "[itemprop='description'], .product-description", "type": "text"},
            {"name": "sku", "selector": "[itemprop='sku']", "type": "text"},
        ],
    }


def _chunks(lst: list, n: int) -> Iterator[list]:
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
