# Behavior and test design (before task breakdown)

Designed 2026-10-16; no new tests or production logic implemented at this stage.
Fixtures use tmp SQLite DBs, existing save_snapshot/Product/Variant/TrustContract,
fixed UTC times T0<T1<T2, distinct retained evidence and canonical identities.
Capture times must be controllable through fixture SQL, never inferred from the
wall clock. Use supplier-role evidence and actual field resolutions. Assertions
inspect report structure, stable IDs, publication counts and qualified lookups.

## Scenario matrix

| FR | SC | Fixture / action | Exact expected outcome and boundary | Offline / live |
| --- | --- | --- | --- | --- |
| 01,09 | SC-01 | Same anchored product renamed A->B, stable price; two products same title | Zero events; identity persists; later one product price 10->11 yields exactly one /price event with correct ID | Acceptance + existing identity tests; live identity repeat |
| 01,02 | SC-02 | Two stable variants reorder; one changes price 10->11, other unchanged; parent title changes | Exactly one variant price event with correct product/variant IDs, old/new evidence owner positions reflect each original snapshot | Offline; live if source variants captured |
| 02,04 | SC-03 | Each separately: stock true->false, pack_quantity 1->2, attributes warranty 12 months->24 months, pack_size 1 L->1000 ml, escaped key a/b~c x->y | One confirmed field event per leaf; no heuristic unit equivalence; path escaped as a~1b~0c; no new scalar warranty/pack_size | Offline only controlled values |
| 03,04 | SC-04 | Missing old/new fields; default scalar 0/USD/true; observed 0->0; invalid negative/NaN/infinity/bool price; null attribute; missing attribute key | No fabricated value or field-removal alert; diagnostic reason; observed valid equal zero gives no event | Offline parameterized |
| 03 | SC-05 | Equal-authority disagreement, stale/future evidence at capture, expired retained payload, unsupported legacy row; valid lower-authority conflict resolution | Ineligible cases no event and explicit reason; eligible selected differing facts produce one event preserving all candidates; qualified old/new selected references exact | Offline + captured live retained references |
| 04 | SC-06 | Decimal 10.00 vs 10; NFC/trim-equivalent attributes; reordered mapping; reordered list; bool false vs numeric 0 attribute | First three no event; list and typed bool/number differences emit events; no source mutation | Offline |
| 04,06 | SC-07 | Price 10 EUR->12 USD; EUR->USD with same price; missing currency on either side; variant price changes with inherited supported EUR | Currency change pending, no price event; unknown currency no price event; supported stable currency permits variant price event | Offline |
| 05 | SC-08 | Current partial/failed/unknown catalog omits 99/100 old records; complete=True with failure reasons is unhealthy; complete current but no recheck | No removal events. Partial absence diagnostic; complete absence produces pending candidates only. No mass false alerts | Offline |
| 05,06 | SC-09 | Complete old present, complete current absent, later complete recheck absent | Exactly one confirmed removal per missing identity; old supported record references + both coverage metadata; no fake new evidence | Offline |
| 05,06 | SC-10 | Removal pending then product reappears; or partial/unknown recheck absent; empty complete catalog recheck | Reappearance rejected; incomplete absence remains pending; explicit complete empty recheck confirms; unknown old support cannot fabricate price details | Offline |
| 05 | SC-11 | New product with previous complete vs partial/unknown, current partial but product supported; absent variant in complete catalog | Complete previous yields one confirmed addition; incomplete previous no addition; unsupported new record diagnostic; variant absence diagnostic only | Offline |
| 05,09 | SC-12 | Different/unknown scopes; missing snapshot; wrong supplier pair; reversed/equal IDs; duplicate identities or corrupt graph | Scope cases suppressed with reason and no events; invalid pair/identity/storage raises explicit error without partial writes; unrelated legacy rows are not parsed/backfilled/mutated, selected legacy rows without identities rejected | Offline |
| 06 | SC-13 | Price 100->50 / 100->200 / 100->50.01 / 100->199.99 / 0->1 / 1->0 | Exact boundaries and zero transitions pending; inside-boundary ordinary changes confirmed; no automatic network calls | Offline |
| 06,08 | SC-14 | Pending price or currency candidate; T2 equals new / equals old / third value / unsupported | Confirmed / rejected / rejected superseded_value / pending unverified_recheck; selected T2 evidence qualified; price recheck missing/different currency (including variant parent) stays pending with currency diagnostic; invalid/wrong-scope/not-later recheck fails atomically | Offline |
| 07 | SC-15 | Call same pair twice, close/reopen DB, same recheck twice; separate T0->T1->T2 values A->B->A and A->B->B | Same IDs, all confirmed events readable, new_events populated once only; reversals each publish, equal last step none; terminal candidate immutable | Offline restart fixture |
| 07,09 | SC-16 | Two independent SQLite connections race same comparison/recheck; injected transaction failure before publication; locked DB; direct-SQL >16MiB input; >10,000 entries or >16MiB report | One durable publisher; rollback leaves zero partial publication and retry succeeds; lock fails within bounded wait; overflow ValueError and zero partial writes; no callback delivery guarantee | Offline focused process/thread test, no local models |
| 08 | SC-17 | Lookup both event sides using IDs reused across records; prune after publication; mutate returned report | Qualified lookup unambiguous, URL/time/typed values exact; expiry explicit with stable report IDs/state; subsequent reload unchanged; stable event ordering | Offline; live retained source lookup |
| 09 | SC-18 | Run existing monitor, completeness, evidence, identity/portable tests and default CLI checks | Existing constructors, return types and default behavior unchanged; reliable API opt-in; no unexpected network | Offline regressions |

## Red-test plan

Create tests/test_reliable_changes.py with named tests mapped SC-01..SC-18 before
production logic. First concrete red case: supported same-identity price 10->11
returns one event with qualified old/new evidence, then a DB reopen replay returns
empty new_events. Initial failure must identify missing reliable report behavior
(not broken fixture/import elsewhere). After declaration skeleton, run all designed
acceptance tests and save bounded failure summary in verification.md plus
artifacts/reliable-change-23/red.log. No production implementation until G2/G3.
Existing small baseline was run by coordinator: tests/test_monitor.py and
tests/test_snapshot_completeness.py: 39 passed; saved baseline.log. This is existing
behavior evidence, not a new acceptance pass.

## Bounded live plan

After offline checks pass, sequential read-only requests to exactly
https://www.boardgamebliss.com/products.json?limit=2&page=1, a previously used
public endpoint. One initial request, save smoke result, then at most two repeats
(three requests total). Timeout at most 20 seconds per request, no retries, no
browser, redirects consume request budget, response capped at 1 MiB, retain at
most two products and four variants per product. No catalog traversal; explicitly
catalog_complete=false. Set HTTP/parser worker count to one, no inference.
Stop on 401/403/429, transport failure, oversize response or invalid JSON. Save
compact response metadata, retained evidence, DB/report IDs and assertions to
artifacts/reliable-change-23/live/ and summarize verification.md. Strip credentials.

Assertions: actual source evidence round-trips; canonical identities persist for
shared anchored records; report values/selected references agree with captured
responses; every removal remains unconfirmed under partial coverage; replay yields
no new events. If captures happen to differ, apply predeclared threshold/currency
rules, never assume a commercial change must occur. No captured difference means
live commercial-change detection is inconclusive, while the live persistence and
comparison smoke can pass. Source access blocked means live blocked, not passed.

Separately labelled controlled-offline tests may derive a fixture from the saved
live response and attach new fixture evidence at synthetic times to mutate price,
currency, stock and absence. Those prove pipeline handling, never actual live
commercial changes. Pure replay and mutations remain offline evidence. Network
acquisition must not occur inside reliable report generation or recheck.
