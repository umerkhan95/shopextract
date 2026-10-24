# WooCommerce category trees

Fetch a merchant's public category tree explicitly, with captured page evidence:

```python
import asyncio
from shopextract import Platform
from shopextract.categories import CategoryScope
from shopextract.categories.woo_tree import (
    fetch_woocommerce_category_tree, woo_tree_to_record,
    woo_tree_from_record, link_tree_memberships,
)

async def main():
    tree = await fetch_woocommerce_category_tree(
        CategoryScope(Platform.WOOCOMMERCE, 'https://your-store.example/shop'))
    print(tree.outcome, tree.reasons, tree.issues)
    record = woo_tree_to_record(tree)
    restored = woo_tree_from_record(record)
    # For existing captured product observations with the same scope:
    # links = link_tree_memberships(restored, categorized_product.observations)

asyncio.run(main())
```

The endpoint includes `hide_empty=false`, paginates sequentially and retains
ID/name/slug/parent facts with their own URL, pointer and UTC receipt time.
Actual parent declarations produce edges; orphan/conflict/cycle/depth issues
remain explicit. Integer parent zero declares root; opaque string `"0"` can
reference a real category ID. Complete traversal is separate from graph integrity
and is never an atomic snapshot or proof of unpublished categories.

`outcome` is complete, partial, unavailable or malformed. `confirmed_empty`
requires consistent zero-total coverage. Woo can omit headers on a short/empty
first page; one second-page confirmation may establish totals. Missing/drifting
headers, malformed fields and budget exhaustion preserve partial evidence.
Default ceilings are 10 HTTP attempts, 1,000 raw category entries, 100/page,
2 MiB identity body/page, 8 MiB canonical retained envelope, depth 8 and 30 seconds.
`WooTreeLimits` may lower these values; zero work caps perform no HTTP request,
while depth zero permits roots. Very small retention caps may return an in-memory
diagnostic that cannot itself fit a portable envelope; serialization raises
CategoryError in that case. Nonidentity compressed responses are unsupported.
There are no retries or LLM calls. Only public addresses and same-origin redirects
preserving the category route/query (optional trailing slash) are permitted.

Lookup links only existing, evidence-supported product memberships to retained
same-merchant IDs. A missing lookup in a partial tree proves no absence. Tree
presence never assigns a category to a product or creates ancestor memberships.
Product/Variant constructors, default extraction, feeds and maintenance are
unchanged. Optional Shopify mapping is deferred; existing exact mapping rules
continue to apply to captured memberships independently.
