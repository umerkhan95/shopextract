# Declaration skeleton: ecosystem service, adapters and skill packages

Date:2026-10-24. Documents only: no source stubs, executable APIs or implementation
claims. Expanded-scope G1/G2, G3 and final content review passed independently.
Child authors must finalize
and independently review OpenAPI/JSON schemas/status mappings before code. Source
and package locations below are proposals, not existing files.

## Ownership and entry points

| Proposed boundary | Owner / consumers | Declaration responsibility |
| --- | --- | --- |
| `shopextract.service.contracts` | Service maintainer; HTTP/MCP/adapters | Typed schemas/envelopes/errors/version/capabilities |
| `service.auth` | Security maintainer | Verified Principal, token scopes/audience, operator grants, owner checks |
| `service.jobs` / `service.store` | Service maintainer | Durable admission/key/publication/restart/expiry/metadata bounds |
| `service.domain` | Domain maintainer | Reuse guarded core paths, stable data/evidence; no copied algorithms |
| `service.http` | HTTP maintainer | Bounded routes, auth/error mapping, optional ASGI entry point |
| `service.mcp` | MCP maintainer | SDK transport/tool metadata, protocol compatibility, same service policies |
| `integrations/<platform>` | Named connector maintainer | Native credentials/UI/serialization/poll checkpoint and package tests |
| `skills/shopextract-review` | Skill maintainer | Trusted instructions/resources, capability manifest/host wrappers |

No declaration licenses a shared SessionStore across principals. Current local stdio
ToolRuntime and jobs remain their own ephemeral implementation contract.

## Proposed service data shapes

```text
Principal = server-derived {principal_id, granted_scopes, token_issuer,
                           audience, credential_expiry}; never caller-supplied
Policy = operator-owned {allowed_origins, capture_grants, limits,
                         storage_root, retention}; paths never tool arguments
Operation = discover | extract | match | changes
Submit = {schema_version:"1.0", operation:Operation, arguments:StrictOperationArgs}
Request context = {principal, validated_idempotency_key, absolute_deadline}
Envelope = {ok:boolean, request_id:string, warnings:SafeWarning[],
            data:TypedData OR error:{code:StableCode,message:safe,retryable:boolean,
                                    details?:SafeDetails}}
Job = {job_id:opaque, state:queued|running|succeeded|failed|cancelled|timed_out,
       created_at, started_at?, terminal_at?, deadline_at, result_expires_at?,
       completion_id?, error?:SafeError}
ResultPage = {job_id, collection, items:TypedRecord[], total:integer,
              next_cursor?:opaque, expires_at, completeness:SupportedCompleteness}
Evidence = {status:available|unavailable|expired, reason, owner_handle,
            evidence_id, captured_support?}; preserve core source/support model
Capabilities = {api_version:"v1", schema_versions:["1.0"], operation_descriptors,
                scopes_required, effective_limits, retention_policy,
                feature_flags:{general_export:false,analytics:false,
                 category_tools:false,maintenance_tools:false,fresh_captures:false}}
Completion = {completion_id:stable, journal_sequence:decimal_integer_text,
              job_id, terminal_at, terminal_state,
              result_availability:available|expired, result_expires_at?}
CompletionPage = {items:Completion[], next_cursor?, high_watermark,
                  retained_floor_sequence, stream_epoch, gap:boolean, checkpoint_version}
```

StableCode preserves existing commerce domain codes: invalid_argument,
unsupported_version, permission_denied, not_found, expired, resource_limit, timeout,
cancelled, source_error, internal_error. Service conflicts may use
`invalid_argument` plus safe `reason:idempotency_conflict` and HTTP409; interrupted
jobs use `internal_error` plus `reason:service_interrupted`, terminal failed.
No unknown enum is injected into unchanged core schema. Exact schemas/error mapping
must be finalized in child G1; tool inputs remain strict, no coercion/unknown fields.
Money is decimal text, no float; canonical IDs/currency/variants/evidence/completeness
are copied from real core outputs, never invented from constructor defaults.

## Proposed HTTP route/method contract

| Method / route | Required scope beyond authenticated owner | Response / effects |
| --- | --- | --- |
| GET `/v1/capabilities` | jobs:read |200 capabilities; no source fetch |
| POST `/v1/jobs` with Idempotency-Key | jobs:submit plus catalog:read/captures:read as operation requires |202 original/new owned job, durable state effect;409 conflicting body |
| GET `/v1/jobs/{job_id}` | jobs:read |200 authoritative queued/running/terminal state; no refetch |
| POST `/v1/jobs/{job_id}/cancel` | jobs:cancel |200 winning state, idempotent state effect |
| GET `/v1/jobs/{job_id}/results/{collection}?page_size=&cursor=` | jobs:read plus data scopes |200 immutable page on success;202 pending typed state; terminal failure safe envelope |
| GET `/v1/evidence/{owner_handle}/{evidence_id}` | evidence:read |200 available/unavailable support;410 owned expired, no recapture |
| GET `/v1/completions?after=&cursor=&page_size=` | jobs:read |200 owned retained-window completion page; gap explicit, no source fetch |
```
Transport mapping proposal: invalid/malformed400; token missing/invalid401 with
challenge; insufficient scope403; unknown or other-owner opaque object404 with
same safe shape; owner-known expiry410; idempotency conflict409; capacity/queue429
with bounded Retry-After; internal failure500; temporary service unavailable503.
Core source error/status is safely represented inside job terminal state, not raw
upstream body. Successful GET status may describe a failed job; it is not success
of the commerce operation. Child schemas specify `ok` for retrieval versus job state.
```

HTTP methods above are service API operations; permitted merchant methods remain
existing guarded GET/HEAD and exact allowlisted native read-only POSTs only. Merchant
state writes/export paths/arbitrary GraphQL/POST body are unavailable. Token auth
middleware never forwards service credentials to source connections. Input URLs are
subject to existing public-DNS/redirect/origin checks at every fetch boundary.

## Durable lifecycle, idempotency and references

```text
admit(context, Submit) -> Job
status(principal, job_id) -> Job
cancel(principal, job_id) -> Job
result(principal, job_id, collection, page_size, cursor?) -> ResultPage | Pending
support(principal, owner_handle, evidence_id) -> Evidence
completions(principal, after?, scan_cursor?, page_size) -> CompletionPage
expire(operator_clock) -> bounded retention outcome (not public path/delete API)
recover_after_restart() -> interrupted nonterminal jobs become failed exactly once
```

One transaction admits owner+normalized body hash+key+deadline. Replays return same
job ID; differing body conflicts. Key namespace includes owner+operation; request
serialization/hash must be schema-normalized and deterministic. Acknowledgement never
precedes durable commit. Key/tombstone24h remains valid after graph eviction; a retry
within window returns expired original result, not a new source job. After key expiry
new admission is explicitly possible; no all-time idempotency claim.

One publication transaction persists terminal graph/catalog/product/variant evidence
owners and references with job+completion. Restart never leaves valid-looking opaque
handles pointing at lost session memory. Incomplete publication is rolled back; failed
or cancelled work publishes no usable catalog. Interruption before publication becomes
failed `service_interrupted`; caller may explicitly submit new key. Cancel/commit has
one terminal winner. Graph expiry invalidates dependent result/evidence handles with
owned explicit expiry; no data refetch. Metadata/key expiry is separate from graph TTL.

Physical cleanup bounded by operator retention; auth checked before exposing existence.
Expiry tombstones must preserve authorized diagnostics without leaking across owners.
32graphs/32MiB total and metadata caps must account for actual copies and retained
references, not virtual dedup savings. Capacity exhausted rejects admission before ack.

## Cursor/checkpoint declarations

Result cursor binds principal/job/collection/schema/page_size/graph generation/expiry.
At sizes1..100 it traverses immutable result only; wrong owner, tampering, wrong size/
collection/version or expiry cannot trigger extraction or expose another graph.

Completion ordering is a durable strictly increasing journal sequence per principal,
not `(terminal_at,completion_id)`. Allocate/increment the principal counter in the same
serialized transaction that publishes terminal job/completion; later commits always
have greater sequence. Persist counters across restart, never reuse committed values;
new/deleted identity stream uses a new stream_epoch so old tokens fail explicitly.
Sequence is decimal integer text on wire; server compares exact integers. JS adapters
pass text/opaque checkpoints without Number coercion; if comparison is needed use
validated BigInt, never float or lexical sorting. SC04/14 include9007199254740993.
Opaque completion identity remains stable for dedup; terminal_at is display metadata.

Owner-authenticated checkpoint includes principal/stream_epoch and committed sequence.
At scan start fix numeric high-watermark H under the owner's transaction snapshot.
Return owned retained records with L < sequence <= H in descending sequence order;
new commits >H remain for next scan even if their wall-clock timestamp is equal/earlier
or opaque ID sorts lower. Scan cursor binds owner/epoch/L/H/page_size/schema and last
returned sequence. Partial-page failure resumes same bounded scan; only after all
records are emitted may consumer advance committed checkpoint to H. At-least-once
emit/checkpoint crash replay remains allowed with identical completion IDs; downstream
idempotent effect ledger handles duplicate business effects.

Retention removes a contiguous committed sequence prefix, advancing persisted owner
retained_floor_sequence. Empty journal retains counter/floor/epoch metadata within
service byte caps. If requested L is below floor, or pruning overtakes an unfinished
scan's unconsumed range, return explicit gap; do not return an apparently complete
empty page or advance consumer checkpoint. Wrong owner/epoch/malformed token fails
without existence disclosure. Child schemas finalize scan token signing/encoding and
gap recovery fields before code, but cannot replace numeric commit ordering with time.
SC14's late-same-time, backward-clock and response-loss fixtures must use the real
journal transaction/cursor path; no external live clock manipulation required.

## MCP and adapter interface mapping

```text
AdapterContext = {credential_handle, validated_service_origin, deadline,
                  max_pages, max_items, retry_budget, checkpoint_store?}
submit(args, context) -> accepted job identity
poll(job_id, context) -> authoritative state
page(job_id, collection, cursor?, context) -> immutable records
cancel(job_id, context) -> winning state
poll_completions(checkpoint, context) -> stable completion events + recoverable progress
capability_preflight(workflow, context) -> supported | explicit prerequisite failure
```

| Target | Host mapping / effects and output |
| --- | --- |
| n8n | Declarative native HTTP actions and credential class; separate programmatic completion trigger; standard Wait/Schedule nodes; stable item outputs |
| Claude | Existing stdio process config or remote MCP OAuth; list/call approved tools, local lifecycle separate from durable remote |
| ChatGPT | Remote MCP tool schemas/structured content/truthful annotations; private install, plugin submission separate; no UI baseline |
| OpenAI MCP | Remote `mcp` route; allowlist/auth/approval flow; no function_call_output for MCP calls |
| OpenAI function | Application sequential dispatch; function_call_output with matching call_id; explicit continuation/budget |
| Zapier | Auth test, submit/status/result/cancel actions; newest-first unique-ID completion array, bounded paging |
| Make | Connection/action/search/poll modules; exact bundles/pagination; pending distinct from empty success |
| Pipedream | App/common client, actions/timer source, service db checkpoint/stable emit IDs; unique cache100 not permanent ledger |

Tool descriptors enumerate auth/scopes and actual service effects. Durable submit,
cancel and replay bookkeeping are not automatically read-only in host annotations;
public source access is open-world. Registration modes/SDK transports are conditional
on host compatibility. No host gets unavailable export/analytics/category/maintenance
by aliasing an existing tool name.

## Proposed skill pack and host layouts

```text
skills/shopextract-review/
  SKILL.md                # trusted YAML name/description + workflow instructions
  references/recipes.md   # approved INT-10a subset, no extended-capability claims
  references/limits.md    # bounded operation/continuation/data-fidelity rules
  compatibility.json      # proposed release metadata, not universal host schema
  agents/openai.yaml      # optional OpenAI metadata, validated by that host
```

Proposed release metadata: pack_version, source_revision, host_wrappers,
required_tools/schema/capabilities, recipe_ids, declared_optional_dependencies,
executor_required (false baseline), expected_local_effects. This metadata cannot grant
scopes or auto-provision tools. Only host-supported frontmatter/manifest fields go
into actual install packages; compatibility.json is project metadata, not injected
arbitrarily into host schemas. ≤1MiB/32files, no absolute/traversal/symlink escape,
secrets or implicit script downloads. Optional scripts are a separately reviewed
extension, not installed baseline.

| Host / ticket | Proposed install wrapper and declaration ownership |
| --- | --- |
| Claude /12 | Product ZIP folder; Code .claude/skills path; API upload skill_id/pinned version separate. Do not sync stores implicitly |
| ChatGPT /13 | Current plugin package with skill + optional MCP config; validate real package schema; not Custom GPT Knowledge/Actions |
| Codex /14 | Repo/user .agents/skills, optional agents/openai.yaml; duplicate scope explicit; config/MCP registration separate |
| Cursor /15 | Selected .agents/skills or .cursor/skills project/user path; cloud/SSH visibility separately tested |
| Copilot /16 | Selected .github/skills or supported .agents/skills repo path; personal scope separate; client surface matrix |
| Gemini /17 | Selected .gemini/skills or alias; trust, workspace precedence, list/reload and selected version |

Activation: trusted intent→capability/auth preflight→bounded recipe→supported structured
result/evidence. Unknown/disabled/stale pack or missing tool is explicit prerequisite,
not hidden installation or arbitrary script fallback. Scraped data never changes policy.
Fresh/update validates intended selected version; no overwrite of unrelated host files.

## Child blockers to resolve before source implementation / live claims

| Exact unresolved decision | Owner / required evidence / blocked activity |
| --- | --- |
| HTTP framework/server+Python3.10 dependency versions | INT-01 author; compatibility pin and child G1; blocks service source scaffolding |
| Final OpenAPI/error enum/status/retrieval versus job success schemas | INT-01 contracts reviewer; schema fixtures/red acceptance design; blocks public API code |
| Durable table/migration/transaction/crash/expiry tombstone and cursor encoding | INT-01 storage owner; exact manifest and ownership/byte accounting design; blocks persistence implementation |
| OAuth provider, issuer/audience, allowed callback/CIMD/DCR/static registration | INT-02 security owner; provider metadata/test clients; blocks remote auth and host live setup |
| Actual SDK/host protocol negotiation | INT-02 + each host author; pinned compatibility smoke; blocks claimed remote support, may require new migration slice |
| Native package/runtime versions and exact plan quotas | Each platform owner; refreshed primary facts + private account; blocks live/package acceptance claim |
| Exact model/tokenizer/pricing for API budget | INT-06 owner; worst-case token/$1 preflight; blocks paid smoke |
| Host package schemas, discovery/updates/selected-version behavior | INT-11..17 owners; validated owned clean-profile install; blocks skill compatibility claim |

These blockers do not stop documentation planning. Platform account absence is a future
live blocker; it cannot waive real-path synthetic/stress checks or be reported as pass.


## Additive provider/agent wrappers (reviewed declarations)

| Ticket / target | Declaration-only package/tool seam | Exact remaining blocker |
| --- | --- | --- |
|18/19 Grok Build | Selected .grok/skills and plugin roots; native inspect/validate lifecycle; skill/MCP bundle | Current manifest/parser/MCP config pin; consumer skill package not inferred |
|18 grok.com /xAI API | Consumer custom MCP URL; API mcp endpoint+allowlist/auth descriptor | API no require_approval/connector_id; service/app consent proof, exact host protocol/model |
|20 Claude Code | .claude-plugin/plugin.json plus root skills and .mcp.json; local#24 route first | Child exact parser/package/version, no remote dependency for local slice |
|12 Messages API | Versioned container.skills with code execution; app-owned approved data input | Container has no network/package installs; separate model/code-execution eligibility |
|21/22 Meta optional | Muse Code .agents/skills+native MCP config; independent direct route | Exact Code plugin manifest/install unknown; personal Muse loader/API tool schema separate |
|23 Mistral Vibe Code | Experimental AgentPlugins1.0 plugin.json/skills/mcp.json, trusted native skill roots | Exact parser/version/reload pin; Work/API route not inferred |
|24 GLM/Z.ai | Native provider nested chat/completions mcp; external Claude Code plugin/skill loader | Entitlement/API model versus host permissions; ZCode native manifest unknown |
|25 Hermes Agent | Portable v1 plugin.json/skills/mcp.json OR minimal native plugin.yaml/register(ctx), native MCP | Pin exact runtime/namespace/partial-load semantics; no model-only installer |

These host wrappers consume existing service/portable contracts without new commerce
operations. No native package schema is guessed where source evidence is incomplete.
Separate descriptor fields: target_host, provider_model_endpoint?, native_loader,
package_format, tool_transport, credential_owner, version/discovery, support_state and
blocker. Skill dependency declaration never grants tool scope. Public catalogs and
organization publication remain external acceptance states. Current source count60;
no actual wrapper/package/source code generated by these declarations.
