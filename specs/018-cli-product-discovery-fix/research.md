# Bounded production research

Research date: 2026-10-31. Scope is the existing `extract` CLI and its native
discovery path for a requested sample of 50. No new operational crawler or
driver is in scope.

## Evidence inspected

- `src/shopextract/_discover.py`: generic discovery attempts platform sitemap
  paths, then `AsyncUrlSeeder` with `max_urls=5000`, then returns filtered
  results. `_parse_sitemap_xml` explicitly returns an empty list for an
  `<sitemapindex>`, so generic discovery cannot follow the root's advertised
  index itself. Generic seeding receives only the host, not the store path or
  operation policy. `_discover_for_platform` does not pass `max_urls` to
  generic/Shopify/WooCommerce/Magento paths; only BigCommerce receives it.
- `src/shopextract/_execution.py`: the CLI stores a monotonic deadline in a
  context-local state, but discovery does not consult it. `run_operation`
  enforces the outer timeout and cancellation at the caller boundary.
- `src/shopextract/_cli_extract.py`: explicit native CLI routes `--max` to
  `extract(max_urls=...)` and timeout to the execution policy. CLI writes the
  output only after operation completion.
- `src/shopextract/_extract.py`: fallback URL discovery calls
  `discover(..., max_urls=max_urls)` but omits its timeout argument, so it uses
  the library default. API-first behavior remains a compatibility boundary.
- `tests/test_discover.py` covers basic sitemap XML parsing, API discovery, and
  a Shopify return-list cap. It does not cover index traversal, robots,
  category-map exclusion, resource-bounded native sitemap traversal, or the
  generic seeder's enumeration behavior. `tests/test_cli_extract.py` checks
  requested max forwarding at CLI extraction/API boundaries, but not native
  URL discovery or 50 parsed products.
- Saved live receipt `artifacts/naheed-cli-50/extract-receipt.json` records
  `E_TIMEOUT`, unavailable completeness and `data: null`; status says the
  process was still observed after 5:17 and no output was published. The
  bounded stderr excerpt shows category URLs being crawled. This is evidence
  of the failed run, not evidence of successful 50-product extraction.

## Root cause and decisions

The native discovery path has no robots-advertised sitemap-index traversal.
Its parser discards sitemap indexes, then delegates generic sitemap work to a
third-party seeder that can enumerate up to 5,000 URLs without the requested
sample cap, store-path scope, robots policy, or shared deadline. On the target
store this falls through to slow category-page browser crawling and exceeds the
CLI's 300-second operation deadline. The caller subsequently reports a timeout
and publishes no result. This explains the saved failure; it does not establish
that the target will yield 50 valid products after repair.

Add a small native HTTP robots/sitemap/index traversal before the legacy seeder
and browser fallback. Traverse advertised indexes in source order, suppress
cycles/duplicates, exclude category/collection sitemap leaves and non-product
URLs, and stop once `max_urls` eligible product URLs are found. Restrict fetched
and returned URLs to the source origin and configured store-path boundary;
consult robots before sitemap and product requests. Bound source requests,
response/aggregate bytes and elapsed time, and derive each request timeout from
the remaining operation deadline. Preserve cancellation (do not turn it into a
successful empty result or start a fallback after cancellation). Keep legacy API,
platform sitemap, seeder and browser fallbacks when native discovery finds no
eligible URLs and time remains. Existing extraction/result contracts remain
unchanged.

`max_urls` is a URL-processing cap, not a promise of catalog completeness. The
acceptance fixture must contain 50 valid product pages and verify that the
existing parsers produce 50 valid records. Category sitemap paths are not
product candidates; URL eligibility should use the repository's existing
filters plus explicit category/collection exclusion grounded in fixture cases,
not a merchant-name list.

Resource proposal from test-design: at most 12 sitemap/robots source requests,
20 MiB aggregate and 10 MiB per response, 30 seconds for native traversal,
always bounded by the enclosing deadline; explicit request timeout at most 15
seconds and no larger than remaining time. These are caps, not targets. Stop
reading at byte cap and cancel promptly at deadline. Reviewers should check
whether the existing configured timeout behavior supports these limits before
implementation; do not silently loosen the CLI deadline.

## Compatibility and unresolved verification constraints

Retain API-first paths, platform product sitemaps, and safe seeder/browser
fallbacks. Successful native discovery must prevent fallback enumeration. Do
not change Product/Variant constructors, identity/evidence, formats, or
completeness semantics. A limited 50-page sample remains explicitly
unverified coverage.

The repository workflow identifies `python scripts/run_tests.py` as the full
gate. The task owner reports that some existing native-Linux-only tests fail on
macOS. No full gate was run during this research-only stage. Record each such
failure by test, expected host requirement, and observed behavior when the gate
is attempted; do not call the full gate passed on this host unless the configured
driver actually passes. Resolve feature-relevant failures separately from
unsupported-host failures, and preserve required full-gate evidence from a
supported environment if available.

The live 3-then-50 CLI check is explicitly required. The saved 50 failure does
not satisfy it. After offline mechanism checks and full gate, repeat the same
existing command first with max 3 and timeout 60, save the receipt, then max 50
and timeout 300. Report actual counts, product validity, source URLs, runtime,
and output status. Do not claim whole-catalog completeness.
