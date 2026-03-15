"""Catalog diff between two stores (#9)."""

from __future__ import annotations

import asyncio
import logging

from .._extract import extract
from .._models import CatalogDiff, Product
from .match import _title_similarity

logger = logging.getLogger(__name__)

_DEFAULT_MAX_PRODUCTS = 200
_MATCH_THRESHOLD = 0.8


async def compare_catalogs(
    store_a: str,
    store_b: str,
    *,
    max_products: int = _DEFAULT_MAX_PRODUCTS,
    threshold: float = _MATCH_THRESHOLD,
) -> CatalogDiff:
    """Compare two store catalogs and report differences.

    Extracts both catalogs, fuzzy-matches products by title,
    and categorizes into only_in_a, only_in_b, in_both,
    cheaper_in_a, cheaper_in_b.
    """
    result_a, result_b = await asyncio.gather(
        extract(store_a, max_urls=max_products),
        extract(store_b, max_urls=max_products),
    )
    return _diff_catalogs(
        store_a, store_b,
        result_a.products, result_b.products,
        threshold,
    )


def _diff_catalogs(
    store_a: str,
    store_b: str,
    products_a: list[Product],
    products_b: list[Product],
    threshold: float,
) -> CatalogDiff:
    """Build catalog diff from two product lists."""
    diff = CatalogDiff(store_a=store_a, store_b=store_b)
    matched_b: set[int] = set()

    for prod_a in products_a:
        best = _find_best_match(prod_a, products_b, matched_b, threshold)
        if best is None:
            diff.only_in_a.append(prod_a)
        else:
            idx, prod_b = best
            matched_b.add(idx)
            diff.in_both.append((prod_a, prod_b))
            _classify_price(diff, prod_a, prod_b)

    for idx, prod_b in enumerate(products_b):
        if idx not in matched_b:
            diff.only_in_b.append(prod_b)

    return diff


def _find_best_match(
    product: Product,
    candidates: list[Product],
    used: set[int],
    threshold: float,
) -> tuple[int, Product] | None:
    """Find the best title match above threshold."""
    best_sim = 0.0
    best_idx = -1
    for idx, candidate in enumerate(candidates):
        if idx in used:
            continue
        sim = _title_similarity(product.title, candidate.title)
        if sim > best_sim:
            best_sim = sim
            best_idx = idx
    if best_sim >= threshold and best_idx >= 0:
        return best_idx, candidates[best_idx]
    return None


def _classify_price(
    diff: CatalogDiff,
    prod_a: Product,
    prod_b: Product,
) -> None:
    """Classify a matched pair by price difference."""
    if prod_a.price < prod_b.price:
        diff.cheaper_in_a.append((prod_a, prod_b))
    elif prod_b.price < prod_a.price:
        diff.cheaper_in_b.append((prod_a, prod_b))
