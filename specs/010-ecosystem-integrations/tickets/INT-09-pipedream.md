# INT-09: Pipedream actions and completed-job source

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#71](https://github.com/umerkhan95/shopextract/issues/71).
Related planned work: [INT-01 / #63](https://github.com/umerkhan95/shopextract/issues/63).

Status: planned; researched2026-10-24. Owner: component maintainer. Dependency:
INT-01; #27 only if a later signed push source is enabled. Covers FR11/04/14,
SC11/04/14. Public registry distribution is a later external release step.

## Component construction

Create an app/common service client and versioned actions for submission, status,
result pages, evidence and cancellation. Use Pipedream app auth/props for credentials
rather than prompt parameters or copied secrets. The [action quickstart](https://pipedream.com/docs/components/contributing/actions-quickstart)
describes `type:action`, key/version/props/run and account-private publication through
`pd publish`. Proposed files live under a future integration package, not generated
inside this documentation slice. Pin helper packages and supported Node/runtime versions
at child implementation; avoid uncontrolled dependency updates in a running action.

Return structured authoritative envelopes and selected records, preserving decimal
strings, variant relationships and field support. Submit acknowledges durable job;
separate status/page actions prevent long crawls consuming action lifetime. No general
export/analytics/category/maintenance actions are advertised. Service auth cannot be
forwarded to a result URL or merchant origin.

## Source lifecycle and replay

Implement optional timer-driven new-completed-job source with persistent checkpoint
using [source lifecycle patterns](https://pipedream.com/docs/components/contributing/sources-quickstart).
Checkpoint tracks per-principal monotonic service commit sequence with stable event identity; timestamps are metadata only; explicit
first-start and reset/retention-gap modes prevent surprise historical floods. Source
activation/deactivation must not launch an independent merchant crawler or mutate stores.

The [component API](https://pipedream.com/docs/components/contributing/api) requires
emitted metadata IDs for dedup; `unique` retains only100IDs. Use it as a supplementary
bounded duplicate filter, not a permanent ledger. A crash between platform emit and
checkpoint commit can still redeliver; document at-least-once external workflow
semantics. Downstream consumers may dedup by stable completion ID. Authoritative
service job/result publication remains unique under INT-01 idempotency even when
workflow events repeat. Downstream recipe consumers use stable completion IDs in an
idempotent business-effect ledger. An ordinary repeated poll within retained checkpoint
state should emit no new event; a crash between emit/checkpoint can redeliver with the
same ID. Never suppress undelivered events just to claim exactly-once.

## Acceptance and future verification

- [ ] Actual action handlers execute submit/status/page/evidence/cancel against the real service boundary; wrong owner/revoked key fail safely.
- [ ] Source repeated poll emits stable IDs, returns late equal-timestamp/lower-ID and backward-clock commits across multiple pages and reports retained-window gaps explicitly.
- [ ] Faults before/after emit/checkpoint reveal documented replay behavior without losing a retained completion; repeated action after lost response uses same key/job.
- [ ] Fixture with >100completion identities proves no reliance on `unique` cache as durable dedup; downstream replay uses stable identity.
- [ ] `0.10`, zero/false/unknown values, variants/evidence and partial completeness survive component props/output; backoff/cancel remains bounded.

Mechanism tests use actual component/action/source code with controlled platform
boundaries and service persistence; save one smoke before stress. Future private live
run one action and two source polls, ≤12service calls/two products/120seconds and≤6
source requests. Runtime event/credit/memory/timeout limits depend on exact account and
must be rechecked rather than assumed. Private publish/deploy and public app/registry
availability are recorded separately. No Pipedream account writes, deployments, installed
packages or runtime tests occurred in this planning task.

Journal sequence/checkpoints remain decimal text or opaque tokens across JavaScript
outputs; never cast to Number. SC04/14 test9007199254740993 losslessly.
