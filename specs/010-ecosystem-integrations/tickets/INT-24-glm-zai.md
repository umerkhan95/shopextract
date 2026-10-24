# INT-24: GLM/Z.ai API and coding-host skill/plugin integration

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#86](https://github.com/umerkhan95/shopextract/issues/86).
Related planned work: [INT-01 / #63](https://github.com/umerkhan95/shopextract/issues/63), [INT-02 / #64](https://github.com/umerkhan95/shopextract/issues/64), [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73), [INT-12 / #74](https://github.com/umerkhan95/shopextract/issues/74).

Status: researched/planned;2026-10-24. Owner: GLM integration maintainer.
Dependencies: INT-01/02 for remote API tool route; INT-11 and existing INT-12/20 for
Claude Code host skills/plugins. Covers FR23, SC23/16/17/18 and shared authorization.

Treat three surfaces independently. [Coding Plan overview](https://docs.z.ai/devpack/overview)
provides model entitlement across hosts including ZCode and third-party agents.
That entitlement is not a ShopExtract tool credential or native skill/plugin loader.
Exact account/model/endpoint/plan limits must be rechecked before implementation.

[Z.ai Claude Code setup](https://docs.z.ai/devpack/tool/claude) configures an external
Claude Code host to use GLM. Reuse our Claude Code plugin/skill only if that actual
host/version loader and MCP route work with selected provider. Instructions must isolate
provider settings and preserve user's existing account config; do not run vendor helper
scripts or overwrite settings automatically. MCP credentials remain separate from model
key. Host namespace, lifecycle and native permission contracts belong to Claude Code,
not a fictitious GLM SKILL.md API.

[Provider MCP calling](https://docs.z.ai/guides/capabilities/mcp-call) documents nested
MCP configuration in chat/completions with third-party endpoint, headers and allowlist.
Build a small route-specific adapter around INT-02, not copied OpenAI Responses payload.
Keep service tokens in headers/server state, never query URLs or model-readable source
text. Exact protocol/auth/approval behavior is a child blocker before remote live calls;
service scopes cannot depend on model compliance.

No exact ZCode-native custom skill/plugin manifest was established in this bounded
source set. Record that native packaging route unverified; do not label the provider
entirely unsupported or imply external-host skills prove ZCode installation. Public
catalog acceptance is a separate unresolved contract.

- [ ] External Claude Code+GLM row discovers actual plugin/skill and approved tools; provider/model setup alone cannot pass installation.
- [ ] API route validates its native request schema/allowlist/auth and rejects cross-owner/unsupported operation without source fetch.
- [ ] Revoked service token and model-key-only cases produce explicit prerequisite, no credential forwarding or widened origin grants.
- [ ] Exact decimal/evidence/partialness/sequence survive; native ZCode consumer/package support stays unverified pending loader evidence.

Future smoke one supported route, ≤6tools/two products/120seconds; paid requests need
exact entitlement/token/pricing$1 preflight. No model inference, config installation,
provider key setup, plugin build or publication performed in this documentation task.
