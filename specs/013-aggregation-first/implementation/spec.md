# Google taxonomy integration: executable child contract

Date:2026-10-31. Author:/root/taxonomy_contract_author. Parent FR01–03/10–13,
SC01–03/10–15. Candidate child behavior, pending independent G1. User has now
authorized implementation; this document does not record completed gates.

## Outcomes and requirements

GFR01 Load the COMPLETE pinned English Google taxonomy into an immutable indexed
catalog. Every parent/leaf ID and exact full path resolves; ID/path uniqueness,
parent existence and counts must validate. Preserve source bytes/hash/URL/locale,
reported version and generated fingerprint. No downloads during import/lookup.
GFR02 Separate source parsing, catalog indexing, resource integrity/loading and
atomic publication. Validated immutable resource directories coexist; invalid or
interrupted publication leaves prior resources readable. Explicit wrong hash,
duplicate paths/IDs, malformed encoding, invalid paths or ambiguous resource
selection fail before activation; unknown ID/path lookup returns None.
GFR03 Map Google IDs/full paths through existing CategoryObservation,
CategoryOptions, map_categories and categorized portable binding. Full catalog
stays outside jobs; relevant subsets obey1000targets/rules,100terms,200refs,
256KiB config/companion and ancestry8. Do not change existing lower bounds.
GFR04 Generic feed observation taxonomy_version remains None. Identity mapping
requires explicit allow_unknown_source_version=True; target pinned identity never
changes source observation version/support. Unknown/missing/unsupported category
retains product and explicit unmapped/unavailable decisions. No taxonomy fact
becomes product/variant specification evidence.
GFR05 Import only audited directional Shopify→Google crosswalk data against exact
source/target catalogs/digests; no reverse inversion. Canonical source ledger is
the parent six-status ordered partition. Invalid rows/exclusion contradictions
block publication; source diagnostics do not become phantom source categories.
GFR06 Reuse all six platform category adapters and trusted merchant-scoped rules.
Same numeric IDs/labels across stores never imply equivalent Google categories;
custom memberships/tree metadata stay distinct. Conflicting routes remain
ambiguous; many target candidates are not an asserted effective single category.
GFR07 Expose explicit Python and taxonomy CLI operations with existing response,
schema/capability and category/evidence export contracts. Selected complete
resource route supports installed offline lookup; old Product.attributes,
Shopify resource/default output, native snapshots and maintenance remain intact.
GFR08 Verify exact target-set equality through real parser/options/capture/mapper/
binder/codec/public projection/export and separately audit every source ID.
No skipped valid target, fabricated live membership or count-only completion.

## Acceptance scenarios

GSC01 Two roots/seven nodes/four leaves yield exactly2/7/4 and reciprocal edges.
GSC02 Duplicate/missing-parent/wrong hash/corrupt update rejects; prior resource loads.
GSC03 Exact ID and full-path feed declarations map with supported source facts,
retain source versionNone, and survive strict categorized record reload.
GSC04 Denied unknown-version permission or unsupported/missing source never maps.
GSC05 Relevant target/rule999/1000/1001 and byte boundaries obey existing caps.
GSC06 Directional crosswalk validates endpoints/exclusions, partitions all source
IDs exactly once, preserves multi-target ambiguity and rejects invalid activation.
GSC07 Six adapter source-shaped fixtures and native/Python/CLI/export agree;
legacy Shopify/string attributes/default outputs remain unchanged.
GSC08 Every pinned target ID passes actual integration, installed resource and
offline package checks; source-resource/live observations reported separately.

## Boundaries

This child implements taxonomy integration, source mapping, taxonomy API/CLI and
resource preparation only. New aggregation/group/offer/specification engines in
parent GAG13–18 remain separate consumers and are not claimed complete here.
Acquisition route/header/hash must be real; official Google bytes or an explicitly
audited upstream-maintained equivalent snapshot must be distinguished, never
present a converted mirror as bytes downloaded from Google's original endpoint.

## Source-route amendment for independent G1

Parent's one direct Google request was denied by the environment proxy403; no
bypass attempted. Explicit operator-provisioned route uses pinned official
Shopify Google integration snapshot at commit2e9aa2e9b882383952c63d212add13eb80f46cf9.
Its full_names.yml contains5,595Google IDs/21roots/maxdepth6,577,969bytes,
SHA2564b6fcdaf79f501a4f5cef9d35b95749b021c0cff48baeb3fd8be6733d1e9bee6.
The derived ignored TXT is482,896bytes,
SHA25630039729880ec5ac4851de088ad228a6898aa253f0de5d5ebea5bb1437478fce.
Its header declares the upstream release from source metadata, not an observed
direct Google-file header. Manifest must bind source_kind=shopify_google_snapshot,
original URL/commit/YAML hash and derivedTXT hash. No raw corpus is committed or
bundled without separate resource distribution decision. This explicit route
must independently pass G1; the earlier planning verdict did not approve it.
Parent inspected forward source:14,528rules+78explicit exclusions=14,606Shopify
IDs;5,455distinct target IDs, zero invalid targets/multioutputrows.140Google
targets lack inbound Shopify mapping but remain required direct Google targets.
