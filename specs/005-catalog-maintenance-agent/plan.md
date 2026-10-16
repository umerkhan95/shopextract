# Implementation plan — initial author draft

## Constitution check

Opt-in MIT/self-hostable workflow; no paid dependency. Preserve extraction, Product/
Variant, identity, monitoring, feed and #24 tool contracts. Evidence supports facts;
uncertainty remains explicit. Behavior/tests precede tasks and implementation.
Sequential author/reviewer gates; bounded work and saved evidence mandatory.

## Architecture and decisions

See research.md for inspected seams. A small maintenance package owns durable
job/step/budget/evidence/report storage, deterministic orchestration and trusted
category profiles. Reuse ToolRuntime native guarded source execution, portable
records, match_products, resolution and evidence contracts. Extend a transport
accounting seam only as necessary to reserve physical requests for a parent job;
existing callers retain defaults. Persist request and optional advisor attempts
before dispatch. Checkpoint result+evidence+usage atomically; unknown attempts stay
charged and require explicit retry. Cache exact policy/profile/version captures;
never persist ephemeral capability handles as durable results.

Initial profiles hardware-v1, footwear-v1, explicit generic-v1. Selected fields have
explicit role and normalization policy; category/variant ambiguity blocks correction.
Optional advisor is a narrow injected contract with no tools/policy authority,
pre-call token/output/cost bounds and no automatic remote provider. Strong identity
conflicts are preserved. Documentation must explain why RAM/boot size conflicts
can be reported for review even when a description spec correction is deterministic.

Deliver reviewable A durable execution, B reconciliation/category/report, C optional
advisor, D–F verification/docs slices from tasks.md. Skeleton/component contracts
come after G1; none are claimed already complete. Avoid general agent frameworks.

## Required gates

G1 behavior/tests/tasks/research pending. G2 skeleton and executable reds pending.
G3 components pending. Final independent review pending. Record artifact digest,
reviewer and actual findings in reviews.md when each gate occurs. Production
implementation requires G3 and saved intended acceptance failures. Changed behavior
returns through design and affected reviews; no rubber-stamped downstream gates.

## Verification and handoff

Execute SC01 smoke before expansion; deterministic exact cases assert zero advisor
calls/tokens. Real-path controlled fixtures cover matching/evidence, unknown crash
windows, persistent budgets, cancellation and category/unit interactions. Explicit
stress limits and one-domain live plan are in test-design.md. Save actual results
in verification.md; keep mechanism/stress vs actual live observation separate.
Baseline reused from parent: 86 identity/resolution tests passed. Required later
checks include relevant maintenance acceptance, tool/identity/evidence/monitor
regressions and full repo suite; inspect repository CI before final required checks.

G1 revisions freeze explicit baseline mode/presence tracking, finite profile table,
comparison-result versus final-finding precedence and POSIX file-lock/state-action
contract. See appended spec and test-design supplements; these govern skeleton.
No baseline source metadata or matching support may be fabricated from defaults.
