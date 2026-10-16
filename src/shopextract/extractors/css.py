"""CSS-based product data extractor using crawl4ai."""

from __future__ import annotations

import json
import logging

from bs4 import BeautifulSoup
from crawl4ai import AsyncWebCrawler
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

from .._models import ExtractorResult
from .._capture import capture
from ._browser import (
    StealthLevel,
    get_browser_config,
    get_crawl_config,
    get_crawler_strategy,
)

logger = logging.getLogger(__name__)


class CSSExtractor:
    """Extract product data using CSS selectors via crawl4ai JsonCssExtractionStrategy."""

    _ESCALATION_ORDER = [StealthLevel.STANDARD, StealthLevel.STEALTH, StealthLevel.UNDETECTED]

    def __init__(self, schema: dict, stealth_level: StealthLevel = StealthLevel.STANDARD):
        self.schema = schema
        self.stealth_level = stealth_level

    def _parse_extracted_content(self, url: str, result) -> list[dict]:
        if not result.success:
            return []
        if not result.extracted_content:
            return []
        try:
            extracted_data = json.loads(result.extracted_content)
        except json.JSONDecodeError:
            return []

        if isinstance(extracted_data, dict):
            products = [extracted_data] if extracted_data else []
        elif isinstance(extracted_data, list):
            products = extracted_data
        else:
            return []
        return self._capture_products(products, result, url)

    async def extract(self, url: str) -> ExtractorResult:
        """Extract product data with stealth escalation."""
        start_idx = self._ESCALATION_ORDER.index(self.stealth_level)
        levels = self._ESCALATION_ORDER[start_idx:]

        if not levels:
            return ExtractorResult(products=[], complete=False, error="No stealth levels to try")

        max_level = levels[-1]
        browser_config = get_browser_config(max_level)
        crawler_strategy = get_crawler_strategy(max_level, browser_config)

        try:
            async with AsyncWebCrawler(
                config=browser_config,
                crawler_strategy=crawler_strategy,
            ) as crawler:
                for level in levels:
                    extraction_strategy = JsonCssExtractionStrategy(self.schema, verbose=False)
                    crawler_config = get_crawl_config(
                        stealth_level=level,
                        extraction_strategy=extraction_strategy,
                    )
                    try:
                        result = await crawler.arun(url=url, config=crawler_config)
                        products = self._parse_extracted_content(url, result)
                        if products:
                            return ExtractorResult(products=products)
                    except Exception as e:
                        logger.debug("CSS extraction at stealth level %s failed for %s: %s", level.value, url, e)
                        continue
        except Exception as e:
            logger.exception("CSS browser startup failed for %s: %s", url, e)

        return ExtractorResult(products=[], complete=False, error="All stealth levels exhausted")

    async def extract_batch(self, urls: list[str]) -> ExtractorResult:
        """Extract from multiple URLs using a single browser instance."""
        if not urls:
            return ExtractorResult(products=[])

        browser_config = get_browser_config(self.stealth_level)
        extraction_strategy = JsonCssExtractionStrategy(self.schema, verbose=False)
        crawler_config = get_crawl_config(
            stealth_level=self.stealth_level,
            extraction_strategy=extraction_strategy,
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
                results = await crawler.arun_many(urls=urls, config=crawler_config, dispatcher=dispatcher)
                for result in results:
                    if not result.success or not result.extracted_content:
                        continue
                    try:
                        all_products.extend(self._parse_extracted_content(result.url, result))
                    except json.JSONDecodeError as e:
                        logger.debug("Failed to parse extracted content for %s: %s", result.url, e)
        except Exception as e:
            logger.exception("Batch CSS extraction failed: %s", e)
            error = str(e)

        return ExtractorResult(products=all_products, complete=error is None, error=error)

    def _capture_products(self, products, result, url):
        html = getattr(result, 'html', '') or ''
        source_url = getattr(result, 'url', None) or url
        soup = BeautifulSoup(html, 'html.parser')
        try:
            bases = soup.select(self.schema.get('baseSelector', 'body'))
        except Exception:
            bases = []
        for product in products:
            if not isinstance(product, dict):
                continue
            candidates = []
            for base in bases:
                values, nodes = {}, {}
                for field in self.schema.get('fields', []):
                    key = field.get('name')
                    try:
                        node = base.select_one(field.get('selector', ''))
                    except Exception:
                        continue
                    if node is None:
                        continue
                    if field.get('type') == 'attribute':
                        value = node.get(field.get('attribute', ''))
                    elif field.get('type') == 'text':
                        value = node.get_text(strip=True)
                    else:
                        continue
                    if key in product and value == product[key]:
                        values[key], nodes[key] = value, str(node)
                required = {f.get('name') for f in self.schema.get('fields', [])
                            if f.get('name') in product and product[f.get('name')] not in (None, '')}
                if required and required <= values.keys():
                    candidates.append((values, nodes))
            values, nodes = candidates[0] if len(candidates) == 1 else ({}, {})
            capture(product, source_url, 'css', source=values,
                    excerpt=json.dumps(nodes, ensure_ascii=False) if nodes else None)
        return [p for p in products if isinstance(p, dict)]
