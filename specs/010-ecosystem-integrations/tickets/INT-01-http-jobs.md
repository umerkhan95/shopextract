# INT-01: Shared HTTP API and durable bounded jobs

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#63](https://github.com/umerkhan95/shopextract/issues/63).

Status: planned implementation; documentation researched2026-10-24. Owner: service
maintainer. Dependencies: delivered #24/PR54; same child must pass behavior/test,
G1/G2/G3 and intended executable red tests. Covers FR02/04/13/14; SC02/03/04/12/13/14.

## Outcome and construction strategy

Expose the existing discover/extract/match/changes/evidence/job_status/job_result/
job_cancel operations over an authenticated HTTP service. Reuse guarded source
adapters, canonical identities and structured result envelopes. Existing runtime
jobs and handles are session-local; add a service-owned persistence boundary rather
than sharing a single session between tenants. HTTP capability discovery and an
owned completed-job listing are control-plane additions. No new commerce capability
is implied. Package the service as an optional self-hosted MIT extra/entry point;
keep existing CLI, constructors and stdio defaults compatible.

Declare typed request/envelope/error schemas before implementation. Proposed routes
are `/v1/capabilities`, `/v1/jobs`, `/v1/jobs/{id}` and result/cancel/evidence routes;
G1 must finalize exact methods/schemas, status codes and OpenAPI. Admission should
finish within5seconds; accepted response includes job/owner-safe identity, state and
actual expiry. Durable publication must persist catalog, evidence and dependent
references atomically. After restart references resolve correctly or explicitly
expire; a durable row pointing to vanished session handles is unacceptable.

## Identity, persistence and limits

Use scoped revocable private automation bearer credentials, operator-granted source
origins, owner-checked evidence and no credential forwarding to stores. Requests
cannot choose operator filesystem paths. Merchant reads are distinct from configured
local service-state writes. Export, snapshot creation and merchant writes are absent.

Proposed service limits:1active/8queued jobs;32terminal graphs;1000items,4MiB graph/job,
32MiB retained graph service total;120s maximum job deadline including queue(default30s).
Idempotency key records and completion journal retain24h with256records each and
1MiB combined metadata cap. Terminal graphs have maximum24h retention but may expire
or evict earlier; keys/tombstones outlive graphs within their24h window. Admission
fails when metadata capacity is exhausted. Same owner/key/body returns original job;
different body conflicts. Interrupted nonterminal jobs fail `service_interrupted`;
retry is explicit new submission. No hidden refetch.

## Acceptance and future verification

- [ ] Lost acknowledgement plus replay/restart yields one publication; cross-owner key/job/cursor never resolves.
- [ ] Restart preserves referenced products, variants and evidence or returns explicit expiry; cancellation has one terminal winner.
- [ ] Results retain decimal text, uncertainty and partial completeness; pages1..100 are immutable and owner-bound.
- [ ] Completed-job listing uses stable completion identity and per-principal monotonic commit-sequence ordering; retained-window gaps are explicit, response-loss polling resumes without inventing completion. Late equal-timestamp/lower-ID and backward-clock commits are returned after the previous checkpoint; timestamps never filter publication order.
- [ ] Real persistence/source/serialization tests exercise crash boundaries, TTL, caps and malicious source input; one smoke precedes bounded stress.

Read the existing contract at `docs/agent-tools.md` and runtime/jobs source. Remote
consumers must remain consistent with [MCP transport semantics](https://modelcontextprotocol.io/specification/2025-11-25/basic/transports), but HTTP jobs are an application contract, not protocol task support. Source/auth ownership aligns with [MCP authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization).

No server is implemented or live-tested here. Production hostname, storage/backup,
credential provisioning and exact dependency versions remain child prerequisites.
#27 owns signed outbound push/retries/dead letters and merchant-write connectors;
completion polling here does not depend on merchant-write approval or implement push.

Journal sequence/checkpoints remain decimal text or opaque tokens across JavaScript
outputs; never cast to Number. SC04/14 test9007199254740993 losslessly.
