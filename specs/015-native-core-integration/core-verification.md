# Core author verification

2026-10-31. Ownership: categories/api.py, _extract.py, extractors/unified.py, extractors/_browser.py and tests/test_native_core_integration.py only. Parent owns CLI/verifier. Design approved by independent reviewer before changes; no author self-approval.

Intended red: core-red-smoke.log, one source-mode case fails at missing option before any I/O; then core-red.log,11 failed/2 passed in0.22s (missing production/include_categories/proxy integration). Green smoke/suite core-green-smoke.log:13 passed in0.35s. Focused existing extraction/category and parent CLI controls regressions core-regression.log:177 passed in7.85s. These controlled source and external browser responses exercise real discovery, HTTP fallback selection, Unified JSON-LD/OpenGraph, CSS strategy/parser, normalizer, category observer and binder. They do not prove Chromium startup or merchant access.

Additional designed API short-circuit test from FP-SC3 added after initial green: actual Shopify transport/parser/capture/binder passes with exactly one API request and no browser. core-green.log:14 passed in0.36s. git diff --check passed. restore_short_gtin forwarding amendment independently approved later; final result below. Original browser/merchant/full5595/nativehost blockers remain.

## Short-GTIN forwarding amendment

NC-FR6: Preserve explicit restore_short_gtin behavior through every existing fallback normalization branch; library default remains false. This is argument forwarding only, not broader GTIN acceptance. NC-SC9: Controlled Shopify API403, real discovery with external URLSeeder response, real Unified JSON-LD parser with captured variants[{id:10,barcode:'29877030712'}], real normalization: false yields no GTIN, true yields0029877030712 per existing tests/test_live_regressions.py checksum fixture. Invalid checksum remains no GTIN. External HTTP/browser boundaries alone are controlled. Other fallback branches forward same option; source data lacking variants remains unaffected. Intended red must show enabled fallback loses restoration before repair, then both expected states pass. No production change until reviewer approves this amendment.

Independent reviewer recorded NC-FR6/SC9 G1/G2/G3 PASS in reviews.md. Intended-red core-gtin-red.log: enabled-valid fallback failed (actualNone vs expected0029877030712); defaultFalse and invalid-checksum passed. Four fallback normalization calls now forward existing opt-in only. No normalizer changed. Combined final focused run core-final-green.log:192 passed,11 dependency deprecation warnings,10.25s. It includes17 new core scenarios plus extraction/live-regression/category and parentCLI tests. No algorithm mocks or live claims. Full configured driver is parent-owned final gate and remains pending here.

## Independent review R6 scope and proxy edges

NC-FR1/4 repair, no new defaults or source contract. New source-origin/sibling-path/literal-parent/encoded-parent/double-encoded-parent inputs demonstrated the intended missing input-scope guard before implementation: core-scope-red.log5failed1passed. Production branch now validates normalized origin and decoded base-path membership before starting native extraction; malformed/ambiguous traversal is rejected. This validates selected input only, not every discovered URL/redirect/subresource. Native hosted-feed behavior is unchanged. Positive descendant case executes actual production discovery/HTTP/browser/parser/binder.

Differing synthetic HTTPS_PROXY/HTTP_PROXY plus NO_PROXY and lowercase HTTPS fallback now explicitly verify documented conservative browser proxy precedence; environment remains unchanged and no HTTPX NO_PROXY parity is claimed. No browser/network starts in config-only test.

core-scope-green.log154passed7.42s (core23 plus category regressions), then added positive descendant requirement case: core-final2-green.log24passed0.55s. Parent-owned configured final suite must include these latest changes. No paid/model or actual browser/merchant proof is inferred.
