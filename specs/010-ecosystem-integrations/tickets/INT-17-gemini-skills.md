# INT-17: Gemini CLI Agent skills (deferred implementation wave)

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#79](https://github.com/umerkhan95/shopextract/issues/79).
Related planned work: [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73).

Status: researched/planned;2026-10-24. Owner: Gemini skill maintainer. Dependencies:
INT-11 and approved reachable MCP/tool route. Covers FR17/18, SC16/17/18.

[Management guidance](https://geminicli.com/docs/cli/using-agent-skills/) describes
user `~/.gemini/skills`/`~/.agents/skills` and workspace `.gemini/skills`/`.agents/skills`,
with workspace overriding user. Extensions are another distinct scope. Document a
single selected install location and explicit collision checks; do not assume all
hosts share this precedence rule.

[Getting-started guidance](https://geminicli.com/docs/cli/tutorials/skills-getting-started/)
provides `gemini skills install <url-or-path>`, link/uninstall, `/skills list` and
`/skills reload`. Workspace trust and exact `SKILL.md` frontmatter/path layout affect
discovery; baseline pack uses one named subdirectory. Install from a reviewed pinned
artifact/path, never untrusted URL supplied by scraped content. Document enable/disable
and version check separately from discovery and task activation/consent.

Package is trusted workflow instructions/resources with no automatic script execution.
MCP registration, remote OAuth and Python environment are separate prerequisites; CLI
skill activation cannot grant merchant/network permissions. Host-supported tool names,
protocol/schema and evidence retention must pass preflight. Script helpers, if later
added, require declared dependencies and permission-aware tests; the instructions-only
baseline needs no downloads/model runs.

- [ ] Disposable user/workspace install is listed; intended prompt activates, unrelated prompt remains inactive, host consent behavior is recorded.
- [ ] Fresh/update reload shows expected version; same-name workspace/user precedence is observed, untrusted workspace remains denied rather than silently enabled.
- [ ] Missing tool/auth/capability returns explicit unsupported state and cannot enable export/analytics/maintenance or leak secrets.
- [ ] Archive traversal/symlink/secret/dependency cases fail shared checks; real tool output retains decimal/evidence/uncertain state.

Future smoke is one fresh install/update and three prompts against bounded two-product
fixture; exact CLI/account/tool versions are prerequisites. Gemini web app and Gemini
API are outside this CLI skill ticket. Extension marketplace packaging, if pursued,
requires separate tested distribution work. No skill installation, trust change, CLI
execution or publication occurs in this documentation task.
