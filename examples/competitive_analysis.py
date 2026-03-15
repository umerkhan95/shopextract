"""Competitive analysis: price positioning and assortment gaps.

Demonstrates:
- Price position ranking against competitors
- Assortment gap analysis (missing categories and brands)
- Brand coverage across multiple stores

Usage:
    python examples/competitive_analysis.py
"""

import asyncio

import shopextract


async def main() -> None:
    my_store = "https://my-store.com"
    competitors = [
        "https://competitor-a.com",
        "https://competitor-b.com",
    ]

    # --- Price Position ---
    print("--- Price Position ---")
    my_product = {
        "title": "Premium Coffee Beans 1kg",
        "price": 24.99,
    }

    position = await shopextract.price_position(
        my_product,
        competitors=competitors,
        max_products=50,
    )

    print(f"Product: {position.product_title}")
    print(f"My price: {position.my_price}")
    print(f"Rank: #{position.rank} out of {position.total_competitors + 1}")
    print(f"Percentile: {position.percentile}% (higher = cheaper)")
    print(f"Market average: {position.market_avg}")
    print(f"Cheapest in market: {position.cheapest}")
    print(f"Most expensive in market: {position.most_expensive}")

    if position.competitor_prices:
        print("\nCompetitor prices:")
        for store, price in position.competitor_prices.items():
            marker = " <-- cheaper" if price < position.my_price else ""
            print(f"  {store}: {price}{marker}")

    # --- Assortment Gaps ---
    print("\n--- Assortment Gaps ---")
    gaps = await shopextract.assortment_gaps(
        my_store,
        competitors=competitors,
        max_products=50,
    )

    print(f"My categories: {', '.join(gaps.my_categories[:10]) or 'None found'}")
    print(f"My brands: {', '.join(gaps.my_brands[:10]) or 'None found'}")

    if gaps.missing_categories:
        print(f"\nMissing categories (competitors have, I don't):")
        for cat in gaps.missing_categories[:10]:
            print(f"  - {cat}")

    if gaps.missing_brands:
        print(f"\nMissing brands (competitors carry, I don't):")
        for brand in gaps.missing_brands[:10]:
            print(f"  - {brand}")

    # --- Brand Coverage ---
    # This uses pre-extracted product data (no network calls)
    print("\n--- Brand Coverage (from local data) ---")
    catalogs = {
        "my-store": [
            {"title": "Nike Air Max", "vendor": "Nike", "price": 120},
            {"title": "Nike Pegasus", "vendor": "Nike", "price": 130},
            {"title": "Adidas Ultra Boost", "vendor": "Adidas", "price": 180},
        ],
        "competitor-a": [
            {"title": "Nike Air Force", "vendor": "Nike", "price": 100},
            {"title": "Puma RS-X", "vendor": "Puma", "price": 110},
            {"title": "New Balance 990", "vendor": "New Balance", "price": 175},
        ],
        "competitor-b": [
            {"title": "Adidas Samba", "vendor": "Adidas", "price": 100},
            {"title": "Nike Dunk", "vendor": "Nike", "price": 110},
            {"title": "Adidas Stan Smith", "vendor": "Adidas", "price": 85},
            {"title": "Puma Suede", "vendor": "Puma", "price": 75},
        ],
    }

    coverage = shopextract.brand_coverage(catalogs)

    # Print as a comparison table
    stores = list(catalogs.keys())
    header = f"{'Brand':<15}" + "".join(f"{s:<15}" for s in stores)
    print(header)
    print("-" * len(header))

    for brand, store_counts in coverage.items():
        row = f"{brand:<15}"
        for store in stores:
            count = store_counts.get(store, 0)
            row += f"{count:<15}"
        print(row)


if __name__ == "__main__":
    asyncio.run(main())
