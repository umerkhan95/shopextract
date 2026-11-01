# G2 red evidence
2026-11-01. Existing .venv, PYTHONPATH=src, one worker, BLAS/OMP threads2, tokenizer parallelism false.
Command: timeout120 pytest tests/test_adapter_coverage.py -q --tb=short (via bounded Python subprocess runner).
Actual19 cases:15failed,4passed in4.65s; red.log retained. Initial19-case run is bounded smoke,not prior isolated smoke. No adapter production changes.
Controls:emptybrand,Shopify429,Shopifyvariantmismatch,Magento defaultcore. Failures:brand/conflict,suppliedchildren/duplicateIDs,Woo enrichment,Magento capabilities/API/CLI and HTML/generic confidence.
No full-driver/live pass claimed. G2 review pending.

G2 repair evidence: first2case smoke2intendedred in4.65s (04/repair-smoke.log). Combined bounded run `pytest tests/test_rendered_money.py tests/test_adapter_coverage.py -q --tb=short`, timeout120, same capped environment:44collected,33failed11passed in6.37s (04/repair-red.log). Rendered17=11red6control;adapter27=22red5control (invalidcapability API existingguard alreadypasses). No timeout/harness error. No implementation yet.

Implementation evidence: A1 Woo firstsmallgreen12pass15deselected0.97s a1-smoke.log;fullnew27PASS1.17s green-attempt.log. Affectednormalizer/storefront/detection/Woo+Magento category/CLI/truthful withnew27=274PASS5.78s (affected.log),timeout120. ExistingShopify `test_shopify_budget_and_id_checked_enrichment`, `test_enrichment_failure_retains_products_and_surfaces_error` (test_live_regressions.py), `test_variant_enrichment_and_gtin_history`, `test_barcode_enrichment_preserves_aggregate_stock_support` (test_capture_provenance.py)4PASS0.92s identifier-controls.log,timeout40. ActualHTTP mocked only;realpublicCLI/API/normalization/evidence executed. No full-driver/live/final pass claimed.

A1shape/route followup:10newcases allintendedred1.62s a1-shape-red.log. Validate listcontainer/detailobject and positiveASCIIdecimal routeIDs beforeHTTP;invalidIDs do not consume requestbudget.37new+normalizer/storefront/Woocategories/CLI=195PASS2.42s a1-shape-green.log,timeout120. A2/A3prior scopedfunctionalPASS;A1independentre-review pending.
Concreteinteropdiagnostic: normalizedunknownvariantstockNone failsportabletype
validation; savedunknown-stock-portability.json. Amendment retainsdefaultTrue/
positional fields,permitsNoneonlyVariantstock.5realnormalize→portable tests:
1intendedred(None)/4bool/default/invalid-text controlspass0.31s portable-red.log.
No productiontypechange yet; affectedexistinginterface review requested.
NullableVariantstock G3 PASS. One annotation changed,bool|None=True; default/order
preserved. Fiveinterop testsPASS0.20s portable-green.log;interop+adapter+bundle+
normalizer110PASS1.11s portable-affected.log,120s ceiling. Userdocs explain newnull
consumer support. Independent functional review pending; no Product migration or
portable resource guard changes.
