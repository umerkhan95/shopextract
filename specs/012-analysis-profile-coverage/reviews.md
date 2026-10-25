# Independent planning review — G1

Date: 2026-10-25. Reviewer: /root/profile_plan_reviewer. Authors: /root and /root/profile_plan_author. Sequential bounded source/document review; no tests, network, inference or production edits. Reviewed local workflow/constitution and seven planning documents; targeted source checks: maintenance/store.py (_validated, validate_profiles, report), maintenance/engine.py (_compare), categories/maintenance.py, maintenance/__main__.py and _cli_data.py.

## Findings and dispositions

| ID | Severity | Finding | Disposition |
| --- | --- | --- | --- |
| G1-01 | Medium | An absent selected-profile rule is rejected at goal admission today; an unconditional runtime review-only fixture could silently weaken compatibility or never reach the intended path. | Repaired test-design/tasks/research: preserve invalid_argument for new goals; use a labelled persisted legacy/corrupt-state fixture for the defensive real-engine guard with strong identity and observed support. Closed. |
| G1-02 | Medium | Existing 1 MiB maintenance CLI output protection was incorrectly implied. Maintenance __main__ prints unrestricted JSON; portable/category paths have separate limits. Concrete paging/output boundaries were missing. | Corrected spec/plan/research: new diagnostics-enabled serialized-output cap, legacy output unchanged without diagnostics. Added 0/1/999/1000/1001 limits, default/nonzero-offset pages, and below/at/above byte boundaries including UTF-8 envelope/newline; reject before partial output/replacement. Closed. |
| G1-03 | Low | Full-registry snapshot concern was left as an audit despite locally observable implementation. | Recorded that snapshots contain selected definitions and validation compares retained entries. Added prior-registry job → expanded-registry replay and changed-selected-definition rejection cases. Original snapshots stay immutable. Closed. |

Review checks: FR01–FR09 and SC01–SC11 trace to sequential tasks and explicit evidence. Whole-market count remains honestly unknown; reviewed families are distinct from taxonomy leaves/platforms and selected-field coverage. Explicit selection remains default. Physical units require source-backed total-volume/product-dimension semantic context; numerical parse alone cannot authorize meaning. Immutable persisted normalization identifiers, additive Python/schema allowlists, custom-profile compatibility, collision and replay checks are specified; exact spellings/carrier/enums remain legitimate G2 interface work. Extraction uses actual capture/support/store paths, not taxonomy metadata or hand-filled attribute-only proofs. Six-adapter synthetic evidence is separated from bounded required live capture. Deterministic smoke-first, real-mechanism, fault/retry and assertion-sensitivity plans have finite limits and independent fixture review. Report diagnostics distinguish configured/requested/checked/unavailable states.

The 48-case manifest is a future reviewed deliverable, not a completed stress result. Runtime admission/defensive tests and pagination/byte boundaries must be included in appropriate focused suites; the manifest's fixed count must not silently omit them. Implementation-informed material changes repeat pilot G1. G2 must freeze serialization and diagnostic cap behavior before code; this review does not approve nonexistent implementations.

Verdict: **PASS for the requested planning endpoint**, after the documented repairs and review of the resulting artifact digests below. No unresolved G1 blockers. G2/G3, executable red/green/full-driver, mechanism/stress, live and final runtime reviews remain pending. APC02 complete; all implementation tickets remain pending.

## Reviewed resulting SHA-256 digests

| Artifact | SHA-256 |
| --- | --- |
| spec.md | `22c31791ee620b31fb43f48b1ecbd4476b3a1edc7e25b874a36bd27d46aeb457` |
| test-design.md | `f668a5bc6690c1a0ff914c1cce27a442d49e3626f8cdf54f1e04dd29ef567af3` |
| tasks.md | `7e1c9f4779ca32366ebfcfc589278f4414118256d8e3e118e6e59c8978ad5c7f` |
| research.md | `2c21693c65ca777058dc5ce323777dbc3fdaab61f14310659b68ab08189c95fd` |
| plan.md | `9812b6b9dfca0bc315023fabfa344de8790e7b913b85a5b6c66db6c2d8300746` |
| status.md | `edff26f16e505236bd6ae2833f1f604f53befba3ea3bcfd7876d482134cf9846` |
| verification.md | `e442eb56fc5356cf2bd00989715feebc87e5910fb993df1e0e1e5f44434adebc` |


# Inventory G2/G3 — 2026-10-25

Independent reviewer: /root; author: /root/coverage_author. G2 initial finding APC-G2-01: default tests depended on untracked retained sources absent from fresh checkout. Resolved by small synthetic schema-valid source fixtures (only pin configuration substituted), static immutable real-pin assertion and separate mandatory real-corpus acceptance driver. No algorithm mocked; source hashes/parsing/selection/order remain real paths. Added empty/duplicate scope, missing file, malformed YAML, duplicate ID and dangling child cases. Saved red13 intended failures/4 baselines reviewed.

G2 verdict PASS: interfaces/errors/source identity, bounds and honest review-pending distinctions match FR01/02/09 and SC01/02/11. G3 verdict PASS on the component contract immediately following G2: reuse profile definitions and existing runtime validator; one offline inventory owner; no runtime auto-import, new framework, source download or policy-selection behavior. Components draft is approved unchanged in behavior and may be marked finalized. Pilot interfaces and runtime gates remain pending.

Reviewed artifact SHA-256:
- `specs/012-analysis-profile-coverage/skeleton.md`: `adfa2edb8b6bf61bc0120ad668dca2a343fcab17eda0fe4ee1cc90ac2a35df08`
- `specs/012-analysis-profile-coverage/components.md`: `f3e31869ef7f61226e168d06c6b11a28e9dc0a62d7e9df8561c0f46c1f1f109c`
- `src/shopextract/maintenance/inventory.py`: `04c1beca9493925dfd260450fb4e3a5945befad54d7e82070aa6420ce576f236`
- `tests/test_profile_coverage_inventory.py`: `2742f6f61e3091bf62169099c1f9f1cc753e1a350dc68f115257ac1ac30152fb`
- `specs/012-analysis-profile-coverage/evidence/retained_inventory_acceptance.py`: `0976eb7f179caa48e94ffc2a2c86da71c43ebdc939ddf16e0356a24488c6470d`


# Inventory final review APC06 — PASS,2026-10-25

Independent reviewer /root reviewed implemented real hash/parser/graph/selection/profile projection paths and final20 focused cases. Selection iterables consume at most4 branch names/5001 IDs; source bytes8MiB/nodes5000/report8MiB caps retained. Distinct disconnected-cycle and unresolved-attribute cases complement duplicate/dangling/changed-source tests. Real retained-corpus gate passed74.148s with5 verified hashes and smoke saved before full4125 rows/order replay. No runtime registry import, captured product claim or exact remaining-family count. Original baseline matrix retained.

Configured full driver first failed an unrelated preexisting resolver startup readiness window (test_tool_mechanisms::test_repeated_process_cancel_no_accumulation), with process group cleaned. Isolated diagnostic passed5.23s; one bounded full retry passed ALL1690 tests,zero skips/failures,376.140763s:1560 main+24 oracle+106 maintenance. No source/assertion changes for transient readiness failure. Both runs retained. Inventory live N/A because offline reference metadata. APC06 PASS; pilot source/support/profile/report G1/G2/G3/runtime/live/final gates remain pending.

Reviewed SHA256:
- `src/shopextract/maintenance/inventory.py`: `2ad18258574633ae65f9fd4729a180528aa4cd3f3962ea778fc81e66149cfe90`
- `tests/test_profile_coverage_inventory.py`: `3c2a664e32901940a4646300c25b0e6a91fcfc9fe20673aaa04ac37f069c1686`
- `specs/012-analysis-profile-coverage/coverage-summary.md`: `602884e1c8b715b214162fb6cfd5ad2524b6b633911d8b6d07fceaa7ac8c2da3`
- `specs/012-analysis-profile-coverage/evidence/coverage-matrix.json`: `0b6f66fba8626d62d430cfa612028905eaf784e71ecaada52fce2b814df7400e`


# Refreshed refrigerator G1 APC08 — PASS,2026-10-25

Reviewer /root; author /root/coverage_author. Reviewed actual six-lane controlled capture/normalize/portable/SQLite/reopen/_supported audit and honest failed wrapper portability probe. Generic SchemaOrg projection is the demonstrated extraction gap; five native adapters remain unavailable, not fabricated parity. Typed carrier requires additive codec/schema work proven red before implementation.

Finding APC-PG1-01 (blocking) CLOSED: initial string-only/exact-semantic-enum transport contradicted real unknown-value/semantic engine scenarios. Revised closed wrapper allows JSON-finite scalars and bounded semantic strings; comparator enforces meaning, preserving0/false/null/net/gross/packaging as unknown/review-only. Numeric nonfinite and malformed nested/extra-key transport remain rejected. Planned real-path tests updated; no whole-job failure substitution for comparison behavior.

Accepted9 fields/no weight, immutable axis normalization IDs/exact arithmetic, defaultFalse opt-in propagation/cache version, old3 definitions/constructor/default-output preservation, mandatory fridge policy/exact binding/wrong-category veto, absent-rule guard/admission compatibility, selected snapshots, derived finding-page diagnostics and bounded SQL paging without new table. Actual envelope UTF8 cap/newline preflight preserves one error envelope; no nonexistent report-file API. Current-policy inventory overlay preserves dated baseline, explicit selected-field/incomplete-family coverage. Concrete live target remains prerequisite, bounded discovery/requests and no fabricated observation.48-case manifest is design only; APC14 still needs executable realism/coverage review.

G1 PASS after repair. No business implementation/stub approval until executable reds + G2 + component G3.

Reviewed SHA256:
- `specs/012-analysis-profile-coverage/pilot-contracts.md`: `17886f86f8da20ab9ba7a13b6d38e88f970458796dba52aef863c842d59932ff`
- `specs/012-analysis-profile-coverage/test-design.md`: `b97ea6a3f33e952e5d24b8eb89669ced34f4afe6335b5ac5a5ce7222754e9238`
- `specs/012-analysis-profile-coverage/research.md`: `bb273fbc08e3928ce78d0f9cfe0a86cf71ac1ccf5f9b8cdced32f9d5a1ba48ac`
- `specs/012-analysis-profile-coverage/evidence/pilot-case-manifest.json`: `c26bb000749153870c41cf3cdc65a1abe5fc7ee01916c20b3991d9af53f0bbe7`


# Refrigerator pilot G2 then G3 — PASS, 2026-10-25

Independent reviewer /root reviewed the authored 77-case acceptance checkpoint,
helper and exact skeleton interfaces before pilot production changes. Tests use
actual SchemaOrg parsing, capture/support, portable round trips, SQLite snapshots,
real matcher/reconciliation, source runtime and both CLI boundaries. Corrupt-state
missing-rule fixture reaches the defensive guard while public admission remains
strict. Raw state tests explicitly prevent unsupported candidates becoming
comparison authority. Baseline old-profile output is exact. Quantity byte limits
count finite UTF8 actual envelope plus newline. Intended interface failures are
recorded as reds, not deeper guard proof.

G2 PASS: frozen nine-field profile, quantity reason/state contracts, additive
carrier, trusted defaultFalse source flag, exact category binding and finding-page
diagnostics agree with refreshed G1. Missing stress cases (duplicate evidence,
source conflicts, expiry, rollback and assertion sensitivity) remain mandatory
APC14/15 work; 77 acceptance cases do not replace that gate.

After G2, component reuse draft reviewed as G3 PASS: existing support, category,
matcher, immutable snapshots and Store checkpoint owners retained; one narrow
stdlib envelope serializer; no new persistence schema or policy engine. Author
may finalize component metadata unchanged and implement APC11–13 sequentially.
No full suite or live verification claimed by this review.

Reviewed SHA256:
- `specs/012-analysis-profile-coverage/skeleton.md`: `76e71715af99be2386d3e3877011bd9c9e1e0d8d9852e6792aeed5035c2e0bd1`
- `specs/012-analysis-profile-coverage/components.md`: `064e592dd299d8facf8cddcd41605dd3f0e0759466505ea409f16664c82ee2e1`
- `specs/012-analysis-profile-coverage/pilot-contracts.md`: `17886f86f8da20ab9ba7a13b6d38e88f970458796dba52aef863c842d59932ff`
- `tests/test_profile_quantities.py`: `4cefd90a1c8859ae865078c405471a810b27bc95f10a242dd5e323de86b3c8dc`
- `tests/profile_coverage_helpers.py`: `dcc56b1f45b66d3b45f7563f2c2343240338dc4461ba531ea3c408c96abe7cdd`
- `tests/test_profile_coverage_integration.py`: `fdceb039671a68ff06cc93b6f5846424ccd81a054835e4fa7bc0bf21fb0cb818`
- `tests/test_profile_coverage_cli.py`: `66f2ac9c38b7d208e8d7d51ca9fe954decc11d74b6d397b893334479af486bca`


# Implementation-informed pilot review clarifications — 2026-10-25

Independent reviewer /root inspected actual quantity parser, projection and
existing identity_match.normalized_attributes before approving bounded repairs.
Long coefficient fixture originally ended ...890 but expected insignificant
fractional zero retained, contradicting canonical formatting. Change final
digits to ...891 preserves the exact precision6 digit assertion; retain separate
trailing-zero case. This is a fixture correction, not rounding acceptance.

Existing matcher compares all overlapping attributes and vetoes on capacity/model
differences before comparison role classification. Preserve that safety priority:
identity_unresolved with an actual attribute conflict is correct needs_review;
variant_specification applies when matcher is otherwise exact. G1/G2 wording
clarified accordingly, with comparison different and no-correction assertions
retained. Do not loosen matcher to pass unit comparisons. New typed wrapper key
order is semantically irrelevant but existing str(dict) invents false conflicts;
a narrow transport-valid-wrapper canonicalization is approved after a designed
red regression, preserving all old string outputs and malformed-input behavior.

Additional review dispositions: closed-shape validation must not be bypassed by
inner null/empty; ASCII whitespace handling coherent; generic-only projection and
sorted declaration iteration; captured-baseline checked coverage requires actual
retained evidence IDs; current-policy inventory overlay must include canonical
profile definition digest. Author must prove these in final focused/mechanism
checks. No premature final acceptance is granted here.


# APC14 initial independent mechanism coverage review — changes required

Reviewer /root read actual fixed48 driver before execution. Tighten existing
interaction assertions to the named reason/conflict instead of any needs_review;
partial+expiry must independently demonstrate both mechanisms. Selected-policy
mismatch must exercise actual run/resume/retry admission, not only a direct
validator call. Manifest seam labels must match direct-comparison cases; common
field case must exercise its named currency guard. Rollback fixture deliberately
commits two unique findings after a failed transaction, so repeated retry must
retain exactly two, not the manifest's mistaken one. Auxiliary source-conflict,
equivalent evidence and cross-process ordering/sensitivity checks remain pending.

Targeted code inspection found no public recheck API. Do not invent one; design
recheck wording means re-evaluation through existing resume/retry. Store.begin
currently returns completed findings before validate_profiles, contrary to the
approved selected-definition mismatch contract. Reviewer authorizes test-first
narrow ordering repair: keep invalid cancelled/failed precedence, then validate
selected definitions before completed read-only replay. Changed selected policy
rejects without mutation/source requests; unrelated additions still replay.
Affected G1/G2 amendment approved with these explicit compatibility expectations;
implementation/green proof and final review still required.


### Author receipt of root-approved compatibility clarifications

Root disposition (not an author-issued gate verdict): preserve authoritative
matcher priority for conflicting capacity,so identity_unresolved replaces the
incorrect variant_specification fixture while actual different/review-only and
capacity conflict assertions remain. Canonicalize only transport-valid closed
wrappers for key ordering,including variant options;do not physically normalize
matcher conflicts. Root approved precision fixture ending891 rather than890 to
match frozen trailing-zero canonicalization while preserving all-digit precision6
proof. Completed replay must validate selected definitions before returning stored
report; narrow begin-order repair preserves cancelled/failed invalid_state.
Designed red and green evidence is indexed in verification.md. Implementation
and APC14 final verdict remain root-owned.


# APC14 revised coverage review — PASS for bounded execution

Independent /root reviewed revised48 driver, five auxiliary checks and exact
manifest after author checkpoint. Prior findings addressed: concrete interaction
reasons/conflicts, expiry plus partial marker, actual run/resume/valid retry
selected-policy rejection with no state mutation, currency guard, honest direct
comparison seams and exactly two unique rollback findings. Auxiliary checks
exercise equivalent source pointers, competing source rejection, native opt-in
lookalike/default compatibility, two fresh hash seeds and temporary real-unit
conversion fault with finally restoration. Real algorithms retained. Limits and
smoke-first saved progress accepted; runtime results remain pending. No additional
feature/test expansion authorized by this review.
- `tests/profile_coverage_mechanism_driver.py`: `d3daa3d3f6fd5ca43d74568a5c6051bd8f936d6e4ff2fa103aaaead5fa5d87eb`
- `tests/profile_coverage_mechanism_checks.py`: `b72b4d2794790afd57a47d6a1036c5d186ee84f9b9cd47ae0e9095b006c0d319`
- `specs/012-analysis-profile-coverage/evidence/pilot-case-manifest.json`: `64730a8befafe9fc42e53a538652f7a5dd3fc2d16712ad73317e7e86a367645e`


### Independent narrow APC14 driver repair review — PASS

Reviewer: /root/coverage_author,2026-10-25;no production edits or test execution.
Reviewed tests/profile_coverage_mechanism_driver.py SHA256 `19bdd5c95a36b4a79618665760187ffd34dfda958eebcdb9fd87cbf968f7ccd5`.

GTIN/MPN assertion repair PASS: actual matcher source emits exact `GTIN differs`
and `MPN differs`. Replacing incorrect lowercase substring search with exact list
membership strengthens the diagnostic contract;retains needs_review and all other
interaction assertions. Initial failed evidence pilot-gtin-assertion-initial-* is
preserved and shows the original case-sensitive assertion failure.

Progress publication repair PASS: same-directory temporary file is fully written
then atomically replaced over progress,so watchdog sees prior complete or next
complete JSON rather than a truncated in-progress document. One sequential writer
owns this mode;existing prelaunch stale reset remains. Size cap,phase timestamps,
115+5total budget,10s invocation guard and invalid-progress failure semantics are
unchanged. Initial pilot-progress-race-initial-* records progress_invalid at2.795s.
No concern blocks continuation of the existing bounded driver.


### Independent narrow selected-policy preflight repair — PASS

Reviewer /root/coverage_author,2026-10-25;no test execution/production edits.
Engine SHA256 `8523f5c76ca084da811bf1472f7fc1d64cd39fac8d3fa27fb1a0f78ccfa7b531`;
Store SHA256 `4056223847fcbbcb82cf18146ca761047074bf23d64e79e703e0c7ee7d96b184`.

Retained pilot-profile-retry-initial-* demonstrates replay-02 rejection occurred
only after Store.acquire recovered intent attempts to unknown,violating the
existing before-mutation contract. Reviewed engine.run preflight uses read-only
status and validate_profiles before ownership recovery or source work. Selected
snapshot comparison remains exact;unrelated registry additions remain allowed.
Existing Store.begin validation under ownership is retained,so this preflight
does not replace protected validation. Closed/active precedence unchanged;
cancelled/failed skip the new preflight and retain existing invalid_state path.
No new API,table,source request or recovery semantics. Existing exact status/step/
attempt immutability assertions remain unchanged. Narrow repair PASS for root's
continued existing48and configured full verification;no scope expansion.


Rollback envelope assertion addendum — PASS (same independent reviewer).
Driver SHA256 `6af025303c06b611dac37bb24d975565018ceb45a4638c1a1e53e38f86aae7fc`.
Store._transaction rolls back then intentionally wraps sqlite3.Error as
MaintenanceError('storage_error');retained pilot-rollback-envelope-initial-*
confirms the actual exception. Driver's exact expected wrapper now matches this
existing public boundary. Zero partial findings/uncommitted step after failure
and2unique exactly-once findings after retry/repeat remain asserted unchanged.
No production repair,test execution or weakened persistence assertion.
