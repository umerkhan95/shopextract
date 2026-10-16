# Local catalog maintenance

The opt-in maintenance API reconciles an explicit supplied or captured baseline
against permitted supplier sources and produces inspectable correction/review
reports. It never updates a shop. Exact deterministic cases use zero LLM calls;
uncertain identity/variants remain review cases. No paid service, API key, model
training or model process is required.

Run the offline native parser/matcher/persistence example:

```sh
PYTHONPATH=src python examples/catalog_maintenance.py /tmp/maintenance-example.db
```

Its source is labelled synthetic and HTTP is controlled. Production runs use the
same guarded native parsers and source-origin policy. There is no browser/LLM
extraction fallback. Supported native integration limits remain in force.

## Python API

```python
from datetime import datetime, timedelta, timezone
from shopextract.maintenance import Budgets, Goal, MaintenanceEngine, MaintenanceStore
from shopextract.tools import ToolConfig

store = MaintenanceStore("maintenance.db")
goal = Goal(
    baseline=({"external_id": "supplier-sku", "sku": "supplier-sku",
               "supplier_id": "https://supplier.example",
               "title": "Sensor", "description": "Current supplied specification"},),
    supplier_origin="https://supplier.example",
    product_urls=("https://supplier.example/products/sensor",),
    profiles={"supplier-sku": "hardware-v1"},
    fields=("description",),
    deadline=(datetime.now(timezone.utc) + timedelta(minutes=2)).isoformat(),
    budgets=Budgets(requests=20, products=100, tokens=0, cost_micros=0),
)
job_id = store.create(goal)
engine = MaintenanceEngine(store, tool_config=ToolConfig(
    allowed_origins=("https://supplier.example",)))
# Within your async function:
# report = await engine.run(job_id)
# report = await engine.resume(job_id)
# await engine.cancel(job_id)
# finally: await engine.close()
```

Supply an actual trusted supplier origin and identifiers. The example values do
not claim that a real source exists. Omit product_urls (empty tuple) for bounded
native sitemap discovery. `status`, paginated `report(offset, limit)` and job-scoped
`evidence(job_id, evidence_id)` inspect durable state. Explicit unknown-step retry
uses `await engine.retry_unknown(job_id, step_id)`; obtain step IDs from
`store.steps(job_id)`. `advisory_history(job_id, step_id)` retains prior publications.

Supplied mode compares only explicit fields in the input, labelled caller assertions;
no source URL/time is invented. Captured mode accepts complete existing
`product_to_record(product)` records and reuses their evidence/freshness. Legacy
scalar defaults do not become observed facts. A source authority or missing fact
cannot be inferred from a hostname or empty default.

## Category policies

Profiles are explicit trusted configuration. Shipped `hardware-v1` compares technical
fields while preserving RAM/storage/model variant risks. `footwear-v1` treats size,
size system, color and fit as variant fields. `generic-v1` makes no domain attribute
assumptions. Supported common fields are description/title/price/currency; hardware
adds RAM/storage/model/material/weight, footwear adds size/size_system/color/fit/
material/construction/weight. Attribute paths are `attributes/key` with JSON Pointer
escaping. No arbitrary JSONPath or scraped policy runs.

Only declared g/kg mass conversion and finite decimal normalization are supported.
US/UK/EU sizes and GB/GiB are not interchangeable. Existing matcher conflicts take
precedence: even equivalent mass text `1000 g` versus `1 kg` can remain review if
raw attributes conflict. Reports retain original/normalized values and the reason.
A different RAM, boot size or material is visible as a before/after review finding;
an unsafe identity is never promoted to a correction by an advisor.

Trusted custom profiles are passed once to `MaintenanceStore(custom_profiles=...)`
as a mapping of versioned names to `CategoryProfile`/`FieldRule`. Definitions freeze
with the job. Reopening with missing/changed definitions permits historical reads
but refuses execution. Restore the original definitions or create a new job.

## Recovery, limits and optional investigation

SQLite and a POSIX file lock support one local runner per canonical store path.
Queued/running/paused/partial/completed/cancelled/failed states are distinct. Process
loss releases the lock; next ownership pauses interrupted work and preserves intent.
Completed external steps are skipped; a dispatched attempt without a committed
outcome is unknown and stays charged. Resume never silently repeats it. Explicit
retry is at most attempt2 under the same original deadline, budgets, source/profile
and model/payload semantics. No external exactly-once guarantee is made.

Request budgets count physical requests, redirects and retries, across steps and
restart. Product/evidence/report limits, absolute UTC deadline and bounded attempts
also apply. Cancellation requests can be persisted while another runner owns the
lock; acknowledgement waits for cleanup. A cleanup timeout means the request is
stored and status must be checked again, not that work stopped successfully.
Source partiality and pending independent work remain partial after advisory success;
coverage is retained. Cache hits revalidate policy, preserve source time and spend
zero new external tokens/requests. Job evidence survives cache eviction.

An optional injected `Investigator` supplies a local/no-spend `bound(payload)` and
async `investigate(payload, reservation=..., timeout=...)`. Only unresolved eligible
cases receive capped selected fields/evidence descriptors, never the whole catalog
or raw HTML. The adapter must honor the accepted model/price/input/max-output/cost
bound, including any internal provider behavior. There is no bundled remote provider
or SDK configuration. Unknown usage retains the reservation. Reported overrun records
actual usage and a durable violation that halts further model dispatch; remote spend
is only bounded when the configured adapter/provider actually honors its contract.

Base findings are immutable. Separate advisory attempt publications compose the
latest committed advice with stable finding IDs and pagination. Failed publication
or cancellation preserves previous advice and uncertain charge. Matching, facts,
budgets, source permissions and category configuration cannot be changed by advice.

## CLI

```sh
python -m shopextract.maintenance --db maintenance.db create goal.json
python -m shopextract.maintenance --db maintenance.db --allow-origin https://supplier.example run JOB_ID
python -m shopextract.maintenance --db maintenance.db status JOB_ID
python -m shopextract.maintenance --db maintenance.db report JOB_ID --offset 0 --limit 20
python -m shopextract.maintenance --db maintenance.db evidence JOB_ID EVIDENCE_ID
python -m shopextract.maintenance --db maintenance.db cancel JOB_ID
python -m shopextract.maintenance --db maintenance.db --allow-origin https://supplier.example resume JOB_ID
python -m shopextract.maintenance --db maintenance.db --allow-origin https://supplier.example retry JOB_ID STEP_ID
```

Goal JSON uses the Goal fields above, an ISO UTC deadline, arrays for tuples and an
object for budgets. Custom CLI profiles use `--profiles profiles.json`, mapping names
to field-path mappings of `kind`, `role`, `normalization`. Allow-origins are separate
operator configuration; a goal/source cannot grant its own authority.

Existing Product/Variant constructors, extraction/matching/monitoring defaults and
ToolRuntime/MCP schemas are unchanged. Maintenance state is a separate opt-in local
store; session tool handles are not durable maintenance IDs. Unrecognized/prototype
SQLite schemas fail explicitly rather than being silently reset. The first public
maintenance schema is version1; preserve backups before future version migrations.
Distributed workers, tenant isolation, scheduling, approval/write actions and
connector delivery remain outside this feature.
