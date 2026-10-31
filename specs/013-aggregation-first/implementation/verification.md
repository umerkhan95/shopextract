# Google taxonomy integration verification

2026-10-31. Branch `google-taxonomy-integration`, base main `a900599`.
Implementation authorized after reviewed full plan. This child delivers reusable
taxonomy catalog/source/mapping/public integration, not the broader product-group,
offer aggregation or specification-insights engine in parent GAG13–18.

## Actual results

| Check | Result and evidence |
| --- | --- |
| Intended missing Google behavior | 11 expected failures before production: `evidence/contract-red.log`; separate crosswalk, effective-classification, CLI and snapshot reds retained. |
| Independent gates | Child G1, catalog/options G2 and G3, source/crosswalk/effective/CLI/snapshot supplements recorded with artifact hashes in reviews.md. |
| Catalog source | Shopify-maintained Google2021-09-21 snapshot, source commit2e9aa2e9b882383952c63d212add13eb80f46cf9; original YAML and consumed derived TXT hashes distinct in manifest. Direct Google HTTP denied403, no bypass. Source receipt `evidence/source-acquisition.json`. |
| Full catalog oracle | Exact original source ID/path/parent/ancestor sets:5595nodes,21roots,4719leaves,5574parent edges PASS. No Google corpus bundled. |
| Source crosswalk | Real complete source loader/ledger PASS:14606Shopify IDs =14528mapped-single +78explicit exclusions;5455Google targets have inbound rules and140remain direct-only. `evidence/full-target-report.json` and `cli-real-source-ledger.json`. |
| Six source families |16controlled source-shaped positive/missing/scoped/tree-vs-membership cases PASS through capture→normalization→native mapping/binding→portable reload→effective Google projection. No claim six-platform actual merchant sampling. |
| Resource/source negatives | Strict parsing, graph/digest/owner/version/scope, atomic publication/fault rollback, cache-corruption/traversal, duplicate JSON/YAML, Unicode/alias and optional-dependency outcomes tested. Distinct reviewer findings reproduced red before repair. |
| Public CLI/export |9CLI checks PASS including prepare, snapshot provenance, info, exact lookup/path, pagination identity, native normalization, JSON errors and existing CSV/category companion export. `evidence/cli-final.log`. |
| Genuine installed package | Wheel installed in isolated venv outside checkout,5595ID/path lookups,3native feed/portable samples and real CLI; ordinary lookup with network/YAML import denied. Offline sdist→wheel rebuild and existing Shopify resource preserved. `evidence/installed-package.json`. |
| Required repository driver | `python scripts/run_tests.py --output-dir build/google-integration-ci`:1777passed (1647main+24oracle+106maintenance), zero failures/skips,111.463886s, original240/480s limits unchanged, no surviving groups. `evidence/configured-ci-summary.json`. |
| Full native/public mapping/export sweep | **BLOCKED, not launched.**3-target smoke and100-target measurement pass, with overlap; these are not103unique or5595pipeline checks. Repaired100measurement3.709s gives259.4s forecast including25%reserve, over180s gate. `evidence/full-target-report.json`. |
| Actual merchant integration sample | Not run: required exhaustive readiness gate remains blocked. Metadata acquisition is not merchant assignment evidence. |

## Bounded verification disposition

The verifier exercised seven actual controls: missing required measurement,
changed identity, existing output, oversized wire, owned timeout cleanup, omitted
target and ambiguity-veto mutation. Initial mutation harness failure and corrected
actual-function mutation evidence are retained; production hashes restored.

Initial100measurement5.117s forecast357.9s exceeded180s, so no full sweep ran.
Reviewer approved one driver-only redundancy removal, retaining each target's
actual public/native mapping, binding and export assertions. Fresh3/100attempts
used the new driver hash; forecast remained259.4s. Per bounded usage rule no
second tuning attempt or raised ceiling occurred. Source ledger completed under
its separate120s/512MiB gate (8.210s worker,344MiB sampled peak).

This is a passing repository/package/catalog/source-ledger result with a blocked
exhaustive feature gate. No overall GFR08/child final PASS is claimed. A later
reviewed performance slice must resolve readiness before full-target completion;
actual merchant integration remains a separate required disposition. Parent
aggregation/grouping/offer features remain pending and were not silently merged.

Raw source corpus and per-batch artifacts are under ignored downloads/build;
compact committed receipts retain exact source/code/policy identities and honest
outcomes. No models or paid inference were used. Declared dependencies were
installed; no browser/model downloaded or launched. Actual incremental session
token counters unavailable; no quota estimate. No commit/push/PR/merge performed.
