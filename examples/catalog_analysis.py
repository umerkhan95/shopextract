"""Analyze a store's product catalog.

Demonstrates:
- Catalog statistics (price range, brands, completeness)
- Price distribution buckets
- Outlier detection
- Brand breakdown

Usage:
    python examples/catalog_analysis.py
"""

import asyncio

import shopextract


async def main() -> None:
    store_url = "https://example-store.com"

    # --- Full catalog analysis from URL ---
    print("--- Catalog Analysis ---")
    stats = await shopextract.analyze(store_url, max_products=50)

    print(f"Total products: {stats.total_products}")
    print(f"Price range: {stats.price_range[0]} - {stats.price_range[1]}")
    print(f"Average price: {stats.avg_price}")
    print(f"Median price: {stats.median_price}")
    print(f"In stock: {stats.in_stock}")
    print(f"Out of stock: {stats.out_of_stock}")
    print(f"Have GTIN: {stats.has_gtin}")
    print(f"Have images: {stats.has_images}")
    print(f"Completeness: {stats.completeness_score:.0%}")

    if stats.currencies:
        print(f"\nCurrencies: {stats.currencies}")

    if stats.brands:
        print(f"\nTop brands:")
        for brand, count in list(stats.brands.items())[:10]:
            print(f"  {brand}: {count} products")

    if stats.categories:
        print(f"\nTop categories:")
        for cat, count in list(stats.categories.items())[:10]:
            print(f"  {cat}: {count} products")

    # --- Analysis on raw product data ---
    # You can also analyze products you already have
    print("\n--- Analysis on Sample Data ---")
    sample_products = [
        {"title": "Widget A", "price": 19.99, "vendor": "Acme", "image_url": "https://...", "gtin": "1234567890123"},
        {"title": "Widget B", "price": 29.99, "vendor": "Acme", "image_url": "https://..."},
        {"title": "Gadget X", "price": 149.99, "vendor": "TechCo", "image_url": "https://...", "gtin": "9876543210987"},
        {"title": "Gadget Y", "price": 199.99, "vendor": "TechCo"},
        {"title": "Premium Z", "price": 999.99, "vendor": "LuxBrand", "image_url": "https://...", "gtin": "5555555555555"},
    ]

    stats = shopextract.analyze_products(sample_products)
    print(f"Products: {stats.total_products}")
    print(f"Avg price: {stats.avg_price}")
    print(f"Completeness: {stats.completeness_score:.0%}")

    # --- Price distribution ---
    print("\n--- Price Distribution ---")
    dist = shopextract.price_distribution(sample_products)
    for bucket, count in dist.items():
        bar = "#" * count
        print(f"  {bucket:>10}: {bar} ({count})")

    # --- Outliers ---
    print("\n--- Price Outliers ---")
    weird = shopextract.outliers(sample_products, std_multiplier=1.5)
    if weird:
        for p in weird:
            print(f"  Outlier: {p['title']} at {p['price']}")
    else:
        print("  No outliers detected")

    # --- Brand breakdown ---
    print("\n--- Brand Breakdown ---")
    brands = shopextract.brand_breakdown(sample_products)
    for brand, pct in brands.items():
        bar = "#" * int(pct / 5)
        print(f"  {brand:>10}: {bar} {pct}%")


if __name__ == "__main__":
    asyncio.run(main())
