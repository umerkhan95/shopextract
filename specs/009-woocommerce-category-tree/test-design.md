# Behavior and test design (before task breakdown)

## Scenario matrix
All cases are new traversal/bridge coverage; existing Woo product-category adapter tests do not exercise per-store pagination, tree topology or transport. Each row names its distinct risk rather than adding random variants.

| FR | SC / fixture | Exact expected outcome / distinct risk | Offline check | Live assertion |
| --- | --- | --- | --- | --- |
| 01/02 | SC01: three nodes across two pages, distinct capture times | Root/child edges supported by own page facts; no product memberships synthesized | `test_tree_pages_preserve_scope_evidence` | Endpoint returns observable node IDs/parents |
| 01/04 | SC02: zero total + empty page; headerless first empty/short page plus page-two confirmation; persistent absent headers | Consistent zero coverage confirms empty; valid page-two totals can confirm headerless first page; persistent missing/invalid headers remain partial | `test_empty_requires_coverage` | Compare headers/body; access permitting |
| 02/03 | SC03: missing/null/0/false/negative IDs; string IDs; escaped labels/slugs | Independent facets survive malformed siblings; root 0 differs from unknown; no HTML normalization of labels | `test_tree_facet_states` | Synthetic malformed cases only |
| 03 | SC04: orphan/self-edge/2-node cycle/9-level chain | Distinct missing-parent, self-parent, cycle and depth reasons; no inferred root | `test_tree_topology_adversaries` | Synthetic only; do not mutate stores |
| 03/04 | SC05: duplicate identical/conflicting IDs, repeated full page, totals drift, reordered pages | Conflicts retained, loop stops, partial coverage; reorder preserves graph semantics | `test_pagination_mutation_and_duplicates` | Mutation remains unobserved unless naturally captured |
| 04 | SC06: 403/404 first page; later timeout; bad JSON/list/object | Unavailable vs malformed vs partial explicit; valid prior facts survive; no deletion claims | `test_tree_failure_retention` | Public availability only |
| 05 | SC07: zero and below/at/above calls/items/bytes/depth/deadline | No budget overrun, terminal fit completes only if justified; nonidentity compressed payload rejected before decoding | `test_tree_budget_boundaries` | Only small smoke; resource extremes synthetic |
| 06 | SC08: local/private IP, redirect chain, changed DNS, cross-origin, cancellation | Guard before each request; redirect/failure charged once; no credentials leakage or subsequent request | `test_tree_guard_and_deadline` | Unsafe cases controlled transport only |
| 07 | SC09: membership vs index-only; exact vs similar label; stale taxonomy version | Only supported membership + trusted matching rule maps; version mismatch fails validation/unavailable | `test_tree_mapping_evidence_boundary` | No live classification accuracy claim |
| 07/08 | SC10: two stores same ID, unknown version, ambiguous target; 999/1000/1001 targets | Scoped decisions isolated; explicit unknown-version opt-in; ambiguity preserved; registry cap unchanged | `test_tree_mapping_scope_version_limits` | Offline deterministic |
| 08 | SC11: feature off; partial index + limited product terms + maintenance report | Legacy output identical; companion cap independent; no false removal/reclassification | `test_tree_opt_in_maintenance_compatibility` | Existing public extraction regression if applicable |

## State and compatibility contracts
- Proposed outcomes: complete/partial/unavailable/malformed plus coverage reasons; final names resolved at G1/G2 without erasing distinctions. Data state and transport outcome remain independently inspectable.
- Initial state unrequested -> acquiring -> terminal result; only explicit fresh invocation restarts. No hidden retry, resumable cross-run merge or fabricated single capture time.
- Empty is confirmed only with success and consistent zero coverage evidence. Nonempty traversal completion records headers/page range/times and no atomicity guarantee. Headerless first short/empty page receives at most one confirmation page; page two must provide consistent total headers or stop partial. Completion requires expected page lengths and raw/distinct-ID counts matching totals.
- Parent relations and memberships remain separate observations. `index`/`parent_edges` are already excluded by exact mapping; preserve that invariant.
- Fact retention counts raw conflicts as well as deduplicated nodes; bytes bound evidence even when duplicates dominate. Reject/stop before exceeding cap, retain prior accepted pages and truncation reason.
- Reordering invariance compares the semantic graph/facet-conflict projection only; page URLs, capture times, response pointers and attempt ledgers remain faithful to their actual input order. Identical duplicates alone do not create a conflict; repeated-page/nonadvancing traversal does create partial coverage.
- Root depth = 0; depth 8 accepted, required expansion to 9 flagged. Do not recursively expand arbitrarily deep/cyclic input.
- Zero budget means disabled work for that resource (no calls at zero request/time/byte/item/page capacity); zero depth permits roots; invalid negative/bool/noninteger settings fail validation before I/O. All partial states remain ineligible for absence claims.

## W02 additional risk cases (before implementation)
- Header suppression is normal upstream: headerless short first page + empty
  second with matching totals completes; no second headers remains partial;
  contradictory second totals or an unexpected nonempty confirmation is partial.
- Totals/pages must agree mathematically; one-sided/negative/nondecimal headers,
  count mismatch, duplicate IDs and malformed facets cannot prove completion.
- Real pinned-backend connector receives checked numeric IP despite DNS changing
  between preflight/connect; mixed public/private answers deny before connecting.
- Blocked body plus deadline/cancel cancels and awaits the fetch and closes the
  stream; event checks between pages alone do not cover this failure mode.
- Membership lookup requires a matching bound observed native-ID fact, accepted
  conversion with equal normalized value and nonempty source evidence (existing
  mapping support semantics). Missing/rejected/mismatched/evidenceless facts
  return unsupported; foreign scope remains scope_mismatch even with weak facts.
- Same-merchant membership ID lookup links only captured memberships; foreign
  scope, missing ID and conflicted tree declarations return explicit unresolved
  outcomes, while original companion observations remain byte-identical.
- Whole tree serialization must account evidence/derived records and reject
  oversized/tampered envelopes. Duplicate facts must consume input/byte budgets.
Acquisition selected scope includes SC01–08/11 and membership lookup. Optional
Shopify bridge SC09/10 is deferred; existing exact mapping regressions remain.

## Red-test plan
After reviewed skeleton, implement the named acceptance tests against public proposed acquisition/bridge entry points. Save expected missing-behavior failure (absent API or explicit NotImplementedError) in `verification.md` before business logic. Do not count import/fixture bugs as intended red evidence.

## Unobservable behavior and synthetic mechanism plan
Author: feature implementation author; independent coverage reviewer: separate workflow reviewer. Fixtures are labelled synthetic, seed `00920261024`; use `.example` origins and fixed page capture times. Prefer deterministic table factories over random corpus.
Exercise actual guarded fetch, parsing, normalization, evidence construction, topology resolution, existing exact mapping, portable persistence/reload and maintenance integration. Replace only external transport/clock using controlled fixtures; never replace topology or mapping logic.
Replay serialized partial/conflicting result and confirm facts, coverage and scoped identities survive; fresh invocation after failure may succeed but never silently merges stale snapshots. Include transport exhaustion + duplicate-page replay and partial index + product cap as distinct interactions.
Record actual entry point names after G2, fixture manifest/provenance, canonical outputs, command and compact failure reproduction. No fixture generation or check execution in this planning slice.

## Bounded stress plan
Start with one saved three-node smoke; then exactly 24 deterministic cases sequentially: 6 topology (orphan, self, cycle, depths 7/8/9), 6 pagination (repeat, conflict, reorder, total drift, exact terminal cap, later failure), 8 budgets (request/item/decoded bytes/retained bytes, at and above), 4 interactions (duplicate + byte cap, partial + replay, two scopes + same ID, cancellation + redirect).
Separate small acceptance cases cover below limits, zero and malformed configuration. Stress seed `00920261024`; max fixture categories 1,001, individual decoded fixture <=2 MiB + 1 byte, total fixture retention <=16 MiB; one worker, 60-second driver deadline, 256 MiB process-memory ceiling, no inference. Stop on first failure, save minimal case; one diagnosed repair then affected rerun within declared limit or record blocker. Confirm a critical absence assertion detects a deliberately injected partial-to-complete fault, then remove the fault. Planned counts prove bounded cases, not production capacity.

## Bounded live plan
After offline success and target selection, save exact public store URL/domain and access prerequisites before execution. Start one read-only smoke with <=3 HTTP attempts total (including redirects/failures), `per_page=2`, <=6 nodes, <=256 KiB decoded/page, <=768 KiB retained, 10 seconds overall, no retries, one sequential process.
Assert query `hide_empty=false`, returned identity/parent field interpretation, header coverage and per-page evidence. Stop on block/challenge, redirect outside policy, unsafe destination, malformed response or limit. Save redacted `evidence/live-smoke.json` and summary before expansion.
Only if smoke passes, one separately saved run <=10 attempts/1,000 categories/30 seconds using reviewed ceilings; do not repeat completed checks without changed input/contract. 403/404/access absence is blocked/unavailable, never empty. Natural mutation may remain inconclusive. Execute synthetic mechanisms regardless of inaccessible rare live cases; report live observation separately. No probes/tests executed yet.

## W08 distinct uncovered interactions (before repair)
- Opaque string ID `0` can be a real category under existing adapter semantics.
  Only raw integer parent 0 declares root; string parent `0` references that node.
  Retain root-vs-reference distinction during conflict comparison and replay.
- Recomputed-digest same-origin page path/query tampering and forged non-200
  attempt cannot establish category provenance. Retained pages must use the
  fixed installation-relative category route (optional trailing slash), exact
  page/per_page/hide_empty=false/order query and a matching successful attempt.
  Same-origin redirects preserve this fixed route/query; other paths/query
  changes are denied before their next wire call. Track actual guarded-hop URL
  through accounting rather than relying on outer HTTPX response.request.
- Store URL wrong scalar/container types raise CategoryError before URL parsing
  or I/O; they are caller contract errors, not transport outages.

## W10 coverage-review additions (before execution)
- Exact full canonical retention threshold is found through the public API with
  a bounded black-box bisection in [0, 8192], at most 17 total invocations including
  threshold-1/threshold/threshold+1 probes. Do not call the admission/reservation
  helper as expected oracle. All three raw bodies fit; below threshold refuses
  the page, at/above retain and complete, and each resulting canonical envelope
  fits its configured cap. Print the discovered threshold and observed sizes.
- Redirects changing fixed category path or hide_empty query are denied before
  destination wire call. A legitimate same-origin trailing-slash redirect must
  retain its actual guarded-hop URL/hash and round-trip with that provenance.
- Mixed public/private DNS answers deny the entire resolution before wire I/O,
  independently of the already-covered all-private and later-rebinding cases.
These strengthen acceptance coverage without changing the original 24 stress
slots. Their execution waits for the coordinator's regression process to finish.

## Independent live-oracle sensitivity supplement
Before executing the live driver, `tests/test_woo_tree_live_oracle.py` exercises
its independent header/page/raw-ID count oracle against real acquisition receipts.
Risk: a status-only live assertion could accept an implementation that wrongly
publishes partial data as complete/empty. Expected: complete and correctly
request-limited captures pass; a deliberately injected partial-to-complete/empty
fault and totals disagreeing with raw row counts are rejected. This challenges
the verification mechanism itself without modifying production code. The two
small controlled cases run in the focused offline suite; no new stress slot.

## W14 final-review repair design (before production edits)
- Native membership support must inspect candidate fact alignment independently:
  raw_value, its conversion source_values and resolved retained source pointer
  must agree, and the inspected raw ID must convert to the asserted normalized
  native ID. Raw-only tamper, source_values-only tamper, changed retained value
  and changed resolving pointer are distinct adverse fixtures; each returns
  unsupported without mutating input. Scope mismatch still takes precedence.
  A separately valid native-ID fact can support the term despite an invalid
  sibling, and unrelated malformed label evidence does not suppress a valid ID.
  Validation is local to candidate native-ID facts, not a global observation
  rejection or change to existing shared mapping behavior.
- Malformed IPv6 initial URL `https://[broken` is an unavailable unsafe_url
  result, with zero DNS/wire/attempts. Its bounded diagnostic may round-trip
  because no captured page claims that malformed URL as source provenance.
- Valid UTF-8 body containing escaped lone surrogate `\ud800` is malformed JSON
  for the canonical UTF-8 capture contract: first page yields malformed with
  malformed_json; later page yields partial and retains exactly prior valid
  pages. Charge the actual attempt, retain no malformed page/fact and never
  normalize to replacement characters. Both terminal diagnostics round-trip.
Executable fixtures: `tests/test_woo_tree_final_edges.py`. Save intended red
before affected design review and one diagnosed local repair per blocker.
