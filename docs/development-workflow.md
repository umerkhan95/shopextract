# Feature development workflow

This repository uses its local Spec Kit structure: constitution, specification,
plan and dependency-ordered tasks. No installed `spec-kit-dev` skill or CLI is
assumed. Apply this workflow to each reviewable feature slice, including child
issues under an epic. Do not implement a whole epic as one unchecked task.

## Ordered stages and gates

1. **Behavior design and test design.** Write `spec.md` and `test-design.md`
   first. Give requirements FR IDs and scenarios SC IDs. Describe observable
   inputs, outputs, state transitions, invariants, failure behavior, compatibility
   and non-goals. This is the behavior skeleton, before code architecture.
   For each scenario define fixture, exact expected outcome, negative/boundary
   cases and offline/live verification. Expected results come from requirements,
   not the eventual implementation. Task breaker checks scenario coverage before
   proceeding. Record unresolved product decisions explicitly.
2. **Task breakdown.** Task-breaker agent writes `tasks.md`: small deliverables,
   dependencies, FR/SC coverage, owner role, checks and completion evidence.
   Schedule executable failing acceptance tests before production code. Include
   research, skeleton, reusable-component and review tasks as dependencies.
3. **Production research.** Researcher first inspects existing code and saved
   evidence. Write `research.md` with bounded questions, alternatives, decisions,
   compatibility, failure/recovery, resource limits and source dates. Consult
   primary external sources when a decision needs current external facts. Start
   with one small saved probe if needed; do not launch broad sweeps. Resolve
   material questions or document a blocking limitation before implementation.
4. **Review G1: behavior, tests, tasks and research.** A separate reviewer checks
   traceability, correctness, scope, missing adverse cases and production risks.
   Update `plan.md` with decisions. Resolve blocking findings before advancing.
5. **Code skeleton.** Author defines interfaces, typed data shapes, module
   ownership and integration seams in `skeleton.md`; add minimal code stubs only
   where useful. Executable acceptance tests must demonstrably fail for the
   intended missing behavior before its implementation. Stubs must fail clearly,
   never return fabricated success. Document declarations can avoid exposing
   incomplete public runtime APIs. Save the red result and failure reason.
6. **Review G2: skeleton.** Separate reviewer checks signatures, dependency
   direction, compatibility, error paths and whether designed tests can exercise
   the interfaces. Skeleton code has no business implementation.
7. **Reusable component model.** Write `components.md`: existing components to
   reuse, shared responsibilities, consumers, boundaries, lifecycle and error
   contracts. Refine the skeleton accordingly. Prefer existing abstractions;
   justify each new shared component with concrete consumers or a stable contract.
   Avoid a framework for hypothetical future use.
8. **Review G3: components.** Separate reviewer checks cohesion, duplication,
   ownership, coupling and revised skeleton against the agreed behavior/tests.
9. **Implementation.** Implement one bounded task at a time against the agreed
   contracts and failing tests. Run focused checks while developing. Requirement
   changes return to behavior/test design and affected reviews. Do not rewrite
   assertions merely to match unexpected output.
10. **Offline verification.** Run designed acceptance checks and affected
    regressions, then required repository checks. Cover failure, replay,
    compatibility and resource boundaries where applicable. Save commands,
    environment, results and requirement coverage in `verification.md`.
11. **Live verification.** After offline checks pass, execute the predesigned
    bounded live plan with explicit domains/endpoints, requests/items, timeout,
    retries, resources and stop conditions. Begin with one smoke case; save it
    before expanding. Use a sequential driver; use read-only operations unless
    writes are authorized. Compare observations to the predeclared assertions.
    A mock/replay is offline evidence. Missing access or nondeterministic state
    is recorded as blocked/inconclusive, never passed. Capture a regression
    fixture for live failures, fix it, rerun affected offline checks, then retry
    the failed live case within its budget. Docs-only slices can be marked live
    not applicable with a reason; feature live requirements cannot be waived
    just because offline tests pass.
12. **Final review and handoff.** Independent reviewer checks final diff,
    behavior coverage, offline/live evidence and remaining limitations. Resolve
    blocking findings. Complete only when required gates and checks pass;
    otherwise report the exact incomplete work. Update docs and issue mapping.

## Agent operation and saved progress

The primary agent coordinates; delegate task breaking, research, skeleton/component
design, implementation and independent reviews as bounded assignments. One
delegate at a time by default; reuse agents where useful. Authors cannot approve
their own deliverables. A reviewer can review several stages but must receive
the actual artifacts, changed contracts and prior findings at each gate.
Do not spawn an agent per tiny edit or repeat completed investigation.

Use `status.md` as the resume point: current stage, scope, agent ownership,
completed artifacts, next action, blockers, resource limits and usage milestones.
Use `reviews.md` for G1/G2/G3/final: reviewer, reviewed revision or artifact
digest, findings, severity, disposition and verdict (pass/changes required).
A meaningful artifact change invalidates affected downstream gates; review those
changes again. Never invent a reviewer verdict or treat a pending review as pass.
Review gates do not add user approval requirements.

Use `verification.md` for actual red/green results, compact summaries and saved log
paths. Planned, failed, passed, blocked and not applicable are distinct states.
Test design is mandatory before implementation; extra tests discovered later
supplement it. Keep credentials out of captured evidence. Keep logs and samples
bounded and follow the repository's artifact retention conventions.

## Feature artifact checklist

Create `specs/<number>-<feature>/` with `spec.md`, `test-design.md`, `tasks.md`,
`research.md`, `plan.md`, `skeleton.md`, `components.md`, `reviews.md`, `status.md`
and `verification.md` as their stages are reached. Do not fill future verdicts
with assumed success. Existing completed specs stay historical; apply this flow
to new slices and material follow-up changes.
