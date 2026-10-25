# Reusable component model

Date: 2026-10-24. Documentation only. Expanded-scope G1/G2, G3 and final
content reviews passed independently; see reviews.md.
No code implementation, extraction/API/skill installation or runtime testing here.
Baseline reuse model retains reviewed service contracts; additive host mappings below
are reviewed planning declarations. Runtime implementation remains pending.

## Reuse inventory and ownership

Paths are repository-relative existing source references, not new public interfaces.

| Component / existing source | Reuse responsibility | Consumers / owner / boundary |
| --- | --- | --- |
| `tools/security.py`, `tools/sources.py`, `tools/context.py` | Existing origin/DNS/redirect/native read-method/byte/deadline enforcement and bounded source modes | Service domain and local stdio; source-security maintainer. Service constructs per-owned-job policy/context, never merges tenant grants |
| `tools/domain.py` parsing/matching/report seams | Reuse existing normalization/portable/domain operation paths, source evidence and guarded extraction | Service domain; commerce maintainer. Functions relying on ephemeral store need reviewed durable adapter, not an exposed shared ToolRuntime |
| `_normalize.py`, `identity.py`, `compare/identity_match.py` | Existing normalization/canonical supplier identity/matching relationships and conflicts | Core/domain consumers; identity maintainer. Preserve existing constructors/semantics; no connector-specific duplicate algorithm |
| `_portable.py`, `_evidence.py`, `tools/domain.py:json_value`, `tools/schemas.py` | Existing portable product/variant/source support serialization, decimal text and tool output schema | Durable graph encoding, HTTP/MCP, native adapter codecs; schema maintainer. Session handles require owner-scoped durable remapping with integrity checks |
| `monitor/reliable.py`, `monitor/evidence.py`, `tools/captures.py` | Existing reliable historical-change/evidence semantics from operator-granted captures | Service changes/evidence operations; monitoring maintainer. Replay bookkeeping is local write; no new snapshot/capture scheduling implied |
| `tools/contracts.py` | Existing strict validation, stable domain errors/envelopes, safe serialization | HTTP/MCP service adapter; schema maintainer. Add service transport fields/status mapping through reviewed schemas, not silent alteration of strict existing tool args |
| `tools/runtime.py`, `tools/jobs.py`, `tools/state.py`, existing stdio server | Reference existing limits, state transitions and local tool surface; preserve local runtime | Existing stdio only; local-runtime maintainer. In-memory jobs/store/session handles are NOT durable multi-tenant storage; lifecycle/storage must be new |

Source code inspection establishes potential reuse, not verified remote compatibility.
Existing private helpers are not promoted to stable public APIs by this document.
Child interface design may extract a minimal seam while retaining source-policy tests;
any changed behavior returns to its FR/SC and affected independent gates.

## New necessary components and shared consumers

| New boundary | Why existing component is insufficient / exact responsibility | Concrete consumers |
| --- | --- | --- |
| Durable admission/publication store | Existing jobs/graphs disappear with session. Own atomic owner+key admission, terminal graph/catalog/evidence references, job state, metadata bounds, expiry/tombstones and restart-failed nonterminals | HTTP actions, remote MCP, every polling platform |
| Owned completion journal | Existing session jobs are not resumable event stream. Own durable per-principal monotonically increasing commit sequence/counter/epoch, retained prefix floor, fixed-watermark scans and owner-bound cursors | n8n, Zapier, Make, Pipedream triggers and compatibility tests |
| Identity/auth boundary | Local operator process is not remote end-user auth. Validate issuer/audience/scopes/revocation, resolve Principal, combine with separate operator source/capture grants | HTTP private bearer and remote MCP OAuth; all owner lookups |
| Service operation facade | Reuse domain/security while mapping durable graph identities and context. One authoritative admission/status/page/cancel/evidence/completion contract; enforce effective limits | HTTP routes, MCP tools, future typed API examples |
| HTTP transport | No existing hosted authenticated routes. Bind reviewed schemas/status/challenges/deadlines, bounded serializations and safe errors to optional ASGI candidate | Native automation nodes/actions and function-tool dispatcher |
| Remote MCP transport | Existing stdio is local process only. Reuse tool shapes/SDK where compatible; expose shared service with truthful effects and host protocol/auth negotiation | Claude, ChatGPT, OpenAI MCP; host skill prerequisite |
| Native adapter codec/checkpoint helper | Native platform item/bundle/array formats differ. Preserve decimal/IDs/evidence/completeness, lossless decimal-text/opaque sequence; platform package owns checkpoint/emit crash recovery | n8n, Zapier, Make, Pipedream; framework-native helpers preferred |
| Trusted recipe/skill definitions | Source core code does not explain bounded user workflows or host install behavior. INT-10a approved definitions feed portable skill, host wrappers validate actual loader/package shape | INT-11 plus six skill hosts; INT-10b release matrix/examples |

No cross-platform plugin framework or arbitrary task scheduler is proposed. Share
stable schemas/fixtures/recipe definitions; platform-specific credential storage,
UI, event emission and package tooling stay native. n8n verification forbids adding
an external helper dependency: its codec can be a small local package module reusing
the contract/fixtures rather than an imported runtime library. Duplication of a short
transport mapping is preferable to violating native packaging requirements.

## Dependency direction and lifecycle

```text
trusted skill/recipe -> available approved host tools (preflight only)
native host adapter or MCP transport -> service operation facade
facade -> auth/owner policy + durable lifecycle + existing guarded domain
existing guarded domain -> normalization/identity/matching/evidence/reliable core
new durable store/journal -> typed portable records and transaction boundary
```

Core cannot depend on a platform package, OAuth UI or model service. Auth identity
never derives from product text or tool arguments. Domain output goes through schema
serialization into an owner-scoped durable graph; transport cannot mint its own facts,
perform unguarded network access or invoke unavailable exports/categories/maintenance.

Admission reserves capacity and commits key/job before ack. One active worker reuses
existing bounded execution principles. Successful terminal commit stores graph plus
all referenced catalog/evidence owners and completion atomically. Fail/cancel/timeouts
have one terminal winner and no usable catalog. Restart marks interrupted nonterminals
failed `service_interrupted`, never silently refetches. Result expiry and key retention
remain separate; expired original keys return original identity/expiry within24h.

Journal commit sequence is numeric/exact at storage and decimal text or opaque token
across JavaScript; no Number cast, timestamps as metadata only. Every owner stream has
persistent counter/epoch/floor. Snapshot scan `(L,H]` excludes future commits until next
scan; those remain discoverable regardless of same/earlier timestamp. Prefix pruning
that overtakes an unconsumed scan returns gap. External emit/checkpoint can redeliver
stable IDs; consumers own a business-effect ledger, service owns unique publication.

## Error ownership and compatibility

- Core/source validation owns invalid_argument, source_error, permission_denied,
  timeout/resource_limit and inspectable uncertainty; safe facade maps them without
  leaking raw upstream bodies, credentials or operator paths.
- Auth owns401/challenge/403; object boundary uses indistinguishable other-owner/unknown
 404 and authorized expired410. Service idempotency conflict is HTTP409 with stable
  error/safe reason; interrupted-job reason stays distinct from successful retrieval.
- Native adapter owns bounded Retry-After, platform request deadlines, pending versus
  empty result, item/page caps and recoverable checkpoint. It cannot retry by issuing
  a fresh submission key or suppress unseen retained events to fake exactly-once.
- Skill owns truthful activation/preflight/unsupported explanation and resource paths;
  it cannot grant scopes, register credentials, change source policy or auto-run scripts.
- Immutable reviewed schemas are shared reference. `/v1`, commerce schema1.0, MCP
  protocol and native package versions stay separate. SDK/client protocol changes need
  reviewed compatibility evidence, not automatic dependency upgrades.

## Verification ownership and remaining boundaries

Child fixture author uses the reviewed44case expectation matrix against real source,
state/auth/serialization/journal mechanisms; independent reviewer validates coverage
before bounded execution. Transport/clock/external APIs may be controlled boundaries,
not replaced domain mechanisms. SC04/14 check sequence9007199254740993 and late/backward-
clock commits; SC11 checks documented at-least-once replay; SC16..18 cover skills.
Offline/live results stay separate, exact child blockers remain in skeleton.md.

#24 remains delivered reuse; #26/#27 adjacent scopes are linked, not imported as
implemented. #27 owns merchant writes and signed push/dead letters; no hard dependency
for completion polling. INT-10a→INT-11→INT-10b avoids a release dependency cycle. Public
publication and installation remain future work with account/version prerequisites.


## Additive host wrapper reuse (expanded draft)

Grok Build, Claude Code plugin, Vibe Code and Hermes Agent consume the same trusted
recipe/skill files and existing local MCP or shared remote boundary; retain native
manifest/parser/lifecycle differences instead of a speculative universal plugin engine.
Grok API and GLM API codecs own their documented request formats; cannot copy OpenAI
approval fields. GLM model entitlement sits outside Claude Code host loader ownership.
Hermes Agent portable adapter versus native Python registry is a host choice, not new
commerce logic. Meta skill/MCP support is retained optional/deferred; missing manifest
blocks only that native plugin path. Messages container has no network: application
owns fetch, container skill owns bounded input processing, no hidden HTTP helper.

Next session only local Claude Code plugin+skill reuse#24 is proposed in handoff.md.
No remote durable/auth component is required for that slice; all other implementation
rows remain planned. Current task changes docs only; expanded G1/G2, G3 and final content review passed.
