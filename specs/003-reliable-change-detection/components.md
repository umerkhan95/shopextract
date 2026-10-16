# Reusable component model — G3 passed

Author: coordinator; 2026-10-16. G2 passed before this design. No production
logic added. The reviewed skeleton interfaces and report keys stay unchanged.

| Component | Reuse / change | Ownership and consumers |
| --- | --- | --- |
| identity.supplier_scope and persisted canonical IDs | Reuse; no new matcher or history migration | Supplier normalization and identity ownership remain identity.py; report engine validates selected unique product/variant IDs |
| monitor.snapshot._get_connection | Reuse initialize=False, five-second timeout/FK settings | Reliable entry owns one BEGIN IMMEDIATE transaction, rollback and close; no network or callbacks inside |
| monitor.evidence._ensure_evidence_schema | Separate DDL-only initialization from legacy-owner backfill, via optional private flag/helper | Public existing save/load callers retain current default behavior; reliable entry uses DDL-only path, never touches unrelated legacy history |
| monitor.evidence._load_snapshot | Extract existing loading body to connection-owned private helper | Public load_snapshot retains signature/initialization and delegates; reliable transaction reuses helper on <=3 selected snapshots with limits before decoding |
| _owner_graph / _read_capture / product_from_record | Reuse existing retained-evidence, expiry and typed product reconstruction | Evidence persistence owns graph integrity/availability; reliable module must not rebuild retention rules or invent support |
| resolve_fields / _equivalent_key | Reuse snapshot-time authority/freshness and conservative typed equivalence | Reliable module validates field-specific types separately, extracts only selected observation evidence, keeps competing observations/reasons in diagnostics |
| encode_value / decode_value | Reuse exact Decimal/datetime representation | Reliable ledger persists detached report dictionaries through existing codec; no float loss or new transport format |
| monitor.reliable field evaluation | New narrow component within reliable.py | Shared evaluator for product/variant fields and rechecks, including parent currency for variant prices; one implementation of support/type/currency decisions |
| monitor.reliable candidate/coverage builders | New internal helpers | Field, addition/removal and recheck flows share exact dictionary schema and qualified references; absence metadata distinct from observed field support |
| monitor.reliable ledger | New additive versioned reports table with unique supplier/pair/policy key | One transaction serializes first publication and pending transitions; no background publisher or external exactly-once callback claim |
| tests fixtures/assert_contract | Reuse test helpers across all feature scenarios | Tests own explicit source/capture times, barrier races, fault injection and exact contracts; expected behavior remains independent of production helpers |
| bounded live driver | Reuse capture -> normalize -> save/load -> reliable report -> qualified evidence lookup | Read-only verifier uses two requests, saves first smoke before repeat, partial coverage, no artificial claim of actual live price mutation |

## Lifecycle and limits

Validate explicit arguments, selected snapshot order/supplier and optional recheck
scope before committed changes. Bound selected scalar/portable/graph reads before
decode; reject missing/duplicate selected IDs. Freeze first report evaluation and
selected refs, update pending candidates only, and publish newly confirmed events
in that same transaction. Return detached dictionaries after commit. Retention
changes lookup availability, not historical report values or IDs.

Candidates+diagnostics <=10,000, report JSON <=16MiB, each selected snapshot's
scalar/portable input <=16MiB. Graph/source bytes use existing storage bounds with
explicit checks for direct corruption. No full history scan, hidden migration,
network, user callbacks, inference or new dependency. Invalid input/limit/failed
commit rolls back DDL and report writes.

## Dependency direction and exclusions

reliable -> evidence private connection loader, snapshot connection, identity and
trust/codec components. Existing evidence modules do not import reliable. Only
monitor/__init__.py adds opt-in exports. Legacy changes/watch models and default
CLI/feed paths remain compatible. No generalized event bus, plugin system or
speculative reusable framework; helpers earn reuse across initial diff/recheck
and product/variant processing. Meaningful contract changes return to G1/G2.
