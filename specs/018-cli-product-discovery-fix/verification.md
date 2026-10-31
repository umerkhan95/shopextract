# Executed verification
G1/G2/G3 independentPASS, digestsreviews.md. Real acceptance red:2failures0.29s because old discovery starts external seeder/browser and returns no productlist. Primary native integration green:2passed0.58s, real publicdiscover and actualCLI50JSONLDrecords; actualsourcecaptureandnativeProducts, no fake extraction reports.
New private sitemap implementation + existingdiscover integration; no operational driver. Platform API-first preserved. Enclosingdeadline + physicalrequest/decodedbody caps cover source reads; cancellation not swallowed. Pending adversarialfixtures/stress, focused/fullchecks, localCLI3then50, finalreview.
Counters unavailable for this parent/fix session; historicalnativeCodexCLI26843 not reused ascurrenttotal. No more nativeCodexmodel sessions/localinference/parallelagents planned. Docker CLI supported-Linux probe unavailable (localdockerinfo crashed); mandatorycurrent-host full driver still required with honestbaselinefailure classification.

## Bounded adversarial discovery checks (2026-10-31)

Added `tests/test_discovery_sitemap_bounds.py`; fixtures are derived-offline and
all transport is `httpx.MockTransport`. Production discovery, URL canonicalizer,
robots parser, XML parser, fallback decision and byte/deadline accounting run
unchanged. No live requests or model processes were used.

- Budget: fixed RNG seed `0`; one 5,000-location sitemap leaf (under 1 MiB),
  requested max 50, no more than 2 HTTP source requests, 30-second shell timeout.
  Observed 50 ordered unique URLs, exactly one large-leaf fetch and no additional
  request. The same suite checks max 0/1/50/51; each positive cap returns exactly
  that many when available, with no product-page requests during discovery.
- Distinct adverse checks: duplicate/cyclic index and fragment canonicalization;
  category map before product map; direct-child `<loc>` ignores image locations;
  foreign origin, path-prefix collision and multiply encoded traversal; robots
  denied map, candidate-only denial and store-path denial; redirect hops counted
  against request cap; inclusive single-response decoded-byte edge and aggregate
  byte cutoff; slow body deadline; explicit cancellation with owned-client close
  and provided-client preservation; malformed XML/DTD rejection and safe legacy
  fallback. These target separate traversal, policy, resource and lifecycle
  failures.
- Green logs: `evidence/bounded-green.txt` (18 passed, one known red excluded,
  0.50s), `evidence/cli-acceptance-green.txt` (existing actual CLI 50 acceptance
  passed, 0.56s), and `evidence/native-smoke-green.txt` (existing 3-URL discovery
  smoke invoked directly under asyncio because this host lacks pytest-asyncio).
- A minimal contract test is intentionally saved red in
  `evidence/robots-specificity-red.txt`: with a broad `Allow: /` and longer
  `Disallow: /shop/item`, production `RobotFileParser.can_fetch` permits the
  candidate, so it is returned despite the more specific denial. Python's
  standard parser currently applies the broad first rule here. This is a
  production policy defect, not a test-fixture issue; the author did not alter
  source or relax the expected outcome. At that milestone it needed a diagnosed fix and rerun; the later coordinator
  rerun below records its resolution and the complete green result.
- Environment note: direct `pytest` here lacks the configured
  `pytest-asyncio` plugin; the new checks use a small synchronous asyncio wrapper.
  The old 3-URL async acceptance was called directly; the old 50-URL synchronous
  CLI acceptance ran in pytest. Full repository gate and live CLI checks remain
  pending with the primary coordinator.

## Coordinator configured-environment rerun
The real specificity red was repaired once by sorting stdlib literal rules by descending path specificity and Allow on equal ties, retaining existing parser matching semantics. RFC9309 section2.2.2 confirms those precedence rules: https://www.rfc-editor.org/rfc/rfc9309.html#section-2.2.2 . Added distinct narrow-Allow and equal-rule tie tests. This is not a claim of a new complete RFC robots implementation.
Configured original `.venv/bin/python` includes pytest-asyncio; both original async smoke and actual CLI50 acceptance ran in pytest without deselection. `evidence/affected-tests.log`:159passed,13warnings,8.32s across both new files and discover/extract/native-core/native-controls/CLI regressions. An existing strict Shopify synthetic fixture needed explicit404 robots/index responses and updated expected request order; its product/count assertion remains unchanged.
At this milestone the required full sequential driver was running; its completed result is recorded below. No model inference or additional model-per-product calls. Exact parent session token counters unavailable.

## Required full driver (actual current host)
`PYTHONPATH=src /Users/umerkhan/code/shopextract/.venv/bin/python scripts/run_tests.py --output-dir specs/018-cli-product-discovery-fix/evidence/full-suite` exited1. Main:1745passed,16failed,1skipped,210.79s; driver214.325s, no process group alive after cleanup. All16failures are in existing `tests/test_google_production.py` owned-process/worker supervision tests on macOS. The unsupported supervisor raises `RuntimeError: Owned browser supervision requires Linux`; some downstream cases instead fail on missing process metadata/status assertions. No discovery/CLI failure. The historical Darwin killpg test passed this run, so there are16, not17 failures. Required driver stops on failed main; reliable-oracle and maintenance groups not executed. Whole-repository gate remains INCOMPLETE, not PASS. Full exact report/log retained. Reviewed host disposition permits requested bounded live diagnosis after159affected passes and classified full result.

Live smoke started with the existing CLI: root `https://www.naheed.pk`, `--max 3 --browser --timeout 60 --format json --output` evidence/live-smoke.json; normal host network, writable browser cache, no LLM flag. stdout/stderr/exit retained.

## Actual live CLI results
Both unmodified command-entry executions completed normally with exit0: smoke3/3, then requested50/50. `evidence/live-smoke.json` and `evidence/live50.json` retain full envelopes, normalized products and raw JSON-LD source captures; stdout/stderr/exit files retained alongside. Same normal-host CLI/environment as command above, then `--max 50 --timeout 300`. No model extraction or operational crawler script.
`evidence/live-summary.json` records50distinct captureURLs,50titles,PKR currency for all50, and all50normalized prices numerically equal retained source offers. Every capture method is json_ld. Compared against all757category URLs in saved advertised category source:zero overlap. First/last50captures16:51:49.446–16:52:19.755UTC; capture span30.309s, not a separately instrumented total process runtime. No timeout/forced termination. `urls_attempted=50`, `urls_succeeded=50`, errors empty.
Coverage remains a sample: `catalog_complete=null`, reason `crawl_coverage_unverified`; envelope `completeness=complete` means operation success, not store-catalog proof. All50source JSON-LD image values are placeholder URLs; extraction preserves this source limitation. These are product records, not evidence of image enrichment.
Both successful runs emit a Playwright startup/cleanup pending-task/TargetClosedError warning on stderr from existing browser preflight; machine JSON/output and exit0 are intact. It remains a known cleanup limitation, not silently marked repaired. Browser product crawling was not needed: actual page captures used JSON-LD native HTTP fastpath. This test validates local CLI acquisition/discovery/extraction, not competitor comparison or recommendations.

## Main-branch integration isolation
The user authorized creating/pushing a PR and merging only verified work. Remote main was `a900599`; original audit base `67a8144` belongs to still-open PR99, so the discovery fix alone was transplanted onto main. No PR99 taxonomy/native-core changes are included. Production discovery module and all three test changes are byte-identical to the reviewed fix; only docs conflict resolved by retaining main docs plus the bounded-discovery section. Main-base affected suite:115passed,12warnings,2.22s (`evidence/main-base-affected.log`). PR99-only native core/control test files are absent on main and not claimed tested on the isolated branch. Historical159/full1745 evidence above belongs to the original PR99 audit environment. Fresh main-base live smoke3 returned3/3 exit0; live50 pending. Merge requires the required full Linux CI gate on this actual main-based head, not the historical incomplete macOS report. Saved category reference copied into `evidence/category-reference.xml` for reproducible overlap inspection without unpublished older audit directories.

Fresh main-base live50 also returned50/50 with exit0,50unique JSON-LD captures,50PKRprices equal retained offers,zero extraction errors and zero category-reference overlap. `evidence/main-base-live-summary.json` records both new runs; `main-base-live3.json` and `main-base-live50.json` retain outputs. Same source-placeholder images and preflight cleanup warning remain. No catalog completeness assertion. These new receipts validate the code actually proposed for main independently of PR99.
