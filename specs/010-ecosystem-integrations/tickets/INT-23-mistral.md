# INT-23: Mistral Vibe skill/plugin and tool integration

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#85](https://github.com/umerkhan95/shopextract/issues/85).
Related planned work: [INT-02 / #64](https://github.com/umerkhan95/shopextract/issues/64), [INT-10 / #72](https://github.com/umerkhan95/shopextract/issues/72), [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73).

Status: researched/planned;2026-10-24. Owner: Mistral integration maintainer.
Dependencies: INT-11 portable workflow; #24 local or INT-02 remote approved tool
route; INT-10b only for final release. Covers FR22, SC22/16/17/18 plus shared auth/data.

[Mistral overview](https://docs.mistral.ai/vibe) distinguishes Vibe Work and Code,
with legacy Chat naming. Target native Code first; a model API or legacy consumer
identity is not a loader. Product rollout/version and exact plan remain prerequisites.

[Code skills](https://docs.mistral.ai/vibe/code/cli/skills) documents SKILL.md with
project/user Vibe/Agent skill roots and trust. Reuse INT-11 instructions, one selected
scope, explicit tool/auth preflight and supported-data reporting. Allowed-tools metadata
is not permission enforcement. No scripts/downloads/hooks in baseline pack.

[Code plugins](https://docs.mistral.ai/vibe/code/cli/plugins) is experimental and uses
Agent Plugins1.0 with root plugin.json, skills and mcp.json; Vibe-specific extensions
are unnecessary for our minimal bundle. Package skills plus approved local/remote MCP,
keep credentials outside artifacts, validate containment/version and native parser.
Actual server names must avoid user-config collision. Session pins plugin contents;
`/reload-plugins` or new session, not ordinary `/reload`, applies updates. These are
Code lifecycle semantics, not a promise that Work accepts the same directory.

Work-native skill/plugin creation and provider API orchestration need their own exact
interface checks before claiming support; selected source set establishes Code route
and surface distinction, not universal consumer plugin submission. Avoid automatic
migration or changing account settings. Distribution can start with reviewed local
folder; public catalog/organization rollout are separately pending.

- [ ] Clean Code skill and plugin installs discover intended namespaced workflow/tools; fresh/update/reload pinned version behavior is observed.
- [ ] Missing MCP/admin denial/credential/scope fails explicitly; plugin cannot override unrelated user connections or enable merchant writes.
- [ ] Invalid manifest/path/secret/undeclared script rejects, with no hidden external execution.
- [ ] Evidence/decimal/partialness and lossless sequence survive real tool path; Work/API rows remain separate pending compatibility.

Future owned-profile smoke one install/update/three prompts, ≤6tools/two products/
120seconds; any paid task requires exact model/token/pricing$1 preflight. Experimental
format changes trigger source/schema refresh and affected review. No Vibe installation,
plugin/skill build, account configuration, model call or publication in this task.
