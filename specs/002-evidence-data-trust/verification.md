# Verification — issue #34

Baseline: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_models.py -q`
Result: 26 passed. Initial invocation without PYTHONPATH could not import the
checkout; corrected once with explicit src path. No inference or crawl required.
Session token counters are not exposed by the available tools; no quota estimate
is inferred. Scope is bounded to contracts, offline fixtures and compatibility.

## Final verification

Command: `PYTHONPATH=src .venv/bin/python -m pytest tests/test_evidence_contracts.py tests/test_models.py tests/test_normalize.py tests/test_identity_matching.py tests/test_export.py tests/test_snapshot_completeness.py tests/test_extract.py tests/test_monitor.py tests/test_compare.py tests/test_quality.py -q`
Result: **241 passed**, 0.91 seconds. `git diff --check` passed.

Contract checks include missing/zero/false, nested field/collection coverage, escaped
pointers, score semantics, Decimal/UTC/tag collision round trips, unavailable states,
malformed schema/IDs/time/state/reference rejection, retained alternatives, mutation
validation and legacy constructor/asdict/canonical identity compatibility.

Spec/plan/tasks consistency review: all four #34 acceptance scenarios map to named
fixtures; the field matrix accounts for every current Product/Variant dataclass field.
FR-01/02/06 contract deliverables are complete; FR-03/04/05/07 implementations and
SC-01–04 end-to-end proof remain unchecked in dependent tickets. Constitution and
three local planning templates initialized without user configuration changes.

Fixture correction: normalize takes a dict, not a list. The existing non-product gate
requires a positive price, image or identifier; using a SKU permits the missing-price
fixture while retaining compatibility. The initial fixture failures were corrected;
no normalizer behavior was changed.

Limitations: source capture authenticity/calibration artifacts are caller responsibilities;
production capture byte limits, automatic extractor coverage, SQLite evidence storage,
retention, source precedence and full Product bundle export await #35–#39. A pre-existing
requests dependency-version warning appears at startup; it did not affect the checks.
No local inference, live crawl, parallel agent, install or broad research was performed.
Actual session token counters are unavailable; no fixed quota claim is made.

## P2 review follow-up

Both findings reproduced with targeted fixtures before changing production code:
9 failures exposed Enum codec bypasses and conflicting-state validated confidence.
The codec now recursively encodes Enum values before other type handling, preserving
Decimal/UTC tagging, raw-map escaping and rejection of nonfinite/unsupported values.
Validated confidence is accepted only for observed support; conflicting and other
unavailable states reject it on construction and after mutation during serialization.

Added 12 regression cases under `test_enum_values_use_recursive_codec`,
`test_enum_values_cannot_bypass_validation`, and
`test_only_observed_state_accepts_validated_confidence`.
The same affected-suite command above now passes **253 tests**, 0.98 seconds.
`git diff --check` passed. Public contract wording updated; component boundaries
unchanged. No agents or inference processes launched. Actual session token counters
remain unavailable.

## Issue #35 verification — 2026-10-04

Focused baseline: evidence contracts + normalization, **80 passed**.
Initial checkout import required PYTHONPATH=src; no dependency installation needed.
Focused new provenance/contracts/normalization run: **90 passed**.
Final command: `PYTHONPATH=src .venv/bin/python -m pytest -q`
Result: **419 passed**, 2.14 seconds, including 14 new provenance cases.
`git diff --check` passed. All checks were offline; no agents, model launches or
live crawling. Actual session token counters remain unavailable through the exposed
tools; no quota percentage is inferred.

Acceptance mapping is recorded in tasks.md. The shared spec includes all five #35
scenarios; plan and public contract document the capture architecture, compatibility,
4096-byte fragment / 65536-byte source-payload budgets and limitations.

Captured redirects use actual fetched API/feed/page URLs. Separate JSON-LD items,
filtered image source indices, variant-ID detail enrichment and escaped nested maps
are covered. A discovered pre-existing restoration bug (skipped invalid variant
shifting output indices) now matches GTIN restoration by variant ID. WooCommerce
explicit false stock is preserved, and namespaced feed links/descriptions parse.
Legacy constructor/asdict/export/snapshot/identity and extraction-error suites pass.

Limits: partial adapters/projections are explicitly unsupported, including unverified
LLM output, layered fallback values and implicit stock/currency defaults. Contract
attachments are not persisted by dataclass export; policy/storage/portable bundles
remain #36/#37/#38. Hand-constructed contracts are caller-supplied and not subject to
adapter byte limits. Raw response memory is not bounded by retained evidence budgets.
The environment emits an existing requests dependency-version warning; tests pass.

## Issue #35 P2 review follow-up — 2026-10-04
Small reproduction baseline saved to `/tmp/shopextract-issue35-review-baseline.log`:
**8 failed, 14 passed**, covering the three initially visible findings (five invalid
price fixtures, image fallback, two rejected-condition fixtures). The other two
reported findings have dedicated Shopware and mocked browser-redirect fixtures.

Final command: `PYTHONPATH=src .venv/bin/python -m pytest -q`
Result: **435 passed**, 2.69 seconds. `git diff --check` passed.
Final run saved to `/tmp/shopextract-issue35-review-full.log`. No inference, agents,
live browser launch or live crawl; all browser results are mocks.

All five P2 findings are addressed. Normalizers expose actual selected inputs and
conversion outcomes through a shared internal abstraction. Contract generation
consumes these outcomes and validates retained-input equality without re-parsing
prices or maintaining a second platform mapping. Additional fixtures prove that
capture truncation cannot substitute a lower-priority source, generic platform
fallbacks use the actual normalizer, and changed captured inputs cannot support
unverified enriched values. Public APIs, dataclass exports and legacy scalar
defaults retain compatibility; unsupported reasons expose rejected conversions.

## Issue #35 live matrix — 2026-10-04

Saved driver and review: `artifacts/live-provenance-35/all-domains/run.py` and
`review.md` / `review.json`. Web discovery references and fetched responses are in
`artifacts/live-provenance-35/store-discovery/`; initial failed cases and pre-fix
contracts are preserved. Eleven cases cover 17 sampled products and nine variants:
Shopify (Board Game Bliss, 401 Games), WooCommerce (aThemes Botiga), Shopware official
public Store API, Magento Magebit public GraphQL, downloaded AdTribes XML/CSV samples,
JSON-LD, OpenGraph, CSS (Books to Scrape), and an actual crawl4ai browser product page.
No contract coverage/pointer/budget violations were found in the saved samples.

Live review resolved aggregate stock invalidation by unrelated barcode enrichment,
uncaptured Shopify cookie currency, native Magento/Shopware field shapes, duplicate
ancestor capture starving late leaf fields, currency-prefix feed prices, CSS currency
symbols and relative image references. These have dedicated offline regressions.
Command: `PYTHONPATH=src .venv/bin/python -m pytest -q`: **444 passed**, 2.93 seconds;
`git diff --check` passed. Actual browser extraction passed; redirected browser
JSON-LD/OG cases remain mocked regressions, not successful live redirect claims.

Limitations: Magento REST returned 401; GraphQL fetch/normalization was exercised
independently, without adding an automatic REST fallback. Shopware Store API requests
used the public key published in its official frontend configuration; no dedicated
Shopware HTTP adapter was added. WooCommerceExtractor was exercised on one public
page, with two products audited. XML/CSV samples are live downloads from publisher
ZIP archives, decompressed before existing parser invocation; archive transport is
not supported by GoogleFeedExtractor.extract. Their `.local` product links are sample
content. The initial Shopware browser URL returned Error404 and was excluded from
successful product totals. LLM provider calls were not run; its mocked unsupported
output/confidence regression passes. Long truncated fragments remain explicitly
unsupported. Results are samples, not exhaustive coverage of all merchants.

## Subsequent storefront routing follow-up — 2026-10-04

The live review's adapter limitations have since been addressed outside the narrow
#35 provenance requirement. The public pipeline now selects Magento GraphQL by
default (explicit legacy REST remains available), and integrates Shopware Store API
and BigCommerce Storefront GraphQL when published or caller-supplied access config
is available. HTML observations select the generic source normalizer even for a
known platform. BigCommerce native product-card discovery avoids broad browser
walking for the tested token-unavailable small sample. Failed API attempts remain
inspectable when HTML succeeds. See `docs/storefront-apis.md` for API options and
limitations, and `artifacts/api-integration/review.md` for the current live results.

Actual `extract()` calls pass on Magento and Shopware at API tier, and on BigCommerce
at UnifiedCrawl tier without a public token. Magento returned 30 configurable
variants across two products. BigCommerce authenticated GraphQL is verified by
fixtures and official schema fields, not a live token-based catalog. Initial failed
cases are retained. This supersedes the earlier statement that no Shopware adapter
or Magento GraphQL API routing existed; it does not change #35's provenance scope.

## Live stress follow-up — 2026-10-04

18 live cases across all six supported platform families passed after a real Magento
last-page truncation defect was reproduced and repaired. A known catalog total
and unclipped response are now required before claiming exhaustion; two new
regressions cover total-count and page-info-only responses. The complete Magebit
catalog returned 181 products / 1,847 variants over 10 requests. All observed field
values, actual-source URLs, pointers and capture budgets were audited.

Final full suite: **481 passed**, 2.88 seconds; `git diff --check` passed.
Detailed cases, repeat-memory measurements, harness corrections, complete retained
evidence and coverage limits: `artifacts/live-stress/review.md` and `review.json`.
Three same-process repeats do not establish long-duration memory stability.
BigCommerce authenticated GraphQL, legacy Magento REST and browser-specific paths
were not newly live-verified in this stress run.

## BigCommerce documentation-based authentication — 2026-10-04

Official authentication/customer-context docs were rechecked. Explicit storefront,
private and impersonation modes, strict customer-session errors, context-safe
continuation and separated observation scopes are implemented. Native nullable-price
mapping and the repeated-cursor regression fixture were corrected. An executable
frozen catalog schema mock checks the actual query; 32 field types/nullability
are retained from the official type reference.

54 additional regression cases; focused storefront/auth suite **91 passed**;
full suite **535 passed**, 27.62 seconds. `git diff --check` passed.
Coverage and provider-boundary limitations: `artifacts/bigcommerce-auth/review.md`,
`tests/fixtures/bigcommerce/README.md` and `docs/storefront-apis.md`. No real
credentials or live authenticated calls were used. Provider signature/permission
verification and token issuance remain outside read-only extraction.
