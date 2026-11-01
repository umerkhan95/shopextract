# R3 documentary seams — no implementation

ExecutionState owns optional ProgressCheckpoint,enabled explicitly by extract-store
run_operation recovery callback. `register_progress_source(rows,platform,shop_url,
normalized=False)` keeps accepted producer references only; generic successful HTTP
parses append to an owned accepted collector. At most8 source handles,first usable
tier priority; no store merge or standalone persistence. Completed normalization
may register its exact Product list. `snapshot()` runs only after owned cancellation
has finished,using existing normalize/product_to_record/preflight/product_from_record
paths. Retention caps1000/8MiB/250knodes/depth56,explicit limit reasons. Source metadata
(scope/platform/restore flag) comes from current pipeline; no default currency.

`run_operation(...,recover=None)` preserves existing generic types unless extraction
opts in. Owned timeout + usable snapshot returns recovery callback result/E_PARTIAL;
empty snapshot raisesTimeoutError. Cancellation is never caught as ownedtimeout.
Normal completion discards checkpoint state. No callbacks or serialization added
to ordinary unowned library use. No new worker/budget framework. R4/R5 separate.
Private constructor may narrow max_products/max_bytes/max_nodes/max_depth for
bounded codec fixtures; values cannot exceed fixed ceilings. Record bytes use the
existing canonical portable JSON encoder. Snapshot construction is synchronous
only after cancellation; no per-page normalization/copy on normal execution.

G2 metadata clarification: `configure_result(result_platform,observation_scope,
restore_short_gtin=False,max_products=None)` sets owner result metadata/options;
source registration's normalization platform is independent. Snapshot returns
`ExtractionResult|None`,with source tier and configured result platform/scope.
HTML markers still select existing generic normalization even for detectedMagento;
no inference of native API provenance. The restore option is passed to the existing
normalizer only. Retention byte/node/depth limits bound recovery work,not wall time;
synchronous cancellation cleanup/freeze/reporting is not claimed inside the I/O
operation deadline. No opaque checkpoint callback can fabricate product rows.
