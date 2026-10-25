# Feature specification: ecosystem integrations

Date: 2026-10-24. Status: behavior proposal; documentation-only delivery in this request.
Epic: ShopExtract ecosystem connections and integrations. GitHub issue links are
assigned by the coordinator; this document does not claim issues already exist.

## Outcomes and requirements

A user can use the same evidence-aware commerce operations from the baseline seven named
platforms plus the user-expanded provider/agent routes without rebuilding extraction or matching inside each connector.
This planning slice delivers a reviewed epic, twenty-five ticket specifications, official
source research and an implementation strategy. Runtime implementation, publishing
and marketplace acceptance remain future work, with independent child gates.

| ID | Observable requirement and completion boundary |
| --- | --- |
| FR-01 | Twenty-five tickets cover HTTP/jobs, remote MCP/auth, n8n, Claude, ChatGPT, OpenAI Responses API, Zapier, Make, Pipedream, recipes/release verification, a shared skill pack and six host skill integrations (Claude, ChatGPT, Codex, Cursor, GitHub Copilot, Gemini CLI). Add Grok skill/plugin, Anthropic Code plugin, optional Meta skill/plugin and Mistral/GLM/Hermes route tickets. Each records dependencies, inputs/outputs, failures, acceptance scenarios, official sources, limits and delivery evidence. |
| FR-02 | Shared HTTP operations submit bounded work and return a job identity before client request deadlines; status/result/cancel and capability discovery are explicit. Durable terminal jobs and their catalog/evidence references survive service restart or return explicit expiry, unlike current session jobs. Interrupted nonterminal jobs fail service_interrupted and require explicit resubmission. An acknowledged key maps to one owned submission; same key plus different normalized request is a conflict. Queued/running work interrupted by restart never silently succeeds or automatically refetches. |
| FR-03 | Remote MCP exposes versioned approved operations with authenticated principal, origin, scope and owner isolation. Existing local stdio remains usable. Missing/expired/revoked/wrong-audience credentials fail closed; supplied source text cannot grant tools, origins, scopes or credentials. |
| FR-04 | Every adapter preserves canonical IDs, decimal text, currency, variant relationships, evidence references, partial-completeness and uncertain match/change states. Page traversal is bounded, immutable and owner-bound; unsupported tools/versions fail explicitly. |
| FR-05 | n8n dedicated node supports credentials, operation selection, job submission/polling/cancel, pagination and stable item outputs. Polling completed-job delivery deduplicates by completion identity; manual actions and trigger semantics are documented separately. |
| FR-06 | Claude local stdio and remote MCP compatibility are separately tested with prerequisite account/client versions. Remote setup covers consent, authorization and reconnect; local session shutdown does not pretend to provide durable jobs. |
| FR-07 | ChatGPT MCP app supports private installation and tested tools with truthful tool metadata. Account/workspace permissions, OAuth/deployment requirements and directory submission are researched separately; private compatibility never implies public listing. |
| FR-08 | OpenAI Responses API example uses documented remote MCP and/or explicit function-tool adapter routes, with secret handling, tool-result continuation, bounded calls and explicit approvals where the chosen route requires them. Model narrative never upgrades uncertain source facts to confirmed observations. |
| FR-09 | Zapier integration has authentication, bounded actions and a defined completed-job polling trigger/dedup contract; input field validation, platform request timeouts and job-completion handoff are documented. Slow jobs never hold an action open beyond the platform limit. |
| FR-10 | Make integration defines connection, action/search/completed-job trigger modules, pagination, scheduling and stable bundles. Incomplete result pagination or an empty poll cannot invent removals or mark a pending job complete. |
| FR-11 | Pipedream components define authenticated actions and optional completed-job polling source with stable event identity, secret-safe execution and restart/replay behavior; code examples distinguish platform execution state from authoritative service state. |
| FR-12 | Recipes demonstrate bounded competitor review, supplier matching and feed preparation. Each operation is mapped to current capabilities or an explicitly dependent expansion; recipes cannot claim missing analytics/export/category/maintenance tools work today. |
| FR-13 | Scope is merchant-read-only: extraction and native read-only POSTs remain permitted by existing policy; no merchant edits, repricing, checkout or purchases. Durable service state, evidence retention, replay bookkeeping and export artifact creation are effects requiring explicit configured local/service scopes, retention and owner checks. Secrets and operator filesystem paths never appear in tool results. |
| FR-14 | Retry/polling follows per-platform limits and server backoff, respects cancellation/deadlines and avoids duplicate jobs and uses stable event identities with documented at-least-once replay boundaries. Rate/byte/item/retention caps are explicit; expiry, queue exhaustion, partial failure and response loss have observable stable outcomes. Completion checkpoints advance by service-assigned per-principal monotonic commit sequence, never display timestamps or opaque identity sorting; late same-timestamp/backward-clock commits remain discoverable. |
| FR-15 | Release verification distinguishes docs checked, adapter implemented, mechanism passed, private live compatible, public submission and public accepted. No future connector or runtime test is reported complete from this planning task. |
| FR-16 | A portable ShopExtract skill pack contains trusted instructions, capability prerequisites, optional explicit script dependencies and versioned examples. It cannot grant credentials/scopes or enable unavailable tools; scraped content remains data. |
| FR-17 | Claude, ChatGPT, Codex, Cursor, GitHub Copilot and Gemini CLI each have researched skill installation, activation, packaging, update/discovery and eligibility instructions. Unsupported host routes are explicit; a connector, Custom GPT Knowledge or Actions is not falsely called a SKILL.md installation. |
| FR-18 | Fresh/update skill checks cover correct activation, conflicting instructions, capability mismatch, dependency checks, archive/path traversal and secret exclusion; no actual skill installation/build occurs in this planning slice. |
| FR-19 | Grok/xAI has separate API tool/plugin-adapter and skill compatibility tickets. Distinguish provider API/function/MCP support, consumer Grok UI plugins/directory, native SKILL.md loading and application-owned instruction wrapper. No unsupported native feature is promised. |
| FR-20 | Anthropic mapping reuses Claude MCP/skill routes and adds Claude Code plugin package/manifest/skill+MCP distribution. Product ZIP skills, Code plugins and API agent/container skills remain separate tested routes. |
| FR-21 | Meta Muse mapping distinguishes personal consumer Muse, Muse Code agent and Meta Model API/model. Separate plugin/tool integration and skill compatibility tickets cite exact official support; unavailable native loader/plugin/distribution is explicit and does not inherit API capabilities. |
| FR-22 | Mistral mapping distinguishes provider API/Le Chat/Vibe; documented native skill/MCP/plugin routes are separate from application tool loops and unknown distribution. |
| FR-23 | GLM/Z.ai mapping distinguishes model/Coding Plan entitlement, API tools and actual coding-agent skill/plugin hosts; model access does not install a skill or grant tools. |
| FR-24 | Hermes Agent mapping targets NousResearch's agent runtime, not merely Hermes models; native skills/MCP/tools/plugin-equivalent route and distribution are documented only where verified. |

## Acceptance scenarios

| SC | Given / when / exact observable result | FR |
| --- | --- | --- |
| SC-01 | Inspect epic and child mapping: exactly twenty-five scoped tickets, seven connector platform targets and six baseline skill-host targets plus Grok and Meta Muse skill/plugin support investigations plus Mistral, GLM/Z.ai and Hermes Agent mapping, with dependency and requirement references, no duplicate merchant-write epic. | 01 |
| SC-02 | Submit one deterministic extraction with key K; replay K; restart after acknowledgement: one owner job remains addressable, one publication maximum. Different body with K returns conflict. Crash-before-commit leaves no acknowledged phantom success. | 02,14 |
| SC-03 | Principal A requests B's job, catalog, evidence or cursor; fails without existence/secret disclosure. Missing, expired, revoked or wrong-audience credentials cannot invoke operations. | 03,13 |
| SC-04 | Return fixtures containing decimal `0.10`, currency, product/variant IDs, unsupported stock, conflicting evidence and partial completeness over three pages: adapters preserve all values and page membership, including journal sequence `9007199254740993` as decimal text or opaque cursor without JS Number coercion; no generated fact or false deletion. | 04 |
| SC-05 | n8n runs an action and two polls with the same completion event: one stable product item per record, one new event delivery, bounded retries and cancellation, no re-extraction during result paging. | 05,14 |
| SC-06 | Claude lists/calls tools locally and remotely; local disconnect releases session state, remote reconnect retains authorized durable job, neither connection exposes denied tools or credential material. | 03,06 |
| SC-07 | Privately installed ChatGPT app lists approved tools, invokes bounded extraction and retrieves supported evidence. Denied workspace/account setup is recorded blocked. Directory acceptance remains a separate external outcome. | 07,15 |
| SC-08 | Responses API route runs submit/status/result continuation under a fixed call budget; malformed tool args fail without fetching and secrets stay server-side. Approval-required calls stop until approved; exhausted budget returns explicit unfinished state. | 08,14 |
| SC-09 | Zapier receives a slow operation and repeated poll fixtures: returns an accepted job within platform timeout, later emits a stable completed-job notification under the retained dedup contract; authentication failure and 429 do not resubmit work. | 09,14 |
| SC-10 | Make traverses two pages into bundles and polls pending then empty-success: unique IDs/data remain exact; pending is not empty completed output and empty success is not a removal event. | 10,04 |
| SC-11 | Pipedream source replays after checkpoint interruption and action retries after response loss: replay preserves stable completion identity and recoverable checkpoint without silently losing retained completions. Ordinary repeated polls deduplicate within the stated retained window; crash between emit/checkpoint may redeliver. An idempotent downstream consumer suppresses repeated business effects; service job publication remains unique. | 11,14 |
| SC-12 | Feed recipe requires unavailable export capability: explicit unsupported/dependency status; enabling an implemented scoped extension yields a bounded owned artifact. No arbitrary path/write scope or merchant mutation is accepted. | 12,13 |
| SC-13 | Source attempts private-network redirect, DNS change, prompt-injection instruction or credential extraction: existing guarded source policy rejects forbidden access; supported harmless data is not treated as authority. | 03,13 |
| SC-14 | At page/item/byte/queue/TTL/deadline boundaries: exact limit succeeds where valid; above-limit rejects explicitly, late completion cannot overwrite cancellation, expired cursors never restart extraction. After checkpoint at sequence41, a later committed completion at42 is returned even with identical/earlier terminal_at or lexically lower opaque ID; response-loss resume returns the same retained sequence or a declared gap, never silently misses it. | 02,04,14 |
| SC-15 | Planning handoff shows docs-only verification and pending runtime/live matrices; all future release statuses remain pending or blocked with specific prerequisite. | 01,15 |
| SC-16 | Install the portable pack on a declared compatible host: trusted user request activates only documented workflow, tool availability/auth preflight blocks unavailable operations, scraped instructions never alter skill policy. | 16,17 |
| SC-17 | Fresh install then update/restart/discovery using each host’s documented scope: the intended selected version is observed; overlapping scopes and stale discovery are reported explicitly. Unsupported direct SKILL.md host route is marked unsupported, not replaced silently with another feature. | 17,18 |
| SC-18 | Inspect archive/resources/optional scripts: traversal, symlink escape, embedded secret and undeclared dependency fail validation; safe minimal instructions-only package installs without downloading or executing arbitrary scripts. | 16,18 |
| SC-19 | Official xAI docs establish native Grok Build skills/plugins and separate API/grok.com MCP routes: Build package discovery and preflight use its verified loader; API instruction wrapper remains application-owned, and unverified consumer skill installation stays blocked. No raw SKILL.md is silently treated as a registered plugin. | 19,16,18 |
| SC-20 | Claude Code plugin installs trusted skill+MCP declarations in an owned test profile: manifest/version/layout valid, discovery/update and tool preflight work; missing OAuth/tool, invalid archive or scope collision cannot produce fabricated success. Claude product/API skill stores do not sync implicitly; Messages skill container network calls are disallowed, so source fetching stays application-side. | 20,17,18 |
| SC-21 | User requests Meta Muse skill/plugin: selection explicitly identifies consumer Muse, Muse Code or Model API. Only source-documented target route is enabled; model/API tools do not imply personal-agent plugin/skill installation. Missing public loader/auth/distribution contract stays blocked; supported wrapper preserves data/scopes. | 21,16,18 |
| SC-22 | Mistral request selects Vibe, Le Chat or API target: supported native loader/MCP or application tools execute only approved workflow; unsupported cross-surface feature returns explicit prerequisite, no universal support inference. | 22,16,18 |
| SC-23 | GLM/Z.ai credentials configure a documented API/coding host: entitlement does not grant tools or install skill; native packaging is enabled only for a verified host, missing/unsupported route stays explicit. | 23,16,18 |
| SC-24 | Hermes Agent skill/tool setup targets actual NousResearch runtime: discovered skill and approved tool route are inspectable; Hermes model-only access cannot claim agent plugin/skill support. Invalid package/auth fails safely. | 24,16,18 |

## Current capability and gap map

Inspected `docs/agent-tools.md`, `src/shopextract/tools/runtime.py`, `jobs.py`
on 2026-10-24. Existing tool names: discover, extract, match, changes, evidence,
job_status, job_result, job_cancel. Jobs and opaque handles are process/session
owned; disconnect/restart loses them. Do not relabel those jobs durable.

| Core family | Current tool coverage | Ecosystem requirement / boundary |
| --- | --- | --- |
| Store detection/discovery | discover; bounded native/public sitemap modes | Preserve allowlists and limits |
| Extraction/normalization/variants | extract; guarded native/static/feed sources | Browser/LLM fallback remains unavailable unless separately designed |
| Matching/catalog comparison | match with existing supported matching output | General comparison/search API beyond this output requires expansion |
| Reliable monitoring/changes | changes over operator-granted captures | Scheduler/fresh captures/history management require scoped service work |
| Evidence/source trust | evidence plus field references | Durable ownership/retention design required; never fabricate retention |
| Feed import | recognized guarded feeds in extraction | General file upload/import needs separate validated surface |
| Export/feed generation | no registered export tool | Scoped artifact extension required; no arbitrary destination paths |
| Analytics/competitive intelligence | no general tool | Capability extension with typed outputs and bounded work required |
| Marketplace validation | no general tool | Explicit rules/version reporting extension required |
| Category mapping/tree acquisition | no standalone general tool | Mapping config and credentials require separate operator ownership |
| Maintenance/correction/review | no general tool | Existing maintenance state is not remote job durability; reports only in this epic |
| Local persistence/snapshots/history | operator APIs; replay bookkeeping may write | Explicit service persistence permission and retention, no merchant writes |
| Hosting/auth/HTTP | local stdio only | New foundation; do not expose session runtime directly without isolation |

First ecosystem release exposes only the existing eight operation names through
new transport/service adapters. HTTP capability discovery and an owned completed-job
listing are service control-plane additions, not new commerce operations. Polling
triggers mean new completed jobs; scheduled fresh capture ingestion and commerce
change streams are deferred extensions. Existing operator-granted historical
captures can support matching/reliable-change review. No connector silently enables
export, analytics, category or maintenance operations.

Capability expansion is not implicit in a connector. Shared tickets must classify
each missing surface as first-release inclusion with designed tests or named later
dependency; recipes requiring deferred capabilities remain pending.

## Boundaries and compatibility

- Keep core MIT/self-hostable; optional commercial platform accounts/hosting are
  prerequisites, never gates on the local core. Preserve existing constructors,
  extraction APIs, source trust and default feed formats.
- Existing #24 MCP work is reused. Cross-link #26 and #27 (Integrations & Event
  Delivery); their approved merchant-write/PIM/store and signed durable webhook,
  secrets/delivery/dead-letter responsibilities are not reimplemented here.
  Polling works without those outbound webhooks; push recipes depend on #27's
  delivery contract and may not claim exactly-once external delivery.
- Public directory/marketplace review, platform billing and eligibility are external
  outcomes. Research must state dates and prerequisites rather than promise acceptance.
- Planned remote jobs do not alter local stdio lifetime defaults. Session handles
  cannot be promoted into durable IDs without explicit authorization/mapping.
- No production credentials, external account writes, platform publication, model
  launches or runtime implementation in this documentation task.

## Workflow

Follow `docs/development-workflow.md`; behavior/test design precede tasks/research.
Independent G1/G2/G3/final gates review this planning artifact set. Architecture
and component deliverables are documents only; implementation children must later
prove executable red tests before logic and run mechanism/live checks themselves.

## Skill extension scope

INT-11 portable skill pack; INT-12 Claude skills; INT-13 ChatGPT skill/plugin route;
INT-14 Codex skills; INT-15 Cursor skills; INT-16 GitHub Copilot skills; INT-17 Gemini
CLI skills. Last three are a deferred implementation wave with researched construction
paths. Skills provide instructions/resources; connector transport, authentication and
durable service remain separate prerequisites. Existing ten connector tickets remain.

## User-steered provider expansion

Retain INT-01..17. Add INT-18 Grok Build plugin/xAI tool adapter; INT-19 Grok Build skill
compatibility/application wrapper; INT-20 Anthropic Claude Code plugin distribution;
INT-21 Meta Muse plugin/tool target mapping; INT-22 Meta Muse skill compatibility.
No blanket native skill/plugin support is assumed. Prior G1/G2 passes remain historical
for their reviewed revision; expanded behavior/test/research/contracts need affected
independent review before final planning completion.

Latest priority: INT-21/22 Meta are optional deferred work, retaining verified Muse
Code native skill/MCP facts without promising personal Muse packaging. Add INT-23
Mistral, INT-24 GLM/Z.ai, INT-25 Hermes Agent mapping. This chat remains documentation
only. Next-session recommendation is one bounded Claude Code local plugin+skill slice
(INT-20+relevant INT-12/#24 reuse), no remote-foundation dependency or work started.
