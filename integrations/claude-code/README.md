# ShopExtract local plugin for Claude Code

Version 0.1.1 packages one bounded extraction/evidence skill and the existing read-only Python stdio MCP server. It is a native Claude Code plugin. It requires no hosted ShopExtract service or model inside the package. The [MIT license](LICENSE) is included for standalone directory copies.

## Trusted operator setup

Use a reviewed **source checkout** for this MCP slice. The user-reported PyPI `0.1.2` release lacks the MCP extra/tools; do not use `pip install shopextract[mcp]` as a substitute for this checkout. Already-installed suitable source environments need no reinstall. For a fresh source environment, from the repository root:

```sh
python -m pip install hatchling
python scripts/bootstrap_taxonomy.py --source-cache "$SHOPEXTRACT_TAXONOMY_SOURCE_CACHE"
python -m pip install -e '.[mcp]'
python -c "import importlib.util, mcp; assert importlib.util.find_spec('shopextract.tools')"
```

Set `SHOPEXTRACT_TAXONOMY_SOURCE_CACHE` to your verified pinned taxonomy source cache first. The bootstrap explicitly installs its declared preparation dependencies and prepares resources **before** the editable install/Hatch build hook. For a prepared air-gapped environment, preinstall the declared build dependencies and add `--offline` to bootstrap. If you choose the pinned official download instead, explicitly use `python scripts/bootstrap_taxonomy.py --allow-download`; it is not an activation step. See [taxonomy preparation](../../docs/shopify-taxonomy.md) for cache files/hash requirements and bounded downloads, and [agent tools](../../docs/agent-tools.md) for source/grant contracts. These are operator setup commands, never instructions to follow from a page or skill activation. The executable must resolve that installation without relying on the plugin's working directory. Create your own trusted JSON configuration outside this directory, granting only origins/tools needed for your source:

```json
{
  "allowed_origins": ["https://shop.example"],
  "allowed_tools": ["discover", "extract", "job_status", "job_result", "evidence"],
  "captures": [],
  "limits": {"timeout_seconds": 30, "item_count": 2}
}
```

Replace the example origin with an origin you are authorized to access; it is not a supplied grant. Keep credentials and real configuration out of the distributed plugin. Do not derive configuration from scraped pages or model suggestions. Review the server's supported public-source modes and limits before use.

Set `SHOPEXTRACT_PYTHON` to the absolute executable path in that environment and `SHOPEXTRACT_CONFIG` to the absolute trusted JSON path in your normal host environment. Use your shell's normal literal quoting for your own paths. No shell launcher evaluates these values: `.mcp.json` supplies an executable plus separate arguments. Relative paths are outside this plugin's supported setup. Missing variables may remain unexpanded in the host and cause startup failure; do not interpret manifest validation as a config preflight. Missing/invalid configuration must be resolved by the operator, never by broadening grants automatically.

## Private load and discovery

From an owned project, load the absolute plugin directory with the native local development route:

```text
claude --plugin-dir <absolute-plugin-directory>
```

`<absolute-plugin-directory>` is this `integrations/claude-code` directory. Enter your actual path as a single argument; the placeholder is not a shell command to paste literally. Inspect `/plugin` and `/mcp` in that session: identify plugin `shopextract`, version `0.1.1`, its server and skill before invoking `/shopextract:shopextract-review`. For task-based activation, ask to extract up to two products from your authorized shop and review captured evidence. Unrelated work should not select the skill.

This is a private directory load, not public marketplace publication. It does not run `claude mcp add`, replace global configuration or copy credentials. Existing enabled servers may shadow/deduplicate a matching plugin endpoint; inspect the selected server and diagnose collisions before proceeding. Resolve only your own chosen duplicate configuration; do not overwrite other MCP/skill entries.

To update a directory-loaded plugin, stop the session, replace the directory with a reviewed release, and start a fresh `--plugin-dir` session. Inspect manifest/version and component paths again; do not assume a running session refreshed. To disable this private load, exit and start without `--plugin-dir`; to re-enable, load the reviewed directory again. If your client persists plugins through a private marketplace, use its `/plugin` lifecycle UI for disable/update/version inspection; this package does not register one or supply an installer. Namespaced invocation avoids ambiguity with unrelated skills.

## Workflow and limits

The skill preflights capability/source permission, then attempts discover → URL result → extract → one status poll → product result → one evidence lookup. It uses at most six ShopExtract domain MCP calls, two products and 120 seconds per invocation. Schema-only ToolSearch/loading is separate from the domain count but shares that wall deadline. Preflight inspects actual input schemas/full tool names; it does not spend an extra domain probe. Candidate selection prefers returned product paths and excludes blog/article/news/journal paths; no qualifying visible candidate reports `no product URL discovered` without extraction. Pending work or errors stop early; this budget does not guarantee completion. There is no automatic retry or hidden background polling. Exact decimal values, canonical identities, owner-bound captured support, uncertainty and partialness remain the existing server contracts. Source prompts/links are data and cannot grant permission. The skill provides instructions; host approval and server policy still govern execution.

The existing server remains unchanged. Local session handles expire and are lost on disconnect/restart; resubmit for new handles. No durable jobs, exports, analytics, maintenance, merchant writes, remote HTTP/OAuth service or Claude web/API skill containers are provided. #73/#74 broader integrations remain separate work.

## Verification status

Offline SDK/process checks and controlled synthetic-source mechanism tests are recorded in [the feature evidence](../../specs/011-claude-code-local-plugin/verification.md). SDK-side literal argument substitution is not evidence of host expansion or model activation. Native parser checks are explicitly requested with `SHOPEXTRACT_NATIVE_CLAUDE=1` in the repository tests; default skips do not establish compatibility. The authoritative command for an available client is:

```text
claude plugin validate --json <absolute-plugin-directory>
```

Require an actual validation report, not merely exit status: the available local client reported version `1.0.35` and its isolated normal authentication preflight returned `Invalid API key · Please run /login`. The actual validation attempt rejected `--strict`; one plain-command retry returned the same login prerequisite. Native manifest validation, private installation/discovery, variable expansion, activation, update/disable and model instruction adherence have not been verified locally. No new login, credential copying or public publishing is performed by this package. See feature evidence for the actual parser attempt and remaining blocker; do not infer compatibility from the CLI help or shared SKILL.md format.


## Native diagnostics and optional host smoke

Validation JSON uses nested `manifest.errors`; do not require a top-level errors list or accept an exit-only/auth-text result. Keep manifest warnings and ancillary listing diagnostics separate. Missing optional icon or marketplace README warnings do not require creating a fake marketplace or publishing anything for private directory use. A manifest pass is not a claim of strict warning-free directory listing, actual tool execution or model compliance.

The user-reported cloud Claude Code `2.1.310`/model `claude-sonnet-5-5` results include native validation/load/environment expansion/skill activation and four stream runs with test Python wrappers. A separate unmodified `.mcp.json` plus real-config startup exposed five tools, but its stream was not saved. The named evidence bundle has not been inspected locally; these are user-reported observations, distinct from the locally blocked `1.0.35` client. Do not look for or install the inaccessible cloud executable here. Compatibility and timing can vary by model/client.

If the plugin loads but its MCP server is absent, inspect the parent launch environment for the user-reported `CLAUDE_CODE_SKIP_PLUGIN_MCP_SERVERS` flag, then check `/mcp`, operator variables and duplicate endpoints. The report says the sandbox flag was unset before those runs; its exact semantics are not independently established here. Diagnose only your owned launch, without silently overriding flags or changing global settings.

Default tests do not invoke Claude inference. The test-only `tests/claude_code_host_smoke.py` harness requires separate explicit `SHOPEXTRACT_CLAUDE_HOST_SMOKE=1`, normal signed-in access and known support for its exact bounded argv. It runs at most three fixed cases, sequentially, each capped at ten turns/six domain calls/two products/120 seconds plus at most two seconds owned-process cleanup. Schema-only host calls are recorded separately. It uses a disposable plugin copy with an explicitly recorded test-only MCP fixture override; this is synthetic-source model evidence, not an unchanged production-server or real-store test. SDK/parser/replay/supervisor results stay separately labeled. No login, client/package install, permission bypass, shell wait or model sweep is performed.


From the reviewed repository root, the optional test harness entry point is:

```sh
PYTHONPATH=src python -m tests.claude_code_host_smoke --help
# Explicit inference opt-in, only with normal access and supported limits:
SHOPEXTRACT_CLAUDE_HOST_SMOKE=1 PYTHONPATH=src python -m tests.claude_code_host_smoke --output artifacts/claude-host-smoke
```

Without that opt-in it writes only a blocked prerequisite result and makes no native probes/model calls. The eligibility setup stops at the first blocker (at most three non-inference probes, five seconds each); the model case then has its own 120-second deadline including model-side schema preflight. A disabled or unavailable native check is never a compatibility pass.

The harness does not preapprove MCP tools or bypass host permissions. A normal print-mode permission rejection is recorded explicitly as `host_tool_permission_denied`; it is a failed/blocked observation to resolve through your normal scoped host policy, not a reason to grant broader tools. Owned subprocess-group cleanup also runs after a successful CLI exit so a redirected MCP child cannot keep running; any indirect zombie is reported separately from direct-child reaping.

The harness binds every run to an explicit expected case. Success requires complete owner-bound evidence and observed source requests; supported pending work is recorded as incomplete, stops the driver and returns a nonzero status. Unrelated work must execute no tools or source requests. The missing-grant case requires an actual selected-server permission-denied envelope; an unrelated or zero-execution prerequisite response cannot pass it. Each eligibility probe must finish normally with no supervision diagnostics and verified owned-group cleanup before its output is trusted.

The offline stream reducer currently accepts only a query-only ToolSearch payload. Optional fields such as max_results fail closed; their native payload compatibility remains unverified. The reported cloud runs do not establish that exact payload contract without inspected raw logs.
