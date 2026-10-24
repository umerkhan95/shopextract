# Implementation plan — design draft

## Constitution check
Explicit opt-in preserves extraction constructors, identity, evidence, feed defaults and maintenance absence semantics. Facts retain their own sources; unknown parent or unavailable endpoint is never a confirmed absence. Core stays MIT/self-hostable with no paid service or inference gate. Work is sequential and bounded; user has now authorized implementation, subject to the required engineering gates.

## Architecture and decisions
1. Acquisition owns read-only per-store Store API pagination and coverage. Reuse existing guarded transport where its security and byte limits fit; audit actual guarantees before choosing an integration seam. Do not route through an unguarded client for convenience.
2. Parser/evidence builder owns category facets and merchant-scoped identities. Reuse category contracts where compatible; propose explicit index/parent-edge representation at G2 rather than changing product membership behavior.
3. Topology resolver consumes bounded facts after acquisition, detects orphan/conflict/cycle/depth issues and preserves competing declarations. It does not assign product categories.
4. Optional bridge consumes evidenced product memberships and explicit trusted exact mapping rules. Reuse `categories/mapping.py`; it intentionally excludes `index` and `parent_edges` observations. Resolve referenced Shopify targets against the pinned packaged catalog; register only needed validated target IDs under existing generic 1,000-target/config-byte caps.
5. Bind rules to merchant scope and pinned target version. No name-based guessed migration after taxonomy updates; reject stale/invalid targets and require reviewed rule update. Unknown native Woo version requires the existing explicit rule opt-in.
6. Keep product companion `terms`, relation references, record bytes and config limits independent of traversal limits. New tree data enters maintenance only through reviewed evidence-aware seams; acquisition incompleteness cannot imply removal.

See `research.md` for known code/source facts and unresolved decisions. `skeleton.md` and `components.md` will be created at their actual later stages; no premature interfaces or future verdicts are claimed.

## Resource contract (W02 resolved; G1 pending)
One sequential flow, max 10 HTTP attempts including redirects/failures; 100 items/page; 1,000 retained categories; 2 MiB identity response (nonidentity encoding is rejected); 8 MiB retained payload including conflicting facts; depth 8; 30 seconds overall; no retries/LLM. Deadline and guard checked before each attempt and during body reads. Counts/bytes apply to rejected and duplicate input as needed to prevent bypass; exact accounting shape is a G2 interface decision.
Configuration may lower ceilings to zero; negative/bool/noninteger limits reject before I/O. Zero depth permits roots; other zero work capacities perform no I/O. Stop before exceeding limits; retain inspectable accepted facts and explicit partial/unavailable reasons. Limits are not claims of complete coverage for large or changing stores.

## W02 decisions
Use the existing numeric-IP-pinned guarded transport with a whole-fetch deadline
and cancellation owner. Permit only same-origin redirects. Reject compressed
responses rather than decompressing. Upstream supports parent IDs and deliberately
omits totals on first short/empty pages: allow a page-two confirmation only for a short/empty first page (a full
headerless page stops partial immediately), require
consistent totals and raw/distinct counts, otherwise preserve partial coverage.
See `research.md` for exact completion/status/accounting rules and source dates.
Acquisition and explicit captured-membership lookup are this delivery. The optional
Shopify bridge is deferred and does not block acquisition verification.

## Required gates
Current deliverables are author drafts pending independent review. W01/W02 are complete; G1 remains pending; no production implementation before G1/G2/G3 plus executable saved red evidence. Reviewer must record artifact revision/digest, findings, severity, disposition and verdict in `reviews.md`. Authors cannot approve themselves. Meaningful contract changes invalidate affected reviews.

## Verification and handoff
`test-design.md` defines named acceptance tests, one small offline smoke, deterministic seed/24-case stress and bounded live smoke. Actual checks belong in `verification.md` when executed; keep live observations, synthetic mechanisms and stress outcomes separate. One diagnosed repair per blocker; save compact reproduction and continue independent work if unresolved. No probes/tests executed during planning or W02.
Next step: independent G1 review of resolved W02 decisions. Skeleton/red tests follow G1, components follow G2, production follows G3. No push or PR is requested.
