# Skeleton contract — G2 submission, 2026-10-16

G1 passed (see reviews.md); no business algorithms implemented. Stub methods raise
specific NotImplementedError rather than fabricated success. Opt-in package only;
existing top-level package/tool schemas remain untouched.

## Public Python declarations

`maintenance/contracts.py`: immutable Goal (baseline records, explicit baseline_mode,
source/URLs, fields/profile mapping, required UTC deadline, freshness/version),
Budgets, AdvisorBound, Investigator protocol, MaintenanceError(code).
`maintenance/store.py`: MaintenanceStore(path).create(goal)->job_id;
status(job_id)->dict; report(job_id,offset=0,limit=100)->dict;
evidence(job_id,evidence_id)->dict; request_cancel(job_id)->status;
acquire()/release()/close().
`maintenance/engine.py`: MaintenanceEngine(store,tool_config,resolver,wire_transport,
utc_now,investigator,failure_hook); async run/resume(job_id)->report;
retry_unknown(job_id,step_id)->report; cancel(job_id)->status; close().
`maintenance/profiles.py`: immutable FieldRule, CategoryProfile; profile(name) and
compare_field(rule,before,after). These do not authorize identity.

Goal baseline explicit-presence map is captured before portable deserialization
fills constructor defaults. Supplied identifiers/fields carry caller assertion
labels; captured mode uses existing portable evidence contracts. Stable product key
is explicit `external_id` or canonical ID; absent IDs use zero-based input index
string. Duplicate keys fail validation. `profiles` maps those keys to shipped or
trusted explicit custom CategoryProfiles; custom registration requires validated
immutable fields and unique versioned name (add optional constructor profile mapping
at component refinement; no scraped input may register a profile). Exact contents
are fingerprinted. UTC deadline is required; no hidden fresh timeout on restart.

## Durable layout and ownership

One SQLite schema_version table plus:
- jobs(id, goal_json, fingerprint, state, cancel_requested, deadline, stop_reason);
- steps(job_id, stable step_id, ordinal, kind, state, payload_digest, result_ref);
- attempts(job_id, step_id, attempt_no, state, reserved_json, usage_json, error);
- captures(id, portable_records_json, support_json, source/time, completeness);
- evidence(id, immutable payload_json, byte_count), job_evidence(job_id,id);
- findings(job_id, finding_id, ordinal, payload_json);
- cache(key, capture_id, expires_at, byte_count).

Foreign keys and uniqueness enforce nonduplicated steps/findings and evidence
retention. Store methods transactionally validate/copy finite JSON and schema version.
No arbitrary pickle or runtime handles. Transaction boundaries encompass result,
evidence references, attempt settlement and checkpoint together. A persisted intent
is conservative unknown on recovery, charged even if it predated actual send.
File corruption/unknown schema fails closed; no silent DB reset or migration.

Exclusive execution acquires a stable canonical DB lock path with nonblocking
POSIX flock; owner death kernel-releases it. Acquiring owner recovers running jobs
to paused transactionally. **Status reads and request_cancel are narrow SQLite
control operations permitted while another process owns execution lock**. They do
not claim workflow ownership. Cancellation acknowledgement requires owner cleanup
or confirmed owner death; merely setting cancel_requested is not acknowledgement.
Store request_cancel returns requested state; Engine.cancel waits bounded cleanup
and returns acknowledged cancellation or explicit cleanup timeout (never pretend
cancelled). All dispatch/commit boundaries recheck persisted cancellation. Other
writes/execution require owner. Repeated calls/terminal states follow spec table.

## Physical source accounting seam (declaration, not implemented)

`RequestAccounting.before_request(method,url)->attempt_id` commits a durable
reservation+intent synchronously and may raise MaintenanceError. Add an optional
accounting field to OperationContext with default None (or equivalent optional
constructor callback passed through runtime/jobs). GuardedTransport invokes it
**immediately before each raw physical HTTP dispatch**, after authorization and
local request limit validation but before `raw.handle_async_request`; redirects and
retries each invoke it. Existing no-hook callers preserve old behavior. Parent job
limits cannot be reset by nested ToolRuntime operations. Response receipt alone
never settles a durable attempt: result/evidence checkpoint commits settlement.
Failure between raw send and result checkpoint retains reservation/unknown outcome.
Known pre-dispatch denial makes no external send; conservative recorded intent is
not casually refunded without proof. Security/SSRF remains owned by existing guard.
Hook failure must propagate explicit partial/budget error and never become success.

One runtime per active step or bounded owned workflow session; results and owner
support are copied to portable retained records before tool graph expiration/close.
Native parser/normalizer/matcher/resolver run unchanged. No unsafe fallback. Relevant
ToolRuntime graph/item/time caps remain additional upper bounds.

## Report and failure shapes

Report dict: schema_version, job_id, state, stop_reason, findings, coverage, usage,
pending_steps; finding: finding_id, product_key, profile, field, role, status,
comparison(equal/different/unknown), before, after, normalized_before/after, trace,
reason, baseline_support(kind/evidence_ids/source_url/observed_at), supplier_support,
evidence_ids and optional advisory. Stable order: input ordinal, requested-field
ordinal; stable finding ID derives job/product/field (not current runtime handle).
Usage includes requests, tokens, cost_micros, active reservations and unknown_requests;
unknown model spend retains full reservation. Evidence retrieval is job-scoped.
Pagination slices same stable committed findings; report cap stops new publication
transactionally with explicit partial reason, never corrupts older findings.

MaintenanceError codes: invalid_argument, unsupported_version, permission_denied,
not_found, owner_busy, already_running, invalid_state, retry_exhausted,
storage_error, cleanup_timeout; partial stop reasons distinguish request_budget,
product_budget, token_budget, cost_budget, deadline, evidence_budget, report_budget,
source_partial and outcome_unknown. Low-level tool errors map without leaking secrets.
FailureHook(event,payload) exposes intent_committed/before_dispatch/after_dispatch/
before_checkpoint/after_checkpoint under test, payload has stable job/step IDs.
Hook is injected trusted testing instrumentation, not accepted in goals/source text.

## Executable red evidence

27 tests collect and run successfully, all fail intentional NotImplementedError in
create/acquire/profile. Command/results are in verification.md. They cover a core
cross-section; remaining matrix cases (captured provenance, real category conflicts,
all budget families, cancellation races, crash subprocesses and advisor timeout)
remain required implementation-stage fixtures in test-design.md, not claimed done.
G2 must review actual signatures and planned seam; no production implementation
before G3 and acceptance reds.

## G2 corrections submitted for rereview

Positive baseline external_id and profile key are now `S1`, matching native JSON-LD
normalization from SKU. The same `supplier_html()` drives HTTP fixture and actual
`tools.domain.synchronous(parse)` precondition; existing classify_match must return
exact/non-review before positive workflow tests reach create. A separate negative
source-ID disagreement stays nonexact/review. Fixture unit check passes without
maintenance implementation.

Advisor invocation signature is now `investigate(payload, *, reservation:
AdvisorReservation, timeout)->AdvisorResult`. `bound` is strictly local/no-spend.
AdvisorReservation holds durable reservation ID plus immutable accepted AdvisorBound.
AdvisorResult declares model, price_version, advisory, evidence_ids and usage;
AdvisorUsage holds finite nonnegative input_tokens/output_tokens/cost_micros. `usage=None`
explicitly means unknown and retains full reservation. Returned model/price must match
accepted bound; known usage must fit each accepted bound or record violation/halt
further calls, preserving evidence uncertainty. Malformed schema never settles spend
optimistically. New red requires actual first invocation receiving accepted bounds,
unknown 64-token/10-micro reservation retained and second eligible case blocked.
Existing adversarial advisor case now requires call count 1 rather than passing
without model boundary invocation.

Custom profile injection is concrete: MaintenanceEngine(..., custom_profiles:
Mapping[str, CategoryProfile] | None = None). Trusted profiles are validated/frozen
and included in durable goal fingerprint before execution; unknown names fail, never
load source-defined rules. No dynamic code/plugin import. This is signature-only.

## G3 profile lifecycle refinement (supersedes engine registry declaration)

Single authoritative configuration owner: `MaintenanceStore(path, *, custom_profiles:
Mapping[str, CategoryProfile] | None=None)`. Engine no longer accepts custom_profiles.
Store.create validates selected names/fields against shipped profiles plus this
trusted registry, deep-freezes exact definitions and stores canonical definitions
and their digest inside immutable goal metadata before returning a job ID.
Mutable caller mappings cannot alter a created job. Custom name collision with a
shipped name or mismatched mapping key/name is invalid_argument; finite declared
normalization/type/role enums only. status includes retained profile_definitions
for inspection, even when reopening without active custom configuration.

Engine consumes persisted definitions from its Store only. Before any new external
dispatch on run/resume, Store validates all selected persisted profiles against
current compatible shipped/custom definitions (name, supported version and exact
canonical definition fingerprint). Missing/changed custom definition or unsupported
shipped version raises profile_mismatch and performs zero dispatch. Existing report/
evidence/status reads remain allowed. Restore original trusted configuration to
resume; semantic profile changes require a new job. Queued jobs have same check.
No second engine registry, dynamic policy loading or silently refreshed fingerprints.
Cache keys include the frozen exact definitions; registry changes cannot reuse old
semantics. This is a declaration, not implemented persistence or validation.
