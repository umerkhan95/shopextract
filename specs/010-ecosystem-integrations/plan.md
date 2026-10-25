# Implementation plan

Date:2026-10-24. Planning deliverable only; no runtime, connector or skill package
implemented. G1 independently passed the revised planning scope in reviews.md.
Expanded-scope G1, G2, G3 and final content reviews passed independently; see
reviews.md. Runtime implementation and host compatibility remain future work.

## Constitution check

Preserve existing Product/Variant constructors, canonical identity, extraction APIs,
feed formats and default local stdio lifecycle. Core remains MIT, self-hostable and
usable without hosted accounts or paid gates. Evidence/support/uncertainty are not
replaced by model summaries. Merchant access stays read-only; service persistence,
job submission/cancel and replay bookkeeping are explicit local effects. Source data
cannot grant policy. Optional paid platforms are integration prerequisites only.

Behavior/tests were authored before tasks/research and architecture. No source stubs,
installs, generated fake APIs or runtime checks in this slice. Future child authors
must prove meaningful red tests, independent design gates, real-path verification and
bounded live compatibility. Sequential work, one worker/no inference and saved progress
follow AGENTS.md. Actual session token counters unavailable; no quota inference.

## Architecture and decisions

Reuse existing guarded extraction/domain/serialization contracts beneath a new
service-owned lifecycle. HTTP automation and remote MCP are adapters to this service,
not independent extraction engines. Local stdio continues using ephemeral session
jobs; no shared unauthenticated session store is promoted to multi-user hosting.
Owner identity is server-derived and every catalog/evidence/cursor lookup is checked.

Proposed package strategy: optional Python HTTP service extra/entry point within the
existing repository, with service modules separated from `shopextract.tools` session
implementation. ASGI with FastAPI/Starlette and an ASGI server are candidates, not
installed or final dependencies; child research pins a Python3.10-compatible tested
combination before code. SQLite is a candidate durable store reusing project storage
experience but with separate owned job/publication/key/journal tables and migrations;
existing snapshot/capture paths stay trusted operator configuration. No network-scale
worker framework introduced for a one-active-job service.

Thin platform packages live under future `integrations/` directories, maintaining
independent platform metadata/version/tests. Keep first delivery in this repository
for traceability; split repositories only if verified platform submission requirements
or release ownership require it. n8n package has no external dependencies/env/file
access, uses built-in HTTP helpers; no Python bundled. Zapier/Make/Pipedream use native
integration artifacts. Claude/ChatGPT reuse MCP server with dedicated setup/evaluation
and packaging. OpenAI examples support two distinct orchestration routes.

`skills/` proposed release source contains trusted portable instruction pack and host
wrapper metadata; no files installed by this task. Host distribution remains native:
Claude ZIP/Code/API stores separate; ChatGPT plugin skill bundle; Codex/Cursor/Copilot/
Gemini supported directories and scope rules. No Custom GPT Knowledge/Actions shortcut.
No optional script baseline or auto-downloads. Dependencies/auth are preflight checks,
not privileges granted by a SKILL.md declaration.

### Contract and lifecycle decisions

- skeleton.md specifies proposed routes/methods/data shapes. Child G1 must finalize
  OpenAPI, schemas/status/error mapping and migrations before runtime code. API route
  `/v1` and commerce `schema_version:1.0` are separate; MCP protocol negotiation is
  separate again. Additive fields must not bypass strict existing input validation.
- Baseline eight commerce/tool operations only. Capability discovery/owned completion
  listing are service control-plane. Exports, generic analytics/validation/category/
  maintenance, fresh snapshot creation/scheduling remain named future extensions.
- Durable admission records request/key/deadline atomically before acknowledgement.
  Publication atomically commits terminal graph, referenced catalog/evidence and
  completion record. Interrupted nonterminal jobs fail `service_interrupted`; no
  automatic source refetch. Terminal referenced state survives or explicitly expires.
- Research limits apply: one active/8queued,32terminal graphs,1000items,4MiB/job,
  32MiB graphs/service; keys/journal256records each/24h/1MiB metadata combined.
  Key tombstones persist after result eviction within24h. Fail admission rather than
  evict idempotency records early. No unlimited tenancy/load claim.
- Result cursors bind owner/job/collection/schema/page size/expiry; immutable pages
  preserve decimal strings, currency, canonical IDs, variant support and partialness.
  Completion checkpoint is a separate ordered retained-window contract controlled
  by service-assigned per-principal monotonic journal sequence committed atomically
  with terminal publication; lossless decimal-text/opaque tokens preserve values beyond JS safe integers;
  timestamps/opaque IDs do not order checkpoints. Retention
  advances an explicit prefix floor and stale checkpoints report gap, not empty success.
- Remote MCP OAuth resource server validates token issuer/audience/expiry/scopes and
  supports host-compatible registration. Trusted operator grants constrain source
  origins/captures independently. Private automation scoped bearer credentials remain
  tied to service origin. No service token is forwarded to stores.
- MCP candidate2025-11-25 is conditional with current Python SDKv1. Current2026-07-28
  semantics differ; host negotiation can block compatibility and require a separately
  reviewed migration. No protocol upgrade or universal host support claimed.
- Polling baseline means completed jobs, not real-time commercial changes. Same
  completion identity supports ordinary retained-window dedup; external emit/checkpoint
  crashes are at-least-once. Consumer business-effect ledger handles duplicate effects.
  #27 owns signed outbound delivery/retries/dead letters, merchant-write/PIM/store
  scope; none is reimplemented here or required for read-only completion polling.

### Dependency DAG and waves (order, not duration commitments)

| Wave / work | Prerequisite | Observable exit |
| --- | --- | --- |
| Planning | FR/SC→tasks→research; G1 passed | G2 declarations, G3 reuse model, final docs/issue mapping |
| INT-10a definitions | Approved spec/tool contracts | Enabled bounded recipe definitions independent of platform release |
| INT-01 HTTP/durable | Delivered #24 reuse; child gates/red | Authenticated bounded durable job/result/evidence/control-plane |
| INT-02 remote MCP | INT-01; #24 schemas | Tested OAuth/principal/protocol transport |
| INT-03 n8n | INT-01 | Native deterministic node/private tests |
| INT-04 Claude | #24 local independently; INT-02 remote | Separate local/remote compatibility rows |
| INT-05 ChatGPT | INT-02 | Private app tools and truthful metadata |
| INT-06 OpenAI API | INT-02 MCP OR INT-01 function | Distinct bounded continuation/approval examples |
| INT-11 portable pack | INT-10a plus #24 local OR INT-01/02 remote | Validated instructions, safe package, capability preflight |
| INT-12/13/14 skills | INT-11 plus Claude/ChatGPT/Codex selected tool route | Separate host install/update/activation rows |
| INT-07/08/09 | INT-01; each own child gates | Zapier/Make/Pipedream native actions/polls and documented replay |
| INT-15/16/17 deferred | INT-11 plus selected supported tool route | Cursor/Copilot/Gemini guide and actual compatibility when implemented |
| INT-10b release | Only enabled implemented connector/skill rows | Importable recipes, measured compatibility, release-ready artifacts |

No cycle: INT-10a is definitions, INT-11 consumes them, INT-10b consumes finished
skills/adapters. Local skill work can reuse #24 without waiting for remote services.
Waves may only run sequentially unless user authorizes parallel agents. No dates,
cost savings or throughput estimate is promised.

### User-expanded native/plugin routes and next-session priority

INT-18/19 Grok Build uses documented native skill/plugin roots; grok.com connector and
xAI API remote MCP remain separate routes. API rejects OpenAI approval/connector_id
parameters; enforce service/application consent rather than pretending provider approval.
INT-20 bundles existing Claude Code skill/MCP, using actual manifest and local#24;
Messages API container is offline for network and receives app-fetched inputs only.

INT-21/22 Meta optional/deferred: Muse Code native skills/MCP verified; exact native
plugin manifest unresolved, personal Muse custom loader unverified, Model API distinct.
INT-23 Mistral Vibe Code uses experimental portable plugin+skills; pin/reload behavior
and Work/API separation reviewed. INT-24 GLM provider nested MCP versus external
Claude Code loader; ZCode native package unverified. INT-25 Hermes Agent uses actual
native skill/MCP and reviewed portable/native plugin route; no model-only claim.

Dependency additions: INT-18a is selected shared/local tool route; INT-19 consumes
INT-11+18a or#24local; INT-18b plugin consumes19afterward, no cycle; INT-20 consumes INT-04/11/12 selected local subset; INT-21a/22 selected Code
route independent from unknown21bplugin manifest (21bconsumes22afterward); INT-23/24/25 consume INT-11 and
chosen documented host/tool route. INT-10b consumes only enabled implemented rows.
No new service framework or all-vendor implementation sweep. handoff.md recommends
ONE next-session local Claude Code plugin+skill slice; no remote service prerequisite
or work started in this chat. All current scope remains docs/tickets only.

## Required gates

G1 re-review PASS is recorded by integration_reviewer; its original findings remain
historical. G2 passed this declaration skeleton; components.md was authored afterward. G3
reviews the reuse model next. Final checks planning diff,
FR/SC/task/source consistency, issue bodies and truthful state. Authors cannot approve
their own gate. Material changes return to affected behavior/tests/review.

Every implementation child repeats its applicable gates and intended executable red
acceptance proof before logic. Planning pass never counts as runtime skeleton/red,
mechanism, private live compatibility or marketplace acceptance.

## Verification and handoff

Current checks: source JSON/unique primary URLs,25tickets/24FR/24SC, registered
citations, relative artifact references and whitespace; saved planning-checks.json.
Future child fixture author serializes the44predesigned family/variant expectations
into exact schema-valid fixtures/crash points/assertion IDs. Independent reviewer
checks real-path coverage before one saved smoke then sequential stress; no generated
or executed44case corpus is claimed now. Seed/count/time/bytes and failures go in child
verification.md; existing valid checks are reused.

G1 fixes remain invariants: SC11 stable-ID at-least-once crash replay; INT-06 live
MCP≤2requests versus function≤5,≤6tools/120s/$1 and token/model/pricing preflight;
44explicit future variant expectations; INT-10a/11/10b acyclic sequencing. Account,
model/pricing/tokenizer or protocol mismatch is blocked live status, not synthetic pass.
API evidence continuation is offline or a separately budgeted live case. Other host
live limits/prerequisites are in test-design.md; begin one two-product smoke, preserve
blocked/inconclusive results and do not substitute mocks for required host evidence.

Versioned compatibility matrix separates documented, implemented, mechanism-tested,
private-live-compatible, submitted and accepted/published. User authorized planning
and issue documentation; actual installs/public releases require future implementation
and relevant authorization. Coordinator maps created issues; author modifies only this
spec directory. Baseline source register40pages reused; user-expanded current register60pages within61cap; before each implementation child,
refresh only material official interface/limit/auth/version facts for that target.


G2 ordering repair: FR14/SC14 now require a per-principal durable commit sequence.
The four additional planned cases make44total; same-timestamp/lower-ID late commits,
backward wall clock and response-loss resume cannot silently lose a retained completion.
The affected G1/G2 re-review passed; see reviews.md.
