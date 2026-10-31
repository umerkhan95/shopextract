# Dependency-ordered tasks

Coverage review (task-breaker, 2026-10-31): FR1–FR4 map to SC1–SC6 with separate failure mechanisms. Production contracts require explicit shape validation, support preservation after image filtering/reindexing, and bounded index application; include these in G1 and implementation tests. No missing requirement identified; additions below clarify adverse cases rather than change scope.

| Task | Owner | Depends | Coverage | Check/evidence |
| --- | --- | --- | --- | --- |
| T1 Behavior/test design | author | — | FR1–4, SC1–6 | spec.md, test-design.md |
| T2 Research and breakdown | task-breaker | T1 | all | research.md, tasks.md; saved sitemap count |
| T3 G1 design review | independent reviewer | T2 | all | reviews.md, plan.md; resolve blockers |
| T4 Skeleton contracts | author | T3 | all | skeleton.md; explicit parser/index/carrier/CLI signatures |
| T5 G2 skeleton review | independent reviewer | T4 | all | reviews.md; shape/scope/provenance checks |
| T6 Reusable component model | author | T5 | all | components.md; reuse capture/normalization/mapping/CLI limits |
| T7 G3 component review | independent reviewer | T6 | all | reviews.md |
| T8 Executable acceptance fixtures and red checks | author | T7 | SC1–6 | focused pytest log before production changes; exercise real mechanisms |
| T9 DOM and image fix | author | T8 | FR1, SC1–2 | focused tests incl. image shape/reindexing and browser result |
| T10 Magento/fallback detection | author | T8 | FR2, SC3 | blocked API transport, negative prose case |
| T11 Bounded listing index and observation | author | T8 | FR3, SC4–5 | scoped URL/card parsing, partial acquisition, retained evidence, shape validation |
| T12 CLI integration | author | T11 | FR4, SC6 | XML/JSON URLs -> artifact -> normalize -> exact rule mapping |
| T13 Offline verification/stress | author | T9–12 | all | focused green plus full scripts/run_tests.py; bounded deterministic stress |
| T14 Bounded live verification | author | T13 | SC1, SC4 | respect enforced allowlist; record blocked if Naheed denied, never synthetic-as-live |
| T15 Independent final coverage/diff review | reviewer | T13–14 | all | actual revision and logs; address blockers |
| T16 Handoff | author | T15 | all | status.md, verification.md; live limitations and commands |

Sequential execution; no simultaneous delegates. Stress fixture generator and execution owned by author and independently reviewed at final gate. All changed tests have an explicit risk and predetermined expected outcome in test-design.md. Default command behavior and no-op absent-index path are regression coverage.

## Completion evidence
T1–T12 implemented and reviewed G1/G2/G3; initial red.log, adversarial-red.log and stream-red.log retain intended failures and fixes. T13 passed focused115 and complete revised driver1734 tests (final-check/report.json), including deterministic100-card/three-page/page-budget mechanism and controlled drip-stream deadline checks. T14 live blocked by enforced allowlist, recorded in verification.md; no757-category crawl claimed. T15 independent final code/coverage/evidence review passed after deadline/type repairs; revised complete driver report and all three logs inspected. T16 docs and status updated; ready for handoff with live integration explicitly blocked.
