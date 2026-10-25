# P4 tasks

1. Author native signature/contract research, behavior/test design. G1 independent reviewer.
2. Author typed skeleton and executable all-family red. G2 reviewer.
3. Concrete existing component reuse model. G3 reviewer.
4. Implement CLI category adapters, catalog ingestion/export companions; C1-C12 focused checks.
5. Reviewer coverage gate; execute saved smoke then bounded sequential stress/fault proof.
6. Affected native/CLI regressions, declared read-only live smoke; docs and coverage actual status.
7. Independent final review, resolve blockers and handoff exact outcomes to parent.

Traceability/dependencies: tasks1-3 cover all F1-F6/SC07/05b/09/10 and precede production4. Task2 red executes F1 extract/normalize,F2 map/validate/record,F3 fetch/link/load/export,F4 inspect/review,F5 companion export. Task4 implements these plus F6 bounds. Task5 coverage C1-C12 with G1 additions C8a/C9a/b/C10a is prerequisite to stress. Task6 live verifies F3 actual availability separately; affected offline regressions protect SC02/05b/06b. Task7 final checks all F1-F6 and parent coverage without claiming P5 completion.

Final actual disposition: tasks1-3 COMPLETE (G1/G2/G3 and affected refinements PASS),
task4 COMPLETE (native implementations plus reviewed crossphase companions),
task5 COMPLETE (coverage PASS,12stressgroups74executions,mutation detected/restored),
task6 COMPLETE (678affectedPASS, one declaredlive with explicit counterlimitation,
docs/coverage updated),task7 COMPLETE (independent final PASS, reviews.md).
Parent owns remote tickets/parent tasks/status and P5 integrated verification.
