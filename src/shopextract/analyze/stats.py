"""Catalog statistics and price analysis.

Pure functions operating on lists of product dicts. No external dependencies
beyond the Python stdlib statistics module.
"""

from __future__ import annotations

import statistics
from decimal import Decimal, InvalidOperation

from .._models import CatalogStats


def analyze_products(products: list[dict]) -> CatalogStats:
    """Compute aggregate statistics for a product catalog.

    Args:
        products: List of raw product dicts (as returned by extractors).

    Returns:
        CatalogStats with counts, averages, and completeness score.
    """
    if not products:
        return CatalogStats()

    prices = _extract_prices(products)
    currencies = count_field(products, "currency")
    brands = count_field(products, "vendor")
    categories = count_categories(products)

    in_stock = sum(1 for p in products if _is_in_stock(p))
    has_gtin = sum(1 for p in products if _has_value(p, "gtin"))
    has_images = sum(1 for p in products if _has_image(p))

    return CatalogStats(
        total_products=len(products),
        price_range=_price_range(prices),
        avg_price=_safe_mean(prices),
        median_price=_safe_median(prices),
        currencies=currencies,
        brands=brands,
        categories=categories,
        in_stock=in_stock,
        out_of_stock=len(products) - in_stock,
        has_gtin=has_gtin,
        has_images=has_images,
        completeness_score=_completeness_score(products),
    )


def price_distribution(
    products: list[dict],
    buckets: list[float] | None = None,
) -> dict[str, int]:
    """Distribute products into price buckets.

    Args:
        products: List of raw product dicts.
        buckets: Bucket boundaries. Defaults to [0, 10, 25, 50, 100, 250, 500, 1000].

    Returns:
        Dict mapping bucket label to product count.
    """
    if buckets is None:
        buckets = [0, 10, 25, 50, 100, 250, 500, 1000]

    prices = _extract_prices(products)
    buckets = sorted(buckets)
    result: dict[str, int] = {}

    for i in range(len(buckets)):
        low = buckets[i]
        high = buckets[i + 1] if i + 1 < len(buckets) else float("inf")
        label = f"{low}-{high}" if high != float("inf") else f"{low}+"
        result[label] = sum(1 for p in prices if low <= p < high)

    return result


def outliers(
    products: list[dict],
    std_multiplier: float = 2.0,
) -> list[dict]:
    """Find products with prices outside std_multiplier standard deviations.

    Args:
        products: List of raw product dicts.
        std_multiplier: Number of standard deviations for outlier threshold.

    Returns:
        List of product dicts that are price outliers.
    """
    prices = _extract_prices(products)
    if len(prices) < 2:
        return []

    mean = statistics.mean(prices)
    stdev = statistics.stdev(prices)
    if stdev == 0:
        return []

    lower = mean - std_multiplier * stdev
    upper = mean + std_multiplier * stdev

    return [
        p for p in products
        if (price := get_price(p)) is not None and (price < lower or price > upper)
    ]


def brand_breakdown(products: list[dict]) -> dict[str, float]:
    """Percentage of catalog per brand.

    Args:
        products: List of raw product dicts.

    Returns:
        Dict mapping brand name to percentage (0-100).
    """
    brands = count_field(products, "vendor")
    total = sum(brands.values())
    if total == 0:
        return {}
    return {brand: round(count / total * 100, 2) for brand, count in brands.items()}


async def analyze(url: str, max_products: int = 500) -> CatalogStats:
    """Extract products from a store URL and return catalog statistics.

    Convenience wrapper that combines extraction with analysis.

    Args:
        url: E-commerce store URL.
        max_products: Maximum products to extract.

    Returns:
        CatalogStats for the store.
    """
    from .._extract import extract

    result = await extract(url, max_urls=max_products)
    raw = result.raw_products if result.raw_products else [
        _product_to_dict(p) for p in result.products
    ]
    return analyze_products(raw)


# -- Internal helpers --------------------------------------------------------


def _extract_prices(products: list[dict]) -> list[float]:
    """Extract valid positive prices from product dicts."""
    prices: list[float] = []
    for p in products:
        price = get_price(p)
        if price is not None and price > 0:
            prices.append(price)
    return prices


def get_price(product: dict) -> float | None:
    """Safely extract price as float from a product dict."""
    raw = product.get("price")
    if raw is None:
        return None
    try:
        val = float(Decimal(str(raw)))
        return val if val > 0 else None
    except (InvalidOperation, ValueError, TypeError):
        return None


def _price_range(prices: list[float]) -> tuple[float, float]:
    """Return (min, max) from a list of prices."""
    if not prices:
        return (0.0, 0.0)
    return (round(min(prices), 2), round(max(prices), 2))


def _safe_mean(prices: list[float]) -> float:
    """Mean price, or 0 if empty."""
    return round(statistics.mean(prices), 2) if prices else 0.0


def _safe_median(prices: list[float]) -> float:
    """Median price, or 0 if empty."""
    return round(statistics.median(prices), 2) if prices else 0.0


def count_field(products: list[dict], field: str) -> dict[str, int]:
    """Count occurrences of a string field across products."""
    counts: dict[str, int] = {}
    for p in products:
        val = p.get(field)
        if val and isinstance(val, str) and val.strip():
            key = val.strip()
            counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def count_categories(products: list[dict]) -> dict[str, int]:
    """Count category occurrences (supports category_path lists and product_type)."""
    counts: dict[str, int] = {}
    for p in products:
        cats = p.get("category_path", [])
        if isinstance(cats, list):
            for cat in cats:
                if cat and isinstance(cat, str):
                    counts[cat] = counts.get(cat, 0) + 1
        pt = p.get("product_type")
        if pt and isinstance(pt, str) and pt.strip():
            counts[pt.strip()] = counts.get(pt.strip(), 0) + 1
    return dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))


def _is_in_stock(product: dict) -> bool:
    """Check if product is in stock (defaults to True)."""
    return product.get("in_stock", True)


def _has_value(product: dict, field: str) -> bool:
    """Check if a field has a truthy non-empty string value."""
    val = product.get(field)
    return bool(val and isinstance(val, str) and val.strip())


def _has_image(product: dict) -> bool:
    """Check if product has at least one image."""
    if _has_value(product, "image_url"):
        return True
    additional = product.get("additional_images", [])
    return bool(additional and isinstance(additional, list) and len(additional) > 0)


_COMPLETENESS_FIELDS = ["title", "price", "image_url", "description", "vendor", "gtin"]


def _completeness_score(products: list[dict]) -> float:
    """Average field completeness across products (0.0-1.0)."""
    if not products:
        return 0.0
    total = 0.0
    for p in products:
        filled = sum(1 for f in _COMPLETENESS_FIELDS if _field_present(p, f))
        total += filled / len(_COMPLETENESS_FIELDS)
    return round(total / len(products), 4)


def _field_present(product: dict, field: str) -> bool:
    """Check if a field is meaningfully present."""
    val = product.get(field)
    if val is None:
        return False
    if isinstance(val, str):
        return bool(val.strip())
    if isinstance(val, (int, float, Decimal)):
        return val > 0
    return bool(val)


def _product_to_dict(product: object) -> dict:
    """Convert a Product dataclass to dict for analysis."""
    if hasattr(product, "__dataclass_fields__"):
        from dataclasses import asdict
        return asdict(product)
    return {}
