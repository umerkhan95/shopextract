# Full Google target driver manifest

2026-10-31. Owner: google_verification_plan; reviewer: taxonomy_code_reviewer.
This manifest must be independently accepted before smoke/measurement/full run.
Driver: `scripts/verify_google_taxonomy.py`. No network, models, browser or pytest.

## Independent inputs and exact expectations

- Original retained Shopify-maintained Google `full_names.yml`: independently
  safe-parse ID/full_name rows, reject duplicate IDs/paths, derive root/parent/
  leaf sets from full paths; compare every ID/path/parent/child against the
  production immutable catalog. Expected current set5595; source hash and actual
  derived set digest recorded, never use production count as an oracle.
- Google explicit prepared catalog root; fingerprint must match explicit arg.
  Source/provenance and payload hashes are retained in the output identity.
- Official forward crosswalk exact SHA256 and Shopify catalog are explicit.
  Ledger mode loads the source catalog once, checks independent raw crosswalk
  source rows, then compares production `audit_source_categories` for all14606:
  expected14528mapped-single/78explicit-upstream-unmapped/zero other statuses,
  inbound5455Google targets/no inbound140. These are source declarations, not
  merchant/product coverage; no reverse mappings or forced matches.

## Real mechanisms and assertions

For every ID: generate a minimal controlled CSV product with that ID, real
GoogleFeedExtractor parser/capture, normalize_with_google_taxonomy with explicit
unknown source-version permission, native categorized encode/decode, and
effective_google_category. Assert exact target, retained source versionNone and
supported source category evidence. Use the raw category ID for half the rows,
complete original path for half, including root and leaf nodes; all IDs are
checked by lookup plus resolve_path independently. Product attributes remain
string maps; companion integrity/effective target checked after every reload.

Every bounded batch invokes the actual root CLI via CliRunner for lookup-batch,
normalize (which calls the same public native normalize helper for every ID),
and existing export(csv+category companion). Decode every normalization record
and every exported companion with the strict native codec; verify source support,
owner and unchanged binding, and effective target. The additional categories
record load CLI is exercised on the smoke only: repeating this thin adapter for
every ID duplicates the same native codec. No duplicate native normalization
loop, mocked algorithms, or reduced target/pipeline assertions.
CLI stdout and input files remain<=1MiB; record companions<=256KiB. Native byte
limits win, so batch default25 is a lowering of100-target upper bound. A100-target
measurement is4sub-batches25, all counted. No fixtures are actual merchant data;
fixed synthetic source URL/time and seed13031 are labelled in every report.

## Phases and supervisor bounds

Driver modes: smoke(3targets root/intermediate/leaf), measure(first100), sweep(all),
ledger(all source IDs). Save smoke before measure, then forecast full elapsed
including CLI work using100-target elapsed/N; require forecast*1.25<=180seconds.
Sweep refuses missing/incompatible passed smoke/measure receipts, refuses existing
output attempt, and binds source/code/policy/catalog/interpreter identity.
Supervisor owns worker process group:180s sweep cap (ledger120s),15s per batch,
512MiB RSS sampled group aggregate,1MiB per result/log/artifact, zero retries.
Worker updates batch heartbeat before work and atomic exact-ID progress receipts
after success; independent parent timer terminates/kills/reaps on deadline or
resource failure. Startup/source validation is counted in total, with first
batch heartbeat established before measured work. Worker failures retain bounded
diagnostics; no next chunk launches. No resume command in this version: existing
attempt directories reject; partial receipts are diagnostic and never silently
promoted/reused across code changes. The implementation task narrows the earlier
proposed resumable design rather than claiming a resume mechanism is tested.

Record attempted/passed ordered ID sets and digest, source/code hashes, phase,
batch sizes/bytes/times, peak sampled RSS and all exit/cleanup outcomes. Full
summary may be copied compactly to implementation/evidence/full-target-report.json
by coordinator; source/captures/large working files stay under ignored build/.
No run is PASS unless exact attempted/pass set equals the independent phase set,
all real stages pass and supervisor confirms worker/process group gone.

Performance amendment: initial3-target smoke passed; initial100-target measurement
passed5.117s but357.87s forecast including25% reserve exceeded180s. Full was not
launched. Independent reviewer approved one driver-only redundancy repair above;
all limits remain. New driver/manifest hashes require fresh smoke and measurement.
If the repaired forecast still exceeds180s, record blocked; no second tuning sweep.

## Adversarial controls and scope

Before full run reviewer checks fixture realism and independent oracle. Exercise
driver controls with a tiny local test fixture/source at readiness stage if
needed: missing measurement, changed code/source identity, existing output,
timeout, oversized wire result, altered target output all fail. Production
malformed mapping/ambiguity/update/portable tests are owned by parent/other agents;
this exhaustive driver does not duplicate their algorithms or claim independent
5595 decoder mechanisms. Required configured repository test driver remains
parent-owned with240/480second unchanged ceilings. Installed-wheel/package tests
and actual merchant observations are separate from this controlled sweep.
