# INT-13: ChatGPT skill packaging through supported plugin routes

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#75](https://github.com/umerkhan95/shopextract/issues/75).
Related planned work: [INT-05 / #67](https://github.com/umerkhan95/shopextract/issues/67), [INT-10 / #72](https://github.com/umerkhan95/shopextract/issues/72), [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73).

Status: planned;2026-10-24. Owner: ChatGPT skill maintainer. Dependencies: INT-11,
INT-05 remote tools, INT-10 recipe claims. Covers FR17/18, SC16/17/18.

Current official [Skills & Plugins](https://learn.chatgpt.com/docs/skills-and-plugins)
and [skill concepts](https://developers.openai.com/plugins/concepts/skills) document
skills for ChatGPT/Codex and plugins as installable bundles. This research supports a
real skill/plugin route; it does not equate Custom GPT Knowledge files or GPT Actions
with `SKILL.md`, or promise raw local folders load on every ChatGPT surface.

Package the reviewed portable skill with [plugin packaging guidance](https://developers.openai.com/plugins/build/plugins),
including current manifest structure, skill directory references and optional shared
MCP connection. Exact allowed package fields/layout must be validated against the
host parser at child skeleton stage rather than frozen from an older Apps SDK example.
Use only remote-tool workflow instructions in browser-compatible baseline; local
scripts require a declared executor/compatible surface, not assumed browser execution.

Private install/test is first. Account/workspace plugin and skill policy must allow
the route; otherwise record blocked host row, not replace with Knowledge and call it
a skill. MCP OAuth remains independently configured per user; skill files contain
no access tokens and cannot widen scopes. Tool dependencies are declared but verified
at activation. Exports/analytics/maintenance recipes remain disabled until extensions.

- [ ] Package validates, installs privately in eligible ChatGPT surface and exposes intended skill; selected version is visible after update.
- [ ] Explicit invocation and relevant natural-language prompt select workflow; unrelated prompt and denied capability do not trigger unauthorized calls.
- [ ] Skill+MCP preflight handles unauthenticated/revoked/unsupported tools honestly; evidence and uncertainty remain preserved.
- [ ] Traversal/secret/unsupported-script pack fails before execution; no claims of universal raw `SKILL.md` upload support.

Public [submission](https://developers.openai.com/plugins/deploy/submission) requires
its own reviewed package/listing/materials and external decision; private compatibility
is distinct. Reuse INT-05 endpoint, avoid a second competing auth/commerce engine.
No plugin or skill was built, installed, submitted or published in this planning task.
