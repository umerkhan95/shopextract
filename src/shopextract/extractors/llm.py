"""Universal LLM-based product extractor -- works on any website."""

from __future__ import annotations

import json
import logging
from difflib import SequenceMatcher

from crawl4ai import (
    AsyncWebCrawler,
    DefaultMarkdownGenerator,
    LLMConfig,
)
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.extraction_strategy import LLMExtractionStrategy

from .._models import ExtractorResult
from ._browser import (
    StealthLevel,
    get_browser_config,
    get_crawl_config,
    get_crawler_strategy,
)

logger = logging.getLogger(__name__)

PRODUCT_EXTRACTION_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Product name or title"},
        "price": {"type": "string", "description": "Price as text including currency symbol"},
        "description": {"type": "string", "description": "Product description text"},
        "image_url": {"type": "string", "description": "Main product image URL"},
        "sku": {"type": "string", "description": "Product SKU or ID if shown"},
        "currency": {"type": "string", "description": "ISO 4217 currency code"},
        "in_stock": {"type": "boolean", "description": "Whether the product is in stock"},
        "vendor": {"type": "string", "description": "Brand or vendor name"},
        "product_url": {"type": "string", "description": "Canonical URL of the product page"},
        "product_type": {"type": "string", "description": "Product category or type"},
    },
    "required": ["title"],
}

EXTRACTION_INSTRUCTION = (
    "This is a product detail page for a SINGLE product. "
    "Extract ONLY the main product being sold -- ignore related products, "
    "recommendations, navigation items, and upsells. "
    "Extract ALL of these fields if visible anywhere on the page: "
    "title (required), price (CRITICAL -- include the full price with currency symbol, "
    "e.g. '$29.99' or '\u00a345.00'), description, main product image URL, SKU or product ID, "
    "ISO 4217 currency code (e.g. USD, EUR, GBP), stock availability (true/false), "
    "brand or vendor name, canonical product page URL, and product category or type. "
    "Return a JSON array containing exactly ONE product object."
)


class LLMExtractor:
    """Universal product extractor using crawl4ai LLMExtractionStrategy."""

    def __init__(
        self,
        llm_config: LLMConfig,
        temperature: float = 0.2,
        max_tokens: int = 4000,
        stealth_level: StealthLevel = StealthLevel.STANDARD,
    ):
        self.llm_config = llm_config
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.stealth_level = stealth_level

    @staticmethod
    def _create_markdown_generator():
        return DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(
                threshold=0.48,
                threshold_type="fixed",
                min_word_threshold=10,
            ),
        )

    def _create_strategy(self) -> LLMExtractionStrategy:
        return LLMExtractionStrategy(
            llm_config=self.llm_config,
            schema=PRODUCT_EXTRACTION_SCHEMA,
            extraction_type="schema",
            instruction=EXTRACTION_INSTRUCTION,
            chunk_token_threshold=8000,
            overlap_rate=0.1,
            apply_chunking=True,
            input_format="markdown",
            verbose=False,
            extra_args={
                "temperature": self.temperature,
                "max_tokens": self.max_tokens,
            },
        )

    @staticmethod
    def _merge_chunk_products(products: list[dict]) -> list[dict]:
        if len(products) <= 1:
            return products

        merged: list[dict] = []
        used: set[int] = set()

        for i, product in enumerate(products):
            if i in used:
                continue

            combined = dict(product)
            used.add(i)
            title_i = (product.get("title") or "").strip().lower()

            if not title_i:
                continue

            for j in range(i + 1, len(products)):
                if j in used:
                    continue

                other = products[j]
                title_j = (other.get("title") or "").strip().lower()
                if not title_j:
                    continue

                similar = False
                if title_i == title_j:
                    similar = True
                elif title_i.startswith(title_j) or title_j.startswith(title_i):
                    similar = True
                elif SequenceMatcher(None, title_i, title_j).ratio() > 0.9:
                    similar = True

                if similar:
                    for key, value in other.items():
                        if value and (key not in combined or not combined[key]):
                            combined[key] = value
                    used.add(j)

            merged.append(combined)

        return merged

    async def extract(self, url: str) -> ExtractorResult:
        """Extract products from any page using LLM."""
        strategy = self._create_strategy()
        try:
            browser_config = get_browser_config(self.stealth_level)
            crawler_config = get_crawl_config(
                stealth_level=self.stealth_level,
                extraction_strategy=strategy,
                markdown_generator=self._create_markdown_generator(),
            )

            crawler_strategy = get_crawler_strategy(self.stealth_level, browser_config)
            async with AsyncWebCrawler(
                config=browser_config,
                crawler_strategy=crawler_strategy,
            ) as crawler:
                result = await crawler.arun(url=url, config=crawler_config)

                if not result.success:
                    return ExtractorResult(products=[], complete=False, error=f"Crawl failed: {result.error_message}")

                if not result.extracted_content:
                    return ExtractorResult(products=[], complete=False, error="No content extracted")

                try:
                    extracted = json.loads(result.extracted_content)
                except json.JSONDecodeError as e:
                    return ExtractorResult(products=[], complete=False, error=f"JSON parse error: {e}")

                if isinstance(extracted, dict):
                    products = [extracted] if extracted.get("title") else []
                elif isinstance(extracted, list):
                    products = [p for p in extracted if isinstance(p, dict) and p.get("title")]
                else:
                    products = []

                products = self._merge_chunk_products(products)
                return ExtractorResult(products=products)

        except Exception as e:
            logger.exception("LLM extraction failed for %s: %s", url, e)
            return ExtractorResult(products=[], complete=False, error=str(e))

    async def extract_batch(self, urls: list[str]) -> ExtractorResult:
        """Extract from multiple URLs using a single browser instance."""
        if not urls:
            return ExtractorResult(products=[])

        strategy = self._create_strategy()
        browser_config = get_browser_config(self.stealth_level)
        crawler_config = get_crawl_config(
            stealth_level=self.stealth_level,
            extraction_strategy=strategy,
            markdown_generator=self._create_markdown_generator(),
        )
        dispatcher = MemoryAdaptiveDispatcher(
            max_session_permit=5,
            memory_threshold_percent=70.0,
        )

        all_products = []
        error: str | None = None
        try:
            crawler_strategy = get_crawler_strategy(self.stealth_level, browser_config)
            async with AsyncWebCrawler(
                config=browser_config,
                crawler_strategy=crawler_strategy,
            ) as crawler:
                results = await crawler.arun_many(
                    urls=urls, config=crawler_config, dispatcher=dispatcher,
                )
                for result in results:
                    if not result.success or not result.extracted_content:
                        continue
                    try:
                        extracted = json.loads(result.extracted_content)
                        if isinstance(extracted, dict):
                            url_products = [extracted] if extracted.get("title") else []
                        elif isinstance(extracted, list):
                            url_products = [p for p in extracted if isinstance(p, dict) and p.get("title")]
                        else:
                            url_products = []
                        url_products = self._merge_chunk_products(url_products)
                        all_products.extend(url_products)
                    except json.JSONDecodeError as e:
                        logger.debug("Failed to parse LLM extracted content for %s: %s", result.url, e)
        except Exception as e:
            logger.exception("Batch LLM extraction failed: %s", e)
            error = str(e)

        return ExtractorResult(products=all_products, complete=error is None, error=error)
