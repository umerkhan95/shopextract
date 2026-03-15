"""Competitive intelligence: price positioning, assortment gaps, brand coverage.

Functions that compare your store against competitors using extracted product data.
"""

from __future__ import annotations

import statistics
from difflib import SequenceMatcher

from .._models import AssortmentGaps, PricePosition
from .stats import count_categories, count_field, get_price


async def price_position(
    my_product: dict,
    competitors: list[str],
    *,
    max_products: int = 200,
) -> PricePosition:
    """Find where your product's price ranks among competitor stores.

    Extracts products from each competitor URL, fuzzy-matches the product
    by title, and returns pricing position.

    Args:
        my_product: Your product dict (must have 'title' and 'price').
        competitors: List of competitor store URLs.
        max_products: Max products to extract per competitor.

    Returns:
        PricePosition with rank, percentile, and market stats.
    """
    my_title = my_product.get("title", "")
    my_price = get_price(my_product)
    if not my_title or my_price is None:
        return PricePosition(product_title=my_title, my_price=my_price or 0.0)

    competitor_prices = await _find_competitor_prices(
        my_title, competitors, max_products
    )
    return _build_price_position(my_title, my_price, competitor_prices)


async def assortment_gaps(
    my_store: str,
    competitors: list[str],
    *,
    max_products: int = 200,
) -> AssortmentGaps:
    """Find categories and brands competitors have that you don't.

    Args:
        my_store: Your store URL.
        competitors: List of competitor store URLs.
        max_products: Max products to extract per store.

    Returns:
        AssortmentGaps with missing categories/brands and competitor distributions.
    """
    from .._extract import extract

    my_result = await extract(my_store, max_urls=max_products)
    my_products = my_result.raw_products or []

    my_cats = set(count_categories(my_products).keys())
    my_brands = set(count_field(my_products, "vendor").keys())

    comp_cat_counts: dict[str, dict[str, int]] = {}
    comp_brand_counts: dict[str, dict[str, int]] = {}
    all_comp_cats: set[str] = set()
    all_comp_brands: set[str] = set()

    for url in competitors:
        result = await extract(url, max_urls=max_products)
        raw = result.raw_products or []
        cats = count_categories(raw)
        brands = count_field(raw, "vendor")
        comp_cat_counts[url] = cats
        comp_brand_counts[url] = brands
        all_comp_cats.update(cats.keys())
        all_comp_brands.update(brands.keys())

    return AssortmentGaps(
        missing_categories=sorted(all_comp_cats - my_cats),
        missing_brands=sorted(all_comp_brands - my_brands),
        competitor_category_counts=comp_cat_counts,
        competitor_brand_counts=comp_brand_counts,
        my_categories=sorted(my_cats),
        my_brands=sorted(my_brands),
    )


def brand_coverage(catalogs: dict[str, list[dict]]) -> dict[str, dict[str, int]]:
    """Brand distribution across multiple pre-extracted catalogs.

    Args:
        catalogs: Mapping of store name/URL to list of product dicts.

    Returns:
        Dict mapping brand to dict of {store: count}.
    """
    all_brands: set[str] = set()
    store_brands: dict[str, dict[str, int]] = {}

    for store, products in catalogs.items():
        brands = count_field(products, "vendor")
        store_brands[store] = brands
        all_brands.update(brands.keys())

    result: dict[str, dict[str, int]] = {}
    for brand in sorted(all_brands):
        result[brand] = {
            store: store_brands[store].get(brand, 0)
            for store in catalogs
        }
    return result


# -- Internal helpers --------------------------------------------------------


def _fuzzy_match_score(title_a: str, title_b: str) -> float:
    """Compute similarity between two product titles."""
    a = title_a.lower().strip()
    b = title_b.lower().strip()
    return SequenceMatcher(None, a, b).ratio()


_MATCH_THRESHOLD = 0.6


def _find_best_match(
    target_title: str,
    products: list[dict],
) -> dict | None:
    """Find the product most similar to target_title above threshold."""
    best_score = 0.0
    best_product: dict | None = None

    for p in products:
        title = p.get("title", "")
        if not title:
            continue
        score = _fuzzy_match_score(target_title, title)
        if score > best_score and score >= _MATCH_THRESHOLD:
            best_score = score
            best_product = p

    return best_product


async def _find_competitor_prices(
    my_title: str,
    competitors: list[str],
    max_products: int,
) -> dict[str, float]:
    """Extract from competitors and find matching product prices."""
    from .._extract import extract

    prices: dict[str, float] = {}
    for url in competitors:
        result = await extract(url, max_urls=max_products)
        raw = result.raw_products or []
        match = _find_best_match(my_title, raw)
        if match:
            price = get_price(match)
            if price is not None:
                prices[url] = price
    return prices


def _build_price_position(
    title: str,
    my_price: float,
    competitor_prices: dict[str, float],
) -> PricePosition:
    """Build PricePosition from my price and competitor prices."""
    if not competitor_prices:
        return PricePosition(
            product_title=title,
            my_price=my_price,
            rank=1,
            total_competitors=0,
            percentile=100.0,
            market_avg=my_price,
            cheapest=my_price,
            most_expensive=my_price,
            competitor_prices={},
        )

    all_prices = list(competitor_prices.values()) + [my_price]
    sorted_prices = sorted(all_prices)
    rank = sorted_prices.index(my_price) + 1

    return PricePosition(
        product_title=title,
        my_price=my_price,
        rank=rank,
        total_competitors=len(competitor_prices),
        percentile=round((1 - (rank - 1) / len(all_prices)) * 100, 1),
        market_avg=round(statistics.mean(all_prices), 2),
        cheapest=min(all_prices),
        most_expensive=max(all_prices),
        competitor_prices=competitor_prices,
    )
