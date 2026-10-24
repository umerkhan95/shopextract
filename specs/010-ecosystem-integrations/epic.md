# EPIC: ShopExtract ecosystem connectors and agent skills

Status: planning documentation; runtime work not started. Date:2026-10-24.

ShopExtract users should run bounded evidence-aware commerce workflows from their
existing automation and AI tools, with dedicated setup and trusted workflow skills.
Keep one MIT/self-hosted commerce engine; adapters handle platform-specific auth,
input/output, durable-job continuation, installation and distribution.

## Scope and requirements

Baseline seven connector targets: n8n, Claude, ChatGPT, OpenAI Responses API, Zapier, Make,
Pipedream. Baseline six skill hosts: Claude, ChatGPT, Codex, Cursor, GitHub Copilot, Gemini CLI. Add Grok Build, Mistral Vibe, GLM-host and Hermes Agent mapping,
Anthropic Code plugin distribution, and optional/deferred Meta Muse routes.
Shared portable pack supplies instructions/resources; skills do not replace API/MCP
authentication or enable unsupported operations. Current ChatGPT plugin skills are
researched separately from Codex local directories and Custom GPT Knowledge/Actions.

First release transports existing8tools only; adds capability discovery/owned durable
job completion listing. Exports, general analytics, category/maintenance and fresh
capture scheduling need explicit future capability extensions. Polling means completed
jobs, not a claim that commercial price transitions were observed. Merchant operations
remain read-only; local durable state, bookkeeping and future exports have explicit
scopes/effects. Data preserves IDs, decimal text, uncertainty and captured support.

Reuse delivered #24/PR54; link #26 and #27. #27 owns merchant-write/PIM/store adapters
and signed outbound event delivery/retries/dead letters. No duplicated merchant-write
scope or requirement to wait for merchant-write approval before read-only polling.

## Child tickets

- [ ] [#63](https://github.com/umerkhan95/shopextract/issues/63) INT-01 Shared HTTP API and durable bounded jobs
- [ ] [#64](https://github.com/umerkhan95/shopextract/issues/64) INT-02 Remote MCP/OAuth and isolation
- [ ] [#65](https://github.com/umerkhan95/shopextract/issues/65) INT-03 n8n dedicated native node
- [ ] [#66](https://github.com/umerkhan95/shopextract/issues/66) INT-04 Claude local/remote compatibility
- [ ] [#67](https://github.com/umerkhan95/shopextract/issues/67) INT-05 ChatGPT MCP/private app
- [ ] [#68](https://github.com/umerkhan95/shopextract/issues/68) INT-06 OpenAI Responses API
- [ ] [#69](https://github.com/umerkhan95/shopextract/issues/69) INT-07 Zapier actions/poll trigger
- [ ] [#70](https://github.com/umerkhan95/shopextract/issues/70) INT-08 Make custom app
- [ ] [#71](https://github.com/umerkhan95/shopextract/issues/71) INT-09 Pipedream actions/source
- [ ] [#72](https://github.com/umerkhan95/shopextract/issues/72) INT-10 Recipes/compatibility/release
- [ ] [#73](https://github.com/umerkhan95/shopextract/issues/73) INT-11 Portable workflow skill pack
- [ ] [#74](https://github.com/umerkhan95/shopextract/issues/74) INT-12 Claude skill routes
- [ ] [#75](https://github.com/umerkhan95/shopextract/issues/75) INT-13 ChatGPT plugin skills
- [ ] [#76](https://github.com/umerkhan95/shopextract/issues/76) INT-14 Codex skill discovery
- [ ] [#77](https://github.com/umerkhan95/shopextract/issues/77) INT-15 Cursor Agent skills (deferred wave)
- [ ] [#78](https://github.com/umerkhan95/shopextract/issues/78) INT-16 Copilot Agent skills (deferred wave)
- [ ] [#79](https://github.com/umerkhan95/shopextract/issues/79) INT-17 Gemini CLI skills (deferred wave)

- [ ] [#80](https://github.com/umerkhan95/shopextract/issues/80) INT-18 Grok Build plugin and xAI/grok.com MCP routes
- [ ] [#81](https://github.com/umerkhan95/shopextract/issues/81) INT-19 Grok Build skills and other host compatibility
- [ ] [#82](https://github.com/umerkhan95/shopextract/issues/82) INT-20 Anthropic Claude Code plugin distribution
- [ ] [#83](https://github.com/umerkhan95/shopextract/issues/83) INT-21 Meta Muse plugin/tool mapping (optional/deferred)
- [ ] [#84](https://github.com/umerkhan95/shopextract/issues/84) INT-22 Meta Muse Code skills (optional/deferred)
- [ ] [#85](https://github.com/umerkhan95/shopextract/issues/85) INT-23 Mistral Vibe skill/plugin routes
- [ ] [#86](https://github.com/umerkhan95/shopextract/issues/86) INT-24 GLM/Z.ai API/coding-host routes
- [ ] [#87](https://github.com/umerkhan95/shopextract/issues/87) INT-25 NousResearch Hermes Agent skill/plugin routes

Parent EPIC: [#62](https://github.com/umerkhan95/shopextract/issues/62). All 25 child issues are created; unchecked means implementation pending.
All artifacts live at `specs/010-ecosystem-integrations/` in the repository.

## Phased strategy outline

1. Review behavior/tests/tasks/research at G1; then document interfaces/G2 and reuse/G3.
2. Future implementation children first prove red tests, then shared HTTP/durable/auth
   foundations. Local stdio compatibility can proceed from existing #24 independently.
3. n8n deterministic node and Claude/ChatGPT compatibility, OpenAI API examples; portable
   skill pack with corresponding Claude/ChatGPT/Codex host wrappers.
4. Zapier/Make/Pipedream adapters and recipes; later Cursor/Copilot/Gemini skill wave.
5. Per-row real-path mechanism/stress then private live proof; separate public package
   submission/acceptance states. No blanket “all platforms supported” from documentation.

## Acceptance and evidence

FR01..24/SC01..24 in spec.md/test-design.md govern scope. Each child has dependency,
construction/source findings, auth/job/error/data contracts, concrete acceptance and
future live prerequisites. sources.json records60 fetched primary pages with date and
read scope; research.md distinguishes fetched facts from design decisions. No runtime,
platform account, public marketplace or commercial-change observation is claimed.

Docs-only handoff requires independent G1/G2/G3/final, source/link/coverage checks and
actual issue mapping. Expanded-scope G1/G2, G3 and final content review passed
independently; see reviews.md. Future
implementation requires its own red/green/synthetic/stress/live evidence. Public
publication is not authorized merely by completing these planning documents.

User steering preserves all25tickets and prioritizes one Claude Code LOCAL plugin+skill
slice next session, using delivered#24 without remote foundations. See handoff.md;
NOT STARTED here. Meta optional/deferred retains verified Code native support; personal
Muse custom installation and exact Code plugin manifest remain unresolved.
