# INT-14: Codex skill discovery and MCP workflow setup

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#76](https://github.com/umerkhan95/shopextract/issues/76).
Related planned work: [INT-02 / #64](https://github.com/umerkhan95/shopextract/issues/64), [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73).

Status: planned;2026-10-24. Owner: Codex skill maintainer. Dependencies: INT-11;
#24 local tool route or INT-02 remote route. Covers FR17/18, SC16/17/18.

[Official build-skills guidance](https://learn.chatgpt.com/docs/build-skills) documents
repository `.agents/skills` scanning from current directory to repository root and
user `~/.agents/skills`. Duplicate same-name skills are not merged; both may appear.
The installation guide must state scope and exact path, detect collisions, and retain
unrelated user files. Do not assume legacy `.codex/skills` paths are the sole universal
current discovery route simply because this machine has them.

Ship portable folder plus optional `agents/openai.yaml` metadata for UI/invocation and
tool dependencies. Local setup may use the existing installer or reviewed manual copy;
reusable distribution can use the plugin wrapper. Automatically discovered new skills
need verification; restart if missing, and restart after relevant config changes.
Pin pack version in release manifest and show how to confirm which instance is loaded.

MCP server registration remains separate: local command needs chosen Python environment,
operator config and allowed origins; remote setup requires endpoint/auth and compatible
protocol. Installing skill instructions grants neither credential nor permission to
fetch arbitrary stores. No generated commands replace user configuration. Baseline
instructions-only pack does not need model downloads or new scripts/dependencies.

- [ ] Disposable repo/user install is discovered, explicit invocation activates, unrelated task remains unaffected.
- [ ] Fresh/update runs identify intended version; duplicate repo/user scopes are visible and resolved deliberately, never silently merged.
- [ ] Missing MCP/capability/auth produces explicit preflight outcome and no invented catalog or unsupported export.
- [ ] Malicious source instructions remain data; optional dependency/package safety and decimal/evidence preservation follow INT-11.

Future verification uses exact Codex surface/version and one selected real tool route;
CLI, IDE, desktop and cloud are separate compatibility rows, not inferred equal.
Cloud environments need skill/credential availability separately from a local home
directory. Package/dependency tests are offline; one fresh install and update with
three prompts is the bounded host smoke. No user skill files, config, MCP registration
or plugin state is modified in this planning slice.
