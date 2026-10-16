# Offline evidence, snapshots and portable exports

Captured observations explain which retained source supports a field and how its
value was normalized. They support review; they do not prove source truth. Source
roles such as `verified_manufacturer` are caller assertions. A model or rule score
is a score; `ValidatedConfidence` requires method, dataset and version metadata.
This example performs no empirical confidence calibration.

Run the small synthetic workflow from a checkout with the package dependencies
installed:

```sh
PYTHONPATH=src python examples/evidence_trust.py --output-dir /tmp/shopextract-trust
```

It parses a captured feed, normalizes zero price and false stock, captures nested
Shopify variants and identifier transformations, resolves a supplier/manufacturer
specification disagreement at a fixed UTC time, stores SQLite, reopens it, retrieves
field evidence, and writes/loads a portable bundle. `report.json` records fixture
name, policy time, factual-path denominator and state counts. These are bounded
fixture coverage measurements, not extraction accuracy or calibrated confidence.
The example has no network, model, credential or hosted-service requirement.

## Capture, resolve and inspect

Normal extractors retain bounded source projections and `normalize()` attaches
`evidence_contract` to Product and Variant. Legacy constructor values remain
available for existing callers. Use `product.trust_view()` to inspect trusted
values: its `value` is absent for unavailable fields, while `legacy_value` retains
the compatibility scalar. A missing price is different from an observed zero;
a missing stock field is different from captured false.

Call `resolve_fields(product.evidence_contract, as_of=aware_utc_datetime)` and attach
the returned contract. The explicit evaluation time and recorded policy/version
make the decision inspectable. Supplier offers and manufacturer specifications
have different authority rules. Conflicts retain every alternative and rationale;
equal-authority disagreements expose no selected trusted value. Resolution does
not change the original Product scalar, source time or raw score.

States distinguish `observed` support, explicit `unknown` missing values,
`unsupported` capture/default values, unresolved `conflicting` candidates, and
`expired` support. Freshness expiry is a decision over retained evidence; retention
expiry removes availability. Imported historical policy output is not refreshed.

## Store, reopen and retrieve

```python
from shopextract.monitor.evidence import save_snapshot, load_snapshot, get_evidence

snapshot_id = save_snapshot(products, 'shop.example', db_path='evidence.db')
restored = load_snapshot(snapshot_id, db_path='evidence.db')
lookup = get_evidence(evidence_id, snapshot_id=snapshot_id,
                      record_key='product/0', db_path='evidence.db')
if lookup.status == 'available':
    print(lookup.evidence.source_url, lookup.evidence.observed_at)
    print(lookup.evidence.resolve_pointer())  # for retained-data pointer evidence
```

Variant owner scope is `product/0/variant/0`. Contract observation IDs are local to
an owner; include owner and snapshot scope when linking reports. Available evidence
contains its original source URL, method, UTC time and excerpt or locally resolving
JSON Pointer. Existing matching `field_support` references are contract-local;
resolve them using the matching record's snapshot and owner scope. A remote URL
alone does not archive the original page. Lookup also
reports `expired`, `missing` or known legacy `unsupported`; corruption raises an
error rather than becoming available evidence.

Snapshots preserve nested typed values and attached contracts in the same SQLite
transaction as their snapshot/identity data. Additive versioned migration preserves
historical rows and marks absent legacy provenance unsupported. Migration does not
invent captures, timestamps or validated confidence. Existing monitoring projections
remain compatible. Evidence IDs are scoped by snapshot and owner. Reusing an ID
with different content within that scope is an error; different scopes may carry
the same ID. Unscoped lookup must resolve unambiguously or raises an error.

## Portable bundle and optional companions

```python
from shopextract.export import write_evidence_bundle, read_evidence_bundle

write_evidence_bundle(restored, 'evidence-bundle.json')
imported = read_evidence_bundle('evidence-bundle.json')
```

The versioned envelope contains stable record keys and shared typed Product records.
Decimal spelling, aware UTC microseconds, Platform/Variant types, literal `$type`
user maps, evidence IDs, candidates, transformations and policy rationale survive.
Dynamic contracts travel explicitly; dataclass `asdict()` is insufficient. Loading
rejects unsupported versions, duplicate keys, malformed fields/tags, nonfinite
numbers, unresolved pointers and dangling references. Bounded input validation
protects byte count, record count and recursive shape. Tuples, sets, bytes and
arbitrary Python objects are unsupported transport values.

Existing dictionary CSV, JSON and marketplace feed exports retain their defaults.
Opt-in companion exports carry complete nested contracts separately. A sidecar
binds format and ordered row mappings to the SHA-256 digest of the exact feed
bytes. Verify the bytes before using a row index; edits and reordering require a
new companion. Duplicate marketplace IDs remain distinct rows. Scoped canonical
identity is preferred; content-derived fallback keys change when content changes.
A digest checks correspondence/integrity, not publisher authenticity or source truth.

```python
from shopextract.export import to_csv, to_feed

to_csv(restored, 'products.csv', evidence_path='products.evidence.json')
to_feed(restored, 'shopping.xml', format='google_shopping',
        evidence_path='shopping.evidence.json')
```

Pass Product objects when requesting companions so attached contracts remain
available. Plain dictionary exports keep their established interface.

## Explicit retention

```python
from datetime import datetime, timezone
from shopextract.monitor.evidence import prune_evidence

report = prune_evidence(db_path='evidence.db',
                        before=datetime(2026, 10, 1, tzinfo=timezone.utc))
# Inspect the dry-run report before requesting dry_run=False.
```

No automatic deletion runs. The default is a bounded dry run with retained
references protected. An explicit `protect_references=False, dry_run=False` expires
referenced support and reloads dependent observations/resolutions as unavailable.
Tombstones retain ID, status, reason, expiration time and payload-free metadata in
`evidence_availability`; bundles preserve those attachments. Re-importing a bundle
must not revive expired facts. This is support unavailability, not secure erasure:
legacy/raw capture copies, old exports and backups may still retain source content.
Shared payload bytes cannot be removed while another available evidence uses them.

Capture fragments are capped at 4096 UTF-8 JSON bytes and product retained support
at 65536 bytes. Truncation is explicit; those caps do not bound total database size,
which can grow with history. Keep backups and apply an application retention policy.

Serialized snapshots are capped at 16 MiB; SQLite uses a 5-second busy timeout.
Bundles allow at most 64 MiB and 100,000 records, with typed data nesting bounded
to 64 levels and one million nodes. Pruning examines 100 records by default and
accepts at most 1000 per batch. A protected prefix can remain eligible on later
calls; `has_more` is not a promise that automatic repeated calls will advance.
Inspect the report and choose an explicit policy rather than looping indefinitely.

## Verification scope

`tests/test_evidence_trust_e2e.py` exercises the runnable example, missing versus
literal values, nested typed/identifier history, alternative retention and equal-role
ties, ungrounded scores, explicit pruning/freshness and expired bundle round trips.
Unit suites separately cover migration, transactional rollback, corruption and feed
companions. The fixtures are labeled synthetic examples and make no population
accuracy, statistical calibration or source-authenticity claim.
