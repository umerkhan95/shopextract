# Behavior and test design — before task breakdown

This is the original preimplementation matrix. Actual phase-specific red/green,
mechanism/stress and live results are in p0/…p5/verification.md; unexecuted later
cases remain planned. Existing tests exercise library mechanisms but no
`CliRunner` references were found in the initial tests search; inspect relevant
tests before adding cases to avoid duplicates. New coverage targets CLI binding,
serialization, process lifecycle and interactions, reusing library fixtures.

## Scenario matrix

| FR | SC | Fixture / action | Exact expected outcome and distinct risk | Verification |
| --- | --- | --- | --- | --- |
| 01 | 01 | AST public exports plus documented module workflows vs coverage manifest | Every callable classified; missing mapping fails audit; helpers have rationale | Offline inventory + independent review |
| 02 | 02 | Saved nine-command baseline, maintenance/tools module help, representative legacy invocations | Same command/argument/alias/default semantics; lazy optional extras do not break root help | CliRunner and installed subprocess tests |
| 03 | 03 | 11 schema-valid products incl variant price Decimal, leading-zero GTIN, null/empty/0/false | Machine JSON parses as one envelope with schema_version=1.0; all 11 records retained; no diagnostics in stdout; money exact and missing support preserved | Controlled transport through real CLI/serialization |
| 04 | 04 | Native-platform fixtures, generic HTML, single product, CSV/XML feed; explicit extraction options | CLI results equal independently specified fixture facts; selected limits/config reach existing APIs; unsupported option rejected before fetch | Existing parser fixtures and controlled source; bounded live extraction |
| 05 | 05 | Two small catalogs with exact variant, ambiguous candidate, incompatible currency, duplicate title; matching dataset | Relations/ambiguity follow identity contracts; exact expected counts; evaluation reports native metrics; no cross-currency invented cheapest | CLI calls actual matching/analyze/validate/export code; native expected fixtures |
| 05 | 05b | Export CSV, JSON, Google/idealo feed, Parquet and trust/category companions; reimport where supported | Existing format semantics retained; optional engine absence fails clearly; malformed stdin and output permission failure do not report success or destroy old output | Real files; formats supported by exporter only |
| 06 | 06 | Two synthetic captures, suspicious change, explicit recheck, repeated report; canonical history | Native event IDs stable on replay, pending change not confirmed without support; correct DB/identity used | Real SQLite and reliable_changes, no fake comparator |
| 06 | 06b | Evidence missing/expired; bundle roundtrip; prune dry-run and explicit apply; identity migration | Lookup never refetches; roundtrip support unchanged; dry-run leaves DB unchanged; apply only declared scope; failure rolls back according to native transaction contract | Temporary databases and real persistence/export APIs |
| 07 | 07 | Shopify/Woo/Magento/Shopware/BigCommerce/generic category fixtures, foreign scope IDs, cyclic/partial Woo tree | Native/mapped distinctions preserved; invalid scope rejected; cycle/partial tree reported; unavailable tree never treated complete; portable records retain policy digest | Real adapters/mapping/validation/tree; controlled HTTP |
| 08 | 08 | Maintenance create/run/interruption/resume/report/cancel/retry using local sources | Durable job survives new CLI process; report page sizes respected; completed step not repeated improperly; same profile/allow-origin semantics as module CLI | Real store/engine with only external boundaries controlled |
| 08 | 08b | tools serve and tools call schemas/bootstrap/submit/poll/page/evidence in one process; restart | MCP stdout protocol-only; bounded foreground call exits after consuming results/closing runtime; stale handle explicitly invalid, denied origins stay denied | Actual MCP SDK/stdio process and real ToolRuntime; missing extra is explicit failure |
| 09 | 09 | Invalid JSON, unknown field, boolean/negative/zero cap, escaped identifier, timeout, SIGINT, output failure | Stable error code/exit; invalid configuration performs no network or mutation; interruption stops work and cleans up; secrets absent from diagnostics | Subprocess/controlled server/fault injection |
| 09 | 09b | watch timeout/max-events; partial extraction + pipeline; expired evidence during recheck | Finite watch emits ordered JSONL then closes; partial result exit 3 and explicit completeness; missing evidence does not become observed fact | Fake clock/external transport only; real watch/recheck mechanism |
| 10 | 10 | Clean built wheel, root/nested help, documented examples with env/config/flag conflicts | Entry point and all mapped command help work; precedence matches spec; unknown config rejected; examples parse without optional runtime activation | Bounded wheel install in disposable environment, no model/source calls |

## State and compatibility contracts

Machine envelope: `{schema_version:"1.0", ok, data, warnings, error}`; error has
stable code/message/retryable fields; partial data sets completeness explicitly.
Envelope version is independent of preserved ToolRuntime payload schema version.
Watch emits one versioned event envelope per JSONL line; status/summary on stderr.
An empty successful collection is distinct from partial, failed and unavailable.
Existing stdout/default exit behavior changes only under explicit machine mode.
Snapshot/maintenance databases, session tool handles and portable bundle IDs remain
separate namespaces. Export command reports artifact metadata through the envelope
when writing a file; streaming artifact bytes to stdout excludes a JSON envelope.

## Red-test plan

Before each implementation slice: add focused `tests/test_cli_*.py` CliRunner and
subprocess checks for its SC IDs; save failure for missing command/flag or broken
contract, not dependency/import failures. Baseline smoke already saved separately;
no acceptance-red claim in this planning deliverable. Verify branch-gate inventory
against the frozen implementation revision to account for current dirty files.

## Unobservable behavior and synthetic mechanism plan

Fixture author and independent reviewer assigned in tasks. Seed 11025; derive small
fixtures from sanitized existing tests, label synthetic URLs/times. Use production
CLI → API → parser/normalizer/matcher/store/recheck/export paths. Mock only transport,
clock or injected disk failure. Predesign SC06/06b/07/08/09b transitions so unchanged
live stores never waive their mechanism coverage. Each case has a distinct risk
above; do not inflate coverage by random seeds. Prove one critical stdout/money or
replay assertion detects a deliberate temporary fault and restore it immediately.

## Bounded stress plan

First save one 11-product smoke. Then 24 deterministic scenarios: 6 serialization/
input cases, 6 state/replay/recovery cases, 6 category/tree cases, 6 resource/cancel/
tool-session cases. Include just-below/at/above the configured item/page/byte caps.
Run sequentially, one process active, 1 MiB input/case, 100 products/case, 30s/case,
12-minute total ceiling, 512 MiB child RSS stop threshold. Cap BLAS threads at one,
intra-op at two, inter-op at one; no inference. Save progress after every case;
stop at first unexpected failure, one diagnosed repair then record any blocker.
These limits measure bounded contract behavior, not production scale capacity.

## Bounded live plan

Planning is docs-only: live checks not applicable now. During implementation,
after offline success, select and record exact previously authorized public targets
from existing saved evidence (not assumed authorized by their presence). Start
with one extraction, max 2 items/5 requests/30s. Expand to at most one source per
five native platforms plus one generic/feed source: total <=30 requests, <=12
items, <=5 minutes, sequential, no retries. Skip expansion after a source failure;
report denied/unavailable access distinctly. Browser/LLM live checks require
preconfigured authorized dependencies and a separate explicit cost/resource cap;
otherwise blocked with deterministic mechanism tests retained. Maintenance and
MCP real-process integration checks are required offline; local controlled HTTP
is not live commercial evidence. No merchant writes or evidence pruning live.
