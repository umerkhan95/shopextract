# Bounded production research

Researched: 2026-10-24. Author: integration_author. Scope: a connector construction
route for seven targets and two foundations, not an exhaustive platform-doc audit.
Official pages were actually fetched; compact source facts/URLs/sections are saved
in sources.json. No account integration, code installation, model request or runtime
probe occurred. Documentation includes future recommendations, clearly separated
from fetched platform facts. Failed obsolete URLs were repaired using canonical
redirects once; unresolved links are excluded as evidence.

## Questions and decisions

| Question | Evidence / alternatives | Decision for child design |
| --- | --- | --- |
| Rebuild or wrap core? | Local runtime already guards native/static sources; stdio jobs expire on disconnect | Reuse domain/security/data contracts, add a service-owned durable lifecycle, never expose a shared SessionStore to multiple principals |
| One transport everywhere? | Automation platforms consume APIs; Claude/ChatGPT use MCP | HTTP durable-job API for deterministic automation; remote MCP delegates to same service; stdio remains local |
| Require an LLM for n8n? | n8n node CLI offers declarative HTTP and programmatic styles | Dedicated native API node; declarative actions plus programmatic trigger. MCP optional AI route, never requirement for ordinary workflows |
| Bundle Python inside n8n? | Verification rules prohibit external dependencies/env/filesystem access | Thin TypeScript HTTP node using n8n helpers; no embedded Python/SDK npm dependency; npm provenance and verification workflow planned |
| Treat remote MCP as current local session? | MCP remote transports/auth differ; local repo pins optional MCPv1 | Keep existing stdio/defaults. Remote adapter must define protocol matrix/auth and owner mapping explicitly |
| Latest protocol automatically? | MCP2026-07-28 per-request metadata differs from2025-11-25 | Initial candidate remote compatibility target2025-11-25 with pinned Python SDK; child must test actual client negotiation. Latest-only clients block that row, requiring reviewed upgrade slice, not claimed compatibility |
| Same authentication on every target? | ChatGPT uses end-user OAuth; automation platforms support own connection schemas | OAuth resource-server identity for remote MCP; scoped revocable bearer credentials for private HTTP automation, optional OAuth connections. No raw user key pasted into ChatGPT tool args |
| Wait for extraction inside request? | Zapier execution budget30s; current core defaults30s and allows120s | Return acknowledged durable job promptly; separate status/result/cancel. Automation steps don't busy-wait for full extraction |
| Do polling triggers need #27? | #27 owns signed outbound push/delivery; platform polling can list owned completions | INT-01 owned completion listing; adapters dedup stable completion IDs. Signed push is optional #27 dependency; no dependency on merchant-write approval |
| Which commerce features ship first? | Exactly8 existing tool operations; general exports/analytics/maintenance/category absent | Baseline only. Capability-gated future recipes; named later extension required before exposing additional operations |
| Is publication automatic? | n8n verification, ChatGPT directory, Make approvals and Zapier public versions are separate processes | Private compatibility first, versioned release preparation next; external acceptance tracked separately. No publishing in this docs task |

## Platform research findings and resulting construction choices

**n8n:** reviewed node CLI, credentials, submission and verification pages (N1..N4).
Use a package named `n8n-nodes-shopextract`, credential class and platform HTTP
helpers. Action UI maps operations to submit/status/result/cancel; a separate
programmatic polling trigger lists completed jobs. Prefer no custom sleep/flow-control
node; use standard schedule/wait nodes. Versions and Cloud verification need actual
private installation and review; no statement that an unverified package works on Cloud.

**Claude:** reviewed Claude Code MCP, remote connector help and official local
connection guide (C1..C3). Deliver separate Desktop stdio config and Claude Code
command examples, plus remote connector setup. Remote consumer connections originate
from Anthropic cloud; localhost/ordinary private VPN reachability isn't sufficient.
OAuth/login, account policy and local process lifecycle must be tested separately.
No new branded transport is needed merely to claim a Claude connector.

**ChatGPT:** build/auth/private-test/submission pages (O1..O4) describe current
Plugins terminology and end-user OAuth. Use the shared remote server with narrow tools;
no optional UI in baseline. Public submission requires its own package/review materials,
not simply an endpoint URL. `readOnlyHint` cannot be set from merchant-read-only
marketing: durable submissions, cancellation or bookkeeping change service state.
Tools accessing arbitrary allowed public stores need truthful open-world metadata.

**OpenAI API:** Responses MCP/function-calling pages (O5..O6). MCP route configures
remote endpoint/auth/tool allowlist; function route executes in application and returns
matching `call_id` outputs. Do not mix output/approval flows. Examples cap turns/tools
and preserve machine output alongside natural-language summaries. No API call was made.

**Zapier:** CLI/auth/dedup/constraints/visibility pages (Z1..Z5). Source currently
recommends `zapier-platform` binary, with older `zapier` alias deprecated. Build
auth test, submit action, status/result action and new-completed-job polling trigger.
Polling returns an array ordered newest first with stable unique `id`. It does not
automatically fetch every page; service filtering/retention/backlog behavior is required.
30-second execution limits make asynchronous submission necessary. Poll frequency
is user-plan dependent; do not copy page summary's30s phrasing as a universal interval.

**Make:** connections/pagination/polling/visibility pages (M1..M4). Connection owns
secrets; request/response module definitions map service calls into bundles; pagination
uses service cursor, not guessed numeric offsets. Use sorted completion records with
start-point configuration. Private installation, published invite link and approved
public catalog are three different states; publishing has deletion/reversal restrictions.
No app was created or published.

**Pipedream:** action/source quickstarts and component reference (P1..P3). Package
an app/common client plus versioned actions and timer source with persistent checkpoint.
`unique` platform dedup caches100 IDs, so it alone cannot prove long-backlog replay
safety. Source must preserve authoritative completion ID/watermark, bound each run,
and document at-least-once external delivery around emit/checkpoint crashes. Private
publish/deploy is distinct from public registry distribution. No component was deployed.

## Proposed first-release service policy (design decisions, not platform facts)

- Owned HTTPS endpoint;5-second admission target, fail explicitly before admission
  timeout. Operation deadline includes queue time, maximum120s and default30s.
  One active job/service,8 queued;1000 items/job;256KiB input;4MiB graph/job;
  32MiB retained service graph state. These conservative limits reuse current runtime
  ceilings; production capacity beyond them needs separate measured design.
- Durable submission keys are scoped to principal+operation. Key lifetime24h; maximum
 256 retained key records/service. Immutable completion journal maximum256 metadata
  records/service retained24h; capacity reached rejects admission before acknowledging.
  Key tombstones outlive result eviction within24h; replay returns same job identity
  and explicit expired result, never a fresh job. Secrets are not journal payloads.
- Terminal graphs capped32/service and24h retention maximum; responses expose actual
  expiry. Evicted/expired result IDs return explicit expiry; completion listings retain
  metadata until journal expiry. Polling older than retained checkpoint returns gap
  status, never silently claims no new items. Metadata/key/journal storage also has a
  1MiB cap/service and fails closed before admission if exceeded.
- Results page1..100(default20), cursor tied to owner/job/collection/schema/page size;
  explicit malformed/expired statuses. Decimal/currency/evidence preserved. Completion
  listing order is descending per-principal monotonic `journal_sequence` (decimal
  integer text, compared numerically) with authenticated owner-bound `after` marker.
  Allocate sequence atomically in terminal-publication commit order and preserve
  counter across restart; timestamps/opaque IDs are metadata only. Retention removes
  a contiguous prefix and advances retained_floor; stale checkpoints return explicit
  gap. Fixed sequence high-watermark and resumable scan preserve late commits for
  the next scan, independent from immutable result cursors.
- Interrupted nonterminal jobs become failed with safe `service_interrupted` reason;
  no automatic re-extraction. A retry requires new explicit submission key. Atomic
  commit records publication, completion and dedup key outcome together. This is a
  deliberately simpler recovery choice than checkpointing partly captured source data.
- Bearer secrets in private HTTP automation are restricted to configured service base
  origin. OAuth/MCP bearer audience is validated for its resource; neither transport
  forwards its credentials to merchant stores. Operator store origins remain deny-by-default.
- Minimum proposed scopes: `catalog:read`, `evidence:read`, `jobs:submit`, `jobs:read`,
  `jobs:cancel`, `captures:read`. Local durable state is a configured operator effect;
  export and merchant-write scopes are absent. Each child refines exact schema at G1.

## Failure, compatibility and open prerequisites

No blanket platform request/payload/rate figure is assumed. Zapier30s and Pipedream100
ID-cache are verified; n8n/Claude/ChatGPT/Make/Pipedream account/runtime quotas and
payload limits must be rechecked against the exact version and plan before executable
children. Use lower service/platform limits, bounded Retry-After, no polling storms.
OAuth provider choice, key management/backups, production hostname and developer
accounts are deployment prerequisites, not resolved by this documentation. Remote
protocol compatibility may require SDK migration; pin/test before advertising support.

#24 is delivered reuse. #26/#27 own adjacent contracts; this epic cannot import their
future completeness as current capability. Shared completion polling does not implement
signed webhooks, secret rotation across external stores or downstream merchant writes.

## User-steered skill extension (behavior/tests/tasks revised first)

The original ten connector tickets remain. Seven added tickets cover a portable
pack plus Claude, ChatGPT, Codex, Cursor, Copilot and Gemini CLI host routes. Baseline
research register:40 distinct successfully fetched primary pages; this includes11
skill-related pages and29 foundational/connector pages. No broad documentation sweep.
All register entries were fetched in this assignment; earlier conversation URLs were
starting references only, not counted as unread proof. Sources have compact paraphrase
notes/read scope, not full duplicated pages. Per-session token counters unavailable;
source count and saved artifacts bound research rather than inferred quota percentages.

| Host | Supported construction route from fetched sources | Installation/update boundary |
| --- | --- | --- |
| Portable pack | SKILL.md plus optional references/assets, scripts opt-in | Common capability preflight; archive/secret/dependency validator; no tool provisioning |
| Claude | Product ZIP upload; Code local skills; Managed Agents skill upload/ID/version | Personal/team/API are separate stores; do not imply cross-surface sync |
| ChatGPT | Official current plugin skill route, packaged skill folder plus MCP | Account/workspace eligibility and private install required; raw local folder loading not promised on web |
| Codex | Repository/user .agents/skills; optional OpenAI metadata | Discovery and duplicate names tested; restart if missing/config changed; MCP configuration separate |
| Cursor | Project/user Agent skill directories | Local discovery does not imply cloud/SSH sync; record exact surface |
| Copilot | Repository/personal skills on documented supported agent surfaces | Cloud cannot assume local user's home skill or MCP/auth files |
| Gemini CLI | Workspace/user skills, CLI install and in-session list/reload | Trust and precedence matter; Gemini web/API outside CLI ticket |

Baseline OpenAI docs affirm skills in ChatGPT/Codex through plugins; no need to label
this unsupported by assumption. Custom GPT Knowledge/Actions remain different features.
Baseline Claude API route was Managed Agents; the later A3expansion separately
fetched Messages skill-container documentation, with network constraints recorded below. No missing
source blocks documentation; actual host credentials/entitlements and transport
version compatibility remain future live prerequisites.

Packaging policy proposals (not platform limits): instructions-only baseline; archive
≤1MiB/32files, no traversal/absolute paths/symlink escape or secrets; optional scripts
require explicit dependencies and review before activation. Installation guide must
not overwrite unrelated host config or grant scopes. Skill invocation receives user
intent, not source-page instructions as authority. Update checks prove selected version
and scope; disabled/stale/duplicate pack states remain visible.


## G1 author revisions (independent re-review passed)

G1-01: Pipedream delivery is at-least-once across emit/checkpoint crashes. Stable IDs
and recoverable checkpoint prevent silent retained-event loss; idempotent consumers
suppress duplicate business effects. Ordinary repeated polls deduplicate only within
the declared retained contract; service publication remains unique.

G1-02: API budgets are route-specific in INT-06/test-design. Remote MCP permits at
most2API requests; if approvals/continuation do not fit it records unfinished rather
than passed full flow. Sequential function smoke allows5requests: submit, status,
optional extra status, result, final. Evidence stays offline or separately budgeted.
Each route remains6tools/120seconds/$1 maximum, with explicit token caps and exact
model/tokenizer/pricing preflight; missing access/count/pricing blocks paid execution.

G1-03: test-design now enumerates eleven families (44cases total) and four variant inputs/expected outcomes
each. These44planned cases must become an exact child fixture/assertion manifest
before generation/execution. No mechanism/stress tests have run in this docs slice.

G1-04: INT-10a is the approved enabled recipe-definition subset from spec/tool contracts;
INT-11 consumes it plus chosen local #24 or remote tool route. INT-10b final executable
recipes/compatibility/release consumes finished connectors/skills. No skill pack waits
for all-platform release verification; no circular dependency.


## G2-01 author revision (affected G1/G2 independently passed)

Behavior FR14/SC14 and test-design were extended before repairing architecture.
Completion identity is distinct from per-principal publication order: a durable
monotonic journal sequence allocated in the same serial commit as terminal publication
controls checkpoints. Wall-clock timestamps cannot filter out later commits. New
four-case family covers late same-timestamp/lower-ID commit, backward wall clock,
response-loss scan plus later commit, and cross-owner/retention-floor gap. The future
manifest grows explicitly40→44cases/1,100operations maximum; other time/resource caps
unchanged. No runtime checks executed or new external research performed.

SC04/14 also preserve sequence9007199254740993 across JS adapters as decimal text
or opaque token, no Number coercion; server orders exact integers.


## User-expanded provider/agent research (current total60sources)

Original40sources remain saved/reused. User then requested Grok, Anthropic and Meta
Muse (11new pages), followed by Mistral, GLM/Z.ai and NousResearch Hermes Agent (9new).
All20new pages actually fetched; total60within revised61cap. No inference/install or
integration execution. This is selected route research, not exhaustive vendor docs.

| Target / sources | Verified construction route | Explicit unsupported/unverified boundary |
| --- | --- | --- |
| Grok Build X3/X4 | Native SKILL.md roots, local plugin directories, inspect/validate/install/update | Exact host package/parser pins future; consumer skill loader not inferred |
| grok.com X1 / xAI API X2 | Consumer custom MCP URL flow; API remote MCP allowlist/auth | API require_approval and connector_id unsupported; do not copy OpenAI approval route |
| Anthropic A1/A2/A3 | Claude Code manifest+skill/MCP plugin; Messages container skill route | Container cannot access network/install packages; app fetches inputs; product/Managed/API stores separate |
| Meta ME1..4 | Muse Code native skills+MCP; personal Muse is another product | Exact Code plugin manifest unresolved; consumer native loader/API tool schema unverified; optional/deferred |
| Mistral MI1..3 | Vibe Code native skills+experimental Agent Plugins1.0/MCP | Work/legacy Chat/API not proven by Code package; pinned/reload lifecycle matters |
| GLM/Z.ai ZA1..3 | Provider nested MCP in chat/completions; Coding Plan external Claude Code setup | ZCode native manifest unknown; model entitlement is not host loader or tool scope |
| Hermes Agent H1..3 | Native skills/MCP and native Python or portable plugin subset | Not Hermes model-only access; exact runtime/namespace/partial-load rules need real parser proof |

Chosen strategies: thin native wrapper when loader is documented, otherwise explicitly
named application-owned instruction/tool adapter or blocked target. No SDK payload is
assumed interchangeable across providers. Keep service-side source/auth/side-effect
limits when provider-mediated approval is unavailable. No automatic account migration,
vendor setup script, hook, agent spawning or model-key registration in our packages.

Meta ambiguity resolved to Meta product family, not an unidentified app. Muse Code
native skill/MCP support is affirmative; optional deferred implementation does not mean
unsupported. Exact plugin package contract and personal-agent custom installation
remain unknown after bounded sources. A guessed Code plugin URL was inaccessible;
stop rather than invent a manifest. User prioritized other platforms; next-session
handoff recommends one Claude Code local skill/plugin slice using existing#24.

Provider cases SC19..24 augment baseline44mechanism expectations with bounded native
host/API route checks; they do not claim an executed corpus or justify another sweep.
Exact model/entitlement/token/rate/cost preflight is mandatory before paid future calls.
Counter visibility remains unavailable;20new source pages and saved artifacts bound this
expansion. Affected G1/G2 reviews must check this scope before downstream final pass.
