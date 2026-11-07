# Inventory skeleton — APC03

Author: /root/coverage_author, 2026-10-25. Scope: inventory only, FR01/02/09,
SC01/02/11. Independent G2/G3 pending. Refrigerator interfaces remain deferred
until accepted inventory and refreshed pilot G1; no pilot approval is implied.

## Interface and ownership

`maintenance/inventory.py` owns offline metadata assembly:

```python
build_inventory(source_dir: Path, *, branch_files: Iterable[str] = BRANCH_FILES,
                selected_ids: Iterable[str] | None = None) -> dict
```

The declaration raises NotImplementedError until reviewed implementation. It does
not touch Store, category configuration, network, model providers or Product.
No public CLI/export is added in this slice. Coordinator writes the resulting
JSON and concise Markdown summary to this spec's evidence directory. The source
directory is explicit; there is no download or implicit full-taxonomy fallback.

`branch_files` must contain each of the three saved branches exactly once, in
any order. It cannot change the denominator or name another path. `selected_ids`
is either None (all branch nodes), or nonempty unique known IDs; order does not
affect output. Empty/unknown/duplicate IDs and invalid branch choices raise
`InventoryError('invalid_selection')`. Missing files, size/hash changes raise
`InventoryError('source_mismatch')`, before any partial report. Verify all five
files even for a one-category selection. Pins are immutable SOURCE_PINS (filename→size/hash) constants taken from the
reviewed source manifest, never trusted from a changed local manifest alone.
Tests may monkeypatch this authority boundary to hash tiny synthetic fixtures;
no runtime argument or source manifest can replace production pins.
Lazy optional YAML dependency failure raises `InventoryError('dependency_unavailable')`.
Malformed or duplicate parsed records raise `InventoryError('invalid_source')`.

## Output version 1

Root keys: `schema_version` (integer1), `source`, `denominator`, `rows`, `summary`,
`unassessed`. No current clock, absolute path, random identifier or duration in
this deterministic result. Capture run timing separately in verification receipts.

- `source`: namespace `shopify:product-taxonomy`, version `2026-08`, commit
  `2e9aa2e9b882383952c63d212add13eb80f46cf9`, files sorted by filename with exact
  `name`, `bytes`, `sha256`. Three branch YAML files + attributes.yml + LICENSE;
  total6,488,755 bytes. Pin map appears independently in acceptance tests.
- `denominator`: `branch_nodes` filename→count (663 apparel,1176 electronics,
  2286 home/garden), `category_nodes`4125, `selected_rows`, `selection` either
  `explicit_ids` or `all_saved_branch_nodes`. Counts include internal nodes and
  leaves, never claim a leaf or world denominator. Selected fridge is an internal
  node. Other branches: `unassessed` is exactly
  `{"scope":"all_other_taxonomy_branches","category_count":null}`.
- `rows`: sorted by exact category ID. Every row carries `category_id`, `name`,
  `source_file`, `source_locator` (`filename#id=ID`, a metadata locator rather than
  claimed product evidence), `parent_id` (null for branch root), `children` sorted,
  `declared_attributes` sorted verbatim (no inherited attribute expansion),
  `family`, `profile`, `policy_coverage`, `backlog_kind`, `semantic_review`,
  `candidate_fields`, `reviewed_rules`, `field_gaps`, `excluded_attributes`,
  `extraction_availability`, `binding_status`, `checked_fields`, `live_observation`.
- `family` is a proposed grouping identifier only for the three reference rows:
  `hardware`, `footwear`, `refrigeration`; null for the remainder. No prefix/name
  heuristic assigns the remaining4122 nodes to these families. All rows initially
  have `semantic_review:"pending"`; independent semantic review is a separate
  step before any exact remaining-profile count.
- `profile`: `hardware-v1` for el-6-6, `footwear-v1` for aa-8-3, null for fridge
  hg-11-7-41 and every pending node. The two existing profiles are `partial` with
  backlog `existing_extension`; fridge is `missing`/`new_profile`; all other rows
  have `policy_coverage:"unassessed"`, `backlog_kind:"review_pending"`.
  `binding_only` is a supported backlog classification with zero initial rows.
  It requires an actual reviewed adequate policy, not a taxonomy name match.
- `reviewed_rules`: exact currently implemented profile field→kind/role/
  normalization records from existing `profile()`, or empty dict. This records
  code inspection, not fully reviewed family semantics or executed checks.
  `candidate_fields` for fridge is sorted capacity/depth/height/model/width paths;
  laptop/boots initially list their existing profile attribute paths; others empty.
  `field_gaps` includes laptop `attributes/ram:numeric_capacity_policy_missing`;
  fridge maps candidate quantity/model paths to `profile_missing`; boots marks
  `attributes/size:size_system_semantics_require_explicit_input`. No numeric RAM
  capacity is inferred from taxonomy memory_technology.
- `excluded_attributes`: fridge `umbrella_opening_mechanism` maps to
  `irrelevant_to_refrigerator_policy`; it remains present in declared metadata
  for faithful source reporting, never becomes a proposed rule. Other rows empty.
  Unreviewed relevance is not silently treated as relevant.
- Six `extraction_availability` entries (shopify/woocommerce/magento/shopware/
  bigcommerce/generic) initially `not_audited`; `binding_status:"not_configured"`,
  `checked_fields:[]`, `live_observation:"not_run"`. Taxonomy/code metadata cannot
  establish extraction availability, source support, actual checks or bindings.
- `summary`: `backlog_counts` contains all four classifications, counting selected
  rows, not unique policies; `reviewed_policy_family_count:0`,
  `remaining_profile_count:null`, `generic_coverage:"common_fields_only"`.
  The two extension rows and one candidate new profile do not determine how many
  profiles the rest of these branches or the whole market need.

## Parsing, bounds and compatibility

Use existing optional `taxonomy-build` PyYAML requirement, lazy import and
safe_load, after hash/size checks. Existing full-release taxonomy build consumes
a different JSON source; do not change its pinned resource or rebuild/download it.
Resolve only selected category attribute handles against saved base/extended
definitions; do not infer enum labels or add product values. Reject duplicates,
unresolved handles, invalid children and multiple parents. No new YAML framework.

Input cap8MiB total, individual size pinned, at most5000 category nodes; complete
matrix JSON cap8MiB. Single process, no inference/workers. Do not apply runtime
1000-target cap to the offline report. Explicit runtime subsets continue through
existing CategoryOptions validation; inventory cannot install a registry.
Canonical JSON uses sorted keys/rows, UTF-8 and finite primitives; timestamps and
elapsed time belong in a separate receipt. Existing category codec remains the
authority for runtime objects; offline rows do not masquerade as portable facts.

## Acceptance and next stage

`tests/test_profile_coverage_inventory.py` defines pinned input identity, smoke
states, misleading attribute exclusion, exact denominator, branch/selection order,
scope rejection, changed-source fail-closed and real runtime999/1000/1001 bounds.
Save red result before implementation. After G2/G3: save the three-reference
smoke before full offline expansion; review pending grouping honestly, execute
repeat/order checks and repository driver, then independent APC06 final review.
Live inventory check N/A: saved reference metadata only. No refrigerator runtime
or extraction coverage claimed by this slice.

## G2 repair: reproducible fresh-checkout tests

The default pytest suite must not read artifacts/open-taxonomy-evaluation, whose
raw sources are deliberately retained locally and excluded from Git. Default
acceptance builds a deterministic7-node source-shaped YAML corpus (2 electronics,
2 apparel,3 home/garden nodes plus4 attribute definitions and synthetic LICENSE).
Only SOURCE_PINS authority is monkeypatched to these fixture bytes/hashes. The
real future file reading, hashing, YAML parsing, graph validation, selection,
profile projection, counters and sorting all execute unchanged. No parser or
algorithm fake. Names/references are synthetic metadata, never live evidence.
Default-pin identity/immutability assertion independently freezes the real pins.
Production branch/total counts are computed from verified source contents; the
4125 actual denominator is an acceptance expectation, never hardcoded output.

Default tests assert7 nodes and4 review-pending rows. Additional distinct adverse
cases cover empty selection, repeated branch filename, missing file, changed
unselected source, malformed YAML, duplicate category ID and dangling child.
Malformed fixtures are deliberately re-pinned by test-only authority so the real
parser can reject them rather than stopping at a hash mismatch. They are not
replacement comparison/parser implementations.

Separate evidence/retained_inventory_acceptance.py is an explicit acceptance
driver over the actual retained5-file corpus. It verifies exact pins and real
4125 denominator,3 reference attribute counts19/16/10,4122 pending rows and repeat
ordering. It never skips missing files, silently refreshes or downloads. Its
current intended red is NotImplementedError after5 hash passes. After G2/G3 and
implementation run it explicitly, save the three-reference smoke before complete
expansion, then save full matrix. This separate actual-corpus gate remains
mandatory for APC05/06; synthetic pytest success cannot substitute for it.

Implementation review refinement: materialize iterable input through islice with
4 branch names/5001 IDs maximum, reject more than3 branches/5000 IDs. Tiny added
cases distinguish disconnected cycle, unresolved attribute and iterable resource
admission risks; see test-design.md. These refine existing graph/link/budget
contracts without changing valid report output.

## Refrigerator pilot interface candidate — APC07

Inventory is finalized; refreshed pilot G1 remains pending. Exact behavior,
quantity shape/unit IDs/reasons, opt-in source capability, snapshot/identity guards,
page-scoped report keys/serialization and inventory overlay are specified in
[pilot-contracts.md](pilot-contracts.md). These are declarations in documentation
only; no production signatures/stubs or implementation were added. Pilot G2 will
freeze callable signatures, validate carrier types and write intentional failing
acceptance tests after independent refreshed G1 (APC08), then pilot G3.

Mandatory boundaries: existing profile records remain3keys; quantities have
explicit axis/total semantic wrapper and versioned normalization identity; legacy
normalization defaultFalse; trusted explicit refrigerator selection enables source
capability; exact category policy/binding still required; existing Store snapshots/
findings own diagnostics, no new persistence table or independent engine. Report
is opt-in and scoped to actual finding page; old unavailable metadata never turns
into checked coverage. No weight field in9-field pilot.

## APC09 exact pilot interfaces and ownership — G2 candidate

APC08 refreshed G1 passed in reviews.md; pilot G2/G3 pending. These declarations
are documentation only; no production stubs introduced. Tests exercise missing
interfaces directly and fail at intended absent behavior, not during collection.

| Owner | Signature/type contract | Consumers / errors |
| --- | --- | --- |
| _models | QuantityValue TypedDict(value:str\|int\|float\|bool\|None,semantic:str); Product/Variant.attributes:dict[str,str\|QuantityValue] | Same constructor order/default; finite closed carrier checked by portable layer; semantic meaning checked by quantities |
| _portable._check_type + portable-product.schema.json | Existing type checker adds only closed QuantityValue support; existing finite-tree validation remains | Extra keys,nested/list value,nonstring/>32semantic,>128value string reject ValueError; finite invalid source scalars survive |
| maintenance.profiles | FieldRule kind adds volume,length; `compare_field(rule,before,after,*,raw_before=_UNSET,raw_after=_UNSET)->dict` | Existing3 kinds/results unchanged; raw_* metadata cannot upgrade unsupported before/after to equality or normalized values |
| maintenance.profiles | `profile('refrigerator-v1')->CategoryProfile` | Exactly9 fields, axis-specific normalization IDs and roles in pilot-contracts.md |
| _normalize.normalize | Existing args plus keyword `include_refrigerator_attributes:bool=False` | Only opted-in generic SchemaOrg projection, source outcomes use exact label/value inputs |
| categories.api.normalize_with_categories | Same additive defaultFalse keyword | Reuses normalize; companions retain capture/config integrity |
| tools.runtime.ToolRuntime / tools.sources.GuardedSources | Constructor keyword include_refrigerator_attributes:bool=False | Trusted engine derives from persisted selection, never public tool/source argument |
| tools.domain parse | Parent-owned payload key include_refrigerator_attributes:bool=False | Validated bool propagated to categorized/plain normalizer; no network/model fallback |
| maintenance.engine | Run/resume/recheck creates same per-job capability; new `_quantity_candidate` private helper returns present raw typed value or missing sentinel | Source support remains authoritative; comparison uses supported inputs; raw candidate metadata preserves empty/null/missing/expired distinctions |
| maintenance.store._profile_record + maintenance-profiles.schema.json | Add exact volume/axis-length kind+normalization pairs | Existing record3keys/custom format/collision validation unchanged; mismatch before mutation |
| maintenance.store.report | `report(job_id,*,offset:int=0,limit:int=100,include_profile_coverage:bool=False)->dict` | Default shape unchanged;1..1000 cap, SQL page-before-materialization and advisory overlay only selected IDs |
| maintenance.reporting (new small shared owner) | `encode_coverage_response(envelope:Mapping)->bytes` | Compact finite UTF8+newline,<=1048576; throws MaintenanceError(resource_limit) before success output |
| _cli_operations.maintenance_operation | Report parameter include_profile_coverage:bool=False | Public operation/native report returns same data |
| _cli_operations report / maintenance.__main__ report | `--coverage` optional flag | Actual root/module envelopes use shared preflight; existing single error envelope remains allowed, no success bytes before size check |
| maintenance.inventory.build_inventory | Existing args plus include_current_policy:bool=False | Default baseline schema1 unchanged; true produces current-policy schema2 with baseline digest and explicit selected-field overlay |

`raw_before/raw_after` default _UNSET means derive input metadata from ordinary
comparison arguments. New quantity before/after remain the supported values
returned by _supported; raw metadata is solely candidate presence/type/state.
A source label/value empty/null may create a typed normalized candidate wrapper
with UNKNOWN support; record the wrapper for diagnostic state without promoting
a fact. `_quantity_candidate` reads the real preserved normalized candidate path;
missing sentinel only when path is genuinely absent. An expired/LLM/unsupported
raw250L still leaves comparison unknown and normalized valueNone; input state can
be value, input reasonNone, blockers explain unavailable support. Unknown historical
raw state stays unknown rather than reconstructed guessed values. No new table.

Current overlay schema2 retains the same pinned-source/denominator rows structure,
adds baseline_digest=SHA256(compact sorted finite UTF8 baseline schema1), and
updates only exact hg-11-7-41 to profile refrigerator-v1,
policy_coverage implemented_selected_fields,implemented_fields sorted9,
whole_family_coverage incomplete. Bindings,actual checked fields and live states
remain unchanged (checked[],live not_run); runtime job evidence never inferred.
Summary preserves unknown remaining count; baseline workload counts must be
explicitly labelled baseline_backlog_counts in schema2 to avoid claiming the new
profile is still absent. Requesting baseline again reproduces original bytes.
Axis definitions and implemented field digest are taken from actual profile()
registry, not another duplicate operational rule table. Profile missing while
requesting current overlay fails invalid_selection, not fabricated implementation.

### Executable test ownership and scope

- test_profile_quantities.py: exact rules/precision/invalid semantics/profile/custom
  schema coherence, bounded input and raw metadata cannot upgrade support.
- profile_coverage_helpers.py: tiny synthetic source factories only; actual HTML
  parser/capture/normalizer, trusted policy and real Store/engine. No mocked matcher,
  quantity parser, persistence or source evidence. Direct _reconcile cases omit
  acquisition explicitly; separate actual run/resume tests cover nested capability.
- test_profile_coverage_integration.py: real support/pointer/portable/type cases,
  finite invalid scalar engine outcomes, binding/identity/absent rule and immutable
  snapshots, actual controlled-transport run/replay. Labelled corrupt-state case
  writes missing-rule goal only after valid public creation; public admission stays
  rejected. Source empty/null gets separate real-path states and no checked count.
- test_profile_coverage_cli.py: real committed legacy-shaped outcome fixtures in
  SQLite; report SQL paging guard,API/root/module parity,help flag and actual UTF8
  serialized-envelope budget. Fixture outcomes deliberately mark unavailable
  support; they do not fabricate executed engine comparisons. No full report path
  may call unbounded _findings for opt-in page. Serializer has3 concrete consumers
  (API report payload guard,rootCLI,moduleCLI) and no dependency back onto CLI.
- test_profile_coverage_inventory.py adds one tiny synthetic overlay acceptance;
  original retained4125 result is reused, never restarted by this stage.

Existing unchanged acceptance/profile recovery/custom validation tests remain
baseline regressions: tests/test_maintenance_acceptance.py field roles, custom
frozen snapshot/recovery and profile identity change; existing category companion
portable guards and tests/test_cli_operations.py custom profiles/schema examples.
Required final full driver remains separate from this intentionally failing stage.
