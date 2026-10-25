# P5 independent reviews

## G1 — 2026-10-25 — changes required

Reviewer: `/root/cli_p5_delivery/p5_reviewer` (independent of author
`/root/cli_p5_delivery`). Review is static design/native-code inspection; no
execution or later gate approval is claimed.

Reviewed SHA-256:

| Artifact | Digest |
| --- | --- |
| spec.md | cee597f1d66dc7403c9268d6b055f777c237596264c8cea30e334c8172e51cc5 |
| test-design.md | 5a4db74948d5367156eda504ce93529c38700138ebbfbfb25124e139fc971bca |
| tasks.md | ffc51918dda19a268608a9a8d1b271d4df9753fe1d12e7333161fddc9f5b4537 |
| research.md | 7d6180bf534a2e77d9c994f1eb8422f2123bbe34637d337c95f72989d9a2d1cc |
| plan.md | 73c870b3dd0942b25d3523a9fc4ca0b04504d3e85939963b82c77e26ce411c3e |

Also checked parent spec/test design, workflow/constitution, native maintenance
contracts/store/engine/module CLI, tool contracts/runtime/MCP/module CLI and root
CLI bootstrap/response policy. Native reuse, source-read-only maintenance intent,
session/durable namespace separation and genuine wheel/SDK checks are sound.

### G1-01 — blocking — session wire and operator-file contracts incomplete

`P5-FR03` defines step fields and references, but does not define the per-step
stored result or final session result shape. Native `bootstrap()` returns raw
`{schema_version,captures,limits}`, while native `call()` returns an envelope;
thus a reference into bootstrap versus match has different paths. `poll` terminal
state behavior (failed/cancelled/expired), `pages` argument schema, and whether
helper outputs retain native envelopes are unspecified. The native operator
config is unversioned and has exactly allowed_origins/allowed_tools/captures/limits;
the proposed packaged config/schema inventory must say explicitly whether that
format is preserved and define new profile/session/helper formats. Otherwise
valid client requests and independent expected results cannot be authored before
implementation.

Required disposition: record closed file/helper shapes, required/default fields,
version ownership, per-step/final outputs and one exact bootstrap -> match ->
poll -> pages reference example. Define polling of non-success terminal jobs,
native-error versus partial-page outcomes, and the partial cursor path. Add
independent acceptance expectations for those paths and version/type rejection.

### G1-02 — blocking — maintenance deadline/interruption contract untested

`P5-FR01` promises a total bounded timeout, but the timeout row in test design
covers session pages only; no expected maintenance timeout exit/state or
interruption recovery is specified. Native `MaintenanceEngine.run()` catches
`asyncio.CancelledError`, marks the job cancelled and returns a report. Therefore
a simple `wait_for(engine.run(...))` may return a cancelled report instead of
raising TimeoutError; generic success serialization can violate the bounded
operation's error contract. Parent SC08/09 explicitly requires interruption,
resume and cleanup, which zero-product happy paths cannot prove.

Required disposition: define timeout and SIGINT outer code/exit and persisted job
state, then design a controlled slow-boundary test through the real engine plus
a subsequent CLI process checking durable state/resume. Assert no worker/lock is
left behind and timeout is never reported as successful completion. Also predesign
a request/native-error cleanup case (not only a successful session close).

Disposition: both findings open. Re-review changed design before G2. Parent24
case mapping, exact byte/page boundary expectations and independent fixture
review remain explicit prerequisites of stress execution; their future planned
status is not a coverage pass.

## G1 re-review — 2026-10-25 — pass

Reviewer: `/root/cli_p5_delivery/p5_reviewer`, same independent reviewer.
Revised spec.md SHA-256
`39032b47c88d266ab1d9ed63d646848028f2eb2d5c4e190383fbe5a5c2147e93`;
revised test-design.md SHA-256
`dffc024aa392f53d3d4fe7fd9be3e5797dce2381ff0c29e41d37fce59c91a136`.
tasks/research/plan digests unchanged from the first review.

G1-01 resolved: exact native/operator compatibility, helper shapes, prior-result
reference paths, result framing, partial cursor and terminal-error behavior are
now specified with a concrete request. G1-02 resolved: observed total deadline
rather than cancellation return controls timeout outcome, timeout/SIGINT durable
cancellation and cleanup have independent expected checks, and native-error
session cleanup is explicit. Rechecked native terminal states and cancelled
resume: `MaintenanceStore.begin()` rejects cancelled jobs with `invalid_state`;
test expectation now correctly requires E_OPERATION/exit1 with unchanged durable
state and no dispatch.

Verdict: PASS for behavior/test/task/research design. No implementation, stress,
runtime or later-gate approval is implied. Planned parent24 mapping and exact
boundary cases still require coverage review before their execution.

## G2 — 2026-10-25 — pass

Reviewer: `/root/cli_p5_delivery/p5_reviewer`, independent of author. Reviewed:

| Artifact | SHA-256 |
| --- | --- |
| skeleton.md | 24fcdfd65f822262f91f527eba72890049b7bd804c0980f1cdafdb43a1f8cb7f |
| tests/test_cli_operations.py | 0db6661b5541cbf032530a7aca416ac764101142cf8bcea7db042a8641223d9c |
| evidence/acceptance-red.log | 4be93ef70884a41e0ecb469dd20b97574b4b30b551c335875d21fc19cb26f430 |

Declarations separate discovery/static schemas from runtime creation, retain
native authority for tools/maintenance, put protocol exemption in root bootstrap,
and explicitly address cancellation-swallowing native execution. No fabricated
public stubs or business implementation occur in the skeleton. The six red tests
exercise all new command families; saved failures are missing-command E_USAGE,
including the serve stdout assertion, rather than import/dependency failures.
Checked native queued state/report fields against the maintenance test.

Verdict: PASS for skeleton and intended-red family seams. These are smoke tests,
not completed scenario coverage: durable cross-process recovery, nonempty native
capture/ref/page/evidence mechanisms, constructor traps, recursive full grammar
equality, timeout/SIGINT, strict boundary validation and genuine SDK/wheel proof
remain required as already designed. Later coverage review must verify distinct
assertions for them; function names alone (such as "durable" or "lazy") do not
establish that evidence. Red log inspected without redundantly rerunning it.

## G3 — 2026-10-25 — pass

Reviewer: `/root/cli_p5_delivery/p5_reviewer`, independent of author.
components.md SHA-256
`c52e0aba08eec3f541826b893a1b34782d0bf2f18c83bee0dc36e7a36078f5b1`;
skeleton.md remains
`24fcdfd65f822262f91f527eba72890049b7bd804c0980f1cdafdb43a1f8cb7f`.
Spec/test-design digests remain the G1 re-review revisions.

Checked declared existing loaders/runtime-file helper/CoreCommand, native store
constructor validation/category ownership, engine cancel/close, tool runtime
validation and worker reaping seams. Responsibilities have concrete consumers:
one shared bounded loader, one deadline observer and central envelope sizing;
native durable/session state machines retain authority. New store list query
and package schema discovery have limited stable responsibilities. Static
discovery does not construct native runtime or invoke command callbacks.
No new generic framework, duplicate domain algorithm or executable configuration
is proposed. Verdict: PASS. Timeout/SIGINT cleanup, byte-cap response behavior and
new list ordering/pagination remain runtime assertions for implementation and
coverage/final review, not established by this component design approval.

## Coverage / pre-stress implementation review — 2026-10-25 — changes required

Reviewer: `/root/cli_p5_delivery/p5_reviewer`, independent of author. Reviewed
coverage proposal, expanded test design, operations/discovery/core/store list,
native session fixture and controlled slow-wire subprocess fixture, schema
generator/resources, API audit script/result and saved green evidence. Reused
parent stress status files were inspected; mapped evidence remains labelled
offline rather than live. No broad suite was rerun. One small real-loader probe
was executed and saved as evidence/reviewer-preflight-probe.json.

Reviewed SHA-256:

| Artifact | Digest |
| --- | --- |
| coverage-review.md | 65ab0d5a0908a9c3b8843e5f86d0caef524ebe42fe2a4bebc3a488201b014365 |
| test-design.md | cf00d4b5d7c983bdf5ff2e8473c1ffed313a48944a2e51a8bb4905ffad81a1df |
| spec.md | b84b3b35b4e3e1a88b15805dbe5511945dbb3f2dca6ddac40ac7f4b66957e1ed |
| _cli_operations.py | b454f01c662edda8ab1b6c3a0b29bbf4e5ed9140de77a944f9fdc61eb66b63d2 |
| _cli_discovery.py | 2c04ecbcc387b3b204b20dbf205d6c1a044ff95b866fa3ad5c3ec1878c7a189f |
| _cli_core.py | 466063f26bda33b15e5451db67732e87540816edf508e79bb1622ada26a1061b |
| maintenance/store.py | ce5c57c7c00ff028497ee68e72326f19c97d90c333ba0f845c5c53bec2af4e2a |
| tests/test_cli_operations.py | 79d17647ac38209809002ded33cd4b6cb2da57404777bb5422dfe54513a1442d |
| tests/cli_operation_fixture.py | bd7dd08c4085a875c8c71a9704840dec58b5dd09e0691ad49e609348eb1533a9 |

### Coverage-01 — blocking — literal preflight bypasses

`preflight_arguments()` defers every dictionary in numeric arguments rather than
only exact validated reference objects. The saved probe confirms `load_session`
accepts `{invalid:1}` as poll interval_seconds, pages max_pages and extract
max_items. Earlier bootstrap may then perform capture/database/worker work before
later dispatch rejects the literal. Moreover validation uses default `Limits()`
rather than loaded operator limits: item_count=1 with later literal max_items=2,
or a reduced input_bytes cap, can also allow earlier side effects. This violates
the promised full literal validation before runtime/work.

Required disposition: distinguish references from arbitrary JSON objects; load
operator configuration and validate every literal step against its effective
limits before constructing runtime. Add constructor-trap cases for malformed
numeric objects and stricter operator item/byte limits in a later step. Include
valid numeric references as a positive case so the repair does not remove the
advertised reference support. Predesign exact outcomes, then save focused results.

### Coverage-02 — blocking — discovery output contract omits artifact streaming

`command_inventory()` classifies `export` as unconditional `json-envelope`, but
`export --output -` writes raw artifact bytes through the real export path.
Clients relying on capabilities will attempt to parse CSV/feed/Parquet as the
outer envelope. The discovery acceptance currently checks four path inclusions,
so it cannot detect incorrect leaf output contracts or omitted options/defaults.

Required disposition: expose the conditional export stdout/artifact contract and
add independent recursive equality checks against Click paths, options/aliases,
defaults/arity/choices plus explicit expected contracts for protocol, streaming,
legacy and envelope leaves. Preserve package grammar evidence for final review.

### Coverage-03 — required distinct coverage before completion

The two-product native SQLite/capture fixture is realistic: production matching,
pagination and evidence ownership execute, with only external transport mocked
for slow-source checks. SDK protocol and cross-process durable checks are genuine.
Parent24 reuse/new mapping and declared limits are adequate for the planned
bounded stress driver after the blockers above are fixed. However add distinct
tests for native list ordering/offset/limit over multiple jobs (one-row smoke
does not prove pagination), a supplied foreign category-policy digest on an
existing job (current test checks matching policy only), and at least one valid
custom profile (current test covers collision only). These gaps are new API and
feature-interaction risks, not covered by parent category/replay stress.

Correct components.md's remaining `CategoryRuntimeConfig integer1` statement to
native unversioned; spec now accurately follows the native codec. This correction
does not change the approved architecture.

Verdict: CHANGES REQUIRED before stress execution. Findings concern actual
preflight behavior/discovery correctness and missing independent assertions;
saved 103-pass integration evidence remains valid for the cases it exercises.
Wheel/full-CI/final whole-feature verification remain pending as planned.

### Coverage repair recheck — 2026-10-25 — pending final small dispositions

Same independent reviewer. `_cli_operations.py` SHA-256
`8c8f278a595c89179401426c722ffbf235f42262ffefc33f97b75028ba6c22ce`;
`_cli_discovery.py`
`17c7847b976ad3835f9fa1b2d0a7aa2120a3b646aa46638aad23e165ee07af36`;
tests/test_cli_operations.py
`4353cc3ea841eeba91f6c070cab6da11a6a331b39bb13d46cdde816c9182877e`;
bounded-driver.py
`3cd9d52b0efc792cce610596dcab3481e2196aa62ca2b65f47a5a66b454c0d5a`.
Saved 112-pass repair result inspected. Repeated only the three small real-loader
probes: all now E_USAGE (evidence/reviewer-preflight-recheck.json). Effective
operator limits now participate before runtime. Export contract accurately
exposes raw artifact stdout. Added three-job pagination, selected valid custom
profile and foreign category policy rejection exercise their real native paths
with useful independent expected outcomes.

Stress driver inspection: sequential groups, explicit per-group30s/total720s,
aggregate process-group512MiB RSS, thread/offline caps, per-group status saving,
unexpected-failure stop and orphan kill/check meet the declared plan. This is
driver design inspection, not an executed stress pass.

Remaining from original disposition: independent recursive full grammar equality
assertions; positive numeric-reference real-session case; components.md native
unversioned correction. Author notified and will request final small recheck;
no repeat full112 suite is needed solely for those additions. Coverage verdict
remains pending those checks, with behavior repair findings resolved.

## Coverage / pre-stress final recheck — 2026-10-25 — pass

Reviewer: `/root/cli_p5_delivery/p5_reviewer`, independent of author. Revised
tests/test_cli_operations.py SHA-256
`01ac655b749707f14fec4f5d4d9ed0e1595c67fcbd931c8cb3a1032da73372f2`;
components.md `2856101c4550fb255ffb6305f45355f7762c2f3ef84ee9b4749145b0383ce78a`;
test-design.md `2bcc7b1fcb547e4b023b09ff58f2104e0b7d31f030f165d65112a011e88b037b`.
Production operation/discovery and driver digests remain those in repair recheck.

All coverage findings resolved. Full recursive independent Click comparison now
checks complete paths/parameters, aliases, arity, required/multiple/flag behavior,
types, JSON-safe defaults, choices and ranges. Exact protocol/streaming output
contracts have explicit checks. Real session positive numeric references use
bootstrap limits for page size/max pages and retain both expected match rows.
Components accurately records native unversioned category config.

Saved focused evidence inspected: coverage-recheck.log (2 passed, 3.57s), then
grammar-final.log (1 passed, 0.18s; SHA-256
`23004d7ee05d423d42523c8c6a6960524ecbe5ad6b46b8491ef00c8f336b80eb`).
No unnecessary full-suite rerun. Real-path fixtures, parent24 reuse/new mapping,
distinct adverse additions and driver limits meet pre-stress review requirements.

Verdict: PASS to execute planned bounded stress and scoped mutation/restoration.
Stress, wheel, full regression and final whole-feature runtime verdict remain
unexecuted/pending and are not implied by this coverage approval.

## Final whole-feature review — 2026-10-25 — completion changes required

Reviewer: `/root/cli_p5_delivery/p5_reviewer`, independent of author. Inspected
P5 final status/verification/traceability/tasks, actual code and expanded tests,
native module preservation, public API reconciliation, docs/examples/schema
resources, wheel driver/report, stress/mutation evidence, full-run logs and exact
completion accounting. P0–P4 final approvals remain prior-phase evidence; they
are reused by the explicit FR01–10/SC01–10 (including suffix cases) mapping,
not relabelled as a new P5 execution. No new suite/model/network run was performed.

### Reviewed revision / evidence digests

All current production Python files match the hashes in capability-manifest.json
(zero mismatches). That manifest SHA-256 is
`ac978fa55ef784210a9a557c5e813e728f6e6371875ca1a7e824a224e6386e00`.
P5 final-traceability.md:
`d39e8fab0daa789187603792dfc84a11b032198679c65299246efc0dc1384f4a`;
verification.md:
`bb94127117898329d429c6448f3d3a401c035ef8296ce3151aec87eb7562c4ff`.

| Evidence | SHA-256 |
| --- | --- |
| stress-status.json | a0929a7c6c85792f54cc9939ecffe36927b0d5e97694ede6223d5b6b542df573 |
| mutation-report.json | 3ed7bf379d53fbbb2abaa7e9eff8596782af9f5a40d33bc9953cb341bf450193 |
| wheel-report.json | cb5df191f87bba2aa1d51bcee76f866ea3c2e62ef2e5e97e272db59d5ea17a28 |
| full-status.json | 3267ec0492ea8aa175b50ece04d99c9ddd9d372a412c331ddb6b289f82f16da4 |
| full-completion-status.json | 2f48ea2cad18dca1f23ee33cdc78abfc576c4e657628e308326fbb14b4f9626a |
| completed-test-accounting.json | 50cce78ce6744247c754d281c4cea9447efb72b0d8097fe7a3a077e54faf7226 |
| complete-remainders.py | 472e759ff125cb19f1db221deb11bc0207340f4427a0f1cc4bde211bc10885cf |
| wheel-check.py | 5b38687b3621145b0c04ac498e750fb9d5efa3cb264df62ad195bc8e838e2b01 |

### Findings / completion disposition

**Final-01 — blocking completion — mandatory configured main CI group lacks a
passing invocation.** P5-FR05/spec and the reviewed research/tasks require full
CI-equivalent groups; the actual workflow runs the main group under 240 seconds.
Saved main invocation was terminated at 240.165s (exit -15, timeout), rather than
passing. The later exact-node completion establishes individual case coverage;
it does not establish that the configured main group passes its required gate.
No assertion failure or feature defect is inferred from the timeout. No cap raise,
requirement waiver or CI change is authorized by this review.

Required disposition: retain the exact required-check limitation and unfinished
final completion status until a passing configured main-group result exists, or
the requirement receives an explicit authorized disposition. Do not mark the
original invocation or full CI-equivalent gate passed on the strength of split
coverage. No additional expensive rerun is requested by this review.

**Individual case accounting accepted with its stated assumptions.** Independently
recomputed the 1249 plain passing progress glyphs, verified collection hash,
disjoint prefix225-remainder partition of1474 main cases, and exact equality of
remaining command node arguments. Default serial collection has no recorded
random/xdist/reordering configuration; in-flight node is conservatively rerun.
225 remaining cases pass, and106 native maintenance cases pass separately. This
supports1580 collected-case passing coverage, with original full-command timeout
preserved. Independent compact check is evidence/reviewer-final-check.json.
It does not supply a successful single-session teardown/group timing result.

**Implementation/package/mechanism review clean.** No further blocking code,
fixture, schema, documentation or API mapping finding was identified. Reviewed
tests exercise native durable state, real engine cancellation/locks, captured
ToolRuntime ownership/matching/pages/evidence, origin and literal/ref restrictions,
actual official SDK stdio, errors and cleanup. Parent24 mapping retains valid
prior cases and adds distinct P5 cases; five bounded groups19executions pass in
45.041s with0orphans and max aggregate RSS212385792 bytes. Actual scoped mutation
fails the real same-session acceptance, then restores identical source bytes and
passes; current source matches reviewed manifest after the rejected fractional
limit hypothesis. That rejected experiment is not counted as feature evidence.

Genuine wheel report/driver prove a new external venv, cleared PYTHONPATH and
site-packages import origin, all85help paths/70leaves under constructor trap,
17schema files/24lookups, console/module capabilities parity and documented
offline examples. Existing required dependencies are reused rather than installed;
only Python3.10.11 is locally evidenced. No3.11/3.12 local matrix pass is claimed.
Discovery is static, old deferred guards are absent, native module CLIs remain,
and legacy-nine compatibility is supported by prior baseline/core regressions.

No new public live proof is required for P5 local workflows; real SDK and durable
subprocess evidence satisfy its actual integration obligations. Prior public
receipts, unobserved commercial transitions/browser/LLM and Woo auxiliary-counter
limitation stay separately labelled. HEAD remains initial
`8081f9d8dc17c9b63aa30ecf0f8e295366f4eee2`, branch `cli-feature-parity`; no new
commit/push/PR is present, naming is neutral and `git diff --check` is clean.
Preexisting dirty work remains scoped by the saved initial baseline.

Verdict: **CHANGES REQUIRED for final completion solely because Final-01 remains
open.** Implementation, package, synthetic/stress, native integration and exact
case-coverage evidence are accepted within their stated limits. This verdict does
not silently waive the required CI-equivalent group check. Root owns parent
completion status, ticket updates and any further explicitly authorized decision.

## CI scheduling amendment — affected G1/G2/G3 review — 2026-10-25

Reviewer: `/root/cli_p5_delivery/p5_reviewer`, independent of author. Reviewed
ci-amendment.md SHA-256
`8840d9c374bac1b2b22858b4db579f20669ef54898a523d03e2329a4197fc903`;
tests/test_ci_driver.py
`c5e6df362428e8ac4d9622290ead4a4ce4ee4746a3610db35b7e8ac3cafe6392`;
evidence/ci-amendment-red.log
`1cae43b905b204cab4143cb35ff6e50b1da613e9a129d37b6a8742c73ae2c5a1`.

Stable file-family partition main/reliable-oracle/maintenance preserves all
assertions and default collection, avoids progress-index selection and includes
new driver tests in main. Saved timing basis supports a scheduling repair without
native optimization. Same per-group240/shared480 maximum, sequential operation,
reserved cleanup, strict narrower-only limits, existing optional-SDK checks and
fresh complete configured run meet the intended required-check repair. Declaration
interfaces are appropriately isolated from product code; stdlib process-group,
path/JSON/time/signal reuse has concrete local and CI consumers. Saved seven red
failures are missing driver/workflow behavior rather than dependency failure.

Affected G3 component design: PASS. Affected G1/G2: CHANGES REQUIRED for one
bounded test-design gap before implementation. CI-FR03 explicitly promises group
cleanup and SIGTERM143, but tests exercise only single sleeping leaders/SIGINT.
Predesign and add real TERM-ignoring descendant group cleanup, SIGTERM143, and
missing-executable spawn failure (safe failure report and no later group launch).
Also add promised negative cap rejection and exact-max/narrow-positive parse
acceptance. These target distinct child ownership, signal mapping, spawn-error and
numeric boundary risks; no timing cap increase or native test changes are needed.
Author notified; final completion finding Final-01 remains open pending a genuine
passing amended configured gate and final independent re-review.

### CI amendment affected G1/G2 re-review — 2026-10-25 — pass

Same independent reviewer. Revised ci-amendment.md SHA-256
`eba7c45a3793909770e9fb185dc4b829a83475ac48cbded5b0f86707f908f776`;
tests/test_ci_driver.py
`2cf29c1f2747bf4af9c560e7c1cdc38f7f11eedc6ad60e5b30405d3ae970227d`;
evidence/ci-amendment-red-expanded.log
`e30b68e218f9b607a2817cbcc60846e526c65571b9bff221a7b35f22877c1cf7`.

Missing lifecycle/boundary expectations now precede implementation and have
genuine executable red assertions: an actual spawned TERM-ignoring descendant
must disappear with its group; both external SIGINT/SIGTERM map130/143 and leave
an interrupted report; missing executable produces safe failed report and stops
later work; negative/max/narrow-positive caps are checked. Ten saved failures are
intended absent driver/workflow behavior. Typed interfaces/ownership remain the
reviewed scheduling-only design. Affected G1 and G2 PASS; prior affected G3 PASS
remains valid. Implementation/first-green and fresh configured full gate must
still execute. No native assertion, time ceiling or final completion waiver.

### CI amendment implementation / coverage review — 2026-10-25 — changes required

Independent reviewer unchanged. scripts/run_tests.py SHA-256
`ca2cc3d92de731dbaafeabb601def55a16631a79b76a3157d9b1f1e198378a2d`;
workflow SHA-256
`430763f2bc8faf770d25291bb4d33bf8c8bd6fbf5dc181db052a62c1659887ae`;
tests remain expanded-red revision above. Saved focused10PASS2.56s inspected.
Actual implementation preserves semantic file partitions, native assertions,
shared480/per-family240 ceilings, reserved cleanup, one process group at a time,
strict caps and optional-SDK checks. Existing wheel/product proof remains reusable
because scheduling source lies outside package/product code.

Blocking CI-Impl01: `_Interrupted` is caught only inside each active child's
inner try. Signals during report saving, between groups, or before the next inner
try escape the outer loop; outer finally restores handlers but neither marks an
interrupted report nor maps130/143. This violates the declared full-operation
interrupt contract even though active-child signal tests pass. Predesign and add
one deterministic boundary signal case using a real harmless completed child and
signal at the inter-group report boundary; assert interrupted final report,
130/143 and no later launch. Add outer handling while retaining active-group
cleanup. No native change or complete gate run is needed before this narrow repair.
Verdict: CHANGES REQUIRED before the fresh complete configured run.

### CI signal repair recheck — 2026-10-25 — one interval still open

Same independent reviewer. Driver SHA-256
`f4b84c55473306fb45cedee11a879c8a55ea53d93aa7c5575940a7e5a2293a99`;
test SHA-256 `140a6145d846b1f305a7fc28e284b3ce021c6cc972f98832a9c508d55abafc3c`;
amendment SHA-256 `33fbef07bdfd9bf97a40f20a3e3b24282f079ea068d85ac01803e289b5bd1ca0`.
13PASS3.04s focused result and1PASS0.30s conservative-probe result inspected.
Intent/checkpoint handling now protects Popen ownership and report/inter-group
boundaries. Bounded membership fallback on unavailable zero-signal probe is
conservative when ps is unavailable and preserves cleanup failure when members
remain; real group test mocks only that OS probe boundary.

CI-Impl01 remains open solely for cleanup interval: `_cleanup()` still installs
SIG_IGN, discarding user SIGINT/SIGTERM while cleanup runs. Intent-only handlers
can now safely latch these signals without interrupting cleanup. Author notified
to predesign/test actual signal at real cleanup TERM dispatch, retain intent
during cleanup and check it afterward. Timeout/success must not replace130/143
when user interrupted. No fresh full gate requested until this narrow regression
passes; no product or package finding added.

### CI amendment affected implementation / coverage — 2026-10-25 — pass

Independent reviewer unchanged. Driver SHA-256
`8c53f2a5aecd3d71b6fb04bd8615cef4d8e10dbe923718ef313217ad053d8dae`;
tests SHA-256 `b6da2548160a8534bc48990a43ba0d858c16309b3fa18a64c17990989cdc12e1`;
amendment SHA-256 `b382a42651ab3a14b7bcc9df15d3c5720f9cae5728a6124ae15f69eddb28e9c6`;
ci-scheduler-green.log SHA-256
`9bd666c9388037ec05b38b5140ed014c6e5b8c04034776ebc95af0843ff4a502`.

CI-Impl01 CLOSED: cleanup retains intent handlers, and outer post-cleanup
checkpoints convert actual SIGINT/SIGTERM into130/143 with persisted interrupted
report and no later group launch. Real harmless active process/TERM dispatch is
retained in the regression; only timing boundary injection is controlled.
Saved15PASS3.89s covers sequential/partition/limits/failure/spawn/descendant/
active/inter-group/cleanup signal and unavailable-probe behavior. Package-source
hashes independently rechecked against final manifest: zero mismatches; existing
wheel/product verification remains valid. No new native assertions or ceiling
changes. Affected implementation/coverage PASS to execute one fresh exact
configured full driver. Final-01 stays open until its actual all-family passing
result is independently inspected; old timeout remains historical evidence.

## Final whole-feature re-review — 2026-10-25 — FINAL PASS

Reviewer: `/root/cli_p5_delivery/p5_reviewer`, independent of author/coordinator.
This supersedes the completion-only CHANGES REQUIRED verdict above. All earlier
findings, repairs and original timeout evidence remain historical; none is
relabelled as an original pass.

### Reviewed revision and actual configured gate

Verified every entry in candidate final-source-digests.json (37 entries) and
final-review-inputs.json (26 entries) against actual bytes: zero mismatches.
All package Python source hashes also match the previously reviewed capability
manifest, preserving genuine wheel/product evidence. Snapshot digests below are
the candidate before this independent review entry and coordinator's subsequent
administrative T21/status update.

| Review input / evidence | SHA-256 |
| --- | --- |
| evidence/final-source-digests.json | 4f464c1bde59c7a4cc122bd7c292cc6f2288a3e965b42510107f030893dc218e |
| evidence/final-review-inputs.json | 236060b0137a2a1055159d374ad503c235d85b4ee3d145b678d449073493dbf1 |
| evidence/configured-ci/report.json | 044d2af62ad3acdcc470dc8e8030a94837f14ba2327ee7354bea44c866d3e28c |
| scripts/run_tests.py | 8c53f2a5aecd3d71b6fb04bd8615cef4d8e10dbe923718ef313217ad053d8dae |
| .github/workflows/test.yml | 430763f2bc8faf770d25291bb4d33bf8c8bd6fbf5dc181db052a62c1659887ae |

Final-01 CLOSED by an actual fresh configured invocation, not split saved-prefix
coverage or a waived check. Independently compared every planned/actual group
command to the reviewed driver's actual build_plan: exact equality. All three
groups exit0/pass with no surviving owned groups, within per-family240/shared480
ceilings including cleanup:

| Family | Actual passing tests | Driver seconds |
| --- | --- | --- |
| Main | 1465 | 187.612391 |
| Native reliable oracle | 24 | 121.997828 |
| Native maintenance | 106 | 109.903748 |

Total1595 fresh passing cases,419.517006 seconds. Actual individual logs and
driver receipt agree; no skipped/failed assertion count or progress-prefix
reuse. The reviewed stable family scheduling retains unchanged native assertions
and prior maximum shared execution ceiling. Independent compact verification is
evidence/reviewer-final-recheck.json; no new expensive suite or network run was
needed by the reviewer.

### Whole-feature disposition

Parent FR01–10/SC01–10 including suffix cases are traceable through the final
matrix and independently reviewed P0–P5 artifacts. Earlier accepted final
implementation/package/mechanism review remains applicable: actual grammar and
native API classifications, nine legacy defaults/module entrypoints, exact
typed/evidence file transport, native extraction/analysis/export/monitor/category
bindings, durable maintenance and restricted same-session tools, static discovery,
packaged schemas, error/resource/security boundaries, and installed offline
examples. No deferred production phase guard remains. The fresh complete gate
includes new scheduler tests, existing CLI regressions and underlying native
oracle/recovery assertions.

Genuine wheel proof remains valid for unchanged package bytes: external new venv,
cleared PYTHONPATH, verified site-packages import,85help entries/70leaves,
17schema files/24lookups, console/module parity and documented offline examples.
Actual SDK stdio and durable process integration, parent24 evidence reuse,
bounded P5 stress and restored mutation proof remain accepted as reviewed.

Parent tasks T01–T20 now link actual evidence and T21 correctly awaits this
independent verdict. Parent/P5 status, verification and traceability preserve
the original timeout, repaired configured gate and separate offline/live evidence.
No ticket closure/publication is claimed; coordinator may now administratively
complete T21/local status and update authorized tickets without product changes.
No commit/push/PR/labels/author/history changes were introduced; neutral branch
and saved initial dirty-work receipts remain. `git diff --check` clean.

Limits remain explicit rather than blockers: local Python3.10.11 only, no local
3.11/3.12 matrix claim; commercial transitions/browser/LLM live unobserved with
mechanism coverage separate; Woo auxiliary-counter limitation preserved; no new
public P5 requests/inference/model downloads; unavailable token counters without
quota estimates. Scope is local delivery, with publication separate.

Verdict: **FINAL PASS for P5 and whole-feature local delivery. No open blocking
findings.** Administrative handoff completion remains with the root coordinator;
material product/test/CI contract changes after this revision require affected
re-review.
