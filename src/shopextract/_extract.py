"""Simplified extraction orchestrator.

Provides the main extract() and extract_one() functions that implement
the tiered fallback chain: API > UnifiedCrawl > CSS.
"""

from __future__ import annotations

import asyncio
import logging
import os
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
    llm_api_key: str | None = None,
    llm_model: str = "openai/gpt-4o-mini",
    llm_temperature: float = 0.2,
) -> ExtractionResult:
    """Extract products from an e-commerce store.

    This is the main extraction function. It:
    1. Detects the platform (if not provided)
    2. Discovers product URLs
    3. Extracts products using tiered fallback (API > UnifiedCrawl > CSS > LLM)
    4. Normalizes to unified Product model

    Args:
        url: The merchant's website URL.
        platform: Pre-detected platform (auto-detected if None).
        max_urls: Maximum product URLs to process.
        shop_url: Base shop URL for normalization (defaults to url).
        llm_api_key: API key for LLM extraction. Enables Tier 4 (LLM) as
            final fallback. If not provided, reads from SHOPEXTRACT_LLM_API_KEY
            env var, then falls back to provider-specific env vars (OPENAI_API_KEY,
            ANTHROPIC_API_KEY, etc.). For Ollama, no key is needed.
        llm_model: LLM model identifier in LiteLLM format (default: "openai/gpt-4o-mini").

            Supported providers and models:

            Cloud providers:
              - "openai/gpt-4o-mini"          (cheapest, recommended)
              - "openai/gpt-4o"               (best quality)
              - "anthropic/claude-sonnet-4-20250514"  (strong alternative)
              - "anthropic/claude-haiku-4-5-20251001"  (fast + cheap)
              - "gemini/gemini-2.0-flash"     (Google, fast)
              - "gemini/gemini-2.5-pro-preview-06-05"     (Google, best quality)
              - "deepseek/deepseek-chat"      (cheap, good quality)
              - "groq/llama-3.1-70b-versatile"  (fast, free tier)
              - "groq/llama-3.3-70b-versatile"  (latest Llama)
              - "mistral/mistral-large-latest"  (Mistral AI)
              - "mistral/mistral-small-latest"  (Mistral AI, cheap)
              - "cohere/command-r-plus"       (Cohere)
              - "perplexity/sonar-pro"        (Perplexity)

            Local models (no API key needed):
              - "ollama/llama3.1"             (local, free)
              - "ollama/mistral"              (local, free)
              - "ollama/qwen2.5"              (local, free)
              - "ollama/deepseek-r1"          (local, free)
              - "ollama/phi3"                 (local, small)

            Other providers:
              - "together_ai/meta-llama/..."  (Together AI)
              - "bedrock/anthropic.claude..." (AWS Bedrock)
              - "vertex_ai/gemini-..."        (Google Cloud)
              - "azure/gpt-4o"               (Azure OpenAI)
              - "cloudflare/..."             (Cloudflare Workers AI)
              - "replicate/..."              (Replicate)
              - "openrouter/..."             (OpenRouter, 100+ models)

            Any model supported by LiteLLM works. See https://docs.litellm.ai/docs/providers

        llm_temperature: LLM temperature (default: 0.2).

    Returns:
        ExtractionResult with products, tier used, quality score.
    """
    if shop_url is None:
        shop_url = url.rstrip("/")

    # Read LLM config from env if not provided
    if llm_api_key is None:
        llm_api_key = _resolve_llm_api_key(llm_model)
    llm_model = os.environ.get("SHOPEXTRACT_LLM_MODEL", llm_model)

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

    if all_products:
        products = _normalize_batch(all_products, platform, shop_url)
        return ExtractionResult(
            products=products,
            raw_products=all_products,
            tier=ExtractionTier.CSS,
            quality_score=scorer.score_batch(all_products),
            platform=platform,
            urls_attempted=len(urls),
            urls_succeeded=len(products),
        )

    # Step 6: LLM extraction (final fallback, requires API key)
    if llm_api_key:
        llm_products = await _try_llm_extraction(
            urls, llm_api_key, llm_model, llm_temperature
        )
        if llm_products:
            products = _normalize_batch(llm_products, platform, shop_url)
            return ExtractionResult(
                products=products,
                raw_products=llm_products,
                tier=ExtractionTier.LLM,
                quality_score=scorer.score_batch(llm_products),
                platform=platform,
                urls_attempted=len(urls),
                urls_succeeded=len(products),
            )

    # Nothing worked
    products = _normalize_batch(all_products, platform, shop_url)
    return ExtractionResult(
        products=products,
        raw_products=all_products,
        tier=ExtractionTier.CSS,
        quality_score=0.0,
        platform=platform,
        urls_attempted=len(urls),
        urls_succeeded=len(products),
    )


async def extract_one(
    url: str,
    *,
    llm_api_key: str | None = None,
    llm_model: str = "openai/gpt-4o-mini",
) -> dict:
    """Extract product data from a single product page URL.

    Tries UnifiedCrawl first. If that fails and llm_api_key is provided,
    falls back to LLM extraction.

    Args:
        url: Product page URL.
        llm_api_key: API key for LLM fallback (optional).
        llm_model: LLM model identifier (default: "openai/gpt-4o-mini").

    Returns:
        Raw product dict or empty dict if extraction fails.
    """
    from .extractors.unified import UnifiedCrawlExtractor

    extractor = UnifiedCrawlExtractor()
    result = await extractor.extract(url)
    if result.products:
        return result.products[0]

    # LLM fallback for single page
    if llm_api_key:
        llm_products = await _try_llm_extraction(
            [url], llm_api_key, llm_model, 0.2,
        )
        if llm_products:
            return llm_products[0]

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

# Provider-specific env var mapping
_PROVIDER_ENV_KEYS = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "groq": "GROQ_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "cohere": "COHERE_API_KEY",
    "perplexity": "PERPLEXITY_API_KEY",
    "together_ai": "TOGETHER_API_KEY",
    "bedrock": "AWS_ACCESS_KEY_ID",
    "vertex_ai": "GOOGLE_APPLICATION_CREDENTIALS",
    "azure": "AZURE_API_KEY",
    "cloudflare": "CLOUDFLARE_API_KEY",
    "replicate": "REPLICATE_API_TOKEN",
    "openrouter": "OPENROUTER_API_KEY",
    "ollama": None,  # No key needed
}


def _resolve_llm_api_key(model: str) -> str:
    """Resolve API key from environment variables based on model provider."""
    # 1. Check shopextract-specific env var
    key = os.environ.get("SHOPEXTRACT_LLM_API_KEY", "")
    if key:
        return key

    # 2. Check provider-specific env var
    provider = model.split("/")[0] if "/" in model else model
    if provider == "ollama":
        return "ollama"  # Ollama needs no real key

    env_var = _PROVIDER_ENV_KEYS.get(provider)
    if env_var:
        key = os.environ.get(env_var, "")
        if key:
            return key

    return ""


async def _try_llm_extraction(
    urls: list[str],
    api_key: str,
    model: str,
    temperature: float,
) -> list[dict]:
    """Try LLM-based extraction on URLs."""
    try:
        from crawl4ai import LLMConfig
        from .extractors.llm import LLMExtractor

        llm_config = LLMConfig(provider=model, api_token=api_key)
        extractor = LLMExtractor(
            llm_config=llm_config,
            temperature=temperature,
        )

        all_products: list[dict] = []
        for url in urls[:10]:  # Limit to 10 URLs for cost control
            try:
                result = await extractor.extract(url)
                all_products.extend(result.products)
            except Exception as e:
                logger.debug("LLM extraction failed for %s: %s", url, e)

        return all_products
    except ImportError:
        logger.warning("LLM extraction requires crawl4ai[llm] — pip install shopextract[llm]")
        return []
    except Exception as e:
        logger.warning("LLM extraction failed: %s", e)
        return []


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
