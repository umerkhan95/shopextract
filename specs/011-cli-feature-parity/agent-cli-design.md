# Agent-facing CLI design research

2026-10-25. Bounded primary-source review after P0 design; implementation now
authorized. No models or paid API calls. Existing P0 contracts remain binding.

- GitHub CLI formatting: https://cli.github.com/manual/gh_help_formatting
  Explicit structured output supports automated consumers. Adopt complete JSON
  envelopes and exact fields; no scraping human tables or hidden preview limits.
- GitHub CLI agent skill: https://github.com/cli/cli/blob/trunk/skills/gh/SKILL.md
  Noninteractive commands should fail promptly rather than prompt; list limits
  and pagination must be explicit. Adopt finite watch/tools sessions, no prompts,
  predictable exit codes and documentation showing bounded examples.
- Click parameters: https://click.palletsprojects.com/en/stable/options/
  Click defaults prioritize environment over default_map. ShopExtract explicitly
  requires flags > trusted file > environment > defaults, so its loader must
  resolve that policy directly; do not rely on Click default_map precedence.
- MCP tools: https://modelcontextprotocol.io/specification/2025-11-25/server/tools
  Named tools expose input/output schemas and distinct errors. Apply the same
  discoverability to CLI command metadata and schemas; preserve native ToolRuntime
  payloads/session ownership and protocol-only stdout on tools serve. This does
  not turn ordinary CLI operations into MCP calls or broaden tool trust.

Design additions for P5 G1: root capabilities/schema discovery with exact installed
command/parameter descriptions and packaged config/response/input schemas. Agents
should inspect these once, use explicit --output-format json before command,
consume data/completeness/error, and retry only when retryable permits. Export
artifact stdout is a distinct explicit mode; mutating retention/migration uses
--apply. No new generic shell execution or callbacks accepted.

Research guides concrete design; links are not evidence that runtime acceptance
has passed. Phase-specific schemas, limits and failure semantics require their
recorded gates. Actual session token counters unavailable.
