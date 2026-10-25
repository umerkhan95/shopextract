# Implementation plan

## Constitution check
Compatibility, meaningful verification, bounded usage, MIT/self-hostability.

## Architecture and decisions
Interfaces, ownership, versioning, limits and resolved alternatives.
Reference research.md, skeleton.md and components.md. Keep initial behavior
design separate from code skeleton and reusable-component design.

## Required gates
Record G1 (behavior/tests/tasks/research), G2 (skeleton), G3 (components) and final
independent review in reviews.md, with revision/digest, findings and verdict.
Implementation depends on G3 and saved executable red acceptance-test evidence.

## Verification and handoff
Named checks, saved results and dependent-ticket boundaries.
Define offline checks and a bounded live plan before implementation, including
assertions, requests/items, timeouts, retries and stop conditions. Save actual
results in verification.md and the resume point in status.md.
For unobservable live behavior, assign agents to reproducible fixture/generator
authoring, real-path mechanism checks, bounded stress and independent review.
Predesign expected outcomes and budgets; save seed/configuration and minimal
failures. Record mechanism/stress results separately from live observations and
reuse matching valid saved checks. Missing required coverage blocks completion.
