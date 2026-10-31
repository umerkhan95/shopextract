# Google integration typed skeleton candidate

Date:2026-10-31. Declarations only, no production implementation. G1/G2 pending.

## Google catalog family

`contracts.py`: GoogleTaxonomyError(ValueError), GoogleTaxonomyIntegrityError,
GoogleTaxonomyLookupError, GoogleTaxonomyPublicationError. Frozen records:
`GoogleCategory(id:str,name:str,full_name:str,parent_id:str|None,child_ids:tuple[str,...],ancestor_ids:tuple[str,...])`;
`GoogleCounts(categories:int,roots:int,leaves:int,parent_links:int)`;
`GoogleManifest(schema_version:int,namespace:str,version:str,locale:str,source_url:str,source_sha256:str,fingerprint:str,counts:GoogleCounts)`.
GoogleManifest additionally retains source_kind:str,
source_provenance:GoogleSourceProvenance|None and catalog_sha256:str.
GoogleSourceProvenance is frozen with exactly source_kind/source_url/source_commit/
source_sha256/derived_sha256. Accepted source_kind: google_txt or
shopify_google_snapshot; mirror requires nonempty HTTPS source_url,40lowercasehex
source_commit and64lowercasehex original YAML/derivedTXT hashes. Optional parser
provenance is a dict with exactly those five keys, never executable/arbitrary data.
Parser validates consumedTXT SHA256 equals provenance.derived_sha256. google_txt
may use provenance=None; fixtures may leave source_url empty without asserting
acquisition. Main source_sha256 is actual consumedTXT hash; provenance preserves
original YAML hash independently. Fingerprint binds source_kind and provenance.

`source.py`: `parse_google_taxonomy(text:str,*,locale='en-US',source_url='',expected_sha256=None,provenance=None)->GoogleTaxonomy`.
Official Google TXT header+`ID - full > path` parser. Mirror/YAML requires a
separate explicit parser/format/provenance contract; never auto-sniff arbitrary data.
`catalog.py`: immutable GoogleTaxonomy(manifest,indexes), `registry_version:str`,
`category(id:str)->GoogleCategory|None`, `resolve_path(path:str)->GoogleCategory|None`,
`ancestors(id:str)->tuple[GoogleCategory,...]` root→parent,
`children(id:str)->tuple[GoogleCategory,...]`, `iter_categories()->Iterator[GoogleCategory]`.
Invalid argument type raises TypeError, unknown nonempty ID/path returnsNone.

`prepare.py`: `prepare_google_taxonomy(source_file,catalog_root,*,locale='en-US',expected_sha256=None,source_url='',provenance=None)->Path`.
Returns published immutable resource DIRECTORY, not changed global pointer.
Optional provenance is a strict bounded declarative source record, not executable
config. source_kind distinguishes google_txt from shopify_google_snapshot; mirror
requires source_url/source_commit/source_sha256(original YAML)/derived_sha256(TXT).
Manifest source_sha256 is the consumedTXT digest; provenance preserves original
YAML digest independently. Fingerprint binds both. Never relabel derived bytes as
original Google-download bytes; explicit operator source preparation only.
`loader.py`: `load_google_taxonomy(version='2021-09-21',*,locale='en-US',catalog_root=None,fingerprint=None)->GoogleTaxonomy`.
Explicit root layout `<root>/<version>/<locale>/<fingerprint>/manifest.json`;
one matching resource allowed without fingerprint, multiple ambiguous. Packaged
resource route uses package data only if actually provisioned and integrity valid.
`resource.py` validates strict manifest/catalog digests; `publish.py` atomically
adds complete immutable directory and never overwrites prior valid identities.
Directory contains manifest.json and catalog.json. Canonical payload has exactly
schema_version1,namespace,version,locale,source_url,source_sha256,source_kind,
source_provenance,categories. categories has exact GoogleCategory records sorted
by numeric ID; source_provenance is strict five-key object or null. Canonical
bytes are UTF8 JSON ensure_ascii=False,sort_keys=True,separators=(',',':'),
allow_nan=False,no newline. fingerprint=catalog_sha256=SHA256(payload bytes).
Manifest has exactly GoogleManifest fields; counts exactly GoogleCounts fields.
Loader verifies byte hash plus metadata/counts/edges even on cached reuse; a
manifest never hashes itself. Payload8MiB/manifest64KiB resource ceilings.

## Native category integration

`options.py`: `google_taxonomy_options(scope,*,category_ids,mappings=(),allow_unknown_source_version=False,taxonomy=None)->CategoryOptions`.
namespace `google:product_category`; registry_version includes release/locale/hash.
Identity rules generated only for selected IDs/full paths under exact source
version permission. Scope is native CategoryScope. Existing validate_options owns
limits; do not clone native category contracts or the mapping algorithm.
`api.py`: `normalize_with_google_taxonomy(raw,*,platform=Platform.GENERIC,shop_url='',taxonomy=None,mappings=(),crosswalk=None,allow_unknown_source_version=False)->CategorizedProduct|None`.
Normalize/observe once, resolve relevant targets, construct finite native options,
invoke `_bind_categories`. Source observations unchanged; target facts remain
derived decisions. Multiple candidates remain native mapped/ambiguous as encoded;
effective classification helper may expose at most one conflict-free target.

`crosswalk.py`: `load_shopify_google_crosswalk(source_file,*,source_catalog,target_catalog,expected_sha256)->ShopifyGoogleCrosswalk`.
`source_ledger.py`: `audit_source_categories(crosswalk,source_catalog)->tuple[SourceDisposition,...]`.
SourceDisposition frozen fields: source_id:str,status:str,target_ids:tuple[str,...],
reason:str; canonical parent six-status partition, source IDs are Shopify shorts.
ShopifyGoogleCrosswalk frozen fields: input_taxonomy:str,output_taxonomy:str,
source_sha256:str,source_catalog_fingerprint:str,target_catalog_fingerprint:str,
rules:immutable source-shortID→sorted-unique-target-ID mapping,
explicit_exclusions:frozenset[str]. Source YAML root keys exactly input_taxonomy,
output_taxonomy,rules,unmapped_product_category_ids. input_taxonomy equals
'shopify/'+source_catalog.manifest.release; output_taxonomy equals
'google/'+target_catalog.manifest.version. Every rules item is exactly
{input:{product_category_id:shortstr},output:{product_category_id:[decimalstr]}};
exclusions is an array of source shortstrings. Safe duplicate-key-rejecting YAML,
no arbitrary tags/objects;8MiB source ceiling and hash checked before parse.
Every input resolves in source_catalog.category(shortID), output resolves in
target_catalog.category(decimalstr); empty outputs/invalid keys/types/unknown
endpoints/exclusion-rule overlap reject before usable index. Repeated identical
rows may deduplicate with explicit diagnostics; conflicting duplicate input rows
reject; multiple output IDs in one valid row remain mapped-multiple.
Version mismatch rejects active loading; diagnostic ledger version-unavailable
requires explicitly nonactivated diagnostic input, never mismatched active index.
Source/target fingerprint bind index identity; no reverse inference. Merchant
source versionNone still requires explicit caller permission before pinned rules.

Top-level `shopextract` exports parse/prepare/load/options/normalize Google helpers;
`taxonomies.google` owns typed catalog and crosswalk APIs. CLI thin adapters use
these helpers and existing `_cli_core` envelopes/registration; no duplicated parser.
Catalog operations/list pagination not copied into bounded Product/job configs.
