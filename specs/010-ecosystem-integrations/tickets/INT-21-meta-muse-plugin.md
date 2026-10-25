# INT-21: Meta Muse Code plugin/tool integration and consumer/API mapping

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#83](https://github.com/umerkhan95/shopextract/issues/83).
Related planned work: [INT-02 / #64](https://github.com/umerkhan95/shopextract/issues/64), [INT-11 / #73](https://github.com/umerkhan95/shopextract/issues/73), [INT-22 / #84](https://github.com/umerkhan95/shopextract/issues/84).

Status: researched/planned; OPTIONAL DEFERRED;2026-10-24. Owner: Meta integration maintainer.
Dependencies: INT-21a direct MCP route reuses#24local or INT-02remote; INT-21b
optional plugin packaging consumes21a plus INT-11/22skills. INT-22standalone skill
does not wait for blocked21bpackaging.
Covers FR21, SC21/03/04/13. Muse identity is Meta; exact host support is separated.

[Meta developer overview](https://dev.meta.ai/docs/overview) distinguishes Model API
inference from Muse Code agent. [Personal Muse announcement](https://about.fb.com/news/2026/09/introducing-muse-personal-ai-agent/)
describes a separate consumer personal-agent product, not a plugin manifest reference.
Do not infer consumer install or API tool schema from Muse Code capabilities.

[Muse Code extending guide](https://dev.meta.ai/docs/muse-code/extending) documents
stdio/streamable_http MCP configuration and skills supplied by enabled plugin bundles.
Implement and test direct MCP route first using existing local command/config or shared
remote endpoint. This route does not itself prove a native plugin installation.

A plugin-wrapper deliverable requires exact current Muse Code bundle manifest,
validation/install/update/enable/discovery contract and permission behavior. Those
mechanism details were not established in this bounded page set; a guessed dedicated
plugin URL was inaccessible. Record package construction as BLOCKED on official
schema/CLI evidence before runtime packaging. Do not assume Claude plugin compatibility
or invent `.muse-plugin/plugin.json`. [Configuration guide](https://dev.meta.ai/docs/muse-code/configuration)
helps locate host settings but does not resolve plugin packaging. INT-22 native skills
can proceed independently through their documented directory/CLI path.

- [ ] Direct Muse Code MCP lists/calls only approved owned tools; credential/source policies/data fidelity hold.
- [ ] Native plugin packaging remains blocked until official manifest/install contract is captured and reviewed; then clean-profile load/update passes real parser.
- [ ] Personal Muse custom-plugin support and Meta Model API tool schemas remain separate unverified rows, not silently enabled from coding-agent docs.
- [ ] Missing host/token/protocol produces explicit prerequisite; no source instructions broaden scopes or install hooks.

Future smoke direct MCP or validated plugin uses two products/≤6tools/120seconds,
one install/update if supported. Public registry/submission has no verified contract
here; do not promise acceptance. No Meta account, model call, plugin install or public
publication occurred. Exact product versions/entitlements and missing packaging facts
are future blockers, not a reason to discard documented Code skill/MCP support.
