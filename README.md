# shopextract

**Extract, compare, and monitor product data from any e-commerce store.**

[![PyPI version](https://img.shields.io/pypi/v/shopextract.svg)](https://pypi.org/project/shopextract/)
[![Python versions](https://img.shields.io/pypi/pyversions/shopextract.svg)](https://pypi.org/project/shopextract/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/github/actions/workflow/status/umerkhan95/shopextract/tests.yml?label=tests)](https://github.com/umerkhan95/shopextract/actions)

No existing pip package lets you extract structured product data from any store URL with zero config. `shopextract` does. Point it at a store, get back clean product data -- titles, prices, images, GTINs, variants -- ready for analysis, comparison, or feed generation.

---

## Installation

```bash
pip install shopextract
```

Requires Python 3.10+. Includes everything: extraction, comparison, monitoring, LLM support, pandas export.

---

## Quick Start

```python
import asyncio
import shopextract

async def main():
    result = await shopextract.extract("https://example-store.com")
    for product in result.products:
        print(f"{product.title}: {product.price} {product.currency}")

asyncio.run(main())
```

Three lines. That's it.

---

## Features

### Extract products from any store

The `extract()` function handles everything -- platform detection, URL discovery, and tiered extraction with automatic fallback.

```python
import asyncio
import shopextract

async def main():
    # Extract from any store URL
    result = await shopextract.extract("https://example-store.com", max_urls=50)

    print(f"Platform: {result.platform}")       # shopify, woocommerce, magento, ...
    print(f"Tier: {result.tier}")               # api, unified_crawl, css
    print(f"Quality: {result.quality_score}")    # 0.0 - 1.0
    print(f"Products: {result.product_count}")

    for p in result.products[:5]:
        print(f"  {p.title} - {p.price} {p.currency}")
        print(f"    GTIN: {p.gtin}  SKU: {p.sku}")
        print(f"    Image: {p.image_url}")

asyncio.run(main())
```

Extract a single product page:

```python
raw = await shopextract.extract_one("https://example-store.com/products/cool-widget")
print(raw)  # {"title": "Cool Widget", "price": "29.99", ...}
```

Use LLM for hard-to-scrape sites (JS-heavy, no structured data):

```python
# With OpenAI
result = await shopextract.extract(
    "https://hard-to-scrape-store.com",
    llm_api_key="sk-...",
    llm_model="openai/gpt-4o-mini",
)

# With local Ollama (free, no API key)
result = await shopextract.extract(
    "https://hard-to-scrape-store.com",
    llm_model="ollama/llama3.1",
)

# Or set env vars and forget about it
# export OPENAI_API_KEY=sk-...
result = await shopextract.extract("https://any-store.com")
```

Import from a Google Shopping feed:

```python
result = await shopextract.from_feed("https://example-store.com/feed.xml")
print(f"Imported {result.product_count} products from feed")
```

### Detect platform

Identify which e-commerce platform a store runs on, with confidence scoring and detection signals.

```python
import asyncio
import shopextract

async def main():
    result = await shopextract.detect("https://example-store.com")
    print(f"Platform: {result.platform}")       # e.g. Platform.SHOPIFY
    print(f"Confidence: {result.confidence}")   # 0.0 - 1.0
    print(f"Signals: {result.signals}")         # ["header:x-shopify", "cdn:cdn.shopify.com", ...]

asyncio.run(main())
```

### Discover product URLs

Find all product pages on a store without extracting them.

```python
import asyncio
import shopextract

async def main():
    urls = await shopextract.discover("https://example-store.com", max_urls=100)
    print(f"Found {len(urls)} product URLs")
    for url in urls[:10]:
        print(f"  {url}")

asyncio.run(main())
```

Uses a three-phase strategy: platform API pagination, sitemap parsing (with XML safety via defusedxml), and browser-based link crawling as a fallback.

### Compare prices across stores

Search for a product across multiple stores and see who has the best price.

```python
import asyncio
import shopextract

async def main():
    result = await shopextract.compare(
        "Wireless Headphones",
        stores=[
            "https://store-a.com",
            "https://store-b.com",
            "https://store-c.com",
        ],
    )

    print(f"Found {len(result.matches)} matches for '{result.query}'")
    if result.cheapest:
        print(f"Cheapest: {result.cheapest.price} at {result.cheapest.store}")
    if result.most_expensive:
        print(f"Most expensive: {result.most_expensive.price} at {result.most_expensive.store}")
    print(f"Average price: {result.avg_price}")
    print(f"Price spread: {result.price_spread}")

asyncio.run(main())
```

Compare two entire catalogs:

```python
diff = await shopextract.compare_catalogs(
    "https://store-a.com",
    "https://store-b.com",
)
print(f"Only in A: {len(diff.only_in_a)}")
print(f"Only in B: {len(diff.only_in_b)}")
print(f"In both: {len(diff.in_both)}")
print(f"Cheaper in A: {len(diff.cheaper_in_a)}")
print(f"Cheaper in B: {len(diff.cheaper_in_b)}")
```

Match products by title similarity or GTIN:

```python
# Fuzzy title matching
matches = shopextract.fuzzy_match(products_a, products_b, threshold=0.8)
for prod_a, prod_b, similarity in matches:
    print(f"{prod_a['title']} <-> {prod_b['title']} ({similarity:.0%})")

# Exact GTIN/SKU matching
found = shopextract.match_gtin("4260442152415", all_products)
```

### Monitor stores for changes

Take snapshots over time and detect price changes, new products, and removals.

```python
import asyncio
import shopextract

async def main():
    # Take a snapshot (stored in ~/.shopextract/snapshots.db)
    count = await shopextract.snapshot("https://example-store.com")
    print(f"Snapshot saved: {count} products")

    # Later, take another snapshot and check for changes
    await shopextract.snapshot("https://example-store.com")
    detected = shopextract.changes("example-store.com")

    for change in detected:
        if change.change_type == shopextract.ChangeType.PRICE_CHANGE:
            print(f"Price changed: {change.title} {change.old_price} -> {change.new_price}")
        elif change.change_type == shopextract.ChangeType.NEW_PRODUCT:
            print(f"New product: {change.title} ({change.price})")
        elif change.change_type == shopextract.ChangeType.REMOVED_PRODUCT:
            print(f"Removed: {change.title}")

asyncio.run(main())
```

Get price history for a specific product:

```python
history = shopextract.price_history("example-store.com", "Cool Widget Pro")
for timestamp, price in history:
    print(f"  {timestamp.date()}: {price}")
```

Continuous watch mode with an async generator:

```python
async def monitor():
    async for change in shopextract.watch("https://example-store.com", interval=3600):
        print(f"[{change.change_type}] {change.title}")
```

### Analyze catalogs

Get statistical insights from extracted product data.

```python
import asyncio
import shopextract

async def main():
    # Analyze directly from a URL
    stats = await shopextract.analyze("https://example-store.com")

    print(f"Total products: {stats.total_products}")
    print(f"Price range: {stats.price_range[0]} - {stats.price_range[1]}")
    print(f"Average price: {stats.avg_price}")
    print(f"Median price: {stats.median_price}")
    print(f"In stock: {stats.in_stock} / Out of stock: {stats.out_of_stock}")
    print(f"Have GTIN: {stats.has_gtin}")
    print(f"Have images: {stats.has_images}")
    print(f"Completeness score: {stats.completeness_score:.0%}")
    print(f"Top brands: {dict(list(stats.brands.items())[:5])}")

asyncio.run(main())
```

Or analyze an already-extracted product list:

```python
# From raw product dicts
stats = shopextract.analyze_products(result.raw_products)

# Price distribution buckets
dist = shopextract.price_distribution(products)
# {"0-10": 5, "10-25": 12, "25-50": 30, "50-100": 18, "100-250": 8, ...}

# Find pricing outliers (beyond 2 standard deviations)
weird = shopextract.outliers(products, std_multiplier=2.0)
for p in weird:
    print(f"Outlier: {p['title']} at {p['price']}")

# Brand market share
brands = shopextract.brand_breakdown(products)
for brand, pct in brands.items():
    print(f"  {brand}: {pct}%")
```

### Competitive intelligence

Understand where you stand against competitors.

```python
import asyncio
import shopextract

async def main():
    # How does my product's price rank?
    my_product = {"title": "Premium Coffee Beans 1kg", "price": 24.99}
    position = await shopextract.price_position(
        my_product,
        competitors=["https://competitor-a.com", "https://competitor-b.com"],
    )
    print(f"Rank: #{position.rank} of {position.total_competitors + 1}")
    print(f"Percentile: {position.percentile}%")
    print(f"Market average: {position.market_avg}")
    print(f"Cheapest: {position.cheapest}  Most expensive: {position.most_expensive}")

    # What categories and brands am I missing?
    gaps = await shopextract.assortment_gaps(
        "https://my-store.com",
        competitors=["https://competitor-a.com", "https://competitor-b.com"],
    )
    print(f"Missing categories: {gaps.missing_categories}")
    print(f"Missing brands: {gaps.missing_brands}")

asyncio.run(main())
```

Brand coverage across multiple catalogs:

```python
coverage = shopextract.brand_coverage({
    "my-store": my_products,
    "competitor-a": comp_a_products,
    "competitor-b": comp_b_products,
})
for brand, stores in coverage.items():
    print(f"{brand}: {stores}")
# {"Nike": {"my-store": 12, "competitor-a": 25, "competitor-b": 8}, ...}
```

### Validate for marketplaces

Check if your product data meets marketplace requirements before submitting feeds.

```python
import shopextract

products = [
    {"title": "Widget", "price": 29.99, "image_url": "https://...", "product_url": "https://..."},
    {"title": "", "price": -5},  # will fail validation
]

# Validate against Google Shopping, idealo, Amazon, or eBay rules
report = shopextract.validate(products, marketplace="google_shopping")
print(f"Pass rate: {report.pass_rate:.0f}%")
print(f"Valid: {report.valid}  Invalid: {report.invalid}  Warnings: {report.warnings}")

for issue in report.issues:
    severity = "WARN" if issue.severity == "warning" else "ERROR"
    print(f"  [{severity}] #{issue.product_index}: {issue.field} - {issue.error}")
```

Check for broken image URLs:

```python
issues = await shopextract.check_images(products)
for issue in issues:
    print(f"  {issue.product_title}: {issue.error} ({issue.image_url})")
```

Find duplicate products:

```python
# By title similarity
dupes = shopextract.find_duplicates(products, method="title", threshold=0.9)
for idx_a, idx_b, similarity in dupes:
    print(f"  Duplicate: #{idx_a} <-> #{idx_b} ({similarity:.0%})")

# By exact GTIN or SKU
dupes = shopextract.find_duplicates(products, method="gtin")
```

### Export to any format

```python
import shopextract

products = [...]  # list of product dicts

# Standard formats
shopextract.to_csv(products, "products.csv")
shopextract.to_json(products, "products.json")

# Marketplace feeds
shopextract.to_feed(products, "google_feed.xml", format="google_shopping")
shopextract.to_feed(products, "idealo_feed.tsv", format="idealo")

# Data science formats
df = shopextract.to_dataframe(products)
shopextract.to_parquet(products, "products.parquet")
```

### CLI

Every feature is available from the command line.

```bash
# Extract products from a store
shopextract extract https://example-store.com
shopextract extract https://example-store.com -n 50 -f csv -o products.csv

# Detect platform
shopextract detect https://example-store.com

# Discover product URLs
shopextract discover https://example-store.com -n 200

# Compare prices
shopextract compare "Wireless Headphones" -s https://store-a.com -s https://store-b.com

# Monitor a store
shopextract snapshot https://example-store.com
shopextract changes example-store.com
shopextract history example-store.com "Cool Widget Pro"

# Analyze catalog
shopextract analyze https://example-store.com -n 100

# Validate product data
shopextract validate products.json -m google_shopping
shopextract validate products.json -m idealo
```

---

## Supported Platforms

| Platform | Detection | API Extraction | Scraping |
|:---------|:---------:|:--------------:|:--------:|
| **Shopify** | Headers, CDN, `/products.json` | `/products.json` (public) | UnifiedCrawl, CSS |
| **WooCommerce** | Headers, wp-json, plugin paths | Store API v1 (public) | UnifiedCrawl, CSS |
| **Magento 2** | Headers, REST API | `/rest/V1/products` (public) | UnifiedCrawl, CSS |
| **BigCommerce** | Meta tags, CDN | -- | UnifiedCrawl, CSS |
| **Shopware 6** | Headers, API config | -- | UnifiedCrawl, CSS |
| **Generic** | Fallback | -- | UnifiedCrawl, CSS |

Any store with product pages will work. Platform detection just enables faster API-based extraction when available.

---

## Extraction Tiers

`shopextract` uses a tiered fallback strategy -- it tries the fastest method first and falls back automatically.

| Tier | Method | Speed | Reliability | Cost | Works On |
|:-----|:-------|:-----:|:-----------:|:----:|:---------|
| **API** | Platform REST APIs | Fast | High | Free | Shopify, WooCommerce, Magento |
| **UnifiedCrawl** | JSON-LD + OG + markdown parsing | Medium | High | Free | Any site with structured data |
| **CSS** | Browser-based CSS selectors | Slow | Medium | Free | Any site |
| **LLM** | AI-powered extraction | Slow | High | Varies | Any site (universal fallback) |

### LLM Tier Configuration

The LLM tier requires an API key (or Ollama for local/free). It supports **every major LLM provider** via LiteLLM:

```python
# Pass API key directly
result = await shopextract.extract(
    "https://some-store.com",
    llm_api_key="sk-...",
    llm_model="openai/gpt-4o-mini",
)

# Or use environment variables
# export SHOPEXTRACT_LLM_API_KEY=sk-...
# export SHOPEXTRACT_LLM_MODEL=anthropic/claude-sonnet-4-20250514
result = await shopextract.extract("https://some-store.com")

# Local models with Ollama (free, no API key)
result = await shopextract.extract(
    "https://some-store.com",
    llm_model="ollama/llama3.1",
)
```

#### Supported Providers

| Provider | Model Examples | Env Var | Cost |
|:---------|:--------------|:--------|:-----|
| **OpenAI** | `openai/gpt-4o-mini`, `openai/gpt-4o` | `OPENAI_API_KEY` | ~$0.01-0.03/page |
| **Anthropic** | `anthropic/claude-sonnet-4-20250514`, `anthropic/claude-haiku-4-5-20251001` | `ANTHROPIC_API_KEY` | ~$0.01-0.02/page |
| **Google Gemini** | `gemini/gemini-2.0-flash`, `gemini/gemini-2.5-pro-preview-06-05` | `GEMINI_API_KEY` | ~$0.01/page |
| **Ollama (local)** | `ollama/llama3.1`, `ollama/mistral`, `ollama/qwen2.5`, `ollama/deepseek-r1`, `ollama/phi3` | None needed | Free |
| **Mistral** | `mistral/mistral-large-latest`, `mistral/mistral-small-latest` | `MISTRAL_API_KEY` | ~$0.01/page |
| **DeepSeek** | `deepseek/deepseek-chat` | `DEEPSEEK_API_KEY` | ~$0.002/page |
| **Groq** | `groq/llama-3.1-70b-versatile`, `groq/llama-3.3-70b-versatile` | `GROQ_API_KEY` | Free tier |
| **Cohere** | `cohere/command-r-plus` | `COHERE_API_KEY` | ~$0.01/page |
| **Perplexity** | `perplexity/sonar-pro` | `PERPLEXITY_API_KEY` | ~$0.01/page |
| **Together AI** | `together_ai/meta-llama/...` | `TOGETHER_API_KEY` | Varies |
| **AWS Bedrock** | `bedrock/anthropic.claude...` | `AWS_ACCESS_KEY_ID` | Varies |
| **Google Vertex AI** | `vertex_ai/gemini-...` | `GOOGLE_APPLICATION_CREDENTIALS` | Varies |
| **Azure OpenAI** | `azure/gpt-4o` | `AZURE_API_KEY` | Varies |
| **Cloudflare** | `cloudflare/...` | `CLOUDFLARE_API_KEY` | Free tier |
| **Replicate** | `replicate/...` | `REPLICATE_API_TOKEN` | Varies |
| **OpenRouter** | `openrouter/...` (100+ models) | `OPENROUTER_API_KEY` | Varies |

Any model supported by [LiteLLM](https://docs.litellm.ai/docs/providers) works.

#### API Key Resolution Order

1. `llm_api_key` parameter (explicit)
2. `SHOPEXTRACT_LLM_API_KEY` environment variable
3. Provider-specific env var (e.g., `OPENAI_API_KEY` for `openai/...` models)
4. For `ollama/*` models -- no key needed (runs locally)

---

## CLI Reference

| Command | Description | Key Options |
|:--------|:------------|:------------|
| `shopextract extract <url>` | Extract products from a store | `-n` max URLs, `-f` format (json/csv), `-o` output file |
| `shopextract detect <url>` | Detect the e-commerce platform | -- |
| `shopextract discover <url>` | Discover product URLs | `-n` max URLs |
| `shopextract compare <query>` | Compare prices across stores | `-s` store URL (repeatable) |
| `shopextract snapshot <url>` | Save a catalog snapshot | -- |
| `shopextract changes <domain>` | Show changes between snapshots | -- |
| `shopextract history <domain> <product>` | Price history for a product | -- |
| `shopextract analyze <url>` | Catalog statistics | `-n` max products |
| `shopextract validate <file>` | Validate products against marketplace | `-m` marketplace |

All commands output JSON by default.

---

## API Reference

### Core

| Function | Signature | Returns |
|:---------|:----------|:--------|
| `extract` | `async (url, *, platform=None, max_urls=20, shop_url=None, llm_api_key=None, llm_model="openai/gpt-4o-mini", llm_temperature=0.2)` | `ExtractionResult` |
| `extract_one` | `async (url, *, llm_api_key=None, llm_model="openai/gpt-4o-mini")` | `dict` |
| `from_feed` | `async (feed_url, *, shop_url="")` | `ExtractionResult` |
| `detect` | `async (url, *, client=None)` | `PlatformResult` |
| `discover` | `async (url, *, platform=None, max_urls=100, timeout=30.0, client=None)` | `list[str]` |
| `normalize` | `(raw, *, platform=GENERIC, shop_url="")` | `Product \| None` |
| `QualityScorer.score_product` | `(product: dict)` | `float` |
| `QualityScorer.score_batch` | `(products: list[dict])` | `float` |

### Compare

| Function | Signature | Returns |
|:---------|:----------|:--------|
| `compare` | `async (query, stores, *, max_per_store=50, threshold=0.6)` | `ComparisonResult` |
| `compare_catalogs` | `async (store_a, store_b, *, max_products=200, threshold=0.8)` | `CatalogDiff` |
| `fuzzy_match` | `(products_a, products_b, *, threshold=0.8)` | `list[tuple[dict, dict, float]]` |
| `match_gtin` | `(gtin, products)` | `list[dict]` |

### Monitor

| Function | Signature | Returns |
|:---------|:----------|:--------|
| `snapshot` | `async (url, *, db_path="~/.shopextract/snapshots.db", max_urls=200)` | `int` |
| `changes` | `(domain, *, db_path=...)` | `list[Change]` |
| `price_history` | `(domain, product_title, *, db_path=...)` | `list[tuple[datetime, float]]` |
| `watch` | `async (url, *, interval=3600, db_path=...)` | `AsyncGenerator[Change]` |

### Analyze

| Function | Signature | Returns |
|:---------|:----------|:--------|
| `analyze` | `async (url, max_products=500)` | `CatalogStats` |
| `analyze_products` | `(products: list[dict])` | `CatalogStats` |
| `price_distribution` | `(products, buckets=None)` | `dict[str, int]` |
| `outliers` | `(products, std_multiplier=2.0)` | `list[dict]` |
| `brand_breakdown` | `(products: list[dict])` | `dict[str, float]` |

### Competitive Intelligence

| Function | Signature | Returns |
|:---------|:----------|:--------|
| `price_position` | `async (my_product, competitors, *, max_products=200)` | `PricePosition` |
| `assortment_gaps` | `async (my_store, competitors, *, max_products=200)` | `AssortmentGaps` |
| `brand_coverage` | `(catalogs: dict[str, list[dict]])` | `dict[str, dict[str, int]]` |

### Validate

| Function | Signature | Returns |
|:---------|:----------|:--------|
| `validate` | `(products, marketplace="google_shopping")` | `ValidationReport` |
| `check_images` | `async (products, *, timeout=10.0, concurrency=20)` | `list[ImageIssue]` |
| `find_duplicates` | `(products, method="title", threshold=0.9)` | `list[tuple[int, int, float]]` |

### Export

| Function | Signature | Returns |
|:---------|:----------|:--------|
| `to_csv` | `(products, path)` | `None` |
| `to_json` | `(products, path, indent=2)` | `None` |
| `to_feed` | `(products, path, format="google_shopping")` | `None` |
| `to_dataframe` | `(products)` | `pandas.DataFrame` |
| `to_parquet` | `(products, path)` | `None` |

### Data Models

| Model | Description |
|:------|:------------|
| `Product` | Unified product with title, price, currency, description, image_url, gtin, sku, variants, etc. |
| `Variant` | Product variant (variant_id, title, price, sku, in_stock) |
| `ExtractionResult` | Extraction output: products, raw_products, tier, quality_score, platform, errors |
| `ExtractorResult` | Raw extractor output: products, complete, error, page counts |
| `PlatformResult` | Detection result: platform, confidence, signals |
| `Platform` | Enum: SHOPIFY, WOOCOMMERCE, MAGENTO, BIGCOMMERCE, SHOPWARE, GENERIC |
| `ExtractionTier` | Enum: API, UNIFIED_CRAWL, GOOGLE_FEED, CSS, LLM |
| `ComparisonResult` | Price comparison: query, matches, cheapest, most_expensive, avg_price, price_spread |
| `Match` | Matched product: title, price, currency, store, product_url, similarity |
| `CatalogDiff` | Catalog comparison: only_in_a, only_in_b, in_both, cheaper_in_a, cheaper_in_b |
| `Change` | Base change event: change_type, title, detected_at |
| `PriceChange` | Price change: old_price, new_price, currency |
| `NewProduct` | New product detected: price, currency |
| `RemovedProduct` | Product removed: last_price, currency |
| `ChangeType` | Enum: PRICE_CHANGE, NEW_PRODUCT, REMOVED_PRODUCT |
| `CatalogStats` | Catalog statistics: total, price_range, avg, median, brands, categories, completeness |
| `PricePosition` | Competitive pricing: rank, percentile, market_avg, competitor_prices |
| `AssortmentGaps` | Category/brand gaps: missing_categories, missing_brands |
| `ValidationReport` | Validation result: marketplace, total, valid, invalid, issues, pass_rate |
| `ValidationIssue` | Single issue: product_index, field, error, severity |
| `ImageIssue` | Image problem: product_index, image_url, status_code, error |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-feature`)
3. Install dev dependencies: `pip install -e ".[dev]"`
4. Run tests: `pytest`
5. Submit a pull request

---

## License

[MIT](LICENSE) -- Copyright (c) 2026 Umer Khan
