# Bounded production research — 2026-10-16

Sources: local working tree; issue #25 via `gh issue view 25 --json title,body,state`.
No model inference, installs or external research sweep. These questions concern
repo-owned behavior, so current third-party documentation was unnecessary.

| Question / inspected source | Decision / rejected alternative / limitation |
|---|---|
| Persistent runtime? `tools/jobs.py`, `state.py`, `runtime.py` | Existing jobs/handles are session-memory/TTL scoped. Add opt-in durable maintenance store; persist portable records/evidence, not session IDs. Do not change #24 semantics or imply it already resumes |
| Existing domain path? `tools/domain.py`, `sources.py`, `context.py`, security guard | Reuse native guarded discovery/extraction and normalization, portable serialization, matching, evidence. Hook physical request accounting before transport dispatch with durable reservation; abstract tool-call counting cannot enforce crawl budget. No unguarded generic extractor fallback |
| Exact identity? `compare/identity_match.py`, `compare/catalog.py` | Reuse unique exact matches; every shared attribute disagreement may mean variant. Preserve guard. Demonstrate safe description-backed outdated spec; attribute specification differences still reported as review with before/after evidence |
| Evidence and freshness? `_resolution.py`, `_evidence.py`, normalization/capture paths | Reuse resolution policy/trust view; preserve conflicting/legacy-default distinctions. Do not infer supplier or manufacturer authority. Durable evidence must be complete enough for post-restart inspection |
| Category semantics? user steering + existing normalized attributes | Trusted finite hardware/footwear/generic profiles and validated explicit extensions. Role/unit differences are deterministic; no scraped policy and no silent size-system/GB–GiB conversions. Fingerprint profiles in cache and job |
| Crash guarantee? durable transactional intent/result design | SQLite transaction makes result/evidence/settlement atomic; external dispatch cannot be atomic with SQLite. Unknown intents retain reservation, no automatic redispatch. Explicit retry is new charged attempt. No external exactly-once promise |
| LLM integration? no mandatory existing provider | Injected optional advisory adapter, disabled default; narrow bounded context and output; no credentials required for tests. Known tokenizer/upper bounds and fixed price required before dispatch; unknown usage stays reserved. Adapter misreport/overrun documented as violation |
| Compatibility? existing tests `test_identity_matching.py`, `test_field_resolution.py`, tool suites | Preserve constructors, matching and existing schema names. Parent saved baseline: 86 passed / 0.47 s in artifacts/catalog-maintenance-agent/baseline-smoke.log; reuse rather than repeat |

Limits: one active runner/store; first implementation self-hosted local SQLite,
explicit finite inputs and bounded native tool responses. Current native per-call
limits remain upper bounds; maintenance budgets additionally accumulate across calls.
Absolute UTC deadline persists; a restarted expired job cannot obtain fresh time.
No durable distributed lease, multi-tenant service, external provider SDK or natural
language planner required. Single runner ownership must fail closed after process
loss/reacquisition and not rely solely on an in-memory semaphore.

No material product question blocks drafting. G1 must resolve any ambiguity in
initial field/profile coverage, reservation callback integration and evidence caps.
Actual session token counters unavailable to this author; no quota percentage or
estimated counter recorded. Output kept compact, saved artifacts reused; no local
inference or parallel agents launched by author.

G1 author clarifications: supplied baseline values are explicit caller assertions,
not generated observations; captured mode keeps strict evidence/freshness. Frozen
profile table and final finding precedence preserve all existing attribute conflicts,
including equivalent-unit raw differences. POSIX flock gives process-death release
for the local runner; no PID freshness heuristic/distributed lease. All resume and
unknown-retry actions now have explicit expected outcomes in spec/tests.
