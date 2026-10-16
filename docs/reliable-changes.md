# Reliable change reports

`shopextract.monitor.reliable_changes` compares explicit saved snapshots using
canonical product and variant identities. It reports supported price, currency,
stock, pack quantity and attribute changes, with qualified old/new source links.
Warranty and pack size use explicit `attributes` keys; no unit or warranty parsing
is implied. A title rename or variant reorder does not become a membership change.

```python
from shopextract.monitor import reliable_changes, get_evidence

report = reliable_changes(
    "shop.example",
    previous_snapshot_id=old_id,
    current_snapshot_id=new_id,
    db_path="snapshots.db",
)
for event in report["new_events"]:
    print(event["event_id"], event["field_path"], event["old"], event["new"])
    for reference in event["new"]["references"]:
        for evidence_id in reference["evidence_ids"]:
            source = get_evidence(
                evidence_id,
                snapshot_id=reference["snapshot_id"],
                record_key=reference["record_key"],
                db_path="snapshots.db",
            )
            print(source.status, source.evidence.source_url if source.evidence else None)
```

Obtain snapshot IDs from `save_snapshot(products, domain, metadata=..., db_path=...)`.
The older asynchronous `snapshot()` returns a product count, **not a snapshot ID**.
Preserve extraction `observation_scope`, `catalog_complete` and
`incompleteness_reasons` when saving. A nonempty reasons list prevents a catalog
from establishing healthy complete absence even if its completeness flag is true.
The caller is responsible for honest coverage metadata; metadata is not a proof
that a remote store was crawled correctly.

## Evidence and health

Known matching observation scopes are required. Both sides of a field change need
eligible retained observations selected by the existing source-resolution policy.
Resolution uses each snapshot's stored timestamp. Defaults, missing observations,
expired payloads and unresolved conflicts produce diagnostics, not fabricated
price/stock values or field-removal alerts. Variant prices inherit the parent's
supported currency. A currency mismatch emits a currency candidate and suppresses
the price comparison.

`candidates` includes confirmed, pending and rejected decisions. `events` contains
confirmed decisions; `new_events` contains only those first published by this
invocation. `diagnostics` explains suppressed or unsupported comparisons and
retains resolution context. Values retain their Python types, including Decimal.
For JSON transport use the existing evidence `encode_value`/`decode_value` codec.

New products require a healthy complete previous catalog and at least one
supported tracked field on the new record. Missing products remain unobserved.
Removal requires an initial healthy complete absence and another healthy complete
absence in an explicit later recheck. Partial or failed crawls cannot confirm
removals. Catalog completeness does not prove variant completeness; variant
membership is diagnostic only.

## Recheck and replay

Under fixed policy `reliable-change-v1`, price decreases of at least 50%, increases
of at least 100%, transitions to/from zero and every currency change remain pending.
Other eligible field changes confirm immediately. Supply a later same-supplier,
same-scope snapshot to recheck pending decisions:

```python
checked = reliable_changes(
    "shop.example", previous_snapshot_id=old_id, current_snapshot_id=new_id,
    recheck_snapshot_id=recheck_id, db_path="snapshots.db",
)
```

Matching the new supported value confirms; matching the old value rejects; a
third supported value rejects as superseded. Unknown support leaves pending.
Price rechecks also require the original supported currency, including parent
currency for variant prices. Missing or different currency cannot confirm a
price. Reports never fetch a recheck or run callbacks themselves.

First evaluation freezes the comparison. Only pending candidates can transition;
terminal results are historical. Stable IDs and publication state persist across
reopen and concurrent calls. Repeating the same pair/recheck returns the stored
events and empty `new_events`. Compare successive pairs for ongoing monitoring;
manually overlapping pairs are separate comparisons. A reversal is a new event.
SQLite publication does not guarantee delivery to an external callback: persist
stable event IDs with your own delivery handling before acknowledging processing.

## Compatibility, migration and limits

Existing `changes()`, `price_history()`, `watch()`, model constructors, feeds and
CLI defaults retain their contracts. This report API is an explicit opt-in.
Legacy scalar-only snapshots cannot supply evidence. Selected records must
already have persisted canonical identities; this API does not migrate history.
Use existing explicit identity migration separately when needed, and capture new
evidence for unsupported legacy facts. Unknown/different scopes yield suppressed
reports. Invalid IDs/order, corrupt data, duplicate identities and size limits
fail explicitly and roll back; missing snapshot IDs raise `KeyError`.

The engine reads at most three selected snapshots in one transaction, without
backfilling unrelated history. SQLite contention waits at most five seconds; no
automatic retry occurs. Snapshot/report payloads are bounded to 16 MiB and report
candidates plus diagnostics to 10,000; overflow fails instead of truncating.
Retained capture limits remain 4 KiB per fragment and 64 KiB per product.

Reports retain values and qualified references, not copied evidence payloads.
Pruning later can make source lookups expire while historical IDs and decisions
remain stable. A replay describes support at original evaluation, not current
source availability or a fresh observation of the remote store.

Run `PYTHONPATH=src python examples/reliable_changes.py` for a self-contained
offline capture/normalization/storage/report/recheck example. Its data and changes
are synthetic; live verification is recorded separately in the feature spec.
