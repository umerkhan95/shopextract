# Behavior and test design (before task breakdown)

Date: 2026-10-24. All runtime checks below are **planned**, not executed.
This slice changes documentation only. Its actual checks are completeness,
traceability, source/link/capability accuracy and independent review.

## Scenario matrix

| FR | SC | Given / input fixture | When | Exact expected outcome | Negative / boundary cases | Offline check | Live assertion / applicability |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 01,15 | 01,15 | Twenty-five-ticket map and status ledger | Inspect documents | Baseline seven connector/sixskill hosts plus Grok/Meta tool and skill mapping and Anthropic plugin plus Mistral/GLM/Hermes;25tickets; no invented completed connectors/reviews | Missing owner/source/test/dependency | Docs traceability/link checks | Docs-only: not applicable |
| 02,14 | 02 | Key K/body A, response lost at ack, controlled crash checkpoints | Retry/restart | One job and at most one publication; same K/body B conflicts | Crash before/after commit; expired key; owner mismatch | Real persistence/submission path with injected crash | Owned service restart; verify same durable ID |
| 03,13 | 03 | Two principals with owned job/evidence; invalid credentials | Access cross-owner or invoke | Deny without object existence/secret/path disclosure | Missing/null/empty token, expiry at boundary, wrong audience, revoked scope | Actual auth/ownership middleware | Two test identities and reconnect/revoke |
| 04 | 04 | Three pages; `0.10`, zero, null, absent, false stock, variants, conflicting support | Serialize through each adapter | Exact decimal text/IDs/evidence/completeness plus journal sequence9007199254740993 as lossless text/opaque cursor; immutable items and counts | Escaped Unicode IDs, tampered cursor, mixed page size/version/owner | Real adapter serialization/pagination | Compare bounded fixture catalog output |
| 05,14 | 05 | n8n action, pending/completed poll and repeated event | Run real node | Stable record output, event emitted once under persisted dedup contract | 429/retry-after, credential error, cancel during poll | Node execute/trigger runner and real service | Private node install; action plus trigger |
| 03,06 | 06 | Local stdio and remote durable service | List/call/disconnect/reconnect | Same approved semantics; local cleanup versus remote authorized persistence | Protocol mismatch; denied tool; disconnected client | Real MCP SDK/transport/client boundary | Separate Claude local and remote connections |
| 07,15 | 07 | Private app with allowed/denied scopes | Install/list/call | Approved tools/evidence usable; no public-acceptance claim | Account/workspace disallows app; unsupported protocol | Real MCP route with controlled client | ChatGPT eligible account/private app required |
| 08,14 | 08 | Responses tool sequence; 6-call budget | Continue results | Submit/status/result works; malformed args reject before fetch; unfinished when budget exhausted | Unknown tool, required approval withheld, model-generated source instructions | Actual example adapter against controlled Responses boundary | Bounded paid API request with eligible model/account |
| 09,14 | 09 | Zapier action exceeding request duration, replayed poll | Run action and polling trigger | Acknowledge job before documented timeout; completed events have stable IDs | Slow/pending/error, replay, rate limit | Actual integration handlers with virtual clock | Private integration connection/action/poll |
| 10,04 | 10 | Make two pages plus pending and empty-complete | Run action/search/trigger | Exact bundles; pending distinct from empty success; no synthetic removals | Pagination cap, missing cursor, 429 | Actual module definitions/helpers in harness | Private app, bounded scenario execution |
| 11,14 | 11 | Pipedream checkpoint crash and response-loss retries | Restart source/action | Stable completion ID and recoverable checkpoint; ordinary poll dedup within retention; emit/checkpoint crash may redeliver, idempotent consumer applies business effect once; one authoritative service job | Crash before/after platform checkpoint; token revocation | Actual component paths with injected boundary failure | Private component deployment/action/source |
| 12,13 | 12 | Recipe requesting unavailable export then scoped extension | Run capability preflight/export | Unsupported first; owned bounded artifact only once extension exists | Filename traversal, CSV formula cells, unauthorized artifact owner | Real recipe runner/artifact boundary | Owned sample artifact; no merchant writes |
| 03,13 | 13 | Controlled source with redirect/DNS/prompt injection | Extract/call tools | Private network/privilege escalation denied, secret absent | Public→private redirect; metadata IP; page-provided API config | Real guarded transport and normalization | Live hostile cases not safe; controlled mechanism required |
| 02,04,14 | 14 | Exact caps/cancel plus commit-order checkpoint fixtures | Poll/page/expire | Valid at cap; clear above-limit error; one terminal winner; per-principal committed sequence42 after41 is returned despite same timestamp/lower ID or backward wall clock | Limit−1/limit/limit+1, TTL expiry mid-page, partial+replay; late same-time commit, backward clock, checkpoint response loss | Real budgets/job state/persistence paths | Small boundary smoke only where safe |
| 16,17 | 16 | Installed trusted skill; tool absent/auth denied; malicious scraped instructions | Activate workflow | Correct preflight and explicit unsupported/denied result, no policy elevation | Wrong task activates; tool name/schema mismatch | Real host parser/discovery + installed tool seam | Each eligible host sandbox |
| 17,18 | 17 | Fresh pack then changed version under host precedence scopes | Discover/reload | Intended version selected; stale/duplicate scope conflict visible | Unsupported direct SKILL.md route; missing restart | Real host install/discovery paths | Record exact host/version/account |
| 16,18 | 18 | Clean pack plus traversal/symlink/secret/undeclared-script cases | Validate package | Reject unsafe cases before install/execution; clean instructions-only pack passes | Missing/null manifest, archive size cap | Real validator and host package loader | Only owned safe pack; hostile packages offline |
| 19,16,18 | 19 | Grok Build verified native loader versus API/consumer routes | Preflight/activate | Verified Build skill/plugin loader with preflight; documented API route or application wrapper separate; unverified consumer skill install explicit | API feature falsely applied to consumer UI, tool consent absent | Real approved API adapter/skill prerequisite seam when implemented | Exact xAI account/model/tool API required; consumer loader proof separate |
| 20,17,18 | 20 | Claude Code plugin package plus separate Messages skill container | Install/update/discover | Versioned valid package activates approved workflow; separate credential/tool preflight | Invalid manifest/path, name collision, disabled/missing server, product/API store conflation; container attempts external HTTP (must remain disallowed) | Real package parser and tool seam | Owned Code profile/plugin route; no organization publication in smoke |
| 21,16,18 | 21 | Consumer Muse versus Muse Code versus Meta Model API | Select/install or call | Exact target and documented mechanism; unsupported loader/plugin stays blocked | Model name treated as host, API tool support mistaken for UI install | Real supported adapter/wrapper seam after docs contract verified | Exact Meta product/account/deployment prerequisite; unsupported rows not passed |
| 22,16,18 | 22 | Mistral Vibe/Le Chat/API support descriptors | Preflight/install or tool task | Verified target-native route or labeled app loop only | Vibe feature propagated to Le Chat/API; API key mistaken for tool authority | Actual chosen adapter/loader seam when implemented | Exact target account/version; unsupported route remains unverified |
| 23,16,18 | 23 | Z.ai Coding Plan/model key versus coding-agent host | Preflight/activate | Entitlement separate from tool/skill loader authorization | Model-only key claimed as native plugin install; wrong host config | Actual documented host/adapter seam | Exact provider/host entitlement and network; no model call here |
| 24,16,18 | 24 | Hermes Agent skill/tool configuration versus model-only use | Install/discover/preflight | Real runtime discovers approved pack/tool; no model-only native claim | Missing runtime, arbitrary command/tool registration, malicious skill input | Real agent loader/tool seam | Owned NousResearch runtime version/profile; no installation here |

Distinct risks: SC-02 lost acknowledgement/durability; SC-03 tenant authorization;
SC-04 data fidelity; SC-05 node item/event semantics; SC-06 transport/session lifecycle;
SC-07 app compatibility versus listing; SC-08 model tool orchestration; SC-09 action
request duration; SC-10 bundle/pending interpretation; SC-11 checkpoint replay;
SC-12 capability/side-effect leakage; SC-13 untrusted source authority; SC-14 budget
and cancellation races plus commit-order versus display-clock checkpoint loss. Existing local tool tests cannot establish the new remote,
platform or durable mechanisms; reuse their guarded-source assertions where unchanged.
SC-01/15 protect planning and release truth rather than count as runtime coverage.

SC-16 adds instruction/tool authority separation; SC-17 adds host lifecycle/precedence;
SC-18 adds package/dependency safety. These are distinct from connector transport tests.
Skill live ceiling: one fresh install and one update in an owned disposable host profile,
three activation prompts, no external script execution or paid API call without child budget.
Missing host/account capability stays blocked. Unsafe package checks use controlled paths.

## State and compatibility contracts

- Durable work: submitted → queued → running → succeeded/failed/cancelled/timed_out.
  Exactly one terminal winner. Interrupted nonterminal work fails `service_interrupted`; terminal results and
  referenced evidence/catalogs are durable or explicitly expired. Atomic publication cannot expose a partially committed result.
- Session work remains session-owned and loses handles at disconnect/restart.
  Durable persistence is scoped separately and does not persist credentials in results.
- Missing, null, false, zero and unsupported remain distinct. Partial extraction
  cannot imply confirmed absence. Evidence identifiers remain bound to actual owners.
- Submission keys and event IDs solve different problems; job idempotency does not
  promise exactly-once delivery to third parties. Key expiry and dedup retention
  must be published and tested before enabling a polling trigger.
- Completion ordering is per-principal strictly increasing durable journal sequence,
  assigned atomically with terminal publication. `terminal_at` and opaque completion
  IDs are metadata, never checkpoint comparison keys. Restart preserves sequence;
  owner-bound cursors/checkpoints cannot cross principals. Retention advances an explicit
  prefix floor; scans older than it return gap rather than silently skip records.
- All seven connectors use approved capabilities. Platform-specific unavailable
  operations return explicit unsupported status; no hidden browser/LLM fallback.

## Red-test plan

Future test modules are proposed names, not existing tests:
`test_ecosystem_http_jobs`, `test_remote_mcp_auth`, `test_connector_contracts`,
`test_ecosystem_recipes`; each platform package owns its framework-native tests.
Expected red failures: missing durable transport/auth/adapter contract, not accidental
import or environment failures. Run and save intended red results after skeleton
reviewable seams exist and before implementing production behavior. This documentation
slice does not add stub APIs or run executable red tests.

## Unobservable behavior and synthetic mechanism plan

Future child author owns factories/driver, independent reviewer validates realistic
schemas and expected outcomes before execution. Provenance is `synthetic` or
`derived-offline`; never label controlled captures live. Seed `10102026` identifies
the reproducible scenario order; expected outcomes are requirement-derived.

Start with one saved extraction fixture (two products, one variant, three evidence
references) through real core→service→adapter paths. Then use ten distinct fixture
families: partial+replay, changed currency+uncertain match, escaped/duplicate IDs,
revoked identity+expired page, cancellation+commit, response-loss+idempotency,
restart+queued job, restart+published result, 429+deadline, unsupported export+path
attack. External service/clock/platform boundaries may be controlled; the mechanisms
under test (auth, persistence, budgets, serializers, trigger completion checkpoints, core extraction)
must remain real. No fixture may return its expected report as a fake mechanism.

## Bounded stress plan

Future execution only. First save one smoke before expansion. One sequential driver,
one worker, no model inference/parallel agents. Eleven fixture families × four explicitly predesigned
variants below = 44 planned scenarios; these are expected inputs/outcomes, not an
executed or generated corpus. Child authors must serialize them into a manifest
with exact fixture fields, crash locations and assertion IDs before execution; at most 25 operations/scenario (1,100 total).
At most 1,000 product rows/scenario, 4 MiB retained graph/job, 32 MiB service retained
fixture state and 512 MiB process RSS; 120 seconds/scenario, 10 minutes total. Source
responses ≤2 MiB and tool inputs ≤256 KiB. Platform-specified smaller limits win.


| Family / SC / distinct risk | Variant A: input → expected | Variant B: input → expected | Variant C: input → expected | Variant D: input → expected |
| --- | --- | --- | --- | --- |
| Partial+replay /04,14 / false absence | Complete2-item catalog → complete with2records | Capped1of2 → partial with1record, no removal | Replay same partial key → same job/no publication duplication | Partial then complete new key → two distinct immutable results, no retroactive page change |
| Currency+match /04 / invented comparability | Same ID/EUR price → supported identity relation with exact decimal | Same ID/USD versus EUR → currency preserved, no unconfigured conversion | Uncertain relation/conflicting support → uncertainty and both references retained | Currency missing versus empty → distinct supported/unavailable/invalid outcome per schema, no default fact |
| Escaped/duplicate IDs /04 / identity loss | Unicode/escaped valid ID → exact roundtrip | Same product across variants → distinct canonical variant ownership | Duplicate same record input → existing canonical dedup semantics, no fabricated extra item | Malformed identifier shape → invalid_argument before source fetch |
| Revoked identity+expiry /03,14 / leakage | Owner valid before TTL → authorized page | Other owner with cursor → deny without existence disclosure | Token revoked before next page → deny, no further data | Owner valid after result TTL → explicit expired, no hidden resubmission |
| Cancellation+commit /02,14 / two winners | Cancel while queued → cancelled/no catalog | Cancel before atomic commit → cancelled/no partial publication | Commit before cancel → succeeded remains succeeded | Repeated cancel after terminal → same terminal state/no new event |
| Lost response+key /02 / duplicate job | Ack lost then same key/body → same job | Same key/different body → conflict | Same key/other principal → separate owned admission, no cross-owner lookup | Result evicted within key lifetime → original job identity plus expired result, no refetch |
| Restart+queued /02 / phantom success | Crash before admission commit → no acknowledged job | Crash after queued commit → failed service_interrupted | Crash running before result commit → failed service_interrupted/no catalog | Explicit new key after interrupted failure → new bounded job, old terminal unchanged |
| Restart+published /02,11 / stale references or loss | Restart after commit → same owned catalog/evidence | Response lost after commit → replay same publication | Source crashes after emit/before checkpoint → stable-ID redelivery allowed, consumer effect once | Checkpoint persisted after emit then restart → resume without silent loss; retained gap explicit |
| 429+deadline /09,14 / retry storm | One429 with Retry-After inside budget → one bounded retry | Retry-After beyond remaining deadline → explicit unfinished/timeout, no sleep beyond cap |401 versus429 → no credential retry/resubmission on401 | Response lost during bounded poll → same checkpoint retry, no second submission |
| Unsupported export+path /12,18 / unauthorized effects | Export absent → unsupported/no artifact | Capability absent but source demands export → same unsupported | Path traversal/secret-bearing pack → reject before install/write | Future reviewed extension plus owner-scope → bounded owned artifact; otherwise scenario remains gated |
| Commit order+checkpoint /14 / late publication loss | A commits sequence41/timeT/idZ, scan ends41; B commits42/timeT/idA → next after41 returnsB despite lower ID | A commits9007199254740992/timeT; clock moves back60s; B commits9007199254740993/timeT−60s → next returnsB with lossless decimal-text sequence | Scan fixed high42, C commits43 while paging; response lost/retry → same retained page IDs within high42, next completed scan after42 returns43 | PrincipalA checkpoint41 used byB → deny; A checkpoint41 after retained_floor42 → explicit gap, never empty success |

One bounded fault injection per persistence/ack/checkpoint boundary demonstrates
assertions catch duplicate publication or disclosure; restore implementation before
passing runs. Stop on first invariant failure/resource overflow, save minimal case;
one diagnosed repair then affected rerun, otherwise record blocker. Save manifest,
seed/config, state transitions, measured count/time/bytes and stderr without secrets.
Reuse valid runs; do not count randomized copies as distinct coverage.

## Bounded live plan

Runtime child work only; this planning slice: live **not applicable**. Each child
must research exact limits and cite official dated sources before live execution.
Missing access means blocked live coverage, while mechanism checks remain required.

| Target | Prerequisite | Small live assertion and ceiling |
| --- | --- | --- |
| HTTP/jobs | Owned HTTPS deployment, two test principals, storage | One two-product job/restart/status/result; ≤12 service requests |
| Remote MCP | Owned TLS endpoint, registered auth test clients | List/call/reconnect plus denied scope; ≤12 protocol calls |
| n8n | Private/community node installation permitted, test workflow | One action plus two scheduled polls; ≤12 service calls |
| Claude | Installed local client; remote-connector-capable account/workspace | One local and one remote list/extract/result; ≤12 calls each |
| ChatGPT | Private MCP app/developer capability allowed by account/workspace | One installation/list/extract/evidence; ≤12 calls |
| OpenAI Responses remote MCP | API credential, budget, supported model/MCP access | ≤2 API requests and ≤6tools; complete only if remote orchestration/approvals fit, otherwise explicit unfinished with remaining coverage pending |
| OpenAI Responses function route | API credential, supported model, local sequential tool dispatcher | ≤5 API requests/≤6tools: submit→status→result→final needs4; one extra pending-status round permits5. Evidence live is separate, not squeezed into this smoke |
| Zapier | Developer/private integration access and connected test account | One action and two polls; ≤12 service calls |
| Make | Private app developer access and scenario execution credits | One scenario with action/search/two polls; ≤12 service calls |
| Pipedream | Private component/deployment rights and execution credits | One action and two source polls; ≤12 service calls |

API route budgets apply separately, each with120seconds and$1 ceiling. Cap each
request at512output tokens and6000input tokens; child must select available exact
model, count input using its supported tokenizer and verify worst-case price for
all planned calls fits$1 before any paid request. If exact model/pricing/counting
cannot be established, record blocked. Cap serialized tool content at12KiB/call,
page size2, retain evidence as handles. MCP-side hidden continuation/approval cannot
exceed request/tool budget: return unfinished and record missing live coverage.
Function smoke uses no evidence call: evidence continuation is controlled offline
acceptance, or a separately budgeted future live case. More than one pending-status
round stops unfinished rather than increasing request cap.

Use only an operator-authorized owned test shop or recorded fixture endpoint for
platform live proof: maximum two products, 120 seconds/case, one retry for transient
failure, no automatic repeated sweeps. Count core source requests too: ≤6 per case.
Credentials remain outside evidence. Stop on unauthorized access, mutation, spend
ceiling or repeated failure. One repair/retry maximum. Public marketplace review
is a separate external prerequisite, not a technical live test substitute.

Save future outputs under child `evidence/` and `verification.md` with versions,
principal aliases, redacted endpoint, request/cost counts and actual outcome.
Actual commercial price changes may remain unobserved; SC-04/14 synthetic transition
coverage must still run without claiming a real price change happened.

## Expanded provider verification (planned only)

SC19 targets native-vs-API authority/support confusion; SC20 targets actual plugin
packaging/skill+MCP lifecycle; SC21 targets distinct Meta host/model routes. All inherit
SC03/04/13/16..18 auth, data fidelity, source-injection and package safety. No new
runtime corpus is executed. The44case mechanism plan remains baseline; new host-route
smokes are separately bounded: one clean install/update if supported or one API task,
three activation prompts, two-product fixture, ≤6tools and120seconds; paid APIs require
exact account/model/rate/token/billing preflight with$1 ceiling, at most5API
requests/512output and6000input tokens per request; unsupported counting/pricing blocks
paid execution and further continuation returns unfinished. If unavailable/undocumented,
record unsupported or blocked target, do not fabricate native install proof.

SC22..24 add distinct model-versus-agent/consumer support boundaries and inherit bounded
host smoke/package/auth/evidence cases. No extra stress sweep; baseline44case mechanism
plan reused where applicable, target-specific expected fixtures must be reviewed before
future implementation. Meta native Code skill/MCP facts are retained but optional
implementation deferred. Current task performs docs checks only.
