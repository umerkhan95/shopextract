# INT-15: Cursor Agent skill installation (deferred implementation wave)

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#77](https://github.com/umerkhan95/shopextract/issues/77).
Related planned work: [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73).

Status: researched/planned;2026-10-24. Owner: Cursor skill maintainer. Dependencies:
INT-11 and an independently tested local/remote tool route. Covers FR17/18,
SC16/17/18. Deferred means no implementation promised by the connector first release.

[Cursor Agent Skills](https://cursor.com/docs/skills) describes automatic startup
discovery and explicit `/` invocation. Project `.agents/skills`/`.cursor/skills` and
user `~/.agents/skills`/`~/.cursor/skills` are supported locations. Local user skills
are not automatically universal cloud/SSH/worker installs; document project repository
pack as the baseline portable route and test any sync/distribution route separately.

Create a host guide/wrapper around the same trusted `SKILL.md`, keeping skill root
references relative. No duplicated commerce logic or secret-bearing MCP config in
skill files. Configure supported MCP/tool route separately and record tested Cursor
client/runtime version. The loader being compatible with other vendors' skill folders
is not proof every optional metadata field/executable helper behaves identically.

Update instructions validate package version, prevent overwriting unrelated skills,
identify duplicate scopes and restart/reload according to tested client behavior.
Do not invent an undocumented reload command. Baseline contains no scripts or automatic
installation hooks. Tool preflight blocks missing auth/capability and keeps deferred
export/analytics/maintenance unavailable. Source text remains untrusted data regardless
of whether Agent reads it as a product or webpage.

- [ ] Project and user install are discovered in disposable local profile; explicit and task-matched activation work, unrelated prompt remains inactive.
- [ ] Fresh/update verifies one intended pack/version and diagnoses scope collisions/stale discovery.
- [ ] Real approved tool route returns exact decimal/support/partialness; absent route fails explicitly without hidden fallback.
- [ ] Traversal/secret/script-dependency fixtures reject before execution under shared pack checks.

Bounded future live proof: one fresh install/update, three prompts, two-product tool
fixture and service request limits. Missing entitlement/network/agent features remain
blocked. Separate desktop/CLI/cloud rows and public plugin distribution if pursued;
no universal compatibility claim from local files alone. No Cursor installation,
settings change, cloud sync or plugin publication occurs in this planning task.
