"""Basic product extraction from an e-commerce store.

Demonstrates:
- Platform detection
- Full store extraction with tiered fallback
- Single product page extraction
- Accessing product fields

Usage:
    python examples/basic_extraction.py
"""

import asyncio

import shopextract


async def main() -> None:
    store_url = "https://example-store.com"

    # Step 1: Detect what platform the store runs on
    print("--- Platform Detection ---")
    platform_result = await shopextract.detect(store_url)
    print(f"Platform: {platform_result.platform}")
    print(f"Confidence: {platform_result.confidence:.0%}")
    print(f"Signals: {', '.join(platform_result.signals)}")
    print()

    # Step 2: Discover product URLs without extracting
    print("--- URL Discovery ---")
    urls = await shopextract.discover(store_url, max_urls=20)
    print(f"Discovered {len(urls)} product URLs")
    for url in urls[:5]:
        print(f"  {url}")
    print()

    # Step 3: Extract products (handles detection + discovery + extraction)
    print("--- Full Extraction ---")
    result = await shopextract.extract(store_url, max_urls=10)

    print(f"Platform: {result.platform}")
    print(f"Extraction tier: {result.tier}")
    print(f"Quality score: {result.quality_score:.2f}")
    print(f"Products found: {result.product_count}")
    print(f"URLs attempted: {result.urls_attempted}")
    print(f"URLs succeeded: {result.urls_succeeded}")

    if result.errors:
        print(f"Errors: {result.errors}")

    print()
    for product in result.products[:5]:
        print(f"  {product.title}")
        print(f"    Price: {product.price} {product.currency}")
        print(f"    Image: {product.image_url[:80]}..." if len(product.image_url) > 80 else f"    Image: {product.image_url}")
        print(f"    GTIN: {product.gtin or 'N/A'}  SKU: {product.sku or 'N/A'}")
        print(f"    In stock: {product.in_stock}")
        if product.variants:
            print(f"    Variants: {len(product.variants)}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
