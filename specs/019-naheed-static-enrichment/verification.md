# Verification
Environment: managed /workspace/shopextract, .venv Python3.12. Dependencies preinstalled. Actual session token counters unavailable.

## Red
`.venv/bin/python -m pytest -q tests/test_naheed_static.py tests/test_listing_categories.py`: 22 failed,4 passed; red.log. Missing DOM enrichment/detector behavior and absent listings module caused intended failures. One test accessor typo (`support` instead of FieldObservation.state) was corrected without changing expected outcomes.
Supplemental empty/hash gallery risk: 3 failed,15 passed in adversarial-red.log before filtering those navigation references. Full routing interaction already passed.

## Offline green
Focused revised check: `.venv/bin/python -m pytest -q tests/test_naheed_static.py tests/test_listing_categories.py tests/test_detect.py tests/test_capture_provenance.py tests/test_cli_categories.py` — **115 passed**,3 existing warnings,2.24s; focused-green.log.

Initial complete driver (full-check/report.json): main1594 passed, reliable oracle24 passed, maintenance106 passed,232.463s total. This run started before final reviewer repairs, so it is diagnostic evidence, not final revised gate. Revised required full driver: `.venv/bin/python scripts/run_tests.py --output-dir specs/019-naheed-static-enrichment/final-check` — **passed** in209.129s total, main1604 passed (104.39s pytest), reliable oracle24 passed (29.62s), maintenance106 passed (67.62s): **1734 tests**, no skips. Machine report: final-check/report.json; all3 per-family logs retained. Final source/test revision unchanged throughout this run. `git diff --check` passed.

Independent final review found an actual total-deadline gap during continuously streamed response bodies. stream-red.log: dripping100 chunks exceeded20ms budget (~1.13s),1 failed/2 passed. Repair wraps complete response/body in asyncio.wait_for with remaining total deadline and reports partial time_budget_reached. Three separate final-response scope/base-path and malformed-capture cases plus invalid CLI artifact/XML entity checks now pass. Invalid helper index types consistently raise CategoryError. No assertions were weakened to fit outputs. Controlled HTTP fixtures and all generated HTML are synthetic, not live captures. Real extraction, normalization, category mapping and portable codecs execute; full routing test fixes only unrelated discovery URL boundary and HTTP transport.
Stress: deterministic nonrandom 100 cards across3 pages; 1/2/3-page limits,200 membership ceiling, inputs <64KiB, at most3 GETs, one worker. Fixed code/fixture, no seed. Request/card counts asserted directly; no algorithm mocks.

## Live
Blocked: current enforced managed network policy permits package-manager hosts, not www.naheed.pk/media.naheed.pk. No denied live requests attempted; planned 1 product +1 category GET (15s each, no retries/browser) not executed. Existing specs018 sitemap has757 URL entries; these are URL evidence only and were parsed offline, not product memberships. User's four-product findings inform synthetic fixture shape but are not newly verified live evidence.

## Limits
No complete crawl of757 categories or live four-product re-extraction claimed. CLI index bounds/resume limitations documented in docs/static-enrichment-listings.md. No automatic Google taxonomy assignments or GTIN/variant invention.
