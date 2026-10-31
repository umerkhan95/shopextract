# Google executable child: behavior-first tests

Date:2026-10-31. Designed before tasks/skeleton/business logic. All verdicts pending.

| Requirement/scenario | Fixture, expected outcome and distinct risk | Real seam |
| --- | --- | --- |
| GFR01/GSC01 | Synthetic TXT with2roots,7nodes,4leaves. ID6/path Electronics > Computers > Laptops agree; parent5/ancestors4,5, children empty. Catalog immutable; unknown IDs/paths returnNone. | New source parser/catalog index; fixtures explicitly synthetic. |
| GFR01–02/GSC02 | Duplicate ID, duplicate path, missing parent, malformed header/UTF8/BOM, wrong source digest, corrupt resource or interrupted rename. Reject before publish; old fingerprint still loads. | Source validator and actual local resource store/atomic publisher; only failure boundary injected. |
| GFR03–04/GSC03 | Actual GoogleFeedExtractor CSV/XML retains ID/full-path through capture. allow_unknown_source_version=True maps exact target, source version remainsNone, target version includes pinned digest, and strict portable reload retains ID/source/support. | Existing feed parser→normalizer→_observe_categories→map_categories→_bind_categories→codec; no fake mapped records. |
| GFR04/GSC04 | Same captured feed under permissionFalse stays unmapped; empty category stays explicit unavailable; LLM/truncated capture cannot acquire observed support. | Existing native support state and mapper guard, unknown target lookup. |
| GFR03/GSC05 | Deterministic relevant target/rule999/1000/1001 and byte below/at/above256KiB; full catalog may exceed1000, selected policy may not. | Native validate_options and option helper; no raised caps. |
| GFR05/GSC06 | Exact directional crosswalk, duplicate equal rows, multiple target candidates, dangling endpoint, row+explicit exclusion conflict, outside-source row, version mismatch. Canonical source ledger partitions S; invalid index not activated. | Actual source parser/index/ledger and mapper, primary status partition from parent source-mapping-plan. |
| GFR06–07/GSC07 | Six source-shaped adapters with store-scoped overlapping native IDs; explicit merchant rules and a conflicting official route. Unavailable facts remain unavailable; product attributes unchanged; API/CLI/export preserve category binding. | Existing adapters/normalizer/mapper/portable/export; CLI subprocess for public contract. |
| GFR01–08/GSC08 | Pinned complete Google target set G, installed package outside checkout and all forward source IDs S. Lookup/map/bind/reload/public/export target sets equalG; all S dispositions accounted, counts not merchant coverage. | Dedicated controlled full-ID driver, immutable receipts, offline wheel/sdist. |

## Red acceptance and staged verification

`tests/test_google_taxonomy_contract.py` is the intended missing-API acceptance
suite. Missing Google API yields explicit assertion failure; dependency/import
failures do not count as red evidence. Run after parent environment readiness,
save output before implementing Google business logic. Future focused source/
crosswalk/CLI tests derive from the table once exact source formats are inspected.

Initial controlled mechanism manifest:8risks above, each with named adverse
subcases, fixed seed13031, one worker, synthetic sources/no inference. Save one
seven-node smoke before expansion. Synthetic resource<=2MiB, generated<=8MiB,
512MiBRSS, per-case30s and focused mechanism180s total. Stop first failure, save
minimal repro; one diagnosed repair, no budget increase. A temporary omission
of one ID and unsafe ambiguity/publication mutations must be detected/restored.

Full target sweep uses parent dedicated180s/15s-batch/100targets/512MiB bounds,
source ledger separate120s/8MiB. Measure3target smoke then100target batch and
forecast+25%reserve before expansion. Required repository driver remains
240s/family480s shared; no old successful run substitutes for new results.

Source acquisition follows parent separate catalog/crosswalk2HTTP/2MiB/30s
budgets. Missing permitted resource/live access blocks that evidence, not a mock
pass. Actual merchant sampling remains parent2URLs/2origins/8HTTP/4products/120s
after offline success; source taxonomy metadata is not live product membership.
