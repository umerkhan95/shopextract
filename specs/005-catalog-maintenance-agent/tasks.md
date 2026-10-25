# Dependency-ordered tasks

Behavior/test design authored first (spec.md, test-design.md, 2026-10-16).
Issue #25 is the epic; reviewed slices map to #55–58.
Each slice gets applicable gates/red/green evidence before merge; no unchecked epic
implementation. Author/reviewer agents ran sequentially. Local implementation,
verification and independent final review are complete; publication is separate.

| Task / slice | Owner / dependencies | FR / SC | Deliverable / completion evidence |
|---|---|---|---|
| [x] P1 behavior, edge inventory and task coverage | Author; none | FR01–12 / SC01–18 | spec.md + test-design.md before this file; category steering integrated |
| [x] P2 bounded code research and initial plan | Author; P1 | FR01–12 / SC01–18 | research.md + plan.md; no external broad research needed |
| [x] G1 independent behavior/tests/tasks/research review | Separate reviewer; P1,P2 | All | reviews.md digest/findings/verdict; resolve blockers |
| [x] S1 durable job/ledger skeleton + red tests | Author; G1 | 01,04–07,09 / SC04–08,11–14 | skeleton.md signatures/store schema, runnable acceptance failures saved |
| [x] G2 skeleton review | Reviewer; S1 | All | Actual signatures, migration/error/recovery/test seams reviewed |
| [x] C1 reusable component model | Author; G2 | All | components.md, compatible integration seams, revised skeleton |
| [x] G3 component review | Reviewer; C1 | All | No duplicated matcher/security/resolution; revised contracts approved |
| [x] A durable read-only workflow slice | Author; G3 + red | 01,04–07,09 / SC04–08,11–14 | SQLite jobs/steps/reservations/evidence; single runner; cancel/retry/resume; focused green checks |
| [x] B deterministic reconciliation/category/report slice | Author; A + relevant reds/gates | 02,08–12 / SC01–04,09–12,14–18 | Guarded native source adapter, physical request accounting, portable snapshot cache, trusted profiles, resolution, existing matching and evidence reports |
| [x] C optional investigator slice | Author; A,B + relevant reds/gates | 03,05,07,08 / SC02,03,05,08,11,13 | Injected advisory protocol, exact input/max-output/cost reservations, no default model calls/provider package |
| [x] D fixture/generator and mechanism evidence | Author; reviewed expectations before fixture code; A–C | All / SC01–18 | Controlled transport, spy advisor, crash fixtures; synthetic provenance, real mechanisms, critical mutation sensitivity |
| [x] E adversarial/offline verification | Verification author; D | All | 3-item smoke then bounded sequential stress; saved config/counts/RSS/repro + acceptance/affected regressions/full required checks |
| [x] E-review independent coverage review | Reviewer; E | All | Generator realism, distinct risks, mechanism traces, limit adherence and minimal failure review |
| [x] F bounded live example/docs | Author; E passing | 02,04,09,10 / SC01,02,04 | One source smoke then bounded expansion; actual unchanged result + resume; changed-spec observation separately inconclusive if unchanged; API/migration/limits docs |
| [x] Final independent review and delivery | Reviewer/coordinator; all applicable checks | All | Final diff, compatibility/evidence/docs and child issue mapping; no invented gates/live pass |

Each slice changes behavior only through updated spec/tests and affected gates.
Unobservable failure modes still require D/E; a live smoke cannot waive them.

Coordinator-created child tickets (metadata, no behavior change): A #55, B #56,
C #57, D–F #58. Exact issue bodies/mapping saved under
artifacts/catalog-maintenance-agent/issues/. All recorded gates passed; coverage.md
and verification.md map completed checks. The initial red subset is historical.
Final delivery here means verified local handoff; GitHub issues remain open pending
publication. Original whole-suite timeout and packaging/live limits remain explicit.
