# Issue 35 — live store validation and review

Reviewed 2026-10-04T15:06:04.067081+00:00. **17 products, 9 variants, 11 cases.** Full suite: **444 passed**. `git diff --check` passed.

Every supported named platform and the generic JSON-LD, OpenGraph, CSS, XML and CSV paths has saved results. These are sampled stores, not an exhaustive crawl. Contract checks cover complete factual-field observations, resolvable retained pointers, reasons for unavailable support, UTC sources, and fragment/product budgets.

## Results

| Family / live source | Products / variants | Price + currency | Execution |
| --- | --- | --- | --- |
| [Shopify — Board Game Bliss](https://www.boardgamebliss.com) | 1 / 1 | 51.47 EUR | Actual ShopifyExtractor, identifier enrichment |
| [Shopify — 401 Games](https://store.401games.ca) | 2 / 2 | 50.00 CAD; 30.00 CAD | Actual ShopifyExtractor, identifier enrichment |
| [WooCommerce — Botiga](https://demo.athemes.com/botiga/) | 2 / 0 | 12 USD; 14 USD | Actual WooCommerceExtractor, one public API page, first two products audited |
| [Shopware — official demo](https://frontends-demo.vercel.app) | 2 / 6 | 6.5 EUR; 6.5 EUR | Public Store API HTTP search + native normalization |
| [Magento — Magebit demo](https://magento2-demo.magebit.com) | 2 / 0 | 45 EUR; 49 EUR | Public GraphQL HTTP fetch + native normalization |
| [Google Shopping XML](https://adtribes.io/product-feed-samples-showcase-download-page/) | 2 / 0 | 110.00 USD; 88.00 USD | Live archive download + existing XML parser |
| [Google Shopping CSV](https://adtribes.io/product-feed-samples-showcase-download-page/) | 2 / 0 | 110.00 USD; 88.00 USD | Live archive download + existing CSV parser |
| [Generic JSON-LD](https://www.boardgamebliss.com/products/catan-fifth-edition) | 1 / 0 | 54.95 CAD | Real fetched HTML + Unified structured extraction |
| [Generic OpenGraph](https://www.boardgamebliss.com/products/catan-fifth-edition) | 1 / 0 | 54.95 CAD | Real fetched HTML + OpenGraphExtractor |
| [Generic CSS — Books to Scrape](https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html) | 1 / 0 | 51.77 GBP | Real HTML + JsonCSS strategy + CSS adapter; no browser |
| [Browser structured HTML](https://www.boardgamebliss.com/products/catan-fifth-edition) | 1 / 0 | 54.95 CAD | Actual crawl4ai headless browser + Unified result extraction |

All listed prices/currencies are observed after fixes. Saved case JSON includes full trust contracts, raw inputs, unsupported reasons, source URLs and UTC observation times. Product defaults without a supporting source remain unsupported: notably OpenGraph/CSS stock, condition defaults and identifiers missing from the merchant.

## Findings resolved

1. All five original P2s: rejected API price conversions, wrong image fallback source, unknown condition supporting NEW, cross-platform variant source mapping, and browser requested/final URL propagation. Shared normalizer outcomes now drive capture contracts.
2. Shopify aggregate stock evidence used whole variant objects; barcode-only enrichment invalidated stock support. It now retains the precise availability/inventory inputs. Rechecked 401 Games with detail enrichment: aggregate and variant stock are observed.
3. Shopify response-cookie currency bypassed source capture. Cookie currency now retains its own response URL/time and original value. Rechecked both Shopify stores: EUR/CAD observed with actual cookie provenance.
4. Native public API shapes were unsupported by the flat Magento/Shopware mappings. Added native GraphQL final-price/currency/stock fields and Shopware calculatedPrice/available/children mappings, with exact nested sources and rejected-value regressions.
5. Large native Shopware responses spent capture budget on duplicate ancestor objects and lost later parent price fields. Leaf capture now gets priority within the existing budget; parent and child prices are observed on two live variant families.
6. AdTribes samples use currency-prefix prices (`USD 110.00`). Feed parsing now accepts both prefix and suffix formats. XML/CSV live rechecks agree on 110.00 USD and 88.00 USD.
7. CSS books price £51.77 previously defaulted to USD, and images stayed relative. Explicit unambiguous £/€ symbols now produce traced currencies; relative images resolve against the fetched page URL. Live books result is 51.77 GBP with an absolute retained-source-derived image URL.

## Review limits / remaining integration work

- **No unresolved false-observed provenance defect found in this sampled run.** This is a sample-based review, not a guarantee for all possible merchant responses. Compatibility suite passes; anonymous demo content can change.
- Magento REST on Magebit requires authentication (401); the original Luma candidate returned 526. GraphQL results were fetched independently and normalized; MagentoExtractor does not automatically fall back to GraphQL.
- Shopware native Store API normalization is verified with the public frontend access key published in the official demo repository. There is no automatic dedicated Shopware HTTP extractor. The key is a public sales-channel key, not an admin credential.
- WooCommerce original official demo hostnames failed DNS. Botiga public Store API is reachable. The actual WooCommerceExtractor fetched one page; two products were audited. Multi-page pagination was not exercised.
- AdTribes XML/CSV are publisher samples in downloaded ZIPs, with example `.local` product links. Existing parsers were used after decompression; GoogleFeedExtractor.extract does not accept ZIP transport. The retained source URL is the fetched archive; the case records its member name. This is not a live production merchant feed.
- Real browser extraction passed on Catan. The earlier Shopware advertised detail URL produced an Error404 fallback; preserved as `11-browser.before-repair.json` and excluded from product totals. Requested-versus-final URL propagation is covered by offline redirected browser results for both JSON-LD/OpenGraph; no successful redirected live product browser case is claimed.
- Real LLM provider calls were not run. The mocked LLM adapter regression passed: generated fields/scores never acquire observed support or calibrated confidence without verified source spans.
- API country/currency contexts differ: Bliss products.json yielded 51.47 EUR with an EUR cookie; independent product HTML/Ajax probes yielded 78.95 CAD with CAD cookies. Both responses are saved; values from separate contexts were not merged.
- Some long source text/parent containers exceed fragment limits and remain unsupported with explicit truncation reasons. Byte-budget enforcement is checked, and prioritizing leaves does not change source selection or substitute fallback values.

## Saved evidence and reproduction

- `run.py`: sequential resumable HTTP/browser driver with per-case timeout; `report.py`: report rebuild from saved results.
- `01-...11-*.json`: case outcomes, raw data and full contracts. `*.source` / `*.zip`: actual fetched source material. `*.http.json`: request/response metadata.
- `*.before-repair.json`, parent directory baseline cases and `store-discovery/`: original failures and source discovery; preserved for before/after review.
- `tests.log`: full offline compatibility/regression suite. `run.log` and `recheck.log`: compact case status and actual browser logs.

Primary discovery references: [Shopware official frontend configuration](https://github.com/shopware/frontends/blob/main/templates/vue-demo-store/nuxt.config.ts), [WooCommerce Store API docs](https://developer.woocommerce.com/docs/apis/store-api/), [aThemes Botiga demo](https://demo.athemes.com/botiga/), [Magebit Magento demo](https://magento2-demo.magebit.com), [AdTribes feed samples](https://adtribes.io/product-feed-samples-showcase-download-page/).
