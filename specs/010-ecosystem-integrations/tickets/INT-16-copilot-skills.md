# INT-16: GitHub Copilot Agent skill setup (deferred implementation wave)

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#78](https://github.com/umerkhan95/shopextract/issues/78).
Related planned work: [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73).

Status: researched/planned;2026-10-24. Owner: Copilot skill maintainer. Dependencies:
INT-11 and supported independently tested tool route. Covers FR17/18, SC16/17/18.

[Official Copilot skills guidance](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
provides repository `.github/skills`, `.claude/skills` or `.agents/skills` locations;
personal local scopes include `~/.copilot/skills` and `~/.agents/skills`. Skill is a
folder with case-sensitive `SKILL.md` and required YAML name/description. Choose one
repository path in baseline installation instructions rather than duplicating packs
into every recognized directory.

Ship the same trusted skill workflow with Copilot host guidance, explicit tool/version
requirements and optional references. Project instructions or a prompt file are not
silently substituted for skill installation. Cloud agent, CLI, app and VS Code agent
mode have separate tool/account environments: test each claimed target. Code-review
skill support does not prove a commerce extraction tool is available in that runtime;
mark review-only/unavailable cases explicitly.

MCP/HTTP execution and credentials remain independently configured; skill files do not
provision secrets or grant outbound network access. Cloud runtime may not read a user's
local home skill/tool config. Baseline repository skill relies on an approved reachable
service and bounded workflow preflight. No merchant writes, auto-install scripts or
unreviewed CLI downloads. Updates preserve unrelated skills and verify discovered version;
record required session restart from actual client behavior, not an invented command.

- [ ] Selected repository and personal-local routes discover/activate skill on intended supported surfaces; unrelated prompts remain inactive.
- [ ] Update and duplicate-scope fixtures identify active version; cloud row remains blocked without available tools/auth/network.
- [ ] Missing or wrong-schema tool fails preflight; source-injected instructions never grant tools, credentials or code changes.
- [ ] Shared archive/secret/dependency validator and real tool-output fidelity cases pass before host live proof.

Live ceiling one disposable install/update with three prompts and two-product fixture;
record exact client/extension version, account and route. Public skill distribution
is a versioned repo/package, separate from platform acceptance or organization rollout.
No repository skill installation, Copilot account/config change or workflow execution
occurs in this planning task. Deferred wave retains a concrete researched path without
claiming compatibility before observation.
