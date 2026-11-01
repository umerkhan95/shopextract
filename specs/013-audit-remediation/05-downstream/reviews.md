# Independent child G1 review

Reviewer `/root/audit_plan_review`,2026-11-01. Verdict: **CHANGES REQUIRED**.
Reviewed spec/test design before tasks/research/plan and shared primary-source
register. Source spot-checks reused current `_cli_data` bounds, canonical identity
allocation, schema ProductGroup handling and eager package/extractor imports.
No new probes, network requests, tests, production edits or subagents.

Blocking: FR-D1 and SC-D1 defer conditional brand/identifier/condition/variant rules to the source register, but that register supplies links and broad caveats rather than an executable condition table. G1 needs exact supported branch inputs and expected issue/eligibility outcomes before skeleton/testing: at least identifiers present versus genuinely absent versus unknown, relevant condition/category/country and variant grouping branches. Explicitly mark unimplemented branches needs_context; do not silently implement a universal requirement or claim Google eligibility from four generic fields. Pin rule identifiers/versions and source sections for supported subset. Other contracts appropriately preserve presence-only score, canonical/vendor feed mapping, unknown stock, candidate-versus-identity semantics and per-product category counts. Canonical IDs without a stable source alias may be allocated UUIDs; tests should distinguish persisted-ID stability from repeat stateless extraction guarantees.

Audit mapping and bounded sequence remain explicit in each spec. Shared test
boilerplate is a ceiling, not concrete collected coverage; each substep must name
actual distinct fixtures, real-path assertions and edge counts before red execution.
Synthetic, stress, actual live and unsupported external-approval states stay
separate. Browser budgets include subrequests or integration is blocked.

## Pending gates

G2 skeleton/executable intended-red tests: pending. G3 components: pending.
Implementation/offline/full-driver/live/final: pending. Parent child01 functional
repair review does not pass its unresolved complete verification gate.

## Reviewed SHA-256

```json
{
  "spec.md": "d159f382312939a260c779c207a5b0b6fc840bda82b8893574c71ed56a4cd137",
  "test-design.md": "ba2c26b4a7933497addb305300c27c136e6fca87fe71bb6cd10fc7a3a70abc17",
  "tasks.md": "1ab5196a4bc8773a3af7b8d2d8ecf633714b3da64d1f6563ee4191286ee113d9",
  "research.md": "312f27620140d8e7cadc01533b97ebcc61b80b39174ec2934e0e38a25b1fa721",
  "plan.md": "41080da65d17f732302a33f7294e73736214f38bc15862e198176039bd3cc0f1",
  "../primary-sources.md": "7efa271a2fb1860960fddcd349d7ba17edbe633478fdeb0f8ea8caf7d10a215d"
}
```

## G1 blocker re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01; documentation-only repair review.
No tests/network/probes/source edits. Supersedes previous G1 changes-required
verdict for hashes below.

The concrete15-row google-catalog-subset-2026-11-01 table now specifies identifier present/unassigned/unknown/contradictory branches, brand exceptions, condition states, region/destination grouping, apparel unsupported scope and needs_context fallback. Baseline fixture and cumulative rule semantics make expectations executable. subset_pass is explicitly not full Merchant Center approval; unassessed checks remain visible. Prior conditional-rule design blocker is resolved.

G2 concrete interfaces and executable intended-red tests are next; G3 and all
implementation/green/full-driver/live/final gates remain pending.

```json
{
  "spec.md": "8aaa994c39e11425f1431593b14355b8b79cd6e0ef91968214eb5da5b3ccac2f",
  "test-design.md": "331687c79a07a623066367ec34e8a5f6b3fa50cf981d495141770883a3efb34a",
  "tasks.md": "6825435567b2aaac328e80b083fa196a6cec47c883947ed46c528b72a97a84bb",
  "research.md": "c594fc6e92b76b60053cbaaa17be775883c8f13f24a2407388c64829c364e548",
  "plan.md": "fc125a9b4c69c93a3a4209baf36aa747b67325ffa5e8c1d1cf9ca9aa411e3fde"
}
```

## D5 behavior refinement — G1 PASS; combined D1–D5 G2 CHANGES REQUIRED

Reviewer `/root/audit_plan_review`,2026-11-01. Inspected reviewed15-row rules,
37 executable cases/documentary interfaces and saved36red/1control plus oneproduct
profile. No new probes/tests/network/source edits.

D5 concept PASS: request-scoped reuse of one actually validated serialization
can avoid measured duplicate work without global caching/trust bypass or original
30s-budget increase. Oneproduct0.389s/two calls is mechanism evidence only,not
proof of25-product timeout cause or eventual complete roundtrip. Actual audit
export/reload remains required observed evidence.

G2 blockers:

1. Native unsupported defaults are not isolated by37cases. Missing/null stock tests
   use plain dictionaries; unsupported_currency native example also lacks many
   core fields,so it cannot expose defaultTrue availability becoming fact. Design
   one otherwise valid captured/portable product lacking source stock but retaining
   constructor-compatible scalarTrue. Through actual CLI analyze/validate/feed,
   require unknown_stock and missing_availability/skip behavior,retaining explicit
   supplied dictTrue as a distinct control. Cover source support at typed/flat
   projection boundary,not a handcrafted expected-support flag.
2. New CatalogStats/ValidationReport fields must survive actual CLI serialization.
   Current report field allowlists omit unknown_stock/subset_status/rule version/
   unassessed fields. Add actual analyze-file and validate CLI assertions so direct
   Python API green cannot leave user-facing reports misleading. Existing15rows
   correctly exercise shared assessment/validator/feed,not these CLI report seams.
3. D5 prepared/validated reuse seam has no named typed internal snapshot interface
   or mutation/validation coverage. Define concrete owner/API/error contract at
   skeleton stage. Add two exports with intervening product mutation,verify each
   fresh snapshot/sidecar exactly matches that invocation; tampered/invalid native
   evidence before writer must reject before replacing existing artifact/sidecar.
   Existing same-path and reload-corruption tests do not prove producer validation
   remains intact after reuse. Do not expose public skip-validation flag or rely on
   cached mutable Product identity as a trust token.

Matching/category/plain-dict tri-state and all15 rule-consumer parity cases are
meaningful; candidate lookup versus identity positive control remains explicit.
Keep additions under64/time/one-worker caps and predesign before code. Components/
G3 and implementation remain gated. Full-driver/live/final and original actualaudit
export timeout remain open independently; no global/trust/performance waiver.

```json
{
  "specs/013-audit-remediation/05-downstream/spec.md": "b7622d5de3871e04555e69bd8beade015044c63d103513e3fcaca1e263787aac",
  "specs/013-audit-remediation/05-downstream/test-design.md": "57300540e9e1bde69e2a5c2708d91d10d920e59007a00471f400c70ef02819f4",
  "specs/013-audit-remediation/05-downstream/skeleton.md": "4e72c0e0af48411d8c57a3b2c2a9574a823d2e0eb717af950737f5dbec6389f9",
  "specs/013-audit-remediation/05-downstream/verification.md": "225238bdfb7fddefbc5c8c8b28b4358b29a271c28a2a665d68157763cca8333a",
  "specs/013-audit-remediation/05-downstream/red-final.log": "989a24e364c07876b39e92ee5df0d99daffca1c875599c8b08397a4920c42f2f",
  "specs/013-audit-remediation/05-downstream/export-profile.txt": "47d9d762c890de958a17c75e5caf0934a1b6b836b9e61806984cc8fc4bfd3079",
  "tests/test_downstream_remediation.py": "574444f9459fad9b08c006a06b0a5acff61362a9da774ab166c6871b81ddb737"
}
```

## G2 seven-case repair re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed44-case file,named snapshot
contract and saved40 intended-red/4passing controls. No tests/probes/network/source
edits. Prior G2 blockers resolved in designed acceptance/interfaces:

- Otherwise valid captured native Woo has legacy scalarTrue but unsupported stock;
  real portable CLI analyze/validate/feed must preserve unknown/missing availability
  and explicit retained/skipped diagnostics. No handmade support flags.
- Actual CLI report tests require unknown_stock/subset_status/rule_version/
  unassessed_checks survive allowlists,not merely direct Python API pass.
- Per-export frozen prepared snapshot holds immutable validated bytes/keys,not live
  Products or arbitrary validated=True. Factory validates producer before staged
  writes; public sidecar still validates. Two-export mutation,NaN/tampered-pointer
  target preservation complement serializer instrumentation and lossless reload.

Three existing snapshot/producer controls already pass and remain controls; no
expected contract weakened. Named private seam preserves request ownership and
validation-before-effects. G2PASS allows components/G3 next,not implementation yet.
D5 actual25-product30s export/sidecar proof remains pending;oneproduct duplicate
serialization profile is not cause/scale proof. Full-driver/live/final gates stay
open independently.

```json
{
  "specs/013-audit-remediation/05-downstream/skeleton.md": "daf8a58c0276aae555ef72f8d6e8bfce982e77bcfbc0efe1575012072a41f0a2",
  "specs/013-audit-remediation/05-downstream/spec.md": "b7622d5de3871e04555e69bd8beade015044c63d103513e3fcaca1e263787aac",
  "specs/013-audit-remediation/05-downstream/test-design.md": "a1c0d604cdfcae372be36096b6942e5dcc71d75f47c9fccae5285419b8938289",
  "specs/013-audit-remediation/05-downstream/verification.md": "a46322c007beee9b6fb4a3e6ea052f77e9d3f314cf098585c7bc9f26ad4bd9b9",
  "specs/013-audit-remediation/05-downstream/repair-red.log": "7b86d3e727559713947b2221c48c0cb2ccf49996336c28bdeef7f6dc125c7974",
  "tests/test_downstream_remediation.py": "2a1c92310234db3f97cf3293ea0567edfdbf8cc71539059c10f60d2bfefa281f"
}
```

## G3 — CHANGES REQUIRED, filtered-feed companion interaction

Reviewer `/root/audit_plan_review`,2026-11-01. Inspected proposed components
against approved44-case G2; no probes/tests/network/source edits. Ownership is
otherwise sound: limited destination rules/canonical projection shared,actual
trust support retained,identity veto reused,tri-state stats additive,private
immutable per-export snapshot owns validated bytes without global/boolean bypass.

One missing mechanism blocks approval before production: component requirement
"companion includes retained items only" combines feed filtering with evidence
snapshot/row mapping,but executable evidence-path tests exercise CSV only. Mixed
Google retained/skipped and all-skipped native catalogs can otherwise write stale
all-input sidecars or incorrect row/digest alignment.

Predesign two source-supported nativeProduct fixtures/cases before code: actual
to_feed(...,context=...,evidence_path=...) with mixed valid/blocked records and
allblocked. Reload using actual load_evidence_sidecar against produced artifact;
expect exactly retained products/entire contracts in order (or []),and correct
retained/skipped counts. Assert blocked product cannot leak through row metadata.
Name the private retained-subset snapshot/projection seam so immutable validated
full input cannot accidentally be paired with filtered row bytes. Reuse validated
records without per-product reserialization or trust bypass; do not invent a
second bundle format/cache. Existing invalid-producer/atomic controls remain.

This distinct D2+D5 interaction is required by newly explicit component invariant,
not random additional variation. Two cases fit64/time/one-worker limits. G3 remains
pending focused intended-red evidence and component clarification; full-driver/
live/final and original actualaudit export timeout remain open independently.

```json
{
  "specs/013-audit-remediation/05-downstream/components.md": "72b202494ace8e4baed64202321b23a2c08caa7dd571fd7a5c6231b5f635f0d6",
  "specs/013-audit-remediation/05-downstream/skeleton.md": "daf8a58c0276aae555ef72f8d6e8bfce982e77bcfbc0efe1575012072a41f0a2",
  "specs/013-audit-remediation/05-downstream/spec.md": "b7622d5de3871e04555e69bd8beade015044c63d103513e3fcaca1e263787aac",
  "specs/013-audit-remediation/05-downstream/test-design.md": "a1c0d604cdfcae372be36096b6942e5dcc71d75f47c9fccae5285419b8938289",
  "tests/test_downstream_remediation.py": "2a1c92310234db3f97cf3293ea0567edfdbf8cc71539059c10f60d2bfefa281f"
}
```

## G3 retained-subset repair re-review — one fixture correction pending

Reviewer `/root/audit_plan_review`,2026-11-01. Component subset_evidence_snapshot
now explicitly selects ordered validated entries/keys without Product reserialization;
all-skipped empty bundle/digest path is specified and two real companion/load tests
exist with saved intended reds. Architecture/seam findings are resolved. No tests/
probes/network/source edits by reviewer.

One small coverage correction before G3PASS: mixed fixture currently [valid,blocked]
retains only prefix[0]. Incorrect snapshot[:retained_count] would pass it while
misaligning skipped-leading/interleaved inputs. Use non-prefix retained index in
same existing mixed case (e.g.[blocked,valid],expected[valid]); no new case count
or interface expansion. Preserve exact reload/contracts/count checks and record
focused red evidence. Deliberate retained input order with two valid records may
strengthen this same case within tiny bounded fixture. This is the specific mapping
invariant originally identified,not arbitrary variation. G3pending only this fixture
correction; no production/full/live/final approval yet.

```json
{
  "specs/013-audit-remediation/05-downstream/components.md": "b42b02a9d6d065545fb8c44da990c86b2fdabd0acfcff0e0690acd12f09e3c1d",
  "specs/013-audit-remediation/05-downstream/test-design.md": "beab4fd28f1eda1f108a1013fbeb303311eb8be32c2331c519eb2fbafdbe2fc2",
  "specs/013-audit-remediation/05-downstream/skeleton.md": "daf8a58c0276aae555ef72f8d6e8bfce982e77bcfbc0efe1575012072a41f0a2",
  "specs/013-audit-remediation/05-downstream/subset-red.log": "1bb6803e07288a9b9716a883c7dd018bacf1b50ca1bdee1b696cb2412e5fe37c",
  "tests/test_downstream_remediation.py": "2ec66846f70b7fc3280bb41e6794cc606ec683bb808c24c669c12d2bd8069b2f"
}
```

## G3 final retained-index fixture re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01; inspected strengthened same two
cases and saved2focused intended reds. No probes/tests/network/source edits.
Mixed [blocked2,valid3,valid1] expects exactly [valid3,valid1],challenging both
naive prefix truncation and identity-sorted order; entire retained contracts and
actual digest-bound loader are still asserted. All-skipped remains empty.

All previous G3 findings resolved. Private ordered subset seam reuses immutable
validated entries/rowkeys without Product reserialization or skipped-record leakage.
46designed cases,44prior full-red+2focused-red only; no46green claim. Sequential
D1/D2,D3,D4,D5 implementation may proceed. Actual25original30s export/sidecar,
full-driver/live/final gates remain pending; no performance/trust waiver inferred.

```json
{
  "specs/013-audit-remediation/05-downstream/components.md": "b42b02a9d6d065545fb8c44da990c86b2fdabd0acfcff0e0690acd12f09e3c1d",
  "specs/013-audit-remediation/05-downstream/skeleton.md": "daf8a58c0276aae555ef72f8d6e8bfce982e77bcfbc0efe1575012072a41f0a2",
  "specs/013-audit-remediation/05-downstream/test-design.md": "beab4fd28f1eda1f108a1013fbeb303311eb8be32c2331c519eb2fbafdbe2fc2",
  "specs/013-audit-remediation/05-downstream/subset-index-red.log": "1bb6803e07288a9b9716a883c7dd018bacf1b50ca1bdee1b696cb2412e5fe37c",
  "tests/test_downstream_remediation.py": "2ec66846f70b7fc3280bb41e6794cc606ec683bb808c24c669c12d2bd8069b2f"
}
```

## D1–D5 functional review — mixed verdict, concrete projection gaps

Reviewer `/root/audit_plan_review`,2026-11-01. Inspected actual destination/feed/
trust/statistics/matching/snapshot code,51case coverage and saved outcome history.
No new probes/tests/network/source edits. Current102scoped pass is distinguished
from previous280pass/1failure broad run; no claimed current282allgreen. Positive
fixture enrichment preserves original source/fidelity checks,not arbitrary expected
value replacement.

### D1/D2 — CHANGES REQUIRED

1. Typed GTIN/MPN do not call observed(field) before satisfying assigned identifier
   rules or projecting manufacturer identifiers. An otherwise supported native
   product with absent sourceGTIN then assigned checksum-valid scalar can satisfy
   identifier_status=present without observed identifier evidence. Predesign GTIN
   and MPN unsupported-source cases; remove/flag unsupported projected identifiers
   and retain original unavailable/source context. Legacy explicitdict stays
   supplied/unverified by existing contract; checksum validity is not source support.
2. Explicitzero now asserts general-context subset_pass with no eligibility issue,
   contrary inherited SC05 zero-eligibility diagnostic and original positive-profile
   skeleton. Preserve observedzero and do NOT label it invalid parsing. Add explicit
   zero eligibility/context diagnostic or review a source-backed scope amendment
   that explains assessed exceptions. No claim here that zero is universally
   prohibited; unsupported destination branches must remain unassessed.
3. Required context checks only key presence for variant; variant='true' can bypass
   `is True` grouping check and yield subset_pass. Add invalid flag/type control
   requiring unsupported context/needs_context rather than silently nonvariant.
4. Idealo filtering reuses Google missing_id (external/canonical only),discarding
   valid SKU-only idealo products despite existing idealo schema/validator accepting
   SKU. Predesign SKU-only legacy/native-compatible control,retained row identity
   and companion mapping; isolate format-specific identity from Google policy.

### D3/D4 — functional PASS for reviewed contracts

Conservative title cues share existing conflict veto; candidate semantics and
exact compatible identifier control preserved. Per-product category dedup and
true/false/unknown stock with typed trust/CLI reporting match designed cases.
No population precision/recall guarantee from few adversarial pairs.

### D5 — functional PASS, actual historical roundtrip observed

Snapshot validates producer once,stores immutable bytes/keys,retained subset uses
actual ordered indices;public sidecar still factory-validates. CSV reuse removes
measured duplicate per-product serialization,without global cache/trust boolean.
Mutation/NaN/tampered-pointer and non-prefix/all-skipped row controls are meaningful.
Actual supplied historical25products/265variants now pass reader,ALL Product/variant
values,entire encoded contracts/captured source values,analyzer and real CSV+sidecar
reload within original30s execution ceiling. Earlier timeouts retained honestly;
this is historical fixture integration,not new merchant live evidence or universal
performance proof.

Full-driver/live/final gates remain open. Actualexport timeout is now resolved for
stated historical input; do not keep reporting it as currently blocked. Author
should design bounded D1/D2 cases/repair before functional re-review; no source
sweep or blanket eligibility standard expansion required.

```json
{
  "src/shopextract/validate/_destination.py": "c5b7180c2c0483f8458dbd5dad6790a7ded5dd85062327fe35e1627adcdeaf35",
  "src/shopextract/validate/marketplace.py": "efb02498dc510f6ba24fd2c72544ca48ddb5e3fd08d44a604f85afe450732e3f",
  "src/shopextract/export/__init__.py": "51a91a1a42e21732c19aa851107b9ce9e844801dfa0ab9e35c362d98a28be0de",
  "src/shopextract/export/_bundle.py": "3260c23aaccb8c8c1a34cf09fde6f28a68f15698812fa076866fd8ee7182009e",
  "src/shopextract/export/_feed.py": "7f33f1428d31ff0756af8f62811213c9fb814257a1143e30bedd42dc1b05dd6f",
  "src/shopextract/analyze/stats.py": "b0f7ab502e341c33ef3bfa8bb70967507b3f01a7180a65c99e2f77178a844fae",
  "src/shopextract/compare/identity_match.py": "3914d4d97d13c5624281a13280989d8679d898d7e60b52045dcd959a41c7833e",
  "src/shopextract/_cli_analysis.py": "0b09a7232b152346d847d4026b47061d55cc76f0c4a1d89a4033bf376bfdd646",
  "tests/test_downstream_remediation.py": "b6a3e6815099b45a670653d12d319a66b7f54c90ba8aad04b5d5df505ccf8bda",
  "specs/013-audit-remediation/05-downstream/verification.md": "ed90bf80ed902df736b04d47d712025e6602e031eb83bb930028e4c19bf104d5",
  "specs/013-audit-remediation/02-money-roundtrip/actual-audit-roundtrip.json": "0d13940fba14c3280347c2cd1bad71e2f608f1d4da4529e151c09b4f5a733c2d"
}
```

## D1/D2 focused functional re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01. Inspected source-aware projection,
reviewed58-case coverage and saved113 scoped pass; no probes/tests/network/source
edits. Previous four findings resolved in designed mechanisms:

- Typed manufacturer GTIN/MPN need observed support before satisfying assignment
  or entering projection; invalid/mutated unsupported values are omitted with
  explicit issues. Source_record also checks current scalar against resolved value,
  preventing stale retained observation from lending authority to a changed scalar.
- Observedzero stays valid monetary observation,not invalid parsing; explicit
  destination-context warning yields needs_context rather than universal subsetpass.
- Variant context requires actualbool; malformed flag cannot bypass grouping as
  falsely known nonvariant context.
- Idealo SKU identity remains distinct from Google external/canonical-ID policy;
  source-backed native/dict SKU-only records retain row/sidecar and do not report
  spurious Google missing_id. Exact companion/contracts remain covered.

Additional current-scalar stock mutation and issue-parity controls are meaningful
source/legacy projection interactions. No trust model was globally relaxed. D3/D4/D5
earlier scoped functionalPASS retained; current113pass includes58acceptance and
selected validator/bundle/CLI companions,not a fresh whole broad-suite pass.

Actual historical25/265 complete30s roundtrip remains resolved. Required full
repository driver,actual live and independent final gate remain pending; no
Merchant Center approval/comprehensive rule coverage inferred from subsetPASS.
Author may continue separately gated runtime/readiness work.

```json
{
  "src/shopextract/validate/_destination.py": "50b3fbd20b7830e0730f774c7890eaa15b666a6ead6fb95d1f20d46c488bd268",
  "src/shopextract/export/__init__.py": "100c72d63940b65e0fff94554552eee24d42b457d21b53243cd0ee995100256d",
  "src/shopextract/analyze/stats.py": "b0f7ab502e341c33ef3bfa8bb70967507b3f01a7180a65c99e2f77178a844fae",
  "tests/test_downstream_remediation.py": "ccce0d30788a8397fbd88ec5c5f6327dbbea6a06c35a64b171aef1eace48a752",
  "specs/013-audit-remediation/05-downstream/functional-red.log": "2c6c9a4854d5d984e66bc8c9357ce13c94a93ffa11b8b8d60d9355ca23458dd6",
  "specs/013-audit-remediation/05-downstream/scalar-red.log": "7091dc3257ec70ca4da90ebc04163838499787b236d8f0be0eb2700b4afa3b40",
  "specs/013-audit-remediation/05-downstream/functional-green-final.log": "b4de4022edf40c0855941e5a0b3661182d1b132bb1df6e135d66a4ce0d95014a",
  "specs/013-audit-remediation/05-downstream/verification.md": "3a240449f4c8651c7c3054397b164c5320858ae871180f854c5d04ea81c1ddc3"
}
```
