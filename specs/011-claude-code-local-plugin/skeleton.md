# Code skeleton and test interfaces

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
