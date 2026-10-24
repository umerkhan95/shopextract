# Dependency-ordered tasks

Behavior/specification and test design were written first. User authorized implementation on 2026-10-24; ordered engineering gates still apply. Every completion needs saved evidence; W01 and W02 are complete, as recorded in reviews.md.

| Status / ticket | FR / SC | Deliverable, dependencies and owner | Named check / completion evidence |
| --- | --- | --- | --- |
| [x] W01 | All | Task-breaker checks traceability and distinct risk inventory; depends on spec/test design; separate reviewer | Matrix review including missing/null/zero/false, interactions and existing coverage gaps; `reviews.md` |
| [x] W02 | 01–08 / 01–11 | Resolve bounded research questions/constants and headerless coverage; author; depends W01 | Source/code audit and official-source decisions saved in research/plan; G1 pass in reviews.md |
| [x] W03 | All | G1 independent behavior/tests/tasks/research review; depends W02 | Artifact digest, findings, dispositions, verdict in `reviews.md` |
| [x] W04 | All | `skeleton.md`, typed acquisition/result seams and executable red tests; author; depends G1 | Named acceptance tests fail for intended missing behavior; saved red log |
| [x] W05 | All | G2 independent skeleton review; depends W04 | Interface/error/compatibility verdict in `reviews.md` |
| [x] W06 | All | `components.md`, reuse/ownership analysis and refined skeleton; author; depends G2 | Existing evidence/transport/mapping reuse justified; no hypothetical framework |
| [x] W07 | All | G3 independent component review; depends W06 | Digest, findings and verdict in `reviews.md` |
| [x] W08 | 01–06 / 01–08 | Implement bounded opt-in acquisition slice; author; depends G3 + saved red evidence | Tree acceptance tests green; evidence/budget/guard assertions |
| [ ] W09 | 07/08 / 09–11 | Optional exact Shopify mapping bridge and compatibility slice; author; depends W08; may ship later separately | Scoped/versioned mapping tests; no index-to-membership conversion; target-cap checks |
| [x] W10 | All | Synthetic factories, manifest and independent coverage review; author then reviewer sequentially; depends reviewed designs/interfaces | Seed, schema realism, expected outcomes and real entry points recorded |
| [x] W11 | Selected slice | Execute real-path mechanism/replay checks and bounded stress; verifier; depends W08 and W10, plus W09 only when bridge is included | Saved smoke then driver results/config/counts/minimal failures in `verification.md`; if acquisition ships first, explicitly defer bridge scenarios and report actual acquisition-case count, never claim all 24 cases passed |
| [x] W12 | All | Offline acceptance and affected extraction/feed/category/maintenance regressions; verifier; depends W11 | Commands and actual results in `verification.md` |
| [x] W13 | 01/02/04/06 | Bounded public live smoke, then optional expansion; verifier; depends W12 | Redacted capture and separate live status; blocked scenarios retain synthetic evidence |
| [x] W14 | All | Final independent review, documentation and handoff; reviewer; depends W12/13 | Reviewed diff/coverage/evidence, limitations and resume state; no invented pass |

W08 acquisition is independently useful. W09 cannot silently expand W08 into a complete classification service. Any new uncovered failure risk returns to behavior/test design and affected review before implementation.

For an acquisition-only delivery, W12–W14 review the selected acquisition FR/SC set and explicitly record W09/bridge coverage as deferred. The optional bridge must receive its own affected design/gate review and saved red/green evidence before later implementation; it is not approved by an acquisition-only pass.

Execution handoff 2026-10-24: W10 independent coverage passed; W11 stress24/24;
W12 focused77/general1018/maintenance106 passed (overlap, not unique sum); W13
actual live smoke passed one attempt/two root categories. W09 deferred; W14
independent final review pending. See verification.md for commands and limits.

W14 repair recheck: independent final reviewer found three local edge blockers;
affected design/red approved, repairs now pass combined130 focused/affected
cases and required parser stress24/24 rerun. W14 remains unchecked pending
independent final recheck. Existing unaffected broad/live evidence reused.

Independent W14 final repair recheck passed on 2026-10-24; reviewed source and
130-case affected green plus parser stress rerun recorded in reviews.md. W09
optional Shopify bridge remains deferred; it is not part of completed delivery.
