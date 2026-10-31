# Static HTML product enrichment and listing categories

Unified extraction reads product JSON-LD/OpenGraph and enriches a single product
from MagicZoom gallery links, a `.brand-name` link and `span.sku` in the same
HTML. Known placeholder paths are discarded before the no-browser fast path.
Genuine structured fields take precedence. HTML field captures remain separate
from original JSON-LD evidence. Missing GTIN, SKU or variants stay missing.

Magento module/RequireJS signatures allow platform detection even when its APIs
are forbidden. Detection does not imply the native API is available. Generic
fallback confidence is zero; other confidence values remain heuristic scores.

## Explicit category listing evidence

A category sitemap supplies URLs, not product memberships. The listing index
fetches those URLs sequentially and records only main product-card links. It
retains each category URL, optional heading label and fetched-page evidence. A
product can belong to several categories. Neither URL slugs nor analytics scripts
are used to infer Google taxonomy identifiers or a category hierarchy.

Use your existing native `CategoryOptions` JSON for the exact store/platform and
pinned target registry. Build a bounded index from a sitemap urlset or JSON array
of category URLs:

```sh
shopextract categories index-listings category-urls.xml \
  --options naheed-options.json --max-pages 20 --max-memberships 1000 \
  --timeout 60 --output listing-index.json
```

Limits include same-origin/store-base-path URLs, no redirects, a 1MiB page/index
ceiling, and explicit page/membership/operation budgets. A partial acquisition
writes its positive evidence and exits with `E_PARTIAL` (exit 3); inspect `reasons`
and `pages_visited`. Default 20 pages cannot cover all 757 saved Naheed categories.
The command does not claim a complete catalog, provide crawl resume, or merge
separate index artifacts. Split/choose input URLs according to the task and keep
artifacts separate when a full store exceeds one artifact's bounds.

Apply one index to saved raw extraction records, then use the existing mapper:

```sh
shopextract categories normalize raw-products.json --options naheed-options.json \
  --listing-index listing-index.json --output categorized-products.json
```

The option is explicit; default category normalization is unchanged. Match exact
product URLs; meaningful query strings are retained. No match means no positive
membership, not proof of nonmembership. Listing observations use namespace
`merchant:listing_category`, unknown taxonomy version, category URL as native ID,
and heading as the optional label. Exact mapping rules can select that category
URL (or label) and map it to independently verified target IDs using the existing
pinned registry. Set `allow_unknown_version: true` for these merchant selectors;
no Google mapping is generated automatically.

Library equivalents are `build_listing_index`, `with_listing_categories`, and
`normalize_with_categories` from the category modules. The saved index validates
shape, store scope and retained capture consistency before it is attached. Caller
supplied captures remain unverified-source evidence.
