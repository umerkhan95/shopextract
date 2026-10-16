# Code skeleton and exact dictionary contract — G2 reviewed

Historical design-stage artifact, subsequently implemented; final state in status.md.
Author: design delegate, 2026-10-16. G1 passed; this contains declarations and
executable acceptance tests only. reliable.py entry point explicitly raises
NotImplementedError. No candidate decisions, DB mutations or fabricated success.

## Public entry point and error boundary

`shopextract.monitor.reliable.reliable_changes(domain: str, *,
previous_snapshot_id: int, current_snapshot_id: int,
recheck_snapshot_id: int | None = None, db_path: str = DEFAULT_DB_PATH) -> dict`.
After implementation export from monitor/__init__.py; preserve legacy exports.
Policy fixed `reliable-change-v1`. Missing DB: FileNotFoundError; missing IDs:
KeyError; invalid IDs/order/domain, malformed graph/identity and size overflow:
ValueError; bounded SQLite contention: sqlite3.OperationalError. Invalid arguments
must not commit DDL, report or candidate writes. No public callbacks/network.

## Report keys (all present)

- `report_id`: stable string for normalized supplier + previous/current IDs + policy.
- `policy_version`: `reliable-change-v1`; `supplier`: normalized supplier string.
- `previous_snapshot_id`, `current_snapshot_id`: ints.
- `status`: `compared` or `suppressed`; `reason`: nonempty explanatory string.
- `candidates`: ordered complete candidate dictionaries, including terminal rejected.
- `events`: confirmed candidates only; same candidate content, stable IDs.
- `new_events`: events first published by this invocation; empty after durable replay.
- `diagnostics`: ordered dictionaries with `canonical_product_id`,
  `canonical_variant_id`, `field_path`, `reason`, `details` (structured explanation).

Candidate keys: `candidate_id`, `event_id` (stable reserved string even pending),
`kind` (`field_changed`, `product_added`, `product_removed`), `state`
(`confirmed`, `pending`, `rejected`), nonempty `reason`, `supplier`,
`canonical_product_id`, `canonical_variant_id` (None for product), `field_path`
(record-local escaped JSON pointer, empty string for product membership),
`previous_snapshot_id`, `current_snapshot_id`, `old`, `new`, `recheck`.
`recheck` is None initially, then ValueSide plus attempted snapshot support.
Event identity does not depend on source array position, title or wall clock.
Sort entities product-ID, variant-ID (None first), field-path, kind.

ValueSide keys: `state` (`observed`, `absent`, `unknown`), `value` (typed normalized
value for observed, None otherwise), `references` (list), `coverage` (dict or None).
Reference keys: `snapshot_id`, `record_key`, `observation_id`, `evidence_ids`.
Only selected observation evidence appears in references. Other observations and
resolution explanations stay diagnostics. Inherited variant currency is validated
from parent selected graph; no invented variant currency evidence. Source URL and
observed_at remain inspectable through qualified get_evidence lookup. Coverage
keys: `snapshot_id`, `observation_scope`, `catalog_complete`,
`incompleteness_reasons`; this supports absence only, never a fabricated observation.
Snapshots explicitly freeze previous/current fields; recheck value may be unknown.
A recheck with a different/unverified currency cannot confirm a price candidate,
including variants; pending reason `currency_unverified` for unsupported currency and
`currency_mismatch` for differing currency. Unsupported recheck field remains
`unverified_recheck`; observed third value uses `superseded_value`.

Python result dictionaries contain Decimal/datetime where appropriate. Persist
using existing encode_value/decode_value + deterministic JSON. Return detached
structures: caller mutations never edit persisted report. Pruning may expire
reference lookups; replay retains original values/decisions without copied payloads.

## Private module ownership and transaction seams

- monitor/reliable.py owns validation, evaluation, stable IDs, report serialization,
  bounded report ledger DDL and atomic comparison/recheck/publication transaction.
- monitor/evidence.py will extract `_load_snapshot(conn, snapshot_id)` from public
  loader and a bounded DDL-only initializer (no legacy owner backfill); public
  loader behavior stays unchanged. All selected metadata/graphs read on one
  caller-owned connection and transaction. Never invoke public loader or lookup
  while a reliable writer transaction is held.
- Existing `_owner_graph`, `_read_capture`, product_from_record, resolve_fields,
  `_equivalent_key`, encode/decode and supplier_scope supply existing behavior.
- Resolve each contract at its snapshot.created_at. Fixed fixture source times
  T0+n hours match explicitly set capture timestamps; roles are supplier.
- Reliable entry requires canonical IDs already persisted. Validate selected
  identities; no identity/history migration and no unrelated owner backfill.
- Use initialize=False connection, BEGIN IMMEDIATE, bounded DDL version check,
  read <=3 selected snapshots, compute or replay, persist, `_before_commit(conn)`,
  commit. Five-second busy wait, no retries. `_before_commit` is a private no-op
  in implementation, currently raising stub; tests inject exception after writes
  to verify rollback and successful retry publication.
- Proposed versioned ledger tables: singleton version and reports keyed uniquely
  by (supplier, previous ID, current ID, policy). Report JSON stores candidate
  state and publication outcome atomically; no async delivery outbox promise.
- Validate selected products_json and summed portable records before JSON decode;
  MAX_SNAPSHOT_BYTES=16MiB per selected snapshot. Candidate + diagnostic count
  MAX_REPORT_ENTRIES=10,000; stored JSON MAX_REPORT_BYTES=16MiB. Overflow is
  ValueError with rollback, no truncation. Constants patchable in bounded tests.

## Red acceptance and gate boundary

tests/test_reliable_changes.py maps SC01–18 through named tests and parameterized
boundaries, restart/race/rollback, selected refs, source expiry, variant recheck
currency and unrelated corrupt legacy history. Fixture graph/schema/save succeeds
before the intentionally missing API behavior raises. Commands/results are saved
in verification.md. Existing 39 monitor/completeness tests must remain green.
Stop for independent G2; components design and business implementation await gates.
