# P0 behavior and test design

Designed before task breakdown/runtime code. Fixtures are synthetic/offline.

| FR / SC | Fixture and distinct uncovered risk | Exact expected result / boundaries | Verification |
| --- | --- | --- | --- |
| 01 / 01 | AST baseline plus Click invocation of all nine commands; stub only native network boundary | exact names/options/defaults/dispatch in baseline; extract 11 products retains legacy preview 10, output file has 11; compare repeated stores preserves order; history positional order; validate issue report retains exit 0 | G2 red acceptance, then legacy regression |
| 02–03 / 02 | Native extraction result containing 11 distinct products; decimal 0.10, missing/null/false/0 and escaped identifiers | machine mode emits one envelope, all 11 in original order, decimal string "0.10", native support states retained, stdout parses with no trailing nonwhitespace; progress stderr only; legacy remains unchanged | phase P1 native-result schema freeze required before its executable payload assertions |
| 03–04 / 03 | Controlled native failure, malformed CLI argument, missing optional engine, incomplete native result, timeout and interrupt | generic code/exit table in contracts.json; unexpected failure sanitized E_INTERNAL/1; no fake success; ordinary business validation findings remain data; broken stdout best effort only | G2 core red tests use controlled injected failures at real CLI boundary; domain partial mapping reserved |
| 05 / 04a | Strict files: {}, [], null, true version, unknown keys, duplicate keys, NaN, BOM, invalid UTF-8, 65,535/65,536/65,537 byte valid whitespace-padded records | valid versioned objects at/below cap accepted; above cap and malformed/unknown inputs E_CONFIG/2 before side effects; missing/unreadable explicit path E_CONFIG/2; no stdout success | real future config loader; no duplicate reference parser as mechanism |
| 05 / 04b | Distinct conflicts across default, file, env and explicit flags; empty env/path; invalid lower-precedence env/file even under override | explicit > trusted file > env > default; false/empty not treated as absence; every selected source validated; unknown env ignored; duplicate root option E_USAGE/2 | 4-step deterministic precedence fixture, read-only source files, snapshot no side effects |
| 04–06 / 05 | Missing config, invalid env, invalid output-format plus recognized --help; nested help; unknown command | recognized help/version exit 0 textual and no config read/side effects; unknown command remains usage 2; no optional-runtime startup | subprocess <=20s with file/open and native activation sentinels; no external network |
| 07 / 06 | Current AST source vs saved six-file inventory plus all __all__ exports, public definitions/methods | no missing symbol classification, every workflow has phase/target; no reserved mapping claims frozen flag/schema; alert/Investigator excluded by name, composed category helpers carry parent target | design audit now; executable gate checks after G1 |

## State and compatibility contracts

First recognize option/command spelling while skipping declared operands; unknown
command or option errors precede bootstrap. Then recognized help/version bypass
value/config validation according to contracts.json. Otherwise choose config path; read and
validate file plus recognized env settings; merge precedence; parse/validate domain
arguments; only then dispatch. Error representation follows contracts.json bootstrap/error_output_routing exactly.
The first explicit format occurrence selects json/legacy if valid; if missing or
invalid, validated selected file then valid env then legacy determines error
representation. Invalid settings still fail; later duplicates cannot change mode.
Recognized help wins over version regardless of token order, but unknown command
or option spelling fails first. Scanner skips declared option operands and stops
recognizing options after `--`. Cases B01–B15 specify exact argv/env/exit/stream
and no-read expectations, including conflicting repetitions, invalid first format,
root-only version, nested help and option-looking operands. These are designed
cases, not runtime results. No result emission before dispatch
completion for this single-response core. Phase-specific streaming is separate.

## Red-test plan

G1 first, then skeleton declarations and focused executable tests using installed
Click/Python and real CLI dispatch. Baseline/help smoke is not red evidence.
Intended red: root `--output-format json` and `--config` currently unrecognized;
strict config currently unavailable. Do not count dependency/import failures.
Bound each subprocess <=20s; total initial red run <=30s; persist each outcome.
Do not create tests against a nonexistent module merely to get ImportError.

## Mechanism / stress plan

Author: `/root/cli_p0_author`; independent reviewer assigned by coordinator.
Seed 11025, one sequential driver, 12 distinct cases max, <=65,537 config bytes,
11 synthetic products, <=30s per run and <=120s total, no inference/network,
BLAS/tokenizer workers 1, intra-op <=2/inter-op 1 if ever loaded (none needed).
Cases: strict-version/type; duplicate-key; unknown-key; nonfinite; encoding;
byte-cap below/at/above; precedence; invalid overridden source; JSON error routing;
quiet/streams; help no activation; inventory drift. Save first smoke before
expansion; stop unexpected failure, one diagnosed repair then record blocker.
Use actual production config/parser/encoder once implemented. Prove duplicate-key
assertion catches temporarily disabled duplicate detection, restore immediately.
No mechanism/stress pass claimed during design.

## Live applicability

Docs-only P0 design and core parser/config behavior require no live source.
Actual extraction/store/monitor/tool observations remain required by their phases;
synthetic fixture execution is offline and cannot be described as live coverage.

## Focused G1 repair cases

R1 schema-only examples: success plus each of nine error codes must validate with
its contracts.json retryable/completeness value; each inverted retryable must fail.
All three independent reviewer witnesses must fail, especially unavailable
E_PARTIAL. These validate the designed schema, not CLI runtime mechanisms.
R2: B01/B02 check order precedence; B03/B04 unknown-command interaction; B05/B06
first repeated format; B07/B15 invalid explicit mode fallback; B08/B09/B13 no-read
bootstrap; B10/B11/B12 distinguish operands/sentinel; B14 root-only version.
R3: audit every workflow label has phase/target/rationale; check engine clock/hook
Python-only, close/acquire/release composed lifecycle, TrustContract.validate
composed schema validation, category codec/config helpers composed, extractor
classes adapter implementations. No blanket method-name inference is permitted.

## D7 gap design before additional tests (G2 follow-up)

Initial red suite is 32 checks, not full SC03–05 verification. The following cases
add distinct read/lifecycle/output interactions; they are designed now, not run.
Do not regenerate or rerun already valid design/initial-red evidence.

| Case / SC | Distinct risk / fixture | Exact expected result / real mechanism |
| --- | --- | --- |
| G01 / 04 | Valid selected config sets json; tracked selected-file open/read count, native detect fixture | Public invocation success JSON, one selected-file open/attempt, full file read once, one native call; later response/error selection cannot reread. |
| G02 / 04 | Malformed selected file, env json, tracked failing/parse read count | E_CONFIG/2 JSON, no native call, exactly one read attempt; cached failure used during representation fallback. Inject second-open exception to detect retry. |
| G03 / 04 | Missing selected file under explicit json, injected first-open OSError | E_CONFIG/2 JSON, exactly one failed open attempt, no native call/no created file. Distinct from parse failure and success cache. |
| G04 / 03 | Quiet + invalid selected config and controlled native unexpected error | Separate public cases: E_CONFIG/2 and E_INTERNAL/1 JSON remain visible in stdout with sanitized message; no progress/traceback/secret stderr. Quiet cannot hide errors. |
| G05 / 02–03 | Actual shared diagnostic seam with informational message and normal/quiet settings; existing extract summary/discover-count consumers | Normal emits nonessential diagnostic once to stderr, quiet emits none; both leave success/error envelope stdout intact. Once helper exists test real helper plus at least one public consumer, not an imitation diagnostic writer. No new normal progress requirement for detect. |
| G06 / 05 | B12 option-looking PATH operand in temporary cwd where --help file absent | E_CONFIG/2 legacy stderr; no help text, one selected-file attempt and no native call. Existing sentinel URL case covers B10 separately. |
| G07 / 05 | B13 repeated conflicting formats plus recognized root --help | Exit0 textual root help, no config/env reads or native calls; unlike repetition-without-help E_USAGE cases. |
| G08 / 05 | B14 root-only version supplied after detect | E_USAGE/2 JSON for explicit json; no native call and no version text. |
| G09 / 03 | B15 first format invalid, second json, env unset | E_USAGE/2 legacy stderr, no stdout/no native call; later valid occurrence cannot choose JSON. |
| G10 / 04–05 | Same CliRunner reused: first invocation valid json config; second plain legacy detect with clean env | First JSON envelope, second native legacy JSON without schema_version; independent single read state/settings cannot leak between invocations. |

No-read assertions for recognized bootstrap must instrument the production config
source seam or file open and documented-env lookup, not merely observe a missing
file produces no error. Count reads for the selected path only; importing Python
modules is not a config read. These checks target actual source attempts and
routing, not a test reference decoder. B01–B15 all have initial tests or G06–G09
planned cases; G01–G05/G10 cover interactions beyond the token table.

Resource limits remain seed11025, one sequential driver, <=12 stress cases,
<=65,537-byte config, <=30s/run and <=120s total. Read instrumentation/faults
restore after each test. Save one small real-loader smoke before bounded stress;
stop unexpected failure, one diagnosed repair then record blocker. Coverage review
is required before stress; passing tests do not imply unlimited scale or live
source observations. No additional tests/run executed at this component stage.

## Coverage review C1 additions (before tests)

These four distinct SC03 branches supplement G01–G10: controlled native
TimeoutError('SECRET') must yield E_TIMEOUT/1/retryable=true; ImportError('SECRET')
E_DEPENDENCY/1/retryable=false; KeyboardInterrupt E_CANCELLED/130/retryable=false.
Each runs the public json detect path with no external IO, retains no secret or
traceback and then invokes plain legacy detect to prove settings reset after
failure. Output case supplies a write-failing TextIO boundary to the actual
emit_response implementation: BrokenPipeError during success and error emission
must exit1, best-effort sanitized stderr, no promise of complete JSON, and settings
reset on the next legacy invocation. Only the stream boundary is injected; the
real encoder, Click stream write, error routing and cleanup remain exercised.
Four test cases, same <=30s/run<=120s total sequential bounds. No new generic error
codes, automatic retries or domain contracts are added.

## Final review F1 design before focused repair

The phase availability guard must run after actual Click command conversion and
before native dispatch. Four distinct public cases: `--output-format json extract`
(missing URL), `... discover URL --max bad` (invalid integer), and `... validate
MISSING` (Click.Path missing file) each yield E_USAGE/2 JSON, no native call.
A valid `... discover URL` remains explicitly deferred E_OPERATION/1 JSON with no
native call. This checks validation-vs-availability order without binding any
reserved domain payload. Native adapter sentinels ensure no accidental network
while moving the guard. Run these four red before repair, then all core tests
within the existing30s cap; retain prior unrelated stress/regression evidence.
