# Code skeleton and test interfaces

Revision1 status: approved revised interfaces below are implemented after G1/G2/G3; original declarations/reviews remain historical. Revised FR08 controls current accounting: six ShopExtract domain MCP invocations exclude schema-only ToolSearch/definition loading, separately recorded; all host/schema activity shares120s. The revised skeleton is declared below after G1; revised components await their stage after G2. Implementation remains gated on revised G3.

G1 passed independently. This stage adds acceptance tests only; production plugin remains absent. Detailed reuse/components follow G2.

## Production surface (declarations only)

- `integrations/claude-code/.claude-plugin/plugin.json`: native metadata object, plugin `shopextract`, version `0.1.0`, MIT, name/description/author; default locations avoid component path indirection.
- `integrations/claude-code/.mcp.json`: `mcpServers.shopextract` command `${SHOPEXTRACT_PYTHON}`, argv `[-m, shopextract.tools, --config, ${SHOPEXTRACT_CONFIG}]`, optional `type: stdio`; no inline credentials/env bootstrap or shell.
- `integrations/claude-code/skills/shopextract-review/SKILL.md`: YAML name/description, trusted workflow body. Preflight -> discover -> result(urls) -> extract -> single status poll -> result(products) -> one evidence lookup/report; stop pending/failure/budget. Six calls, two products, 120 seconds. No automatic retry, grants or permission preapproval.
- `integrations/claude-code/README.md`: exact local operator setup, native parser/version observations, private load/install/update/version/disable diagnosis, source/session restrictions and truthful live status.

No Python public API or server signature changes. No runtime stubs return fabricated success.

## Executable acceptance at this gate

`tests/test_claude_code_plugin.py` owns `required(path) -> str` (explicit missing-artifact assertion), metadata/layout assertions, exact direct argv assertion, trusted-skill guardrails and real `claude plugin validate --strict --json` with 20-second timeout. Native parser check explicitly opts in with `SHOPEXTRACT_NATIVE_CLAUDE=1`; ordinary pytest skips this proprietary-client integration check, which is not parser-pass evidence. When requested, missing client fails as a blocker and the actual result is saved separately. Native malformed/path/MCP negative matrix and stricter inventory tests will extend this module after G3.

`tests/test_claude_code_workflow.py` owns `declared_launch(executable: Path, config: Path) -> tuple[str,list[str]]`: read actual shipped declaration and replace only exact known placeholder values for the SDK. No general interpolation or shell. Test creates literal hostile executable/config names and launches the existing production CLI through real MCP SDK, initializes, checks restricted tool discovery, exercises denied origin, and asserts no injection sentinel. SDK exercise uses 15-second ceiling. This is SDK argv evidence, not evidence Claude expands variables correctly.

## Test fixture/driver interfaces for implementation stage

Keep these test-only, small and sequential; no new production launcher/framework:

- `fixture_runtime(case: str) -> ToolRuntime`: real runtime/parsers/jobs/evidence with controlled resolver and wire transport using seed24 source fixtures. Cases: two-record success, duplicate canonical identity, three-record/two-item partial cap, malicious source, source failure, pending gate and timeout. Choose fixed fixture byte/request bounds; no random sweep. Expose observed outbound requests for denied-origin assertions. Runtime remains production engine, not canned tool envelopes.
- `sdk_fixture_session(case: str) -> async context manager[ClientSession]`: new real stdio process calling existing MCP `serve(fixture_runtime(case))`; controlled CLI case selection is test-owned. Close/cleanup bounded to 15 seconds; one session process at a time.
- `run_recipe(call, url: str, *, max_calls=6, timeout_seconds=120) -> RecipeTrace`: test driver for the instruction recipe; trace has ordered actual calls/envelopes, stopping reason and selected record/evidence. Driver never creates expected product reports. Pre-submit budget/deadline checks; statuses/errors returned by real engine. Harness may await deterministic completion without extra tool calls before each planned result step; label these synchronization waits as offline-only. Pending cases deliberately withhold completion and must stop. Final trace is assertions/evidence, not a production export.
- Restart acceptance: run first SDK fixture session, retain one real handle, close it, then a second sequential fresh session submits old handle and observes existing denial/not-found/expired contract. No restart persistence shim.

Expected output envelopes remain existing schema1.0: `ok/data` or `ok/error`; Product/Variant identity fields, decimal strings, owner/evidence handles and partialness are reused without mapping. Missing optional support is unavailable, never filled with default facts.

## Failures and ownership

Package assertion failures are feature reds. Optional dependency/client absence is environmental blocked evidence. Invalid config uses existing CLI stderr/exit2; paths are literal argv. A relative path is outside documented plugin setup, not newly prohibited by core. Native parser errors and stricter repository inventory rejections must be reported separately. Model activation/injection compliance and actual host variable expansion remain SC08 live assertions; tests do not fabricate those passes.

## G3 component ownership refinement

See components.md: reuse the existing CLI/runtime/MCP without new production wrappers. A feature-specific test fixture may extend existing resolver/wire seams, selecting fixed payloads and response gates only. It must not mutate shared existing fixtures, replace jobs/parsers/evidence, or disguise the fixture process entry as the shipped production launch. Host variable expansion and model compliance remain separate live claims.

Implementation landed only after G3: the declared package plus standalone LICENSE, test-only fixture/recipe modules and documented actual evidence now exist. Current status is verification.md/status.md; earlier skeleton language records the preimplementation gate rather than implying files are still absent.

## Revision 1 skeleton (2026-10-25, after revised G1)

Revised G1 passed independently. This stage adds declarations and executable acceptance only; no skill/README/parser/fixture/harness implementation changes until revised G3. Existing delivered code is the red baseline.

### Test-side interfaces (no new production Python API)

- `tests.claude_code_recipe.select_product_url(urls: list[str], origin: str) -> str | None`: operate only on returned same-origin candidates. Decode the path before splitting so encoded separators cannot hide excluded segments; reject ambiguous backslash/encoded backslash paths rather than treating them as product routes. Exclude blog/blogs/article/articles/news/journal whole segments before positive ranking. Rank products/product/p/item/dp followed by nonempty item segment, then original URL lexical order. Preserve returned URL unchanged. `None` causes exact trace.stop `no product URL discovered`, no extract call. Schema-only accounting is not folded into this URL selector.
- `tests.claude_code_recipe.preflight_tools(definitions: list[dict], *, server_prefix: str) -> dict`: returned keys `ok`, `tools` (short operation -> actual full name), `reason`. Require exactly the five needed operation definitions from the trusted selected server prefix and schema_version1.0 in each input schema (const or enum). Missing/unusable definitions yield explicit prerequisite without executing a domain tool. No guessed namespace, extra schema probe domain call or permission grant.
- Existing `run_recipe` remains a bounded **mechanism oracle**, consumes actual domain envelope calls, and does not become the host model test. It invokes the selector, preserves max_items2 and six domain executions/120s; state/pending stop is truthful. Optional old completion hook is retained only for clearly labeled synchronized SDK success. Unsynchronized tests may impose finite **transport/caller latency** to let actual work start, but never join job completion before checking pending status.
- `tests.test_claude_code_plugin.parse_native_report(stdout: str, returncode: int) -> dict`: keys `valid`, `manifest_errors`, `manifest_warnings`, `ancillary_warnings`; parse actual nested manifest.errors. Successful exit plus valid nested shape/no errors and no explicit false validity is required. Missing/invalid JSON, authentication string, explicit false flags or nonempty manifest.errors returns valid false and diagnostic. Retain section-tagged ancillary warnings without inventing marketplace artifacts. Called by opt-in native validator check; no default native process call.
- `tests/claude_code_host_smoke.py` (test-owned, not distributed), `reduce_stream(events: list[dict], *, expected_tools: dict[str,str]) -> dict`: keys `domain_count`, `schema_host_count`, `skill_host_count`, `returned_products`, `evidence_verified`, `errors`, `outcome`. Deduplicate identical streamed tool_use IDs; conflicting reuse fails. Correlate tool_result IDs with actual successful envelopes. Known selected-server names map domain operations; schema-only ToolSearch is excluded from domain budget, Skill invocation is separately recorded, any other host tool/unknown server fails. No fake model execution.
- `host_preflight(...)->dict` and `run_host_case(...)->dict` in the same future test module: callable only under separate explicit `SHOPEXTRACT_CLAUDE_HOST_SMOKE=1` opt-in. Before inference require normal auth, supported bounded CLI invocation with max-turns plus an independent120s supervisor, source fixture/provenance and owned plugin copy. `--help` text alone is insufficient; use an actual non-inference native preflight establishing option acceptance or recognized version/capability evidence, with saved selected version. If support/auth cannot be established, blocked before inference. Default import/pytest must never launch `claude -p`.

### Stream and model-output contracts

Native trace parser consumes documented stream-json event families: assistant message content tool_use(id/name/input), user message content tool_result(tool_use_id/content/is_error), final result event. Synthetic fixtures use these shapes and are replay/parser tests, never actual host evidence. Actual installed-version shape discrepancies fail closed with bounded saved diagnostics; do not infer a pass from unfamiliar events or a final text string.

The positive host **test prompt** requests a structured final summary with outcome, product_url, owner_handle, evidence_id and evidence_status. Completed evidence must correlate selected product owner/field evidence with successful evidence tool arguments/result. No evidence-success claim without that correlation. Pending result may be honest and accepted as pending behavior, but does not fulfill a completed-evidence host claim. Exact no-product outcome has no extraction. This JSON output request belongs only to the test prompt; ordinary users are not forced into a harness format by the product skill.

`run_host_case` launches a real `claude -p --plugin-dir <copy> --output-format stream-json --verbose` only after eligibility. Copy hashes/fixture-only MCP override are saved. The stream supervisor counts domain6 separately from schema-host activity, returned products<=2 and wall<=120s, with bounded cleanup. Seventh emitted domain call is a failure even if observation/termination races execution; no false preventive guarantee. No shell/background tools or inference default. Actual output/return code/final completion, request log and domain evidence must all support pass. Up to3fixed prompts, sequential, no login/retry/client install.

### Realistic external source fixture seam

Extend `tests.claude_code_fixture.CASES` only after G3 with `index-blog-first`, `index-no-product`, `product-redirect`, `denied-redirect`, `delayed-discover`, `delayed-extract`. Fixture payloads<=16KiB; index/maps2entries each, discoverymax2, <=8requests per bounded case. Resolver/wire only; retain production ToolRuntime/jobs/normalization/evidence/MCP. Record request start before a finite<=1second response delay. A delayed pending assertion must prove that wire request was actually observed and active, rather than merely reading queued before scheduling.

For delayed tests, test caller latency may `await asyncio.sleep(.01)` after an actual call, while source response remains delayed .2-.5s; this models host round-trip time without awaiting completion. It is explicitly mechanism-only latency, not a host wait capability. Discovery phase may be made naturally fast/ready before extraction through finite caller latency; extraction request-start log and job_status show pending. No after_submit completion join in these representative cases. Cases have15s overall/2s cleanup bounds. Real-host model latency can cause completion instead: verify actual state/evidence rather than forcing a timing outcome.

### Intended red acceptance ownership

`tests/test_claude_code_revision.py` adds requirements-derived tests. Existing modules are imported normally; unavailable planned helpers are guarded by explicit callable/file assertions naming missing feature behavior, not accidental import failures. A real existing `run_recipe` no-product integration assertion is defined behind the explicit missing source-case guard; it will exercise real discovery/selection after that fixture seam is implemented. This is not a fabricated envelope test or a current pass. Source README assertions fail existing PyPI-ambiguous/bootstrap-absent guidance. Finite-delay fixture names have explicit missing-seam guards before invocation. No unavailable proprietary client/inference is needed for these reds.

Revision1 seam detail: finite-delay fixture requests are a sequence of `(method,url)` plus `active_delays` set observing real wire-response delay paths. Update the set at request entry and remove in finally after finite delay/cancellation. Pending tests assert both observed request and active delay, not just queued status. Add pure `assess_preflight(*, enabled: bool, normal_access: bool, capabilities: dict) -> dict` (`eligible`, `reason`); missing/false max_turns capability rejects before any inference. `host_preflight` gathers actual bounded non-inference evidence and passes it to this gate; a pure true decision is not host observation.

### Revision G2 runnable host harness and concrete bounds

Constants: `MAX_TURNS=10`, `WALL_SECONDS=120`, `CLEANUP_SECONDS=2`. Supervisor bound is independent from CLI turn limit; cleanup is TERM/wait1s then KILL/reap1s on a newly owned process group. stdout/stderr traces remain bounded; no attempt to kill user-owned processes. Unsupported safe process-group control blocks actual native execution. Test-only supervisor permits a smaller positive wall.2s for a controlled child; production host case always passes120/2.

Required executable test-owned interfaces (to implement after G3):

```python
host_preflight(*, enabled: bool = False, executable: str = 'claude',
               profile: Path | None = None, project: Path | None = None) -> dict
# Returns eligibility/reason plus selected executable/env/version/auth/capability
# evidence. Disabled returns before any subprocess. Eligible evidence establishes
# finite max-turns10 and the exact required flags without inference; help alone
# cannot authorize run_host_case.

build_host_argv(executable: str, plugin_dir: Path, prompt: str) -> list[str]
# Includes -p, --plugin-dir <one literal path>, --output-format stream-json,
# --verbose, --max-turns 10, --tools ToolSearch,Skill, then one literal prompt.
# No shell expansion, bypassPermissions, background agents or sleep tool.

supervise_process(argv: list[str], *, env: dict, cwd: Path,
                  wall_seconds: float = 120, cleanup_seconds: float = 2) -> dict
# Actually spawns owned subprocess/group, consumes bounded stream, independently
# enforces wall/cleanup, and reaps it. Returns events, returncode, timed_out,
# terminated, pid and safe diagnostics. PID/group belongs to this spawn only.

run_host_case(*, preflight: dict, plugin_dir: Path, project_dir: Path,
              prompt: str, expected_tools: dict, request_log_path: Path) -> dict
# Rejects ineligible/unsupported preflight before launch. Uses build_host_argv and
# supervise_process(wall_seconds=120,cleanup_seconds=2), then reducer+request-log
# evidence. A mocked supervisor result is only test wiring, never saved host pass.
```

Runnable acceptance tests must fail if only a reducer/dummy host module exists: preflight and run_host_case are callable; default/blocked calls cause zero Popen/run; eligible case actually routes literal argv through supervisor with exact bounds; generic supervisor actually terminates/reaps a controlled TERM-ignoring Python child. Controlled child stdout is synthetic parser/supervisor fixture and never labeled a Claude/model result. Caller/test fallback cleanup prevents a leaked child on broken supervisor implementation. No actual native inference before G3 or by default pytest.

Preflight capability decision requires true max_turns, plugin_dir, stream_json and restricted_tools support; absent/ambiguous support blocks native execution. Unit wiring supplies explicit synthetic eligibility only for that test, not host evidence. Controlled supervisor acceptance has an independent4s POSIX signal watchdog and fallback child ownership check, so a broken subject cannot leave the intended60s sleeper running or signal a reaped/reused PID.

### Revision G3 component refinement (declarations only)

See components.md Revision1 for the exact ownership matrix. Reuse existing SDK/runtime/domain schemas/source parsers; no production executables/wrappers. New smoke module owns only eligibility/argv/stream/reducer/supervisor. Native case raw stdout+stderr combined cap1MiB; collect bounded chunks without blocking one pipe behind the other, terminate/fail on invalid/oversize trace. Owned group only, no global process signals. Non-inference eligibility setup and in-model schema preflight are distinct: the latter is inside the case120s alongside all schema/domain activity. Fixture-only copied MCP declaration/hash is recorded and never distributed. Operator setup offline seam validates real bootstrap/build ordering without installing/downloading merely to test docs or claiming fresh-install success from source imports.

Eligibility setup bound: at most3non-inference probes (selected version, exact flag-acceptance/capability, normal auth), each<=5s with<=2s owned cleanup on timeout; stop at first blocker and do not auto-retry. No probe runs when opt-in is absent. These setup observations precede a model case; model-visible tool/schema preflight remains inside its120s supervisor.

Implemented after reviewed SC15b: supervise_process returns group_cleanup details even on normal exit; direct parent returncode is preserved. Cleanup checks only owned group membership/state, signals boundedly, and separates direct-child reaping from indirect zombie observations. The saved red proves the old normal-exit survivor; controlled targeted green proves the repair, not actual native/model operation.

### Focused final-review interface correction (awaiting affected review)

`run_host_case(..., expected_case: str)` gains a required trusted keyword. It validates the fixed case before launch and binds reducer outcome to it. `success` can be passed only with complete/evidence_verified/domain and source execution; truthful pending returns incomplete. `unrelated` requires no activation; `missing-grant` requires an actual selected-server permission_denied envelope, recorded by reducer as correlated domain denial metadata. CLI passes the case explicitly. No optional default can reintroduce model-selected case acceptance.

host_preflight's probe collector retains sanitized supervisor state and rejects timeout/terminated/diagnostics/unverified cleanup before consuming stdout; each stage stops immediately. Actual supervisor boundary cases exercise existing pipe collection/stop/owned cleanup, not just reduce_stream. Selector rejects original encoded slash/backslash before decode, then checks residual encodings/exclusions/dots. Empty-discovery branch stays distinct. No new production APIs/components or native inference.
