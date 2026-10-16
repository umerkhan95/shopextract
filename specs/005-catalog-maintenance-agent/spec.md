# Catalog Maintenance Agent — behavior specification

Issue: #25. Revision: author draft 2026-10-16. Phase: evidence-backed reports only.
Behavior and test design precede task breakdown. This epic is delivered as separately
reviewed slices; no implementation is authorized by a planning document alone.

## Outcomes and requirements

- **FR01 Goal contract.** Accept an explicit versioned reconciliation goal: baseline
  portable catalog/capture, supplier origin and optional bounded product URLs,
  selected supported field paths, item limits, freshness policy, budgets and optional
  investigator configuration. Validate before dispatch. No natural-language planner
  is needed. Unknown fields, malformed IDs, nonfinite/negative/bool numeric limits,
  ambiguous supplier scope and unauthorized origins fail without external calls.
- **FR02 Deterministic reconciliation.** Discover/extract using existing guarded
  tools; normalize, resolve evidence and match using existing rules. Only unique
  `exact`, non-review matches permit supported field comparisons. Matching conflicts,
  variants, bundles, duplicates, substitutions and title-only similarity stay review
  cases. Compare resolved observed values, preserving types and source support;
  absent/unknown/default/conflicting/expired values never authorize corrections.
  Equal supported values produce `unchanged`; supported differences produce
  `proposed_correction`; uncertainty produces `needs_review` with reason.
- **FR03 Optional bounded investigator.** Disabled by default. Deterministic cases
  make zero LLM calls. Only unresolved cases may send selected identifiers, selected
  field values and capped evidence excerpts to a configured local/user adapter.
  No bundled paid dependency or automatic external provider. Investigator output is
  advisory, schema-validated and evidence-linked; it cannot promote unsafe matches,
  manufacture facts, grant origins/tools, raise budgets or authorize writes. Disabled,
  failed or unavailable investigation preserves review cases and deterministic work.
- **FR04 Durable execution.** Persist job definition, policy/version fingerprint,
  ordered steps, attempts, budget ledger, portable results/evidence and report in a
  local transactional store. States: `queued -> running -> completed | partial |
  cancelled | failed`; recovered interrupted work becomes `paused` until explicit
  resume. Checkpoints commit result, evidence and accounting atomically. Resume
  skips committed external steps and is idempotent for report entries.
- **FR05 Honest crash recovery.** Reserve budget and persist intent before each
  external attempt. Crash after dispatch but before committed outcome leaves
  `outcome_unknown`: retain full reservation, never silently redispatch or reclaim
  it; continue independent work and surface review/partial status. Explicit operator
  retry may dispatch a new charged attempt if budget remains. Exactly-once external
  delivery is not promised. Stale runtime/session handles are never persisted as
  durable evidence; retain immutable portable records and source support.
- **FR06 Cancellation/retries.** One active workflow per store; exclusive ownership
  rejects a second runner. Cancellation is persisted, checked before every dispatch
  and commit, and does not erase committed results. No publication after acknowledged
  cancel; in-flight uncertain outcome stays charged. Retry only transient boundary
  errors, at most two attempts total per step, with persisted bounded delay; auth,
  policy, invalid data and unsupported fields do not retry. Restart never resets
  attempts/deadline/budgets. Terminal cancelled jobs cannot resume.
- **FR07 Hard cumulative budgets.** Enforce product count, actual HTTP attempts
  including redirects/retries/discovery, input/output evidence bytes, LLM input plus
  reserved maximum output tokens, cost in integer currency micro-units and absolute
  UTC deadline. Validate all caps before dispatch; zero request/token/cost allowance
  is valid and disables that external work. Token/cost upper bound and model price
  identity must be known before model dispatch or investigation is skipped. Unknown
  usage retains reservation. Provider-reported usage above reservation is recorded
  as a budget violation, halts model work and makes no claim of strict remote spend
  control. Timeouts bound each attempt and use remaining deadline; expired jobs
  become partial with completed findings, explicit remaining work and stop reason.
- **FR08 Durable cache.** Reuse only committed complete captures keyed by canonical
  source, exact extraction/normalization version, options and security-policy scope;
  investigator cache additionally keys model/prompt/selected evidence and field
  digest. Freshness is explicit and persisted; no new observation timestamp on hits.
  Expired/partial/missing-payload/corrupt entries miss or fail explicitly. Security
  authorization is revalidated on hits. Cache hits spend zero external/token budget,
  count as processed products, and preserve evidence provenance. Bound cache bytes
  and report bytes independently; eviction cannot delete evidence retained by jobs.
- **FR09 Reports.** Persist and return a versioned, stable ordered report with goal,
  field-level before/after and source values, durable evidence references/capture
  times, deterministic match reason, advisory investigation, unresolved reasons,
  coverage/counts, partial/terminal reason and charged/reserved/unknown usage. Each
  correction is inspectable after restart and cache eviction. Baseline input values
  are labelled supplied unless captured; supplier support never implies manufacturer
  authority. No probability calibration claim. Pagination/export preserve stable IDs.
- **FR10 Compatibility and operation.** Add opt-in Python API plus a runnable
  read-only example/CLI. Preserve existing Product/Variant constructors, extraction,
  ToolRuntime/MCP contracts, matching, monitoring and feed defaults. No downstream
  store writes, approval workflow, connector delivery, business prioritization,
  distributed workers, tenancy, scheduling or model training in this epic.

## Acceptance scenarios

SC01 supported technical description correction; SC02 all deterministic catalog;
SC03 ambiguous/disabled/advisory investigation; SC04 checkpoint restart; SC05 crash
windows; SC06 cancellation/runner ownership; SC07 bounded transient retries;
SC08 every budget edge and cumulative nested accounting; SC09 cache freshness,
policy and evidence lifetime; SC10 unsupported/missing/conflicting values;
SC11 malformed inputs and prompt injection; SC12 report bounds/order/compatibility;
SC13 investigator accounting/failure; SC14 partial-source plus restart interaction.
Exact fixtures and independent expected results are in test-design.md.

## Product decisions and boundaries

Conservative defaults: LLM disabled; single local SQLite store/runner; explicit goal
rather than free-text autonomous planning; caller sets supplier source policy and
freshness. Initial comparison fields are supported top-level `description`, `title`,
`price`, `currency`, plus explicitly addressed observed attributes; no arbitrary
JSONPath execution. Currency mismatch blocks price correction. Every conflicting
identity attribute is review-only under the current matcher, even if it is the
requested correction field. Thus RAM/weight changes may be unresolved. Initial
outdated-spec fixture changes operating-temperature text in `description` while
identity attributes remain equal. No implicit matching override is introduced.
No material user decision is currently blocking; the independent G1 reviewer must
challenge these conservative scope/default choices before contracts are frozen.

## Category-specific behavior (user steering, same draft)

- **FR11 Versioned category policies.** Category semantics are trusted configuration,
  never inferred policy from source prose or LLM output. Ship finite `hardware-v1`,
  `footwear-v1`, `generic-v1` profiles with explicit selected fields, identity/variant
  roles, compatible representations and units; allow validated caller-defined
  profiles using the same declarative contract. Hardware RAM/storage/model are
  identity/variant-sensitive; footwear size/size-system/color/fit are variant-sensitive.
  Technical dimensions/weight and material/construction specifications are comparable
  when supported and identity is independently safe. Generic policy makes no domain
  unit or attribute-role assumptions. Caller assigns profile per product/category via
  explicit mapping; missing, conflicting or unknown assignment produces review.
  Explicit generic assignment is allowed; it is never a silent fallback.
- **FR12 Category-aware findings.** Apply profile-specific deterministic comparison
  and narrowly declared unit aliases/conversions with traceable transforms. Exact
  decimal `1000 g = 1 kg` is permitted for declared mass fields; `GB` versus `GiB`
  and footwear `US` versus `UK`/`EU` are not equivalent. Category mismatch blocks
  correction even if identifiers agree. A field such as `color` may be comparable
  under a caller-defined hardware accessory policy and variant-sensitive for footwear;
  existing match conflicts still dominate both. Report category-relevant differences
  as `needs_review` with before/after evidence when identity is unresolved, rather
  than hiding differences or promoting them to corrections. No global weakening of
  matcher identity rules or silent deletion of conflicting attributes is permitted.

SC15–SC18 below cover these requirements. This supersedes any implication that only
description text matters: supported category specifications must be inspected and
reported, with conservative correction status when current identity rules conflict.

## G1 clarified baseline authority (G1-01)

Baseline mode is explicit and persisted: `supplied` or `captured`. In supplied mode,
only fields explicitly present in the submitted portable record are caller assertions
eligible for before-values; `0`/`false` are present, `null`/missing are unknown.
Constructor/legacy defaults introduced during loading are not explicit assertions.
An equal explicit value may produce unchanged and a different explicit value may
produce a correction when the supplier field is resolved, observed and supported.
Both results label the baseline `supplied`; source URL, observation/capture time and
evidence references are null/empty unless genuinely supplied captured support exists.
No evidence contract is fabricated. In captured mode, both before and after require
resolved nonexpired observation support; unsupported/default/conflicting baseline
values produce review. Missing before-values in either mode produce review, never
an invented before-value or inferred deletion. Empty string is an explicit supplied
string where allowed; captured empty values require actual observation support.

Matching is independent of comparison field authority: explicitly supplied baseline
identifiers/attributes may enter existing rules as caller assertions, labelled as
such in match reasons. Captured baseline identifiers preserve observed support and
must not be reconstructed from default scalar values. Supplier identifiers used for
exact authorization require resolved observed support. Conflicting identifiers or
attributes and one-to-one ambiguity always preserve existing match safeguards.
Live unchanged example explicitly selects supplied mode and copies explicit fields
from its saved real capture; it does not claim the supplied baseline was separately
observed. Captured-to-captured evidence is checked separately offline.

## Frozen initial category profiles (G1-02)

All keys below are exact field paths; attributes use JSON Pointer escaping (`~0`,
`~1`), no wildcard evaluation. Types refer to supported resolved values or explicit
supplied baseline values. Only requested declared keys are compared. Extra selected
keys fail validation; extra unselected fields are not silently compared.

| Profile | Field paths | Type / role | Allowed normalization |
|---|---|---|---|
| all three | `description`, `title` | string / comparable | exact Unicode text, no summarization or whitespace erasure |
| all three | `price`; `currency` | finite decimal; string / price context | existing decimal conversion with trace; currency must agree before price correction |
| hardware-v1 | `attributes/ram`, `attributes/storage`, `attributes/model` | string / identity-variant | exact strings; no GB/GiB or capacity conversion |
| hardware-v1 | `attributes/weight` | decimal + g/kg unit string / comparable | exact decimal g↔kg conversion to kg, retain original and transform |
| hardware-v1 | `attributes/material` | string / comparable | exact strings |
| footwear-v1 | `attributes/size`, `attributes/size_system`, `attributes/color`, `attributes/fit` | string / identity-variant | exact strings; size requires explicit agreeing size system; no US/UK/EU conversion |
| footwear-v1 | `attributes/weight` | decimal + g/kg unit string / comparable | exact decimal conversion to kg |
| footwear-v1 | `attributes/material`, `attributes/construction` | string / comparable | exact strings |
| generic-v1 | no attributes | no domain assumptions | only shared top-level fields above |

Profile role describes field meaning, not permission to bypass matching. Every pair
first runs the unmodified existing matcher on complete records. A nonexact/review
match makes final finding `needs_review` even if a field comparison is equivalent.
Record a separate comparison result `equal`, `different` or `unknown`, original
before/after and normalized values/trace. For a safe exact match, comparable equal
becomes unchanged and comparable different becomes proposed_correction. A changed
identity-variant field is review-only regardless of other signals. Thus `1000 g`
versus `1 kg` gives comparison equal/normalized 1 kg but final needs_review when
raw shared attribute difference triggers existing identity conflict. Never remove
those attributes before matching. Typed unsupported unit syntax becomes unknown/
needs_review; no best-effort conversion. Profile contents/version are immutable
within a job; editing them requires a new goal/job.

## Full local execution/action contract (G1-03)

`partial` is quiescent with visible unfinished/review work, not successful completion.
`completed` means all planned steps reached committed outcomes (review findings may
remain). Unknown external outcomes prevent completed until operator retries succeed
or explicitly leaves them unresolved, yielding partial. A complete but partial-source
capture is a committed attempt; resume does not automatically refetch it.

| Persisted state | resume action | cancel action |
|---|---|---|
| queued | idempotently return same job; eligible runner may claim | become cancelled, no dispatch |
| running, active owner | return `already_running`, no new runner | persist cancellation and await bounded cleanup before acknowledgement |
| paused after process loss | acquire ownership and transition running; unknown intents remain charged | become cancelled, retain unknown reservations |
| partial | resume only unfinished uncommitted steps, if fixed budgets/deadline permit; committed partial captures skipped | become cancelled, retain report |
| completed | idempotently return completed report, zero work | return completed unchanged |
| cancelled | reject `invalid_state`, never resume | idempotently return cancelled |
| failed | reject `invalid_state`; fatal validation/storage/version errors require diagnosed repair/new job | return failed unchanged |

Before resume dispatch, expired deadline or exhausted required allowance yields/
retains partial with precise stop reason and zero dispatch; no extension or reset.
Unknown intent counts as one attempt even when crash happened before actual wire
send. Explicit `retry_unknown(step)` is allowed only in paused/partial state, with
ownership, remaining time/budget and attempts <2; it creates/reserves a new attempt,
keeps old unknown reservation charged and never silently changes it to unspent.
At two attempts return `retry_exhausted`. Resume alone never retries unknown work.
Bounded transient retries use the same two-attempt ceiling. Successful explicit
retry may close step uncertainty for report purposes but retained unknown spend is
still shown. Irrecoverable individual source failure becomes a committed review
outcome; fatal store/contract failure is failed and cannot publish guessed success.

A local nonblocking OS advisory file lock (`flock` on supported POSIX systems) is
held for active store mutation/execution, with one stable lock path per canonical DB
path. It is kernel-released on process death; no stale PID deletion protocol.
Opening a read-only status view is allowed, a competing active runner fails
`owner_busy`. New owner verifies schema and atomically converts old running jobs to
paused, preserving queued jobs, attempts, intents and evidence. Database transaction
locking remains necessary; the file lock is not distributed ownership. Unsupported
lock platforms fail explicitly rather than pretending ownership is safe.

## Approved interim refinement — immutable advisory retry

FR05/FR09 now use immutable base findings plus separately committed immutable
advisory attempt publications. Reports compose latest committed publication by
attempt number while keeping base finding ID/status/before/after/match/evidence and
pagination stable. Pending/uncommitted advice never appears. Historical publications
and old unknown charged attempts remain inspectable. A latest successful second
attempt resolves advisory outcome uncertainty; previous unknown spend remains fully
reserved. Latest unknown remains partial; attempt3 is retry_exhausted. Any recorded
model overrun is a durable global model-dispatch halt across reopen/resume/retry.

Explicit unknown-advisor retry from paused/partial revalidates fixed goal deadline,
remaining budgets, cancellation, compatible exact profile definitions, original
selected payload/evidence fingerprint and original immutable accepted bound/model/
price/policy. Changed semantics require new job; no cache shortcut or fresh prompt
hides retry spend. Advisory result, usage, publication and checkpoint commit together.
Publication/cap/cancellation failure leaves previous composed report intact and new
uncertain reservation charged. Composed and retained advisory bytes count toward
existing report/evidence caps. Resume alone never retries and unknown/overrun stop
state derives from persisted attempts/publications, not runtime-only flags.

Product cap limits baseline processing and acquisition; it cannot truncate already
captured candidate evidence before identity classification. Preserve every captured
candidate within native/byte limits and mark scope partial when product cap is
exceeded. Zero product budget prevents even sitemap discovery or HTTP reservation.

Completion is shared across normal workflow and explicit advisory retry: durable
partial source coverage, unfinished independent source/comparison steps and model
outcomes are all considered. A successful advisory retry cannot convert partial
catalog coverage to completed or erase coverage. State/control updates without new
coverage preserve the prior coverage record. Source partiality/pending work takes
precedence over resolved advisory success in terminal reporting.
