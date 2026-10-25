# Verification evidence — 2026-10-24

## Existing behavior baseline (coordinator)
`PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
TOKENIZERS_PARALLELISM=false .venv/bin/python -m pytest -q
tests/test_category_woocommerce.py`: **12 passed**, 0.07 seconds.
Saved `evidence/legacy-woo-baseline-green.log`. Initial invocation without
PYTHONPATH failed conftest import; one diagnosed environment correction, saved
`evidence/legacy-woo-baseline.log`. Neither is intended feature-red evidence.

## W04 executable acceptance red
Author `/root/woo_author`; after recorded G1 pass, before any business logic.
Command: `PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
TOKENIZERS_PARALLELISM=false .venv/bin/python -m pytest -q --tb=line
tests/test_woo_tree_acceptance.py`.
Result: **40 failed in 0.29 seconds**, each at an explicit operation
`NotImplementedError` (37 acquisition-dependent cases and three direct
codec/link contract cases). Saved `evidence/acceptance-red.log`; not a green
runtime claim. All collection/imports and deterministic boundary fixtures work.

Initial red run exposed one fixture error: httpx tried decoding deliberately
invalid compressed bytes in Response construction, before reaching the API.
One diagnosed fixture repair replaced buffered content with an AsyncByteStream;
no production change or assertion weakening. Initial output preserved in
`evidence/acceptance-red-initial-fixture-repair.log`. Final concise run contains
only the intended explicit stub failures. Three direct codec/link cases were
added so their missing operations are independently exercised.

Coverage: SC01–08/11 initial pagination, evidence, facets, topology, headerless
confirmation, totals drift/repeated pages/conflicts, failure retention,
zero/malformed configuration, page-atomic item cap and terminal fit, unsafe DNS,
redirect, unsupported encoding, precancellation, codec replay and captured
membership lookup. Additional declared blocked-body cleanup, real pinned backend,
precise bytes/metadata, tampered projection, generated stress and default-output
regressions remain planned and must execute before final completion. Optional
Shopify bridge SC09/10 is deferred.

## Pending
G2 skeleton review, component design/G3, implementation, green acceptance,
remaining deterministic mechanism/stress, affected regressions and bounded live
smoke. No live checks or inferred production correctness. Actual session token
counters unavailable; no inference or parallel agents launched by this author.

## G2 evidence-strengthening red revision
Reviewer required native-ID fact support rather than trusting CategoryTermRef.
Added six distinct direct lookup cases: missing ID fact, rejected conversion,
mismatched normalized ID, empty evidence, unknown support, wrong term binding.
Each also requires foreign scope to remain scope_mismatch. Expected support
contract follows existing `mapping._supported` semantics; no business logic.
Command is the W04 command above; result **46 failed**, all explicit intended
NotImplementedError. Saved `evidence/acceptance-red-g2-revision.log` before
implementation. Prior 40-case red evidence preserved. G2 recheck pending.

## W08 small smoke and focused mechanism results
Saved first three-node smoke before expansion: acceptance SC01 **1 passed in
0.14s**, `evidence/first-tree-smoke.log`. Then original 46 acceptance plus 15
mechanism cases: **61 passed in 0.67s**, `evidence/focused-initial.log`.

Mechanism fixtures were authored before business logic. Their initial stub run
had one passing existing pinned-backend check and missing-operation failures;
three blocked-stream cases initially timed out waiting for an unentered stream.
The fixture now races operation completion so missing stubs propagate directly;
this initial scaffold output is not counted as clean intended red evidence.
The prior reviewed acceptance red remains authoritative.

Coordinator identified distinct opaque-string-zero vs integer-root, same-origin
page URL/query/attempt provenance, and invalid store URL type gaps. Predesigned
cases and saved `evidence/provenance-zero-red.log`: **9 failed**, exposing those
exact gaps. One diagnosed repair per gap preserves raw-root distinction, validates
fixed route/query and successful attempt binding, records the guarded actual-hop
URL instead of outer HTTPX request, and validates scope types before URL parsing.
Focused rerun command as above with both test files: **70 passed in 0.85s**,
`evidence/focused-green.log`. No shared dirty transport/runtime edits.

Implemented standalone acquisition, topology, strict tree codec and supported
captured-membership lookup. Usage in `docs/woocommerce-category-tree.md`.
No optional Shopify bridge implementation. Initial implementation checks are
not final verification or independent approval.

## W10 fixture/stress design pending independent coverage review
`evidence/fixture-manifest.json` and `tests/woo_tree_stress_driver.py` describe 24
sequential cases: 6 topology, 6 pagination, 8 budgets, 4 acquisition/link
interactions. All original stress slots remain acquisition relevant; bridge
SC09/10 are explicitly deferred. Driver has a 60s overall deadline, 1,000-category
maximum retained fixture, <=2 MiB +1 individual fixture, <=16 MiB per-case fixture,
one worker and observed peak RSS checks against 256 MiB. RSS is checked after
each case, not claimed as hard OS isolation. Fixed 8192-byte retention cases
check normal fit and evidence-overhead crossing; raw-body exact fit/one-over
checks are separate. Stress has NOT run; reviewer must approve first. Existing
focused checks exercise production parser/guard/topology/codec/lookup, substituting
only HTTP, DNS, connector, clock and injected blocked streams.

Coordinator owns affected broader regressions and real public observation.
Selected live plan `evidence/live-plan.json` and `tests/woo_tree_live_driver.py`
use https://demo.athemes.com/botiga after offline success, <=3 attempts/6 nodes/
10 seconds smoke. No live run yet. Independent reviewer should inspect that
driver too. Mutation-sensitivity check remains pending before final verification.
Actual token counters unavailable to this author; no inference or parallel work.

## Final execution evidence — coordinator, 2026-10-24
Earlier pending statements above are stage history. Required execution now
completed; independent final review is the remaining gate.

- **Revised focused acceptance/mechanisms/oracle:** command
  `PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
  TOKENIZERS_PARALLELISM=false .venv/bin/python -m pytest -q --tb=line
  tests/test_woo_tree_acceptance.py tests/test_woo_tree_mechanisms.py
  tests/test_woo_tree_live_oracle.py`: **77 passed in 0.89s**, saved
  `evidence/focused-final-green.log`. Initial `evidence/focused-final.log` had
  coordinator oracle-test import setup failure; one diagnosed tests-package
  import correction, no production change. Earlier red/green results preserved.
- **Independent absence/fault sensitivity:** the two live-oracle tests passed
  in that run. They inject partial-to-complete/confirmed-empty publication state
  while retaining incomplete receipts and require rejection; inconsistent totals
  also reject. Fault injection is confined to test value objects, no shipped
  production mutation. Threshold search, direct redirect policy, actual trailing
  slash hop provenance and mixed DNS tests passed in the same focused run.
- **Deterministic stress:** `PYTHONPATH=src .venv/bin/python
  tests/woo_tree_stress_driver.py`, **24/24 passed in 8.711s**, observed peak
  RSS **145,375,232 bytes**, `evidence/stress-results.json` and
  `evidence/stress-run.log`. Fixed seed 00920261024, one sequential worker,
  60s driver ceiling, max 1,000 retained categories; all declared cases and
  post-case elapsed/RSS checks passed. RSS checks establish observed peak under
  these cases, not hard OS isolation or unlimited capacity. W10 independent
  coverage approval is recorded in reviews.md before this run. The added exact
  retention threshold acceptance uses <=17 public black-box invocations, not
  the private reservation calculation as expected oracle; stress retains its
  original 24 named slots. Optional bridge SC09/10 is not counted as implemented.
- **Repository regressions:** **1,018 passed in 232.83s**,
  `evidence/repository-regressions.log`. Bounded driver return code 0 and wall
  time 236.24s within its 240s suite cap in `evidence/regression-results.json`.
- **Maintenance regressions:** **106 passed in 106.23s**,
  `evidence/maintenance-regressions.log`; bounded driver return code 0, wall
  time 108.81s within its separate 240s cap. Suites ran sequentially. The general
  suite was collected before seven later focused tests were added. Counts
  overlap; do not add them together as a unique-test total.

### Actual public-store observation
Coordinator executed `PYTHONPATH=src .venv/bin/python
tests/woo_tree_live_driver.py` only after offline success, using saved
`evidence/live-plan.json`. **Live smoke passed** on
https://demo.athemes.com/botiga: **one HTTP attempt, one page, two root
categories, 3.879s**. All six independently checked assertions passed: attempts
bounded, hide_empty=false requested, ID/parent facets present, pointers/URLs/times
match receipts, partial cannot imply empty, and coverage agrees with headers,
page lengths and raw distinct counts. Full portable receipt and assertions are
saved in `evidence/live-smoke.json`; summary in `evidence/live-smoke.log`.

This store's observed traversal was already complete within the small smoke.
Optional expanded acquisition was not repeated against unchanged input. The live
store had no observed child edges or natural category mutation in this sample;
those behaviors are verified only by deterministic real-path synthetic fixtures
and bounded stress. Live success is one deployed public endpoint observation,
not a claim about all stores, private/unpublished categories, snapshots or
commercial change frequency.

### Remaining gate / scope
Independent final diff, coverage and evidence review remains pending. Optional
Shopify mapping bridge remains deliberately deferred, with no inferred product
membership or maintenance integration. No commit, push or PR. Actual session
token counters unavailable; no quota percentage inferred.

Final documentation/clock check: coordinator strengthened existing SC01 to supply
distinct per-page receipt clocks NOW and NOW+1s and assert each page/fact retains
its own clock. Count unchanged; **1 passed in 0.19s**,
`evidence/per-page-clock-green.log`. This is an affected rerun after the focused
77-case run, not an additional unique test. Feature-owned added/updated source,
tests and docs were checked with `git diff --no-index --check /dev/null <file>`
(to include untracked files); `evidence/feature-diff-check.log` records actual
per-file results. No production change or broader suite rerun was needed for
this test/documentation-only strengthening.

## W14 blocking-edge design and red — before production repair
Independent final review found three uncovered paths, reproduced in
`evidence/final-review-probe.json`. Added requirements/expected outcomes to
test-design.md and eight executable cases in `tests/test_woo_tree_final_edges.py`
before production edits. Narrow command: `PYTHONPATH=src OPENBLAS_NUM_THREADS=1
OMP_NUM_THREADS=2 TOKENIZERS_PARALLELISM=false .venv/bin/python -m pytest -q
--tb=line tests/test_woo_tree_final_edges.py`. **7 failed, 1 passed in 0.20s**,
`evidence/final-edges-red.log`: four ID source-alignment assertions report linked
instead of unsupported; malformed IPv6 raises ValueError; first/later escaped
surrogate raise UnicodeEncodeError. Independently valid native-ID sibling and
unrelated malformed label case already passes and must remain passing.

Initial fixture assumed whole-product evidence; actual category evidence retains
`{source_pointer, value}` with `/value` pointer. One diagnosed fixture correction
uses that real existing evidence shape; initial two fixture failures preserved
in `evidence/final-edges-red-fixture-initial.log`, not credited as intended red.
No production repair yet. Affected design review is required before edits; final
W14 remains changes-required. Prior unaffected broad/stress/live evidence remains
valid and will not be repeated without a relevant change.

## W14 approved local repairs and affected green — 2026-10-24
Affected design pass is recorded in reviews.md before the three local repairs.
No shared production files changed.

1. Membership lookup now validates each supported native-ID candidate in an
   isolated observation using existing validate_observations source/pointer/
   conversion checks, plus the existing exact support predicate and native ID
   converter. A malformed candidate is unsupported; an independently valid
   sibling remains sufficient, and unrelated labels do not trigger global
   rejection. Scope mismatch keeps precedence. Existing shared mapping behavior
   remains unchanged.
2. Initial URL splitting, guarded normalization and endpoint encoding now share
   the same malformed-URL boundary. Invalid IPv6 returns unsafe_url without I/O
   and its diagnostic round-trips when within retention cap.
3. Page parsing validates decoded string/key UTF-8 encodability before hashing/
   retention. Escaped lone surrogates produce malformed_json: malformed on first
   page, partial with exactly prior pages retained on later page. No replacement
   characters, fabricated facts or leaked UnicodeEncodeError.

Command: `PYTHONPATH=src OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
TOKENIZERS_PARALLELISM=false .venv/bin/python -m pytest -q --tb=line
tests/test_woo_tree_acceptance.py tests/test_woo_tree_mechanisms.py
tests/test_woo_tree_live_oracle.py tests/test_woo_tree_final_edges.py
tests/test_category_woocommerce.py tests/test_category_shared_contract.py
tests/test_category_review_repairs.py`: **130 passed in 20.94s**,
`evidence/final-repair-focused-affected.log`. This includes 85 feature/oracle
cases and 45 existing affected Woo/mapping/shared-contract/review regressions;
counts overlap earlier runs and are not added as a new global unique total.
All seven intended red failures now pass, as does existing independent support.

Because the general _rows parser changed, reran the reviewed 24-case stress
driver to verify real-path semantics and resource overhead: **24/24 passed in
8.673s**, observed peak RSS **146,325,504 bytes**. Current
`evidence/stress-results.json` / `evidence/stress-run.log` describe this affected
rerun; earlier 8.711s/145375232-byte evidence preserved as
`stress-results-before-final-repair.json` / `stress-run-before-final-repair.log`.
Same seed00920261024, case count, limits and sequential driver; no new sweep.

Completed unaffected general/maintenance regressions and real Botiga observation
were reused; no broad suite or live repeat. Updated manifest final dispositions
and removed stale G2/unimplemented module docstring. W14 independent final repair
recheck remains pending; no feature-complete claim, commit, push or PR. Actual
session token counters remain unavailable.
