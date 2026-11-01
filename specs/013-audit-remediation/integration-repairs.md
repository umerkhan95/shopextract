# Final integration repair design — before code

First full main:2070pass/14fail/9setup errors236.62s; driver238.95s. Configured
fail-stop left oracle/maintenance NOT RUN. Exact IDs/traces in evidence/final-driver.
No production/tests changed during the run. No live gate opened.

Approved-contract compatibility repairs (no scope expansion):
1 Shared JSON-LD resolver must preserve an opaque CategoryCode.inCodeSet @id as
captured namespace, not treat it as missing product-node dereference. Only this
semantic property is exempt; dangling offers/mainEntity still unobserved/diagnosed.
Existing c09 distinguishes two namespaces and asserts original category evidence.
2 Native HTML results now truthfully mark catalog coverage unverified. Maintenance
may cache/replay validated positive per-page observations when the ONLY diagnostic
is catalog_coverage_unverified, preserving complete=false. Error/budget/parser
partial must not cache. Existing auth-on-hit, scope/policy/freshness keys, codec
validation, corruption-as-miss remain. Bump native cache version to invalidate old
complete=true cache entries. No new cache/model. Tests actual200 vs500 source,
cache row metadata and second-operation wire counts. This is local source-result
reuse, not proof of catalog coverage.
3 Catalog32MiB/1M-node allowance must not widen category artifact/publication1MiB
contract. _cli_categories owns1MiB; categorized export staging uses same cap;
common reader retains32MiB/1M. Existing1MiB artifact rollback tests unchanged;
old tests of COMMON reader move literal bounds32MiB/1M. Capability advertises1M
nodes (literal assertion). Native tree response/retention remains1MiB.
4 Tests injecting corrupt domain reply update list->products envelope path, same
invalid binding/rollback assertions. Legacy seeder mocks removed. CLI outcome
fixtures may bridge external worker-process boundary to actual _discover_local
with supplied MockTransport; parser/guard algorithm is never replaced. Owned
worker isolation continues tested by19 real-process/loopback cases. Direct live
worker and synthetic mechanisms are explicitly distinguished.
5 Existing assertions align approved canonical ordering by ID while checking ALL
record/evidence values, extra robots request/diagnostics (not dropping them), and
empty extraction error policy. No production behavior weakened to fit old tests.

Gates: existing failed cases are saved intended-red evidence. New2 actual cache
controls+capabilities literal assertion before repair. Independent amendment review
before source edits. Focused ALL failed nodes +newcontrols<=120s; fresh configured
driver with output-only -vv/short traces/durations, unchanged240/480 ceilings and
frozen source/tests. One diagnosed repair per blocker, no speculative sweep.

Cache implementation seam refinement: store.cache_get/cache_put also enforce
complete=true. Their optional keyword allow_page_observation defaultsFalse,
engine passes it ONLY for extract-mode eligible positive observations; shared
private predicate checks complete=false/nonempty product list/sole coverage
code. Engine validates portable/categorized payload before reuse as before.
Direct/default cache callers retain complete-only semantics. Diagnostic from
real file-backed spawned Harness confirms sole coverage code (cache-diagnostic.json);
one stdin probe was invalid for multiprocessing spawn and is not mechanism proof.

Resource reuse amendment BEFORE fixture change: first focused ALL failed nodes
passed45/40.99s, including actual32MiB/1M repeated old boundaries. Dedicated
money reader cases retain cap-1/cap/cap+1 actual32MiB checks. To avoid duplicate
large scans during the fresh full gate, the two old generic-reader mechanism
tests first assert DEFAULT32MiB/1M, then lower their local monkeypatched guards to
original1MiB/100k and retain exact original accept/reject assertions. No source or
driver limit changes; default full-size proof remains executable in money tests.

Functional review correction: optional partial-source flags must occur ONLY in
_source's extract-mode get/put. Advisory _advise get and advisory publication put
remain original complete-only calls; mode/page_only are out of scope there.
Existing known-usage advisor control exercises actual injected boundary publication
and subsequent exact cached reuse, no model/provider launched. Save red then green;
no broad cache replacement or default behavior change.

Fresh full driver source-frozen timed out239.06s at93% (all completed nodes pass),
oracle/maintenance NOT RUN. Live still blocked by offline gate. One bounded
cProfile on real Woo100 later404 pipeline/CLI control,60s process cap, capped
threads, records existing assertions and top cumulative source costs before any
performance decision. No limit increase/skips, no inference. Profile identifies
mechanism; no fixed performance promise or guessed bottleneck.

## Maintenance family integration amendment — design before source change
Driver3 main2099pass231.66s, oracle24pass67.09s; maintenance101pass5fail40.40s,
total344.30s (all ceilings respected). Four failures share inferred source_partial
masking durable model budget_violation/cost_budget/model_usage_unknown. Only the
INFERRED generic source_partial reason ranks below actual model stop; explicit
source deadline/cancellation/budget/error and pending-work reasons retain priority.
State remains partial and coverage.source_complete remainsFalse, no refunds or
extra model dispatch. Existing retry/resume durable usage tests retain all asserts;
add explicitFalse coverage checks. Positive control successful advisory retry must
still report source_partial when no current model stop remains. Ownership is one
completion reason-selection expression in MaintenanceStore; no engine/cache changes.
Fifth failure is expected required robots first request: native workflow fixture
explicit robots404 and asserts robots THEN sitemap, one robots fetch, exact
requests accounting and same proposed correction. No fake model/process provider.
Save focused red/control then independent amendment review before source repair.
