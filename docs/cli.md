# Command-line automation

Run `shopextract --help` for root options and `shopextract COMMAND --help` for
arguments. Root options go before the command. Existing command invocations keep
their historical output and defaults.

```console
shopextract --output-format json detect https://store.example
shopextract --config ./cli.json --output-format json detect https://store.example
```

Machine responses contain `schema_version: "1.0"`, `ok`, `data`, `warnings`,
`error` and `completeness`. Read `data` only when the response permits it: success
is complete; a partial response identifies incomplete work and uses exit 3.
Errors contain a stable `code`, sanitized `message` and `retryable` flag. JSON
stdout contains one document; diagnostics go to stderr. `--diagnostics quiet`
suppresses nonessential CLI progress while preserving errors.

JSON result support covers `detect`, `discover`, `extract`, `extract-one`, `feed`,
`normalize`, `quality`, `compare`, `analyze` and `validate`, plus the P2 commands
listed below and the P4 category commands. New commands always emit JSON envelopes, including errors, except
raw artifact stdout. Monitoring/evidence and category commands implement P3/P4 machine contracts. Artifact `--format` is distinct from the root response format.

Optional CLI config is strict UTF-8 JSON, at most 65,536 bytes:

```json
{"schema_version": 1, "output_format": "json", "diagnostics": "quiet"}
```

Only those three keys are supported. Duplicate/unknown keys, nonfinite values,
wrong types, BOM and unsupported versions are errors. Select a file with
`--config PATH` or `SHOPEXTRACT_CONFIG`; no file is auto-discovered. Setting
precedence is explicit flag, selected file, `SHOPEXTRACT_OUTPUT_FORMAT` /
`SHOPEXTRACT_DIAGNOSTICS`, then legacy/normal defaults. Invalid selected settings
are rejected even when overridden. Config cannot enable models, browser execution
or trusted origins. Help/version bypass config reads/validation.

Exit statuses: 0 success, 1 operation/internal/dependency/timeout failure,
2 usage/config error, 3 partial result, 4 validation rejection, 130 interruption.
Historical legacy validation reports keep their existing exit behavior. Error
retryability does not imply an automatic retry. For scripts, put one explicit
`--output-format json` before the command; repeated root options are usage errors.

Exact schemas: [response](../specs/011-cli-feature-parity/p0/response.schema.json),
[config](../specs/011-cli-feature-parity/p0/config.schema.json), and
[error/bootstrap contract](../specs/011-cli-feature-parity/p0/contracts.json).

## Bounded extraction and local files

```sh
shopextract --output-format json detect https://example.com --timeout 15
shopextract --output-format json discover https://example.com --platform shopify --max 10
shopextract --output-format json extract https://example.com --platform shopify --max 11 -o catalog.json
shopextract extract-one https://example.com/products/item --timeout 20
shopextract feed https://example.com/feed.xml --max 100 --shop-url https://example.com
shopextract normalize raw-products.json --platform shopify --shop-url https://example.com
shopextract quality catalog.json
cat raw-products.json | shopextract normalize -
```

Machine extraction retains every product within its explicit limit; it has no
hidden ten-product preview. `--max/-n` is1–1000 (extract default20, discover100);
feed retains at most `--max` products (default1000). Feed transfer/parser limits
remain native, so the retention cap does not limit the downloaded feed size.
`--timeout` bounds the operation to a finite value greater than0 and at most300
seconds, default30 on bounded commands. Cancellation awaits async cleanup; these
are cooperative deadlines rather than OS process/resource guarantees.

Plain legacy `extract` and `discover` retain their defaults. Adding new controls
or selecting machine mode activates bounded execution. Browser and LLM execution
are off on bounded/new commands even when provider environment keys exist. Use
`--browser` only with an already configured Playwright Chromium; missing browser
setup is actionable and never triggers installation. `--no-browser` is explicit.

Extraction flags also include `--platform`, `--shop-url`, `--enrich-identifiers`,
`--restore-short-gtin` and `--storefront FILE`. The storefront file is a closed JSON
object of native string options: `endpoint`, `access_token`, `protocol`,
`token_type`, `customer_access_token`, `customer_id`. A `protocol` requires explicit
Magento selection and `graphql` or `rest`; BigCommerce token/customer options
require explicit BigCommerce and native valid authentication combinations. Keep
credentials in that trusted file, not command arguments. Field resolution policy
is a separate workflow; extraction has no field-policy argument.

Explicit inference uses `--allow-llm`, `--llm-model provider/model`, and
`--llm-key-env ENVIRONMENT_VARIABLE` (default `SHOPEXTRACT_LLM_API_KEY`). Ambient
`SHOPEXTRACT_LLM_MODEL` does not override explicit bounded model selection. An
already running `ollama/` or `ollama_chat/` endpoint needs no key; this command
never starts a server or downloads a model. Supported bounds are
`--llm-max-calls`1–10 (default1), `--llm-max-output-tokens`1–4096 (default512),
`--llm-max-input-bytes`1–32768 (default8192), `--llm-temperature`0–2 (default0.2).
The input-byte cap applies to fetched source content; each provider request also
includes one fixed extraction instruction.
Each operation shares its call allowance/deadline across nested native fallbacks,
submits sequentially, requests zero provider retries and caps requested output
tokens. **These limits are not a currency billing guarantee:** providers may bill
timed-out requests. LLM options require explicit activation. No inference is
performed by help, config parsing, normalization or quality scoring.

`normalize FILE` and `quality FILE` accept UTF-8 JSON object or object array;
`-` reads stdin once. Inputs are limited to1MiB,1000 records,64 nested levels and
100000 nodes, with duplicate keys, nonfinite values, BOM and malformed typed
values rejected. Normalize takes raw platform records and reports dropped indices;
quality also accepts native portable record arrays or extraction/normalization
result envelopes. It returns native per-product and batch scores, including an
empty batch score0. No CSV sniffing or arbitrary Python code is supported.

Extraction and normalization return native portable v1 product records, preserving
variant evidence, leading-zero identifiers, missing/false values and exact money:
`{"$type":"decimal","value":"0.10"}`. Decode these with the native portable
codec; the envelope version is independently `"1.0"`. Raw products use the native
evidence value codec. `extract-one` returns one raw captured product rather than
inventing normalized facts. `extract -o FILE` in bounded mode atomically replaces
one full JSON response envelope file after encoding; old output survives replacement failure.
Bounded extraction rejects `--format csv`; the legacy CSV path stays available.

A known incomplete source or retained product cap produces usable data with
`E_PARTIAL`, exit3, `retryable:false`, and explicit completeness metadata. Unknown
catalog coverage remains explicit metadata and does not alone fail the operation.
An empty `extract-one` has no usable partial data and fails with `E_OPERATION`.
Extraction payloads include products/raw_products, platform/tier, quality, attempted/
succeeded counts, errors, observation scope and catalog completeness/reasons.

P2 analysis and exports are available. New commands emit versioned JSON envelopes
by default; existing `compare`, `analyze`, and `validate` opt in with the root
`--output-format json` flag. Plain legacy defaults remain available. Root options
must precede the command; nested help works without activating native runtimes.

```sh
shopextract --output-format json compare 'Widget' -s https://store.example --max-per-store 20 --threshold 0.6 --timeout 30
shopextract compare-catalogs https://a.example https://b.example --max-products 20
shopextract match left.json right.json --method identity
shopextract match-pair one-a.json one-b.json
shopextract match-gtin 00012345600012 catalog.json
shopextract match-evaluate labeled-pairs.json
shopextract identity assign products.json --supplier-id https://store.example
shopextract identity inspect products.json
shopextract analyze-file products.json
shopextract stats distribution products.json --buckets 0,10,25,100
shopextract stats outliers products.json --std-multiplier 2
shopextract stats brands products.json
shopextract competitive position one-product.json --competitor https://competitor.example
shopextract competitive gaps https://store.example --competitor https://competitor.example
shopextract competitive brands store-catalog-mapping.json
shopextract --output-format json validate products.json --marketplace google_shopping
shopextract images check products.json --concurrency 1 --timeout 30
shopextract duplicates products.json --method gtin
shopextract export products.json --format csv --output products.csv
shopextract export portable-products.json --format google_shopping --output feed.xml --evidence-output feed.evidence.json
shopextract export products.json --format json --output -
```

Analysis file inputs accept flat product arrays, native portable record arrays,
or P1 envelopes containing `data.products`. `-` reads strict JSON stdin once.
The P1 byte/record/depth/node bounds apply. Concrete Product fields retain native
types: money accepts finite decimal strings or codec tags, identifiers are strings,
stock is boolean, attributes are string mappings, variants use native Variant
field names. Flat extension fields remain raw JSON data. Identity assignment uses
a typed Product projection and rejects unsupported extension fields. Portable
input preserves evidence and typed exact money. Flat data does not acquire evidence.
Pair classification requires exactly one record on each side. GTIN and fuzzy
lookup are candidates; identity matches retain native ambiguity/review semantics.

Matching configuration is declarative JSON, without Python imports or callbacks:
`{"schema_version":1,"publisher_aliases":{"00012345600012":["A","B"]}}`, or
`{"schema_version":1,"semantic_candidates":[[0],[1]]}`. Candidate row positions
align with left catalog indices; entries are right catalog indices. Rules still
determine identity. Catalog URL commands validate actual dimensions after fetch.
Evaluation rows contain exactly `id`, `a`, `b`, `label`; labels are native
`exact`, `variant`, `bundle`, `substitute`, `unmatched`, or `uncertain` relations.

Competitive brands takes a mapping of store names to catalog inputs (at most10
stores and1000 total records). Position takes one product with explicit currency
and competitor URLs; gaps and compare-catalogs take store URLs. URL operations
use bounded P1 execution with browser/LLM off, at most10 stores and1000 products
per store, default30s shared cooperative deadline. Unknown completeness is explicit;
known incomplete/failed sources return usable partial data with exit3, all unusable
sources fail. These controls do not bound native downloaded response bytes.

Machine compare groups matches by observed currency before calculating cheapest
or averages; missing currency is unranked, including a default USD scalar without
source support. Position excludes different/unknown currencies before converting
to native float aggregates and reports exclusions. Native statistics are approximate
float calculations and exclude nonpositive prices; exact original money is retained
in product transport and exports. No exchange conversion is performed.

Export formats are native JSON, CSV, Google Shopping XML, idealo TSV and optional
Parquet. Amazon/eBay are validation targets. Parquet needs pandas plus an engine
such as pyarrow; unavailable dependencies fail actionably and are never installed
automatically. `--output -` writes only raw artifact bytes, without a JSON response;
file output returns metadata. Evidence companions support portable input with
CSV/Google/idealo file outputs. Paths must differ, including symlink/hardlink aliases.
Payload and companion are staged before replacement. Each file replacement is
atomic; the pair is not a filesystem-wide transaction. A later replacement failure
restores old files/removes newly created outputs. Failed recovery retains named
backup/staged paths for manual recovery and reports failure.


P3 monitoring and evidence commands use native SQLite, comparison, resolution and
portable evidence codecs:

```sh
shopextract --output-format json snapshot https://store.example --db snapshots.db --max 20 --timeout 30
shopextract snapshot-save portable-products.json --domain store.example --db snapshots.db --metadata metadata.json
shopextract snapshot-load 1 --db snapshots.db
shopextract --output-format json history store.example "Product title" --db snapshots.db --canonical-id p_ID
shopextract --output-format json changes store.example --db snapshots.db
shopextract --output-format json changes store.example --reliable --previous 1 --current 2 --recheck 3 --db snapshots.db
shopextract watch https://store.example --interval 60 --max-events 2 --timeout 120 --max 20 --db snapshots.db
shopextract resolve portable-products.json --as-of 2026-10-25T12:00:00Z --policy policy.json
shopextract evidence inspect portable-products.json --view trust
shopextract evidence inspect portable-products.json --view paths
shopextract evidence get e_ID --snapshot 1 --record-key product/0 --db snapshots.db
shopextract evidence prune --before 2026-01-01T00:00:00Z --db snapshots.db
shopextract evidence bundle create portable-products.json -o bundle.json
shopextract evidence bundle load bundle.json
shopextract evidence sidecar create portable-products.json --payload products.csv --format csv -o sidecar.json
shopextract evidence sidecar load sidecar.json --payload products.csv
shopextract identity migrate --db snapshots.db --apply
```

Snapshot `--max` bounds URL work and retained products (1–1000); excess products
mark incomplete coverage. New network operations use the explicit execution policy
with browser/LLM disabled and a cooperative deadline (0,300] seconds. Plain legacy
snapshot/changes/history keep their existing behavior. Explicit options and JSON
use the new contracts. History keeps both positional operands, including when
`--canonical-id` selects identity; its new mode reads exact stored Decimal text
without migration. Classic changes and history read existing databases without
writes; old unmigrated identities require explicit `identity migrate --apply`.
That migration has no preview. Snapshot save and reliable comparison persist local
state; reliable reports use native replay/recheck semantics and reject foreign,
misordered or known mismatched-scope IDs before any ledger writes.

Watch requires all three finite bounds: interval (0,3600], max-events 1–1000 and
timeout (0,300]. It emits JSONL envelopes. Each native scalar-change diagnostic has
`verification="unverified_scalar_comparison"`; these are candidates, not confirmed
captured facts. Use reliable changes for confirmed events. Its terminal envelope
contains `events`, `reason` (`max_events` or `timeout`) and `initialized` (whether
the initial snapshot persisted, not whether its catalog is complete). An unchanged
store still stops at the deadline with exit3; initial capture timeout has
initialized=false. Source failure is an operation error. Cancellation exits130
and closes the generator/transport.

Metadata files are closed JSON objects:
`{"schema_version":1,"metadata":{"observation_scope":"catalog:store.example:all","catalog_complete":true,"incompleteness_reasons":[],"max_urls":20}}`.
All metadata fields are optional; scope/completeness/max may be null, meaning
unknown. Coverage is an operator assertion when importing files. Resolution policy
is `{"schema_version":1,"offer_max_age_seconds":86400,"specification_max_age_seconds":2592000}`;
optional ages default to native policy, integer1–31536000 only. Evaluation time must
include a timezone. Resolution preserves scalars and all competing observations,
returns portable products plus product/variant references, and never infers source
roles. Inspection preserves native unsupported/default distinctions.

Evidence lookup is scoped by snapshot and record key, never refetches, and returns
available/expired/missing/unsupported explicitly. Prune defaults to reference
protection and a read-only preview on an in-memory SQLite copy: original file and
schema remain unchanged. Read-only preview permits at most64MiB of logical
database pages and5seconds copying; oversize/contention fails actionably before
retention, with both connections closed. `--apply` expires selected evidence; add
`--unprotect-references` only when intentional. `--batch-size` limits one prefix
(1–1000, default100); protected prefixes can remain on later calls. Retention removes
supported access, not every residual raw/compatibility copy. Native tombstones
survive load and bundle roundtrips.

Bundle and sidecar input/output artifacts are bounded to1MiB and1000products;
output growth beyond the CLI artifact limit fails before publication. `-o` writes
an atomic native artifact; load commands write a portable product array directly
usable by snapshot-save/resolve/export. Without it stdout returns the artifact or
portable products in an envelope. Bundle load reads its bounded input once. Native bundle file and in-memory APIs are both exercised.
Sidecars accept native CSV/Google Shopping/idealo projection bytes and verify exact
digest correspondence. Only one input may read stdin. Outputs must differ from
all inputs, including filesystem aliases; invalid artifacts and publication faults
preserve previous output. P2 export `--evidence-output` uses the same native sidecar
contract. Payload hashes establish byte correspondence, not source authenticity.


## Scoped categories and WooCommerce trees

P4 uses native category extraction, observation validation, exact mapping, portable
codecs and deterministic local policy review. No model, advisor or browser runs.
All six native platforms are supported: Shopify, WooCommerce, Magento, Shopware,
BigCommerce and generic static structured data/feed sources. Source observations
and mapped target assignments stay separate. No universal taxonomy ships, merchant
IDs stay scoped, and unknown/unsupported facts never imply known empty categories.

`--options FILE` is the exact native `CategoryOptions` wire shape. Every field is
required (including nullable scope fields); unknown or duplicate keys reject.
For example, save this as `category-options.json`, replacing the store URL:

```json
{
  "scope": {"platform":"woocommerce","store_url":"https://your-store.example/shop","catalog":null,"channel":null,"locale":null},
  "registry": {"namespace":"my-catalog","version":"2026-10","target_ids":["boots"]},
  "rules": [],
  "limits": {"terms":100,"relation_refs":200,"ancestry_depth":8,"record_bytes":262144,"rules":1000,"targets":1000,"config_bytes":262144}
}
```

An empty rules array retains categories without assigning target IDs. To add an
exact rule, replace it with an array of this shape (the selector scope must repeat
the complete store scope above; `scope:null` explicitly removes that selector
restriction within the already validated source scope):

```json
[{"rule_id":"merchant-boots","version":"1","selector":{"namespace":"woocommerce:product_cat","taxonomy_version":null,"scope":null,"native_id":"7","raw_label":null,"raw_path":null,"allow_unknown_version":true},"target_ids":["boots"]}]
```

Choose exactly one of native_id/raw_label/raw_path; null taxonomy versions require
explicit allow_unknown_version. Native exact matching is case sensitive. Conflicting
rules retain ambiguous target candidates. Limits may be lowered to zero where the
native contract permits it; zero category terms preserves partial source state.
Config and each companion are capped256KiB by native codecs. All CLI JSON inputs
are read once, at most1MiB/1000records/depth64/100000nodes. Category artifacts and
entire response bytes are capped1MiB; a dual projection can exceed this limit even
when its input fits. Reduce input/limits when rejected. Only one input can use `-`.

```sh
shopextract categories extract https://your-store.example/shop --options category-options.json --max-products 2 --timeout 20 --output categorized.json
shopextract categories normalize captured-raw.json --options category-options.json --output categorized.json
shopextract categories map categorized.json --options category-options.json --output remapped.json
shopextract categories validate remapped.json --options category-options.json
shopextract categories record create categorized.json --options category-options.json --output rebound.json
shopextract categories record load rebound.json --output checked.json
shopextract analyze-file checked.json
shopextract export checked.json --format csv --output products.csv --evidence-output products.evidence.json --categories-output products.categories.json
shopextract categories record load products.categories.json
shopextract snapshot-save checked.json --domain your-store.example --db snapshots.db
```

Extract requires the URL to remain within the configured store origin/base path;
dot segments and ambiguous traversal encodings reject before HTTP. `--max-products`
is1–1000 (default20), `--timeout` is(0,300] seconds (default30). Static generic
extraction does not prove catalog coverage; partial results exit3. No usable
products is an operation failure. Native source errors never become empty success.
`--storefront-config FILE` reuses the closed native string options described for
`--storefront` above, including explicit endpoint/access credentials and native
platform auth/protocol checks. `--enrich-identifiers` and `--restore-short-gtin`
forward the native opt-in policies. Normalize also supports --restore-short-gtin.
Neither option adds taxonomy or manufacturer authority. Plain uncaptured raw JSON
can normalize products but cannot establish observed category support.

Category files are native categorized-record arrays: each record has schema_version1,
ordinary portable product, scope, observations, mappings, config_digest and
original_binding. Native digests/bindings reject mutation. Stdout includes both
products and categorized_products; category records are authoritative and an
ordinary projection must exactly match their order/content. Invalid companion
claims never fall back to ordinary products. Map/create recompute native mappings
and bind the chosen options digest; validate additionally requires matching policy
and mappings. Record load verifies without rebinding. No constructor-per-command
or executable plugin configuration is exposed.

All P2 catalog consumers and P3 product-file consumers accept categorized inputs.
P3 snapshots/resolution/evidence operate on ordinary Product projections; keep
the explicit category companion file for categories (SQLite has no category schema).
Every categorized export format requires --categories-output, including JSON and
Parquet. Native CSV/feed trust companions can be added with --evidence-output.
Categorized exports require file paths; raw payload stdout is rejected. The payload,
trust companion and category companion are staged together, each<=1MiB, then
replaced with rollback/recovery as described above. Every input/output and output
pair must differ, including symlink/hardlink aliases. Old files survive validation,
size or staging failure; failed recovery explicitly names retained backups.

For categorized Parquet, structured top-level Product fields use compact JSON
strings with the native evidence value codec (`evidence-json-v1`), preserving
Decimal tags, Unicode and empty/null values without Arrow empty structs. The
response declares structured_json_columns and structured_json_encoding. Scalar
columns retain native export behavior; the required category companion retains the
full native records. Ordinary non-category Parquet defaults remain unchanged.

Woo trees are opt-in, separate from product extraction and membership assignment:

```sh
shopextract categories tree fetch --options category-options.json --limits tree-limits.json --timeout 20 --output tree.json
shopextract categories tree load tree.json
shopextract categories tree export tree.json --output checked-tree.json
shopextract categories tree link checked-tree.json categorized.json
```

Optional `tree-limits.json` is the exact native shape with reduced ceilings:

```json
{"requests":5,"per_page":2,"categories":2,"response_bytes":1048576,"retained_bytes":1048576,"depth":8,"seconds":20}
```

Omit --limits for native defaults narrowed to1MiB response/retention in the CLI.
Only WooCommerce scope is accepted. Native seconds accepts integer/float0–30;
booleans/nonfinite values reject. Zero work produces unavailable with reasons and
no HTTP. Complete traversal returns0, partial3, unavailable/malformed1 with explicit
outcome and data. Load/export preserve outcome. Complete traversal is independent
of graph integrity: cycles, missing parents and conflicts stay inspectable issues.
Tree lookup links only already supported same-scope memberships. Missing lookup
in a partial tree does not prove absence; tree presence does not assign categories.
File output is the native tree envelope (schema_version/payload/sha256), directly
reloadable; response data.tree contains that envelope.

Local policy uses an exact `CategoryRuntimeConfig` object: `options` is the full
CategoryOptions object above and `profile_bindings` is an array of
`[target_id, profile_id]` pairs, for example `[["boots","footwear"]]`.

```sh
shopextract categories policy inspect --config category-policy.json
shopextract categories policy review categorized.json --config category-policy.json --profile footwear > review.json
shopextract export review.json --format json --output products.json --categories-output reviewed.categories.json
shopextract categories policy review reviewed.categories.json --config category-policy.json --profile footwear
```

Review reports native sorted reasons per product and exits4 when review is needed.
No profile is selected automatically. Runtime policy_digest covers options plus
profile bindings; each companion's config_digest covers options alone. Both are
validated separately with actual source scope. Export preserves runtime config and
policy_digest in a versioned category companion envelope when present; reloads
validate it. Record/map/tree-link transformations reject policy-bearing inputs to
avoid silently discarding or making policy stale; use matching policy review or
catalog export, or the original bare categorized records. Maintenance integration
uses the same native policy contract and is completed with P5 operations.

## Installed discovery and agent use

The console entry point and `python -m shopextract.cli` expose the same commands.
Use the environment where ShopExtract is installed; `python -m shopextract` is not
an entry point. Inspect once, then use explicit machine output and finite bounds:

```sh
shopextract capabilities > capabilities.json
shopextract schema list
shopextract schema show response
shopextract schema show config
shopextract schema show maintenance-goal
shopextract schema show tool-session
shopextract schema show tool:match
shopextract tools schemas
```

`capabilities` contains the actual installed nested grammar: paths, group/leaf,
arguments, option aliases, arity, required/multiple flags, defaults, choices,
numeric bounds and output contract. It does not start a runtime or extraction.
`schema list/show` reads packaged JSON Schema resources; native tool schemas are
generated from the native eight-tool contract and include input/output schemas.
Outer response `schema_version:"1.0"`, native tool response `schema_version:"1.0"`,
CLI/profile file integer `schema_version:1`, native goal/session string version,
and native unversioned tool operator/category configuration are separate contracts.
Native codecs additionally enforce cross-field scope, binding, digest and evidence
invariants described here; a JSON Schema check alone cannot establish those facts.

Read `ok`, `completeness`, `error.code` and `error.retryable` before consuming data.
Only E_TIMEOUT is retryable at the outer CLI level. Explicit pagination and partial
exit3 are part of the contract; never infer completion from a nonempty page.
Watch emits JSONL; explicit export artifact stdout emits payload bytes; MCP serve
uses protocol-only stdio. These are declared exceptions to single-envelope output.

## Durable maintenance jobs

Maintenance reads supplier sources and persists advisory findings in an explicitly
selected local database. It never writes a merchant catalog. `create`, `run`,
`resume`, `retry`, and `cancel` authorize their named local state change; they have
no merchant `--apply` or simulated merchant dry-run. Retention and identity migration
retain their own documented dry-run/apply behavior. Group options precede the
maintenance subcommand; an explicit `--db` is required for every operation.

```sh
shopextract maintenance --db ./jobs.db create goal.json
shopextract maintenance --db ./jobs.db list --offset 0 --limit 20
shopextract maintenance --db ./jobs.db show JOB_ID
shopextract maintenance --db ./jobs.db status JOB_ID
shopextract maintenance --db ./jobs.db --allow-origin https://store.example run JOB_ID --timeout 30
shopextract maintenance --db ./jobs.db --allow-origin https://store.example resume JOB_ID --timeout 30
shopextract maintenance --db ./jobs.db report JOB_ID --offset 0 --limit 20
shopextract maintenance --db ./jobs.db evidence JOB_ID EVIDENCE_ID
shopextract maintenance --db ./jobs.db cancel JOB_ID
shopextract maintenance --db ./jobs.db --allow-origin https://store.example retry JOB_ID STEP_ID --timeout 30
```

The durable ID remains valid across processes within this database. Missing DB
reads do not create a database. Status/show include native state, stop reason,
cancel intent, goal fingerprint and profile definitions. List returns jobs in
creation order; list/report limit1..1000, default100, offset>=0. Reports retain
native findings/usage/coverage/pending steps. Run/resume/retry default total30s,
range1..120s, one worker, native at most two source attempts and goal deadline/
budgets. Timeout always reports E_TIMEOUT/exit1 after cleanup even when native
cancellation returns a report; running state persists cancelled. SIGINT reports
E_CANCELLED/130 after cleanup. Cancelled jobs cannot be resumed (native invalid_state,
E_OPERATION); create a new goal. Partial/outcome-unknown jobs follow native recovery,
with explicit `retry JOB STEP` when allowed. CLI supplies no model investigator;
nonzero token/cost budgets alone cannot start inference. See
[catalog maintenance](catalog-maintenance.md) for native state/accounting semantics.

Minimal deterministic offline goal, intentionally a zero-product partial run:

```json
{"schema_version":"1.0","baseline":[{"external_id":"S1","title":"Synthetic widget","description":"old"}],"supplier_origin":"https://store.example","product_urls":["https://store.example/products/widget"],"deadline":"2030-01-01T00:00:00+00:00","budgets":{"products":0}}
```

For actual sources choose a valid future deadline, authorized origin and positive
bounded products/requests. Goal fields and defaults follow native `Goal`/`Budgets`;
unknown fields/type/version/duplicate keys reject before DB creation. Default fields
are `["description"]`; `baseline_mode` is supplied or captured (native portable
records). Selected profiles and fields must be supported. `--profiles profiles.json`
loads closed `{"schema_version":1,"profiles":{"custom-v1":{"description":{"kind":"text","role":"comparable","normalization":"exact"}}}}`.
Shipped profiles are generic-v1, hardware-v1, footwear-v1; custom names cannot
replace shipped names. `--category-config category-policy.json` uses exactly the
native options/profile_bindings record from category policy commands and persists
its policy digest with the job. Profile bindings must name configured profiles.
Subsequent execution reconstructs the frozen policy; supplied policy must match.
Custom profile definitions used by a job must be provided unchanged on execution.
`--operator-config operator.json` selects the native tool allowlist/limits instead
of repeatable `--allow-origin`; supplying both rejects. All config is declarative.

## Native tool sessions and MCP

`tools schemas` and help are static and work without the optional MCP SDK. Install
the optional extra explicitly when serving: `pip install 'shopextract[mcp]'`.

```sh
shopextract tools serve --config operator.json
# Existing module entrypoints are retained:
python -m shopextract.tools --config operator.json
python -m shopextract.maintenance --help
shopextract tools call --config operator.json --request session.json --timeout 30
```

Serve stdout is exclusively MCP JSON-RPC. Root CLI response-format/config/environment
settings are intentionally ignored on this protocol path, including invalid ambient
settings; failures use stderr and an exit code. Never pipe a CLI envelope into an
MCP transport. The eight public native tools remain discover, extract, match,
changes, evidence, job_status, job_result and job_cancel. The native MCP session
resource is `shopextract://session`. The root wrapper uses the existing SDK adapter.

Operator config retains its native **unversioned** closed object format:

```json
{"allowed_origins":[],"allowed_tools":["discover","extract","match","changes","evidence","job_status","job_result","job_cancel"],"captures":[],"limits":{"active_jobs":1,"item_count":100,"timeout_seconds":10}}
```

An empty `{}` grants no source origins/captures. Sources remain subject to native
public-origin/DNS/redirect restrictions; operator grants cannot be expanded by
request arguments or referenced content. Captures are trusted declarations
`{"alias":"baseline","db_path":"./snapshots.db","snapshot_id":1,"supplier":"shop.example"}`;
the database must be a real supported snapshot database. Origins/tools are string
arrays, captures have positive integer snapshot IDs, limits are positive finite
native types no larger than defaults. One active worker is mandatory. Config,
request and goal JSON are each<=1MiB/depth64/100000nodes; root settings remain64KiB.
See [native tool limits and trust](agent-tools.md) for per-operation byte/time/graph,
retention, cancellation and cleanup limits. CLI responses are capped at1MiB;
oversize responses fail explicitly and never silently truncate.

A `tools call` request has string schema_version1.0 and1..32 ordered closed steps,
each `{id,tool,arguments}` with a unique identifier. It creates one real runtime,
executes those steps and always closes/reaps it. Tool names are the native eight
plus CLI composition helpers bootstrap, poll and pages. Native arguments still
require their own schema_version1.0. Exact empty-bootstrap smoke:

```json
{"schema_version":"1.0","steps":[{"id":"boot","tool":"bootstrap","arguments":{}}]}
```

With a configured capture, bootstrap -> native match -> poll -> page:

```json
{"schema_version":"1.0","steps":[{"id":"boot","tool":"bootstrap","arguments":{}},{"id":"matched","tool":"match","arguments":{"schema_version":"1.0","left_catalog":{"$ref":"boot#/captures/0/catalog_handle"},"right_catalog":{"$ref":"boot#/captures/0/catalog_handle"}}},{"id":"done","tool":"poll","arguments":{"job_id":{"$ref":"matched#/data/job_id"}}},{"id":"rows","tool":"pages","arguments":{"job_id":{"$ref":"matched#/data/job_id"},"collection":"matches","page_size":10,"max_pages":2}}]}
```

References must be whole `{"$ref":"earlier-id#/json/pointer"}` objects, resolve
against that earlier step's **result**, support ~0/~1 pointer escapes and cannot
refer forward or execute code. Full step topology/literal argument validity is
checked before runtime creation; values from refs are validated natively when
resolved. Bootstrap result is raw `{schema_version,captures,limits}`; native tool
results retain native envelopes. Poll takes `{job_id,interval_seconds?}` with .01..1s,
default.05, returns the last native status envelope on succeeded, and fails on other
terminal states. Pages takes `{job_id,collection,page_size?,cursor?,max_pages?}`,
page_size1..100 default20, max_pages1..10 default10; it waits for success then calls
native job_result until completion or that cap. Result is
`{pages:[native envelopes],next_cursor,complete}`. A remaining cursor/native partial
collection returns outer partial/exit3 with retained pages; cursor path for another
step is `rows#/next_cursor`. Native evidence requests can reference bootstrap
`boot#/captures/0/owners/0/owner_handle` and a known evidence ID; they never refetch.

Session data is `{session_only:true,steps:[{id,tool,result}],completeness}`. Native
errors stop with safe E_OPERATION; malformed inputs use E_USAGE. Overall deadline
(default30s,1..120s) uses E_TIMEOUT and cleanup. Returned job/catalog/capture/owner/
cursor handles expire at the end of this invocation: they cannot be used by another
CLI process. Plan submit/poll/pages/evidence in the same request. Durable maintenance
job IDs use a different namespace. For an interactive client retaining handles,
use one MCP stdio session instead of separate `tools call` commands.

## Migrating scripts

Existing nine root commands preserve legacy defaults. Replace human-text parsing
with root `--output-format json`, inspect completeness and exits, and retain native
portable records for exact money/variants/evidence. Export `--format` selects actual
artifact formats json,csv,google_shopping,idealo,parquet; Amazon/eBay are validation
targets only. Use explicit selected DBs and apply intent where documented. No
callback/config imports or arbitrary Python function execution is supported;
Python extension protocols (watch callbacks, advisor/investigator) stay Python APIs.
`examples/cli/` contains offline inputs for normalization, discovery, bootstrap and
bounded maintenance; no external service or model is needed to run those examples.
