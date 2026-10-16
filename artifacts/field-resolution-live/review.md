# Live field-resolution verification — 2026-10-16

**12/12 final cases passed** across 6 supported families and seven actual sites. The final cases audited 106 product observations, 262 variant observations and five additional HTML product contracts: 5282 field resolutions. These are observations, not deduplicated catalog totals.

The final matrix recorded 74 requests. Including the initial captures before adding independent API/HTML comparisons, 120 actual requests were made. All cases ran sequentially with per-operation and hard process deadlines; no models or agents were launched.

| Platform family | Cases | Product observations | Variants | Live path |
| --- | ---: | ---: | ---: | --- |
| shopify | 4 | 32 | 32 | Public product JSON, enrichment, public extract, paired HTML |
| woocommerce | 2 | 14 | 0 | Store API, public extract, paired HTML |
| magento | 2 | 22 | 219 | Paginated GraphQL, public extract, paired HTML |
| shopware | 2 | 22 | 11 | Paginated Store API, public extract, paired HTML |
| bigcommerce | 1 | 8 | 0 | Public extract → actual HTML (API token unavailable) |
| generic | 1 | 8 | 0 | Production CSS strategy/capture/normalizer on fresh HTTP HTML |

## Resolution checks

Every live product and additional HTML contract passed capture coverage/source-URL/payload audits, immutable observation/evidence checks, normalized-value preservation, shuffled-input determinism, typed contract serialization/load and matching-report reference checks. Re-evaluating 31 days later expired all originally observed support while retaining the original evidence and observation states. Scalars and relationship scores stayed unchanged. All full evidence exports were read back successfully.

Five real same-product API/HTML pairs (two Shopify stores, WooCommerce, Magento, Shopware) were aligned by URL and currency. All twelve field observations per pair remain retained in the combined contracts; policy can select only supported candidates.

The Shopware live pair is a useful support boundary: the API price is supported at 22 EUR; HTML has an unsupported price observation and its scalar default is zero. The resolver correctly keeps API 22 EUR and retains the unsupported HTML alternative. It does not fabricate an observed zero or conflict. Magento’s API and HTML both support 69 EUR; equivalent observations retain both sources and select a stable representative. Both real captures are now compact offline regression fixtures.

## Fault probes and findings

96 additional controlled policy probes passed. They seed actual live values but explicitly alter fixture roles/values/timestamps to check supplier versus manufacturer authority, equivalent peers, tied price disagreement, stale/future/unsupported evidence, and boolean versus numeric zero. They are labeled synthetic and do not claim that any live site is a verified manufacturer or published the altered value.

No new application defect was reproduced in this live run. No production fix was invented to turn unsupported source data into a fact. The prior stress worker gained an import guard so the new sequential harness can reuse the actual extraction and audit functions. Two saved-live regression cases were added.

## Validation

- `PYTHONPATH=src .venv/bin/python -m pytest -q tests/test_field_resolution.py`: **55 passed**, 0.28 seconds.
- `PYTHONPATH=src .venv/bin/python -m pytest -q`: **590 passed**, 3.74 seconds.
- `git diff --check`: passed.

## Scope and saved evidence

This is live sample/correctness verification across all currently supported families, not every merchant on the internet, every theme/plugin or a long-running load test. Public native extraction was exercised for Shopify, WooCommerce, Magento and Shopware; BigCommerce used actual public HTML. BigCommerce authenticated GraphQL remains covered by documentation-based mocks. Generic CSS uses real HTTP pages and production extraction/capture code without launching a browser. Genuine verified-manufacturer registration remains a caller responsibility; altered role tests are explicitly synthetic. Persistence/export epic work is still #37/#38.

Per-case JSON summaries contain HTTP journals, timings, memory, paired-source comparisons and policy outcomes. Compressed evidence exports retain the resolved real contracts. Initial captures are saved separately. Re-running `PYTHONPATH=src .venv/bin/python artifacts/field-resolution-live/run.py` reuses completed results; `--smoke` selects the small case.

Live sites:
- [https://www.boardgamebliss.com](https://www.boardgamebliss.com)
- [https://store.401games.ca](https://store.401games.ca)
- [https://demo.athemes.com/botiga](https://demo.athemes.com/botiga)
- [https://magento2-demo.magebit.com](https://magento2-demo.magebit.com)
- [https://frontends-demo.vercel.app](https://frontends-demo.vercel.app)
- [https://cornerstone-light-demo.mybigcommerce.com](https://cornerstone-light-demo.mybigcommerce.com)
- [https://books.toscrape.com](https://books.toscrape.com)
