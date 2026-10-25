# Independent P0 G1 review

Date: 2026-10-25. Reviewer: `/root/cli_p0_review`; author: `/root/cli_p0_author`.
Scope: DESIGN ONLY, core freeze, schemas, native legacy baseline, capability
classification and planned acceptance. No production implementation reviewed.
Parent spec/test-design/plan/coverage and repository workflow/constitution read.

**Verdict: CHANGES REQUIRED.** Three blocking design findings below. G2/G3,
runtime red/green, mechanism/stress and final review remain pending. This review
neither claims CLI parity nor approves reserved P1–P5 domain contracts.

## Findings

### R1 — blocking / P2: response schema does not enforce frozen error invariants

`response.schema.json` accepts `ok=false, completeness="unavailable", data=null,
error.code="E_PARTIAL"`. Spec FR03 and contracts exit 3 require partial data and
completeness partial for that code. It also accepts E_USAGE with retryable=true
and E_TIMEOUT with retryable=false despite contracts.json's exact retryable table.
These are concrete schema witnesses saved in `evidence/reviewer-design-checks.json`;
all three unexpectedly validate under installed Draft202012Validator.

Required: enforce the inverse E_PARTIAL implication and error retryability in the
machine schema (or explicitly redefine schema scope and provide an equally exact,
reviewed invariant validator contract). Add negative schema test design for these
witnesses and positive examples for each frozen status/error class. No runtime
implementation requested at G1. Disposition: OPEN.

### R2 — blocking / P2: bootstrap and duplicate-format machine routing are ambiguous

The spec says help/version resolve first, help wins over invalid root values,
unknown commands stay invalid, and both help/version use historical text. It does
not select output for `--version --help` versus `--help --version`, nor state how
that interacts with an unknown command. More materially, repetition must yield
E_USAGE, but `--output-format json --output-format legacy detect URL` satisfies
both the valid-explicit-json and valid-explicit-legacy routing rules. There is no
unique stream/envelope outcome. An invalid explicit output format plus valid JSON
environment also has no explicit outcome: the documented fallback starts with
"Without an explicit output-format option" while the explicit option is invalid.

Required: freeze a small exact bootstrap/routing decision table, including both
help/version orders, unknown command, repeated/conflicting output options, invalid
explicit format with JSON environment, and an option-looking operand after `--`.
Define which help token is recognized as an option so a positional `--help` does
not silently bypass validation. Add distinct SC03/SC05 expected outputs/exits and
no-read assertions. This concerns core grammar only, not reserved domain syntax.
Disposition: OPEN.

### R3 — blocking / P2: symbol labels are complete but classification/traceability is not

Source digest checks match all 92 records and the native nine-command baseline.
However, the audit labels every public MaintenanceEngine/MaintenanceStore method
as workflow, including `MaintenanceEngine.now`, `hook`, `close`,
`MaintenanceStore.acquire/release/close`, and `ToolRuntime.aclose`. These are clock,
callback or lifecycle mechanics, not independent operator workflows. The literal
module parent_target "maintenance"/"tools" has no phase or specific parent mapping,
while test-design SC06 requires every workflow to have phase/target. Blanket
name-based rules also classify `TrustContract.validate` as workflow by collision
with marketplace validate; category config/codec helpers remain workflows despite
FR07 calling them composed helpers. Extractor classes are labelled data_schema by
capitalization, obscuring executable adapter roles. These labels do not establish
reviewed workflow coverage or explicit helper exclusion rationale.

Required: correct these concrete misclassifications, use explicit grouped
rationales/phase/target links for actual workflows and helper families, and audit
that every workflow resolves to such a link. Grouped explanations are fine; no
384-item prose expansion or later-phase flag freeze is required. Distinguish
library adapter mechanisms, lifecycle and injection from operator workflows.
Correct the FR07 claim that signatures are saved unless the artifact actually
records them; reserving signature inspection to each phase is sufficient here.
Disposition: OPEN.

## Checks and limits

- Read actual source declarations/dispatch for all nine native root commands;
  saved baseline source SHA256 matches. No default/alias removal found.
- Reviewed precedence flags > selected file > environment > defaults, strict
  JSON configuration (including overridden values), version string "1.0", core
  ok/data/warnings/error.retryable shape, exit 4 validation, no tool trust grants,
  and honest reserved domain/payload/streaming work. These choices agree with the
  parent contracts, subject to R1/R2.
- One bounded local Python/jsonschema probe checked three negative response
  examples and all saved source digests; exit 0, <1s. Evidence records unexpected
  acceptance as findings, not runtime success.
- No installs/network/models, source execution, production edits, delegates or
  live claims. Actual session token counters unavailable. Runtime mechanism and
  synthetic stress execution belongs after G1/G2/G3; design syntax checks cannot
  substitute for it.

## Reviewed artifact SHA256

Digests below identify this reviewed revision. Changes invalidate affected findings
and require an independent follow-up; they do not automatically become approved.

| Artifact | SHA256 |
| --- | --- |
| `spec.md` | `c589bb85d77a2af725a369ddcb6ab89ec5c7a14bfedbdca52e6173a10f2a44f4` |
| `test-design.md` | `e9fdc78eddeb2116ee89b0500eb6f4e90835795550ba27a368dcc61ed63d89ad` |
| `tasks.md` | `27a09e8445689609eb44d3999fbbbd84e0ff27bf22e97634c1c345aaf9bc39a9` |
| `research.md` | `52ee0484b4cd370ef896398aa2bb0a0a54ba2202cfaaab9701509bf2fc7811d9` |
| `plan.md` | `c149882d29d3611b149aa5c54579cb556d8d4a612bf64cc644f82a78f3e4dead` |
| `contracts.json` | `a115521926cc488e7ef8667c85867ff71b1c641b6642b65a7a9c63633ce9c885` |
| `config.schema.json` | `d2cfdc3c4ec364832fa340e86e3520733005f669e25e1c873f78ca403615395d` |
| `response.schema.json` | `a6d151eed76cf68a24567431cd976295116c12d5524c118fe1bc006e1854f299` |
| `command-baseline.json` | `6dbb592fea817148992dfe41c8b5848278c42bb6f17d26c7869bd0c6d98426d4` |
| `capability-manifest.json` | `e7ecdbc6e5417256d388528ba31958926eb1f1555cea5a54069f0a6d6942b286` |
| `status.md` | `0b6db9b2f2d129b9c6fee9091eab513ad19b25660c5525e64bae01186478ef91` |
| `verification.md` | `f4328acd688741b71940f784a414242e471c06b22c371dd966d5537c8da9b18e` |
| `evidence/audit-design.py` | `235f9f51e7da7158ece993a0e73ede4be6c4dfd5b58ac6d5e84a5e40b01f8bcb` |
| `evidence/audit-summary.json` | `9447cd351142d4ffa8a56c4bb89dcda6f99d165b881b2810d98a5de123cbb51b` |
| `evidence/reviewer-design-checks.json` | `64e7f270318417f2600047084ecfba66eea5a1abb2bc82681dd24bc06ac31c39` |

## Focused author repair disposition — re-review pending

Author `/root/cli_p0_author`, 2026-10-25. Original reviewer findings, witnesses and
digests above are preserved. This records attempted corrections, not approval.

- R1: response schema cross-constrains every frozen code's retryable and
  completeness values; E_PARTIAL cannot accompany unavailable/null data. Added
  positive examples for success/every code and negative inverses/reviewer witnesses.
- R2: contracts.json bootstrap rules and B01–B15 specify recognized option tokens,
  operand/`--` boundaries, help-before-version, unknown command/option priority,
  first explicit format selection, invalid-first fallback, exact streams/exits and
  no-read bootstrap behavior. spec/test design now link the same table.
- R3: explicit class+method workflow allowlist replaces blanket method-name rules.
  Clock/hooks/protocols are Python-only; storage/resource lifecycle and category
  config/codecs are composed helpers; TrustContract.validate is schema validation;
  extractors are adapter implementations. Each workflow has phase/target/rationale;
  helper groups have parent/rationale. Native signature inspection is reserved.

Executed only design checks: 22 schema examples (including all three original
invalid witnesses rejected), 69 workflow links and 15 named classifications; all
passed. Evidence: evidence/author-repair-checks.json and reproducible local script.
B01–B15 runtime cases remain planned, not executed. No production edits, network,
models or installs. **G1 remains CHANGES REQUIRED until independent recheck.**

## Independent focused G1 follow-up

2026-10-25. Reviewer `/root/cli_p0_review`. Re-reviewed R1–R3 and changed contract
consistency after the single focused author repair. **Verdict: CHANGES REQUIRED;
one precise R3 classification blocker remains.** No scope expansion.

- **R1 CLOSED:** independently checked 108 code/retryability/completeness/data
  combinations against reviewed contract expectations, with zero mismatches.
  Original three invalid witnesses are rejected; frozen valid forms are accepted.
- **R2 CLOSED:** manually checked bootstrap rules and B01–B15. Help/version
  priority, unknown spelling, first-format routing, invalid-mode fallback and
  option-operand/sentinel recognition now have consistent explicit decisions.
  Runtime scanner conformance and legacy regressions remain G2/onward obligations;
  these design cases have not been executed through a new runtime.
- **R3 PARTIALLY FIXED / OPEN:** named class-method, lifecycle, category helper,
  adapter and signature-claim corrections are present; all 69 workflow definitions
  have phase/target/rationale links. However `src/shopextract/tools/contracts.py`
  top-level `validate(name, arguments, limits)` is still classified as **workflow
  P2 validate/images/duplicates**. Actual source validates ToolRuntime request
  argument shapes, schema versions and resource limits. It is a P5 tools schema
  validation helper, not marketplace validation. The generator's bare top-level
  `name in families` inference retains this false link. Required correction is
  exactly this source-qualified helper classification plus a named audit check;
  no additional domain grammar is requested.

Evidence: `evidence/reviewer-recheck.json`; one local Python/jsonschema process,
<1s, zero source-digest mismatches. No production edits/runtime execution,
network/models/installs or delegation. Actual session token counters unavailable.

Two administrative documentation items do not change behavior: parent coverage
examples must place root `--output-format json` before the command; author repair
JSON currently lives at `p0/author-repair-checks.json`, while its disposition claims
`p0/evidence/author-repair-checks.json`. Coordinator may align paths/examples.

### Follow-up reviewed artifact SHA256

| Artifact | SHA256 |
| --- | --- |
| `spec.md` | `21bbfe04025a70250dae509e35e290ea4f76ab9f97dc2ed962688ceb61147799` |
| `test-design.md` | `42083340f4d2d04e69d24e625ce541268112cb0019f2ffdb09f222db059e225d` |
| `contracts.json` | `007836d9e7f09a972ee5596f5a837dc18cc166af4b628b3ac8779743d8fa477f` |
| `response.schema.json` | `872def7faf437582e61fbd895bcd88a162e852d911226063055a3b8a20abee39` |
| `capability-manifest.json` | `3e3626ddc35c8ff62dd5b0d00cb85c82e55dedf6c45ac02ca7ef2103811165e5` |
| `research.md` | `7ead904f6041f7e3fd3650b9775a4bebc9cefc2f57da784e1abfc9abbdf06e2f` |
| `evidence/audit-design.py` | `8692d7978e87b429ab7ef8d1910fb4c3e1ad684989dce201614cfa48b478952d` |
| `evidence/author-repair-checks.py` | `7489ca99c97fac14d5cf7ea79620ad18f6df4455aab388cace50ab4d33297856` |
| `author-repair-checks.json` | `0412778405b8bfc6c9d778394fca4d78294956f4b34f3cc995104c4a5c39cd98` |
| `evidence/reviewer-recheck.json` | `ca75cf56f86716891979b19b91bc4d6ab01711df2996c4dd7c204a0a52af5cc7` |

## Final narrow independent G1 disposition

2026-10-25. Reviewer `/root/cli_p0_review`. **G1 PASS — design only.**
R1 and R2 remain closed under the prior independent schema/bootstrap review.
R3 is now CLOSED: source-qualified `tools/contracts.py::validate` is a composed
helper linked to P5 tools; it is absent from operator workflow links. The named
audit assertion checks that exact exclusion. All 92 source digests still match.
Regenerated artifacts contain 68 linked workflows and author evidence records
16 named classifications plus 22 schema examples. Evidence path and parent root
option placement are corrected. Original findings/digests above remain historical.

Independent narrow check saved in `evidence/reviewer-final-check.json` (<1s).
No runtime CLI implementation or production mechanism was executed. This PASS
approves the P0 contract-freeze design to enter skeleton/red-test work; G2/G3,
acceptance red/green, mechanism/stress and final implementation review remain
pending. Reserved P1–P5 domain grammar/payloads and actual CLI parity remain
unapproved. Actual session token counters unavailable.

### Final G1 reviewed artifact SHA256

| Artifact | SHA256 |
| --- | --- |
| `spec.md` | `21bbfe04025a70250dae509e35e290ea4f76ab9f97dc2ed962688ceb61147799` |
| `test-design.md` | `42083340f4d2d04e69d24e625ce541268112cb0019f2ffdb09f222db059e225d` |
| `tasks.md` | `27a09e8445689609eb44d3999fbbbd84e0ff27bf22e97634c1c345aaf9bc39a9` |
| `research.md` | `7ead904f6041f7e3fd3650b9775a4bebc9cefc2f57da784e1abfc9abbdf06e2f` |
| `plan.md` | `c149882d29d3611b149aa5c54579cb556d8d4a612bf64cc644f82a78f3e4dead` |
| `contracts.json` | `007836d9e7f09a972ee5596f5a837dc18cc166af4b628b3ac8779743d8fa477f` |
| `config.schema.json` | `d2cfdc3c4ec364832fa340e86e3520733005f669e25e1c873f78ca403615395d` |
| `response.schema.json` | `872def7faf437582e61fbd895bcd88a162e852d911226063055a3b8a20abee39` |
| `command-baseline.json` | `6dbb592fea817148992dfe41c8b5848278c42bb6f17d26c7869bd0c6d98426d4` |
| `capability-manifest.json` | `d277d7ad426e4be60eb8e9e5f25e8bf1ecc5722e6cbd812562543a53d935c85d` |
| `verification.md` | `73615c3dead4724336358acb529057199aa0a3f17cb7bdf84d5f9a4953ca2cb7` |
| `evidence/audit-design.py` | `c1ad10947e53df4a6784edbe1cb8e4dfecb0fbdc6a53a7148166ab2e2500e053` |
| `evidence/audit-summary.json` | `9447cd351142d4ffa8a56c4bb89dcda6f99d165b881b2810d98a5de123cbb51b` |
| `evidence/author-repair-checks.py` | `4ec439ae24f6f9e39a22a21928352b58075a130c9f3bd4b97de410d8417dab5a` |
| `evidence/author-repair-checks.json` | `18a057fef4062736d323a293f4372e858a2115dad6c460e220a9707bc68b9963` |
| `evidence/reviewer-final-check.json` | `ac33bc759b9c65477bf9414b0088ac74972854c17eb717a936e4f7fa986e3169` |
| `../coverage.md` | `ef8b7f7cebe0e6905d04742a9f308fd9aeee87f4c48f39cab1c6d308a6a7a164` |

## Independent G2 skeleton review

2026-10-25. Reviewer `/root/cli_p0_review`; author `/root/cli_p0_author`.
**G2 PASS.** Reviewed typed declaration-only skeleton, real public-entry tests and
saved actual red evidence. G1 research was reused; no production stub/code added.

- Typed settings/bootstrap/failure/config-source/response seams separate Click
  registration from config, error selection and emission. ConfigSource retains a
  single selected read attempt and its failure for later machine-error routing;
  it does not allow a second read to change mode after failure. Explicit ordering
  agrees with frozen B01–B15 and first-occurrence output selection.
- Legacy callbacks retain signatures/default/native dispatch; machine branches
  avoid parsing historical stdout. Native failure translation is centralized,
  sanitized, with no retry or optional runtime startup in bootstrap. Typed
  failure/response construction can represent partial data and fixed exit codes.
- Tests call actual `cli.main`; only the native detect boundary is replaced.
  Thus real parser/config/emitter interfaces remain exercisable through the
  public boundary. The deterministic detect projection is existing native output,
  not a substitute implementation of config/error mechanisms.
- Saved initial run has 28 failed and 4 passed in 0.64s test time / 3.172s
  bounded process time, under a 30s cap. Failures are absent root controls or
  the intended bootstrap precedence difference, with no ImportError or
  ModuleNotFoundError. Legacy source digest still matches the frozen baseline.
  Red log is genuine missing-feature evidence, not a green/runtime claim.

No blocking G2 findings. Later implementation/final verification must execute
all remaining designed config/machine paths, especially single-read success and
failure, quiet/error stream behavior, and remaining B cases. Current initial
32 checks are not complete SC03–05 or stress coverage. D7 remains responsible
for those checks; G3 component review is still required before production work.

No test rerun was needed: saved bounded red output and current test/source
artifacts were inspected directly. No production edits, network/models, installs
or delegates. Actual session token counters unavailable.

### G2 reviewed artifact SHA256

| Artifact | SHA256 |
| --- | --- |
| `specs/011-cli-feature-parity/p0/skeleton.md` | `24d79a8754c50be89d454dd7a6275ae9b6ded180799020aea547acfa685879e5` |
| `tests/test_cli_core.py` | `96622d9bf6e18437870cf70427be54f2e9b2aeaa66d923dd1d62efeaf6caa07e` |
| `specs/011-cli-feature-parity/p0/evidence/acceptance-red-g2.log` | `951553bc9a27a393de7485db7f892413bc110a1f60a6d8fb76020c3b6fd52133` |
| `specs/011-cli-feature-parity/p0/evidence/acceptance-red-g2.json` | `a7c79036ee4aa5aacdeb3f004110f853e1eea62465e6a3c7eca34cedeeef2a61` |
| `specs/011-cli-feature-parity/p0/contracts.json` | `007836d9e7f09a972ee5596f5a837dc18cc166af4b628b3ac8779743d8fa477f` |

## Independent G3 component review

2026-10-25. Reviewer `/root/cli_p0_review`; author `/root/cli_p0_author`.
**G3 PASS.** Reviewed components.md, refined typed skeleton and G01–G10 gap
design; reused actual G2 red evidence without rerunning it.

The private core has concrete current consumers and clear dependency direction:
Click registration/settings/config/error emission depend on the core; domain
services do not. ConfigSource is invocation-local and reused for settings/error
selection, retaining failed attempts without global state or rereads. Strict
flat-config validation and the fixed policy table avoid runtime dependence on
spec files/development jsonschema. Native domain codecs remain owned by their
phases, avoiding a duplicate reflection serializer or speculative framework.

The added emit_diagnostic seam has existing extract-summary/discover-count
consumers and supports quiet without hiding structured error responses. It does
not own raw exception sanitization. No new process/runtime lifecycle is added;
existing native dispatch and future domain cancellation boundaries remain clear.

G01–G10 address distinct prior gaps: successful/parse-failed/open-failed single
reads, quiet config/internal errors, real diagnostic consumers, B12–B15 and
invocation isolation. Expected outcomes are defined before additional tests and
require real loader/parser/emitter mechanisms with only native boundaries/I/O
faults controlled. No-read assertions include selected config and documented
environment lookup. Resource bounds remain finite and sequential.

No blocking findings. Production implementation may proceed within P0. Expanded
acceptance, coverage review, first mechanism smoke, bounded stress/regressions
and independent final review still block implementation completion. This gate
does not approve reserved domain grammars or establish live/CLI parity. The
skeleton's old "G2 pending" footer is historical administrative text; the actual
G2 verdict above remains authoritative and coordinator may align that footer.

No production edits/tests rerun, network/models, installs or delegation. Actual
session token counters unavailable.

### G3 reviewed artifact SHA256

| Artifact | SHA256 |
| --- | --- |
| `components.md` | `dedec38903ffbba71a80dbf5ee5798869351160f2cacc18b2da2dbc0c73e17de` |
| `skeleton.md` | `cad2331247d0f637a922ba4aa2ddb79ede6440d080524ca27b3c0d1a74446682` |
| `test-design.md` | `b18dd1ed7abd449899d7ed9880e61baf74213f76e219ee2cec9cfac510144d7e` |
| `evidence/acceptance-red-g2.json` | `a7c79036ee4aa5aacdeb3f004110f853e1eea62465e6a3c7eca34cedeeef2a61` |

## Independent D7 pre-expansion coverage review

2026-10-25. Reviewer `/root/cli_p0_review`; implementation author
`/root/cli_p0_author`. **CHANGES REQUIRED for complete pre-stress coverage;**
existing G01–G10 design/tests and duplicate-key fault-proof approach accepted.
No production edits or expanded checks executed by reviewer.

Reviewed actual _cli_core.py/cli.py, expanded test source, frozen contracts,
components/skeleton and saved initial32 green smoke (exit0,2.561s,30s cap).
The fixtures use realistic deterministic native detect/discover return shapes,
real Click/config/response paths, temporary real files, and injected selected
file-open failure. Config/parser/emitter are not replaced with expected outputs.
G01–G10 are distinct read, precedence, stream and invocation-isolation checks.
Non-detect machine E_OPERATION guard is explicit phase deferral, not parity.

### C1 — blocking coverage gap: distinct root error/emission branches

SC03 freezes timeout, missing dependency, interruption and emission failure, but
current tests only inject RuntimeError for generic internal native failure.
Separate CoreGroup branches are unexercised. Before expansion/final verification,
add designed cases with independent expected outcomes, then executable checks:

| Risk/input at real CLI boundary | Expected outcome |
| --- | --- |
| Native detect raises TimeoutError under explicit JSON | One valid E_TIMEOUT envelope; exit1; retryable=true; no leaked exception text; no automatic retry. |
| Native detect raises ImportError under explicit JSON | One valid E_DEPENDENCY envelope; exit1; retryable=false; actionable sanitized message; no raw missing-module/token text. |
| Native detect raises KeyboardInterrupt under explicit JSON | One valid E_CANCELLED envelope; exit130; retryable=false; clean invocation settings restoration. |
| stdout write deliberately fails through actual emit_response/Click stream boundary | Exit1; best-effort sanitized stderr; no false success or dispatch retry. Valid stdout JSON is explicitly not guaranteed. Restore stream fault immediately. |

These are separate failure modes/contract table entries; schema-only checks of
error constructors or another RuntimeError test do not cover native-to-CLI
translation or response-emission recovery. Existing frozen SC03/FR04 already
requires them, so this supplements verification rather than changing behavior.

### Accepted bounded fault/stress plan

Temporarily replace actual duplicate-pair hook with a duplicate-accepting hook,
invoke real public CLI with duplicate schema_version input, and prove the normal
E_CONFIG assertion fails. Restore in try/finally and rerun affected normal case.
This is mechanism sensitivity, not a replacement decoder serving expected data.
Keep <=12 stress cases,<=65,537-byte configs,30s/run,120s total,sequential; save
progress, stop first unexpected failure, diagnose one repair. Initial32 smoke is
already saved and should be reused. Expanded acceptance tests are distinct from
the <=12-case stress budget. No live claim follows from these controlled checks.

Actual session token counters unavailable. No installs/network/models/delegates.

### Coverage-review artifact SHA256

| Artifact | SHA256 |
| --- | --- |
| `src/shopextract/_cli_core.py` | `e991b9570d448933f04ab1a51d8ed9c1dc4f0cf451508330849a08ce1585ef66` |
| `src/shopextract/cli.py` | `3da88320db5086f8f99db47a1d8354ecd4f8818163989a2383f31e144597116b` |
| `tests/test_cli_core.py` | `0f0f8ee8a45efccd42fb145d0a8d45fbe632903e94407ae3b0852d65dbb6805c` |
| `specs/011-cli-feature-parity/p0/test-design.md` | `b18dd1ed7abd449899d7ed9880e61baf74213f76e219ee2cec9cfac510144d7e` |
| `specs/011-cli-feature-parity/p0/components.md` | `dedec38903ffbba71a80dbf5ee5798869351160f2cacc18b2da2dbc0c73e17de` |
| `specs/011-cli-feature-parity/p0/skeleton.md` | `cad2331247d0f637a922ba4aa2ddb79ede6440d080524ca27b3c0d1a74446682` |
| `specs/011-cli-feature-parity/p0/contracts.json` | `007836d9e7f09a972ee5596f5a837dc18cc166af4b628b3ac8779743d8fa477f` |
| `specs/011-cli-feature-parity/p0/evidence/core-first-smoke.json` | `73cdd4da4f8188a6a5b54287166e7be9ec1165ebbb666ef75930a82e41a2cce0` |

## Independent C1 pre-execution recheck

2026-10-25. Reviewer `/root/cli_p0_review`. **Coverage design PASS; C1 CLOSED.**
Inspected exactly four added public cases and their predeclared expectations.
Timeout/dependency/interruption inject only the native boundary and assert exact
code/exit/retryability plus sanitized output and subsequent legacy settings reset.
BrokenStream is supplied to the original real emit_response through partial;
encoder, Click writes, root error handling and cleanup remain real. Both success
and error emission encounter the deliberately failing stream, with exit1 and
best-effort sanitized stderr expected. No implementation mechanism is mocked.

Existing G01–G10 and bounded duplicate-pair sensitivity plan remain accepted.
Expanded acceptance/fault/stress checks may now run within reviewed limits. No
run or green claim is made here; final review still requires actual evidence.
No production edits, network/models/installs/delegates; counters unavailable.

| Artifact | SHA256 |
| --- | --- |
| `tests/test_cli_core.py` | `8417aa463d82c4f5b3fd7c58e69d5442ffd624a6b5a6e099e723a5bd1229a38d` |
| `specs/011-cli-feature-parity/p0/test-design.md` | `173ad6e9c0ab9573f35e981d24ff9f886057e61542058de61e30e064a9fe2dfd` |

## Independent final P0 implementation review — initial verdict

2026-10-25. Reviewer `/root/cli_p0_review`; author `/root/cli_p0_author`.
**CHANGES REQUIRED: one core validation-order blocker F1.** Prior G1/G2/G3
and coverage review remain recorded; the finding concerns actual integration.

### F1 — blocking / P2: phase guard bypasses known Click usage validation

CoreGroup.main rejects non-detect machine commands before calling Click domain
argument/option parsing. Consequently these invalid existing-command invocations
all produce E_OPERATION/1 instead of frozen E_USAGE/2:

- `--output-format json extract` (missing required URL);
- `--output-format json discover https://fixture.invalid --max bad` (bad integer);
- `--output-format json validate /definitely/missing.json` (invalid existing path).

Independent local real-CLI probe executed all three without network/models/native
dispatch; exact argv/results saved `evidence/reviewer-final-probe.json`. All emit
a valid envelope, but wrong error code/exit. Frozen SC03 usage mapping and
skeleton integration step4/5 require known argument validation before dispatch.
Domain payload deferral does not require bypassing already-frozen legacy syntax.

Required: design missing-required/type/path interactions first, then use Click
validation before the explicit non-detect phase guard, while still preventing
native service work for a syntactically valid deferred machine command. Add a
valid-deferred invocation sentinel proving E_OPERATION/1 with no native dispatch.
No P1–P5 payload or new grammar is requested. One diagnosed focused repair,
affected checks, then independent recheck; no broad sweep. Disposition OPEN.

### Accepted evidence and limits

Expanded48 and affected181 passing logs/metadata, bounded12-case stress and scoped
duplicate-hook fault proof were inspected. Mechanism driver invokes real CLI,
uses real temporary bytes/config/parser/emitter, controls native detect only,
saves each case and restores actual duplicate hook. Baseline2/mutant0/restored2
proves the expected rejection assertion detects disabled duplicate detection.
Finite timings/input/case bounds and offline provenance are stated.

Single-read state, environment precedence, sanitization/error classes, quiet
diagnostics, invocation cleanup and explicit domain deferral have focused tests.
Core compatibility artifact preserves all nine declarations/native dispatches and
classifies new private symbols separately from the frozen historical inventory.
This supports bounded core verification, not live/domain CLI parity. No broad
regression rerun was needed to discover F1. Preexisting unrelated changes remain
outside this review. Docs accurately limit implemented JSON results to detect.

No production/test edits, installs/network/models or delegates. One local probe
process completed in ~1.3s. Actual session token counters unavailable.

### Final-review candidate artifact SHA256

| Artifact | SHA256 |
| --- | --- |
| `src/shopextract/_cli_core.py` | `e991b9570d448933f04ab1a51d8ed9c1dc4f0cf451508330849a08ce1585ef66` |
| `src/shopextract/cli.py` | `3da88320db5086f8f99db47a1d8354ecd4f8818163989a2383f31e144597116b` |
| `tests/test_cli_core.py` | `8417aa463d82c4f5b3fd7c58e69d5442ffd624a6b5a6e099e723a5bd1229a38d` |
| `docs/cli.md` | `c973d0ec16e2c0433f03a58b8dc34e49f6bfb61d0c52d90969d89cb664c17b52` |
| `specs/011-cli-feature-parity/p0/verification.md` | `6d3ca381542d125295445975ba78c86f7a757500634a5f31e326e7ca31bb56f8` |
| `specs/011-cli-feature-parity/p0/evidence/core-mechanism-driver.py` | `66fd332f5008948ec02a5e54d40f60c4661855450706aec3101839bc9857b4e7` |
| `specs/011-cli-feature-parity/p0/evidence/core-expanded.json` | `bb940c65e2151ff5a841c2c29c7f98ba30661589f6e5c34d68d75680deec7d94` |
| `specs/011-cli-feature-parity/p0/evidence/core-regressions.json` | `d93ece9e8f2da468e08ea569c274da16998f2b07e3d3facbb1dd9a083a1b3f50` |
| `specs/011-cli-feature-parity/p0/evidence/core-stress.json` | `37f641a7b3e4a7480a7fa4d57abeebb27cfc58ed4d13ea0639fae6ca3f639d78` |
| `specs/011-cli-feature-parity/p0/evidence/core-fault-proof.json` | `163e143e93aff4b53cdcae47af9aba5dc32d391d4728c0cf3f952ebacb5d5a33` |
| `specs/011-cli-feature-parity/p0/evidence/core-compatibility.json` | `e03874cd1322832452dce050d38b7eddb6bb0e48c83ba19ac62d5a963e5893d7` |
| `specs/011-cli-feature-parity/p0/evidence/reviewer-final-probe.json` | `3eb816ab2f1f3a3afd579bffc21ea4eadae275848f857e9aa04d6a6abf1c43fa` |

## Independent final P0 disposition after focused F1 repair

2026-10-25. Reviewer `/root/cli_p0_review`. **FINAL PASS for P0 core slice;
F1 CLOSED.** This supersedes the initial final CHANGES REQUIRED verdict only
for the reviewed repaired artifacts; historical findings remain preserved.

CoreCommand.invoke now guards availability after Click context/argument validation
and before native callback execution. CoreGroup selects that command class; the
earlier preparse guard is removed. Root options and nine legacy declarations/
dispatches remain unchanged by the repair. Refined skeleton/components describe
the same existing validation-order contract.

Four cases were designed before repair: initial targeted red3fail1pass is saved;
all52 core tests now pass in the bounded30s run. Independently executed the same
three invalid argument classes plus one valid deferred command with real CLI and
native-dispatch failure sentinels: all4 produce expected E_USAGE/2 or E_OPERATION/1
without native work. Saved `evidence/reviewer-f1-final.json`. No full-regression
or stress rerun was needed for this localized dispatch-order fix; prior affected
181pass, bounded12case real-mechanism stress and duplicate sensitivity proof
remain applicable to unchanged parsing/config/encoding mechanisms.

P0 core bootstrap/config/error/envelope/diagnostics and detect machine binding
are verified within the stated offline bounds. Live N/A is appropriate for this
core policy slice; no source observation or P1–P5 CLI parity is claimed. Other
domain machine commands remain explicitly deferred. Future phases still require
their domain contracts/gates/tests/live applicability. Unrelated dirty-tree
changes are outside this review. Status/task administrative closure may follow
this verdict; no behavior/schema change is approved by administrative updates.

No production/test edits by reviewer, no installs/network/models/delegates/push.
Independent probe was one bounded local process. Token counters unavailable.

### Final repaired P0 artifact SHA256

| Artifact | SHA256 |
| --- | --- |
| `src/shopextract/_cli_core.py` | `d75847c2f52e850eee588e43809a9dd52617362440a03707c36b1f05e137c0db` |
| `src/shopextract/cli.py` | `3da88320db5086f8f99db47a1d8354ecd4f8818163989a2383f31e144597116b` |
| `tests/test_cli_core.py` | `8cc3b16ba7c7883134d10e42b378fde42f8c170bb887e68b524d7b87c6728e57` |
| `docs/cli.md` | `c973d0ec16e2c0433f03a58b8dc34e49f6bfb61d0c52d90969d89cb664c17b52` |
| `specs/011-cli-feature-parity/p0/spec.md` | `3b5694517bdde4b280c1955d9b20aa4a691b9e142eff3b17513bfb065b366c26` |
| `specs/011-cli-feature-parity/p0/test-design.md` | `b5588cdae118be8c471365958a1a55d3efddd620a13cebcf3551b24abcdb8b4b` |
| `specs/011-cli-feature-parity/p0/components.md` | `8445e9d037365231746c4bf51588a5731c56a941e34e13442d5e4fa444c38633` |
| `specs/011-cli-feature-parity/p0/skeleton.md` | `7b77d25566e9492f3ff5fbb56953f413a83030005d536ad3179ce3a38fb75600` |
| `specs/011-cli-feature-parity/p0/verification.md` | `0084b166cef6e7ef6119cbc10d154f810fe68e8aeda1cbdacce28ca3258b92cd` |
| `specs/011-cli-feature-parity/p0/evidence/core-f1-red.json` | `630eb8ac378b8c1a8d5432e3a1a57a40596967f8d32760a72a033a7399317435` |
| `specs/011-cli-feature-parity/p0/evidence/core-f1-green.json` | `61cd012e9d9c42a279569a7310319774768e97c2a7818c29fc13a588e68f0346` |
| `specs/011-cli-feature-parity/p0/evidence/core-f1-compatibility.json` | `c08657b25690594a08cc52f76be71890d4e334f2a3bbcf1c0292af88c35a8d6e` |
| `specs/011-cli-feature-parity/p0/evidence/reviewer-f1-final.json` | `1c09bf55ea2a42c801ebe3de6862af2714460e5919acdb4f2a0a9fabbe9cfc77` |
