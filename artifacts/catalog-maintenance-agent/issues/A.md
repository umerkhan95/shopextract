Parent: #25 — Catalog Maintenance Agent.

## Scope
Transactional local job/checkpoint/evidence persistence, exclusive runner ownership, restart/resume, cancellation, bounded retries, unknown-outcome reservation and cumulative physical-request/token/cost/deadline budgets.

## Traceability and dependencies
Slice A. FR01,04–07,09; SC04–08,11–14. Depends on none.

## Acceptance and workflow
Follow specs/005-catalog-maintenance-agent/ spec.md, test-design.md and tasks.md. G1 passed; implementation requires executable intended red acceptance evidence and independent G2/G3 reviews. Preserve full parent scope, existing public API compatibility, MIT/self-hostability and category-specific safety.

Completion requires mapped focused/regression and applicable mechanism/stress/live evidence plus independent review. No downstream writes, automatic paid provider calls or fabricated evidence.
