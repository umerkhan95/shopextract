# INT-04: Claude local and remote MCP compatibility

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#66](https://github.com/umerkhan95/shopextract/issues/66).
Related planned work: [INT-01 / #63](https://github.com/umerkhan95/shopextract/issues/63), [INT-02 / #64](https://github.com/umerkhan95/shopextract/issues/64), [INT-12 / #74](https://github.com/umerkhan95/shopextract/issues/74).

Status: planned; researched2026-10-24. Owner: Claude integration maintainer.
Dependencies: delivered #24 for local stdio; INT-02 for remote transport/auth.
Covers FR06/03/04, SC06/03/04. Installation guides and compatibility evidence are
separate from public connector-directory review or a future Claude skill package.

## Two distinct connection routes

Reuse the existing local `python -m shopextract.tools --config <operator-file>`
server. Provide a minimal Claude Desktop `mcpServers` JSON fragment and Claude Code
stdio command using the chosen Python environment. Merge config instructions, never
replace a user's unrelated servers. Existing capture paths and allowed origins are
trusted operator configuration, not prompt arguments. [Local connection guidance](https://modelcontextprotocol.io/docs/2026-07-28/develop/connect-local-servers)
shows the Desktop configuration mechanism; the ShopExtract package requires Python,
not the example filesystem server's Node dependency.

[Claude Code MCP](https://code.claude.com/docs/en/mcp) documents local stdio and
remote HTTP setup, OAuth and process shutdown. Record actual versions/OS and
stdio cleanup behavior instead of assuming a generic client keeps the process alive.
Remote setup uses INT-02 service URL plus end-user authorization. Per
[remote connector help](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp),
Claude account remote connectors connect from Anthropic cloud, including desktop
clients; a locally reachable VPN/localhost endpoint alone is insufficient. Account
and organization permissions govern setup. Document network access without copying
static IP lists into code.

## Tool behavior and workflow

Show list→discover/extract→job_status→job_result→evidence, plus matching authorized
catalogs and reviewing reliable changes between granted historical captures. Tool
surface is the same eight operations; no added export/analytics/category/maintenance
or browser/LLM fallback. One request may need several calls, so recipe instructions
must cap polling and return job identity when unfinished, not ask the model to loop
forever. Evidence support and uncertainty must survive any assistant explanation.

Local disconnect cancels owned session work/releases handles; remote disconnect is
not automatic cancellation of durable jobs. Reconnect requires valid owner identity.
No authentication token or operator path enters tool output. Source text is not
instructional authority. MCP request cancellation and job_cancel are distinct effects.
Any host consent remains truthful for durable submissions and cancellation.

## Acceptance and future verification

- [ ] Actual Claude Desktop local and Claude Code local list/call/session-exit tests record separate results; install docs preserve existing config.
- [ ] Remote connect/login/list/extract/status/result works with declared protocol; unsupported negotiation or account policy stays blocked.
- [ ] Owner A cannot reuse B's job/evidence/cursor; revoked token blocks continuation, correct reconnect preserves durable references or reports expiry.
- [ ] Local restart shows expired session handles rather than durable recovery; remote restart follows INT-01 persistence contract.
- [ ] Supported/unsupported stock, decimal strings and captured evidence remain inspectable; malicious source instructions do not broaden grants.

Run controlled MCP mechanism cases first; future live ceiling is one small local and
remote case, ≤12calls each, two products,120seconds/case. Recheck exact host tool
limits/version compatibility before running. No Claude client was configured or live
verified here. A public listing is external optional distribution, not acceptance
criteria for private compatibility; skills installation is covered by INT-12.
