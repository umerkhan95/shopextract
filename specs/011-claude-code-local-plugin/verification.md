# Verification evidence

Date: 2026-10-24. All results below are offline mechanisms unless explicitly labeled native host. No model inference, public store test, public publishing, login or dependency installation occurred. Core production Python code is unchanged.

## Commands and saved results

Commands ran from the isolated checkout with the existing primary workspace `.venv/bin/python`, `PYTHONPATH=src`. Expanded tests also set `OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 TOKENIZERS_PARALLELISM=false`. Environment/version and fixture bounds are saved in evidence/environment.json (Python3.10.11, MCP1.30.0, pytest9.1.1). No downloads or inference workers were launched. Actual session token counters are unavailable; no quota percentage is inferred.

| Stage / command suffix | Actual result | Saved evidence |
| --- | --- | --- |
| Existing baseline `-m pytest tests/test_mcp_reference_client.py -q` without source path | Import failure; diagnosed isolated PYTHONPATH omission | baseline-smoke.txt |
| Same baseline with `PYTHONPATH=src` | 1 passed / 7.66s | baseline-smoke-repaired.txt |
| Preimplementation acceptance `-m pytest tests/test_claude_code_plugin.py tests/test_claude_code_workflow.py -q` | 5 intended missing manifest/MCP/skill failures / 0.35s | acceptance-red.txt |
| G2 native-opt-in revision, same focused command | 4 intended missing package failures, 1 native skip / 0.27s | acceptance-red-g2.txt |
| First package smoke, same focused command | 3 passed, 1 failed, 1 skipped; hostile executable symlink lost venv dependency discovery | green-smoke.txt |
| One diagnosed launch repair: add already-installed purelib to test process PYTHONPATH, same focused command | 4 passed, 1 skipped / 2.55s | green-smoke-repaired.txt |
| Expanded focused suite, same focused command | 31 passed, 4 fixture-construction failures, 1 skipped / 24.15s | offline-focused.txt |
| `-m pytest tests/test_claude_code_workflow.py -k real_source_recipe_cases -q` after first fixture corrections | 5 passed, 3 unsupported-field mapping assertion failures / 5.35s | fixture-repair.txt |
| Affected regression command below after corrections | **147 passed, 1 native skip / 58.42s** | offline-regressions.txt |
| Supplemental no-refetch/canonical restart: `-m pytest tests/test_claude_code_workflow.py -k 'real_source_recipe_cases or sequential_restart' -q` | **9 passed, 10 deselected / 16.70s** | evidence-identity-checks.txt |
| Final standalone LICENSE/package policy: `-m pytest tests/test_claude_code_plugin.py -q` | **16 passed, 1 native skip / 0.21s** | package-policy-final.txt |
| CI optional SDK import compatibility (set sys.modules['mcp']=None, instantiate runtime/check8 schemas) | Passed; subprocess exit0 | optional-sdk-import.txt |
| `-m compileall -q` on four new test/helper modules; `git diff --check` | Passed | command record in this file |

Affected regression command (one bounded run, no full-suite/CI claim):

```text
-m pytest tests/test_claude_code_plugin.py tests/test_claude_code_workflow.py tests/test_mcp_reference_client.py tests/test_agent_tool_api.py tests/test_tool_lifecycle.py tests/test_tool_bootstrap.py tests/test_evidence_contracts.py tests/test_field_resolution.py -q
```

Saved text logs have trailing whitespace normalized for repository checks; command output and outcomes are otherwise retained. Historical failed logs remain failed, not relabeled green. Fixture construction corrections used the actual existing serialized Product contract (`vendor: null`, with no supporting IDs) instead of an invented `brand` member or an assumed absent mapping key, and integer timeout1s instead of invalid fractional limits. The requirement stayed unsupported/unknown data with no fabricated evidence. No production assertions or core behavior were weakened to fit results. Existing RequestsDependencyWarning appeared in this environment.

## Mechanism coverage and bounds

- SC01/07: shipped JSON parsed by Python JSON parser and exact project inventory/config policy; standalone private copy/update keeps original version intact. Twelve deterministic negative copies reject malformed JSON/type, traversal/absolute component fields, missing skill, malformed MCP command, hook file, escaping symlink, synthetic credential sentinel, real-style operator path, >1MiB and >32files. This is **project policy rejection**, not a native host parser result.
- SC02: actual shipped command/argv launched through official MCP SDK with literal hostile executable/config filenames (spaces, quotes, semicolon, `$()`, Unicode). Real CLI initializes, restricts tool discovery and denies an ungranted origin. No sentinel execution. Five actual config-launch failures (missing, invalid JSON/grant, unset literal, empty) return safe exit2/stderr with no stdout; missing executable raises an explicit startup error. Test-side exact placeholder replacement proves SDK argv handling only.
- SC03/04: seed24 controlled public-origin resolver/wire fixtures use real production source parsing/normalization/jobs/evidence. Six-call success is discover/result/extract/status/result/evidence; source injection never triggers metadata access or extra capabilities. Exact10.25 EUR, unsupported vendor, canonical IDs, observation time and owner-bound support are retained. Duplicate sitemap URLs collapse; three real XML product records cap at two with partial completeness. Evidence lookup makes zero additional outbound requests. Existing affected field-resolution/evidence tests cover uncertainty/competing support; no model resistance is inferred.
- SC05: deterministic real jobs cover discovery/extraction pending states, source failure and actual1s timeout; recipe stops at2/4 calls. Separate actual-call tests stop before a third call when max_calls2, and before the second at deadline120. No unlimited polls/retries. Driver synchronization waits for real owned tasks only for offline completion; it does not fabricate reports or establish host behavior.
- SC06: real SDK controlled-source stdio session returns captured evidence. Wrong owner type is rejected; after sequential close/restart old job/owner handles return not_found. Fresh extraction keeps canonical product ID and mints a distinct owner. Total returned products across those two sessions: two; test ceiling20s. Lifecycle diagnostic calls are separate from the six-call recipe trace, not hidden recipe calls.
- Bounded stress:9 actual submissions admitted (one active/eight queued), tenth rejected resource_limit. One observed outbound response is held at the fixture boundary; no fake job engine. Shutdown completes within2s and releases all jobs/retained charges. Direct cases have15s ceiling, actual job await8s, parser command20s. No parallel model/session launches.

## Native parser and live host: BLOCKED

Coordinator preflight evidence/host-preflight.json: local CLI reports1.0.35; `auth status --text` contradicts help and rejects flag; plain isolated normal auth returns exit1 `Invalid API key · Please run /login`. No sign-in or credential copying performed.

Actual parser attempt (evidence/native-parser.json): `claude plugin validate --strict --json <package>` under disposable profile returns exit1, unknown `--strict`. One diagnosed plain-command repair (evidence/native-parser-repair.json) returns exit1 with the login prerequisite. Stop: no further parser retries or new client install. **No native parser, native-negative, directory discovery, actual variable expansion, private install/update/disable, skill activation or model instruction-compliance pass is claimed.** Default native test skip is not compatibility evidence.

Native test opts in with `SHOPEXTRACT_NATIVE_CLAUDE=1`; absent client or nonzero validation result fails. Even exit0 must contain a structured JSON validation report with errors list and true success/valid flag; an auth message cannot pass. The installed client was attempted directly as above; the unavailable parser is not repeatedly invoked through pytest after the blocker. No alternative parser is mislabeled native. Host test prompts were not sent because normal isolated access is unavailable. Remaining work requires a functioning native parser/client and normal signed-in access; no new service/backend is needed.

## Review/handoff state

G1, G2 (after native-opt-in correction), G3 independent passes are in reviews.md. Implementation and available offline checks are complete; independent final engineering/offline review passed with no blocking code findings (see reviews.md). Native/live verification remains blocked. Required native/live compatibility remains blocked as stated, rather than waived. #82 local package work does not complete broader #73/#74 or other #62 tickets. No commit/push/PR has been performed by this author.
