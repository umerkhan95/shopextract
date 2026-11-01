# Dependency-ordered tasks

Written after spec/test design. Owner: author `/root/audit_research`; independent
reviewer `/root/audit_plan_review`; sequential agents only. Coverage SC01a/b,
SC02a/b,SC03a/b,SC13a maps every child FR; existing controls named in test-design.

- [x] TO01 FR01/02/08 — behavior/test design and distinct risk inventory; spec.md,
  test-design.md created before this breakdown. Source research below complete.
- [ ] TO02 G1 — reviewer assesses behavior/tests/research/tasks/plan; resolve findings.
- [x] TO03 afterG1 — author skeleton.md, minimal interfaces and acceptance tests;
  record red failures for intended defects. Evidence skeleton.md,tests/test_truthful_outcomes.py,
  verification.md and saved red logs. No production business logic yet.
- [ ] TO04 G2 — reviewer checks API/tool compatibility, HTTP/error paths and tests.
- [ ] TO05 afterG2 — author components.md; reuse existing outcomes/normalizers/
  extraction data/CLI envelope/tool diagnostics; separate reviewer G3.
- [ ] TO06 afterG3 — production author implements one bounded task: shared assessment
  and projections SC01a/b, browser/product admission SC02a/b, Woo404 SC03a/b.
- [ ] TO07 fixture/executor author — deterministic41-case maximum plan, saved smoke
  before expansion, real mechanism probes and minimal failures; reviewer validates
  fixture realism, independent expectations and existing coverage reuse.
- [ ] TO08 verification author — focused regressions and full repository driver;
  record offline commands/results. Then predeclared bounded live plan, separately
  labelled blocked/inconclusive where needed; no simulated live pass.
- [ ] TO09 final reviewer — diff, actual coverage, full-driver/live evidence,
  remaining limits; update status/reviews/verification and umbrella task mapping.

G2 follow-up: SC01c/SC03c added after reviewed coverage findings, source-backed
feed/Woo seams and exact five-case expectations designed before tests. Actual
acceptance count46, focused intended-red evidence red-g2-seams.log/json. Reviewer
must re-assess G1 affected coverage additions and G2; no gate preapproved.

G2 PASS prerequisite satisfied. TO05 component-model author portion complete:
components.md records concrete reuse, private helper consumers, lifecycle/error
contracts. Separate G3 review remains pending; implementation not started.

Implementation TO06 complete against child contracts;46 acceptance/10 status cases
observed green. TO08 REQUIRED FULL REPOSITORY GATE BLOCKED on240s main-family
ceiling; reliable-oracle/maintenance unrun,4 failure nodes unknown. Live not
attempted pending offline gate. TO09 independent final review pending; child not
complete. See verification.md and full-suite/report.json; no further sweep.
