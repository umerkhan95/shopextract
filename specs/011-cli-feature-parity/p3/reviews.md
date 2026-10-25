# P3 independent reviews

## G1 — 2026-10-25
Reviewer: p3_reviewer (separate sequential reviewer; no author edits).
Verdict: **changes required**. No implementation approval implied.

Reviewed SHA-256 revisions:

| Artifact | SHA-256 |
| --- | --- |
| spec.md | 20d09c913a45b5ae7b01fc15f89bb7231e21edf563403fce6442876051e2eb23 |
| test-design.md | b0caada8971863ba8bc65dbd06bb788d1335bd71a508b9a9786156c6ed1582d2 |
| tasks.md | d6d31792c195ea298831a8053fa17691aeda2a146a2ea5ca0c6fb6f9817471d0 |
| research.md | d0c72e82b0b4f713b9587c29a494507c0bb7392a9d5222ff8251c55681f0cd71 |
| plan.md | d0e9bd0920452672c9a52c7999d0324d87e5f0dd05810b2aa25a6bc3fc78ef9b |

Read AGENTS.md, development-workflow.md, constitution, parent spec/test-design/coverage; inspected native watch/snapshot/changes/evidence/reliable/resolution/bundle and shared CLI data/core seams. No network, inference, agents or runtime tests used at this design gate. Actual token counters unavailable.

### Blocking findings

1. **G1-01 / P1 — Exact executable expectations and local traceability are incomplete.** T1–T7 are useful risk summaries, but do not state concrete input/expected-output matrices sufficient to distinguish success from a plausible wrong implementation. In particular the metadata/policy version key and null/omitted semantics, watch change/terminal data shape and termination counts, reliable confirm/revert/expiry states and replay publication counts, and bundle byte/record/depth boundary behavior need predeclared expectations. Add stable P3 FR/SC IDs (or an explicit mapping from P3-1..6 and T1..7 to parent FR/SC), explicit exit/output/state expectations, and concrete cases at below/at/above applicable limits. Define a small distinct interaction set with risks and outcomes (for example partial coverage + replay and expired evidence + recheck), not only broad labels. Disposition: open; author design revision required before implementation.

2. **G1-02 / P1 — Reliable scope rejection contradicts the proposed native reuse.** P3-3 says foreign supplier/scope/order is rejected; T3 promises rejection before ledger writes, but native reliable_changes checks mismatched previous/current scopes in _compare by returning status=suppressed and subsequently persists reliable_reports. Only a supplied recheck currently enforces matching scopes before comparison. Research must explicitly choose and document CLI read-only scope preflight, or amend the behavior to native suppression/persistence with a justified compatibility decision. Add a concrete mismatched-scope case without recheck and assert selected outcome plus ledger/schema invariants. Do not assume the existing native transaction alone fulfills the stated rejection contract. Disposition: open.

3. **G1-03 / P1 — Network cap units and retained/live bounds are ambiguous.** Native snapshot(max_urls=N) forwards an extraction URL budget; native watch currently has no product cap. T7 says maxproducts and the live plan requires retained<=2, whereas research proposes only forwarding max_urls. A Shopify response can contain multiple products per URL. State whether --max is a URL/request budget, product retention cap, or both, and design a transport fixture returning more products than the URL budget to prove the chosen contract. Also predeclare the exact bounded live command/path and assertion semantics for products exceeding the cap; a post-hoc truncation must not silently imply complete coverage. Disposition: open.

### Nonblocking observations

- The additive read-only/exact modes, in-memory backup for prune dry-run, native typed codec reuse and transaction ownership are appropriate directions. Preserve native default APIs and test file bytes/schema before/after both successful and failed read invocations.
- Deadline around the whole async consumer covers initial and unchanged watch work; tests should exercise cancellation while initial extraction is blocked and while iteration is unchanged, including generator close and absence of later writes.
- The overall stress budget is bounded. The execution evidence should identify actual selected test groups, child RSS enforcement, stop/repair outcomes and byte-identical mutant restoration. The stated live extraction->save/load path must remain labelled separately from a CLI snapshot live observation.

Re-review the revised affected artifacts before G2. D2 may begin only after G1 blockers close.

## G1 re-review — 2026-10-25
Reviewer: p3_reviewer, same independent sequential reviewer.
Verdict: **PASS** for behavior/test/task/research gate; implementation and execution evidence remain future gates.

Reviewed revised SHA-256 digests: spec.md `b24c1a547680b76bc9126ac96d7931f0a5791d40f0aa1577697128827aed721a`; test-design.md `d6cd475d1eab459f7796964df2ff19a26d3d64a74c6ee4bf188bf28245fb1ef0`; research.md `9b1b74e9224e2ed3a175837972f419bb85fb5ab8ed5e4ccada6cd4bec18cbc64`. tasks.md and plan.md unchanged from first review.

- G1-01 closed: normative exact matrix now maps local requirements/checks to parent FR/SC, gives envelope/exit shapes, closed schemas, reliable state/publication outcomes, distinct partial+replay/expiry+recheck interactions, and concrete byte/count/depth boundaries. Fixtures must still meet native validity requirements; boundary acceptance does not bypass native record validation.
- G1-02 closed: CLI explicitly selects read-only known-scope/supplier/order preflight, with mismatched known scope without recheck expected to fail before ledger creation and preserve database bytes. Native Python suppression remains unchanged.
- G1-03 closed: both URL budget and retained-product cap now explicit for new CLI modes; optional native retention parameter preserves legacy defaults. Oversized adapter fixture requires two retained products plus incomplete metadata. Live path is explicit extraction followed by persistence and CLI retrieval, not a CLI snapshot live claim.

Implementation review must check the above exact contracts, generator cleanup on deadline/cancellation, staged-file publication and legacy default compatibility. No further G1 blockers. Author may proceed to skeleton/red/G2.

## G2 — 2026-10-25
Reviewer: p3_reviewer (independent sequential reviewer).
Verdict: **PASS** for document-only skeleton and initial red gate.

Digests: skeleton.md `5adeca288f6998d80616bba7de1ee63dccff96868caa75e86173e86668aee1f4`; tests/test_cli_monitor.py `a4e19dffd2516ee0587e49deaef6b9585e9149fc5488a9fc0ebd6e99f398b896`; evidence/acceptance-red.log `e673bdc146b5e5f762969fdec4dad28f03309f71eb5e8cb977b7819960ef0b08`.

The proposed additive keyword signatures preserve current defaults; the read-only opener is below domain readers, native persistence/compare/resolution own business behavior, and CLI registration/encoding are separate from native mechanisms. Preflight can reject supplier/identity/schema prerequisites before writes. Ephemeral prune preview can reuse the native algorithm without a source-file mutation. The retained-product limit is optional on the native Python APIs and explicit in new CLI modes. Error paths distinguish invalid input from missing migration/schema prerequisites. No runtime stub fabricates success.

Inspected executable tests and saved red result: both fail with E_USAGE/unknown command, at missing snapshot-save and resolve invocations. The failures are for the intended absent behavior, not broken fixture imports or environment errors. The tests subsequently exercise real persistence/portable Decimal and absent-contract resolution once implemented. These two initial checks establish the red gate only; they do not establish complete T1–T7 acceptance coverage. Remaining designed checks must be authored before their corresponding implementation tasks and reviewed at coverage/final gates.

No G2 blockers. G3 must identify concrete reuse/ownership, particularly native connection/preflight lifecycle, staged artifact validation, and serializer field ownership. No runtime execution repeated because the saved red evidence is sufficient at this gate.

## G2 expanded-family review — 2026-10-25
Reviewer: p3_reviewer.
Verdict: **PASS for binding/discoverability red only; changes required if the requested all-family gate requires runtime behavioral acceptance red**. The earlier skeleton approval stands; broader behavioral approval is not inferred.

Digests: tests/test_cli_monitor.py `77d981dae25ade2f4339d5580a5fe9850293f30cf54f2513af62bc7d846e1676`; evidence/acceptance-red-all-families.log `ef9c6685649de0ff0abb7b2edab297a561e30f1994e7022eb5e1b5031ac80022`; skeleton.md unchanged `5adeca288f6998d80616bba7de1ee63dccff96868caa75e86173e86668aee1f4`.

Saved output contains 11 failures for missing commands/options, with no fixture/import failures. Nine added cases invoke --help and assert usage. These are legitimate discoverability assertions and safely avoid network work, but Click help bypasses command callbacks; an implementation registering no-op leaves would pass them. Their missing DB/input placeholders cannot establish history exactness, watch bounded execution, reliable ledger behavior, prune immutability, evidence lookup, bundle/sidecar fidelity or migration semantics. Only snapshot roundtrip and absent-contract resolution currently assert runtime behavior. Under a requirement for all-family runtime red, add valid native fixtures and one distinct observable behavior assertion per remaining family, save failure evidence, then re-review before production. Do not report 11 behavioral acceptance failures.

## G3 — 2026-10-25
Reviewer: p3_reviewer.
Verdict: **PASS** for reusable component model. This does not waive the G2 runtime-red qualification above.

Digest: components.md `ac3f6e0d357b05ba3b4f7c9aeda17d4d9d885544ab73b1dd23dcce2bfa865152`.

Concrete consumers and ownership are identified: shared bounded/portable CLI transport; bootstrap/error/envelope reuse; native monitor comparison/storage/resolution; additive read-only seams; one prune algorithm over an isolated connection; native staged bundle validation; shared P2/P3 sidecar semantics. The custom watch consumer has a justified present need for JSONL/deadline/close handling. No speculative framework or business-algorithm duplication is proposed. Native connection lifecycle and explicit Evidence field serialization are adequately assigned for implementation review. No G3 blockers.

## G2 runtime-family follow-up — 2026-10-25
Reviewer: p3_reviewer.
Verdict: **changes required for unconditional all-family runtime red**. G3 remains **PASS**, components digest unchanged.

Digests: tests/test_cli_monitor.py `3e3ddf73e31ee499a4afe680ff4d99c27ed918742de2a58400c1c6aecbcea470`; evidence/acceptance-red-runtime-families.log `0bbb4908aa84802458334cee53b523c49c2fecef6081e89c3bcf558662547903`.

Valid native fixture setup now supports genuine missing-behavior red for exact history, reliable/replay, scoped evidence get, bundle create, and explicit migration apply, in addition to snapshot save/load and resolve. Saved result is 16 failed/1 passed. The invalid watch test passes for unknown-command E_USAGE, so is explicitly not validation proof.

Remaining blocker: test_evidence_get_prune_readonly_red exits at missing evidence get before prune is invoked; test_bundle_sidecar_runtime_red exits at bundle create before any sidecar invocation. Split these into independently executable fixture-backed tests so prune and sidecar have actual runtime red. Explicit bounded snapshot still has help-only red, and finite watch has no runtime positive-behavior test. Author states finite watch runtime will precede watch implementation; retain that as a blocking prerequisite, not completed evidence. Add snapshot transport-bound fixture/runtime assertion and finite watch external-boundary fixture/runtime assertion before their production tasks. Independent tests must reach the relevant command during the red run, rather than relying on later assertions behind an earlier failure. No G3 contract change was found.

## G2 all-family runtime-red closure — 2026-10-25
Reviewer: p3_reviewer.
Verdict: **PASS**. Prior all-family red blocker closed. G3 remains **PASS**, component/skeleton contracts unchanged.

Digests: tests/test_cli_monitor.py `3e8b6c52c5795979d910349272d91e0b119d28e3861492430f9d6ca06d2a96e8`; evidence/acceptance-red-runtime-families.log `a505ec2677af3ce0ee8ef72d5812763fb08c7deb27d84eaa5faa9f21e34d767d`.

Inspected independent prune, sidecar, explicit snapshot and finite unchanged watch tests plus updated saved run. Each now reaches its own CLI command without a preceding missing-family assertion: prune expects protected native preview plus identical bytes; sidecar loads a native-created artifact; explicit snapshot supplies an oversized extraction boundary response and expects retained count/incomplete metadata; watch replaces only extraction and expects the real native generator to time out with a zero-event terminal envelope. Saved red is 20 failed/1 passed in 0.64 seconds, all intended missing registration/options. The one invalid-watch E_USAGE pass remains explicitly non-proof until implemented validation tests run. Tests do not stub persistence, native watch, comparator or bundle mechanisms.

These checks establish meaningful initial runtime acceptance red across the families; they do not replace the full designed edge/adversarial T1–T7 suite or final coverage review. No further G2 blockers; production tasks may proceed within reviewed contracts.

## Watch amendment — affected G1/G2/G3 — 2026-10-25
Reviewer: p3_reviewer, independent sequential review before amended production code.
Verdicts: **G1 PASS; G2 PASS; G3 PASS** for the amended watch contracts. Runtime coverage/final approval remains pending.

Digests: spec.md `dc00c0c32fdb89f94191b6de47b45e35822b3a89bb87ead5c90cedfad7ab363a`; test-design.md `cb60997e3d458a2636e049e0cc5812b376ee18610dc997a86dda3a5ff0a8bff1`; skeleton.md `449d8cc76d5f88ac72d28d54799d1511b17179c11c7776da136e970f1d61a33b`; components.md `c988b8a46395e5aa1b8002f2b542a527eb872d3f17217e3ed229b99e05e09582`; tests/test_cli_monitor.py `8e912fa4fe149c1859dda0cdbb5773ed578f2278bd4736b5928d5256cc8bb5c0`; evidence/watch-amendment-red.log `70142eca3f63526d3b0b3d234a0923193f80f69218817c4c789ff63e9d48e343`.

G1: Explicit verification=unverified_scalar_comparison on every watch event honestly describes classic scalar comparator diagnostics. The event key can remain event when this mandatory label and documentation prohibit confirmed/captured-fact claims. Partial, truncated, failed or default scalar observations must never be promoted to confirmed factual changes; the reliable command retains that role. The initialized field correctly distinguishes lack of a persisted baseline from a successfully persisted initial capture; E_OPERATION distinguishes source exception from timeout. Amendment predesigns initial-block cancellation/no DB, initial source exception, partial/truncated diagnostic events and unchanged/changed terminal behavior.

G2: Two saved executable failures are genuine: initialized is missing after blocked initial extraction and verification is missing from an actual native classic partial-source price event. Tests replace only extraction, exercising real watch/snapshot/persistence/comparison/deadline paths. Red run: 2 failed, 21 deselected, 0.33 seconds. The new callback signature is additive and typed; mark initialized only after native snapshot returns successfully. This means persisted baseline, not verified catalog completeness. Existing unchanged-watch exact terminal assertion must be updated to include initialized=true as a direct reviewed contract change, and then executed green. Source-exception and truncated-source cases still need execution evidence at coverage review.

G3: Single native lifecycle notification avoids duplicated persistence/scheduling logic; CLI owns terminal state and explicit diagnostic serialization. No arbitrary callback loading is exposed. No component blocker or need to rename the event key.

## Source-result/alias refinement and pre-stress coverage review — 2026-10-25
Reviewer: p3_reviewer.
Affected gate verdicts: **G1 PASS; G2 PASS; G3 PASS** for the refinement. **Coverage approval for stress: changes required** pending the known repairs and distinct gaps below.

Reviewed digests: spec.md `b52d7b866d710d89a18450f475b3f521ce84e97af1fdc4a1f6f1a17e97705921`; test-design.md `c11e096a426858dae745714393c031164676ae1a61ed49c04611ee5f49f56820`; tests/test_cli_monitor_mechanisms.py `04347ff53fb90f128399e11efe0db4c30d728fa1bd5717a3e4ea71cdbc8e6100`; src/shopextract/_cli_monitor.py `b826fab7f91f1cb23c2d5b83a12839455efe6b2023adbff74f5e2416acc00eda`. Inspected mechanisms-green.log (61 passed/1.29s), adverse-red.log (2 failed/1 passed), CLI adapter and native reader/snapshot seams. Saved prior green does not include the new failing cases.

The refinement properly distinguishes empty errored capture from a valid empty catalog: strict retained-limit mode raises E_OPERATION before persistence, without altering legacy default snapshot behavior. Nonempty errored captures must become incomplete with source_errors even when the extractor incorrectly claims completeness. Alias rejection belongs in one concrete artifact preflight shared by bundle/sidecar create/load. New red tests actually reveal empty-failed baseline and destructive same-path publication, not mock failures. Interfaces/component ownership remain valid; native snapshot owns source-result handling and CLI owns artifact alias checks.

Required repairs and distinct coverage before stress:

1. **Known reds:** execute the two new failure regressions green after one focused repair. Add nonempty errors+catalog_complete=true case: persist incomplete/source_errors and label any resulting watch diagnostic unverified. Existing exception/zero-products/oversize cases do not cover erroneous completeness accompanying retained data.
2. **Alias identity:** execute symlink and existing-hardlink aliases, including sidecar output aliasing its payload and load output aliasing artifact input. Expect E_USAGE and all original input/payload bytes unchanged. The single same-path bundle-create case misses both secondary input and filesystem identity aliases.
3. **Cancellation:** execute SIGINT/KeyboardInterrupt during native watch work, expecting exit130, exactly the declared cancellation envelope, generator/transport finalization and no subsequent writes. Timeout tests do not establish signal behavior.
4. **Lookup semantics:** exercise valid snapshot with missing evidence and owner without contract, expecting explicit missing/unsupported statuses and no file mutation/transport. Current scoped available/expired tests do not exercise these branches. Because CLI requires full owner scope, native duplicate-ID ambiguity can be covered by existing native tests rather than weakening that CLI requirement.
5. **Malformed artifacts/publication:** execute bad bundle/sidecar versions and truncated JSON with preexisting destination; expect E_USAGE and preserved destination. Existing tampered payload tests exercise digest rejection, not envelope/parser failures.
6. **Reader lifecycle:** existing_db and identity migrate use sqlite3.Connection as a context manager, which commits/rolls back but does not close the connection. Close deterministically on success/error and verify with a real SQLite Connection subclass or close-tracking opener; do not mock SQL/algorithm behavior. This matters for repeated in-process invocations and clean local file lifecycle.
7. **Serialization boundaries/error contract:** a near-1MiB valid portable input can expand when wrapped as a native bundle/sidecar; declare and test whether creation rejects output beyond the CLI reload bound before publication, avoiding creation of an artifact its paired load command rejects. Also exercise one corrupt stored JSON/graph input and ensure E_OPERATION as specified; the broad native ValueError->E_USAGE mapping currently risks classifying storage corruption as user input.

Already useful coverage: suspicious confirm/revert/replay, partial+replay removal suppression, wrong scope/supplier/order/missing IDs with byte preservation, snapshot/reliable transaction faults and restart, prune expiry->load->bundle->recheck, legacy migration prerequisite, resolution cutoff/future/conflict/variant paths, exact shared input byte/count/depth edges, atomic rename failure, changed/unchanged/initial-block/partial/truncated watch. Reuse these saved cases; do not inflate stress by repeating seeds. Add the above cases to test design with risks/outcomes before implementation. Stress approval awaits repaired green evidence and focused coverage recheck; no live claim yet.

## Coverage repair re-review — 2026-10-25
Reviewer: p3_reviewer.
Affected gates: **G1 PASS; G2 PASS; G3 PASS** for source-result, aliases, lifecycle, integrity-error and artifact output-cap clarifications.
Mechanism coverage: **PASS** for the previously requested distinct gaps under the saved 77-test bounded run. **Stress execution approval: changes required** for process-tree limits below. No live verification yet.

Digests: spec.md `e92092f05100c80a99f1029b86353df798f011d49578bb759c54e279da876811`; test-design.md `53618971dbf6a6665b0e49adcba4cabe1eb063bc53beee2e417d60764d21dbbe`; _cli_monitor.py `c9827bdc5131f0441832ba8222f9dbdb5653920347e025eb64de903bd49cae95`; monitor/snapshot.py `e282ca9cf10d9a9872dd1368ee880a97a377d0f1db21ba540124f23b5b235768`; test_cli_monitor_mechanisms.py `a692d488e14ff3d01acbee3f6c524b716dc6fe688fa936a9eabe30798b0acc91`; cli_monitor_stress_driver.py `9490361b533ec0ce70572a41db8e835addc65d7f3fd794a43a3085afebd1de2a`.

Inspected saved coverage-repair-green.log: 77 passed/7.96s. New real-path cases cover nonempty errored completeness, symlink/hardlink projection aliases, missing/unsupported lookup and corrupt retained payload, malformed envelopes/truncated JSON with preserved output, deterministic four SQLite closes, native bundle wrapping growth and real subprocess SIGINT130 with transport-finally marker. Source guards share concrete helpers and retain native algorithms. Closing wraps both preflight and migration lifecycle; strict failed-source behavior remains opt-in. Stored=True error classification is appropriate for persisted reads. Artifact output guard rejects expansion before staging/publication under the declared CLI bound. The prior seven requested mechanism gaps are closed by code+cases+saved passing evidence.

Reviewer attempted a small focused rerun using environment python and three selected cases; no output appeared within the initial tool yield and the process remained running. Terminated reviewer-owned PID56831, without modifying source. This attempt is **unverified**, not another pass; reuse author's saved 77-pass evidence. No model/network call was launched.

Remaining stress-driver blocker: driver samples only pytest PID RSS, while the SIGINT case creates an additional Python child, and resource termination kills only pytest PID. Therefore the claimed child RSS cap and cleanup do not cover the actual process tree. Start groups in separate process groups/sessions, measure descendant-inclusive RSS (or enforce an equivalent explicit child bound), and terminate the entire group on limit/failure/finally. Save cleanup/no-orphan outcome with group status. Twelve distinct selections, 30s group/300s total, fixed seed, sequential execution and status persistence are otherwise appropriate. No need to repeat the full 77-test run after a driver-only repair; review driver then execute declared stress once.

## Stress-driver bounds closure — 2026-10-25
Reviewer: p3_reviewer.
Verdict: **PASS — bounded stress execution approved**. No stress result or live result is implied.

Driver SHA-256 `3386945ddf9a830ed9831c881a1f950b8ff976e2e8fbad2b0b58ab0bdded88d6`.

Verified isolated start_new_session per sequential pytest group; RSS sums current process-group members, covering the controlled SIGINT child; limit/finally cleanup kills the entire isolated process group; post-cleanup inventory saves remaining members and fails if any remain. Existing 12 selections, per-group/total deadlines, thread/worker caps and saved status remain. The controlled tests do not detach children from this group. The previous process-tree blocker is closed. Execute once and retain actual group counts, peak RSS, durations and cleanup results. Stop on failure under the declared one-repair policy.

## Final review — initial disposition — 2026-10-25
Reviewer: p3_reviewer.
Verdict: **changes required** for one bounded-resource blocker; prior completed mechanism/stress/live evidence remains reusable.

Reviewed P3 native monitor diffs, CLI registration/adapter/error seams, verification/status, docs grammar, saved stress status/mutation/live receipt and live driver. Saved affected suite: 503 passed/24.48s; bounded stress: 12 groups/76 executions/40.417s, maximum group RSS198564KiB and zero orphans; exact-float mutant detected/restored byte-identically; live receipt one GET200/two retained products/1.148s and no lookup HTTP. Live evidence honestly proves explicit Shopify extraction->native persistence->CLI retrieval, not fresh CLI snapshot or observed commercial-price transition. Read-only/exact native defaults remain additive; diagnostic watch labeling and baseline state match reviewed decisions. History annotation/doc-only follow-up does not require replaying all unaffected tests. Parent whole-repo/clean-wheel work remains P5, not claimed complete here.

**F1 / P1 — unbounded prune preview backup.** New read_only_preview calls source.backup into memory for the entire SQLite database before bounded prune selection. batch_size limits candidate records but does not bound database copy size or duration; a long-running catalog can exhaust memory despite the passing small fixtures. Current stress bounds establish exercised fixture limits only, not safety for arbitrary existing database size. The author independently flagged this same issue.

Required design-first repair: explicit default preview cap (proposed64MiB logical database) and5s backup deadline; preflight logical SQLite page count/size, then enforce backup progress total/time to handle concurrent/WAL growth or busy backup. Reject before full allocation when oversize, close source/copy on every failure path, return actionable E_OPERATION, and preserve original bytes/schema. Keep native default behavior unchanged outside opt-in readonly preview. Predesign deterministic real SQLite below/at/above a reduced injectable test budget plus controlled-clock timeout and failure cleanup; clock/fault injection is permitted, backup/retention mechanism must stay real. Save red before repair, then focused CLI/native evidence checks and updated docs/evidence. No further merchant request or repeated broad stress run is needed for this focused change. Final PASS awaits this repair and focused verification.

Documentation cleanup for final handoff: verification.md retains earlier 'Actual outcome pending' prose before completed sections; reconcile to current final state so readers do not need to resolve contradictory status. This is nonblocking editorial cleanup.

## F1 design/red affected gates — 2026-10-25
Reviewer: p3_reviewer.
Verdicts: **G1 PASS; G2 PASS; G3 PASS** for the proposed preview-resource repair. Final F1 remains open until implementation and focused green evidence.

Digests: spec.md `9f2655a5940a4800545e195a3fc1f7ac4c167da3159105d4b520557f2cbc40e2`; test-design.md `1b2a9d632390ca1a3a3984629b5dc05568aaa23d3ba25d2375f756b583a4bdb4`; test_cli_monitor_mechanisms.py `62a251bb9b9ce120b854051da2715b947afd087ffe2c820b5f2863af02e0e6a5`.

Real SQLite fixture tests at measured logical size-1/size/size+1 and real backup with clock injection establish genuine pre-repair red: 2 failed/2 passed/0.42s, no import/fixture error. Oversize test requires no backup call; all cases require byte-identical source and balanced real connection closes. Callback seam/typed PreviewLimitError allow native-owned backup limits with safe CLI E_OPERATION reason; no duplicated retention algorithm. Proposed 256-page progress batches bound responsiveness, with actual total-page and clock checks needed during backup. Preflight should occur before memory-copy allocation; error handling must cover schema preparation as well as copy. Native legacy dry_run/apply behavior remains unchanged. The described reported-total growth boundary should be executed before closing F1; only the race report may be injected, real SQLite backup must still run. Author may implement the reviewed focused repair.

## F1 implementation closure / artifact pipeline amendment — 2026-10-25
Reviewer: p3_reviewer.
F1 verdict: **CLOSED / PASS**. Artifact pipeline affected **G1 PASS; G2 PASS; G3 PASS**, implementation/final green pending.

Digests: monitor/evidence.py `4b662287d2c5aa255a822229f85ba439b12679928139baa5cc758c8fcd792a0b`; spec.md `dc26931d0b2ccc3bb8d1bf988b4946071519222b97e1b5d4d2a0c50a4a54c6b7`; test-design.md `cdd015791c522c9491ea46f40357af0f2a47c0bff745113cd5118c4df3df5462`; test_cli_monitor_mechanisms.py `2a0ad667783e80ae611453865d7ef3dd0ddb96c07291d8deb132b3f1d814e77e`.

F1 source now preflights SQLite logical pages before memory allocation, bounds real backup progress to64MiB and5s with256-page increments, uses safe PreviewLimitError size/deadline reasons, and closes both connections on copy failure plus schema-preparation failure. Legacy native modes unchanged. Inspected real growth-progress seam and cleanup tests, and saved f1-final-affected.log:305 passed/19.87s. The originally unbounded preview blocker is resolved within stated copy limits. Existing live/stress evidence remains applicable; no repetition required.

The artifact amendment correctly fixes two distinct final portability risks: output files from bundle/sidecar load should be native portable arrays reusable by existing consumers, while stdout retains data.products envelope; decoded bundle input must not be reread from a mutable original path after bounded validation. Native read/write file APIs remain exercised on owned staged creation. Two pre-repair executable failures in file-pipeline-red.log (2 failed/0.52s) use real native bundle/sidecar inputs, exact price and downstream snapshot-save/load assertions; the file-read boundary alone rejects a second original-input read. Expected outcomes are independent of implementation. Shared product-publication helper is appropriate, preserving atomic output/alias/byte-limit ownership. Author may implement; final PASS requires focused green pipeline checks and affected CLI/native export regressions.

## Final closure — 2026-10-25
Reviewer: p3_reviewer, independent sequential reviewer.
Verdict: **FINAL PASS for P3**. No remaining implementation blockers identified in the reviewed slice.

Final reviewed source digests:

| Artifact | SHA-256 |
| --- | --- |
| src/shopextract/_cli_monitor.py | 4c74b212be1923978c85b46784ccb3b75a399d2ce731afe32dae9b9f7e98dd8e |
| src/shopextract/monitor/changes.py | cafdc1636d7f352acc803cbf1875a1e21d87644c653b35e7154f9da0b4756bd9 |
| src/shopextract/monitor/evidence.py | 4b662287d2c5aa255a822229f85ba439b12679928139baa5cc758c8fcd792a0b |
| src/shopextract/monitor/snapshot.py | e282ca9cf10d9a9872dd1368ee880a97a377d0f1db21ba540124f23b5b235768 |
| src/shopextract/monitor/watch.py | 4441d495fa7ffa84ee8731453935ffe6e91ef4d7316b99caa60b335bd1ee72b7 |
| tests/test_cli_monitor.py | 4015449a3ee32f9d1513eb286109bb151ac71a887533adf3d61210f2b0401139 |
| tests/test_cli_monitor_mechanisms.py | 2a0ad667783e80ae611453865d7ef3dd0ddb96c07291d8deb132b3f1d814e77e |
| docs/cli.md | 07eeec825d0bb6639a59fa8ac449c162d575e41b6d987a60415857c469772688 |
| p3/capability-manifest.json | 72ea0dfc680c73d0c4ba100b2b5eab472eff465a360ec1f18ab4d4d70a6dcba4 |

Inspected final portable_output helper and both load consumers: destination files are native portable arrays, stdout preserves data.products, artifact aliases/byte bounds and atomic publication remain shared, and bundle input is decoded once without reopening the original. Native staged bundle creation still exercises file read/write validation. The two real downstream file-pipeline assertions now participate in saved final-511-affected.log: **511 passed,73 existing warnings,24.55s**. F1 resource and cleanup tests remain included; earlier F1 CLOSED/PASS stands. No further live/stress expansion was required for these isolated repairs.

Final conclusions: additive native read-only/exact contracts preserve legacy defaults; reliable native transactions/replay remain authoritative; watch emits explicitly unverified scalar diagnostics and honest initialized/timeout/cancellation state; artifact files preserve typed data and reusable pipelines; retention preview is read-safe and bounded. Synthetic/adversarial mechanism coverage and declared stress limits are independently reviewed. Actual live integration is precisely limited to one GET/two products through explicit Shopify extraction, temporary native persistence, CLI load/get, and no lookup HTTP. Source-price transitions remain unobserved live, with synthetic mechanism evidence reported separately. Parent full-repository/clean-wheel integration remains P5.

Author may mark P3 D7 complete. Nonblocking handoff cleanup: replace stale pending/unbounded-preview sentences in status.md/verification.md with final state rather than leaving superseded claims beside later appendices. This editorial reconciliation does not change reviewed behavior or invalidate gates. No commits/push/PR/labels performed by reviewer; actual token counters unavailable, no quota estimate.
