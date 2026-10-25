## Outcome
Build catalog maintenance agent for the open-source Product Truth Engine and Catalog Maintenance Agent.

## Phase
Agentic MVP: evidence-backed reports only

## Scope
- [ ] Goal-based supplier reconciliation workflow with explicit investigation steps and uncertain-result review.
- [ ] Persistent jobs, checkpoints, restart/resume, cancellation and bounded retries.
- [ ] Crawl/token/cost/deadline budgets, caching and evidence-backed correction reports; no downstream writes.

## Acceptance criteria
- [ ] A fixture workflow finds an outdated specification and produces a before/after correction with evidence.
- [ ] Restarting resumes a checkpoint without repeating completed external work.
- [ ] Budget exhaustion stops safely with partial results; unresolved facts are not invented.

## Dependencies
#21, #22, #23, #24

## Planning estimate
5–8 focused engineering days for one engineer, assisted by AI, after dependencies are ready. This is a preliminary estimate, not a delivery commitment; external integrations, evaluation results and deployment requirements may change it. Break this epic into reviewable child issues before implementation.

## Definition of done
- [ ] Acceptance criteria demonstrated with meaningful automated checks and an end-to-end example.
- [ ] Public APIs, migration notes and operating limitations documented.
- [ ] Existing extraction/comparison/monitoring compatibility checked where affected.
- [ ] Core implementation, tools and workflows remain MIT open-source and self-hostable; no paid feature gate.

## Boundaries
Do not expand this epic into the other roadmap workstreams. Managed hosting/support may be offered separately. Do not mark the epic complete solely because a demo or MCP wrapper exists.


## Reviewed implementation breakdown

Behavior and acceptance design: `specs/005-catalog-maintenance-agent/`. Independent G1 passed; skeleton/G2/components/G3 and implementation verification remain pending. Category-specific hardware/footwear policies; LLM optional and disabled by default, deterministic cases require zero LLM calls.

- [ ] #55 — Durable catalog maintenance jobs and cumulative budgets
- [ ] #56 — Category-aware catalog reconciliation and evidence reports
- [ ] #57 — Optional bounded investigation for ambiguous catalog cases
- [ ] #58 — Catalog maintenance mechanism verification and operating examples
