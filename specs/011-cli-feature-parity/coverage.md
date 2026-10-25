# Public capability → CLI coverage

Baseline observed 2026-10-25 before implementation; not a clean-release claim.
Root baseline/import inventory are saved in `evidence/`. The baseline column is
historical. P0–P4 have independent final PASS. P5 runtime is implemented and
undergoing final integrated review; exact actual grammar is emitted by
`shopextract capabilities` and documented in docs/cli.md. All rows below are
implemented locally; release/publication is separate. Final evidence and remaining
verification limitations are recorded in p5/.

| Capability / public APIs | Baseline root coverage | Target command/option (child contracts authoritative) | Phase / scenarios |
| --- | --- | --- | --- |
| detect, discover | Basic commands | Same commands + machine output, supported platform/timeout controls | P1 / SC02–04 |
| extract | max/JSON/CSV/file only | extract + platform, shop URL, identifier options, trusted storefront/LLM config | P1 / SC03–04 |
| extract_one, from_feed | Missing | extract-one URL; feed URL | P1 / SC04 |
| normalize; QualityScorer.score_product/score_batch | Missing | normalize FILE; quality FILE (product/batch scores) | P1 / SC04–05 |
| resolve_fields, resolution_references; ResolutionPolicy | Missing | resolve FILE --as-of TIME --policy FILE; report includes references | P3 / SC06b |
| factual_paths, trust_view | Missing | evidence inspect FILE --view trust/paths | P3 / SC03,06b |
| compare | Query + stores only | Same command + native max-per-store/threshold | P2 / SC05 |
| compare_catalogs | Missing | compare-catalogs A B + matching options | P2 / SC05 |
| fuzzy_match, match_gtin, match_products, classify_match | Missing | match LEFT RIGHT --method identity/fuzzy; match-gtin GTIN FILE; match-pair A B | P2 / SC05 |
| assign_identity, normalized_attributes | Missing | identity assign FILE; identity inspect FILE includes normalized attributes | P2 / SC05 |
| evaluate_matching | Missing | match-evaluate DATASET | P2 / SC05 |
| migrate_snapshot_identities | Missing | identity migrate --db DB --apply (explicit mutating invocation) | P3 / SC06b |
| analyze, analyze_products | URL summary only | Preserve analyze URL; analyze-file FILE with complete statistics | P2 / SC03,05 |
| price_distribution, outliers, brand_breakdown | Missing | stats distribution/outliers/brands FILE | P2 / SC05 |
| price_position, assortment_gaps, brand_coverage | Missing | competitive position/gaps/brands with native-shaped inputs | P2 / SC05 |
| validate, check_images, find_duplicates | Marketplace text report only | --output-format json validate FILE; images check FILE; duplicates FILE | P2 / SC05,09 |
| to_csv, to_json, to_feed, to_parquet | CSV/JSON only through extraction | export FILE --format json/csv/google_shopping/idealo/parquet | P2 / SC05b |
| to_dataframe | Python object only | export --format csv/parquet covers tabular conversion; no in-memory Python object command | P2 / SC05b |
| snapshot, changes, price_history | Basic commands | Add DB, snapshot max and canonical-ID selection; history positional form retained | P3 / SC02,06 |
| watch | Missing | watch URL --interval N --max-events N --timeout N (finite bounds mandatory) | P3 / SC09b |
| monitor.watch.alert callback registration | Python callable interface | Callback objects remain Python-only; bounded watch JSONL supports external consumers. No arbitrary Python predicates or callback imports in CLI; classify declarative alert requirements at P0 before parity claim | P0/P3 / SC01,09b |
| reliable_changes | Missing | changes --reliable --previous ID --current ID [--recheck ID] --db DB | P3 / SC06 |
| save_snapshot, load_snapshot, get_evidence | Missing | snapshot-save FILE; snapshot-load ID; evidence get ID with native scope | P3 / SC06b |
| prune_evidence | Missing | evidence prune --before TIME --db DB [--apply], dry-run default | P3 / SC06b |
| create/load/read/write_evidence_bundle | Missing | evidence bundle create/load; file and stdout modes cover in-memory/file variants | P3 / SC05b,06b |
| create/load_evidence_sidecar | Missing | evidence sidecar create/load + export --evidence-output FILE | P3 / SC05b,06b |
| extract_with_categories, normalize_with_categories, validate_options | Missing | categories extract/normalize --options FILE; native storefront/enrich/restore controls | P4 / SC07 |
| map_categories, validate_observations, category portable codecs | Missing | categories map/validate/record create/load; export --categories-output preserves bindings/policy | P4 / SC07,05b |
| fetch_woocommerce_category_tree, link_tree_memberships, tree codecs | Missing | categories tree fetch/link/load/export with native guarded limits/codecs | P4 / SC07 |
| category_policy_digest, category_review_reasons | Missing | categories policy inspect/review --config FILE; maintenance composition uses P5 native durable policy binding | P4 / SC07; P5 / SC08 |
| MaintenanceEngine + configured profiles/category policies | Separate python -m shopextract.maintenance | maintenance create/run/status/report/evidence/cancel/resume/retry | P5 / SC08 |
| ToolRuntime schemas/bootstrap, discover/extract/match/changes/evidence/jobs | Separate Python API; no direct root commands | tools schemas; tools call --config FILE --request FILE, one foreground session with automatic bounded result consumption | P5 / SC08b |
| MCP stdio server | python -m shopextract.tools --config FILE | tools serve --config FILE, preserve existing module invocation | P5 / SC08b |
| Product/Variant and other exported data models/enums/contracts | Library schemas | Versioned file/envelope schemas; no constructor-per-command surface | P0–P5 / SC01,03,10 |

Non-public parser/adapter helpers remain implementation details. Public policy,
context, limits and category selector/registry dataclasses become validated config
shapes. Semantic-candidate/publisher-alias inputs use schema-defined files, not
Python callbacks or executable plugins. Internal diagnostic helpers are represented
through their parent reports. Future integrations in spec 010 remain separate.

Before G1 per implementation slice, expand its row into a machine-readable manifest
of exact callable/command/flag/schema mappings. Compare all root `__all__` entries,
module public exports and documented workflows; a new public workflow without a
mapping blocks that slice's parity claim. This initial matrix is a reviewed planning
inventory, not a claim that every proposed CLI contract already exists.

Maintenance Advisor/Investigator callback protocols remain Python extension interfaces; CLI accepts supported trusted declarative profile/goal/category configuration only. Advisor injection is not exposed as executable user input. Native category config/portable helper functions are represented by validated configuration and record create/load, with exact callable classification due at P0.

## P0 named inventory

[p0/capability-manifest.json](p0/capability-manifest.json) classifies local public
definitions/methods/re-exports and reconciles the saved AST inventory, including
callback/helper exclusions. [p0/command-baseline.json](p0/command-baseline.json)
freezes the nine legacy declarations. Reserved targets identify phase families,
not approved flags/input or payload schemas; Historical P0 design state is superseded by p0/status.md (final PASS).

## P1 delivered extraction binding (2026-10-25)

`detect`, `discover`, `extract`, `extract-one`, `feed`, `normalize`, and `quality`
now have implemented machine contracts, bounded activation controls and native
portable transport. Exact mappings/limits: [p1/capability-manifest.json](p1/capability-manifest.json)
and [p1/spec.md](p1/spec.md). Plain legacy extraction/discovery stay compatible;
new workflow browser/LLM activation is explicit and context-local. Other rows
remain dependent on their phases; this entry does not claim complete CLI parity.

## P2 delivered binding (2026-10-25, independently reviewed final PASS)

P2 implements compare/analyze/validate machine branches and matching/identity,
statistics/competitive, images/duplicates, native export commands. Exact commands,
flags and input schemas are frozen in [p2/capability-manifest.json](p2/capability-manifest.json).
Comparison native URL inputs retain source status and observed currency provenance;
new currency-safe modes leave legacy defaults intact. Evidence companion export is
implemented for native CSV/feed portable inputs; standalone bundle/sidecar lifecycle
commands and identity migration remain P3. Completion evidence/status lives in
[p2/status.md](p2/status.md); whole CLI parity remains dependent on P3–P5.


## P3 delivered binding (2026-10-25, independently reviewed final PASS)

P3 implements all monitoring/trust rows: DB/max/deadline snapshot controls,
read-only exact canonical history/classic changes, finite watch with explicitly
unverified scalar diagnostics, native reliable changes/recheck/replay,
portable snapshot save/load, resolution/references, trust/path inspection,
scoped no-refetch lookup, bounded reference-protected retention preview/apply,
native bundle/sidecar lifecycle and explicit apply-only identity migration.
Exact grammar/schemas: [p3/capability-manifest.json](p3/capability-manifest.json)
and [p3/spec.md](p3/spec.md). Legacy defaults remain intact. Evidence/status in
[p3/status.md](p3/status.md):511affectedPASS,12boundedstressgroups,actual bounded
Shopify extraction->temporarySQLite->CLIload/get smoke. Merchant price transition
remains unobserved; native synthetic mechanism evidence is separate. Whole CLI
parity remains dependent on P4/P5 and integrated package/fullrepo checks.


P4 runtime category rows now have local implementations: exact native options/runtime
configuration, scoped extraction/normalization across six platforms, deterministic
mapping/validation/bound portable records, guarded Woo tree fetch/codec/link, and
local native policy digest/reasons. Helper dataclasses/config/record functions are
composed by these commands; no arbitrary Python callbacks/plugins or constructor
commands. All catalog consumers accept categorized files; category exports require
explicit native companions, preserving runtime policy envelopes when present.
P3 product consumers use explicit ordinary projection, category files retained.
Categorized Parquet declares evidence-json-v1 structured columns and required
native companion; ordinary exports keep prior defaults. Actual focused/affected,
stress, mutation and live receipts are in p4/verification.md; independent final PASS.
One live Woo tree complete2nodes/native1GET200, auxiliary transport instrumentation
limitation stated separately; no all-platform live claim. P5 implements maintenance category composition through the same native runtime
policy contract; whole-feature package/check outcomes are recorded in p5/.


## P5 integrated operations and discoverability

Maintenance create/status/show/list/run/resume/cancel/retry/report/evidence now
compose the native explicit-DB store/engine, frozen profiles and category runtime
policy. Tools schemas preserves exactly8native public schemas; serve reuses the
genuine SDK stdio adapter and protocol-only output. Bounded tools call composes
bootstrap/native calls/poll/pages/evidence using earlier-result refs in one runtime,
then closes/reaps it; session handles never become durable IDs. Capabilities emits
actual installed nested grammar and conditional stdout contracts; schema list/show
serves packaged input/config/response/native-tool contracts without runtime launch.
Exact classified reconciliation, command paths/options and helper/data/Python-only
rationales: [p5/capability-manifest.json](p5/capability-manifest.json). Every frozen
native workflow has an actual target, with new list API and bootstrap explicitly
mapped; no command-count inference or deferred machine guard. Native module entry
points retained. Whole FR01–10/SC01–10 including suffixcases are mapped in
[p5/final-traceability.md](p5/final-traceability.md).

Actual mechanism/stress/process/SDK/full-repository/wheel outcomes and local cap/
live limitations are in p5/verification.md; final independent verdict is in
p5/reviews.md. This mapping is local implementation evidence, not publication.
