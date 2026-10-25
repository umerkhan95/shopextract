# Independent review record

## G1 — 2026-10-16 — changes required

Reviewer: `maintenance_reviewer`, separate from `maintenance_author`.
Scope: behavior, tests, tasks, research and plan only; no implementation or test
execution. Reviewed issue #25 using `gh issue view`, local workflow/constitution/
templates, and the real guarded transport, source execution, domain adapter,
normalization and identity matcher seams. No external research or inference.

Reviewed SHA-256 digests:

| Artifact | SHA-256 |
|---|---|
| spec.md | `4b7edaa2f4f4414021c6c65e06f2f5dbdb38a08081bde14e5715078bb27d01a3` |
| test-design.md | `d39ec0459828ef863854402f1a00ef77e1765feaa245ebbbeae7a56cbe218008` |
| tasks.md | `66d7e40406d81a71c22b7750e5d15158247c0c1f8fe1b62758a02b8b8c895661` |
| research.md | `32abf3cbe09aff2e6787d96ff3d322fb6b9df258c40d6e8efef982f656deb49c` |
| plan.md | `5f6cff492e266c4acadaced3bc5959359b46f4ac11910464ce96eeaaad6aa913` |
| status.md | `f2b30ee305ac890c627b53edbf94d748f4c8b7be8ed9c7c8214cb1ebf4bc6e14` |

### Findings requiring author disposition

1. **G1-01 / P1 / open — supplied baseline comparison is contradictory.**
   FR01 accepts a portable baseline catalog, FR02 permits only resolved observed
   values, while FR09/SC01 allow supplied baseline labelling and the live plan
   expects an identical supplied baseline to produce unchanged findings. A plain
   supplied catalog need not contain an evidence contract. Decide explicitly
   whether such values are eligible as labelled caller assertions or require a
   captured baseline. Define identifier/matching support independently from field
   support; never synthesize observations or supplier authority for supplied data.
   Add separate exact outcomes for supplied baseline + captured supplier, captured
   baseline + captured supplier, legacy/default baseline, and missing baseline
   values. Align live preconditions and correction/unchanged/review expectations.

2. **G1-02 / P2 / open — category and unit acceptance outcomes are not frozen.**
   FR11 promises finite shipped profiles but names no finite comparable key/type/
   role/unit table; SC15 has no concrete values and SC17 only says mass becomes
   equivalent. The actual matcher treats every differing shared attribute as a
   conflict before returning exact, including mass/material. Consequently
   `1000 g` versus `1 kg` can have equivalent comparison values while the product
   pair still requires review. Specify initial profile keys/types/roles, allowed
   transforms, and precedence of match status versus field equivalence. Supply
   concrete hardware and footwear cases (including a comparable specification,
   variant-sensitive change, and the mass case) with final finding status and
   before/after/normalization expectations. Keep matcher inputs/conflicts intact;
   do not solve this by silently removing attributes or weakening existing rules.

3. **G1-03 / P2 / open — resume state transitions need explicit observable rules.**
   FR04 lists terminal-looking `partial`/`failed` outcomes and separately introduces
   recovered `paused`, but SC14 expects partial-source + resume and the spec does
   not say which states can resume or how unknown attempts/pending work affect
   completion. Define a state/action table: resume of queued/running/paused/partial/
   completed/cancelled/failed; exact outcome for expired deadline or exhausted
   budget; explicit retry of an unknown attempt versus the two-attempt limit;
   and recovery after owner process death. Add bounded two-process ownership
   death/reacquisition and invalid-state resume expectations to SC04–08. This is
   local ownership/recovery only, not distributed worker scope.

### Satisfied design constraints and next gate checks

Issue acceptance and user steering are otherwise traced to FR/SC IDs. Deterministic
cases require zero model calls; optional advisory cannot override identity/policy.
Physical HTTP accounting must hook `GuardedTransport` before each `raw` dispatch,
not only `GuardedSources.execute`, whose native extraction/discovery may perform
several requests. This requirement is correctly recorded; inspect actual hook and
failure semantics at G2. Crash reservations, unknown usage retention, cache-policy
revalidation and retained evidence are explicitly required. Model cost guarantees
are honestly conditional on the configured adapter's known upper bounds, with
overrun treated as a violation rather than a promise of strict remote spend control.

Verdict: **changes required before G1 passage**. Author resolves these findings in
behavior/test artifacts; reviewer checks changed digests and dispositions. No G2,
G3, red/green, synthetic, stress or live result is claimed by this review.

### Author dispositions submitted for G1 rereview

Author: maintenance_author, 2026-10-16. Reviewer verdict above remains unchanged.
- G1-01: spec baseline-authority section freezes supplied/captured modes, explicit
  presence/default distinction and independent matching authority; test supplement
  adds four separate exact baseline outcomes and aligned live preconditions.
- G1-02: spec freezes hardware/footwear/generic field/type/role/unit table, final
  match-status precedence and comparison equal/different/unknown; tests add concrete
  comparable/variant/material/mass cases preserving complete matcher inputs.
- G1-03: spec adds all state/resume/cancel outcomes, unchanged fixed limits/deadline,
  unknown retry within two total attempts, POSIX flock ownership/death recovery;
  tests add actual two-process rejection/reacquisition and invalid-state/limit cases.
Disposition: changes authored, independent rereview pending; no passage claimed.

## G1 rereview — 2026-10-16 — pass

Reviewer: `maintenance_reviewer`, separate from author. Read revised spec/tests,
research/plan/status and unchanged task mapping; no implementation or tests run.

| Artifact | Reviewed SHA-256 |
|---|---|
| spec.md | `521d43e25ccc3bde2dfb73099827b700b03be4e7b8c02bb8d3cc3e0ba80e8a95` |
| test-design.md | `2aa3ab228765476c6618ebacb9888daee4485c3a53353d1a2339ecd70d337828` |
| tasks.md | `66d7e40406d81a71c22b7750e5d15158247c0c1f8fe1b62758a02b8b8c895661` |
| research.md | `a5c1ea3f3d64dc4b9b8b77662fbdf3c204c66ab8cc85dfd79d413b97e524f5b1` |
| plan.md | `984d1893ac10560aece45f7468c7a4313860d204907435cadc83a8f7f2a8b687` |
| status.md | `e74ff397d033fe104d3ecaa06024ecc0f0daec45c25aa95e0f91890c8560f350` |

- **G1-01 / resolved:** Explicit supplied/captured modes distinguish caller
  assertions from observed support. Presence/default/null rules and separate
  identifier authority are stated; four baseline fixtures and live preconditions
  now match this distinction. The appended clarification governs the earlier
  shorthand observed-only comparison statement.
- **G1-02 / resolved:** Finite profile key/type/role/unit table, original-versus-
  normalized values and final matcher precedence are specified. Concrete hardware,
  footwear, material, size and mass expectations preserve the real matcher's full
  input and conservatism. Comparable material changes correctly remain review
  findings under existing identity conflicts; description corrections demonstrate
  the supported positive correction path.
- **G1-03 / resolved:** State/action table defines resume/cancel, immutable budgets,
  partial capture behavior, unknown retry accounting and the shared two-attempt cap.
  Local kernel-released ownership plus bounded two-process death/reacquisition
  checks addresses stale ownership without distributed worker expansion.

Verdict: **G1 pass; ready for skeleton and executable red acceptance tests**.
No blocking G1 findings remain. At G2 inspect explicit supplied-presence tracking
before Product/default reconstruction, supported supplier identifiers, per-physical-
request durable reservation hooks, cancellation while the runner owns its lock,
immutable goal/profile fingerprints and exact token/cost reservation boundaries.
These are implementation contract checks, not additional product decisions.
G2/G3 and all executable verification remain pending; G1 passage does not authorize
skipping skeleton/components gates or claim the epic implemented.

## G2 — 2026-10-16 — changes required

Reviewer: `maintenance_reviewer`. Inspected actual five Python skeleton files,
acceptance tests, skeleton/verification/status and approved G1 contracts. Existing
normalization/matcher code inspected to check fixture feasibility. Saved red log
confirms 27 collected intentional stub failures; reviewer did not rerun tests.

| Artifact | Reviewed SHA-256 |
|---|---|
| maintenance/__init__.py | `88ea96282d0c6cac5b7d3a5b8419c00aa2d39f0ba1ab2f832b823266c4c3c221` |
| maintenance/contracts.py | `10191202f87f7b96c7a138f837e2a4a912672e2760bae56d289384ee49e60e7e` |
| maintenance/engine.py | `440ffd4a13d8b85a21f37703900536cf1b688a875d4ed7b6fb49362ba8659a1c` |
| maintenance/profiles.py | `b5ae722ab004cd2756f9e31fb41ed7458ca12d6c1b286affeabe506e121ec12a` |
| maintenance/store.py | `51de3bad62d70a2478a4a0d645e28894752b2deae07031d66379894791a3a3b4` |
| test_maintenance_acceptance.py | `2be55edecfc37d1b0a72c1478e743272452b7bf04553080b20e3cde12fc53256` |
| skeleton.md | `40c2e84ea1bbde2ef62feb9af73480b8cc19fb211997a0ca36a131b4fd091b15` |
| verification.md | `1444daece25d835746e1a6ba7c9b67d970ef6011e38d020acc587797297efdee` |
| status.md | `b1ea8f01d6ee5e8230f5a256c0432a48e271ad798219b438951b59ec44f4a68d` |

1. **G2-01 / P1 / open — positive fixture contradicts the actual matcher.**
   `baseline()` submits external_id `p1` and sku `S1`, while supplier JSON-LD has
   sku `S1`. `_normalize_jsonld` derives external_id from `/sku`, hence `S1`.
   Both have the same supplier scope. `_classify_match` explicitly appends
   `supplier source ID differs` before considering equal GTIN evidence. Therefore
   positive correction/unchanged acceptance expectations cannot pass through the
   unmodified required matcher. Align baseline/supplier source identity and profile
   mapping, and assert the normalized real-parser fixture yields exact/non-review
   using the existing matcher as an explicit fixture precondition. Preserve a
   separate source-ID disagreement negative case. Rerun saved reds; fixing matching
   implementation or weakening expectations is not the remedy.

2. **G2-02 / P2 / open — investigator execution/reservation protocol is underspecified.**
   `bound(payload)` returns a model/price/token/cost promise, but
   `investigate(payload, timeout=...)` receives none of the accepted reservation.
   There is no declared result schema for usage versus unknown usage, model/price
   identity, advisory evidence and malformed output. Freeze this boundary before
   implementing settlement: bound must be local/no-spend, invocation must be bound
   to the accepted model/price/max-output reservation, and returned usage must
   distinguish known from unknown and be validated. Typed declarations or precise
   schema documentation suffice; this does not require a provider SDK. Add a
   meaningful red that observes a non-deterministic call receiving the reserved
   limits and cannot silently change model/price or exceed budget on a second call.
   Existing title-only test can pass even if advisor is never invoked, so does not
   exercise this seam. Remaining elaborate advisor fixtures can stay planned.

Other seams are usable for skeleton stage: no fabricated runtime success, explicit
errors, pre-deserialization presence tracking, durable intent layout, optional
physical per-dispatch hook, and narrow cancellation writes outside execution lock
are documented. Native transport hook is declaration only, appropriately pending
implementation. Custom profile registration is explicitly reserved for component
refinement. Remaining designed real-path/crash/budget/category cases remain required
before their behavior is implemented/verified; 27 red cases are not full coverage.

Verdict: **changes required before G2 passage**. No production implementation or
G3 passage is approved by this review.

### Author G2 dispositions submitted for rereview

maintenance_author, 2026-10-16; reviewer verdict remains unchanged.
- G2-01: baseline/profile ID now S1; shared native parser fixture is asserted exact
  by real classify_match before positive tests reach stubs; source-ID conflict
  negative precondition separately passes. No matcher edits.
- G2-02: accepted AdvisorReservation now passed into investigate; typed result and
  known/unknown usage/model/price contracts added; actual-invocation and unknown
  reservation/second-call blocking reds added. Custom profile constructor injection
  signature also frozen for later component review.
Rerun: 28 intentional stub failures, 1 passing real fixture precondition in 0.86 s.
Draft components.md prepared only; G3 not requested/passed before G2 rereview.

## G2 rereview — 2026-10-16 — pass

Reviewer: `maintenance_reviewer`. Inspected corrected code signatures, acceptance
fixture and saved 28-stub-failure/1-fixture-pass evidence. No tests rerun.

| Artifact | Reviewed SHA-256 |
|---|---|
| maintenance/__init__.py | `6878645a7f3323fce0f70d476e96802d635b38c0f858fd0dadc8ce24b28cf1a3` |
| maintenance/contracts.py | `4474ee94197f3cdf0212bb872021cb744eda525809fd0fff4c13ed1f5b050a27` |
| maintenance/engine.py | `3ae4204a35bee026aca30031a5c7ad1fbd3115cb9afb3f8a300a9e12e9b729b3` |
| maintenance/profiles.py | `b5ae722ab004cd2756f9e31fb41ed7458ca12d6c1b286affeabe506e121ec12a` |
| maintenance/store.py | `51de3bad62d70a2478a4a0d645e28894752b2deae07031d66379894791a3a3b4` |
| test_maintenance_acceptance.py | `d232827272f6d2da267c5cb94b075db7b6994c9befc3f13a6382dd2959009503` |
| skeleton.md | `9a6b8c3a90e9aef9e08f7939e0cea782ea0c37630a2c098362a2a4d076519246` |
| verification.md | `8799abaf4da9faf8d32d04a6f52a8c8b15a2f7115e93bfd903c26b700b806dc4` |
| status.md | `d2b33633b218c2ef8af2e67c37a08609c001aefe32dc94684c2351b185fbafde` |

- **G2-01 resolved:** baseline/profile key S1 matches actual native normalization;
  real parser/matcher precondition proves exact/non-review, and the source-ID
  disagreement negative case preserves the existing guard.
- **G2-02 resolved:** accepted immutable AdvisorReservation is passed to execution;
  AdvisorResult/AdvisorUsage distinguish model/price identity and known/unknown
  spend. Actual invocation and full retained reservation blocking a second call are
  asserted by a new intended red. Bound is explicitly local/no-spend.

Verdict: **G2 pass**, ready for component review. Neither runtime behavior nor full
SC01–18 coverage is claimed implemented; remaining designed fixtures are mandatory.

## G3 — 2026-10-16 — changes required

Reviewer: `maintenance_reviewer`, separate from component author. Reviewed
components.md SHA-256 `8697e22fe12a2fcc41787f07deaa6552cc92e1a3951127d4454781fb8a5ce286`
against approved G1 behavior, revised skeleton and the actual code digests in G2
rereview immediately above. No implementation or tests executed.

1. **G3-01 / P1 / open — custom profile validation/fingerprint owner lacks the registry.**
   Component model assigns validation/presence/fingerprinting to Store.create and
   recovery. Yet Store(path).create(goal) sees only profile names, while actual
   definitions exist solely in MaintenanceEngine(custom_profiles=...). Store.create
   must reject unknown profiles/unsupported fields and freeze exact profile content
   before execution. These signatures cannot safely accept a custom profile and
   fulfill that ownership contract. Give one authoritative registry to creation and
   recovery (for example store constructor configuration with frozen definitions
   persisted in each job), remove contradictory engine-only ownership, and declare
   how reopening with missing/changed definitions behaves before any dispatch.
   Add intended reds for custom-profile create/persistence and changed-definition
   resume rejection. No new profile framework/provider infrastructure is needed.

Existing codec/resolver/matcher/security reuse is coherent; Store/Engine ledger and
cache responsibilities avoid an unnecessary second generic job framework. Physical
HTTP accounting and cancellation control ownership are correctly separated in the
component declaration. The new custom registry lifecycle is the remaining blocking
component seam, not a requirement to implement business behavior during skeleton.

Verdict: **G3 changes required**. Production implementation remains gated on G3.

### Author G3-01 disposition submitted for rereview

maintenance_author, 2026-10-16. Store constructor now owns sole custom profile
registry; engine-only injection removed. Frozen definitions/digest persisted at
create, status inspection independent of active registry, dispatch compatibility
check and missing/changed profile_mismatch contract declared. Added intended reds
for frozen persistence and changed/missing registry zero-dispatch resume. No business
implementation. G3 reviewer verdict remains changes required pending rereview.

## G3 rereview — 2026-10-16 — pass

Reviewer: `maintenance_reviewer`, separate from author. Reviewed actual changed
Store/Engine signatures, component/skeleton refinements, three new executable reds,
and saved 31 intentional stub failures / 1 real-parser fixture pass. No tests rerun.

| Artifact | Reviewed SHA-256 |
|---|---|
| maintenance/store.py | `78479e13ead92d61d04ac4f15850866e3a69d0a5ea605444347322163d23e7b2` |
| maintenance/engine.py | `440ffd4a13d8b85a21f37703900536cf1b688a875d4ed7b6fb49362ba8659a1c` |
| test_maintenance_acceptance.py | `96369825a3e8cdf0707e90d0e25e5500810ad82b10b870a1ae4419f79372445b` |
| components.md | `b840d67de981b9768ffe25603993f0e85b72c12b47522796117c4c1fdf875e1f` |
| skeleton.md | `668876cad4aca52f819a813ca0de7e4efac7bcd26f25450116e34261eedebdb0` |
| verification.md | `07eb394284672106876f6a4d77daf9e34aa480c0def1933b69b9f74063f98eb3` |
| status.md | `57a2251d8ffab278acd9a57e5934f76e010643bf380745d35ca39c0240c44f0b` |

**G3-01 resolved:** Store is the sole trusted profile registry owner; Engine has no
second configuration. Creation validates/fixes canonical selected definitions in
the durable goal. New tests require mutation-resistant snapshots, inspection after
reopen without active config, and zero-dispatch `profile_mismatch` for changed or
missing active definitions. This gives creation, recovery and cache fingerprinting
one compatible lifecycle. Existing historical reads remain available.

Verdict: **G3 pass**, with affected skeleton refinement reviewed here. No blocking
design findings remain. Proceed with bounded implementation slices against saved
reds and approved FR/SC contracts. Production implementation, remaining acceptance
fixtures, offline mechanism/stress checks, bounded live checks and final independent
review remain required; these gate passages are not feature-completion evidence.

## Interim A/B/C source, FR05 refinement and live-plan review — 2026-10-16

Reviewer: `maintenance_reviewer`, independent of author. This is NOT final review.
Bounded read of maintenance source, context/security accounting hooks, four feature
test files and components/test-design/verification/status. No tests repeated, live
requests, inference or agents launched. Exact 14-artifact SHA-256 manifest saved as
`artifacts/catalog-maintenance-agent/interim-review-sha256.txt`; manifest SHA-256:
`fae185cf37bf36957b8f8b8ecbbe6b46a9439538f278b9e3d0c248fae234dbb7`.

### Blocking source findings (one diagnosed repair and focused evidence each)

- **I-01 / P1 / open — candidate truncation can manufacture uniqueness.**
  `_collect` slices supplier records to product budget before `match_products`.
  Two distinct captures with same SKU/GTIN but different descriptions are both
  exact candidates through the real matcher; products=1 hides one and permits a
  correction instead of ambiguity. Preserve ambiguity from all already captured
  records or fail closed when truncated, without weakening matcher or expanding
  resource limits. Predesign native two-product fixture: first alone exact, both
  ambiguous, budget1 never proposed_correction; reverse order same safety result.
- **I-02 / P1 / open — zero product budget still discovers.**
  `_collect` calls sitemap discovery before checking products==0. Move zero-cap
  guard before any source step. Distinct red: no product URLs, products=0, positive
  request allowance -> zero physical calls, partial/product_budget and no findings.
- **I-03 / P1 / open — unknown/violation job state is not durable.**
  `run` resets `_model_stop`; committed comparison steps skip `_advise`. A repeated
  resume can therefore mark completed despite unresolved unknown advisor attempts.
  Likewise an overrun halt is only runtime state. Derive unresolved/violating model
  state from persisted attempts/results before completion or model dispatch.
  Predesign repeated resume after unknown usage/timeout/crash: no replay, retained
  charge, partial until explicit retry or declared unresolved disposition. Known
  overrun remains a model-dispatch halt after reopening with pending comparisons
  and otherwise ample budget; no reservation refund or new call.

### FR05 advisory retry refinement — approved contract, implementation pending

Immutable base finding plus separate immutable advisory attempt results is approved
as the limited affected G1/G2/G3 refinement, with these exact constraints:

1. Retain stable base ID/status/before/after/match/evidence; report composes latest
   committed advisory by durable attempt order, never a pending/uncommitted result.
   Prior advisory results, unknown attempts and charged spend remain inspectable.
2. Explicit retry only from paused/partial, with unknown attempt and total attempts
   below2. Resume alone never retries. Revalidate cancellation, fixed deadline,
   remaining token/cost allowance, profile/security and original payload/evidence/
   bound/model/price identity before dispatch. Changed semantics require new job;
   no fresh prompt/model authority or cache shortcut hides an unknown retry charge.
3. Commit advisory result, usage settlement, associated step/checkpoint and report
   publication atomically; cancellation or persistence/report/evidence-cap failure
   leaves previous composed report intact and uncertain reservation charged.
   Composed advisory bytes and retained attempt results obey existing resource caps.
4. Resolve I-03 using durable outcomes. Successful second attempt may resolve the
   finding's unknown outcome, but prior unknown spend remains charged. A second
   unknown result remains partial; attempt3 rejects retry_exhausted. Violations
   halt further model work durably and cannot be bypassed by explicit retry.

The existing saved FR05 red must pass; first add distinct intended reds for attempt2
unknown/attempt3 denial, cancelled/deadline/budget/profile retry refusal, failed
advisory publication preserving prior composition, and stable pagination after
advisory retry. These target different failure paths, not alternate random inputs.
No FR05 waiver and no final behavior pass is granted.

### Bliss live amendment — source accepted, executable limits changes required

Saved #24 native evidence supports Bliss as the replacement source. Explicit
generic profile and separation of live unchanged observations from synthetic
category/change proof are appropriate. Before execution fix two plan/API mismatches:
engine source retries are currently hardcoded up to2, with no no-retry option;
either declare those bounded attempts inside the three-physical-request phase cap
or provide reviewed opt-out. Also set runtime `Limits.item_count=2` explicitly:
maintenance otherwise asks for products+1 and can capture3 despite plan <=2.
Keep same origin, phase/combined request/deadline/byte caps, zero LLM, first smoke
saved before second phase and stop conditions. Verdict: **amendment changes
required before live execution**, solely for executable retry/item limits.

### Remaining required D coverage and overall verdict

Do not treat current passing subsets as full SC01–18 proof. Required D includes the
designed 100 mixed/100 exact batches with enabled eligible-only advisor assertions;
all budget boundaries including evidence/report rollback; real-engine crash windows
and mutation sensitivity; partial-source+resume and expiry during pause; captured
outdated/unsupported baseline cases; custom color-role, size-system/unit and escaped
field cases; cache policy/version/corruption interactions; cancellation/commit and
unknown retry interactions. Use reviewed fixed seeds/counts/time/RSS limits, actual
code paths and a first saved smoke. Existing still-applicable focused results may
be reused; execute gaps rather than repeat passing suites. Save commands and distinct
mechanism/stress/live outcomes and independent coverage assessment.

Overall: **interim changes required** for I-01..03 and live plan corrections;
FR05 refinement approved as specified, implementation and evidence pending.
Final independent gate remains pending after D/offline/live/docs completion.

## Interim repair rereview / live approval / D expectation review — 2026-10-16

Reviewer: `maintenance_reviewer`. Read changed collection/advisory retry/store
publication/stop mechanisms, new regressions and saved 86-feature-pass evidence;
no suite repetition or live execution. Exact eight-artifact manifest:
`artifacts/catalog-maintenance-agent/interim-rereview-sha256.txt`, SHA-256
`b0a69ceec269a71932753b6dc3dc8a82c404dccf0e0e862bd85a0819a1009de7`.

**I-01 resolved:** all already captured distinct supplier candidates reach real
matching before scope reporting; both ambiguity orders have explicit regression.
**I-02 resolved:** zero-product guard precedes discovery; zero-send regression.
**I-03 resolved:** Store derives model unknown/violation from durable latest attempts;
repeated reopen/resume retains partial/charge and no replay, and violations veto
new advice. FR05 now has immutable advisory histories, original payload/bound/model/
price/profile/policy guards, two-attempt cap and atomic capped composition. Reviewed
new cap/cancel/unknown/registry tests; saved passing evidence has no exclusions.

**I-04 / P1 / open — successful advisor retry loses source state and coverage.**
`_retry_advisor` finishes completed whenever model_stop clears, without checking
source completeness or independent pending steps. It calls Store.finish with no
coverage, which overwrites persisted coverage with `{}`. A source_partial or
product-budget job can therefore become completed solely because its advisory
retry succeeded, losing required coverage counts. Preserve coverage and derive final
status from all durable workflow outcomes, not only model state. Add distinct red:
real native partial capture + unknown advice -> successful explicit retry updates
advice/retains old charge but stays partial/source_partial with original coverage;
unfinished independent source/comparison steps likewise prevent completed. One
focused repair/check is needed before D expansion. Existing stable base/history
tests remain unchanged and must continue passing.

### Executable Bliss amendment — approved

Corrected plan explicitly sets item_count2, request3/phase, 2 MiB, attempt10s,
deadline30s/phase and at most2 logical attempts within physical limits. Combined
6 requests/2 products/60s, same origin, zero LLM, sequential first saved smoke,
stop-on-error and honest partial catalog scope are consistent with actual APIs.
Verdict: **live plan approved**, execute only after required offline D checks pass.
This is plan approval, not live evidence or an authorization to expand domains.

### D generator expected outcomes — approved, execution still pending

Approved SC01–18 fixture expectations and frozen seed25/count/time/RSS/byte limits
remain in test-design.md. Build real native multi-product smoke before the 100 mixed
80/15/5 batch and 100 exact batch; enabled advisor can reach only the5 ambiguous
cases, disabled/exact batches zero calls. Generate only controlled external boundary
responses; production parser/matcher/resolver/store/ledger/report must run unchanged.
Reuse saved valid retry/cancel/ownership cases where their exact boundaries match.

Execute outstanding exact families rather than declaring86 tests complete coverage:
20 crash/replay cycles at reviewed windows; 18 resource edges; 8 original pairwise
and8 category interactions; mutation sensitivity; captured outdated/unsupported
before-values; malformed/escaped keys; partial+resume/expiry; report/evidence cap
rollback; cache policy/version/corruption; footwear size-system and custom color-role.
Each has predeclared FR/SC outcomes in the approved design. Add I-04's exact partial
retry/coverage expectation before its repair. Save smallest failure, one diagnosed
repair, focused rerun; do not weaken assertions or broaden180s driver after failure
without recorded diagnosis and reviewed limit update. Actual execution/runtime
traces and independent D coverage assessment remain required before live expansion.

Overall: I-01..03 resolved; live and D expectations approved. **Interim changes
required solely for I-04** before D execution. No final gate or epic completion.

## I-04/R01 focused confirmation — 2026-10-16 — pass

Reviewer: `maintenance_reviewer`. Read only shared Store.completion, finish coverage
preservation, both Engine completion consumers, three new predesigned regression
cases and saved red/green log. Actual reviewed SHA-256:

| Artifact | SHA-256 |
|---|---|
| maintenance/store.py | `4dedee2b756310fbee0a8c26090b082fe0849bf1c73d0b673b0be5780a82c8b0` |
| maintenance/engine.py | `9a0419664a5e59f1fc10296c6ebe3c29373a6bf0f0ee9c37c1d832d9ed30fb24` |
| test_maintenance_review_repairs.py | `24b1a82156acb69a0b63a5ee0df7a47d44e7162307e473674ebba99bef941322` |

**I-04 resolved:** normal run and explicit advisor retry share durable source/
pending-work/model completion evaluation; finish(None) retains prior coverage.
Native partial capture stays partial/source_partial after successful retry, with
old reservation and coverage retained; pending independent source and compare work
also prevent completed. Saved evidence is3 intended reds ->6 focused passes/8.26s,
including existing stable retry/publication/attempt-ceiling invariants. Reviewer
did not rerun tests; no unrelated source sweep or broad test repetition.

Verdict: **focused repair pass; no open interim blockers**. Proceed with D fixture/
generator implementation and bounded execution under already approved SC01–18,
fixed counts/seed/resource/stop limits and required gap inventory. Existing still-
applicable passing evidence may be reused. Corrected Bliss live plan remains
approved but execution follows required offline D success and coverage review.
Do not waive any designed FR/SC, substitute mocks for mechanisms, or claim final
completion from this repair gate. Independent D coverage review and final gate
remain pending.

## D timeout amendment / matching optimization review — 2026-10-16

Reviewer: `maintenance_reviewer`. Read bounded stress driver, changed matching
materialization, both saved timeout receipts and proposed limit update. No tests,
models or live requests run. Exact six-artifact manifest:
`artifacts/catalog-maintenance-agent/stress-amendment-review-sha256.txt`, SHA-256
`9f302cdb5e6d830f1492731462d7a457455964c9af896096497f5654db3c63b2`.

Both original failures remain failures: cooperative5s timeout produced observed
10.716s and9.516s wall time; neither demonstrates a hard5s enforcement. Both native
3-item smokes remain saved successful evidence; do not repeat or erase them.

**Limit amendment approved with executable enforcement:** only the3 100-item cases
may use15s rather than5s. Small cases5s/crash10s, sequential worker1, global180s,
RSS/input/evidence limits and stop-first-failure remain. Run each remaining case in
its own process group, supervised externally rather than the event loop doing the
work. Per-case allocation is min(case cap, global remaining); global monotonic clock
includes startup, serialization, persistence and cleanup. Terminate the whole group
at its deadline, kill/reap grace <=1s measured separately, save timeout versus cleanup
wall time distinctly. No child launches if remaining global time is exhausted.
One tiny controlled hung worker/descendant probe must demonstrate external group
termination and no survivor before stress resumes; no model process is needed.
Log self/descendant RSS metric honestly rather than relabelling old parent-only RSS
as aggregate memory. No second performance optimization or broader sweep approved.

**Dictionary optimization contract approved; executable equivalence required first.**
Existing matcher already asdict-converts Product input per pair; preconverting the
complete record once retains every matcher field. Own report support continues
through original Product/resolver/evidence objects. Before stress, execute bounded
native-parsed positive, source-ID conflict, RAM/variant conflict and duplicate-exact
ambiguity cases with object and full-dict inputs. Compare relation, needs_review,
confidence, evidence strings, conflicts, indices and candidate_method exactly.
Document field_support as intentionally absent for dictionary matcher inputs;
separately assert maintenance report's captured source URL/time/IDs and retrieved
retained evidence still match real parsed support. Do not remove fields or alter
public matching behavior. Save small equivalence result before any100-item batch.

**D-01 / P1 / generator fixture repair required before execution:**
`checkpoint_reuse` creates a fully completed job. Engine.resume returns at
Store.begin(False), so `_source` is never reached and the checkpoint mutant cannot
possibly be detected. Replace with a real interrupted workflow after source
checkpoint but before job completion (existing after_checkpoint crash hook), then
reopen with expired cache. Control must revisit and skip committed `_source` with
zero requests; temporary mutant must actually reset that checkpoint, perform a
request and trip the no-repeat assertion. Record mutation reached/detected/restored;
restore in finally. This fixes test mechanism feasibility, not production behavior
or a second optimization. Predesigned counts/expected invariants are unchanged.

Resume only unfinished cases after these small prerequisite checks; cite saved
smoke receipts and keep old failed runs separate. Overall amendment approved as
specified; equivalence/enforcement probe and D-01 fixture correction are mandatory
prerequisites. Full D proof, live execution and final independent gate remain pending.

## D coverage evidence / bounded offline continuation plan — 2026-10-16

Reviewer: `maintenance_reviewer`. No tests or live requests executed. Exact eight-
artifact digest manifest: `artifacts/catalog-maintenance-agent/offline-continuation-review-sha256.txt`,
SHA-256 `286f4ae6013ecf4667e704efee519220458cde6656f71c291c838fffebc3a319`.

D receipt review confirms47 new passes+12 cited still-applicable proofs, alongside
2 retained failed workers. Authoritative corrected cumulative charge172.427229/180s
includes original timeouts/startup reserves; max workerRSS170.49MiB. Do not use the
older142.814s subtotal as total. Three100-item batches, crash/replay/budget/interaction
and mutation families have saved receipts; repeat none without a new failure/change.
Two additional actual engine os._exit windows are distinct offline proof (2passed,
5.798s), honestly separate from the stress-driver budget, not live observations.

Reviewed unique identifier-anchor context selection: it does not change matcher
relation/conflicts/needs_review, and duplicate anchors remain ambiguous. Context only
provides before/after/evidence for a review finding; exact authorization still uses
the unchanged matcher plus support checks. Saved equivalence, report support and
106 maintenance tests provide current affected-path coverage. Complete the final
FR/SC evidence matrix linking exact nodes/receipts (including12 reuse citations),
remaining-edge and OS-death checks before final review. Current evidence does not
replace whole-repository verification or the final independent gate.

### Suffix-only offline continuation — approved

One timed-out240.032s suite confirms783 passes through strict quiet-line mapping;
140 collected nodes remain unconfirmed. Next node may have been inflight or not
started; do not assert which. Source identity matches all20 saved entries. Run ONLY
the saved140-node suffix, in recorded order, under ONE externally supervised240s
aggregate deadline including startup/cleanup; stop on first failure/timeout. Isolate
the first heavy existing seeded node with <=60s process-group guard, then run the
remaining139 with the lesser of180s or aggregate remaining time. Record start/end/
node outcomes verbosely enough to avoid another ambiguous suffix; zero overlapping
workers. No repetition of the783 confirmed nodes. If first node fails/times out,
save exact evidence and stop rather than rerun or edit that unrelated test.

Keep `tests/test_reliable_changes_stress.py` and unrelated53ab96c history unchanged.
It is an existing #23 workload, not new #25 behavior. The timeout alone establishes
no regression. Union783 saved passes with140 new confirmed passes only if source
identity stays unchanged and every unique collected node is covered; report this
as complete coverage across bounded runs, not one successful monolithic run.

### Same-job CI partition — approved scoped change

Keep Python3.10/3.11/3.12 matrix, job count and existing parallelism unchanged. Two
sequential steps may partition existing817 versus maintenance106 nodes, each with
240s timeout and recorded failure status. This isolates additive #25 verification
time while preserving all existing checks, including the unrelated heavy #23 test.
Use exact current maintenance-file lists and complementary ignores; independently
verify disjoint/complete node sets. Do not drop/modify tests or claim either partition
fits240s until actual CI proves it. This increases aggregate allowed job test time
to480s; it does not parallelize work or silently enlarge any individual timeout.
Local continuation remains suffix-only; CI partition does not authorize rerunning
all completed local nodes or rewriting unrelated history.

Plan verdict: **approved bounded suffix continuation and scoped CI partition**.
After all offline nodes are confirmed and no blocking result remains, proceed with
the already approved Bliss plan (<=3 requests/phase, <=6 combined, item_count2,
<=60s combined, zero LLM). Missing build/hatchling remains an explicit unverified
wheel limitation; no install/release is implied. Final FR/SC matrix, actual live
evidence, source review and independent final verdict remain required.

## FINAL independent gate — 2026-10-16 — pass for local implementation handoff

Reviewer: `maintenance_reviewer`, independent of implementation author. Reviewed
current source/contracts and prior resolved source findings, actual tracked adapter/
README/CI diff, API/CLI/example docs, FR01–12/SC01–18 coverage map, completed suffix,
stress/reuse/OS-death and live receipts. No test suite/model/network rerun.
Independently recalculated all32 hashes in final-source-manifest: no mismatch.
Original20 source/test/API/doc entries remain unchanged across prefix/suffix/live;
approved CI partition is the only tracked verification-policy change. Unrelated
preexisting specs004 dirt/untracked artifacts and prior #23 test/history remain
outside this feature's edits/delivery scope.

| Reviewed artifact | SHA-256 |
|---|---|
| final-source-manifest.json (32 entries) | `935ee36d85eb39c2d52c4abdf928eea7764a530845554bfef497387ed60b8f62` |
| author-final-digest.json | `bb50902f661563f384f000430005866327b784c87465e06569ed5dcd8473695f` |
| coverage.md | `61b4e77acd9bea102d64290d812930386c27543c6f24a1d38d393653fc253fe4` |
| .github/workflows/test.yml | `5bd32cf2aabea92e2f186d83e50911093923840167748e7eca95c959366e0532` |
| docs/catalog-maintenance.md | `c6523a24c03eb1683cdfe9c0e18982644af7ce78702cb0aa9e258a63fb61e5b6` |
| maintenance/engine.py | `17b994ba1b8eb2b4dee47f2b9c82fa17c53881d90ceec11c91461a5fc7a40d3a` |
| maintenance/store.py | `12df64016b08d6e8a0ff885447f5f86f6edc1be6e0954f7a91ccc74ec6da7251` |

### Final findings and evidence disposition

No blocking findings remain. Prior G1/G2/G3, I-01..04 and D-01 dispositions are
resolved with actual reviewed contracts and executable evidence. Category-specific
roles/units and review context preserve full matcher conflicts and duplicate-anchor
ambiguity. Supplied assertions remain labelled separately from captured facts.
Optional investigation is narrow/advisory; deterministic cases zero model calls.
Physical source reservations, retained unknown spend, bounded explicit retries,
immutable advisory history/composition and durable violation halt are implemented
and exercised. Conditional remote-spend guarantees and POSIX/local ownership limits
are clearly documented; no paid service gate or downstream writes introduced.

- **Repository coverage accepted:** independently checked923 unique ordered nodes,
  exact suffix equality to nodes784–923,783 recorded prefix passes plus seed1passed
  and remaining139passed in saved logs. All923 distinct nodes have passing evidence
  on unchanged source; suffix64.777606s/240. The original monolithic240.032s timeout
  remains a timeout, not a fabricated whole-command pass. No hidden exclusions.
- **CI partition accepted:** seven explicit maintenance files cover106 nodes;
  complementary existing817 remain. Same3-version matrix/job, sequential240s each,
  aggregate480s disclosed. Actual remote CI has not run; no CI-green claim.
- **D coverage accepted:**47 new passes+12 exact reuse proofs, corrected cumulative
 172.427229s/180 including historical failures/startup reserves, maxRSS170.49MiB.
  Mutation detectors reach real mechanisms and restore changes. Separate2 actual
  OS-death cases passed5.798s; they are not relabelled stress-budget or live proof.
  FR/SC map and remaining-edge fixtures cover the designed distinct gaps.
- **Required live integration accepted:** actual approved Bliss source,4/6 physical
  requests,2 supported unchanged title findings,2-item partial/source_partial scope,
  preserved evidence, restart0HTTP, zero model tokens/cost,18.440964s inner/
 19.941616s outer. Phase1 saved before phase2; no domain/budget expansion. Actual
  commercial specification change remains inconclusive; synthetic correction proof
  is separately identified and not claimed as an observed merchant change.
- **Operating evidence accepted:** compile, CLI/help/create/status and runnable
  offline example passed; existing APIs/default schemas retained. Wheel build is
  **unverified** because local build/hatchling are absent. This is an environment
  limitation, not a successful package/release build; no installation required.

Verdict: **FINAL PASS — local implementation/evidence handoff ready**. No required
local implementation or designed mechanism/live check remains outstanding. Preserve
documented limits: wheel unbuilt, remote CI unobserved, no concrete remote provider
integration, real commercial-change observation inconclusive, session token counters
unavailable. No publication, commit, push, PR, issue closure or release is implied
or requested by this verdict. Coordinator may update current status/tasks to the
actual final gate result; evidence/source identities above anchor this review.

### Author interim dispositions submitted for independent rereview

maintenance_author, 2026-10-16. Reviewer verdict above remains changes required.
- I-01: preserve all captured supplier candidates before matcher, mark cap scope
  partial; forward/reverse native duplicate-identity reds now pass.
- I-02: zero-product check precedes discovery; zero-send red now passes.
- I-03: completion/model dispatch derive durable attempt/publication outcome;
  repeated unknown/violation reopen reds now pass.
- Approved FR05 refinement implemented with immutable base findings, separate
  immutable advisory publications, original bound/payload/profile/policy identity,
  atomic cap/settlement/publication and explicit attempt2 only. Required retry,
  attempt3 denial, refusal, cap rollback, cancellation and pagination cases saved.
- Live plan explicitly sets item_count2/request3 and declares up-to2 logical source
  attempts within same physical cap; no live request executed.
Targeted repair results and remaining D gaps are recorded in verification/status.
No author verdict or final feature completion claimed.

### Author I-04 / R01 disposition for confirmation

maintenance_author, 2026-10-16. Shared durable completion evaluates source partiality,
uncommitted independent source/comparison steps and model state; regular run and
advisor retry use the same path. finish preserves prior coverage unless explicitly
replaced. Real native partial source + unknown advisor + successful retry stays
partial/source_partial with unchanged coverage and retained charge; pending source/
compare also prevents completed.3 observed reds ->6 targeted greens/8.26 s including
prior stable finding/publication/retry ceiling cases. Digests in verification.md.
Reviewer verdict unchanged; D execution awaits confirmation.
