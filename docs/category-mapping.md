# Category mapping

Category support is opt-in through `shopextract.categories`. It preserves source
categories separately from a caller-owned, versioned target registry. Exact rules
map supported source facts to target IDs. No LLM or fuzzy classification runs by
default, and no universal market taxonomy or complete set of mapping rules ships
with the library.

```python
from shopextract import Platform
from shopextract.categories import (
    CategoryOptions, CategoryScope, CategorySelector, MappingRule, TargetRegistry,
    extract_with_categories, categorized_product_to_record,
)

scope = CategoryScope(Platform.SHOPIFY, "https://your-shop.example")
options = CategoryOptions(
    scope=scope,
    registry=TargetRegistry("my-catalog", "2026-10", ("laptop",)),
    rules=(MappingRule(
        "merchant-laptop", "1",
        CategorySelector(
            "shopify:product_type", None, scope=scope, raw_label="Laptop",
            allow_unknown_version=True,
        ),
        ("laptop",),
    ),),
)

# Inside an async function, using a shop you are authorized to read:
# result = await extract_with_categories(scope.store_url,
#     category_options=options, max_urls=2)
# for companion in result.products:
#     record = categorized_product_to_record(companion)
```

`normalize_with_categories(raw, platform, shop_url, category_options=options)`
also accepts an existing captured raw product. Plain dictionaries without captured
support cannot establish observed category facts. Each companion contains the
ordinary `product`, source `observations`, derived `mappings`, configuration digest
and original binding. Unknown versions require explicit permission in each selector.
Rules are exact and case-sensitive. All applicable rules must agree on their full
target set; disagreements retain the union as ambiguous candidates.

| Source | Retained meaning and acquisition |
|---|---|
| Shopify | Public `product_type` is a custom merchant label. Standard category and collections remain distinct when actually captured; no new Admin access. |
| WooCommerce | Product category IDs/names are unordered memberships. Sibling names never become a hierarchy. |
| Magento | Optional minimal `categories { uid name }`; opaque UIDs and name support are independent. |
| BigCommerce | Optional fixed first-20 membership query, with completion metadata. No category-tree follow-up. Storefront credentials/publication remain required. |
| Shopware | Returned `categoryIds`, unordered `categoryTree` and actual parent associations remain separate. Existing request associations stay bounded. |
| Generic | JSON-LD Text/URL/Thing/CategoryCode, feed Google category/custom product type and repeated OpenGraph values retain separate representations. LLM output cannot establish source evidence. |

Missing, null, empty, malformed and partial source states remain explicit. A valid
ID does not support a failed name field. Product membership, parent edges and index
entries have different meanings. Scope includes platform, store/base path and any
known catalog/channel/locale; IDs are not globally interchangeable.

Defaults cap retained category terms at 100, relation references at 200, ancestry
depth at 8, companion/configuration records at 256 KiB, and rules/targets at 1000
each. Limits may be reduced. Catalog completeness is separate from category
completeness. Limits do not imply a complete store taxonomy was fetched.
The companion byte limit includes the ordinary Product evidence record. Large
configurable products can already exceed it before adding category facts; encoding
then raises `CategoryError` instead of dropping evidence. The sampled Magento
products hit this limit; they do not establish live companion verification.

## Persistence and maintenance

Use `categorized_product_to_record` / `categorized_product_from_record` for the
explicit version-1 companion envelope. The ordinary Product codec and extraction
APIs retain their old formats. Changing a nested Product, evidence or transformation
after binding invalidates the companion; encoding must reject it.

For maintenance, supply `CategoryRuntimeConfig(options, profile_bindings=...)` to
`MaintenanceStore(..., category_config=config)` **before creating a job**. The store
atomically saves its complete canonical policy snapshot. A corresponding engine
configuration is an expected identity check; the stored job policy is authoritative.
Category-enabled creation upgrades the database to schema 2. New code reads schemas
1 and 2; older code rejects schema 2. Back up an existing database before upgrading
if older applications still use it.

Legacy jobs remain legacy on resume. Changing a job's mode or policy is rejected
before state or network activity; create a new job for a changed policy. Category
cache identity includes policy and scope, and corrupt companions become cache
misses. Target-to-profile bindings only add review requirements: they cannot select
a profile automatically or override identity, RAM, boot-size or variant safeguards.
The existing hardware, footwear and generic profiles remain separate domain policies.

Feature design, independent reviews and offline/live evidence are recorded in
[`specs/006-category-mapping`](../specs/006-category-mapping/). Planned checks are
not completed verification; consult its status and verification files for limitations.

## WooCommerce category trees

For opt-in public store category acquisition, actual parent relations, portable
tree evidence and lookup of already captured memberships, see
[WooCommerce category trees](woocommerce-category-tree.md). Tree presence does
not assign a product membership; optional Shopify mapping remains separate.
