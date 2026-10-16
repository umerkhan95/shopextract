# Saved-evidence owner audit — before execution

Root approved this as a stronger assertion of the existing planned ownership
invariant. No new fixture, generator batch, behavior or stress rerun. Audit only
the22 conformant saved logical cases after the continuation stopped.

For every candidate old/new/recheck qualified reference, load the referenced
snapshot via production connection-owned _load_snapshot on a read-only SQLite
connection. The Product at record_key must have candidate.canonical_product_id;
a variant owner must additionally have candidate.canonical_variant_id. Product
owners require canonical_variant_id=None. Existing source value/pointer/time/role
checks remain unchanged. Check snapshot/record-key parsing and index validity.

One sequential process, read-only transactions, <=20second hard subprocess bound,
zero network/inference/data generation. Known execution132.607 seconds; maximum
with audit152.607 <=180. Save counts and exact timing separately; stop mismatch
without changing source or assertions. No writes/DDL against saved DBs.
