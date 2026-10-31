# Mapping tranche interface amendment

Author `/root/google_mapping_plan`,2026-10-31. Narrow G2 required before crosswalk logic.
Catalog/options already have G2/G3; use existing native observation/mapper/binder once.

The frozen skeleton crosswalk fields remain, adding `duplicate_rows:int=0` for
identical-row diagnostics. `rules` is MappingProxyType, values sorted-unique tuples;
exclusions frozenset. Loader accepts UTF8 strict JSON or safe YAML by explicit file
operation (not runtime catalog import),8MiB bytes before parse, no YAML anchors,
aliases, merge keys, arbitrary tags or duplicate mapping keys. JSON duplicate keys
also reject. Safe YAML parser caps recursive structure before schema traversal.
Only exact source inspected four-root structure is accepted. Empty/malformed root,
version mismatch, dangling endpoints, empty outputs, duplicate target IDs, unknown
source exclusion, exclusion/rule overlap or conflicting duplicate rows reject before
activation. Identical rows deduplicate and increment duplicate_rows. Expected source
hash is required64lowercasehex and checked on raw bytes before parsing. Optional
PyYAML is imported only by explicit non-JSON crosswalk load; absence gives actionable
GoogleTaxonomyError naming taxonomy-build extra, never automatic installation.

`audit_source_categories(index,source_catalog)` requires matching source version AND
fingerprint; returns ordered SourceDisposition for each actual short source ID.
Validated active indexes yield mapped-single/mapped-multiple/explicit-upstream-unmapped/
missing-rule. Parent six-status vocabulary is preserved; invalid-reference and
version-unavailable belong explicitly nonactivated diagnostic inputs, not invalid
indexes made usable by this function. Mismatched active ledger is rejected.

Proposed `effective_google_category(value,*,taxonomy)->GoogleClassification` validates
the actual CategorizedProduct original binding via categorized_product_to_record.
Frozen GoogleClassification has status:str,target_id:str|None,candidate_ids:tuple[str,...],
reason:str. Only this target namespace+registry_version decisions are eligible;
wrong catalog version/dangling targets reject. Distinct target candidates across
routes or one multiple-output route yield ambiguous/no target. Exactly one supported
nonpartial mapped candidate with no conflicting route yields mapped. No candidates
yield unavailable if no usable route else unmapped; partial candidates remain
ambiguous with reason. It never mutates source observations or grants fact support.

Crosswalk and ledger public exports live in taxonomies.google. Top-level package
exports only parse/prepare/load/options/normalize helpers as parent skeleton requires.
Crosswalk mapping in normalize validates target fingerprint; then derives only
observed Shopify-standard source rules under explicit unknown-source-version
permission. Merchant rules retain their own native explicit permission. No implicit
crosswalk inversion or overwrite of contradictory direct declarations.

Intended acceptance red: tests/test_google_crosswalk.py asserts missing public callable
before source parser import; no missing dependency/collection failure counts as red.
Mapping tranche further tests cover route conflict, unsupported source, sourceNone,
wrong scope, selected limits and effective-classification original-binding protection.
