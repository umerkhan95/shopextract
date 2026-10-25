# INT-05: ChatGPT MCP app/private plugin compatibility

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#67](https://github.com/umerkhan95/shopextract/issues/67).
Related planned work: [INT-01 / #63](https://github.com/umerkhan95/shopextract/issues/63), [INT-02 / #64](https://github.com/umerkhan95/shopextract/issues/64), [INT-13 / #75](https://github.com/umerkhan95/shopextract/issues/75).

Status: planned; researched2026-10-24. Owner: ChatGPT integration maintainer.
Dependencies: INT-02 transport/auth and INT-01 durable state. Covers FR07/03/04/15,
SC07/03/04/15. Current official docs use Plugins terminology; this ticket preserves
user-facing “ChatGPT connector” as a goal, not a claim of existing directory presence.

## Construction and authentication

Expose the shared HTTPS MCP server with narrow tools, versioned schemas, readable
descriptions and structured results following [server guidance](https://developers.openai.com/plugins/build/mcp-server).
Baseline has no UI component. Do not create separate commerce logic for ChatGPT.
Declared tool annotations must reflect service-state effects: extraction submission
creates durable state; cancellation changes job state; changes may write replay
bookkeeping. Merchant-read-only does not justify blanket `readOnlyHint:true`.
Public source access requires truthful open-world behavior. Tests compare annotations
to actual implementation effects before packaging.

Use end-user OAuth according to [authentication guidance](https://developers.openai.com/plugins/build/auth),
including protected-resource discovery, issuer/audience validation and host-compatible
client registration. Do not design a ChatGPT API-key text field or assume machine-to-
machine grants are supported. Secret material is connection/server state, not tool
arguments or returned content. Scope each call/result/cursor/evidence lookup to the
validated principal, not an assistant-provided account identifier.

## Private installation and public distribution

Follow [connect/test instructions](https://developers.openai.com/plugins/deploy/connect-chatgpt):
eligible account/workspace adds the custom remote MCP server, installs resulting
plugin, then exercises tools in a fresh conversation. Keep exact current UI labels
in versioned instructions, with account restrictions explicit. A real private smoke
is required; an SDK replay alone is mechanism evidence. Unsupported protocol/client
negotiation is blocked until a reviewed upgrade, not waived.

[Public submission](https://developers.openai.com/plugins/deploy/submission)
requires a packaged artifact, review materials and platform review. Prepare listing,
privacy/support/terms, reviewer-safe sample account and demonstration/test cases when
runtime exists; no secrets in public ZIP. Mark private-installed, submitted, approved
and published as separate statuses. This planning ticket does not authorize publication.
Bundled skills belong to INT-13 and can reuse the same remote server.

## Acceptance and future verification

- [ ] Private installation discovers only granted tools with correct schemas/annotations; direct, paraphrased and follow-up prompts select intended bounded operations.
- [ ] Extraction returns durable job identity; follow-up status/result/evidence preserves owner and actual support. Unfinished jobs are never summarized as complete catalogs.
- [ ] Revoked credentials, denied workspace policy, unsupported operation/version and cross-owner evidence fail explicitly without secret/path disclosure.
- [ ] Model-facing decimal/variant/partial/uncertain data remains exact in structured output; source injection cannot change instructions or request new scopes.
- [ ] Documentation records tested service/SDK/host versions, account prerequisites and private versus public state; public acceptance remains externally pending.

Use real MCP/auth mechanisms with controlled external boundaries; one private live
conversation ≤12tool calls/two products/120seconds after offline success. No universal
account availability, rate/payload limit or listing outcome is promised; recheck exact
plan/client limits before implementation. No app/plugin was built or connected here.
