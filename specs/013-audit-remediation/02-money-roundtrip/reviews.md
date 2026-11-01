# Independent child G1 review

Reviewer `/root/audit_plan_review`,2026-11-01. Verdict: **CHANGES REQUIRED**.
Reviewed spec/test design before tasks/research/plan and shared primary-source
register. Source spot-checks reused current `_cli_data` bounds, canonical identity
allocation, schema ProductGroup handling and eager package/extractor imports.
No new probes, network requests, tests, production edits or subagents.

Blocking: FR-M3/SC-M4 need an explicit compact-reference expansion budget. A32MiB wire file below100k nodes can reference one large capture many times; enforcing limits only before reference hydration does not bound reconstructed bytes/nodes/depth or subsequent downstream serialization. Specify whether dedup references stay shared, reject cycles and malformed tables, enforce a concrete expanded budget before allocation, and add repeated-reference/cycle/expanded-cap boundary cases. Also qualify the saved5.4MiB legacy success assertion by retained record/node/depth limits: a byte-cap change alone does not establish that file fits every other bound. Need source-size/node inspection or exact compliant fixture rather than assuming it. Other monetary contracts correctly separate rupee-family amount context from PKR authority, preserve direct constructors and distinguish missing/rejected/zero. These blockers require author design repair before G2; no production work approved yet.

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
  "spec.md": "05dad05541251d770d22b3fc2222de3f858ce366a39faaa50c61f80c47425e35",
  "test-design.md": "9ca5683db43491118ea6e9e8b3575e571f3366fc432eea96f677a993cdbde272",
  "tasks.md": "5cc76c4ee75d38fc0b749408c7f0dc672594f088661a8aa52f852b89d9fef37c",
  "research.md": "0c5fca097b1451165340786b019da8cdb28f80979a9a23dfb1c219b40a4e3dc2",
  "plan.md": "9046bf2836d414e3a2e84ec709cbaa207c6b98e2b5c3f255c6892df54f04e148",
  "../primary-sources.md": "7efa271a2fb1860960fddcd349d7ba17edbe633478fdeb0f8ea8caf7d10a215d"
}
```

## G1 blocker re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01; documentation-only repair review.
No tests/network/probes/source edits. Supersedes previous G1 changes-required
verdict for hashes below.

FR-M4 and SC-M5 now bound both wire and expanded logical trees, count repeated references by occurrence before allocation/serialization, verify unique canonical hashes, and reject nested/cyclic/dangling/mismatched references. Legacy5.4MiB success is correctly conditioned on unchanged structural limits. Prior compact expansion and unsupported saved-file promises are resolved.

G2 concrete interfaces and executable intended-red tests are next; G3 and all
implementation/green/full-driver/live/final gates remain pending.

```json
{
  "spec.md": "58a94d55fe8c55eef7ef9e6913d89d8dcfdd5e7ebe5c193a7c83c347909ae095",
  "test-design.md": "4d6a1343655764f0446c77442e32cb31a62cdc4f8131e3a0a594c54fcf9deb21",
  "tasks.md": "0e5065bd1ed4a3f642d04bfddedc367fefc2f2eb0997177ebcefcae812eea33f",
  "research.md": "b4c3734f18f42c542633024b0bc0e0a9ed7bf7e3fe520d39da0e2fd679b4d13c",
  "plan.md": "f60e66e26602a0064477ccaee7f7515c03889bf23b0b20ca50844ded804f27d4"
}
```

## G2 — CHANGES REQUIRED, integration acceptance gaps

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed documentary codec/money
signatures,39 acceptance tests and saved34 intended-red/5-control evidence. No
source edits,tests,network/probes. Typed limit/codec ownership and pre-hydration
expanded-cost policy are suitable; repeated byte/node/depth cases exercise real
expansion budgets rather than only wire size.

| Finding | Severity | Required disposition |
| --- | --- | --- |
| FR-M1 promises normalizers-wide missing/rejected/uppercase/conflict semantics, but only Shopify and two CSS examples have acceptance coverage; `_normalize.py` separately defaults Woo(admin/store),Magento,Shopware,schema/OG toUSD | Blocking contract gap | Add representative real-normalizer fixtures for every changed dispatcher branch and explicit invalid-code/lowercase/conflicting-currency cases with exact output and support/path assertions. Native valid codes and direct constructor defaults stay controls. Do not infer that Shopify helper coverage proves separate adapter defaults. |
| Compact success uses codec directly and CLI output is decoded directly, so reader/full-envelope/downstream integration can be forgotten | Blocking roundtrip gap | Feed actual full CLI compact stdout through actual bounded reader/products projection and a downstream command; assert products/Decimal/variant evidence preserved. Add invalid compact input/output atomic target preservation where promised. Avoid a helper-only decode substitute. |
| Skeleton reserves exact $capture_ref objects and promises source-value escaping, but no source-value lookalike case exists | Blocking source-fidelity gap | Predesign and test a legitimate raw captured value resembling {$capture_ref:...} through real encode/decode, including actual provenance position. It must survive unchanged rather than be hydrated/rejected as a transport reference. |

Keep64-case ceiling/one-worker/time/byte limits or explicitly re-review bounded
count expansion; no reason to waive distinct integration coverage. Child02 G3
components/implementation remain gated until repaired G2.

```json
{
  "specs/013-audit-remediation/02-money-roundtrip/skeleton.md": "1e769ec1430c7ddb67b6ee4275d279754af6ef880993e12a47eab2b889161c40",
  "specs/013-audit-remediation/02-money-roundtrip/spec.md": "58a94d55fe8c55eef7ef9e6913d89d8dcfdd5e7ebe5c193a7c83c347909ae095",
  "specs/013-audit-remediation/02-money-roundtrip/test-design.md": "fafef84cd055ca9265e306a573d135f9c9e732d2a6440ee8552639ec9ceb474f",
  "specs/013-audit-remediation/02-money-roundtrip/verification.md": "af2341de80c336b940f4577def21e6942fe3d7028b3600630c344cb8f7d145dd",
  "tests/test_money_roundtrip.py": "9d0a1813394d20b7e01c69a7473bc08a99d4ee7e3f33e54ba42f357ed3bbb2b2",
  "specs/013-audit-remediation/02-money-roundtrip/red-final.log": "af3d70c7dc42b621cb32f1d88effd1645722b702f78557cb9fb890ec4439a433",
  "specs/013-audit-remediation/02-money-roundtrip/red-final.json": "e5822c2a79644863592487fb765b288d57a97fd84982c7b06b246f20f9e33ad7"
}
```

## G2 blocker re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed designed25-case expansion
and updated64-case acceptance file plus saved14 intended-red/11control focused
results. No source/tests/network/probes executed. Prior G2 blockers resolved for
hashes below; components/G3 next, production remains gated.

- Ten separate native/schema/OG/feed dispatch branches now assert missing/valid
  currency and exact source paths; CSS/Shopify controls additionally cover invalid,
  lowercase and conflicting source values with source support.
- Full actual compact CLI output enters bounded reader/products projection and
  analyze-file; Decimal/variant identity/evidence/source-literal checks exercise
  downstream integration. Output os.replace failure and malformed input preserve
  existing targets. Literal $capture_ref survives raw_data and capture values,
  covering source/transport ambiguity rather than trusting codec-only equivalence.
- Prior expanded bytes/nodes/depth and malformed reference contracts remain intact;
 64 is exact current case count and ceiling, no full64-case green claimed. New
 integration red currently stops at missing --compact, so downstream assertions
 must actually execute in green verification and cannot be counted passed now.

Source-backed coverage gaps from previous review are addressed without changing
product expectations to match current behavior. No compact/money implementation
or full-driver/live/final gate is passed by this skeleton review.

```json
{
  "specs/013-audit-remediation/02-money-roundtrip/spec.md": "58a94d55fe8c55eef7ef9e6913d89d8dcfdd5e7ebe5c193a7c83c347909ae095",
  "specs/013-audit-remediation/02-money-roundtrip/test-design.md": "694066f0d7d88ae616e4fd83db61f90d3538abea1ff1792ddda5f151944d802a",
  "specs/013-audit-remediation/02-money-roundtrip/skeleton.md": "c08759690b586b633400e0aef587b49d0d81114d422e5b066ed39af4bf00fd05",
  "specs/013-audit-remediation/02-money-roundtrip/verification.md": "f7f1245c98716fb91c5cbfe7cb1c534a39e24d7efa692a84f2e051c35cd58739",
  "specs/013-audit-remediation/02-money-roundtrip/g2-integration-red.log": "dfe1b4b165906ffa4d72fa1e88468783ea93de36d1e84cda057ae00df57610d4",
  "specs/013-audit-remediation/02-money-roundtrip/g2-integration-red.json": "98874ca4af07918d39f4410a3d096685bfad92cccedd3aee9bfa9a8783656321",
  "tests/test_money_roundtrip.py": "7636774629a00cd7624feb4361b6c7c74025921699fd3c27c038fe34d0a5b191"
}
```

## G3 — PASS, money and bounded compact components

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed component model against
approved64-case G2 contracts. Existing Normalizer outcomes/capture/portable identity
are reused; pure codec owns immutable narrowed limits, canonical hashing, reserved
source escaping and pre-hydration wire/expanded budgets. CLI owns nested envelope
recognition and atomic replacement; no parallel validator/identity scheme/global
cache. Diagnostic ownership remains caller-side and exact source support survives.
No production/tests/network/probes executed by reviewer.

Implementation may proceed in bounded money/codec substeps. Actual64-case green,
expanded-limit mechanism verification, affected/full-driver/live/final remain
pending; no prior full-driver failure waived.

```json
{
  "components.md": "66dd667977d3b62098464625c878cbee34d6cec9cf42f7d5f137e61b048f22a1",
  "skeleton.md": "c08759690b586b633400e0aef587b49d0d81114d422e5b066ed39af4bf00fd05",
  "spec.md": "58a94d55fe8c55eef7ef9e6913d89d8dcfdd5e7ebe5c193a7c83c347909ae095",
  "test-design.md": "694066f0d7d88ae616e4fd83db61f90d3538abea1ff1792ddda5f151944d802a",
  "tests/test_money_roundtrip.py": "7636774629a00cd7624feb4361b6c7c74025921699fd3c27c038fe34d0a5b191"
}
```

## Functional code and node-budget amendment review — CHANGES REQUIRED

Reviewer `/root/audit_plan_review`,2026-11-01. Bounded source/test/doc inspection
only, no new probes/network/full suite. Saved64 acceptance/271focused passes do
not resolve actual audit-output incompatibility or omitted invalid-code cases.

| Finding | Severity | Required disposition |
| --- | --- | --- |
| Normalizer.currency validates only three ASCII letters; QQQ/ZZZ are accepted and observed | Blocking factual-support defect | Add explicit supported currency registry/ISO membership with documented scope/version; reject unknown lexical codes with reason, preserve accepted real codes/source paths and constructor defaults. Predesign QQQ/ZZZ/lowercase-valid cases before repair; do not call regex ISO validation. |
| Actual25-product Allbirds output5425392bytes/193134nodes/depth11 fits bytes but fails current100k node cap | Blocking intended user case | Implement reviewed bounded amendment only after named scanner interfaces, executable intended-red cases and affected gates; real audit reader/product/analyze/export roundtrip is required, not merely padded-string success. Keep hash/provenance labelled historical. |
| Codec unescape interprets exact $capture_ref maps anywhere under data, whereas skeleton restricts transport references to captured provenance positions | Blocking contract validation gap | Enforce explicit allowed reference-location grammar and test out-of-slot refs rejected, or revise/review the behavior contract before accepting arbitrary reference locations. Legitimate source lookalikes must still roundtrip through escaping. |

Positive implementation findings: exact canonical capture hash verification,
escaped source-literal handling, duplicate/nested/cyclic rejection, per-occurrence
expanded cost before deepcopy hydration, immutable narrowed limits and full
CLI/reader/portable/downstream/atomic scenarios are present. No digest is treated
as manufacturer/factual authority. These do not waive blockers above.

### Amendment G1 concept verdict: PASS; G2 remains pending

Raising logical ceiling to1M while retaining32MiB wire/expanded bytes,depth64,
1000products and adding2M lexical/key-token prescan is bounded/proportional to
measured193k-node sample, not an unlimited100-item promise. Repeated-ref expanded
limits and preallocation dense-input rejection are essential. G2 must name scanner
signature/token-count convention and provide executable red boundary/escape/dense
input/real-audit roundtrip cases before cap changes. Final parse remains strict;
preflight must count keys and values without treating escaped string content as
structure. Memory256MiB remains measured fixture target, not proven universal cap.

No amendment G2/G3, repaired functional pass, full-driver/live/final completion is
recorded. Prior full-driver timeout and missing-family/live gates remain open.

```json
{
  "src/shopextract/_normalization.py": "56412344addb44ab4d391c4ab06098bd5d9604f033e495acbf1e5e9696f421d2",
  "src/shopextract/_compact_catalog.py": "b87b7cba91579e32d33ef7d432eba7c4223919d4680bd4c7062683b695d8f980",
  "src/shopextract/_normalize.py": "e3eee84606233d953af7de2c6a813deb45330800fa4d81a4e65ad6d837135f0a",
  "src/shopextract/_cli_data.py": "53932c0cf39c126c3a9d892e9af0176c77ee140d932615171ea2de946700d4ee",
  "src/shopextract/_cli_extract.py": "004596e9ffda2d0b6b8a5d5469868732e42af83e975c01e3f96d1a9fb7bd8275",
  "tests/test_money_roundtrip.py": "7636774629a00cd7624feb4361b6c7c74025921699fd3c27c038fe34d0a5b191",
  "specs/013-audit-remediation/02-money-roundtrip/node-budget-amendment.md": "38b48fbcf2478fef41208982b2196ca697f5fd537cb498551122fc2232cc0b32",
  "specs/013-audit-remediation/02-money-roundtrip/actual-audit-shape.json": "fa43addfb8ff5beca4675606f531ea36b81d61d312a32dfeeeee290f8a6d3f5a"
}
```

## Amendment G2 — CHANGES REQUIRED, one remaining preallocation seam

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed exact JSONShape scanner
signatures,17 new cases, saved16red/1control and3focused forbidden-slot reds, actual
audit reader/projection diagnostic, resolved SIX metadata/XML. No new fetches,
probes/tests/full suite/source edits. Prior TLS blockage is historical: pinned
publication2026-09-17/hash and178 assigned codes are now inspectable; XXX/XTS
rejection is explicitly pricing policy rather than fabricated ISO nonmembership.

One blocking coverage gap: dense-input-before-decoder case exercises read_json_file
only. Direct decode_compact_catalog is an independent consumer that currently
allocates via json.loads; reader-only preflight cannot protect direct callers.
Add one actual direct compact decode dense-value/key fixture with full json.loads
prohibited, asserting budget ValueError before decoder allocation. No replacement
scanner/codec algorithm, no enlarged memory/time/worker budget. This is a distinct
entry-point invariant, not extra random variation.

Other amendment interfaces/expectations are sound: tokens=values+keys and explicit
root-depth convention,1M nodes/2M tokens with byte/depth ceilings, escaped structure
control, portable-budget alignment and native-category default compatibility.
Real product title/price/raw attribute reference slots now meaningfully challenge
transport location grammar. A new registry/limit implementation must still execute
all17+newcase and64 earlier acceptance checks; no existing green claim transfers.

Actual audit diagnostic currently validates reader/products/count/first price,
not actual analyze/export/variant/evidence roundtrip. It is correctly labelled
reader diagnostic; keep remaining real-source assertions as mandatory green/final
evidence, never promote its eventual success to complete roundtrip proof. G3
amendment/components and production remain gated pending this last G2 case.

```json
{
  "specs/013-audit-remediation/02-money-roundtrip/node-budget-amendment.md": "83ebdf2805eb246571f9c36940dbd380e305f4c13a64db629e02d995e71b265f",
  "specs/013-audit-remediation/02-money-roundtrip/skeleton.md": "0cb3e308d30641b37912f91dfec23eebc6b71bfd11019bd21b7b4a4788748862",
  "specs/013-audit-remediation/02-money-roundtrip/test-design.md": "38f41c80a09328f1586c1fd75941e6ebd167af911bd4cb2da9a4b1a0f52fada1",
  "specs/013-audit-remediation/02-money-roundtrip/verification.md": "1ba59708cecb0f543487781367cbf3a0e95d0d66d9474a34880098984a632ba2",
  "specs/013-audit-remediation/02-money-roundtrip/iso4217-source.xml": "33139b438657d1cee116ba737807ea71d19d6de4b90f799a09c56f0cc6a1b0ff",
  "specs/013-audit-remediation/02-money-roundtrip/iso4217-source.json": "af8e81933d5cbbc76dd6b6a37c200616d4afc89fb069b831ffba1b1e4cef4925",
  "specs/013-audit-remediation/02-money-roundtrip/amendment-red-full.log": "326d6352f20211a3ee38a47d0a8e18b5de621b8d0d8a6604920eca226959f7ba",
  "specs/013-audit-remediation/02-money-roundtrip/amendment-slots-red.log": "3f78b3bd04c2704d131f9d1c05934c8d5cd645be6fad32d9a78e90f4ffae1958",
  "specs/013-audit-remediation/02-money-roundtrip/actual_audit_roundtrip.py": "4315ecdff1ca3853f7b32a0eb755a422b233dbcad53ba9307b9de9f54062471a",
  "tests/test_catalog_budget_amendment.py": "f39a1ff1daa5914c5f530daaf387d2195bde1d217e7d419f105e322c39990051"
}
```

## Amendment G2 direct-codec repair re-review — PASS

Reviewer `/root/audit_plan_review`,2026-11-01; inspected added direct compact
dense fixture and saved one intended-red report. Direct decode_compact_catalog
now has an executable assertion that prohibits full JSON allocation before lexical
rejection, independent of read_json_file. Existing17-case contracts retained;
18-case amendment budget remains bounded. No new test/probe/network/source edit.
Prior G2 blocker resolved. Amendment component author/G3 next, no amendment
production or eventual actual-audit roundtrip pass implied. Final audit diagnostic
prepares reader/analyze/export/reload/evidence assertions but remains unexecuted.

```json
{
  "specs/013-audit-remediation/02-money-roundtrip/skeleton.md": "23fb98d3f16fe56bec74904e6b06966ff3fd0650f97fbae13408a77071b9963d",
  "specs/013-audit-remediation/02-money-roundtrip/node-budget-amendment.md": "83ebdf2805eb246571f9c36940dbd380e305f4c13a64db629e02d995e71b265f",
  "specs/013-audit-remediation/02-money-roundtrip/test-design.md": "5805cc9146f3385eacb4b392217524c34ad28bfcc878571b9f2ca1990dc89c01",
  "specs/013-audit-remediation/02-money-roundtrip/verification.md": "e71de3584970d7c3ddf4c6fae59abf0586eb7cea64809a2db016cdbd7c786f7c",
  "tests/test_catalog_budget_amendment.py": "e87c21a1314cd09671dff41cad969d1029134ff3c668a57552b912f620fa852f"
}
```

## Amendment G3 — PASS, bounded preflight/registry/reference ownership

Reviewer `/root/audit_plan_review`,2026-11-01. Inspected amended components
against approved scanner/registry/slot signatures,18 amendment+64baseline contracts
and saved official SIX metadata. No author implementation, probes/tests/network.

Shared pure preflight precedes full decoder in both independent consumers; catalog
1M logical nodes remains separated from protected native category limits and
portable/default validation allowances. Pricing registry is immutable/offline and
source-pinned; existing conversion outcomes retain conflicts and actual source
paths. Existing compact codec owns path admission/escaping, canonical hashes and
per-occurrence expanded cost before hydration; no duplicate serializer, cache or
lifecycle. CLI still owns typed errors/record projection/atomic replacement.

Minor reviewer documentation repair clarifies original100k component paragraph is
historical/superseded for catalogs and final amendment count18. No behavior or
interface change. Functional implementation may proceed against reviewed tests;
actual audit analyze/export/reload/variant/evidence diagnostics still need execution.
No full-driver/live/final verification pass, no native-limit enlargement approved.

```json
{
  "specs/013-audit-remediation/02-money-roundtrip/components.md": "4deb62cf0654f634a0ba5185ff054d17c2e3b63e156ffbc505a0b5331012a1d2",
  "specs/013-audit-remediation/02-money-roundtrip/skeleton.md": "23fb98d3f16fe56bec74904e6b06966ff3fd0650f97fbae13408a77071b9963d",
  "specs/013-audit-remediation/02-money-roundtrip/node-budget-amendment.md": "83ebdf2805eb246571f9c36940dbd380e305f4c13a64db629e02d995e71b265f",
  "specs/013-audit-remediation/02-money-roundtrip/iso4217-source.json": "af8e81933d5cbbc76dd6b6a37c200616d4afc89fb069b831ffba1b1e4cef4925",
  "specs/013-audit-remediation/02-money-roundtrip/iso4217-source.xml": "33139b438657d1cee116ba737807ea71d19d6de4b90f799a09c56f0cc6a1b0ff",
  "tests/test_catalog_budget_amendment.py": "e87c21a1314cd09671dff41cad969d1029134ff3c668a57552b912f620fa852f",
  "tests/test_money_roundtrip.py": "7636774629a00cd7624feb4361b6c7c74025921699fd3c27c038fe34d0a5b191"
}
```

## Amendment functional review — PASS for implemented repairs; verification incomplete

Reviewer `/root/audit_plan_review`,2026-11-01. Inspected actual prescanner,registry,
codec path admission,catalog/native bounds and actual audit comparison script/report.
No new probes/tests/network/full suite/source edits. Saved82 acceptance pass is
valid scoped evidence; original120s timeout/one optimized scan repair remain saved.

Previous code blockers resolved: assigned offline currency membership replaces
three-letter acceptance,XXX/XTS policy explicit; direct compact and legacy JSON
consumers preflight before full decoder,1M values/depth/byte bounds enforced;
unescaped reference slots restricted before hydration,source literal escapes
retained. Expanded per-occurrence costs still precede deep-copy hydration,exact
canonical hashes retained. Native Woo category default/check stays independent
of catalog cap. Final strict JSON decoder remains syntax authority; scanner is
allocation-light budget guard,not replacement JSON parser.

Comparison equivalence review: actual-audit script compares every decoded Product
dataclass field (variants as complete dataclass dicts) with original record values,
and separately compares entire encoded product/variant evidence-contract dicts,
including captured source values. This preserves exact value/support comparison
without repeatedly recalculating portable trust projections; no weakened expected
assertion found. Analyzer validates25 count. Source SHA/provenance are retained.

**Actual source final roundtrip remains incomplete:** report explicitly timeout
at export after30s; sidecar reload/export equality is NOT verified. Reader/evidence
and analyzer success cannot stand in for that remaining stage. No retry/budget
increase inferred. Future export work can address cost,then scoped re-verification.
Full-driver/live/final gates remain pending independently; no02complete verdict.

```json
{
  "src/shopextract/_bounded_json.py": "0f4c29498a9692d7672f9200e3d158633e4156dded8e2e924dc9a05bf370079b",
  "src/shopextract/_compact_catalog.py": "f32909e36864c57980bdf96f8c2290d8e65c4a35c34be5cb835c8e850f060e77",
  "src/shopextract/_currencies.py": "77d3ecac383299bc0cf4d29dbc69003ffc7b6101cd27330aa2a770f598fe4563",
  "src/shopextract/_normalization.py": "8cc5d3c78c9b9e8848e7e17adfcd365317fb6832df4c75c31a4582fff0c0083e",
  "src/shopextract/_cli_data.py": "496ab9ecc60b296adaee9065bc30eac28b74b6cbbbd00868c12ffff5f8e7fca1",
  "src/shopextract/_cli_categories.py": "17569edfc45e63fbd78edc37e8699c4611e8bb7bc24008636aa6bce80c7723d4",
  "tests/test_catalog_budget_amendment.py": "e87c21a1314cd09671dff41cad969d1029134ff3c668a57552b912f620fa852f",
  "specs/013-audit-remediation/02-money-roundtrip/actual_audit_roundtrip.py": "ce650e13d62a6f69f1c22706438917f8bfe77d4c662d4bc48ff274d4f5b46f5b",
  "specs/013-audit-remediation/02-money-roundtrip/actual-audit-roundtrip.json": "bd0b4b3ecfc561003641adfcec425c489df6d0b13815e5775fed4083971a4621",
  "specs/013-audit-remediation/02-money-roundtrip/verification.md": "023438a29153593519526bbdbc5c1f1dd6a72216adbf8a5731a353a39a9fc67b"
}
```
