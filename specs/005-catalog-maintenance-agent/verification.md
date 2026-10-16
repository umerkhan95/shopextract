# Verification evidence

## Baseline (coordinator, reused)

86 passed in 0.47 s: tests/test_identity_matching.py and tests/test_field_resolution.py.
Log: artifacts/catalog-maintenance-agent/baseline-smoke.log. No repeat expansion.

## G2 acceptance red — actual

Command (2026-10-16):
`env OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 NUMEXPR_NUM_THREADS=2 TOKENIZERS_PARALLELISM=false PYTHONPATH=src .venv/bin/python -m pytest tests/test_maintenance_acceptance.py -q`

27 failed in 0.70 s, expected nonzero pytest result. Log:
artifacts/catalog-maintenance-agent/acceptance-red.log. All 27 collected and execute;
failures are explicit NotImplementedError for absent maintenance goal/store/workflow/
category behavior, not import/collection/syntax failures. Five initial contracts
files are stubs; no implementation green claimed. After this run deadline became a
required constructor argument with matching fixture; rerun final result below.

No synthetic mechanism/stress/live feature verification has passed yet. The controlled
transport in acceptance tests is synthetic offline, never labelled live. Remaining
SC01–18 cases stay planned per test-design.md and skeleton coverage limitations.
Counters unavailable to author; no quota estimates. No inference or parallel agents.

Final required-deadline fixture rerun: 27 failed in 0.70 s, same intentional stub
failures; saved log above overwritten with this final run. `git diff --check` clean.

## G2 corrected fixture/protocol red — actual

Same bounded command; final saved acceptance-red.log: 28 failed, 1 passed in 0.86 s.
Passing check executes native HTML parser/normalization and real classify_match:
positive S1 identity exact/non-review, differing source ID negative needs_review.
Positive workflow tests additionally execute this precondition before stub failure.
All 28 failures remain intended missing store/profile/workflow behavior, not a
fixture mismatch. New unknown-advisor bound test is intentionally red. No green
feature/investigation/stress/live claim. Draft components is documentation only.

## G3 lifecycle corrected red — actual

Same bounded command: 31 failed, 1 passed in 1.01 s; saved acceptance-red.log.
Three new failures intentionally identify missing custom definition snapshot and
missing/changed registry recovery guards. Native fixture precondition still passes.
No algorithms implemented; git diff --check clean.

## Slice A #55 durable foundations — actual

Saved smoke first: tests/test_maintenance_store.py initial one real SQLite checkpoint/
reopen/evidence case passed in 0.19 s (store-smoke.log). Expanded focused Store
suite: 13 passed in 1.61 s (store-lifecycle.log). Includes actual two-process kernel
flock death/reacquisition (no inference), unknown reservation/explicit retry ceiling,
cumulative request/token/cost edges, real transaction rollback, cancellation control
while owner lock held, fixed deadline and persisted retry delay/nonretry policy.

Combined Store + acceptance: initially 23 failed/22 passed; diagnosed error text
omitted its structured code when message present, so invalid-goal tests could not
match documented error. One repair makes MaintenanceError text include code.
Final slice-a-focused.log: 21 expected remaining engine/comparison stub failures,
24 passed in 2.52 s. No remaining failures in Store suite; source/workflow/advisor
integration is incomplete by design until B/C. No full-green feature claim.
No unrelated baseline rerun. Finite profile registry declarations implemented for
Store validation/snapshot only; category comparison remains stub. Actual session
usage counters unavailable. No installs, inference or parallel agent launches.

Final dedicated physical-request step append case added for B seam; Store suite
rerun saved store-lifecycle.log: 14 passed in 1.63 s. No duplicated request-step
ordinal or attempt reset on repeated append. Diff check clean.

## Slice B #56 native deterministic workflow — actual

First guarded source correction smoke saved before expansion: 1 passed in 1.57 s,
source-smoke.log. Initial combined check 43 passed/3 failed in 18.60 s: two are
expected C advisor cases; one revealed SystemExit in nested asyncio.wait_for task
terminates the event loop rather than behaving as an isolated fault. Replaced only
test fault type with custom BaseException SyntheticCrash; it still bypasses workflow
error handling, and actual process-death coverage remains separate. After this
single diagnosed instrumentation repair, source recovery+correction 2 passed in
1.96 s (source-recovery-repair.log).

Distinct real-path workflow checks: 13 passed/16.19 s (workflow-mechanisms.log),
including hardware/footwear specs/mass with intact matcher, captured baseline,
category conflict, active cancellation, same-store second runner, redirect accounting,
cache exact expiry/evidence eviction and known transport retry. Added explicit
unknown retry and native sitemap discovery: 2 passed/3.18 s (source-retry-discovery.log).
B aggregate (only two C advisor tests deselected): 59 passed, 2 deselected in 35.02 s,
slice-b-green.log. Subsequent narrow safety refinements retain timeout/checkpoint
unknown reservations and settle known failed boundary receipts atomically.

Optional parent request hook preserves legacy tool defaults. Callback denials become
ToolError with same structured code/last_error so native adapters cannot swallow
parent budget failures and fall back to apparent success. Logical capture checkpoint
validates child settlement belongs to same job and declared parent kind. No actual
source network/model calls; HTTP and clocks are controlled offline boundaries.

B affected existing regression command (same bounded environment):
pytest tests/test_tool_redirect_credentials.py tests/test_tool_discovery_lazy.py
 tests/test_agent_tool_api.py tests/test_identity_matching.py tests/test_field_resolution.py -q.
Result 99 passed in 7.92 s, slice-b-regressions.log. No full-suite repetition.
Final targeted refinement checks (unknown explicit retry, known transient retry,
six actual category/mass cases): 8 passed in 11.68 s, slice-b-refinements.log.
Refinements enforce exact selected evidence attribution, freshness in cache key,
matching-claim-specific identifier support, missing footwear size-system review and
currency provenance. Source allowed_tools/authorization errors remain explicit and
zero-send; no new fallback. Diff check clean. C's two model-invocation tests remain
intentionally unimplemented and excluded from B-green aggregate.

## Slice C #57 advisory boundary — actual, incomplete FR05 retry

First small saved smoke: unknown usage retained and second eligible call budget-
blocked, 1 passed/1.64 s (advisor-smoke.log). Focused advisory + original C acceptance
checks: 10 passed/14.09 s (advisor-focused.log). Real injected adapter observes the
accepted immutable reservation; no model/provider process is launched. Cases cover
known settlement, exact advisory cache, model/price identity, injection/forged IDs,
conservative invalid-result charge, explicit actual usage overrun/violation stopping
second dispatch, pre-call cost denial, timeout and selected structured payload.
Additional crash/no-replay, changed-price cache invalidation and invalid-bound
checks: 3 passed/4.37 s (advisor-recovery-cache.log).

**Required remaining red:** explicit retry of unknown advisor after resumed partial
finding currently rejects invalid_argument because retry_unknown supports sources
only. Saved advisor-retry-required-red.log: 1 failed/1.76 s. Requirement FR05 is NOT
waived. The test requires stable base finding/status/before/after, a newly available
advisory and old reservation retained (64 old +36 new tokens). Do not claim C complete
or all acceptance green. Separate immutable advisory attempt publication/composition
needs design refinement and independent approval before implementation, rather than
silently rewriting committed base findings. No repair to production attempted yet.

New trusted-only checkpoint violation flag records known actual over-bound model
usage in the ledger, increments violations and halts model work; it does not pretend
remote spend remained within bound. Normal/source settlement still rejects overrun.
Accepted bound/payload digest is durable before invocation; returned advice is
schema/evidence checked and cannot change deterministic status/matching/profile/
budgets. Unknown spend retains full reservation; cache publication occurs only after
committed finding/settlement. No raw HTML/catalog in selected model context.

Final C + affected Store/original C checks (same bounded env):
pytest tests/test_maintenance_advisor.py tests/test_maintenance_store.py
 tests/test_maintenance_acceptance.py::test_advisory_cannot_authorize_title_only_identity
 tests/test_maintenance_acceptance.py::test_unknown_advisor_usage_retains_bound_and_blocks_second_call
 -q -k 'not explicit_unknown_advisor_retry'.
27 passed, 1 required FR05 red deliberately deselected in 18.89 s; saved
slice-c-focused.log. Exclusion is explicit incomplete coverage, not feature passage.
Diff check clean; no full-repository suite, live requests or model execution.

## Interim I-01..03 + FR05 repairs — actual

Predesigned review reds: 5 failed/5.73 s (interim-repairs-red.log), covering two
candidate orders, zero-product discovery and repeated unknown/violation recovery.
Additional retry boundary reds: 4 failed/1 already-passing cancel in7.16 s
(advisor-retry-boundaries-red.log). Original explicit advisor retry red retained.
After reviewed repair:11 passed/13.72 s (interim-repairs-focused.log).

Publication/policy tests initially2 failed/1 passed in4.44 s
(advisor-publication-policy.log): durable unknown halt prevented recording prior
outcome_unknown advisory history on resume. One diagnosed repair permits committed
unknown-outcome publication for prior attempt without permitting fresh model calls.
Rerun3 passed/4.21 s (advisor-publication-policy-green.log): failed report publication
keeps previous composition and2112 reserved tokens, cancellation keeps previous
composition and128 reserved tokens, missing custom profile prevents dispatch.
No expectation weakened; retained publication/usage invariants are asserted.

Final focused feature command (same bounded env): pytest
 tests/test_maintenance_store.py tests/test_maintenance_workflow.py
 tests/test_maintenance_acceptance.py tests/test_maintenance_advisor.py
 tests/test_maintenance_review_repairs.py -q.
Result:86 passed in67.63 s, maintenance-repairs-green.log. No exclusions remain.
A final internal retry lookup removes public-page-limit dependence (no behavior
expansion); explicit retry rerun1 passed/1.48 s, advisor-final-retry.log. Diff check
clean. No repository fullsuite/stress/live executed during this repair assignment.

## I-04 / R01 shared completion repair — actual

Predesigned native partial-capture/advisor retry + pending independent source/compare
reds:3 failed/4.38 s (completion-retry-red.log). Shared Store.completion now evaluates
persisted source completeness, uncommitted source/comparison work, preserved coverage
and durable model outcomes; Engine normal completion and explicit advisor retry use
it. finish without new coverage preserves existing coverage instead of replacing{}.
One diagnosed repair, targeted rerun6 passed/8.26 s (completion-retry-green.log),
including existing stable finding retry, failed publication and attempt2 unknown/
attempt3 rejection. No broad rerun or D expansion yet; reviewer confirmation pending.

Reviewed-code candidate SHA-256:
store.py 4dedee2b756310fbee0a8c26090b082fe0849bf1c73d0b673b0be5780a82c8b0
engine.py 9a0419664a5e59f1fc10296c6ebe3c29373a6bf0f0ee9c37c1d832d9ed30fb24
test_maintenance_review_repairs.py 24b1a82156acb69a0b63a5ee0df7a47d44e7162307e473674ebba99bef941322

## D bounded driver checkpoint — STOPPED for timeout-plan review

New driver: tests/maintenance_stress_driver.py, seed25. First native3-item smoke
saved before expansion:2 unchanged/1 correction/0 review,2 physical requests,
zero advisor calls/tokens;1.605 s and92.91 MiB parent peak RSS. First100-mixed-disabled
case hit cooperative5 s timeout, observed10.716 s including delayed event-loop
handling/cleanup. Saved stress-first-timeout/{config,progress,smoke}.json and
stress-first-timeout.log. No remaining cases executed in that run.

One diagnosed bounded repair materializes full dataclass matching dictionaries once
instead of per candidate pair; it preserves all identity/variant fields and calls
unchanged match_products. Product objects remain available for own actual trust/
source evidence checks. Second native smoke passed same2/1/0 counts/zero LLM,
1.606 s and93.74 MiB RSS.100-mixed-disabled again timed out:observed9.516 s.
Saved stress-second-timeout/{config,progress,smoke}.json and stress-second-timeout.log.
No second optimization attempted. The5 s asyncio timeout is cooperative, NOT a hard
wall-clock guarantee; observed runtimes are recorded honestly. Failed batches are
not counted passed/completed. No fullsuite/live/model/inference executed.

Stopped per coordinator pending independent plan amendment. Remaining execution:
100 mixed disabled,100 mixed enabled exactly5 eligible advisor calls,100 exact zero
calls,20 crash/replay cycles,18 byte/token/cost/request/deadline edges,8 pairwise,
6 new category executions plus2 exact saved-category reuse citations,2 temporary
mutations restored; remaining SC edge fixtures/public docs/fullsuite/live/final review.
Current driver has not executed or claimed these planned counts. During arithmetic
inspection evidence-byte edge setup was corrected to include serialized null step
result bytes; its cases have not run, no result inferred.

Proposed amendment (UNAPPROVED): only100-item batches15 s in dedicated sequential
case subprocess with external process-group deadline and <=1 s kill/reap grace;
unchanged global driver180 s with external group guard, small cases5 s/crash10 s,
worker1, RSS256 MiB/input256 KiB/evidence16 MiB and stop-first-failure. No additional
sweep or domain. Independent reviewer must approve before resuming. Save exact
wall time and forced cleanup separately; never describe async timeout as hard cap.

Equivalence check design pending: actual native parsed Product pairs and equivalent
full asdict inputs to match_products must agree on relation,needs_review,confidence,
evidence strings,conflicts,index_a/index_b,candidate_method for positive, source-ID
conflict, RAM/variant conflict and duplicate exact ambiguity. Optional MatchDecision
field_support differs for dictionary inputs; maintenance must retain independent
actual trust/evidence references and observable report evidence inspection. This
optimization does not alter the public existing tool match path. No extra check
executed after stop instruction; reviewer decides before continuation.

## D final stress receipt and budget correction — actual

Prerequisites3 passed/5.99 s (stress-prerequisites.log): real Product/full-dict
matcher equivalence (relation/reasons/conflicts/indices, documented optional support
metadata difference), actual captured report evidence, hung worker+descendant killed/
reaped, genuine post-source/pre-comparison checkpoint crash with expired cache and
isolated replay mutation detected. Old completed-job checkpoint detector is superseded.

Stress driver uses external per-case process groups, only three100-item cases15 s,
small5 s/crash10 s, measured<=1 s cleanup, original180 s cumulative/256 MiB/one-worker
limits. Original breaches remain historical. Enabled100 initially failed eligible
context assertion: many similar-title candidates caused all context to be dropped.
Minimal real3-product fixture1 failed/1.68 s ->1 passed/1.54 s after one repair:
only one positively identifier-anchored candidate may provide review context;
actual relation/needs_review/conflicting attrs and duplicate anchors remain unchanged.
Completed100-disabled evidence was reused because deterministic status/count invariant
is unchanged. Deadline edge later failed fixture construction (deadline belongs to
Goal, not Budgets); one fixture correction, previous passes reused, no cap increased.

Final47 newly passed cases +12 exactly cited prior proofs =59 reviewed driver cases.
Includes all three100-item batches,20 crash/replay cycles,18 resource edges,8 pairwise
and8 category cases (some reused), both real temporary budget/checkpoint mutations
caught and restored.47 counts NEW executions;12 REUSED entries identify log/test and
current applicability in stress-resumed/progress.json.2 failed workers remain history,
not passed.3-item smoke was separately saved before expansion.

Author initially omitted pre-amendment receipts from cumulative arithmetic; corrected
audit includes ALL runs:23.443 s observed original smoke/timeouts +6 s reserved parent
startup;22.028969 s first amended workers +3 s reserved startup;92.198975 s guarded
continuation;25.756285 s guarded final continuation. Total charged172.427229/180 s,
including conservative startup reserves; max worker RSS170.49 MiB. Original internal
summary142.814 s is retained but is NOT the full cumulative budget. Authoritative
stress-resumed/summary-corrected.json and cumulative-budget/watchdog/outer receipts
show correction. No remaining driver cases; no broad restart/sweep.

## Remaining distinct SC edges and operating checks

remaining-edges-red.log:5 failed/2 passed in10.12 s; one diagnosed repair per distinct
failure: expired/unsupported baseline classification, footwear size-system mismatch,
scalar/version-corrupt cache rejection. remaining-edges-green.log:6 passed/1 distinct
missing-dynamic-contract failure in12.28 s. That absent attachment is a separate
legacy baseline failure; getattr fallback repaired it. unsupported-zero-green.log:
3 passed/4.14 s, including explicit zero price versus boolean false. Supported captured
before-values, expiry during pause, escaped attribute pointers, cache policy denial,
custom color role, size-system context and prior SC cases have actual real-path proof.

Compile, CLI help, synthetic offline example, CLI create/status and old8 tool schemas
passed; logs named compile/cli-help/offline-example/cli-create/cli-status. No inference
or external source involved. Wheel check BLOCKED: local frontend `build` and backend
`hatchling` both absent; no install attempted, wheel.log records original failure.
This limitation is not a successful package build. Public API/CLI/recovery/category/
provider limits in docs/catalog-maintenance.md; runnable examples/catalog_maintenance.py.

## Whole-suite deadline checkpoint and read-only diagnosis

Actual single run: full-repository-suite.log / full-repository-suite-receipt.json:
240.032077s outer wall deadline, SIGTERM returncode-15, cleanup0.021925s.
No failure characters observed; this is a timeout, NOT a passing full suite.
Collect-only1.54s yielded923 unique ordered nodes. Strict whole-line qchars
contain783 dots; full-suite-progress-map.json maps those783 completed passes.
140 nodes remain unconfirmed. Next collected node is
`tests/test_reliable_changes_stress.py::test_sm09_seeded_event_oracle[2909-7]`;
quiet log does not prove that node started. No percentage-derived pass claim.
Ordered and unconfirmed node files saved. Source-identity-after-full-suite.json
matches all20 manifest entries. No source/test changes since pre-suite receipt.

No suffix execution or CI edits. Proposal awaits independent reviewer:
same existing matrix job, sequential existing817 and maintenance106 nodes with
240s per partition, no added parallelism. No promise partition timing fits yet.
Actual Bliss live remains unexecuted. Packaging remains build/hatchling missing.

A shell launched before stop steering also completed the already-prepared
real engine OS-death fixture; engine-os-crash.json/log:2passed in5.798033s.
Both actual os._exit91 windows reopen SQLite and resume with0newrequests:
before source checkpoint retains2unknown charges/partial; after committed source
checkpoint yields completed/0unknown. Controlled native HTTP boundary, real
engine/parser/SQLite, no actual external network. No further rarecrash runs.
These distinct SC edge receipts are outside the completed172.427s stress driver;
no reclassification of stress totals. Session counters remain unavailable.

## Approved suffix completion and CI partition

Reviewer-approved run only unconfirmed140 nodes, no783repeat. Actual bounded
run-approved-suffix.py: first seed1passed in8.58s pytest/10.838716s outer;
remaining139passed in51.55s pytest/53.937256s outer. Aggregate64.777606s/240
including both interpreter startups and cleanup. No timeout or failure.
Receipts suffix-receipt.json, suffix-seed.log, suffix-remaining.log.
All923 distinct nodes now have observed passing outcomes across the original
783-prefix and suffix140. The original whole-suite240s command remains timed out.

Approved CI edit only: .github/workflows/test.yml keeps same3-version matrix/job,
two sequential explicit disjoint file partitions existing817/maintenance106,
each240s. Aggregate per matrix job now up to480s, previously240s. No extra
parallelism. ci-partition-receipt.json records7maintenance test files and exact
counts. No second local whole-suite run. FR01–12/SC01–18 exact-node map in
coverage.md; named-node references independently checked against AST definitions.
Git diff --check passed. Missing build/hatchling remains packaging limitation.

## Actual live — approved bounded Bliss phases

Actual origin https://www.blissworld.com only; no credentials/model/provider.
Approved config live/config.json:2items,3physical requests/phase,6total,
10sattempt/30sphase/60stotal; external group guard59s plus <=1scleanup.
Phase1 smoke saved before phase2:2products,2HTTP200,8.795886s, native structured
Shopify capture (homepage and products.json?limit=2&page=1). Actual evidence files:
live/phase1-capture.json, phase1-smoke.json, phase2-report.json,
phase2-evidence.json, summary.json and execution.json. Phase2 native engine:
2HTTP,2unchanged title findings ('Bliss Halloween Costume', 'Salmon DNA Duo'),
linked captured evidence, honest partial/source_partial because itemcap2,
restart0additionalHTTP, LLM0tokens/cost. Total4/6HTTP,18.440964sinner,
19.941616souter, no timeout. No actual commercial specification change observed;
correction/crash/category/advisor proof remains separately labelled synthetic.
No retries/further domains/live runs. Final exact requirement map coverage.md.

## Final author disposition

All923 distinct collected tests confirmed passing across783prefix+140suffix;
original240s whole-suite timeout retained, no whole-suite repeat. Separate D
stress47new+12reused172.427s and OSdeath2passes5.798s retained independently.
Source/test/API/docs20-entry manifest unchanged from pre-full-suite. Approved
CI-only change adds same-job sequential partitions; aggregate cap480s disclosed.
Final manifest adds CI/spec documents; unrelated dirty specs004 excluded.
Compile/CLI/example passed. Wheel remains unbuilt because build/hatchling missing;
no install. Actual session counters unavailable. No provider inference, source
writes, Git commits/pushes or external issue mutations by author. Final independent
review still required; no final gate verdict claimed by author.
