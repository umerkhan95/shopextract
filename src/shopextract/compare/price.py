"""Cross-store price comparison (#8)."""

from __future__ import annotations

import asyncio
import logging
from decimal import Decimal

from .._extract import extract
from .._models import ComparisonResult, Match
from .match import _title_similarity

logger = logging.getLogger(__name__)

_DEFAULT_MAX_PER_STORE = 50
_DEFAULT_THRESHOLD = 0.6


async def compare(
    query: str,
    stores: list[str],
    *,
    max_per_store: int = _DEFAULT_MAX_PER_STORE,
    threshold: float = _DEFAULT_THRESHOLD,
) -> ComparisonResult:
    """Compare prices for a product query across multiple stores.

    Extracts products from each store, fuzzy-matches titles against
    the query, and returns matches sorted by price.
    """
    tasks = [extract(store, max_urls=max_per_store) for store in stores]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    matches = _collect_matches(query, stores, results, threshold)
    return _build_result(query, matches)


def _collect_matches(
    query: str,
    stores: list[str],
    results: list,
    threshold: float,
) -> list[Match]:
    """Collect matching products from extraction results."""
    matches: list[Match] = []
    for store, result in zip(stores, results):
        if isinstance(result, Exception):
            logger.warning("Extraction failed for %s: %s", store, result)
            continue
        for product in result.products:
            sim = _title_similarity(query, product.title)
            if sim >= threshold:
                matches.append(Match(
                    title=product.title,
                    price=product.price,
                    currency=product.currency,
                    store=store,
                    product_url=product.product_url,
                    similarity=sim,
                ))
    return matches


def _build_result(query: str, matches: list[Match]) -> ComparisonResult:
    """Build ComparisonResult from collected matches."""
    matches.sort(key=lambda m: m.price)
    result = ComparisonResult(query=query, matches=matches)
    if not matches:
        return result

    result.cheapest = matches[0]
    result.most_expensive = matches[-1]
    prices = [m.price for m in matches]
    result.avg_price = Decimal(str(sum(prices) / len(prices)))
    result.price_spread = max(prices) - min(prices)
    return result
