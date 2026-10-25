# P1 actual verification

Baseline: `.venv/bin/python -m pytest tests/test_cli_core.py -q` initially import-failed due src layout; diagnosed repair `PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python -m pytest tests/test_cli_core.py -q` passed52 in0.35s; logs baseline-smoke*.log. No import-failure red claim.

G2 red: same bounded env `pytest tests/test_cli_extract.py -q`, evidence/acceptance-red.log. Expected failure missing new commands/flags/machine domain binding, not imports. Implementation pending.

Counters unavailable. No network/models/installs/push. Seed11025; later mechanism/stress/live pending.

Implementation mechanism: initial minimal smoke59passed. Expanded native-path fixtures exposed three diagnosed binding defects (partial Click exit returned0 through P0 main wrapper, Python3.10 asyncio.TimeoutError mapping, malformed Decimal ArithmeticError mapping); repaired once and focused95passed. Partial exit fix preserves direct standalone_mode=False return, raises configured nonzero process exit under standalone mode. P0 deferred-command guard test moved from now-implemented discover to still-deferred analyze; direct guard remains. Shopify normalized false-stock test uses actual Shopify schema; generic CSS normalization has no in_stock input mapping. First coverage expansion97passed/1fixture expectation failed: native discovery first requests products.json then sitemap, corrected controlled fixture to explicitly supply empty API page. No public live spend yet. A prior old-P0 deferred discover test briefly attempted `.invalid` before its adaptation; no public store request. No inference.

Coverage-ready focused112passed in1.71s (exact elapsed in coverage-final-ready.log), P0 included. Discover fixture now explicitly404 API then sitemap: native empty API enumerates APIurl by design rather than sitemap fallback. This is controlled native behavior, not external failure. Context lock serializes provider submissions even nested helpers; shared call counter/deadline retained.

Independent coverage repair:129focusedpassed (author1.82s, independent1.72s), coveragePASS. Complete/partial exact envelope file pipeline2passed0.30s; explicit native portable/raw mixed case separated. Pipeline amended G1/G2/G3/coveragePASS.

Reviewed bounded stress command: `PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 .venv/bin/python tests/cli_extract_stress_driver.py`,12 sequential case groupsPASS in28.671s, per-case logs and actual RSS/status evidence/stress/status.json. Seed11025; maximum30s/case/180s total/512MiB child RSS, source-schema record-edge max1001, normalized products<=100, no inference. All provider activity is controlled boundary stubs.

Fault proof command: same environment plus `PYTHONPATH=src:tests pytest -p cli_extract_fault_plugin tests/test_cli_extract.py::test_eleven_products_native_transport_and_exact_codec -q --tb=short`; process-local mutation drops11th product from actual output binding. Critical assertion failed1case0.53s (detected). Separate normal process restored testPASS1case0.57s. Plugin opt-in only, production files never mutated; logs fault-mutant.log/fault-restored.log.

Affected regression command: focused CLI3files plus native test_extract.py/test_normalize.py/test_quality.py/test_discover.py/test_storefront_apis.py/test_capture_provenance.py, same bounded environment, `-q --tb=short`:298passed3.17s, evidence/affected-regressions.log. No whole repository sweep. Click stdin deprecation and environment RequestsDependencyWarning remain warnings, not functional failures.

Live predeclaration: tests/cli_extract_live_driver.py targets only www.boardgamebliss.com read-onlyGET, explicitShopify, retained<=2products, <=5actualHTTP attempts, <=30seconds, no retries/no browser/no models. Original AsyncHTTPTransport.handle_async_request preserved beneath counter; sameURL repeat, foreignhost, method/cap violation blocked before send; first HTTPerror raises driver stop through native catches. First result saved; no expansion authorized/attempted. Live result pending driver completion.

Actual live observation:PASS, first saved result evidence/live/{report.json,stdout.json,stderr.log};1actualHTTPsend/2retainedproducts/0.527seconds, no retries/browser/model. CLI exit3 is expected explicit max2 product-budget partial, native catalog_complete=false; nonempty titles and captured evidence present. This proves the bounded read-only integration on that observed response, not full catalog coverage/commercial changes/provider/browser execution. No expansion. Epic live budget spent1request/2items/0.527seconds by P1.

`git diff --check` for P1 modified tracked source/test files passed (no output). New files exercised by focused tests. Actual token counters remain unavailable; no inferred percentages.

Final independent review PASS recorded in reviews.md with digest manifest; no blockers. Browser/LLM actual live checks are blocked by absent separate configured execution budget; no provider/model/browser execution was authorized or performed. Deterministic external-boundary coverage proves the exercised budget/activation mechanisms only. P1 done; parent owns later CLI phases/ticket updates.
