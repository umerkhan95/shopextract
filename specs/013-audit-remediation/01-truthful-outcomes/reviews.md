# Child01 independent reviews

## G1 — PASS, behavior/test/task/research planning

Reviewer `/root/audit_plan_review`,2026-11-01, source baseline90d5bd1.
Reviewed all five artifacts below and spot-checked `_cli_extract.py:128–172`,
`_models.py:129–151`, `woocommerce.py:51–65`, `_schema_org.py:126–155`,
`unified.py:90–115,230–264`, `_normalize.py:692–730`, `_opengraph.py:19–80`,
`tools/sources.py:105–194`, `tools/domain.py:130–143`. No production edits,
network requests, tests, inference or subagents during this review.

Verdict: PASS for this child G1; no blocking design findings. This is not G2/G3,
implementation acceptance, live proof or final approval.

| Finding | Severity | Disposition |
| --- | --- | --- |
| Exact synthetic parameter bookkeeping not yet enumerated;41 is budget maximum, not collected coverage | Minor | Reviewer clarified test-design.md; author must enumerate concrete sets at red-test stage before claiming counts. Check both batch/single and actual tool parse/source/domain seams, not only shared helper. |
| One browser crawl can generate many navigation/subresource requests, so crawl count alone cannot establish12-request bound | Minor verification-plan ambiguity | Reviewer added explicit request accounting/interception requirement; if unenforceable, browser live case is blocked, never unrestricted or reported passed. |
| Exit3 on discovery/unknown HTML and source_error on empty native tool catalog intentionally change former behavior | Compatibility observation | Explicitly specified with retained partial data and unchanged enums/constructors. Regression updates must cite this contract; atomic-file preservation and tool graph parity have dedicated scenarios. |

Distinct risks covered: empty/unknown/contradictory completion, discovery-vs-extract
empty meaning, later-page404 after progress, transport status separate from crawler
success, policy metadata rejection without rejecting legitimate zero/free product,
atomic-file outcome parity, conservative tool-native semantics and terminal-page
positive controls. Static HTTP status control and actual native auxiliary parser
path are required in test design. Missing status fails closed by explicit decision.
No price/currency/field/runtime expansion is approved in this child.

## Reviewed SHA-256

```json
{
  "spec.md": "3bdc5ff4037e1d17c88c03c88ea50a2d990245e57f7f7487cd6086d3f182596e",
  "test-design.md": "8bd7cd3c74d26ed657e677376bd000cd4346e7aa47f8e4613f8afd1485145743",
  "tasks.md": "2df7ca8a4ae0c21a45c67f20e76511bef522db20e0edcdb4fab7b2979ff3e7c2",
  "research.md": "8a33b9b983d04a64dc360f07abaaed9cc70e4d1422070d5874ea523390ec09a2",
  "plan.md": "6a54c3acd5a4eca964f1ed36303b8edd7e4533bfc62b7af23e73cf3e5bbddfbe"
}
```

## Pending gates

G2 skeleton and executable intended-red acceptance evidence: pending.
G3 components/revised skeleton: pending.
Implementation, complete offline checks, bounded live observation and independent
final review: pending. Next owner author creates skeleton and red tests.

## G2 — CHANGES REQUIRED, documentary skeleton and acceptance reds

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed skeleton, all41
acceptance cases, actual red logs/metadata and source extraction/feed seams. No
tests executed, no source changes, no network or subagents. Initial red harness
failures are honestly excluded; repaired run reaches intended assertions. Latest
seeder fixture change has focused two-case evidence, not a fresh41-case result.

| Finding | Severity | Required disposition |
| --- | --- | --- |
| FR01b explicitly includes feed/catalog emission, but no acceptance case exercises `extract_feed`; it currently has its own duplicated partial predicate at `_cli_extract.py:209` | Blocking coverage gap | Add bounded real feed transport/CLI tests for empty, positive unknown and capped output, or explicitly narrow the reviewed contract through design change. The shared outcome helper test alone cannot catch a forgotten feed projection. Save intended-red evidence. |
| SC03a promises Woo later404 -> pipeline/CLI retained partial data, but only the direct adapter is exercised | Blocking integration gap | Add controlled Woo100 then404 through real pipeline/CLI, assert100 retained, page-specific error and partial exit/envelope; include successful terminal source control with conservative pipeline coverage. Do not replace pipeline/adapter mechanism with fabricated results. |
| Shared assessment/admission/gate names and ownership remain unnamed in skeleton | Minor contract clarity | Before implementation name planned module/functions and typed signatures, preserving pure dependency direction; G3 may refine reuse but should not invent the G2 integration seam afterward. |

The41-case cap is a resource ceiling, not a reason to omit uncovered contracts.
Revise the bounded count to accommodate distinct cases if needed, preserving one
worker/time/byte caps; update affected design count and independent review.
Crawler/transport/DNS/seeder doubles otherwise stay at external boundaries; real
normalizers, parsers and native runtime/domain are exercised. G3 and implementation
remain pending until blockers resolved.

### G2 reviewed SHA-256

```json
{
  "specs/013-audit-remediation/01-truthful-outcomes/skeleton.md": "9e789b0b2a179a366316ce7556a1edad8bc029ef78fe34243240d0aceb267291",
  "tests/test_truthful_outcomes.py": "ceeb76d798c7f9d3b001a565a1423fc90ef90391c5a3b507f774cca2858b0284",
  "specs/013-audit-remediation/01-truthful-outcomes/verification.md": "56458addde1c34c2166cfec44609ae91d119c80f855cf2c6b0c4a4484a5b1fa3",
  "specs/013-audit-remediation/01-truthful-outcomes/red-repaired.log": "ff210f6603538a36fc5383abc1558ff6c386ad40084e414c8503fff39326f0c2",
  "specs/013-audit-remediation/01-truthful-outcomes/red-repaired.json": "0b72ad8888457fbf2f8e16970cbb1a68d7ef73cb4cb16b5a5209f6ef3b402d1a",
  "specs/013-audit-remediation/01-truthful-outcomes/red-discovery-fixture.log": "8974caef42bacab1fd952f6c01a201719373feaf7bc605a17c93c3d95ad30af5"
}
```

## G2 re-review — PASS, repaired integration coverage

Reviewer `/root/audit_plan_review`,2026-11-01. Scope: prior G2 findings only,
latest named skeleton,46-case acceptance file, revised test design/tasks and saved
five-case focused evidence. No tests/source/network/subagents executed by reviewer.
Prior changes-required verdict remains historical; this verdict supersedes it for
reviewed hashes below. Added SC01c/SC03c refine existing FR01b/d behavior rather
than adding scope, so the corresponding design delta is also accepted.

- Feed gap resolved: real CSV transport/from_feed/normalization/CLI empty, positive
  unknown and capped paths; no fabricated pipeline outputs. Focused unknown-feed
  failure is intended; empty/capped positive controls pass.
- Woo pipeline gap resolved: real100-record adapter->pipeline->CLI with later404
  versus empty200, retained normalized/raw IDs and two-request invariant, distinct
  error/coverage metadata assertions. Current incorrect exit fails first; later
  assertions must be exercised in green verification, not counted passed now.
- Ownership clarified: typed private `_outcomes.assess_extraction_outcome`,
  `_product_admission.has_product_evidence`/`crawl_document_allowed`, stdlib-only
  dependency direction, specified model/CLI/feed/tool/browser consumers.

Saved red-g2-seams evidence:3 intended failures,2 passing controls,41 deselected.
No full46-case red run claimed. Before stress, update exact enum/budget inventory
for added seam cases; no stress pass exists. Verdict allows component design next;
G3 remains pending and production implementation remains gated.

### G2 re-review SHA-256

```json
{
  "specs/013-audit-remediation/01-truthful-outcomes/spec.md": "3bdc5ff4037e1d17c88c03c88ea50a2d990245e57f7f7487cd6086d3f182596e",
  "specs/013-audit-remediation/01-truthful-outcomes/test-design.md": "d1b7e9a7dfb4750bd4810d6de0f1fd3ef021cb6f17de4f9cc0995805c77973ed",
  "specs/013-audit-remediation/01-truthful-outcomes/tasks.md": "bd3670f5015409c033dff4d76dabd20012bbb14a522e64198802e81f121dff9d",
  "specs/013-audit-remediation/01-truthful-outcomes/research.md": "8a33b9b983d04a64dc360f07abaaed9cc70e4d1422070d5874ea523390ec09a2",
  "specs/013-audit-remediation/01-truthful-outcomes/plan.md": "6a54c3acd5a4eca964f1ed36303b8edd7e4533bfc62b7af23e73cf3e5bbddfbe",
  "specs/013-audit-remediation/01-truthful-outcomes/skeleton.md": "f9579145d08fbff13d39a986bc27945dcb2523ec3ddf08c812e3629e6cb9a4c0",
  "specs/013-audit-remediation/01-truthful-outcomes/verification.md": "20d9f702d1413ff5ac87b79a0df37b76ffd40afb879db2296ccbab7d8ab490ed",
  "specs/013-audit-remediation/01-truthful-outcomes/red-g2-seams.log": "8fc74bb8e7650a95bc511a61a2da9a6ca93f99d9f524f189a09e1dd0f78566a6",
  "specs/013-audit-remediation/01-truthful-outcomes/red-g2-seams.json": "781cef5471d0b5f65e8dc6d4362dc0b97c9a53b49edd3b1f02c84a1a0fe92200",
  "tests/test_truthful_outcomes.py": "40e96a1e500484d941d50e376f76b3c19419fc79a234f3764f9c3d805fc6b89c"
}
```

## G3 — PASS, reusable components and ownership

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed components against G2
skeleton/signatures, accepted behavior and46-case acceptance scope. No source
implementation, tests, network or subagents executed during review.

Verdict PASS. Shared assessment has concrete model/CLI/feed/tool consumers; shared
admission/HTTP gate has static/browser/normalization consumers. Helpers remain
pure stdlib-only and privately scoped, with caller-owned diagnostics, transport
and cleanup. Existing capture/Normalizer/portable identity and atomic emission
components are reused; no parallel lifecycle or speculative policy framework.

One minor compatibility clarification added by reviewer to components.md: generic
HTML/metadata admission must not blanket-reject native/feed/portable formats that
lack OG/schema keys. This reiterates accepted native-source validity and preserves
G2 feed controls; it adds no new behavior or interface. Implementation must verify
this via existing affected normalization/feed regressions.

G1/G2/G3 now pass for reviewed artifacts. Implementation is next; no green/stress/
full-driver/live or final-review pass is implied. Added seam stress inventory must
be finalized before stress; source status/zero/metadata distinctions stay mandatory.

### G3 reviewed SHA-256

```json
{
  "components.md": "cf5928da713e598fd872bf2d926073fa6eb14fe61dd58388236cced095d8b04a",
  "skeleton.md": "f9579145d08fbff13d39a986bc27945dcb2523ec3ddf08c812e3629e6cb9a4c0",
  "spec.md": "3bdc5ff4037e1d17c88c03c88ea50a2d990245e57f7f7487cd6086d3f182596e",
  "test-design.md": "d1b7e9a7dfb4750bd4810d6de0f1fd3ef021cb6f17de4f9cc0995805c77973ed"
}
```

## Implementation/final review — CHANGES REQUIRED, feature incomplete

Reviewer `/root/audit_plan_review`,2026-11-01. Reviewed actual production diff,
new pure modules, acceptance/stress code and saved full-driver status. One small
synthetic production parser/emitter probe, no network/models/source edits; results
in review-probe.json. All source hashes below identify this reviewed revision.
G1/G2/G3 historical approvals do not pass final implementation or verification.

| Finding | Severity | Required disposition |
| --- | --- | --- |
| `_product_admission.has_product_evidence` recognizes only exact Product while existing SchemaOrgExtractor intentionally supports/enriches ProductGroup; new unified filtering drops valid named groups | Blocking regression | Preserve explicitly supported ProductGroup typing without restoring arbitrary substring type acceptance. Design regression cases for static/browser and typed-list/URL forms as appropriate. Probe: schema count1, unified count0 for ProductGroup with priced variant. |
| `_cli_extract.emit_result` now rejects any products=[]; normalize_file also calls it, changing empty normalization from successful empty/dropped-index report to E_OPERATION | Blocking scope/compatibility regression | Restrict failed-empty extraction semantics to extraction/feed callers or obtain an explicit reviewed normalization behavior change. Add empty/all-dropped normalize controls to prove unrelated projection remains compatible. |
| `UnifiedCrawlExtractor.extract_batch` marks rejected transport incomplete, but HTTP200 metadata rejected by parser/admission leaves complete=True/error=None, including mixed good+policy batches | Blocking contract gap | Record failed product admission as incomplete with useful diagnostic and retained good siblings, as components.md promises. Add mixed valid/policy and missing/blank product-evidence cases; do not treat every HTTP200 as admitted product. |

Existing positive architecture: shared pure assessment avoids envelope-enum expansion;
CLI file classification precedes replacement; generic OG guard reuses source policy;
Woo404 preserves adapter records; native empty extraction no longer retains empty
catalog handle.46 acceptance and10 status mechanisms reportedly pass but omit the
three interactions above; they do not override these findings.

### Verification gates still incomplete

Required full repository driver reports timeout in main group (~239s), only~67%
progress and4 failures whose tracebacks were not saved before termination. This is
a failing gate, not a partial pass. Collection diagnostic30s also timed out. Native
oracle and maintenance families were not run after main termination. Actual live
verification has not run. No claim of full regression, whole mechanism/stress
coverage, live behavior or feature completion is justified. Resolve concrete code
findings first, diagnose the four failures within existing bounded-repair policy,
then rerun only appropriate checks before the mandatory complete driver/live gate.
If unavailable, retain explicit incomplete status and saved evidence.

### Reviewed implementation SHA-256

```json
{
  "src/shopextract/_outcomes.py": "bb41ec82c26f0fd7a7417075b3f907d0a8771f838483bbae58f96681cd5b1dcf",
  "src/shopextract/_product_admission.py": "7c9271512c10bf83befc75c16f0eed91d1a6ad2125e8e28bef7734d076587556",
  "src/shopextract/_models.py": "82f6a785ad0ab7b7afb7ccd8e3b1d3a0ba1da60f1e7cb25cc991dc5fded7438a",
  "src/shopextract/_cli_extract.py": "77b3bb1464f89cc73f944669f0ab5329fea769a220c24f1ff6f95d0cfe6bc03f",
  "src/shopextract/_normalize.py": "a275581143f664f1691c1ee417e45ca62b46c5a19799510428c1147645bf7c20",
  "src/shopextract/extractors/unified.py": "16926558a64f2bbd5f9e78549275784800dffee0f2fc4efe73f6a88b16e1f931",
  "src/shopextract/extractors/woocommerce.py": "7031c1f232a6aba357951a4cd38559081b8474b6eacf211a55492932029a282c",
  "src/shopextract/tools/sources.py": "6f6cc4537e326881f7fa4f754a66a10d5059e27105ca8676ad2342aec8f68970",
  "tests/test_truthful_outcomes.py": "40e96a1e500484d941d50e376f76b3c19419fc79a234f3764f9c3d805fc6b89c",
  "tests/test_truthful_outcomes_stress.py": "a9d357195cd0c639ad8d19815da6cdd11f1ff3f88a307578e2af39629221b474",
  "tests/test_cli_extract.py": "5d618a93a062a5e976a8e97ac401c795275f9ba50e9bd32ebb8844ad1fde3f39"
}
```

## Implementation re-review — three functional blockers resolved; FINAL PENDING

Reviewer `/root/audit_plan_review`,2026-11-01. Scope strictly prior three code
findings, new regression cases and saved repair evidence. No additional probes,
tests, network or source edits. Reviewed hashes below.

Functional verdict: **PASS for the three repaired findings**, not feature completion.

- Named ProductGroup, list and schema URL forms now pass exact-token admission;
  static/browser controls preserve prior support. Substring impostor is rejected.
- Empty failure is limited to extraction/feed call sites; generic emit_result no
  longer rejects normalize output. Empty/all-dropped normalization controls
  preserve products=[], count and dropped indices while extraction still fails.
- Browser batch HTTP200 with no admitted product now records incomplete/error and
  retains legitimate siblings. Policy and blank-name fixtures exercise the actual
  parser/aggregation path, not a fabricated admission result.

Saved evidence reports57 acceptance +10 status cases passing. Broader repair run
reports216 passing,6 failing: legacy native helper jobs did not finish within100
polls; no claim that these are baseline-only, harmless or functionally passing.
Reviewed child native tests complete with separate bounded10s polling; that does
not repair or waive the six affected regression failures.

Final gate remains pending: previous required full driver main-family timeout and
its unresolved failures, no complete oracle/maintenance family result, no actual
live check. No final acceptance/merge readiness or feature-complete verdict. Any
continuation to other authorized slices must carry these unresolved verification
items in status rather than treating this focused functional pass as completion.

### Repair re-review SHA-256

```json
{
  "src/shopextract/_product_admission.py": "f8d35af064b74c884ba73dc650450bed693a79448de3e934c9018fc40526da9d",
  "src/shopextract/_cli_extract.py": "3e1eb0662d8d3457ebe627a1c5f32d6e0e60be8a3b2389f3051e222e88db1020",
  "src/shopextract/extractors/unified.py": "ee8efc7fc9360ff21c3a5ebb41847f01199961c87195a049e24476b885f53053",
  "tests/test_truthful_outcomes.py": "2f4e4d93fedee3b1f863410f4604303b7ca55439ec1461af4654ab1e1f8b2877",
  "specs/013-audit-remediation/01-truthful-outcomes/spec.md": "cc615b32f091bf0e0fdc71bd1bb152f142ff098fe668f23153b7acae710f8b14",
  "specs/013-audit-remediation/01-truthful-outcomes/test-design.md": "1808998ad7dbb62c2d10d9a8b70b3bdde2ffa7c43a113ec4ccbea87ad03c4277",
  "specs/013-audit-remediation/01-truthful-outcomes/verification.md": "b28888afd2fd88d7cd1fd8b3fb389ae9f83faef66ee78ee0fcf895d8502572c9"
}
```
