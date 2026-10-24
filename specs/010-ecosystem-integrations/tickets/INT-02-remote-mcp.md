# INT-02: Remote MCP transport, OAuth and principal isolation

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#64](https://github.com/umerkhan95/shopextract/issues/64).
Related planned work: [INT-01 / #63](https://github.com/umerkhan95/shopextract/issues/63).

Status: planned; researched2026-10-24. Owner: security/MCP maintainer. Dependencies:
INT-01 durable service; delivered #24/PR54 local tool contracts. Covers FR03/04/13/14,
SC03/04/06/13/14. No production deployment or OAuth client registration in this task.

## Outcome and construction strategy

Provide an optional self-hosted HTTPS `/mcp` endpoint around approved ShopExtract
operations, delegating execution to the same service-owned job/evidence boundary
used by HTTP connectors. Keep local stdio independent and unchanged. Do not duplicate
extraction algorithms or use one global runtime session as authentication state.
MCP protocol version and ShopExtract `schema_version:1.0` are different contracts.

Use the supported SDK transport where possible, with explicit compatibility tests.
Candidate initial remote protocol is2025-11-25; this is conditional on actual SDK and
host negotiation. Current repo pins Python MCPv1 maintenance line. The current
[2026-07-28 transport overview](https://modelcontextprotocol.io/specification/2026-07-28/basic/transports) uses per-request protocol metadata and cancellation semantics distinct from
[2025-11-25 transports](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports).
Do not advertise latest-protocol compatibility without testing or silently upgrade
the SDK; unsupported clients require a reviewed migration slice before that row passes.

## Authentication, state and metadata

Implement OAuth resource-server discovery/challenges, validate issuer/audience,
expiry/revocation and least-privilege scopes per request. Use an established auth
provider rather than writing a new identity system. [MCP authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization)
separates resource-server validation from token issuance. Registration support is
host-specific (static preregistration, CIMD or DCR as supported); publish the exact
supported modes. Source origins and captures remain operator grants. User token,
source content or protocol session ID never grants another owner's job or evidence.

Proposed scopes distinguish catalog/evidence reads, job submit/read/cancel and
capture reads. Durable submission/cancellation/local bookkeeping are effects even
though merchant access stays read-only; tool annotations must describe actual effects.
Do not use blanket read-only flags to bypass host consent. Preserve structured
content/envelopes/error status; tool registration must reflect available capabilities.
Missing export/analytics/category/maintenance methods remain unavailable.

## Acceptance and future verification

- [ ] Tools/list and tools/call negotiate declared protocol and expose only granted operations; unsupported protocol returns explicit failure.
- [ ] Invalid/expired/revoked/wrong-audience token and cross-owner handle/cursor fail without leaking object existence, secrets or paths.
- [ ] Disconnect/reconnect to remote service preserves authorized durable references; local stdio still releases its session state.
- [ ] Public-origin, redirect/DNS, tool-injection and schema guards run through real production seams; source text cannot broaden scopes.
- [ ] Cancellation of transport request is distinguished from explicit durable-job cancellation; orphaned admission/replay produces no duplicate publication.

Test actual SDK/HTTP/auth middleware with a controlled endpoint, two principals and
fault-injected response loss before bounded host live checks. Respect INT-01 limits,
per-host smaller budgets and Retry-After. No SSE reconnect guarantee implies job
durability. Account eligibility, HTTPS reachability, provider configuration and
protocol-version support remain release blockers until observed. Public directory
publication belongs to each host ticket; #27 owns signed outbound event delivery.
