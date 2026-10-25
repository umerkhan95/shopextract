# INT-18: Grok Build plugin and Grok/xAI tool integration

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#80](https://github.com/umerkhan95/shopextract/issues/80).
Related planned work: [INT-01 / #63](https://github.com/umerkhan95/shopextract/issues/63), [INT-06 / #68](https://github.com/umerkhan95/shopextract/issues/68), [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73), [INT-19 / #81](https://github.com/umerkhan95/shopextract/issues/81).

Status: researched/planned;2026-10-24. Owner: Grok integration maintainer.
Dependencies: INT-18a tool-route compatibility reuses#24local or INT-01/02remote;
INT-18b native plugin packaging consumes18a plus INT-11/19skill subset. INT-19does
not wait for18b. Covers
FR19, SC19/03/04/13. Reuse commerce engine; no native support inferred from model name.

Three distinct routes are documented. [Grok Build extensions](https://docs.x.ai/build/features/skills-plugins-marketplaces)
provide local plugins, skills and MCP components with marketplace sources; this is a
native coding-agent package target. [CLI reference](https://docs.x.ai/build/cli/reference)
provides inspect/plugin validation/install/update commands. Deliver a minimal reviewed
plugin wrapper with approved skills/MCP configuration, no hooks/background agents or
auto-install scripts. Exact manifest and local MCP config schema are child prerequisites;
claimed Claude compatibility does not replace our package/parser tests.

[grok.com connectors](https://docs.x.ai/grok/connectors) separately documents a custom
MCP URL setup flow with required auth and public reachability. Record private consumer
connection separately from Grok Build filesystem plugin and catalog acceptance.

[xAI API remote MCP](https://docs.x.ai/developers/tools/remote-mcp) supports custom
endpoint, tool allowlist and authorization, but explicitly lacks OpenAI `require_approval`
and `connector_id` support. Do not copy INT-06 approval payloads. Enforce user-authorized
operations/scopes/limits in service; if application approval cannot be reliably enforced,
block state-changing admission rather than claim provider-mediated approval. Model/tool
eligibility, protocol and billing require exact child preflight. Ordinary automation
still needs no model.

- [ ] Build plugin validates/installs in owned profile; skill+MCP discovery/update is exact and credentials stay outside package.
- [ ] grok.com custom MCP and API routes each list/call only allowed tools; denied auth/owner/protocol is explicit.
- [ ] API payload excludes unsupported approval/connector fields; missing consent cannot authorize job creation or merchant write.
- [ ] Decimal/evidence/partialness and lossless journal sequence survive actual route; no fabricated source support.

Future smoke: one clean install/update or one bounded API task per selected route,
≤6tools/120seconds/two products; paid API requires exact token/pricing$1 preflight.
Public directory/marketplace review is separate and unverified. Native Build plugin
support is source-documented; consumer arbitrary plugin ZIP and other Grok surfaces
remain unclaimed. No package, account connection, API call or publication occurred.
