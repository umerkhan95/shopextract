"""Catalog diff between two stores (#9)."""

from __future__ import annotations

import asyncio
import logging

from .._extract import extract
from .._models import CatalogDiff, Product
from .identity_match import MatchRelation, SemanticCandidates, match_products

logger = logging.getLogger(__name__)

_DEFAULT_MAX_PRODUCTS = 200
_MATCH_THRESHOLD = 0.8


async def compare_catalogs(
    store_a: str,
    store_b: str,
    *,
    max_products: int = _DEFAULT_MAX_PRODUCTS,
    threshold: float = _MATCH_THRESHOLD,
    semantic_candidates: SemanticCandidates | None = None,
    publisher_aliases: dict[str, list[str]] | None = None,
    enrich_identifiers: bool = False,
    restore_short_gtin: bool = False,
) -> CatalogDiff:
    """Compare two store catalogs and report differences.

    Extracts both catalogs, accepts unique evidence-backed exact matches,
    and categorizes into only_in_a, only_in_b, in_both,
    cheaper_in_a, cheaper_in_b.
    """
    result_a, result_b = await asyncio.gather(
        extract(store_a, max_urls=max_products, enrich_identifiers=enrich_identifiers, restore_short_gtin=restore_short_gtin),
        extract(store_b, max_urls=max_products, enrich_identifiers=enrich_identifiers, restore_short_gtin=restore_short_gtin),
    )
    return _diff_catalogs(
        store_a, store_b,
        result_a.products, result_b.products,
        threshold, semantic_candidates=semantic_candidates, publisher_aliases=publisher_aliases,
    )


def _diff_catalogs(
    store_a: str,
    store_b: str,
    products_a: list[Product],
    products_b: list[Product],
    threshold: float,
    *,
    semantic_candidates: SemanticCandidates | None = None,
    publisher_aliases: dict[str, list[str]] | None = None,
) -> CatalogDiff:
    """Build catalog diff from two product lists."""
    diff = CatalogDiff(store_a=store_a, store_b=store_b)
    diff.match_report = match_products(products_a, products_b, threshold=threshold, semantic_candidates=semantic_candidates, publisher_aliases=publisher_aliases)
    matched_a, matched_b = set(), set()
    for decision in diff.match_report:
        if decision.relation != MatchRelation.EXACT or decision.needs_review:
            continue
        i, j = decision.index_a, decision.index_b
        prod_a, prod_b = products_a[i], products_b[j]
        matched_a.add(i)
        matched_b.add(j)
        diff.in_both.append((prod_a, prod_b))
        if prod_a.currency == prod_b.currency:
            _classify_price(diff, prod_a, prod_b)
    diff.only_in_a = [p for i, p in enumerate(products_a) if i not in matched_a]
    diff.only_in_b = [p for j, p in enumerate(products_b) if j not in matched_b]
    return diff


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
