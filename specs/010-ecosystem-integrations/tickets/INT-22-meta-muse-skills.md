# INT-22: Meta Muse Code native skills and other Muse host compatibility

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#84](https://github.com/umerkhan95/shopextract/issues/84).
Related planned work: [INT-02 / #64](https://github.com/umerkhan95/shopextract/issues/64), [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73), [INT-21 / #83](https://github.com/umerkhan95/shopextract/issues/83).

Status: researched/planned; OPTIONAL DEFERRED;2026-10-24. Owner: Meta skill maintainer. Dependencies:
INT-11 portable pack; #24 local/INT-02 remote via documented INT-21 MCP route. Native
skill directory does not wait for blocked plugin packaging. Covers FR21/16/18,
SC21/16/17/18.

[Meta's extending guide](https://dev.meta.ai/docs/muse-code/extending) affirmatively
documents native Muse Code skills: project `.agents/skills/<id>/SKILL.md`, user skills,
list/inspect/validate/install commands and interactive slash invocation. Provide one
reviewed project directory or user install route and validate selected version.
Plugin-supplied skills are a distinct optional route whose package contract must be
resolved in INT-21. [Host configuration](https://dev.meta.ai/docs/muse-code/configuration)
and exact rollout/version affect available behavior; no auto-import of personal
Claude/Codex directories or automatic policy changes in our installer.

Skill is instructions/resources around approved ShopExtract tools; it cannot authorize
network access, create credentials, register an arbitrary server or broaden origins.
Baseline has no executable scripts/hooks/subagents. Source text remains data; matching
uncertainty, partial catalogs, decimal prices and evidence survive final report.
Fresh/update must identify discovered pack/scope, preserve unrelated user skills and
explicitly diagnose disabled/missing dependencies.

Personal consumer Muse is [a different agent product](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/);
no public custom SKILL.md install route was verified for it. Meta Model API is inference,
not a skill folder loader. An app can supply trusted workflow instructions around a
separately documented API tool loop, but that wrapper must be labeled application-side
and remains gated until exact tool/auth contract is researched. Never rename a model
or saved prompt into proof of native skill installation.

- [ ] Muse Code native clean install/update/validation discovers intended pack and task-matched activation; unrelated prompt stays inactive.
- [ ] Missing tool/auth/protocol and package/path/secret problems fail explicitly before execution.
- [ ] Consumer/API rows remain unverified without target-specific loader evidence; Code compatibility does not propagate automatically.
- [ ] Plugin packaging gap does not block standalone Code skill+MCP route or get hidden as a passed plugin install.

Future owned-profile smoke one fresh install/update/three prompts, ≤6tools/two products/
120seconds. No skill, plugin, config, account or model run was created/changed here.
