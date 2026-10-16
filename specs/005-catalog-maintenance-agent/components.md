# Reusable component model — DRAFT, awaiting G2 then G3

No gate passage or implementation is implied. G2 corrections pending rereview.

| Component / owner | Consumers / reuse / lifecycle and error contract |
|---|---|
| Existing portable record codec and evidence resolver | Store capture/report and deterministic comparator reuse product_to/from_record, trust_view/resolve_fields; preserve observations/transforms/default distinction; never recapture imported evidence |
| Existing ToolRuntime + DomainAdapter + GuardedTransport | Maintenance native source driver uses existing guarded discovery/extraction/normalization; optional parent RequestAccounting callback reserves physical requests, defaults None for old callers; no forked parser/security implementation |
| Existing match_products | Reconciliation retains full records and existing exact/variant/conflict/one-to-one rules. Category comparator cannot authorize identity or erase attributes |
| MaintenanceStore (local durable owner) | Engine/report/evidence/status/control consumers; SQLite transactions own intents, attempts, reservations, checkpoint, stable findings and job-retained evidence. One flock execution owner; narrow cancel/status controls do not need execution lock; no public generic task framework |
| Goal validation/presence/fingerprint | Store creation and engine recovery; finite JSON, explicit supplied presence before reconstruction, selected field/profile/security/version fingerprints. Invalid schema/identity fails before network; immutable job content prevents changed-profile resume |
| CategoryProfile/FieldRule | Reconciliation and advisor payload selection; shipped finite hardware/footwear/generic plus Store custom_profiles trusted mapping. Validate/freeze exact fields/units and fingerprint contents; compare_field reports equal/different/unknown only; final match precedence lives in reconciliation |
| MaintenanceEngine | Public run/resume/retry_unknown/cancel callers; owns bounded step order, one runtime/advisor invocation, source cache and report commits, maps tool failures to explicit partial outcomes; no distributed scheduling |
| Investigator protocol and reservation/result types | Optional engine invocation only for unresolved cases; bound has no external spend; exact accepted reservation passed to invoke; returned model/price/usage validated, unknown usage stays charged. No provider SDK or extra shared service |

The durable budget ledger is part of Store/Engine, not a second general-purpose
budget framework. Existing per-operation tool budget remains compatible; parent
ledger additionally accumulates physical attempts across calls/restarts. Cache is
store-owned exact-version/policy/profile captures with freshness and independent
byte limits; evidence references pinned by jobs survive cache eviction. Report
pagination/evidence are read-only store queries; no downstream action connectors.

Schema/refinement consumers are real and limited to reconciliation/report/recovery;
new abstractions without those consumers are deferred. Existing constructors and
tool schemas remain unchanged. Component review should examine injection ownership,
transaction atomicity, tool context callback and cancellation cleanup. Matching,
field support and remote-response authority never move into advisor. See skeleton.md
for exact signatures, tables, failure boundaries and remaining test fixture work.

## G3 lifecycle correction (author submission)

This supersedes engine custom_profiles ownership above: Store constructor alone
receives trusted custom_profiles. It validates and snapshots shipped/custom exact
definitions with each job during create, owns deep-freezing and canonical fingerprint,
and exposes retained definitions in status. Engine consumes persisted definitions;
it receives no separate registry. Recovery compares Store's active compatible
registry against frozen selected definitions before dispatch; missing/changed values
raise profile_mismatch without network. Read-only historical evidence/report/status
remain accessible even if active definitions are missing. Restore original config
for resume or create a new job with changed semantics. No profile framework added.
New executable reds cover mapping mutation after create, durable definition inspection
on reopen and both missing/changed registry rejection before dispatch.

## Proposed FR05 unknown-advisor retry refinement — reviewer decision pending

Current implementation stores advisory within immutable base finding and correctly
retains uncertain attempts, but cannot explicitly retry after a resumed review finding
is committed. Do not waive FR05 or mutate deterministic facts. Proposed small design:
store immutable base finding plus separately committed advisory attempt results;
report composes latest committed advisory with stable base finding ID/status/values,
keeping prior attempt/result lineage and unknown charge. Explicit retry alone may
create attempt 2 under remaining fixed budgets/deadline; resume alone never retries.
The existing two-attempt ceiling applies across restarts. Missing/invalid/overrun
advisory cannot alter base match/fact authority. All writes/usage/publication stay
transactional and cancellation checked. No such refinement is implemented yet;
reviewer must approve contract/tests before production changes. Required failing
acceptance is in test_maintenance_advisor.py and verification.md.

## Approved interim refinement implemented for rereview

Store owns new immutable advisories table keyed job/step/attempt number, unique
attempt link and stable finding ID. Report composes latest committed advice; base
findings remain immutable. No runtime-only publication authority. Pending model step
persists original selected payload+digest, exact bound/model/price, profile and
security-policy digest. Explicit retry checks same contract and existing evidence,
then reserves attempt2 under original fixed budgets/deadline; no cache shortcut.
Store.checkpoint atomically publishes advisory/settlement/step with cap checks and
same-job declared child ownership. Historical publications are queryable via
advisory_history. Durable model_stop derives latest attempts/results; any violation
halts all model work, latest unknown stays partial. Normal resume never dispatches
an unknown advisor again. Provisional schema has no silent reset/migration of an
unrecognized store; missing required advisory schema is unsupported_version.
