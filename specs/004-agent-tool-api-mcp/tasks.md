# Dependency-ordered tasks — #24

Behavior/test design was saved first. All tasks below remain unchecked except design authorship. Slice names are local child-ticket drafts, not created external tickets. Owners are roles assigned by coordinator; authors cannot approve their own artifacts. Every implementation slice depends on G1, G2, G3 and its recorded executable red checks.

| Draft slice / task | Dependency | FR / SC coverage | Owner | Deliverable and completion evidence |
| --- | --- | --- | --- | --- |
| A #49 — versioned contracts and bounded session runtime | Gates below | FR-02,04–07; SC-01,03,04,09,12 | Runtime author | Typed schemas/envelopes, handles, immutable results/cursors, bounded jobs; red then green contract/job/expiry/publication-race checks |
| B #50 — guarded source adapter and discovery/extraction tools | A | FR-01,03,07–10; SC-02,05,06,09,11 | Source author | Shared bounded egress with vetted-IP connection, native parser integration, retained capture/provenance; no browser/model fallback; denied-target, rebinding, timeout, partial/empty real-path checks |
| C #51 — matching, changes and authorized evidence tools | A,B | FR-03,05,11; SC-02,03,07,08,12 | Domain author | Existing matching/reliable-change/evidence reuse, configured capture bootstrap, owner-checked lookup; negative ownership/replay/partial/recheck tests |
| D #52 — real MCP stdio server and reference client | A,B,C | FR-01,02,04,06,08,10,12; SC-01,02,04,05,10,12 | MCP author | Optional dependency/entry point, advertised schema/permission parity, real SDK client subprocess complete flow, protocol-clean stdout/shutdown/cancel tests |
| E #53 — operating docs, verification and delivery | A–D | All FR / SC | Verification author + independent final reviewer | Runnable examples and errors, migration/limits/license, affected compatibility suite, bounded mechanism/stress/live receipts and final review |

- [x] Behavior and test-design authorship: spec.md/test-design.md; 12 scenarios, no gate claimed.
- [x] Task-breaker coverage check: verify every FR and each distinct scenario matrix risk has named executable checks and fixtures in these slices. Independent G1 reviewer validates mapping and practicality before proceeding.
- [x] Bounded production research: inspect existing code first, one SDK availability probe, primary official sources, resolve dependency/transport/native-parser alternatives. Save research.md and plan.md.
- [x] G1 independent review: behavior, tests, task mapping and research; save artifact digests/findings/verdict in reviews.md. Resolve blockers; child-ticket draft scope must remain full #24.
- [x] Skeleton author: skeleton.md declarations/interfaces and dependency seams for A–D, no fabricated implementations. Author executable failing acceptance checks first, including missing MCP integration and security/cancellation cases; save actual red commands/results in verification.md.
- [x] G2 independent skeleton review: check signatures, supported Python, connection pinning boundary, owner graph, lifecycle and testability against declared behaviors.
- [x] Component author: components.md explicitly maps native parsers/normalization, identity matching, reliable reports and evidence serialization to consumers; justify narrow new job/guard/cursor components; refine skeleton.
- [x] G3 independent component review: coupling/reuse, guarded seams, public compatibility, failure behavior; save digest/verdict.
- [x] Implement A sequentially; focused checks and saved red→green evidence.
- [x] Implement B sequentially; stop for design/review if security/format limitations materially change agreed contract.
- [x] Implement C sequentially; fixture author creates schema-valid deterministic real evidence/capture graph and declared matching/change outcomes before integration fixes.
- [x] Implement D sequentially; genuine SDK subprocess integration, no fake dispatcher-only reference client.
- [x] Fixture/generator author: seed 24 and fixed clock, controlled storefront/DNS/redirects, malformed cases, exact limits and publication faults per test-design.md; label synthetic/derived-offline provenance. Independent reviewer checks realistic fixtures, distinct risks and production path coverage before execution.
- [x] Verification author: save small complete-flow smoke before up to 48 case bounded mechanism/stress driver; exercise real parsing/normalization/identity/persistence/comparison/ownership/jobs/egress; only external boundary/clock/fault injected. Save limits/counts/minimal failures and critical negative-control assertion evidence. No inference, no parallel agents.
- [x] Offline checks: all planned acceptance risks, affected extraction/matching/monitoring compatibility, packaging/docs examples, then required full repository checks. Coordinator baseline model smoke: 26 passed with PYTHONPATH=src; reuse log, do not recount as feature proof.
- [x] Live checks after offline pass: documented real MCP client public discovery/extract/match/evidence flow plus saved-capture changes; <=16 requests/120s, first smoke saved, no source writes. Actual commercial change can remain inconclusive; missing rare behavior still requires mechanism/stress checks. Live access failures remain blocked/inconclusive.
- [x] E final review/handoff: separate reviewer checks final diff, FR/SC evidence and real MCP interoperability, docs/migration/limits/MIT. Update scope/status and issue mapping; no assumed pass. Child issues may be created by coordinator within authorized feature workflow before implementation; no external mutation performed by this author.

## Gate and verification rules

Any behavior change returns to spec/test design and affected reviews. Keep reviewable slice implementation commits separate where practical; no whole-epic unchecked task. Save actual status rather than planned success. A design case can group parameterized boundary values but must not hide a distinct uncovered invariant. Missing required coverage blocks completion; resource ceilings trigger a report/refinement, not automatic waiver. One diagnosed repair per blocker; reuse valid prior evidence. Unrelated working-tree artifacts stay untouched.

## G1 revision mapping (all checks planned)

- Slice A: FR-05–07/11, SC-03/07/09/12, R5/R6 — full graph and session byte reservation, conservative shared-capture accounting, owner invalidation and release; configured capture bytes included.
- Slice B: FR-06–10, SC-02/04/05/06/09/11/12, R1/R2 — killable owned DNS subprocess/late result denial, <=2s resolve/<=1s reap grace, no replacement on cleanup failure; <=1 auxiliary worker.
- Slice B: FR-07–09, SC-09/11, R3/R4 — identity encoding policy, predecode header rejection, bounded raw chunks and actual body/framing caps.
- Slice B/C integration: FR-03/08–09, SC-02/05/06, R7/R8 — normalized discovery eligibility, denied cross-origin diagnostics and mandatory extraction-time DNS revalidation.
- Independent G1 rereview must check these revised contracts and the eight-case substitution within unchanged 48-case budget. G2 must check concrete interfaces make each check executable before implementation. No current author disposition asserts reviewer pass.

Skeleton milestone: G1 independent pass recorded in reviews.md. Child issues #49–53 linked to #24 (coordinator receipt). skeleton.md plus explicit runtime/guard stubs and SDK scaffold saved; optional mcp1.30.0 installed/probed successfully. Eight intentional acceptance reds saved in verification.md. G2 pending, component design/G3 and all production implementation/green verification still unchecked.

G2 response milestone: G2-01–03 author dispositions in reviews.md, typed resource context declarations and strengthened real-evidence/optional-extra tests saved; eight revised intentional reds recorded. components.md authored, but G2 rereview and G3 verdict still pending. A#49/B#50 own shared context/worker/guard budget seam; C#51 owns existing foreign evidence graph test/lookup; D#52 owns extra-enabled MCP tests/optional-import compatibility; E#53 retains full verification requirement. No task becomes implemented merely from skeleton/components authorship.

Affected-review checkpoint: B#50 native Shopware existing read-only search POST needs exact reviewed route/body policy. Amendment and NS-01–03 cases saved before enabling. Review pending; current guard remains fail-closed for that POST. A#49 focused lifecycle3 passed; preliminary B/C domain smoke10 passed after one diagnosed class-import repair, saved logs. Native5-platform, broader egress/lifecycle/owner coverage, D/E, full regressions and independent fixture/stress/live/final gates remain incomplete. No issue is closed or production-complete based on this smoke.

Implementation checkpoint: real native5 smoke passed, real MCP complete flow passed, focused20 and affected187 passed; detailed evidence in verification.md. A–D implementation and E docs/reference client exist locally, but all child completion checkboxes remain pending full verification/final review. Exactly48 concrete cases/29 new mechanism functions and resumable bounded driver prepared. Independent coverage/fixture gate is next; no stress/public live/full repository run yet. Full repository ceiling180s must be enforced after gate. No source capability silently omitted; server source-mode restrictions are explicit and Shopware amendment independently approved.

MC review repair ready: exact48 case mappings and outside-run obligations, surgical actual-branch negative controls, real partial-replay/TTL/publication interactions, full dependency/resume identity, measured fixture ledger and14,490,163-byte preflight bound. No stress execution. CI #52/#53 now requires dev,mcp across Python3.10–3.12 with separate optional-import compatibility. Actual process probe peak5 includes both trackers; amended limit needs affected review. Branch tool-api-mcp-server; no issue closed. Resume only after independent corrected gate.

Final MC04 driver-only repair saved: resource overflow becomes persisted failed_resource before save, legacy overflow resume blocked, and final success includes zero resource history. Four pure state regressions passed0.06s; no mechanism run. Await independent narrow MC04 rereview; all48-case budgets/digests preserved.

F02 author implementation checkpoint: reviewed eight scenarios now included in current813-pass ordinary suite; distinct owned-work completion correction passed unchanged B05/B06 within remaining focused budget. Async callers/docs/CI updated. Independent final rereview required; no epic/child close, commit or push. Historical stress/public-live limitations unchanged. Exact change list/hashes f02-repair.json.

Delivery author verification complete: NEW current-revision48/48 approved mechanisms passed within180s/15s/fixture/RSS/process bounds; historical failures preserved separately. Public native DATA flow and actual partial-capture changes proof saved. Exact delivery allowlist/evidence ready coordinator staging/commit/push/PR/current CI/merge and ticket updates under user authorization. No author git mutation.

Delivery checkpoint: all implementation and local verification tasks have evidence in verification.md/reviews.md, including 48/48 current-code mechanism cases and the actual live MCP flow. The clean PR tree must pass the Python 3.10–3.12 CI matrix before merge; PR and ticket delivery state is recorded on GitHub.
