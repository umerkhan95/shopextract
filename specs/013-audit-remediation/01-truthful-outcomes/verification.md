# Child01 skeleton and executable red evidence

2026-11-01; author /root/audit_research; source90d5bd1,branch fix/audit-remediation.
No production implementation/stubs. Documentary declarations in skeleton.md;
actual acceptance tests in tests/test_truthful_outcomes.py. G1 PASS retained;
G2 pending independent review. No G3/components or green implementation claim.

## Environment and commands

Use `PYTHONPATH=src OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
TOKENIZERS_PARALLELISM=false .venv/bin/python -m pytest tests/test_truthful_outcomes.py
-q --tb=short`. Sequential one pytest process; full new-file diagnostic wrapped in
subprocess.run(timeout=120). Tool domain worker runs as normal production auxiliary
process, not a model; each runtime closed in finally. No inference/model launches.
Exact session token counters unavailable. Tool polling has10s bound plus owned
runtime cleanup. No production/browser processes launched by fake crawler tests.

## Actual red runs

1. First saved smoke `red-smoke.log`: selected one zero/unknown Python outcome;
  1 failed/45 deselected in1.05s, intended AttributeError missing read-only outcome.
  At that time initial file had46 collected acceptance cases; subsequently reduced
  representative batch status rows and added missing file/discovery seam cases.
2. Initial bounded file `red-full.log`, `red-run.json`:41 collected,28 failed,
  13 passed;18.38s pytest/27.737s wall,exit1. Two native-tool rows stopped at a2s
  polling ceiling; these were harness failures, not intended defect evidence.
3. One diagnosed tool-startup repair: allow10s polling (same bounded real source/
  parser/domain path). Also enrich synthetic Product fixture with image,description,
  SKU so HTML CLI reaches its intended unified path instead of unrelated low-score
  CSS fallback. Final41-case file `red-repaired.log`/`red-repaired.json`:27 failed,
  14 passed;31.66s pytest/41.628s wall,exit1. All4 tool rows now reach intended
  outcome assertions: generic HTML falsely complete, policy and empty native
  extraction succeed, discovery falsely complete. No timeout/collection errors.
4. Discovery fixture correction: Shopify discovery intentionally returns API URL
  even for empty products; that was not an empty-URL fixture. Changed empty case
  to Woo source404 + externally empty seeder + browser disabled, yielding an actual
  empty list through production discovery. Explicitly replaced external seeder in
  every CLI fixture to prevent cache/network library activity. Focused rerun saved
  in red-discovery-fixture.log:2 intended failures,39 deselected in1.30s.
  Positive and genuinely empty URL lists both incorrectly return exit0 today.

Earlier generic CLI runs did not independently intercept the seeder object even
though httpx was controlled; they are not claimed as measured zero-network runs or
fresh store observations. Final fixtures control seeder, HTTP,DNS,crawler external
boundaries. No live verification performed or inferred from these runs.

## Enumerated acceptance coverage (41 collected)

| Group | Cases | Distinct contracts |
| --- | ---: | --- |
| Python assessment |8| zero coverage3; positive unknown/false/true; contradictory errors/reasons |
| OG normalization |5| generic policy,explicit product free,identifier,offer-zero,blank title |
| Static policy/schema control |1| reject generic policy; preserve typed free product |
| Browser transport status |7| single200/404/missing/successFalse;batch200/404/missing |
| Mixed batch |1| retain good sibling and incomplete source |
| Browser policy markdown |1| prevent markdown amount from inventing product |
| Woo transitions |4| first/later404 vs short/empty200 terminal |
| Actual CLI extract |3| emptyShopify/unknownHTML/completeShopify |
| Actual CLI discovery |2| positive/empty enumeration retain unknown coverage |
| Static HTTP status |2|200 vs404 admission |
| Native tool runtime/domain |4|HTML unknown/policy/emptyShopify/empty discovery |
| Atomic CLI output |3|failed preserves file,partial/complete stdout-file parity |

Positive controls pass currently; failures expose missing behavior, not a repair.
Not every planned adverse status permutation is represented in acceptance reds:
302/500/zero/malformed status enumeration remains reviewed mechanism/stress work.
Full repository suite, implementation greens, broader mechanism/stress, actual live
and final review remain pending. Missing mechanisms cannot be waived by these reds.

## G2 blocking-gap repair and focused red evidence

After independent G2 requested changes, designed SC01c feed projection and SC03c
Woo adapter->pipeline->CLI before adding their5 executable cases. Skeleton now
names private helper module paths/signatures and feed/tool dependency consumers.
No production/components changes. Updated acceptance file has46 collected cases;
prior41-case results remain tied to their earlier revision, not a full46-case run.

`red-g2-seams.log`/`red-g2-seams.json`: bounded120s invocation selecting
`feed_own_outcome_projection or woo_later_page_pipeline_cli_retention`.
Actual result3 failed,2 passed,41 deselected in6.82s pytest,exit1. Intended failures:
positive feed with unknown coverage emits exit0; Woo100 then404 emits exit0;
Woo100 thenempty200 unproved pipeline coverage also emits exit0. Passing controls:
empty feed already fails and capped feed already reports partial. Each Woo test
asserts100 retained IDs/raw/normalized records, exactly2 requests and separate
404-vs-normal terminal metadata once the missing truthful exit contract passes.
Mocks replace HTTP transport only; real from_feed/parser/normalizer and
extract/Woo/pipeline/CLI run. Existing CLI error blocks downstream retention
assertions until fixed; no claim of those post-fix assertions passed yet.

Next: G2 re-review of new design, named documentary skeleton and actual5-case
red log. Original G2 changes-required verdict preserved. G3/implementation/full
46-case green and full repository verification remain pending.

## Implementation and focused green evidence

G1/G2/G3 PASS precede implementation. Shared private _outcomes assessment and
_product_admission helpers added; additive ExtractionResult.outcome; CLI extraction,
feed and discovery use truthful projections; unified static/browser admission,
Woo404 and native source graphs corrected. No currency/field/runtime feature work.
First saved `green-smoke.log`:1 pass/45 deselected in0.25s. `acceptance-green.*`:
46 pass13.76s pytest,120s subprocess ceiling. Existing constructors/codecs retained.

`affected.*`:153 passed/2 failed21.57s; both old CLI compatibility expectations
contradicted reviewed FR01a/c. Designed disposition recorded before test updates.
`focused-final.*`:210 passed/1 failed22.30s (211 total, including all46 acceptance
and10 complementary status cases); remaining old exact discovery-data assertion
omitted the specified new coverage fields. Corrected exact expected dictionary;
`compatibility-green.log`:2 passed/63 deselected0.22s. No source behavior changed
in response to that mismatch, no expected fields/forwarded option checks removed.

Required repository driver now running under its standard480s total/240s family
ceilings; `full-suite/` and `full-suite-driver.log` hold actual evidence. Do not
infer full pass from focused checks. Live driver prepared with pinned endpoints
and request accounting, but no live execution until required offline gate passes.
Complementary stress is deterministic10 status cases, not a throughput/load claim.


## Required full-driver blocker and handoff

`PYTHONPATH=src OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2
TOKENIZERS_PARALLELISM=false .venv/bin/python scripts/run_tests.py --output-dir
specs/013-audit-remediation/01-truthful-outcomes/full-suite` ran once, unchanged
configured limits240s family/480s total. `full-suite/report.json` reports main
GROUP TIMEOUT at239.238s, total239.240s,exit1,returncode-15; owned group alive after
cleanup=False. Main reached approximately67%, with4 failure markers but no pytest
node summary before termination. Do not call those failures baseline or fixed.
Reliable-oracle and maintenance families were not started. Full gate NOT passed.

One bounded diagnostic attempted collect-only order mapping to failure markers,
30s subprocess ceiling; it also timed out before mapping could be established.
Saved collection-diagnostic.json. No failed node IDs are known from this run; no
invented candidate results or further collection/full sweep. No focused four-node
rerun could be performed without a valid mapping. User budget limits take priority.

Actual live checks NOT ATTEMPTED because required offline full gate is not green.
Prepared live_driver.py is unexecuted, pinned endpoints/request cap in test-design.
Browser actual-live integration additionally blocked on enforceable subresource
request accounting. Synthetic real-path HTTP/crawler/Woo/native mechanisms passed
within46 acceptance +10 complementary status cases; that does not replace required
live or full-repository evidence. Final independent review and completion pending.

Production diff: private outcome/admission helpers; additive model property;
CLI extract/feed/discovery semantics; generic OG admission; browser status/mixed
batch diagnostics; Woo404 retained incomplete; native tool empty/coverage behavior.
Only existing CLI compatibility assertions changed, with explicit design basis.
No commits/push, model calls, currency fixes, field/readiness/runtime expansion.


## Independent review three-blocker repair

Designed SC02c/SC01d/SC02d before adding11 cases (acceptance57,status10). Saved
`review-repair-red.*`:10 intended failures,1 substring-negative control pass,
46 deselected,3.97s pytest. Repairs: exact ProductGroup/list/schema URL admission;
remove extraction-only empty rule from generic emitter, guard feed explicitly
(store already guards); HTTP200 batch metadata rejection records incomplete
with diagnostic and retains good siblings. No unrelated normalization semantics.

`review-repair-green.*` combined222 cases under120s:216 passed,6 failed,41.72s
pytest. ALL57 child acceptance +10 status cases passed, including11 new regressions.
Six affected failures occurred at legacy helper `completed`100 bounded polls,
not at returned functional assertions: test_agent_tool_api.py::
test_complete_domain_flow_uses_native_code_paths and all five parametrizations
(shopify,woocommerce,magento,shopware,bigcommerce) of test_tool_native_modes.py::
test_native_mode_guarded_parser_and_retained_evidence. Those helper jobs did not
finish within100 polls; no baseline attribution/functional result invented.
New child actual native-tool tests with reviewed10s polling completed successfully.
No test-budget assertion was weakened; no further retry/sweep for these failures.

Full driver previous GROUP TIMEOUT remains failing gate, no rerun authorized in
this repair. Oracle/maintenance and live remain unrun. Source repair ready for
independent re-review, not feature completion. No commits or pushes.
