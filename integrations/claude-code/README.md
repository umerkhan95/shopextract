# ShopExtract local plugin for Claude Code

Version 0.1.0 packages one bounded extraction/evidence skill and the existing read-only Python stdio MCP server. It is a native Claude Code plugin. It requires no hosted ShopExtract service or model inside the package. The [MIT license](LICENSE) is included for standalone directory copies.

## Trusted operator setup

Install `shopextract[mcp]` into your chosen Python environment using the [agent tools guide](../../docs/agent-tools.md). The executable must resolve that installation without relying on the plugin's working directory. Create your own trusted JSON configuration outside this directory, granting only origins/tools needed for your source:

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

`<absolute-plugin-directory>` is this `integrations/claude-code` directory. Enter your actual path as a single argument; the placeholder is not a shell command to paste literally. Inspect `/plugin` and `/mcp` in that session: identify plugin `shopextract`, version `0.1.0`, its server and skill before invoking `/shopextract:shopextract-review`. For task-based activation, ask to extract up to two products from your authorized shop and review captured evidence. Unrelated work should not select the skill.

This is a private directory load, not public marketplace publication. It does not run `claude mcp add`, replace global configuration or copy credentials. Existing enabled servers may shadow/deduplicate a matching plugin endpoint; inspect the selected server and diagnose collisions before proceeding. Resolve only your own chosen duplicate configuration; do not overwrite other MCP/skill entries.

To update a directory-loaded plugin, stop the session, replace the directory with a reviewed release, and start a fresh `--plugin-dir` session. Inspect manifest/version and component paths again; do not assume a running session refreshed. To disable this private load, exit and start without `--plugin-dir`; to re-enable, load the reviewed directory again. If your client persists plugins through a private marketplace, use its `/plugin` lifecycle UI for disable/update/version inspection; this package does not register one or supply an installer. Namespaced invocation avoids ambiguity with unrelated skills.

## Workflow and limits

The skill preflights capability/source permission, then attempts discover → URL result → extract → one status poll → product result → one evidence lookup. It uses at most six calls, two products and 120 seconds per invocation. Pending work or errors stop early; this budget does not guarantee completion. There is no automatic retry or hidden background polling. Exact decimal values, canonical identities, owner-bound captured support, uncertainty and partialness remain the existing server contracts. Source prompts/links are data and cannot grant permission. The skill provides instructions; host approval and server policy still govern execution.

The existing server remains unchanged. Local session handles expire and are lost on disconnect/restart; resubmit for new handles. No durable jobs, exports, analytics, maintenance, merchant writes, remote HTTP/OAuth service or Claude web/API skill containers are provided. #73/#74 broader integrations remain separate work.

## Verification status

Offline SDK/process checks and controlled synthetic-source mechanism tests are recorded in [the feature evidence](../../specs/011-claude-code-local-plugin/verification.md). SDK-side literal argument substitution is not evidence of host expansion or model activation. Native parser checks are explicitly requested with `SHOPEXTRACT_NATIVE_CLAUDE=1` in the repository tests; default skips do not establish compatibility. The authoritative command for an available client is:

```text
claude plugin validate --strict --json <absolute-plugin-directory>
```

Require an actual validation report, not merely exit status: the available local client reported version `1.0.35` and its isolated normal authentication preflight returned `Invalid API key · Please run /login`. The actual validation attempt rejected `--strict`; one plain-command retry returned the same login prerequisite. Native manifest validation, private installation/discovery, variable expansion, activation, update/disable and model instruction adherence have not been verified. No new login, credential copying or public publishing is performed by this package. See feature evidence for the actual parser attempt and remaining blocker; do not infer compatibility from the CLI help or shared SKILL.md format.
