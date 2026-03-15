"""Compare product prices across multiple stores.

Demonstrates:
- Cross-store price comparison
- Fuzzy product matching
- GTIN-based exact matching
- Catalog diff between two stores

Usage:
    python examples/price_comparison.py
"""

import asyncio

import shopextract


async def main() -> None:
    stores = [
        "https://store-a.com",
        "https://store-b.com",
        "https://store-c.com",
    ]

    # --- Cross-store price comparison ---
    print("--- Price Comparison ---")
    result = await shopextract.compare(
        "Wireless Headphones",
        stores=stores,
        max_per_store=30,
        threshold=0.6,
    )

    print(f"Query: '{result.query}'")
    print(f"Matches found: {len(result.matches)}")

    if result.cheapest:
        print(f"Cheapest: {result.cheapest.price} {result.cheapest.currency} at {result.cheapest.store}")
    if result.most_expensive:
        print(f"Most expensive: {result.most_expensive.price} {result.most_expensive.currency} at {result.most_expensive.store}")
    print(f"Average price: {result.avg_price}")
    print(f"Price spread: {result.price_spread}")

    print("\nAll matches (sorted by price):")
    for match in result.matches:
        print(f"  {match.price} {match.currency} - {match.title}")
        print(f"    Store: {match.store} (similarity: {match.similarity:.0%})")

    # --- Catalog diff ---
    print("\n--- Catalog Diff ---")
    diff = await shopextract.compare_catalogs(
        "https://store-a.com",
        "https://store-b.com",
        max_products=50,
    )

    print(f"Store A: {diff.store_a}")
    print(f"Store B: {diff.store_b}")
    print(f"Only in A: {len(diff.only_in_a)} products")
    print(f"Only in B: {len(diff.only_in_b)} products")
    print(f"In both: {len(diff.in_both)} products")
    print(f"Cheaper in A: {len(diff.cheaper_in_a)}")
    print(f"Cheaper in B: {len(diff.cheaper_in_b)}")

    # Show price differences for matched products
    for prod_a, prod_b in diff.cheaper_in_a[:3]:
        print(f"\n  {prod_a.title}")
        print(f"    A: {prod_a.price} {prod_a.currency}")
        print(f"    B: {prod_b.price} {prod_b.currency}")

    # --- Fuzzy matching between product lists ---
    print("\n--- Fuzzy Matching ---")
    products_a = [
        {"title": "Blue Cotton T-Shirt", "price": 19.99},
        {"title": "Red Running Shoes", "price": 89.99},
    ]
    products_b = [
        {"title": "Blue Cotton Tee", "price": 22.99},
        {"title": "Red Running Sneakers", "price": 79.99},
        {"title": "Black Leather Belt", "price": 34.99},
    ]

    matches = shopextract.fuzzy_match(products_a, products_b, threshold=0.5)
    for prod_a, prod_b, similarity in matches:
        print(f"  '{prod_a['title']}' <-> '{prod_b['title']}' ({similarity:.0%} similar)")

    # --- GTIN matching ---
    print("\n--- GTIN Matching ---")
    catalog = [
        {"title": "Product A", "gtin": "4260442152415", "price": 29.99},
        {"title": "Product B", "sku": "SKU-12345", "price": 39.99},
        {"title": "Product C", "gtin": "0012345678905", "price": 49.99},
    ]

    found = shopextract.match_gtin("4260442152415", catalog)
    print(f"Found {len(found)} products matching GTIN 4260442152415")
    for product in found:
        print(f"  {product['title']} - {product['price']}")


if __name__ == "__main__":
    asyncio.run(main())
