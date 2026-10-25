# P2 analysis and export behavior

FR21: Preserve legacy compare/analyze/validate invocations. Explicit machine mode
and new commands return complete versioned envelopes. Export stdout is raw bytes;
file exports return metadata. Nested help loads no runtime.
FR22: Expose native compare controls (max-per-store, threshold), compare-catalogs
URL operands and native matching controls; identity/fuzzy match, GTIN lookup,
pair classification, evaluation, assign/inspect normalized attributes.
FR23: Analyze URL/file; stats distribution/outliers/brands; competitive position
(single product FILE plus competitor URLs), gaps (store URLs), brands (catalog
mapping FILE). Preserve native algorithms; aggregate float outputs are approximate.
FR24: Machine validate with four native marketplaces, images check with timeout /
concurrency, duplicates title/gtin/sku; native exporters json/csv/google_shopping/
idealo/parquet, optional CSV/feed evidence companion.
FR25: Strict JSON file or '-' stdin, 1MiB/1000 records/64 depth/100000 nodes. Flat
catalog records or native portable records/envelopes are explicit distinct inputs.
Money strings become Decimal only at typed Product fields; GTIN remains string.
Reject malformed types before network or writes. At most 10 stores, max1000/store,
finite thresholds [0,1], timeout (0,300], concurrency1..20. One stdin per command.
FR26: Currency-safe machine comparison groups by explicit currency before ranking;
competitive position retains requested currency and excludes different/unknown
currency before native float reduction, lists excluded currencies. Unknown currency
never becomes USD. Legacy algorithms/defaults unchanged.
FR27: Export validates/stages payload and companion before replacement; each single
replacement atomic. Back up prior bytes and restore on second replacement failure;
if recovery fails report exact recovery paths. Never claim two-file atomicity.
No automatic dependencies/install/network/model activation. Native extraction uses
P1 ExecutionPolicy default browser/LLM disabled and one shared deadline.

SC21 compatibility/nested grammar; SC22 matching identity and ambiguity; SC23 exact
transport and aggregate precision; SC24 currency provenance; SC25 validation/images;
SC26 staged export/recovery; SC27 bounds and declarative matching configuration.

G1 clarification: new network reports carry source completeness/errors and exit3
with usable partial data, exit1 on no usable sources. Deadline exhaustion is
E_TIMEOUT (no fabricated complete report). compare grouping uses observed raw
currency if present, otherwise supported evidence-contract currency; Product's
constructor USD alone is not observed. Unknown-currency matches are unranked.
Position currency is explicitly supplied by product FILE, no default currency.
Export '-' stdout forbids companion; companions only CSV/feed portable input.
Reject output/input/companion aliases using resolved paths plus samefile inode
checks where paths exist. Rollback records existence separately: initially absent
targets are unlinked after failure; existing targets restored from backups. Failed
recovery retains backup and staged files and returns recovery paths in error.
