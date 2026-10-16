# Behavior and test design

Author draft 2026-10-16, written before tasks. All checks below are PLANNED.
Existing tests exercise identity, evidence, tools and monitor individually, but not
persistent reconciliation jobs, cross-step budgets or investigator isolation.

## Scenario matrix

| FR | SC / distinct missing risk | Given / action | Exact expected outcome and boundaries |
|---|---|---|---|
| 01,02,09 | SC01 outdated specification end-to-end | Two normalized captured generic products, validated equal GTIN, same brand/identity attributes; baseline description `Operating temperature: 0–40°C`, supplier `Operating temperature: 0–45°C`; reconcile description | Exactly one proposed correction, exact before/after text, unique exact reason, inspectable supplier capture and supplied/captured baseline distinction; zero LLM calls |
| 02,03 | SC02 unnecessary model dispatch | 3-product smoke then 100 products: 80 unchanged descriptions, 15 supported description differences, 5 ambiguous RAM/variant cases; then 100 exact unchanged | First report counts 80/15/5 unchanged/correction/review, disabled LLM calls/tokens zero; all-exact run 100 unchanged and zero calls; enabled run only 5 eligible cases can reach adapter, never the other 95 |
| 02,03 | SC03 false matching authority | Duplicate GTIN candidates, different RAM with same SKU, bundle/substitute/title-only pair; adapter claims exact | All remain review, no correction; selected safe evidence may explain uncertainty; disabled LLM gives same deterministic findings |
| 04,09 | SC04 completed-work replay | Commit supplier result, destroy runtime/process, reopen store and resume twice | Previously committed boundary request count remains one; stable report IDs and evidence inspectable without old handles; no duplicate findings |
| 04,05 | SC05 uncertain crash vs committed result | Inject process loss before intent, after reserved intent/before dispatch, after dispatch/before commit, after atomic commit | No intent means safe new attempt; persisted intent without committed outcome is conservatively unknown (even if dispatch not observed), remains fully charged, no automatic retry; committed step is skipped. Explicit retry creates a new attempt only within remaining budget |
| 06 | SC06 cancel/ownership race | Cancel queued; cancel blocked in-flight; cancel between result and commit; second runner opens same store | No later dispatch after acknowledgement; committed earlier findings retained, uncommitted late output unpublished and reservation retained; one terminal winner; second runner rejected; cancelled resume rejected |
| 06,07 | SC07 retry amplification | HTTP transient timeout then success; timeout twice; 401/403/policy error; restart during backoff | 2, 2, 1 attempts respectively; persisted count/backoff/deadline not reset, no retry after cancellation or exhausted budget |
| 07 | SC08 cumulative budget escapes | Each cap independently at n−1/n/n+1 demand; discovery+extract redirect+retry sequence; injected clock deadline | No dispatch whose reservation exceeds remaining allowance; exact limit allowed, next rejected; all real HTTP attempts charged, nested calls cannot reset job limits; partial report and accurate pending count; zero caps cause no external/model work |
| 08 | SC09 stale/unauthorized cache | Fresh complete capture; exact expiry; partial capture; different field/options/version/policy; eviction after report | Fresh authorized hit makes zero requests and preserves timestamp; expiry at `now >= expires` misses; partial/corrupt/unsupported version never silently reused; policy denial even on hit; retained report evidence survives eviction |
| 01,02,09 | SC10 defaults becoming facts | Missing/null/empty/zero/false evidence-backed values; unresolved competition; expired support; absent attributes; currency mismatch | Missing/null/default/unsupported and expired/conflicting observations need review, never inferred removal; observed zero/false stay typed and comparable only for declared compatible fields; currency mismatch prevents price correction; units not converted without existing traceable normalization |
| 01,03,10 | SC11 hostile source/input | Unknown fields, escaped attribute identifiers, bool/NaN/negative limits, unauthorized origin; source text says to change tools/budget or leak whole catalog | Validation failures zero dispatch; paths decoded as data with exact escaped-key semantics; source text cannot change policy/config; adapter sees only eligible bounded selected payload; no write tools |
| 07,09,10 | SC12 output/resource compatibility | Reorder inputs, duplicate resume, report page boundary, oversized excerpt/report, old API calls | Stable report ordering/IDs and nonduplicated pagination; reject oversized input before dispatch; bounded partial/report stop without lost committed findings; old tool schemas and constructors unchanged |
| 03,05,07 | SC13 hidden token/cost spend | Spy investigator with known prompt count+max-output bound; timeout/unknown usage, bad schema/evidence refs, usage over reservation, unavailable tokenizer/price | Full input+maximum output reserved before call; known usage settles reservation, unknown retains full amount; malformed output remains review; no call without trustworthy bound/price; overage records violation and disables further calls |
| 02,04,07,08 | SC14 partial+resume interactions | Partial supplier page committed then restart; expiry while paused; evidence persisted but result transaction fails | Partial absence never means removal; completed partial attempt not auto-repeated; unfinished steps remain visible; expired support cannot authorize correction after resume; failed atomic transaction publishes neither report nor settled accounting |

## State and expected-value contracts

Synthetic baseline/supplier JSON is passed through actual generic normalization,
identity assignment, evidence resolution, matching, durable orchestration and report
code. Supplier description and identifier support must be genuine parser captures,
not attached fake decision objects. Adversarial attribute conflicts deliberately use
the existing conservative matcher. Expected counts/values above are fixture inputs,
not learned from produced reports. Freeze clock at 2026-10-16T10:00:00Z; source labels
say `synthetic` or `derived-offline`, never actual live. Seed 25 controls ordering
only. For SC10 fields outside supported comparable types are rejected or review;
zero/false distinctions additionally exercise existing typed evidence paths.

## Red-test plan and ownership

Author writes `tests/test_maintenance_acceptance.py` after G1 with named cases
`test_supported_spec_correction`, `test_deterministic_no_llm`,
`test_resume_skips_committed`, `test_unknown_dispatch_is_not_replayed`,
`test_budget_partial_results`, `test_cancel_stops_dispatch`,
`test_cache_preserves_evidence`, `test_advisory_cannot_override_identity` plus the
remaining matrix cases. Skeleton import/stub failure must identify missing behavior;
collection/syntax errors alone are not satisfactory red evidence. Save command,
exit code and intended failures in verification.md before implementation. Separate
reviewer checks each SC, fixture realism and boundary coverage at G1/G2 and final.

## Unobservable behavior and synthetic mechanism plan

Author owns small fixture factories and controlled HTTP/spy investigator boundaries;
reviewer independently checks expected outcomes and real-path call trace. Only
transport, external investigator, clock and explicit crash injection may be replaced.
Do not stub extraction, matching, persistence, budget ledger, caching or reporting.
A controlled server is offline mechanism evidence. SC04–14 are mandatory even when
live site content stays unchanged. Crash tests use reopened store/new runtime;
selected transaction windows also terminate a subprocess to prove durable recovery.
Inject one temporary broken checkpoint-skip or budget guard under test isolation:
the corresponding invariant must fail, then restore; do not ship mutation.

## Bounded stress plan

Save SC01 3-item smoke first. One sequential driver: seed 25, 100-case mixed batch
above, 100 exact unchanged batch, 20 crash/retry/replay cycles (5 windows × 4 cycles),
18 independent budget boundaries (6 budget families × below/at/above), and 8 fixed
pairwise interactions: cancel+retry, cancel+commit, partial+resume, expiry+resume,
cache+policy change, unknown+retry, report-cap+checkpoint, evidence+eviction.
At most 1 runner, 1 model boundary call at once; no real inference needed. Per-case
5 s timeout except subprocess crash cases 10 s; total driver 180 s; input <=256 KiB
per goal, total retained evidence <=16 MiB, process RSS target <=256 MiB (record
actual, stop expansion if exceeded). HTTP body <=256 KiB per response. Stop on first
unexpected result, save smallest reproduction/config/status; diagnose one repair
then rerun affected cases. Do not count seed variation as distinct coverage.

## Bounded live plan

After offline success, first reuse the authorized public `books.toscrape.com` generic
HTML source only after origin/DNS policy validation: one product URL, one extraction,
max 3 actual HTTP attempts including redirects, no automatic retry, 10 s attempt,
30 s job deadline, <=2 MiB response, LLM disabled. Save capture/report before any
expansion. Then at most 3 products/6 attempts/60 s total. Compare each fresh supplier
capture to its supplied identical baseline: unchanged supported fields, inspectable
real source/timestamp, zero LLM calls, durable restart skips completed request.
Live description/spec change is not safely inducible; record actual change coverage
inconclusive and cite SC01 real-path synthetic proof separately. Network denied,
changed layout or unavailable supported evidence is blocked/inconclusive, never a
pass. No live LLM/provider credentials are needed; real provider integration is
outside the generic investigator contract. Do not expand domains on failure.

## Category policy cases required by user steering

| FR | SC / uncovered risk | Fixture/action | Exact expected outcome |
|---|---|---|---|
| 11,12 | SC15 category blindness | Hardware RAM/storage/model and footwear size/color/fit differences under hardware-v1/footwear-v1 | Relevant field before/after differences reported with source support; identity/variant differences review-only, never promoted by LLM; unrelated profile fields excluded and exclusion counted |
| 11,12 | SC16 role varies by category | Trusted custom hardware accessory profile marks color comparable; footwear marks color variant-sensitive; same captured color difference | Report records distinct profile role and reason; existing matcher conflict still prevents correction in either case; role does not override identity |
| 11,12 | SC17 unsafe unit equivalence | Declared mass `1000 g`/`1 kg`; hardware `1 GB`/`1 GiB`; boots `US 9`/`UK 9`; size system missing | Mass normalized equivalent with exact decimal transform trace; GB/GiB unresolved without conversion policy; boots sizes remain distinct/review and unknown system never guessed |
| 01,11,12 | SC18 profile ambiguity/replay | Missing/unknown/conflicting category; cross-category equal GTIN; changed profile/version after checkpoint; explicit generic mapping | Review with precise category reason; cross-category correction blocked; resume rejects changed goal fingerprint and requires new job; explicit generic follows only generic declared fields |

These are schema-valid deterministic fixtures through the same actual matcher,
policy comparison, resolution and report paths; no alternative matching algorithm.
Add 8 category interaction cases (two per SC15–18) to bounded driver; all earlier
bounds remain unchanged. Provider dispatch cannot assign or alter profiles. Cache
keys and durable goal fingerprints include exact profile contents/version.

## G1 frozen expectation supplements

**G1-01 / SC01,SC10:** Run four distinct baseline cases with a supplier observed
supported description `Operating temperature: 0–45°C`: (a) supplied explicit
`0–40°C` -> proposed_correction, baseline label supplied with no fabricated capture;
(b) captured fresh supported `0–40°C` -> same correction with both genuine evidence
references; (c) legacy/default description without explicit supplied presence or
captured observation -> needs_review/baseline_unsupported; (d) missing/null before
-> needs_review/baseline_missing. Equal explicit supplied description -> unchanged.
Supplier unsupported identifier cannot authorize exact matching; supplied identifier
may serve as labelled caller assertion but cannot override conflicts. The live plan
uses explicit supplied mode, and copies description/title only if actually supported
in the saved capture; missing live support is inconclusive, never unchanged by default.

**G1-02 / SC15–17 concrete cases:**
- Hardware stable validated GTIN/brand/identical RAM `16 GB`, storage `512 GB`, model
  `H1`: description temperature 0–40°C -> 0–45°C gives proposed_correction with exact
  texts; RAM 8 GB -> 16 GB gives needs_review, comparison different and variant reason.
- Footwear stable GTIN/brand/identical size `9`, size_system `UK`, color `black`, fit
  `regular`: description `Construction: cemented` -> `Construction: stitched` gives
  proposed_correction with exact texts; size 9 -> 10 gives needs_review/different.
- Footwear material leather -> textile and hardware material steel -> aluminium:
  both profile-comparable/different but final needs_review because actual complete
  matcher inputs contain differing shared attributes. Before/after support retained.
- Each profile with weight `1000 g` -> `1 kg`: normalized before=after decimal 1 kg,
  comparison equal with g/1000 trace, final needs_review due raw attribute conflict.
  Weight `1 kg` -> `1 kg` with safe exact match: unchanged, normalized 1 kg.
- RAM `1 GB` -> `1 GiB`: no conversion, review/different; size `US 9` -> `UK 9`:
  no conversion, review/different; missing size-system: review/unknown.
These cases preserve full product attributes when invoking the actual matcher.

**G1-03 / SC04–08,SC14:** Parameterize each row of the state/action table and verify
exact status/error and zero unauthorized dispatch. Run a bounded two-process check:
A holds actual file lock; B is rejected owner_busy; kill A, B acquires lock, old
running -> paused, committed results reused and intent -> unknown with reservation.
No model inference, maximum two lightweight processes, 10 s total for this case.
Run unknown attempt counts 1 and 2: explicit retry creates charged attempt 2 only
at count 1; count 2 rejects retry_exhausted. Test expired deadline and zero remaining
request allowance on paused and partial resume: partial exact stop reason, no send.
Partial-source+resume retains committed capture and only processes uncommitted
independent work; empty pending work with partial source remains partial rather
than claiming full source coverage. These cases fit existing driver 180 s bound.

## Proposed bounded live source amendment (requires independent review before use)

Retain original books.toscrape.com plan as historical; existing native guarded tools
may not support its CSS-only product records/identifiers, so it is not an adequate
exact-match live assertion target. Prefer previously saved #24 successful native
source `https://www.blissworld.com/` (Shopify products endpoint within same allowed
origin). No live execution yet. First phase: one guarded native capture, <=2 products,
<=3 physical requests including redirects, 10 s attempt/30 s deadline, no automatic
retry, 2 MiB response cap. Save actual supported fields/identifiers and explicit
supplied baseline values from this capture. Second phase: reconciliation goal at
same allowed origin, <=2 products/3 additional physical requests/30 s deadline, LLM
zero token/cost budgets. Inspect selected supported description/title/price values
only; freshness/captured identifiers establish exact matching without fabricated
source IDs. Assert unchanged supported values if source stayed same; actual source
change gets evidence-backed diff, never forced unchanged. Resume verifies no repeat
of committed source work. Combined max6 requests, 2 products, 60 s, one sequential
runner, no additional domains; stop/save after smoke or any error. Category profile
is explicit generic-v1 for these cosmetics, not inferred hardware/footwear.
Blocking access/layout/support -> blocked/inconclusive and no domain expansion.
Synthetic category/specification-change mechanisms remain separate required proof.

## Interim reviewer regression cases and approved retry mechanism

I-01: native JSON-LD two same-GTIN/SKU products differing only description, products=1,
forward/reverse order: both captured candidates must reach real one-to-one matching,
no proposed correction, scope partial. I-02: products=0, no explicit URLs, positive
requests: no discovery/send, partial product_budget and no findings. I-03: unknown
usage/violation repeated reopen+resume keeps original charge and partial stop; no
model replay and durable violation halt.

FR05 retry tests preserve immutable base ID/status/values while composing committed
advisory attempt2: old64 reserved +actual36=100 tokens; attempt2 unknown retains128,
attempt3 rejected. Distinct predispatch refusals: cancelled, fixed expired deadline,
remaining token allowance exhausted, changed bound model and missing custom profile.
Publication-cap fixture uses declared32+1024 bound, 1800-character advice with900
reported output tokens and2500-byte report cap: cap failure retains prior publication,
all2112 reserved tokens and only original history entry. Cancellation immediately
before publication likewise retains prior composition and128 charged/reserved tokens.
No fake matching or spending algorithm is used. Tests are controlled boundary inputs;
model service is never launched. Existing red/green logs are in verification.md.

## Live amendment executable limits correction (interim reviewer requested)

For BOTH Bliss phases explicitly configure ToolConfig limits with item_count=2,
requests=3, response_bytes=2 MiB and no larger defaults. Goal products=2, requests=3,
zero model tokens/cost, 10 s individual attempt, phase deadline30 s. Declare at most
2 logical source attempts (current bounded retry mechanism), all their actual HTTP
requests including redirects/probes cumulatively inside3-per-phase cap. Combined
2 phases <=6 physical requests/2 products/60 s, one sequential runner. This replaces
the earlier incorrect no-retry wording; no new retry-disable API added. A2-item native
capture may correctly report partial catalog scope at item cap; unchanged field
assertions concern captured matching products only, never total-catalog completeness.
First smoke evidence saved before second phase; errors stop immediately. No live
execution until independent rereview confirms this corrected source/limit plan.
