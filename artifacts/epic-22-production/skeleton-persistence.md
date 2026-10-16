# Persistence skeleton and reviewed handoff — #37

Status: skeleton only, 2026-10-16. No live crawl/model runs. Existing baseline is
74 passing tests reported by coordinator; no new behavior is implemented or tested.

## File ownership and public signatures

`src/shopextract/monitor/evidence.py` contains typed result envelopes and stubs.
Implementer owns that module, transaction integration in `monitor/snapshot.py`,
public exports in `monitor/__init__.py` and package `__init__.py`, and focused tests.
Coordinate shared spec changes with the integration owner.

- `save_snapshot(products, domain, *, db_path=DEFAULT_DB_PATH, metadata=None) -> int`
  returns snapshot row ID. `products` is an iterable of Product. Allowed metadata:
  `observation_scope: str | None`, `catalog_complete: bool | None`,
  `incompleteness_reasons: list[str]`, `max_urls: int | None`; reject unknown keys.
- `load_snapshot(snapshot_id, *, db_path=DEFAULT_DB_PATH) -> list[Product]`;
  absent row raises KeyError. Legacy rows restore typed scalar compatibility
  values, with no evidence attachment and therefore unsupported trust inspection.
- `get_evidence(evidence_id, *, snapshot_id=None, record_key=None,
  db_path=DEFAULT_DB_PATH) -> EvidenceLookup`. Status is available, expired,
  missing or unsupported. An available result carries validated Evidence;
  other statuses carry no Evidence and have a reason. Expired adds UTC expired_at.
  Unknown ID is missing; a specifically scoped legacy owner lacking a graph is
  unsupported. Insufficient scope matching multiple captures raises ValueError.
  Missing snapshot/owner is missing; corruption/version errors raise ValueError.
- `prune_evidence(*, db_path=DEFAULT_DB_PATH, before: datetime,
  protect_references=True, dry_run=True, batch_size=100) -> PruneReport`.
  Explicit UTC cutoff is required. Captures strictly older than cutoff qualify.
  Batch size is 1..1000; deterministic order by capture time and compound key.
  Counts describe examined candidates, protected captures, actual/prospective
  expirations, deleted/prospectively deleted shared payloads, and has_more.

Existing async `snapshot(url, *, db_path, max_urls) -> int` keeps its observed
product-count return and completeness behavior; it calls the shared internal
write path, not public save followed by a separate identity transaction.

## Shared codec and owner identity

Use `_portable.product_to_record/product_from_record`; public bundle helpers live
in `export/_bundle.py` (confirmed against completed #38 skeleton).
Do not independently implement Decimal/UTC encoding. Contracts use
TrustContract.to_dict/from_dict exactly once; preserve literal `$type` mappings.
Preserve platform enum, nested Variant types, dynamically attached contracts,
raw/normalized values, scores, confidence metadata, alternatives and policy.

Storage owner keys: `product/N` and `product/N/variant/M` within a snapshot,
independent of portable bundle record keys. Product contract's nested field paths
and standalone variant contracts remain separate owners. Evidence identity is
`(snapshot_id, record_key, evidence_id)`; observation identity adds observation_id
within the same owner. Evidence IDs are contract-local, not DB-global. Same
scoped key/different capture is rejected; equal bytes deduplicate independently.
An underspecified lookup must never silently choose the first matching row.

## Proposed additive schema and transaction

Keep `snapshots.products_json` in its existing legacy representation for identity,
diff and monitor consumers. Add a versioned typed product representation and
graph side tables. Suggested tables (final SQL may refine names):

| Table | Required keys/content |
| --- | --- |
| evidence_schema | module-local singleton version, reject unknown newer version |
| snapshot_records | PK(snapshot_id, record_key), typed Product/Variant data without captures, graph availability/reason |
| evidence_contracts | owner FK, graph observations/resolutions and schema version, no duplicate retained payload copies |
| evidence_records | PK(snapshot_id, record_key, evidence_id), capture metadata, payload hash, status/reason/expired_at |
| evidence_payloads | PK(payload_hash), canonical typed fragment bytes, byte_size |
| evidence_references | owner/observation/evidence compound keys and real compound FKs |

Do not use global PRAGMA user_version unless coordinated with other schema owners;
a module-owned version table avoids overwriting unrelated schema state. Enable
foreign_keys before transactions; index child keys and evidence lookup/ref edges.
Hash deterministic local typed bytes (not an RFC 8785 claim). Hashes establish
stored-byte consistency, not truth/authenticity. Metadata remains capture-specific.

Prepare and validate portable records before BEGIN IMMEDIATE. Enforce 16 MiB
serialized snapshot cap (documented engineering choice), existing 4096-byte
fragment / 65536-byte product capture limits, and bounded SQLite busy timeout.
One transaction includes additive migration, existing identity migration and
assignment, snapshot insert, typed records, captures, payloads and all references.
Rollback every exception; do not disable SQLite journal/synchronization.
Connection creation currently commits metadata migration separately: consolidate
write flow deliberately without circular imports or nested BEGIN/commit.

Migrate legacy rows conservatively and idempotently. Preserve row IDs, created_at,
prices, scope/completeness and identity/history. Mark absence of graph with stable
unsupported reason. Do not fabricate source observed_at from created_at/current
time, infer captures from raw_data, or rewrite legacy scalar JSON gratuitously.

## Retention and effective projection

No automatic deletion; total database size may grow. Dry-run is default and one
call inspects at most the explicit batch cap; protected candidates count toward
that bound. has_more reports additional eligible candidates, not permission for
an unbounded internal loop. Callers may repeat with explicit policy/cutoff; a
protected prefix can remain eligible, so document this and avoid claiming progress
through all protected rows without a cursor.

Default protect_references skips every capture referenced by a retained owner.
Explicit False expires referenced captures atomically and keeps scoped tombstones.
Delete payload bytes only after all available owners using that hash expire.
Contract JSON must not retain an unpruned second authoritative Evidence payload;
graph audit metadata retains observations/resolutions separately from captures.
Product.raw_data['_capture'] and legacy products_json may contain duplicate source
bytes. Therefore pruning promises support unavailability and removal of the
deduplicated authoritative payload row, **not secure erase or guaranteed storage
reclamation**. Enforce the availability overlay before any codec reconstruction,
never use residual raw_data to revive expired capture. Do not claim all copies
were deleted; a separate explicit redaction feature would be needed for that.

On load, build an effective valid TrustContract: omit unavailable Evidence records;
for each observation depending on any expired capture, set state expired, attach
reason, clear evidence_ids and validated_confidence. Retain raw/normalized audit
values and transformations. For any selected resolution whose observation expired,
set state expired, clear selected_observation_id and give explicit reason; retain
all observation alternatives and policy metadata. Do not select another candidate,
refresh capture timestamps or manufacture confidence. Preserve untouched stored
historical observation/resolution metadata for audit. Public trust_view must show
no observed value supported by expired bytes. Retention is distinct from #36
freshness policy; portable export of loaded effective Product remains valid.
Retain original source metadata (URL/time/method/role/pointer, no payload) and
expiration reason/time in tombstones. Coordinate optional `evidence_availability`
Product/Variant attachment/portable branch with #38 so offline export carries
this audit metadata without reconstructing invalid Evidence. Exact agreed shape:
each model's `evidence_availability` attachment is a list of dictionaries with
`evidence_id: str`, `status: 'expired'`, nonempty `reason: str`, `expired_at: aware
UTC datetime`, and `metadata: dict` (source capture metadata excluding all payload
bytes). Portable record optionally carries `evidence_availability` and
`variant_evidence_availability` (variant-index-aligned list of lists or null),
using shared typed codec once. No dangling contract reference is permitted.
These branches remain optional for existing records and strictly validated.

## Separate post-skeleton research review

Reviewed all three completed saved reports after settling skeleton interfaces:
`research-persistence.md`, `research-portability.md`, `research-verification.md`.

- Persistence research: atomic identity + graph transactions, additive idempotent
  migration, FK enforcement, tombstone envelopes and shared-payload retention all
  have explicit implementation requirements above. Research's proposed DB-global
  evidence identity is deliberately revised to compound scope: current validators
  scope IDs to a contract, and portability research requires owner-aware lookup.
- Portability research: one typed codec, no double encoding, dynamic attachments,
  strict validation and standalone variant scopes are aligned. Storage owner keys
  are explicitly distinguished from portable record keys to prevent API coupling.
- Verification research: scalar compatibility values never imply observed support;
  projected expiration clears selected resolutions/confidence while retaining
  alternatives. Public APIs suffice for offline restart/bundle/prune example.
- Gaps resolved during review: record-key ambiguity raises rather than guesses;
  metadata keys/row-ID return are explicit; bounded prune behavior and protected
  prefix limitation are documented; authoritative graph JSON cannot bypass expiry.
- Actual #38 stubs reviewed: codec lives in `_portable.py`, bundle APIs live in
  `export/_bundle.py`. Explicitly distinguish support expiry from secure erasure
  because compatibility raw_data may retain copied bytes; coordinate tombstone
  attachment for metadata-preserving offline export.

## Acceptance tests for implementer

Start with one tiny file-backed round-trip fixture. Then cover restart with nested
and standalone variant contracts, tagged Decimal/UTC/literal-map preservation,
ID collisions in distinct owners, underspecified lookup ambiguity, malformed
pointers/version/size rejection, and legacy unsupported lookup.

Inject write failure after snapshot and graph insertion; verify identities,
snapshot rows, payloads and references all roll back. Migrate twice; assert IDs,
history, timestamps/completeness and unsupported reason stable. Two snapshots
share bytes: protect by default, explicit expiry returns tombstone, another live
capture retains bytes; expired required support cannot remain observed/selected
or carry validated confidence. Verify small batch bounds and strict cutoff, dry
run leaves DB unchanged, missing vs expired vs unsupported vs corrupt semantics,
integrity_check and foreign_key_check. Run affected existing monitor/identity/
completeness/contract/capture/resolution tests, then coordinator runs full suite.

Update shared spec/plan/data-model/contracts/tasks and public operating-limit docs
before declaring #37 complete. Skeleton imports only; no behavior passes yet.
