# Live stress review — 2026-10-04

**18 cases passed**, across all six supported platform families and seven live sites. 26 extraction rounds, 158 recorded HTTP requests, 561 product observations and 3611 variant observations. Counts include repeated extraction of the same products; they are not unique catalog totals.

| Case | Products / variants (final round) | Requests | Seconds | Peak RSS MiB |
| --- | ---: | ---: | ---: | ---: |
| 01-magento-smoke | 7 / 63 | 3 | 0.99 | 99.64 |
| 02-shopware-smoke | 7 / 0 | 5 | 0.89 | 103.53 |
| 03-magento-pagination | 31 / 335 | 7 | 3.25 | 132.6 |
| 04-shopware-pagination | 31 / 13 | 9 | 2.28 | 131.34 |
| 05-magento-pipeline | 25 / 272 | 2 | 2.77 | 126.29 |
| 06-shopware-pipeline | 25 / 13 | 4 | 1.51 | 127.22 |
| 07-shopify-bliss | 20 / 79 | 21 | 4.76 | 111.46 |
| 08-shopify-401 | 20 / 20 | 21 | 3.39 | 98.22 |
| 09-woocommerce | 8 / 0 | 1 | 0.87 | 93.76 |
| 10-bigcommerce-html | 6 / 0 | 8 | 3.11 | 102.36 |
| 11-magento-repeat | 25 / 272 | 6 | 4.74 | 133.47 |
| 12-shopware-repeat | 25 / 13 | 12 | 3.94 | 141.01 |
| 13-bigcommerce-repeat | 6 / 0 | 24 | 8.46 | 111.61 |
| 14-magento-boundary | 4 / 51 | 2 | 0.58 | 98.64 |
| 15-magento-full-catalog | 181 / 1847 | 10 | 13.41 | 167.81 |
| 16-shopware-page-budget | 5 / 0 | 3 | 0.58 | 103.14 |
| 17-magento-page-budget | 5 / 63 | 1 | 0.52 | 98.74 |
| 18-generic-css-repeat | 6 / 0 | 19 | 3.75 | 96.95 |

## Reproduced production bug and repair

A real Magento GraphQL query selected five existing catalog SKUs. With page size 3 and retained-product budget 4, the adapter fetched the final server page, discarded the fifth product, and incorrectly returned `complete=True`. The saved before-fix contract and summary reproduce this. Completeness now requires that the response was not clipped; a known total also takes precedence over the last-page marker. The live recheck returns four products and `complete=False`. Two deterministic regressions cover known-total and page-info-only responses.

The full Magento catalog independently returned 181 products and 1,847 variants over 10 pages, with `complete=True`. Limited-product and one-page-budget cases return incomplete status.

## Evidence checks

Every emitted factual field has a support observation. Observed values match the normalized product; evidence pointers resolve, source URLs match actual fetched responses, capture times include UTC offsets, and fragment/product payload limits hold. All returned products have observed price and currency. CSS books omit stock and product URL inputs, so these defaults correctly remain unsupported. Known nonempty identifiers are unique; absent identifiers are not treated as duplicate products. Every saved full evidence export was read back and its record count checked.

Shopify checks include live variant barcode/detail enrichment at Board Game Bliss and 401 Games. Shopware includes products with child variants. BigCommerce checks exercise its public HTML pipeline with the missing Storefront API token recorded explicitly. Generic CSS runs the production selector strategy and capture/normalizer against freshly fetched Books to Scrape HTML; it does not launch a browser.

## Harness corrections and memory

The first BigCommerce audit incorrectly counted repeated empty external IDs as duplicate IDs. Actual product URLs were distinct. The harness now compares only nonempty IDs; retained before-harness-fix results document the correction.

The first whole-catalog run passed product/evidence checks but exceeded the harness’s 24 MiB uncompressed export cap. Streaming gzip exports preserve every raw product and contract. The recheck saved a 2.09 MiB compressed export and reduced overall harness peak RSS from 357.48 to 167.81 MiB. RSS includes audit and artifact serialization, not only extractor memory.

Same-process repeated pipeline RSS (MiB): Magento 102.81 → 114.76 → 116.06; Shopware 105.32 → 112.73 → 120.73; BigCommerce 104.95 → 109.25 → 111.59. Three rounds cannot establish a memory plateau or rule out a long-running leak. No soak or concurrent throughput claim is made.

## Validation and limits

`PYTHONPATH=src .venv/bin/python -m pytest -q`: **481 passed**, 2.88 seconds. `git diff --check` passed. The initial pytest attempt omitted PYTHONPATH and failed import; rerun used the repository’s source layout correctly.

Live requests were read-only and run sequentially by case with subprocess and operation deadlines. Case summaries, HTTP journals, before-fix failures, scripts and complete raw/evidence exports are retained here. Re-run `PYTHONPATH=src .venv/bin/python artifacts/live-stress/run.py`; completed cases are reused. Boundary recheck uses `--boundary`.

This is live correctness/pagination/repeat testing, not high-rate load testing. It covers Shopify, WooCommerce, Magento, Shopware, BigCommerce and generic CSS. Authenticated BigCommerce GraphQL and legacy Magento REST remain fixture-tested, not live-verified. Browser redirect behavior and malformed-source failures remain covered by prior fixtures/probes; this run does not reproduce every malformed source or browser branch. A full Shopware catalog sweep and long-duration soak were not run.

Live sites:
- [https://magento2-demo.magebit.com](https://magento2-demo.magebit.com)
- [https://frontends-demo.vercel.app](https://frontends-demo.vercel.app)
- [https://www.boardgamebliss.com](https://www.boardgamebliss.com)
- [https://store.401games.ca](https://store.401games.ca)
- [https://demo.athemes.com/botiga](https://demo.athemes.com/botiga)
- [https://cornerstone-light-demo.mybigcommerce.com](https://cornerstone-light-demo.mybigcommerce.com)
- [https://books.toscrape.com](https://books.toscrape.com)
