# Dependency-ordered tasks

Dependency roadmap, 2026-10-25. Full implementation is authorized; checkboxes
reflect completed task scope, and child phase artifacts record actual gates/
evidence. FR/SC identifiers refer to `spec.md` and `test-design.md`. Paths below
are relative to this feature directory. Coordinator assigns named agents in
`status.md`; author and independent reviewer must be different agents. Work is
sequential, one delegate/process at a time; reuse saved artifacts and evidence.

## Planning and G1

- [x] T01 — Task-breaker: check behavior/scenario coverage and public inventory (FR01–10; SC01–10 incl suffix cases). Depends: behavior/test design. Deliver: this breakdown plus explicit uncovered risks in `test-design.md`; check: every requirement/scenario has an owner and verification task. Evidence: coordinator records task-breaker findings/disposition in `status.md`.
- [x] T02 — Researcher: reconcile `coverage.md` with AST public callables, documented workflows, native signatures and existing tests (FR01/02/04–08/10; SC01/02/04–08b/10). Depends: T01. Deliver: `research.md`, revised command matrix and existing-coverage references. Check: bounded code/saved-evidence inspection; classify helpers explicitly; resolve command/config/codec/session questions before code. Evidence: revision, sources and unresolved limitations.
- [x] T03 — Fixture/test designer: refine distinct boundary/interaction cases and independent expected facts (FR03–09; SC03–09b). Depends: T02. Deliver: case IDs, existing-gap rationale, native schema-valid samples and planned synthetic transitions in `test-design.md`. Check: cases cover relevant below/at/above caps, money/missing values, partial/replay, expiry/recheck, persistence failure and interruption. Evidence: reviewed case manifest; no generator execution yet.
- [x] T04 — G1 independent reviewer: review behavior, tests, tasks and research (FR01–10; SC01–10 incl suffix cases). Depends: T02/T03. Deliver: findings/verdict with artifact revision/digests in `reviews.md`; coordinator updates `plan.md`. Check: traceability, unresolved decisions and adverse-case sufficiency. Evidence: pass only after blocking findings resolved; meaningful changes reopen affected gates.

## Skeleton, red acceptance and components

- [x] T05 — Skeleton/test author: define command interfaces, typed envelope/config shapes, module ownership, lifecycle and error seams in `skeleton.md`; add focused executable CLI/subprocess acceptance tests (FR01–10; SC01–10 incl suffix cases). Depends: G1 pass. Check: freeze implementation revision/dirty baseline, preserve legacy fixtures, save intended missing-command/flag/contract failures before each slice; dependency/import failures do not count as red. Evidence: bounded commands/logs and reasons in `verification.md`; stubs never fabricate success.
- [x] T06 — G2 independent reviewer: inspect skeleton and red tests (FR01–10; SC01–10 incl suffix cases). Depends: T05. Check: signatures match APIs, dependency direction, lazy extras, compatibility and tests exercise intended interfaces. Evidence: artifact digests, findings and resolved pass in `reviews.md`.
- [x] T07 — Component author: write `components.md` and refine skeleton (FR01–10; SC01–10 incl suffix cases). Depends: G2 pass. Deliver: reused native APIs/codecs/stores plus shared config, output and lifecycle responsibilities, concrete consumers and error contracts. Check: justify new shared abstractions; update changed tests/contracts through affected gates. Evidence: component-to-command mapping.
- [x] T08 — G3 independent reviewer: check cohesion, duplication, coupling, ownership and revised skeleton (FR01–10; SC01–10 incl suffix cases). Depends: T07. Evidence: reviewed digests/findings and resolved pass in `reviews.md` before any implementation slice.

## Bounded implementation slices

Every slice additionally depends on G3 pass and its saved executable red evidence;
complete only after focused green checks and affected legacy checks. API behavior
changes return to design and affected review gates. Keep each slice reviewable.

- [x] T09 — CLI author: additive command registration, shared explicit machine envelope/errors, config precedence, lazy extras and inventory audit (FR01–03/09/10; SC01–03/09/10). Depends: T08. Check: nine-command compatibility, complete 11-product output, stderr separation, native exact serialization, invalid config before side effects. Evidence: focused red/green and command manifest.
- [x] T10 — Extraction author: bind product/store/feed extraction and supported controls to native APIs (FR02/04/09; SC02/04/09). Depends: T09. Check: controlled transport/native parser facts, option fidelity, timeout/cancel and no implicit model download/paid inference. Evidence: focused acceptance and relevant extraction regressions.
- [x] T11 — Offline workflow author: matching/evaluation, compare/statistics/competition, validation/images/duplicates and existing exports (FR03/05/09; SC03/05/05b/09). Depends: T09. Check: ambiguity/currency semantics, evidence/category companions, stdin/output failures and missing engines through real code. Evidence: exact expected reports and real artifact/reimport checks where supported.
- [x] T12 — Monitoring/trust author: explicit DB/history/watch/change/recheck/replay, snapshots/evidence/bundles/retention and migration controls (FR03/06/09; SC03/06/06b/09/09b). Depends: T09/T10. Check: real SQLite transitions, stable event IDs, no refetch for evidence lookup, finite JSONL, dry-run nonmutation and explicit apply scope. Evidence: replay/restart/rollback and expiry interaction results.
- [x] T13 — Category author: native extraction/scopes, rules/registry mapping, validation/portable records, Woo tree, membership and local policy review (FR03/07/09; SC03/07/09). Depends: T09/T10/T11/T12. Check: all supported native platforms, foreign scope rejection, cycle/partial-tree behavior and retained policy digest using real mechanisms. Evidence: focused acceptance and category regressions.
- [x] T14 — Operations author: wrap maintenance module CLI, MCP stdio serve and bounded same-process tools-call lifecycle (FR02/03/08/09; SC02/03/08/08b/09). Depends: T09/T12/T13. Check: durable maintenance IDs across processes, resume/cancel/retry, protocol-only stdout, session-only tool handles, origin restrictions and runtime cleanup. Evidence: actual offline engine/SDK subprocess integration, actionable missing-extra results.
- [x] T15 — Documentation/package author: update command examples, file schemas, config precedence, migration notes and coverage manifest (FR01/02/10; SC01/02/10). Depends: T10–T14. Check: each supported public capability mapped; installed root/nested help and examples parse without activating optional runtimes. Evidence: disposable built-wheel smoke and documentation audit.

## Fixtures, verification and handoff

- [x] T16 — Fixture author: implement reviewed deterministic factories/controlled sources for unobservable cases (FR03–09; SC03–09b). Depends: T03/T08; before corresponding slice mechanism verification. Check: seed 11025, sanitized provenance, synthetic URLs/times and independently specified expectations; mock transport/clock/injected failures only. Evidence: fixture manifest and generator revision.
- [x] T17 — Independent coverage reviewer: inspect T16 realism, distinct risks/interactions, real-path exercise and stress configuration (FR03–09; SC03–09b). Depends: T16 plus corresponding CLI slices. Evidence: findings/resolution in `reviews.md`; review before stress execution, author cannot self-approve.
- [x] T18 — Mechanism/stress verifier: save one 11-product smoke, then sequential reviewed 24-case driver (FR03–09; SC03–09b). Depends: T10–T14/T17. Check: real CLI/API mechanisms; 6 input/serialization, 6 state/recovery, 6 category/tree, 6 resource/session cases; prove one critical assertion detects a temporary fault and restore it. Limits: 1 MiB and 100 products/case, 30s/case, 12min total, 512 MiB child RSS stop; BLAS 1, intra-op <=2, inter-op 1, no inference. Save each case; stop on unexpected failure, one diagnosed repair, then record blockers. Evidence: seed/config, counts, smallest failures and mechanism/stress sections in `verification.md`.
- [x] T19 — Offline verifier: run complete designed CLI acceptance and affected repository regressions/checks (FR01–10; SC01–10 incl suffix cases). Depends: T15/T18. Check: baseline compatibility, subprocess cleanup, install and inventory coverage; reuse still-applicable saved evidence. Evidence: commands/environment/revision and explicit passed/failed/blocked status in `verification.md`.
- [x] T20 — Live verifier: execute reviewed bounded live plan only after offline success (FR04/06–09; SC04/06–09b where applicable). Depends: T19 pass. Check: record exact previously authorized targets; one smoke <=2 items/5 requests/30s, save before expansion; total <=30 requests/12 items/5min, sequential/no retries; stop expansion after source failure. Browser/LLM require configured authorized dependencies and explicit cost cap. Evidence: actual observations separate from controlled/synthetic coverage; denied/unavailable/inconclusive remain so; docs-only planning live status is not applicable, runtime live requirements remain open.
- [x] T21 — Final independent reviewer and coordinator: review final diff, traceability, gates and evidence; update docs/status/handoff (FR01–10; SC01–10 incl suffix cases). Depends: T19/T20 dispositions. Check: missing mechanism/stress blocks completion; live limitations explicit; authors never approve own changes. Evidence: final artifact/revision review in `reviews.md`, completed/remaining scope in `status.md`, separate offline/mechanism/stress/live outcomes in `verification.md`. No commits, push or PR have been made for this local delivery.

## Actual completion evidence

T01–T08 and T16–T17: phase p0/…p5/ behavior/tests/research/tasks, genuine
acceptance-red logs, skeleton/components and independent G1/G2/G3/coverage
reviews. Parent planning review is historical; it did not approve implementation.
T09–T15: actual phase verification, shipped command grammar and
[p5/capability-manifest.json](p5/capability-manifest.json). The frozen public
inventory and new/helper surfaces are classified; no workflow binding is missing.
T18: reviewed parent24 mapping reuses20 applicable saved scenarios plus4 new
P5 resource/session scenarios; bounded real mechanisms and fault proofs are in
phase verification files. This is not24 newly generated independent cases.
T19: actual configured CI gate PASS from scratch,1,595 tests=1,465 main+24 oracle+
106 maintenance,419.517006 seconds under shared 480 and240 per group. Original main
command timeout remains historical evidence. Real built-wheel smoke PASS outside
checkout with installed import origins,85 help paths/70 executable commands,schemas/examples.
T20: bounded P1/P3/P4 public observations after corresponding offline passes;
global 3 HTTP requests / 6 items / 5.629 seconds. Price transitions and browser/LLM live execution
remain unobserved, with relevant synthetic mechanism coverage separately recorded.
P4 auxiliary transport-hook limitation and corrected offline proof are preserved.
No new public P5 request; actual SDK stdio and durable process checks are offline
integration. Scheduler-only changes do not invalidate those source observations.
T21 complete: independent FINAL PASS for P5 and whole-feature local delivery is recorded in p5/reviews.md; coordinator completed the administrative handoff.

See [p5/final-traceability.md](p5/final-traceability.md) and
[p5/evidence/configured-ci/report.json](p5/evidence/configured-ci/report.json).
