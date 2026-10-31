# CLI product discovery repair

## Outcomes and requirements
FR01: Existing `shopextract extract STORE --max 50 --browser --timeout 300 -o FILE` reaches merchant product pages through advertised public sitemap/index sources before broad Crawl4AI category crawling. No site-specific hardcoded merchant list or external driver.
FR02: Bound native sitemap discovery by requested URL count, same-origin/store-path scope, robots permissions, cycle/duplicate suppression, response/request/time caps. Advertised category/collection-only sitemap leaves are exclusions, not product candidates. Never enumerate entire catalog to select50.
FR03: Native discovery obeys remaining operation deadline and propagates cancellation; absent API/sitemaps retains existing safe API/seeder/browser fallbacks. Existing Product/Variant, identity/evidence, schemas and feed defaults unchanged. Resource cutoff is not complete catalog coverage.
FR04: CLI output retains actual Products/raw capture and current partial/error semantics, including honest unextractable pages and no output success on timeout. `--max` remains URL-processing cap; fifty valid input pages must produce50valid supported records in controlled acceptance, without claiming any catalog complete. Live50case reports actual count/validity, not fabricated count.

## Acceptance scenarios
SC01: Root robots advertises index and category map; index points to numeric product leaf with50valid product URLs; discover returns ordered50product URLs, not category URLs, never fetches later leaves or starts browser/seeder. Existing machine CLI then returns50Products through actual native parsers.
SC02: Duplicated/cyclic index, category first, image:loc, foreign/nested-path/disallowed URL and redirect escape cannot consume candidates or cause broad fetch; origin/path and robots scope maintained.
SC03: max1/exact50/over51, request/byte/deadline limits, slow stream, malformedXML/DTD, missing/403 sources and cancellation stop safely; no hidden250kURL enumeration or mock of mechanism.
SC04: Shopify/API success and old seeder fallback/native browser controls remain compatible. Retry/repair limited, no inference.
SC05: Fresh local CLI live smoke3 followed by Naheed50 using same command as failed run; validate saved output/source URLs and bounded runtime. Any unresolved live gap stays explicit.

## Boundaries
Fix repository discovery/orchestration, not new onboarding app/driver or full-store crawl. Price grouping, GTIN enrichment, default-price semantics and cross-store recommendations are separate known findings. No dependency/browser/model installation, push/PR creation or merchant write requested.
