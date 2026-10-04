# Storefront API integration review

Reviewed 2026-10-04T15:51:19.023636+00:00. Full compatibility/regression suite: **479 passed in 10.77s**. `git diff --check` passed.

The identified protocol-routing, missing storefront adapter and documentation gaps are implemented. Existing extraction tiers remain API → structured HTML → CSS → configured optional LLM. A forced REST → GraphQL sequence was not added.

| Actual public pipeline | Tier | Products / variants | Result |
| --- | --- | --- | --- |
| magento | api | 2 / 30 | 69 EUR; 57 EUR |
| shopware | api | 2 / 0 | 22 EUR; 99 EUR |
| bigcommerce-pipeline | unified_crawl | 1 / 0 | 249 CAD |
| shopware-variants | api | 4 / 0 | 22 EUR; 99 EUR; 33 EUR; 199 EUR |

The extra four-product Shopware sample overlaps the two-product case; do not sum them as unique products. The sample filename `shopware-variants` was exploratory; those four products had no children. Magento live products each returned 15 configurable variants, with native evidence mappings.

BigCommerce public pipeline returns Canvas Laundry Cart at 249 CAD through UnifiedCrawl. Its API-unavailable reason remains visible in `result.errors`; this is a successful HTML extraction with an unavailable API attempt, not an authenticated GraphQL success.

## Resolved findings

- Magento default REST assumption replaced with GraphQL API routing; configurable variants and configured URL suffixes retained.
- Shopware/BigCommerce adapters discover public runtime configuration or accept explicit endpoint/token options; absence continues to HTML with an inspectable API reason.
- Generic HTML sources no longer use a detected platform API normalizer, which previously could erase extracted prices.
- BigCommerce native product-card discovery avoids a broad browser discovery walk when a small sample is requested without a public API token.
- Compressed streamed responses no longer decode twice; keyed redirect and canonical-Origin regressions pass.
- Page/product budgets, cursor progress, known variant truncation and empty catalog behavior are explicit.
- README platform claims now match actual API dispatch and access requirements.

## Validation and limits

- BigCommerce token-based GraphQL adapter is schema/fixture verified, not live authenticated catalog verified; official demo exposes no token.
- New adapters certify bounded source results, not full merchant catalog coverage. Non-Shopify catalog completeness remains unverified.
- Magento core products GraphQL supports Open Source/PaaS; SaaS Catalog Service and customized schemas can use HTML fallback.
- Inline public configuration discovery is intentionally limited to explicit storefront fields; bundled/computed keys need caller-supplied API options.
- No live LLM provider or authenticated legacy REST call was made.

- Deterministic fixtures cover native `extract()` dispatch, product/page/variant budgets, cursor/ID repetition, partial GraphQL errors, zero/false values, correct nested variant pointers, API-context currency, no-access HTML continuation, generic-source normalization, gzip responses, anonymous/keyed redirects, canonical BigCommerce Origin, empty catalogs, legacy REST options and bounded product-card discovery.
- Live sources: [Magento Magebit demo](https://magento2-demo.magebit.com), [Shopware official frontend demo](https://frontends-demo.vercel.app), [BigCommerce official Cornerstone demo](https://cornerstone-light-demo.mybigcommerce.com). Shopify/WooCommerce live results from the earlier provenance review are preserved in the sibling artifact directory.
- BigCommerce query field names were checked against the official GraphQL reference. Saved extracted schema types confirm all requested Product/Variant fields and `isInStock` inventory fields. Public token access was not available on the selected demo.
- Initial failures are retained as `*.before-repair.json` and `bigcommerce-pipeline.before-card-discovery.json`. The BigCommerce pipeline initially timed out during broad browser discovery; the native card discovery fix passes the actual public pipeline.

## Files

- `live.py`: sequential native API/pipeline driver; `*.json`: saved raw products and complete trust contracts.
- `full-tests.log`: complete regression results; `baseline-tests.log` / `focused-tests.log`: earlier checkpoints.
- `bigcommerce-schema-reference.source`, `bigcommerce-schema-types.json`: official GraphQL reference and extracted schema definitions.
- `docs/storefront-apis.md`: public routing, configuration, access and pagination documentation.
