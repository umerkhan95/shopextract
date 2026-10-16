# Dependency-ordered tasks — issue #23

Behavior/test design preceded this breakdown. Child slices linked below; no production work before all gates.

| State | Task / owner | Dependencies | FR / SC coverage | Deliverable and completion evidence |
| --- | --- | --- | --- | --- |
| [x] | T01 behavior author + task breaker coverage audit | none | FR01–09 / SC01–18 | spec.md, test-design.md; all requirements mapped, live boundaries explicit |
| [x] | T02 bounded researcher | T01 | FR01–09 / SC01–18 | research.md and plan.md; inspected existing code only, no network |
| [x] | T03 independent G1 reviewer | T02 | all | reviews.md artifact digests, blocking findings resolved |
| [x] | T04 skeleton author | T03 | all | skeleton.md API/schema/error contracts; executable tests/test_reliable_changes.py with saved intended failures in verification.md and red.log |
| [x] | T05 independent G2 reviewer | T04 | all | reviews.md skeleton verdict; production logic absent |
| [x] | T06 component author | T05 | all | components.md reuse/boundaries, refine skeleton without behavior implementation |
| [x] | T07 independent G3 reviewer | T06 | all | reviews.md component verdict; affected changed contracts reviewed |
| [x] | T08 implementer: [#45](https://github.com/umerkhan95/shopextract/issues/45), report and field contracts | T07 + red tests + child issue linked | FR01–04,08–09 / SC01–07,12,17–18 | explicit API/types; selected evidence extraction; identity-aligned fields; additive connection-owned snapshot load; focused green tests |
| [x] | T09 implementer: [#46](https://github.com/umerkhan95/shopextract/issues/46), health and explicit rechecks | T08 + child issue linked | FR05–06,08 / SC07–14 | scope/completeness diagnostics; pending suspicious candidates/removals; third-snapshot decisions; focused green tests |
| [x] | T10 implementer: [#47](https://github.com/umerkhan95/shopextract/issues/47), durable replay and integration | T09 + child issue linked | FR07–09 / SC15–18 | atomic ledger, stable IDs/new_events; reopen/race/rollback tests; public opt-in exports/docs |
| [x] | T11 verifier, offline | T10 | all | designed acceptance + monitor/completeness/identity/evidence/portable regressions + repository checks; verification.md and bounded logs |
| [x] | T12 verifier, live | T11 green | SC01,05,08,15,17 | predeclared <=3 public requests; actual saved smoke, honest inconclusive/blocked commercial-change status |
| [x] | T13 independent final reviewer + coordinator | T12 | all | final diff/evidence review, resolved findings, issue mapping and handoff |

Use one delegate at a time. Child A/B/C are implementation slices of the same
agreed contracts; none can be called feature-complete independently of dependent
verification. No broad platform sweep, automatic monitoring or unrelated refactor.
