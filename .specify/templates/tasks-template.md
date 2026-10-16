# Dependency-ordered tasks

Use `[ ]` or `[x]` plus ticket, FR identifiers, deliverables and named checks.
Only mark tasks complete after their verification succeeds.

For each task include SC IDs, dependencies, owner role and completion evidence.
Behavior and test design must already exist before this breakdown.

- [ ] Task-breaker review of behavior/scenario coverage.
- [ ] Bounded production research and plan.
- [ ] G1 independent review: behavior, test design, tasks and research.
- [ ] Code skeleton and executable red acceptance tests with saved failure reason.
- [ ] G2 independent skeleton review.
- [ ] Reusable component model and skeleton refinement.
- [ ] G3 independent component review.
- [ ] Implementation tasks, each dependent on G3 and red test evidence.
- [ ] Offline acceptance and affected regression verification.
- [ ] Bounded live checks after offline success, or justified applicability status.
- [ ] Final independent review, docs and handoff.
