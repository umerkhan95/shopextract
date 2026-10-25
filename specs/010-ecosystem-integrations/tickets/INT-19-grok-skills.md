# INT-19: Grok Build native skill pack and other Grok skill compatibility

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#81](https://github.com/umerkhan95/shopextract/issues/81).
Related planned work: [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73), [INT-18 / #80](https://github.com/umerkhan95/shopextract/issues/80).

Status: researched/planned;2026-10-24. Owner: Grok skill maintainer. Dependencies:
INT-11 portable pack; INT-18a selected tool route or#24local. Native plugin
distribution18b consumes this pack later, not a prerequisite. Covers FR19/16/18, SC19/16/17/18.

[Official Build skill documentation](https://docs.x.ai/build/features/skills-plugins-marketplaces)
confirms native SKILL.md discovery in project/user `.grok/skills`, enabled plugin
skills and configured paths, with slash invocation. This is affirmative native support
for Grok Build, separate from Grok model/API or grok.com consumer UI. Deliver one selected
scope guide plus minimal host wrapper; do not copy the same skill into multiple roots.

Use [inspect/plugin lifecycle commands](https://docs.x.ai/build/cli/reference) to
verify actual discovered configuration/version before and after update. `allowed-tools`
in skill metadata does not grant or restrict tool authority; service scopes and host
permissions remain authoritative. Baseline instructions-only recipe references existing
approved tools and preserves incomplete/uncertain data. Credentials and executables are
not packaged merely because native skills may contain scripts.

For xAI API, an application can use the trusted workflow as application-owned instructions
around documented tools, but that is not a native API SKILL.md upload/install. No native
grok.com private skill loader or consumer directory contract was established by these
bounded sources; keep those rows unverified rather than deny the documented Build route
or invent consumer installation. Public Build marketplace distribution is separate from
successful local discovery.

- [ ] Build fresh install/update has intended selected version; implicit/explicit activation matches commerce task and unrelated prompt remains inactive.
- [ ] Missing MCP/auth/capability fails preflight; product instructions cannot enable tools or export/maintenance extensions.
- [ ] Invalid paths, secrets and undeclared scripts reject package checks; no arbitrary hooks executed.
- [ ] API instruction wrapper and consumer-unverified rows are labeled honestly and cannot claim native loader proof from API calls.

Future verification follows SC16..19 and one owned install/update with three prompts;
actual Build/version/account and tool transport are prerequisites. No skill/plugin
installation, CLI execution, API model request or marketplace publication occurs in
this planning task. Reuse INT-11, do not build a second commerce recipe engine.
