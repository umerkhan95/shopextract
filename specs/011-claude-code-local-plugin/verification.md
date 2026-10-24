# Verification evidence

## Current revision1 result (2026-10-25)

Plugin version0.1.1 is implemented; revised G1/G2/G3 and supplemental SC15b design review passed. Final available affected checks after focused reviewed corrections: **219 passed,1 native-parser skip in74.39s**. Focused repairs passed28/4.52s after the saved20red/8green reproduction. The bounded driver returned0, did not time out, had no diagnostics, reaped its direct child and verified its group disappeared with0indirect zombies (evidence/revision-1/final-affected-driver.json). Default native skip is not native compatibility evidence. Independent final review is next; no author commit/push.

| Revision evidence | Actual outcome |
| --- | --- |
| revision-1/baseline.json | Existing unsynchronized recipe queued after2domain calls;0products, mechanism-only |
| revision-1/acceptance-red.txt |29 intended failures/0.60s before implementation |
| revision-1/acceptance-red-g2.txt |32 intended failures/0.96s after runnable-harness/bound tests added |
| revision-1/green-smoke.txt |12passed/0.10s, small smoke saved before expansion |
| revision-1/focused-green.txt |48passed/1native skip1.81s |
| revision-1/offline-plugin.txt |77passed/1native skip35.27s |
| revision-1/normal-exit-red.txt |1intended failure0.52s: successful parent left controlled child running; fallback cleaned owned group |
| revision-1/supervisor-green.txt |5passed3.07s after reviewed group-cleanup repair; actual controlled processes, not models |
| revision-1/affected-regressions.txt |191passed,1native skip69.03s, historical prior affected run |
| revision-1/final-review-red.txt |20intended failures/8passes4.73s, before narrow repairs |
| revision-1/final-review-green.txt |28passed4.52s after repairs |
| revision-1/final-affected-regressions.txt |**219passed,1native skip74.39s**, latest affected run |
| revision-1/final-affected-driver.json |Exit0, no timeout/diagnostics; owned group disappeared, direct child reaped,0indirect zombies |
| revision-1/local-preflight.json |One actual local version probe1.0.35; blocked known-capability gate, **0model calls** |

Final command: existing .venv Python `-m pytest tests/test_claude_code_review_repairs.py tests/test_claude_code_revision.py tests/test_claude_code_plugin.py tests/test_claude_code_workflow.py tests/test_mcp_reference_client.py tests/test_agent_tool_api.py tests/test_tool_lifecycle.py tests/test_tool_bootstrap.py tests/test_evidence_contracts.py tests/test_field_resolution.py -q --tb=short`, under `PYTHONPATH=src:.`, OMP/OpenBLAS/MKL2 and tokenizer parallelismfalse. `supervise_process(...,wall_seconds=120,cleanup_seconds=2,parse_events=False)` bounded the whole run and saved driver status separately. No unrelated/full-repository suite claim. Compileall on changed helpers/tests and `git diff --check` passed. Source bootstrap `--help` ran within the suite without pip/build/download; this verifies the offline setup seam, **not** a fresh installation. Existing RequestsDependencyWarning remained.

Coverage: domain/schema preflight accounting; ranked same-origin product candidates, encoded separators/backslashes and exact no-product result; real index/blog-first and same/denied redirect paths; finite observed wire delays without completion joins; nested manifest.errors/warnings and auth-text rejection; real runnable CLI/default opt-in/eligibility/argv/stream reducer; false evidence/article/unreturned URL/state/permission traces; actual direct-timeout and normal-parent-exit descendant cleanup. Supervisor preserves parent exit0 and records indirect zombies separately; no claim it reaps indirect orphans. Host-level permission denial is explicit; no MCP preapproval or bypass added.

Actual native model cases were **not run locally**. The inaccessible cloud2.1.310/modelclaude-sonnet-5-5 results and named ZIP remain user-reported/uninspected. Wrapped stream runs are separate from reported unmodified .mcp/real-config5tool startup without stream. Existing SDK synchronized success/replayed stream fixtures/control subprocesses are mechanism evidence only. No client/package install, login, credential copy, public publishing or model sweep. Actual token counters unavailable; no quota percentage inferred. No src/ production-core changes.

The following sections retain historical original and intermediate results; their pending-stage notes do not supersede the current revision status above.

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

G1, G2 (after native-opt-in correction), G3 independent passes are in reviews.md. Implementation and available offline checks are complete; independent final engineering/offline review passed with no blocking code findings (see reviews.md). Native/live verification remains blocked. Required native/live compatibility remains blocked as stated, rather than waived. #82 local package work does not complete broader #73/#74 or other #62 tickets. Author made no commit/push. Coordinator delivered draft PR #89 and updated #82 evidence; implementation commit 2988600. Native/live blockers keep the PR draft and tickets open.

## Revision 1 preparation baseline (2026-10-25)

Saved `evidence/revision-1/baseline.json` before revised design expansion. Command used existing .venv Python, isolated `PYTHONPATH=src` and bounded thread env; `asyncio.wait_for(run_recipe(engine.call, ORIGIN),5)` against existing success fixture with **no after_submit completion synchronization**. Actual result: queued after discover/job_result,0records,0outbound requests before stop; runtime closed in finally. This reproduces the timing gap in SDK-only success assumptions; it does not establish host/model behavior. No test/production code changed and no new intended red/green or native result is claimed yet. User-reported2.1.310 native success remains separately attributed, while prior local1.0.35 observations remain historical local evidence.

### Revision 1 intended acceptance red (after revised G1)

Command: `PYTHONPATH=src OMP_NUM_THREADS=2 OPENBLAS_NUM_THREADS=2 MKL_NUM_THREADS=2 TOKENIZERS_PARALLELISM=false /Users/umerkhan/code/shopextract/.venv/bin/python -m pytest tests/test_claude_code_revision.py -q --tb=short`.

Actual result: **29 failed in0.60s**, saved evidence/revision-1/acceptance-red.txt. All failures are intended new-contract assertions: old skill lacks domain-only/preflight/selection wording; old README lacks source-bootstrap/attribution/troubleshooting; selector/schema/native-report helpers and host harness module are explicitly absent; six realistic external source seams are explicitly absent. Guards name the missing feature interface before executing it; no ImportError/ModuleNotFoundError, optional native-client error, dependency install or inference explains these failures. Parameterized cases define distinct expected classifications/adverse events for later implementation; they are not29 independent implemented mechanisms or29 runtime failures. New real-runtime delayed/no-product integration assertions remain behind missing-fixture guards, not falsely marked executed.

No plugin/README/fixture/recipe/parser/harness implementation was changed in this stage. Skeleton declares interfaces, encoded-separator handling, actual finite-delay request observations and non-inference max-turn eligibility gate. Revised G2 review pending; production depends on revised G3. The old SDK baseline is reused, not rerun as new red evidence.

### Additional user-reported cloud evidence (not locally inspected)

User clarification relayed by coordinator2026-10-25: Claude Code2.1.310 at a cloud-sandbox executable path is inaccessible locally; it is not a client to locate/install here. Bundle named `shopextract-pr89-claude-code-2.1.310-evidence.zip` is reported but not attached/accessed/inspected by this author. Reported validation on bce3d9b exited0 with full nested manifest JSON; the reported native-enabled focused suite had1assertion failure/35passes. Reported4stream runs used model `claude-sonnet-5-5`: fixture success, pending-extract and2muskvice replays, with test wrappers supplied through SHOPEXTRACT_PYTHON. Separately, the user reports unmodified .mcp plus real operator config started the real server and exposed5tools, with no stream saved for that separate observation. The sandbox inherited the skip-plugin-MCP flag and the user unset it for those host runs.

These are **user-reported observations**, not local reproductions, inspected raw traces or proof of an unmodified production server in the wrapped stream runs. Keep version/model/wrapper distinction and local1.0.35 auth blocker separate. No cloud access search/new login/client install/model run is authorized by the bundle name alone; current author model usage remains0runs. Later actual harness limits remain model-sensitive and require eligible bounded normal access.

### Revision G2 correction: runnable host harness acceptance and exact bounds

Reviewer required explicit finite turn/cleanup bounds and tests that cannot pass with a reducer-only module. Design/skeleton now set max-turns10,120s process wall and2s total owned-group cleanup (TERM/wait1s, KILL/reap1s). Added intended-red tests for callable host_preflight/run_host_case, disabled/ineligible zero subprocess launch, literal argv and eligible runner-to-supervisor wiring with exact120/2 parameters, plus genuine controlled-process timeout/reaping. A test-only independent4s signal watchdog bounds a broken supervisor test, and fallback only signals a still-owned child (not a reaped/reused PID). The supervisor fixture is plain Python/synthetic events, not Claude/model evidence.

Rerun same revision pytest command: **32 intended failures in0.96s**, saved evidence/revision-1/acceptance-red-g2.txt. The3new tests currently stop at the explicit absent host-harness module guard. They have **not** spawned a controlled child or native/model client yet; implementation remains prohibited until revised G3. Earlier29failure log remains historical. No production/fixture/helper implementation changed. Awaiting focused independent G2 re-review.

## Final-review correction intended reds (before repair)

Defined FR15..18/SC16..19 and affected test/interface/component contracts before adding `tests/test_claude_code_review_repairs.py`. Ran only that file with the existing bounded thread/PYTHONPATH environment: **20 failed,8 passed in4.73s**, saved evidence/revision-1/final-review-red.txt. Failures reproduce wrong/unexecuted case acceptance, missing explicit case binding/denial provenance, positive pending falsely passed, unsafe supervision ignored in version/flags/auth probes, and single original encoded slash accepted contrary to clarified policy. No import/client/auth incidental error explains the reds.

The8passes include4genuine harmless supervisor subprocess cases: invalid JSON, combined stdout/stderr overflow, seventh domain-tool emission and unexpected-tool emission. Each existing supervisor stopped/terminated/reaped its controlled child and verified owned-group cleanup within existing bounds; retained output stayed<=1MiB. These are live pipe/supervisor mechanism observations, not native/model/tool execution. Other passes cover already-conservative encodings and query-only ToolSearch rejection of unverified optional fields. No native client/model run or production/helper repair occurred during this red/design stage.

Focused affected G1/G2/G3 review is requested before repair of case/eligibility/selector code. Prior191pass result remains a valid historical regression result for that code revision, not approval against these newly reproduced gaps. User-reported cloud bundle remains uninspected; actual local model calls remain0.

## Focused correction implementation and handoff

Focused affected G1/G2/G3 passed before helper repairs. Required expected_case now flows from the CLI controller into every run; only complete evidence plus observed source execution passes success, supported pending is incomplete/nonzero and stops the driver, unrelated requires no activation/source requests, and missing-grant requires correlated selected-server permission_denied from discover/extract. Each version/flag/auth probe records sanitized supervision metadata and fails before parsing stdout on timeout, forced termination, diagnostics or unverified cleanup. The same clean-supervision predicate gates case completion. Original single/double encoded separators reject; unreserved encoding remains eligible. Four genuine invalid-JSON/combined-byte-cap/seventh-tool/unexpected-tool subprocess checks remain in the latest219test run. ToolSearch query-only payload is a conservative offline contract; optional max_results native compatibility remains unverified. No native/model inference was run; earlier local blocked/user-reported cloud distinctions remain unchanged. Final independent engineering/offline re-review passed (reviews.md); no author commit/push.
