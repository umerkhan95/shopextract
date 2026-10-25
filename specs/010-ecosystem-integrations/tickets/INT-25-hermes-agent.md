# INT-25: NousResearch Hermes Agent skill/plugin and MCP integration

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#87](https://github.com/umerkhan95/shopextract/issues/87).
Related planned work: [INT-02 / #64](https://github.com/umerkhan95/shopextract/issues/64), [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73).

Status: researched/planned;2026-10-24. Owner: Hermes integration maintainer.
Dependencies: INT-11 portable instructions; #24 local or INT-02 remote approved MCP.
Covers FR24, SC24/16/17/18 plus shared auth/data/source boundaries. This targets Hermes
Agent runtime, not an arbitrary application using a Hermes model.

[Working with Skills](https://hermes-agent.nousresearch.com/docs/guides/work-with-skills)
documents native skill directories/install/discovery and session refresh behavior.
Use one reviewed instructions-only pack, inspect selected version and invoke intended
workflow. Host/plugin skill namespacing and discoverability vary by route; verify exact
runtime rather than assume all plugin skills appear in the same list automatically.

[MCP documentation](https://hermes-agent.nousresearch.com/docs/user-guide/features/mcp)
provides config-driven local stdio and remote tool connections. Reuse guarded ShopExtract
server and approved owner grants. Do not enable unrelated Hermes messaging/gateway
capabilities or expose Hermes itself as a broad tool server merely to extract products.
Credentials, sources and model provider are independent configuration concerns.

[Plugin authoring](https://hermes-agent.nousresearch.com/docs/developer-guide/plugins)
distinguishes native plugin.yaml/register(ctx) from a portable Agent Pluginsv1 subset.
Prefer minimal portable plugin.json+skills+mcp.json when exact tested runtime supports
it, avoiding unnecessary Python registration/hooks. If native plugin required, design
its minimal registration/capabilities before code. Install-disabled, validate and enable
explicitly in owned profile; manifest environment strings are public package data, not
secret storage. Invalid components may be skipped independently: partial load cannot
be reported as full successful plugin compatibility.

Public catalog submission and dependency installation are separate later work. Do not
execute validation flags that install dependencies in this documentation scope. Fix
runtime versions and verify namespace/server conflict rules before packaging.

- [ ] Native skill and chosen plugin route discover exact workflow plus approved MCP; fresh/update/session behavior observed separately.
- [ ] Disabled/partially loaded package, duplicate server, missing auth/tool or denied capability yields explicit status, no fake completeness.
- [ ] Path/symlink/secret/script fixtures reject; baseline requests no privileged override or messaging permissions.
- [ ] Actual tool path preserves evidence/decimal/uncertainty and lossless sequence; model-only endpoint cannot pass agent install checks.

Future smoke one clean install/update/three prompts, ≤6tools/two products/120seconds;
model requests require exact key/token/pricing$1 preflight. No Hermes runtime installed,
provider selected, skill/plugin built, model run or public submission here.
