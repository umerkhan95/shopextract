# Independent planning review

## G1 — umbrella verification and implementation plan

Reviewer: `/root/audit_plan_review`, independent of behavior, research and plan
authors. Date2026-11-01; production baseline90d5bd1. Exact reviewed artifact hashes
are saved in `evidence/planning-review-digests.json` (10 artifacts). Source spot
checks: `_cli_extract.py:128–172`, `woocommerce.py:51–65`,
`_schema_org.py:126–155`, `_normalization.py:100–117`, `unified.py:185–201`,
`analyze/stats.py:202–220`. Compared diagnostic construction and saved results;
no source edits, network requests, model launches or new test sweeps.

Verdict: **PASS for planning deliverable only**. No blocking planning findings.
This does not pass any child implementation gate or claim live reproduction.

| Finding | Severity | Disposition |
| --- | --- | --- |
| Verification described final replay as though its saved result already existed | Minor evidence-status wording | Reviewer changed to explicitly planned, not yet passed. Primary must record actual bounded replay result separately. |
| Research called runtime slice0 enabling without the plan's explicit nonblocking-first-repair clarification | Minor ordering ambiguity | Reviewer aligned research: small harness first; broad runtime changes are separate cross-cutting children. Truthful reporting remains first repair. |
| Missing currency, schema version/outcome parity, feed ID, robots and candidate semantics remain unresolved | Child implementation prerequisites | Correctly listed as blocking child design decisions, not falsely resolved by this umbrella. Resolve in each child before implementation G1. |
| Historical timing, precision, browser404 and stdout/hang attribution are not current end-to-end reproductions | Evidence limit | Research classifies historical/unresolved claims; no unsupported live pass. Empty-result diagnostics exercise current emission helper/predicate rather than full CLI; limitation is explicit. |

Traceability: FR01–08 and SC01–13 map to task slices and distinct risks. Design
preserves legitimate free products, supported variant linkage and legacy constructor
contracts. Intended acceptance failures, child skeleton/components, synthetic
mechanism/stress and full repository/live checks are required later; none are
reported passed. Exact byte/deadline and destination rules remain child research
rather than unverified current standards claims. Roadmap scope is large but explicitly
split into independent reviewable changes and adapter children.

## Remaining gates

- Child G1: pending per child; unresolved contracts must be resolved first.
- G2 skeleton: not started, no implementation interfaces reviewed.
- G3 components: not started.
- Implementation/offline regression/stress/live/final implementation review: not started.
- Planning handoff bookkeeping and bounded diagnostic replay: primary coordinator next.

## Final integration compatibility amendment — G1/G2/G3 PASS

Independent reviewer `/root/audit_plan_review`, 2026-11-01. Bounded inspection of
design, new real Harness controls, saved first reds and actual owner code. No
production edits/test sweep. First main2070pass/14fail/9setup in236.62s remains
a failed main run; fail-stop oracle/maintenance NOT RUN. No live/final pass.

G1: changes preserve existing contracts: CategoryCode.inCodeSet opaque namespace
is not a missing product-node reference; bounded category artifacts retain their
1MiB publication limit independently of catalog32MiB; validated positive per-page
cache observations may remain incomplete without relabeling catalog coverage.

G2: existing failed namespace/rollback/corrupt-domain assertions plus newly designed
real200positive/500negative cache and literal capabilities1M tests provide relevant
red evidence. Cache control asserts stored complete=false, nonempty products,
sole coverage diagnostic, repeat-operation wire reuse;500 has no cache and refetches.
Worker-process fixture seam may inject local transport only; real worker tests
continue exercising isolation. Fixture changes must retain all evidence/value,
rollback, robots request/diagnostic and canonical-order assertions.

G3: use existing resolver property context for the narrow CategoryCode.inCodeSet
exception; dangling offers/mainEntity remain diagnosed. Existing maintenance
cache path retains auth-on-hit/policy/freshness/codec validation; only extract-mode
positive validated products with sole catalog_coverage_unverified diagnostic may
use the new partial-cache exception. Native cache version bump invalidates old
complete=true payloads. Existing category CLI/export staging own the1MiB cap;
common reader and capabilities use approved32MiB/1M catalog defaults. No additional
cache/framework/public model is warranted. No design blockers.

Approved for exact repairs and focused failed-node checks, followed by a fresh
unchanged-ceiling full driver. This is amendment approval, not functional/final
approval or a waiver of oracle/maintenance/live gates. Preserve unrelated012 edits.

```json
{
  "specs/013-audit-remediation/integration-repairs.md": "6fd59936db71eb650d989a5e99fc585dc7344e720e7b8312f138a06c18216b3a",
  "tests/test_audit_integration_compat.py": "b6e048dc80e4ab4b41b5f222f4f5f7ac0e11f7da4b14c09dc343d5620b785945",
  "tests/test_cli_operations.py": "a05f5ee2fcd0832457bc23e5ee3dd6a0a687540d43ab0d5b46cfb7b91257b7f4",
  "specs/013-audit-remediation/evidence/integration-first-red.log": "adee112cb69cc1376fcb6d1bb9d0883ad2d81126e7df64caec2cdc250fadb96d",
  "src/shopextract/maintenance/engine.py": "8523f5c76ca084da811bf1472f7fc1d64cd39fac8d3fa27fb1a0f78ccfa7b531",
  "src/shopextract/extractors/_schema_org.py": "b0d8197ae45ccc7145bc188100ef5aef208b6e3dcfbf08d84467ccf2aa29ccd9",
  "src/shopextract/_cli_categories.py": "17569edfc45e63fbd78edc37e8699c4611e8bb7bc24008636aa6bce80c7723d4"
}
```

## Integration repair functional review — BLOCKED (advisory regression)

Reviewer `/root/audit_plan_review`, 2026-11-01. Exact source inspection; no broad
test/network sweep. Saved45 focused passes plus4 resource/control passes are
scoped evidence, not complete regression coverage.

Concrete blocker: new `allow_page_observation` arguments leaked into unrelated
advisory callers. `_advise` passes `mode=='extract'` although mode is undefined
in that method; comparison advisory publication passes `page_only` although that
name exists only in `_source`. Any advisor reaching these branches raises
NameError, bypassing the intended cache/review flow. Restore these two callers
to their original complete-only default. Exercise an existing real advisor
maintenance case through new-result cache publication and subsequent cache hit;
no network/model launch is required. This is the approved direct-caller default
compatibility contract, not a new cache behavior. Hold fresh full driver until
fixed and focused verification saved.

Otherwise inspected changes match amendment: store opt-in defaultsFalse and
strict page-observation predicate, source-mode cacheversion2/auth/portable
validation retained, captured inCodeSet namespace survives without fetching,
category publication limit1MiB is independent, capabilities advertises actual
32MiB/1M. Fixture/local guard refinement retains actual full-size money cases
and original rollback assertions. No waiver of full/oracle/maintenance/live/final.

```json
{
  "src/shopextract/maintenance/engine.py": "6059700ff6f8d76a885de9b0524c9a285bbc7f4099ef1bebed94a1eba80652a6",
  "src/shopextract/maintenance/store.py": "193793ecae9b416fa7f63eb080da11861427933e66747680233a5ac70ab055f7",
  "src/shopextract/extractors/_schema_org.py": "5bd8104efede385d34a4f96ed6c8ecb15aab7ad2a0c0e4bb32ac61c7eab5fe72",
  "src/shopextract/_cli_categories.py": "7f3d19d18707f33141b2df0d3907199398bb2f4b9b28b6c3c43d22e17ebb1ccc",
  "src/shopextract/_cli_discovery.py": "25250fd9600798a364b470ec83a8546730c35d8eab16a685e7998d22a517a20a",
  "tests/test_audit_integration_compat.py": "b6e048dc80e4ab4b41b5f222f4f5f7ac0e11f7da4b14c09dc343d5620b785945",
  "specs/013-audit-remediation/integration-repairs.md": "12792d177f3335c8fa94e6a53be704bdba94db62a6f5d8d3a15b47916855389c"
}
```

## Integration functional advisory repair re-review — PASS

Reviewer `/root/audit_plan_review`, 2026-11-01. Exact source/call-site and saved
red/green evidence inspection, no new sweep/model/network or production edits.
Only two engine opt-in flags remain, both locally scoped in `_source`; unrelated
advisory publication/get use original complete-only defaults. Undefined variables
are removed. Existing known-usage advisor test reproduced NameError before repair
and exercises actual publication followed by exact cache reuse after repair;
with two positive/negative source-cache controls,3PASS1.39s. Store optional default
remainsFalse. Earlier45-node/resource checks retain their scoped historical meaning.

Integration functional blocker resolved. Proceed fresh frozen full driver with
unchanged240/480 ceilings and required oracle/maintenance families; no full/live
or final approval implied.

```json
{
  "src/shopextract/maintenance/engine.py": "2d1b5c582d653684a7d21768bb2eab911733428fdf866457b9483f4b4b601520",
  "src/shopextract/maintenance/store.py": "193793ecae9b416fa7f63eb080da11861427933e66747680233a5ac70ab055f7",
  "specs/013-audit-remediation/evidence/integration-advisor-red.log": "727ae4d7bcd320ceb9b95692977d342989f4f47e1e9691353c0fe3180a2571ee",
  "specs/013-audit-remediation/evidence/integration-advisor-green.log": "5393dfbf2a3591494a3b111e4ebf31e99f10d9e7d84ca19986ccbbcf39515677",
  "specs/013-audit-remediation/integration-repairs.md": "9f402e0dea97926e79346c1609e3a31a1117d7c954a12e7a9893546e9eeafacb"
}
```

## Portable projection performance amendment — G1/G2/G3 PASS

Reviewer `/root/audit_plan_review`, 2026-11-01. Bounded design/test/source review;
no production changes/model/network or broad benchmarks. Profile establishes
local repeated deepcopy/asdict and duplicate validation cost, not causation of
entire239.06s main timeout. Completed tests passing at93% is not a main pass;
oracle/maintenance/live remain gated.

G1: reuse known immutable leaves and one already-performed contract validation
within the synchronous portable serializer; no limits, schemas, cache, public
acceptance or evidence semantics change. G2: four predesigned tests include exact
standard-asdict encoded JSON field/order oracle with a real captured variant and
all contracts/reload, delegated deepcopy spy, detached mutable containers and
unsupported/tampered/cyclic negatives. Saved2missing-helper reds/2controls match
proposed seam. G3: private evidence projection shared at exactly three declared
call sites; public TrustContract.to_dict retains validation. `_contract_to_dict`
can reuse trust_view's actual contract.validate without an await/mutation/cache
seam. Existing product type/tree/encoded validation remains.

Implementation must preserve standard subclass/container semantics via fallback;
immutable shortcuts must not treat arbitrary user subclasses with mutable state
as proven immutable. Preserve field insertion order, dictionary keys, dataclass
containers and tuple fallback semantics; unsupported values remain rejected by
existing codec. This clarifies the documented unknown-type fallback, not a new
public type policy. No blockers to bounded implementation.

Required after repair: original Woo100 control, selected portable/evidence tests,
original30s actual25/265 all-field/evidence/analyzer/export reload diagnostic,
then unchanged-ceiling full driver. Functional/final not yet approved.

```json
{
  "specs/013-audit-remediation/serialization-perf.md": "404a20d4923e87a0769a6bb4cf304376ad0a404ac713ce548fcea91d35bed34d",
  "tests/test_portable_projection_perf.py": "275ecda318e17a77b893dc36ecf502f8bb126d1ae2eccc67d4e9d955b964e8f7",
  "specs/013-audit-remediation/evidence/projection-red.log": "54de0d28eb526579f389a6e241a05f69b393ee446654d38014c3e86f3293730c",
  "src/shopextract/_evidence.py": "368cad9ae37c289951f1bbeec2562f28f419d2c9f9dd8adf0bf63d8f5427859f",
  "src/shopextract/_portable.py": "27bed781a87f590bdad49598e4cc8561c6845a11bd354baaad287bb411103794"
}
```

## Portable projection functional review — PASS

Reviewer `/root/audit_plan_review`, 2026-11-01. Bounded helper/callsite/test/saved
roundtrip inspection, no new tests/model/network sweep. Exact immutable primitive
types bypass deepcopy; arbitrary subclasses fall back. Container/dataclass and
namedtuple reconstruction follows standard asdict semantics; dictionary order
is preserved. Enum optimization preserves custom hooks/reducers and restricts
its standard path to immutable values. Detached mutable-text positive spy control
proves real fallback is observed. Unknown values still reach existing validation.

Exactly three serialization sites use the helper. Public contract serialization
still validates; private portable contract serialization follows synchronous
trust_view validation. Product type/tree and encoded record validation remain;
no global cache/transport/schema/limits change. Four scoped controls and selected
240PASS evidence are accepted as reported; same Woo100 profile shows local cost
reduction, not whole-suite causation or guaranteed speed. Original30s historical
25Product/265variant all-field/contract/analyzer/CSV-sidecar equality report is
passed. No current functional blocker.

Proceed fresh unchanged-ceiling full driver. Earlier239s93% timeout remains
failed; oracle/maintenance/live/final gates still pending.

```json
{
  "src/shopextract/_evidence.py": "95d8c30199c66f59870223ae818ab504164ba26d832929a36338230bd1b41275",
  "src/shopextract/_portable.py": "b62ede3c181835f8f64508d2d27cadfe5825e4d2b1357b31c6137462babead6b",
  "tests/test_portable_projection_perf.py": "005a4b42182bbb416af877b384feed8dadd3a65d1a324ed3f4bdcbcd6685f9a3",
  "specs/013-audit-remediation/serialization-perf.md": "227a4d28fd23d6088a2f0a96ddbda9a9c1322620aa1072fc3c6cf3d7c1f66fe7",
  "specs/013-audit-remediation/02-money-roundtrip/actual-audit-roundtrip.json": "0d13940fba14c3280347c2cd1bad71e2f608f1d4da4529e151c09b4f5a733c2d"
}
```

## Maintenance completion compatibility amendment — G1/G2/G3 PASS

Reviewer `/root/audit_plan_review`, 2026-11-01. Exact completion/model-stop source,
design and saved4red/2controls reviewed; no model/network/sweep/source edits.
Third driver main2099PASS/oracle24PASS accepted as family evidence; maintenance
101PASS5FAIL means whole driver is still failed. No live gate waived.

G1: inferred generic source_partial must preserve truthful partial state/False
source coverage while allowing actual durable model failure/budget reason to be
reported. Explicit source stop reasons retain their existing priority. G2: actual
advisor dispatch/denial and durable reopen cases reproduce reason masking while
retaining call/usage assertions; Falsecoverage assertions strengthen the contract.
Successful retry still needs generic source_partial if no current model stop;
robots-first workflow fixture retains exact accounting/proposed correction.
G3: one owner MaintenanceStore.completion reason selection; preserve distinction
between caller-explicit source reason and inferred generic source_partial. Only
the latter ranks below durable model_stop/model_reason. No settlement, extra
dispatch, cache, engine or coverage computation change. Other inferred concrete
pending/budget/error reasons retain ordering. No design blockers.

Proceed narrow repair and focused verification; functional review then fresh
unchanged-ceiling required full driver. Maintenance/full/live/final remain pending.

```json
{
  "specs/013-audit-remediation/integration-repairs.md": "c8af6de15ee969980d2c84ad5680404c1be6b7e114a71092009011d2dfff3082",
  "src/shopextract/maintenance/store.py": "193793ecae9b416fa7f63eb080da11861427933e66747680233a5ac70ab055f7",
  "tests/test_maintenance_advisor.py": "a65c38f5fa9ceb8c29d58335c673457a15742137378fe228744e60862b28e16e",
  "tests/test_maintenance_review_repairs.py": "24b1a82156acb69a0b63a5ee0df7a47d44e7162307e473674ebba99bef941322",
  "tests/test_maintenance_workflow.py": "a70a68c58b653a1425a899f587bfe2db12d0d46ede84e03b457cd73215c8f7b8",
  "specs/013-audit-remediation/evidence/maintenance-integration-red.log": "6187fa399ce48f173ad58219836418eaa8abb2960027202c8d3943031a8e663f"
}
```

## Maintenance completion functional re-review — PASS

Reviewer `/root/audit_plan_review`, 2026-11-01. Exact source/green evidence read;
no additional sweep/model/network/source edits. `inferred_partial` is captured
only when caller source_reason is None and observed coverage/source step is
partial. Durable model stop/model_reason wins only in that inferredgeneric
branch. Explicit caller stop reasons and remaining source fallback order retain
priority; returned partial state/coverage unchanged. No accounting/cache/engine
or dispatch change. Six actual advisor/resume/retry/robots controls PASS3.66s
resolve scoped maintenance blocker. Proceed fresh unchanged-ceiling full driver;
previous main/oracle passes do not substitute for a whole fresh driver pass.
Live/final remain pending.

```json
{
  "src/shopextract/maintenance/store.py": "6119651f39fb0aa299d7378e75d63e62bc8791965e445d4488c93ddf4ba49107",
  "specs/013-audit-remediation/evidence/maintenance-integration-green.log": "975050c9ee795a72567e3c00ca47fb34ed4502403280e570ca0c4892c9fee972",
  "specs/013-audit-remediation/integration-repairs.md": "c8af6de15ee969980d2c84ad5680404c1be6b7e114a71092009011d2dfff3082"
}
```

## Discovery decoded-copy amendment — G1/G2/G3 PASS

Reviewer `/root/audit_plan_review`, 2026-11-01. One-seam source/design/real HTTPX
decoder fixture and saved2red/1control reviewed; no merchant requests or tests
run by reviewer. Existing _read consumes decoded aiter_bytes then copies encoding
headers, reproducing double decoding. G1 behavior correct: remove Content-Encoding
and original Content-Length only from copied decoded response; preserve other
header multiplicity (including cookies), status/request URL; existing decoded
byte caps remain before reconstruction. G2 genuine HTTPX gzip robots/XML and JSON
fixtures reproduce actual decoder failure; compressed-over-decoded-limit negative
passes before repair. G3 ownership limited to _read copy return; no limits/policy/
retry changes, preserve original response headers rather than mutating them.
No design blockers. Proceed narrow repair and scoped green, functional re-review
then fresh full source verification.

Driver4 2229tests344.10s is a historical full offline pass. New source repair
requires fresh verification; four bounded one-request live HTTP cases pass only
their claimed outcomes. Khaadi robots policy unavailable remains inconclusive,
not attributed to this bug or retroactively passed. Merchant expansion stopped;
no additional request authorization inferred by this amendment. Final pending.

```json
{
  "specs/013-audit-remediation/discovery-compression.md": "49a4be2f75730a7970494eadd1db4756ad330926645712209103a161da6d0b59",
  "tests/test_discovery_compression.py": "bfbb3fff9b63f4f4b7602cc4a743f517c2cd54d085f4d1865ef378457f5bcc52",
  "specs/013-audit-remediation/evidence/compression-red.log": "c3234350adac82625fd303e99d3dcbe4aaffb6ab3d3ab0736632d53f9110a814",
  "src/shopextract/_discovery_runtime.py": "52d56b2c8574e0162289fa7305e6f5f85845b995174178ddd3dc9ab0b8d1e683"
}
```

## Discovery decoded-copy functional review — PASS

Reviewer `/root/audit_plan_review`, 2026-11-01. Exact one-seam source and saved
38PASS6.09s compression/discovery/tool controls inspected. Header copy preserves
multiplicity and original response; only obsolete encoding/length removed before
new Response creates correct decoded length. Status/request retained, decoded
cap remains enforced before reconstruction. No functional blocker. No new tests
or merchant/browser requests by reviewer. Proceed fresh unchanged-ceiling full
driver; historical driver4 pass is stale for changed source. Khaadi original
inconclusive remains unchanged. Parent-scoped retry authorization is separate
from this code review; browser live remains blocked unless its request bounds
can actually be enforced. No final or broader live approval implied.

```json
{
  "src/shopextract/_discovery_runtime.py": "ded8120f0dd3a6c8b0ba0bbddd082cefb98398b1b32fa9d79789f0a00305ade6",
  "tests/test_discovery_compression.py": "bfbb3fff9b63f4f4b7602cc4a743f517c2cd54d085f4d1865ef378457f5bcc52",
  "specs/013-audit-remediation/evidence/compression-green.log": "022450e4413ba02d1010c04cac1ca9cc9863a5db40d2e48f7bf1df96cfb6e452"
}
```

## Final independent verification assessment — G4/resource PENDING

Reviewer `/root/audit_plan_review`, 2026-11-01. Bounded final status/claims/docs,
actual driver JSON reports and source manifest reviewed. All282 manifest hashes
match current source/tests/docs. No source/test edits, network/browser/model
launch, broad sweep or process modification by reviewer. Minor docs correctness
repair: tasks.md labels its original unstarted roadmap historical and points to
current status; no acceptance/task implementation claims changed.

Functional disposition: all01–07 and exact integration amendments have independent
scoped functional PASS records, including compression38PASS6.09s. No additional
code defect identified in this final evidence review. This is not full approval.
Driver4 genuinely passed2229tests344.10s with240s/group480s/total1worker limits,
but predates compressed-response source repair. Latest unchanged-ceiling driver5
status is timeout (main239.16s, completed tests pass, oracle/maintenance NOT RUN).
Prior green plus scoped compression controls cannot replace latest full gate.
Therefore G4/latest-source full-resource approval and feature completion remain
PENDING, not waived. Host activity snapshot does not establish timeout cause.
No further source optimization or repeated sweep warranted from that snapshot;
any primary-authorized single unchanged retry requires separate evidence that
transient host activity has settled, otherwise retain the exact pending limit.

Live disposition: four actual single-request HTTP cases pass their narrow source
status/partial outcomes only. Khaadi robots200/policy-unavailable remains
inconclusive, exact cause unknown, no forbidden request/emission. Authorized
retry has not occurred and remains gated by fresh offlinegreen. Browser merchant
live is BLOCKED because supported SDK configuration does not establish service-
worker/global request bounds; deterministic admission/merge/process tests are
mechanism passes, not observed browser-live behavior. No further merchant calls
authorized by this review. Current Google/ACP qualification and historical/current
distinction in A01–A35 mapping are preserved; no certification/precision/RAM/time
promise. Historical25/265 exact portable/analyze/export roundtrip remains passed.

Final outcome: implementation functionally reviewed; current resource/full gate
unresolved and external live limits explicit. No commit/push/PR or complete-gate
approval. Preserve unrelated012 edits. Counters unavailable, no quota inference.

```json
{
  "specs/013-audit-remediation/status.md": "f132dc21db0ec68d3989802923d7b2f331026b72305ff7dcb1dc6ab5b73fcff5",
  "specs/013-audit-remediation/verification.md": "7019a5553c4060fe342b11a23df67357225524e1d3c60786e5d07ee13f613103",
  "specs/013-audit-remediation/claim-coverage.md": "ec96378c088a02b0b816a65c7076e0f745e4aac832ed3dd35e2cdc908d7ad545",
  "specs/013-audit-remediation/tasks.md": "152d958d8deea71e903b49e15cf32c6bedde5e9a1310131e29174a59b5d415a2",
  "specs/013-audit-remediation/evidence/final-source-manifest.json": "c05ce7357f79a4d4ca783beeeb04fbfc06664481c239aaca88e9b6257d91ba0b",
  "specs/013-audit-remediation/evidence/final-driver-4/report.json": "5c515983b088900a2f8eb0ce0973204dbbc7571092ed5589088f04158e514981",
  "specs/013-audit-remediation/evidence/final-driver-5/report.json": "71e8c19eef3f8928bad224880b129b50d808cdbd22c2404a22fbc9ba60c51350"
}
```
