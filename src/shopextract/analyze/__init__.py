"""Catalog analysis and competitive intelligence.

Public API:
    analyze(url) -> CatalogStats (async convenience wrapper)
    analyze_products(products) -> CatalogStats
    price_distribution(products) -> dict[str, int]
    outliers(products) -> list[dict]
    brand_breakdown(products) -> dict[str, float]
    price_position(my_product, competitors) -> PricePosition
    assortment_gaps(my_store, competitors) -> AssortmentGaps
    brand_coverage(catalogs) -> dict[str, dict[str, int]]
"""

from .competitive import assortment_gaps, brand_coverage, price_position
from .stats import (
    analyze,
    analyze_products,
    brand_breakdown,
    outliers,
    price_distribution,
)

__all__ = [
    "analyze",
    "analyze_products",
    "price_distribution",
    "outliers",
    "brand_breakdown",
    "price_position",
    "assortment_gaps",
    "brand_coverage",
]
