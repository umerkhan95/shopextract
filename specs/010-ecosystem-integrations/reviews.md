# Independent review ledger

## G1 — 2026-10-24 — changes required

Reviewer: integration_reviewer (separate from integration_author). Scope: documentation-only behavior, tests, tasks, bounded research, epic and seventeen issue bodies. No runtime implementation, host installation or GitHub mutation was performed. No G2/G3/final verdict is supplied.

Reviewed artifact tree SHA-256: `9277c788a9b5cd50a0796cf1c53e5725c82bdc1d16b3fe0594d8543d7738544b` (25 files, excluding reviews.md; relative paths sorted; each path + NUL + bytes + NUL). Key digests:

- spec.md: `5118d79c8fa157b4e3d9f05a07b275f1245673aaa58f033580b45779a216f590`
- test-design.md: `f92f99ca5dbfffc8aabcf8c419d021308e93bf03a0a4f50ea9a119566268e337`
- research.md: `110751ef335487d57dd423d924abf8aad1e54fd9bdc747fa9ee0989381ac905b`
- tasks.md: `43fe8cf9ebebade81449f9f2371bbb47ae1d8d39ff8a22716d8d5a5dda78e181`

### Findings

| ID | Severity | Finding / required disposition | Status |
| --- | --- | --- | --- |
| G1-01 | P2, blocking | spec.md SC-11 requires checkpoint-interruption replay to suppress duplicate downstream emission, whereas test-design SC-11 and INT-09 explicitly allow at-least-once redelivery across emit/checkpoint crashes. Stable IDs and a 100-ID platform cache cannot establish crash-safe exactly-once external emission. Align SC-11 with the detailed contract: retained events are not silently lost, replay preserves identity, duplicate delivery may occur across the documented crash window, and authoritative service publication remains unique. Keep a separate ordinary repeated-poll dedup assertion within stated retention. | Open; author revision and reviewer recheck required. |
| G1-02 | P2, blocking | INT-06 and test-design live plan cap the API smoke at two API requests, yet the function route calls one tool at a time and acceptance requires submit/status/result continuation (and INT-06 controlled acceptance adds evidence). Sequential application-executed function outputs require additional model requests to obtain the dependent calls; two requests cannot prove the advertised complete flow. Provide route-specific bounded live plans with a feasible maximum, or explicitly limit the two-request smoke to unfinished-state behavior and keep full continuation live coverage pending. Preserve the tool/cost ceilings and separate statuses for MCP versus function routes. | Open; author revision and reviewer recheck required. |
| G1-03 | P3, nonblocking clarification | The stress plan says four declared variants per fixture family, but no exact four variants are enumerated. Before child fixture generation/execution, record variant inputs, risk, expected terminal outcome and assertion mapping. Existing boundary lists provide good ingredients; they are not yet a 40-case executable manifest. This is future verification detail, not a demand to execute runtime tests in this docs slice. | Child design prerequisite; make the boundary explicit in plan/tasks. |
| G1-04 | P3, nonblocking clarification | INT-11 ticket depends on INT-10 recipes, while tasks.md lists only selected transport dependencies. Clarify that it consumes the approved enabled recipe subset and does not wait for all platform release verification, or align the task table dependency. Local #24 skill route should remain independently usable as described. | Author clarification recommended. |

### Checks and source truth

Reviewed repository workflow/constitution, current agent tool docs and runtime/job/SDK seams, all requested planning artifacts and issue bodies. Requirements/scenarios and seventeen ticket scopes are traceable; read-only merchant boundary, durable local effects, owner isolation, retention gaps, unsupported capabilities and separate private/public states are explicit. Existing stdio runtime remains ephemeral and MCP dependency is `mcp>=1.30,<2`; the plan does not falsely claim remote support or durable local handles.

Reused sources.json and compact research; only three material official pages were spot-fetched. Official OpenAI documentation explicitly confirms ChatGPT/Codex plugin skills containing SKILL.md, so INT-13 is source-supported rather than presumed unsupported: https://developers.openai.com/plugins/concepts/skills . MCP 2026-07-28 transport overview confirms per-request body metadata and stream-close cancellation: https://modelcontextprotocol.io/specification/2026-07-28/basic/transports . Keeping 2025-11-25 as a conditional candidate with host/SDK negotiation tests is honest; neither version is claimed proven compatible. The function-calling flow requires application execution followed by an additional API request for outputs/continuation: https://developers.openai.com/api/docs/guides/function-calling . Exact host entitlements and live compatibility remain unverified as recorded.

No broad research, model inference, package installation or runtime tests. Actual session token counters unavailable; this bounded review reused saved material. Verdict is changes required solely for G1-01 and G1-02; downstream gates remain pending.

## G1 re-review — 2026-10-24 — pass

Reviewer: integration_reviewer. Reviewed the changed spec/test-design/tasks/research, INT-06/09/10/11 and planning-checks against the original findings. No new research, runtime execution or GitHub changes. Reviewed artifact tree SHA-256: `1804f0389281c7c0c2848ae8d530be2db6ab7599633fee9e16919666df35d94b` (25 files, excluding reviews.md, same digest algorithm as above).

| Finding | Actual disposition | Result |
| --- | --- | --- |
| G1-01 | SC-11, scenario matrix and INT-09 now distinguish ordinary retained-window poll dedup from stable-ID at-least-once crash replay. No silent retained-event loss; authoritative publication remains unique. Downstream idempotent-consumer example has an explicit separate ledger responsibility. | Resolved. |
| G1-02 | Function smoke now allows at most five API requests: three sequential calls plus final response take four requests; one extra pending-status round fits five. Remote MCP retains two-request ceiling and records unfinished if orchestration/approval cannot fit. Tool/time/token/cost caps, pricing/count preflight and separate evidence-live status are explicit. | Resolved. |
| G1-03 | Ten risk families now enumerate four input/outcome variants each. Exact fixture fields/crash locations/assertion IDs remain an explicit child manifest prerequisite before generation/execution; the document does not claim an executed corpus. | Resolved at planning scope. |
| G1-04 | INT-10a approved recipe definitions precede INT-11; INT-10b consumes enabled implemented rows for final compatibility/release. Tasks and ticket agree; local #24 remains a viable independent route. | Resolved. |

No remaining blocking G1 finding. Pass applies only to the documentation planning scope and reviewed revision; child contracts still require their own design gates and executable evidence. G2, G3 and final remain pending and are not approved here.

## G2 — 2026-10-24 — changes required

Reviewer: integration_reviewer. Reviewed new plan.md/skeleton.md against G1-approved spec/test design/research/tickets. Documentation declarations only; no source stubs, runtime, model calls or new research. Artifact tree SHA-256: `c0325ba16fc136a946cb0de23c7b715bc85563357594d2116d17fbbf2b3310e8` (27 files excluding reviews.md, same algorithm).

| ID | Severity | Finding / required disposition | Status |
| --- | --- | --- | --- |
| G2-01 | P2, blocking | The completion scan fixes a high-watermark and filters later scans using descending `(terminal_at, completion_id)`, but neither field is specified as monotonic in publication order. A completion committed after the scan can share its terminal timestamp yet sort below its high-watermark because its opaque ID is lower; clock regression creates the same loss across timestamps. Such a completion is excluded by a later `after` checkpoint despite remaining retained. Declare a commit-ordered monotonic journal position (or equivalently enforce a strictly increasing ordering tuple), separate display timestamps from checkpoint ordering, and explicitly require a late same-timestamp completion plus backward-clock fixture. Descending newest-first platform arrays may still be produced while using a monotonic high-watermark. This is an ordering invariant, not merely cursor token encoding. | Open; author revision and reviewer recheck required. |

The remaining declarations are consistent at planning scope: server-derived Principal and grants; credential-origin isolation; atomic job/key admission and graph/evidence/publication persistence; unchanged local session lifetime; honest side effects; explicit scope/owner/error boundaries; immutable owner-bound result paging; at-least-once external delivery; acyclic dependency waves; actual host-specific skill wrappers and capability preflight. Final framework, storage, schemas, auth registration, protocol/client and package pins are honestly preimplementation child gates. None is reported implemented. G1 remains approved except the newly identified ordering interaction requires an additive behavior/test clarification. G3 and final remain pending.

## Affected G1 and G2 re-review — 2026-10-24 — pass

Reviewer: integration_reviewer. Reviewed revised FR14/SC04/SC14, test contracts and eleven four-variant families, research, affected service/polling tickets, plan/skeleton and author-check records. Artifact tree SHA-256: `9c7e750aa2e7b8e5a57a525179fbb5358d21e18a0b5f555a0b128c58d34a5355` (27 files excluding reviews.md; same algorithm). No runtime checks, new research or GitHub changes.

G2-01 resolved: publication order is a strictly increasing per-principal sequence allocated in the same serialized transaction as terminal publication. Counters survive restart; owner/epoch-bound checkpoint and fixed H scan exclude new commits only until the next scan. Timestamp/opaque-ID order no longer filters out new publication. Retention advances a prefix floor and interrupted scans report explicit gap if unconsumed records are pruned. Decimal-text sequences and exact integer comparison preserve values above JavaScript safe integers.

Affected G1 additions pass: the four new cases declare late equal-time/lower-ID publication, backward-clock publication with sequence 9007199254740993, fixed-watermark response-loss resume with concurrent later publication, and owner/retention-gap behavior. They target the uncovered ordering/precision/recovery interaction. The new plan is 44 scenarios and at most 1,100 operations; execution and exact child fixture manifests remain future work.

Affected G1 verdict: pass. G2 verdict: pass for documentation declarations only. Prior G1 findings remain resolved; G2-01 is closed. Exact schemas, storage pins, token encoding and live compatibility retain their named child gates. G3 and final remain pending.

Nonblocking editorial note: research.md's earlier G1-03 paragraph still says ten families while now saying 44 cases; the later G2 revision correctly explains the 40-to-44 increase and test-design correctly has eleven rows. Align that earlier prose when editing the next artifact set. Historical author-check counts are identifiable as prior-stage records and do not establish current execution.

## Expanded G1 — 2026-10-24 — pass

Reviewer: integration_reviewer. Reviewed expanded behavior/test design/tasks/research, sources register and INT-18..25 plus changed INT-12. Artifact digest: `4a1bb9db4dd3d6300ea9c70eb83fd768746926985d1d3180ddf7869cc5616ed5` (40 files excluding reviews.md; relative paths sorted, path + NUL + bytes + NUL). Reused the saved 60 primary-source records and compact read scopes; no new broad research or spot-fetch was needed. No runtime or model calls.

FR/SC coverage is now 24 contiguous requirements/scenarios and 25 ticket bodies. Grok Build native skills/plugins, grok.com MCP and xAI API payloads are separate; unsupported OpenAI approval parameters cannot be copied. Claude Code plugin, product/Managed Agents and network-disabled Messages skill container are distinct. Meta Code skill/MCP support is affirmative but optional/deferred, exact plugin packaging and personal Muse/Model API contracts remain explicitly unverified. Mistral Vibe Code experimental plugins are separate from Work/API; GLM model entitlement/API MCP is separate from external Claude host and unresolved ZCode loader; Hermes Agent native/portable packaging is separate from model-only access. No undocumented native loader is presented as achieved support.

New SC19..24 identify distinct host/provider/authority confusion and package/lifecycle risks, inherit relevant adverse auth/source/package/data cases, and retain bounded future host/API verification. The 44-case service mechanism design remains planned; it is not falsely counted as execution or proof for every new loader. INT18a→19→18b, INT21a→22→21b and INT10a→11→10b are acyclic. No blocking finding. Affected G1 passes at documentation scope.

## Expanded G2 — 2026-10-24 — pass

Reviewer: integration_reviewer, after expanded G1 pass above. Artifact digest: `4a1bb9db4dd3d6300ea9c70eb83fd768746926985d1d3180ddf7869cc5616ed5` (40 files excluding reviews.md; relative paths sorted, path + NUL + bytes + NUL). Reviewed plan/skeleton provider additions against the accepted behavior/tests/tickets.

Thin host wrappers consume approved tool/skill boundaries and retain provider-specific request/manifest/permission/lifecycle contracts. Unknown schemas remain named child blockers, not fabricated declarations. Current local #24 remains independent of remote HTTP/OAuth; the one proposed next-session Claude Code local slice consumes only INT20/relevant12/minimal11 subset. The shared durable service declarations preserve server-derived principals/scopes, atomic job/evidence publication, session-handle remapping, explicit expiry, monotonic per-principal commit sequences, snapshot checkpoints/prefix-gap behavior and lossless decimal sequence 9007199254740993. No new tool or privileged scope is granted by native plugin metadata. No blocking finding; affected G2 passes for declarations only.

## G3 — 2026-10-24 — pass

Reviewer: integration_reviewer, after expanded G1/G2 pass above. Artifact digest: `4a1bb9db4dd3d6300ea9c70eb83fd768746926985d1d3180ddf7869cc5616ed5` (40 files excluding reviews.md; relative paths sorted, path + NUL + bytes + NUL). Reviewed components.md and refined declaration consumers/ownership/error/lifecycle boundaries.

Existing domain/security/normalization/evidence/reliable-change paths are reused; ephemeral runtime/state/jobs are explicitly unsuitable as shared durable multi-principal storage. New persistence/journal/auth/facade components have concrete consumers and clear ownership. Native codecs/loaders retain platform rules, including n8n dependency restrictions and Hermes partial-load semantics. No speculative universal plugin framework or copied commerce engine is introduced. Local-only Claude Code packaging does not require building unused remote components. No blocking finding; G3 passes at documentation scope.

## Final content review — 2026-10-24 — pass

Reviewer: integration_reviewer, after the ordered expanded G1/G2/G3 reviews above. Artifact digest: `4a1bb9db4dd3d6300ea9c70eb83fd768746926985d1d3180ddf7869cc5616ed5` (40 files excluding reviews.md; relative paths sorted, path + NUL + bytes + NUL). Scope is reviewed planning content and issue-ready bodies, not runtime delivery, actual issue creation, install or publication.

Independent text/JSON checks executed in this review: 60 unique source URLs, 25 ticket files, 24 contiguous FR/SC IDs, epic ticket-file references, balanced fences/trailing-whitespace checks and precision-contract presence all passed. Semantic review covered source truth, capability gaps, merchant-read versus local effects, auth/owner/secret boundaries, stable replay/expiry/cancellation, practical per-host scope, compatibility states and next-session handoff. Historical G1-01/02/03/04 and G2-01 remain resolved. The earlier family-count editorial note is fixed in research.

Compatibility matrix, verification and handoff distinguish researched/documented from implemented/mechanism-tested/private-live/submitted/accepted. No runtime tests, skill activation, model inference, account configuration or public release occurred. Meta remains optional/deferred; unsupported/unverified targets are honest future gates. Handoff proposes exactly one bounded Claude Code local plugin+skill implementation slice, not started, with existing #24 and no remote prerequisite.

Final content verdict: pass; no blocking content findings. Actual GitHub epic/subticket mapping and delivery receipts remain coordinator work. This pass permits mechanical addition of actual issue IDs/links, receipts and truthful review/status updates without repeating content review, provided scope, requirements, contracts and issue bodies are not substantively changed. It does not permit marking runtime work or live compatibility complete. Material content changes invalidate affected gates.

Nonblocking editorial observation: the baseline trusted-recipe consumer row in components.md still refers to six skill hosts, while its additive-host section correctly extends the consumers. Treat six as baseline or clarify on the mechanical status update; no architectural gap results. Actual session token counters unavailable; review reused saved sources and ran bounded docs checks only.
