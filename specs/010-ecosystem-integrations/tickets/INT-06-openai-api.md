# INT-06: OpenAI Responses API integration routes

Parent: [#62](https://github.com/umerkhan95/shopextract/issues/62). Ticket: [#68](https://github.com/umerkhan95/shopextract/issues/68).
Related planned work: [INT-01 / #63](https://github.com/umerkhan95/shopextract/issues/63), [INT-02 / #64](https://github.com/umerkhan95/shopextract/issues/64).

Status: planned; researched2026-10-24. Owner: SDK/example maintainer. Dependencies:
INT-02 remote MCP route; INT-01 function route, or existing #24 for an explicitly
session-local example. Covers FR08/04/14, SC08/04/14. This is a developer API example,
separate from ChatGPT installation or public directory distribution.

## Route A: remote MCP

Following [Responses MCP guidance](https://developers.openai.com/api/docs/guides/tools-connectors-mcp),
configure an `mcp` tool with chosen server label/URL, allowed tool list, authorization
and explicit approval policy. API invokes remote tools; application handles approval
request/response flow where required. Credentials stay server-side and are refreshed
by application-owned auth handling. Do not invent a built-in `connector_id` for
ShopExtract; it is a custom endpoint. Secure MCP Tunnel is an optional documented
connection alternative, not required baseline infrastructure or a substitute for
testing deployment reachability.

Application limits model/API calls and commerce jobs independently. Tool access is
least-privilege; no implicit permission to submit further jobs once the user-requested
bounded task completes. Require honest state-changing annotations and approvals;
never treat merchant-read-only as “no service effects.” Surface job identity and
unfinished status if the operation needs later continuation.

## Route B: application-owned function tools

Use [function-calling guidance](https://developers.openai.com/api/docs/guides/function-calling)
to declare schemas and dispatch validated allowlisted calls through the shared HTTP
client. The application executes the call and returns `function_call_output` with
matching `call_id`, then requests continuation with required conversation items.
Do not return function outputs for remote `mcp_call` execution or confuse approval
request IDs with function call IDs. Avoid parallel execution in the bounded reference
example; one call at a time makes ownership/cancel and counters inspectable.

## Packaging, limits and behavior

Deliver two small examples plus shared typed envelope handling, environment/setup
documentation and fixtures. No model hardcode marketed as universal support: select
and record a documented tool-capable model available to the user's API account.
Pin tested SDK/schema versions and keep optional dependencies outside core.

Preserve exact structured data alongside natural-language summary; price decimal
strings, currency, canonical/variant IDs, support and uncertainty are not converted
into model-invented facts. No new export/analytics/maintenance tools are exposed.
429/backoff, unauthorized, timeout, malformed args and unknown tools have explicit
branches. All retries reuse original idempotency key rather than create another job.

## Acceptance and future verification

- [ ] Controlled API boundary drives real example dispatch through submit/status/result/evidence; function outputs correlate exact call IDs, MCP approvals use their distinct path.
- [ ] Invalid/extra arguments, wrong owner, unsupported capability and missing approval cause no forbidden source call or duplicate job.
- [ ] Six-tool-call example budget ends with actual partial/unfinished state; response loss resumes poll, cancellation stays one terminal outcome.
- [ ] Secrets absent from logs/fixtures/model summaries; decimal/variant/support output survives both routes.
- [ ] Actual paid API smoke records model/SDK/cost and selected route after offline success; second route has its own live status.

Future live budgets are route-specific. Remote MCP: ≤2API requests and ≤6tools;
complete the flow only if remote orchestration/required approval fits, otherwise
return explicit unfinished state and retain missing live coverage. Sequential function
route: ≤5API requests and ≤6tools; submit→status→result→final uses4requests; one extra
pending-status round permits5. Further pending polls stop unfinished. Evidence is
covered offline here; a live evidence continuation needs a separate declared case.
Each route: two products,120seconds,$1 maximum,512output tokens/request and6000input
tokens/request. Before paid execution select exact available model/tokenizer, count
inputs and price worst-case planned usage below$1; otherwise blocked. Tool output
≤12KiB/page size2, evidence references only. No hidden retry expands budgets.
Eligibility, API key, billing/model access remain prerequisites. No API/model calls
or connector publication occurred.
