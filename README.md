# shopextract

Extract, compare, and monitor product data from any e-commerce store.

## Installation

```bash
pip install shopextract
```

## Quick Start

```python
import asyncio
import shopextract

async def main():
    # Detect platform
    result = await shopextract.detect("https://example-store.com")
    print(result.platform)  # shopify, woocommerce, magento, etc.

    # Extract products
    result = await shopextract.extract("https://example-store.com")
    for product in result.products:
        print(f"{product.title}: {product.price} {product.currency}")

asyncio.run(main())
```

## License

MIT
