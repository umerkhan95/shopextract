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
   proceeding. Identify behaviors unlikely to occur during a live sample and
   predesign synthetic mechanism/stress cases as described below. Require relevant
   edge cases and distinct tests for uncovered failure modes, not inflated counts.
   Record
   unresolved product decisions explicitly.
2. **Task breakdown.** Task-breaker agent writes `tasks.md`: small deliverables,
   dependencies, FR/SC coverage, owner role, checks and completion evidence.
   Schedule executable failing acceptance tests before production code. Include
   research, skeleton, reusable-component and review tasks as dependencies.
   Assign fixture/generator authoring, adversarial stress execution and independent
   coverage review explicitly; unobserved live behavior still needs mechanism tests.
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
    environment, results and requirement coverage in `verification.md`. Execute
    the reviewed synthetic mechanism and bounded stress plan against real code.
11. **Live verification.** After offline checks pass, execute the predesigned
    bounded live plan with explicit domains/endpoints, requests/items, timeout,
    retries, resources and stop conditions. Begin with one smoke case; save it
    before expanding. Use a sequential driver; use read-only operations unless
    writes are authorized. Compare observations to the predeclared assertions.
    A mock/replay is offline evidence. Missing access or nondeterministic state
    is recorded as blocked/inconclusive, never passed. If the expected transition
    does not occur, agents must execute or reuse passing, still-applicable
    synthetic mechanism/stress checks; an inconclusive live sample alone is not
    sufficient verification. Capture a regression
    fixture for live failures, fix it, rerun affected offline checks, then retry
    the failed live case within its budget. Docs-only slices can be marked live
    not applicable with a reason; feature live requirements cannot be waived
    just because offline tests pass.
12. **Final review and handoff.** Independent reviewer checks final diff,
    behavior coverage, offline/live evidence and remaining limitations. Resolve
    blocking findings. Complete only when required gates and checks pass;
    otherwise report the exact incomplete work. Update docs and issue mapping.

## Required synthetic mechanism and stress coverage

When a live source is unchanged, a rare failure cannot be induced safely, access
is unavailable, or a target transition is otherwise unobservable, agents must
construct and run the missing scenarios. This is an automatic part of authorized
feature verification; it does not require another permission request or an
external model service. Do not merely report that the behavior was not observed.

- **Design first.** Map each unobserved FR/SC to exact inputs, state transitions,
  expected outputs and invariants before writing its generator or repair. Derive
  expectations from the agreed contract, not the implementation's output. Include
  realistic schema-valid cases plus explicitly labelled malformed inputs.
- **Generate reproducibly.** Use existing schemas and sanitized saved samples
  where available. Prefer small deterministic factories and fixed seeds over
  large generated corpora. Record provenance as synthetic or derived-offline;
  simulated source URLs/timestamps must never be presented as actual captures.
- **Exercise the real mechanism.** Run through production parsing, normalization,
  persistence, comparison, recheck and publication paths relevant to the scenario.
  Mock only unavailable external boundaries, clocks or deliberately injected
  failures. Do not stub the algorithm under test, return expected reports from
  a fake, or test a duplicate implementation. Where transport matters, use a
  controlled local server or transport fixture; label it controlled, not live.
- **Challenge invariants.** Select relevant transitions such as normal/suspicious
  changes, revert/supersede, missing vs absent, conflicting/expired evidence,
  partial/failed sources, duplicate/reordered inputs, replay/restart, rollback,
  currency/type boundaries, and exact budget edges. Exercise contention only
  where relevant, using a fixed small worker count within resource limits.
  Use fault injection or a narrowly scoped temporary broken implementation when
  appropriate to prove critical assertions detect the intended failure; never
  ship that breakage or weaken the assertions to pass.
- **Design edge cases and distinct tests.** Inspect existing coverage before adding
  cases. For each new scenario name the uncovered risk, why existing checks miss
  it, and the exact expected outcome. Include relevant just-below/at/just-above
  boundaries; missing/null/empty/zero/false distinctions; malformed or escaped
  identifiers; and feature interactions such as partial data plus replay, expiry
  during recheck, or failure during persistence. Consider ordering, contention and
  recovery when the feature depends on them. Use a small pairwise selection or
  invariant-based generator when it covers a real interaction gap. Distinct tests
  must target different failure modes or contract interactions; renamed copies,
  arbitrary random values and multiple seeds alone are not unique coverage.
  Reviewers challenge trivial assertions and identify missing adverse cases.
- **Bound and execute.** Save one small smoke result before stress expansion.
  Declare case/iteration counts, seed, input-byte/memory limits, timeout, worker
  cap and stop conditions before running. Use one sequential driver with saved
  progress; no unbounded fuzzing, broad sweeps or parallel model launches. Stop
  on a failure, save the smallest reproducible case, diagnose one repair, then
  rerun the affected checks within budget or record the blocker. Reuse valid
  completed checks rather than regenerate them every time live data is unchanged.
- **Review and report.** A separate reviewer checks generator realism, independent
  expected outcomes, real-path execution, distinct edge/interaction coverage and
  stress limits.
  Save seeds/configuration, commands, counts, outcomes and minimal failures in
  `verification.md`, with traceability in `test-design.md` and `tasks.md`.
  Report mechanism correctness, stress results and actual live observations
  separately. A synthetic pass proves the exercised mechanism under stated
  conditions; live commercial-change coverage can remain inconclusive. Synthetic
  checks do not waive an explicitly required real integration check or prove
  unlimited scale, production load capacity or real-world change frequency.

Missing required mechanism/stress coverage blocks verification completion even
when a live smoke passes. New gaps discovered during live testing return to test
design before adding a generator or fixing production code. Existing valid
coverage may satisfy the gap if its scenario and limits match; cite the saved run.

## Agent operation and saved progress

The primary agent coordinates; delegate task breaking, research, skeleton/component
design, synthetic fixture generation, adversarial mechanism/stress verification,
implementation and independent reviews as bounded assignments. One
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

## Complete repository check command

Run `python scripts/run_tests.py` in the configured development environment. CI
uses this same driver. It runs every test sequentially in three stable file
families: ordinary tests, the native `test_reliable_changes_stress.py` oracle,
and the seven maintenance files. No assertions or test cases are skipped. Each
family has a 240-second ceiling and all three share a 480-second ceiling,
including reserved cleanup time; these preserve the prior two-group maximum.
The driver terminates/reaps owned process groups on timeout, failure or interrupt
and stops before launching another group. Its JSON report and per-family logs
are saved in the printed output directory; `--output-dir PATH` selects one.
Limits can be narrowed, never increased. Use the full configured driver for final
gate evidence; partial saved coverage is diagnostic evidence, not a passing gate.
