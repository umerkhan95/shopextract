"""CLI entry point for shopextract."""

from __future__ import annotations

import asyncio
import json
import sys


def main():
    """Main CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: shopextract <command> <url>")
        print()
        print("Commands:")
        print("  detect <url>     Detect e-commerce platform")
        print("  discover <url>   Discover product URLs")
        print("  extract <url>    Extract products from store")
        print("  extract-one <url>  Extract single product page")
        print("  from-feed <url>  Parse Google Shopping feed")
        sys.exit(1)

    command = sys.argv[1]
    if len(sys.argv) < 3:
        print(f"Error: {command} requires a URL argument")
        sys.exit(1)

    url = sys.argv[2]

    if command == "detect":
        asyncio.run(_detect(url))
    elif command == "discover":
        asyncio.run(_discover(url))
    elif command == "extract":
        asyncio.run(_extract(url))
    elif command == "extract-one":
        asyncio.run(_extract_one(url))
    elif command == "from-feed":
        asyncio.run(_from_feed(url))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


async def _detect(url: str):
    from . import detect
    result = await detect(url)
    print(json.dumps({
        "platform": result.platform.value,
        "confidence": result.confidence,
        "signals": result.signals,
    }, indent=2))


async def _discover(url: str):
    from . import discover
    urls = await discover(url)
    for u in urls:
        print(u)


async def _extract(url: str):
    from . import extract
    result = await extract(url)
    print(json.dumps({
        "platform": result.platform.value,
        "tier": result.tier.value,
        "quality_score": result.quality_score,
        "product_count": result.product_count,
        "urls_attempted": result.urls_attempted,
        "urls_succeeded": result.urls_succeeded,
        "products": [
            {
                "title": p.title,
                "price": str(p.price),
                "currency": p.currency,
                "image_url": p.image_url,
                "product_url": p.product_url,
                "sku": p.sku,
                "gtin": p.gtin,
                "vendor": p.vendor,
                "in_stock": p.in_stock,
            }
            for p in result.products[:10]  # Show first 10
        ],
    }, indent=2))


async def _extract_one(url: str):
    from . import extract_one
    result = await extract_one(url)
    print(json.dumps(result, indent=2, default=str))


async def _from_feed(url: str):
    from . import from_feed
    result = await from_feed(url)
    print(json.dumps({
        "tier": result.tier.value,
        "quality_score": result.quality_score,
        "product_count": result.product_count,
        "products": [
            {
                "title": p.title,
                "price": str(p.price),
                "currency": p.currency,
                "gtin": p.gtin,
                "vendor": p.vendor,
            }
            for p in result.products[:10]
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
