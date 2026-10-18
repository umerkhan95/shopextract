# G2 skeleton — declarations only, 2026-10-18

G1 independently passed (reviews.md). No runtime algorithm/stub/package resource/query producer is added here. Public interfaces below are the implementation contract for G2; executable red smoke tests the named absent API. G3 will refine concrete responsibilities, never invent a second mapper/codec.

## Namespace, immutable records and errors
New explicit public package `shopextract.taxonomies.shopify` exports the catalog/bridge/update names below; existing top-level/category APIs remain compatible.
- TaxonomyError(ValueError); TaxonomyLookupError(TaxonomyError); TaxonomyIntegrityError(TaxonomyError); TaxonomyPublicationError(TaxonomyError). Wrong argument Python type raises TypeError; unsupported version/empty ID/ambiguous alias raises TaxonomyLookupError; unknown valid nonempty ID returns None for singular lookup. Relation methods on unknown ID raise TaxonomyLookupError. No implicit casefold/slug guessing or GID-kind coercion.
- TaxonomyManifest(schema_version:int=1, namespace:str, release:str, commit:str, fingerprint:str, source_hashes:tuple[(name,sha256),...], counts:TaxonomyCounts). Frozen primitive/tuple records, no mutable exposed dictionaries. Counts include categories/base_attributes/extensions/values/context_links/parent_links/ancestor_links/return_reason_links.
- CategoryRecord(id:str,short_id:str,name:str,full_name:str,level:int,parent_id:str|None,child_ids:tuple[str,...],source_ancestor_ids:tuple[str,...],return_reason_ids:tuple[str,...]); id is ACTUAL source GID, short_id exact known suffix. Preserve source parent-first ancestry; public ancestors is documented reversal.
- AttributeRecord(id:str,handle:str,friendly_id:str,name:str,description:str,value_ids:tuple[str,...],extension_handles:tuple[str,...]); id actual canonical base GID. ValueRecord(id:str,handle:str,name:str) likewise source GID, no invented ID.
- AttributeExtension(handle:str,friendly_id:str,name:str,description:str,values_from:str,base_attribute_id:str,value_ids:tuple[str,...]); extensions have NO independent GID. All316 definitions including unused2 retained. values_from exact same-commit YAML friendly_id resolves a canonical base attribute; allowed value IDs are exactly the declared source set, no category-ancestor union.
- CategoryAttributeBinding(category_id:str,base_attribute_id:str,handle:str,name:str,description:str,extended:bool,extension_handle:str|None,value_ids:tuple[str,...]); retains category-specific override and underlying source ID.2891extended bindings remain distinct from canonical labels. Invalid/missing values_from or cycle rejects build; no fallback to a similarly named attribute.
- CategorySchema(category:CategoryRecord,attributes:tuple[CategoryAttributeBinding,...]); ProductTaxonomySchema(catalog_identity:str,resolved:tuple[CategorySchema,...],unresolved:tuple[MappingDecision,...]). Read-only metadata; no Product attributes/evidence is populated from it.

## Offline catalog and discovery signatures
```
load_shopify_taxonomy(version: str = '2026-08', *,
    catalog_root: Path | None = None, fingerprint: str | None = None) -> ShopifyTaxonomy

ShopifyTaxonomy.version: str                    # human release
ShopifyTaxonomy.fingerprint: str                # 64 lower-case SHA256 hex
ShopifyTaxonomy.registry_version: str           # '<release>@sha256:<fingerprint>'
ShopifyTaxonomy.manifest: TaxonomyManifest
ShopifyTaxonomy.category(id_or_gid: str) -> CategoryRecord | None
ShopifyTaxonomy.attribute(id_or_handle: str) -> AttributeRecord | AttributeExtension | None
ShopifyTaxonomy.value(id_or_handle: str) -> ValueRecord | None
ShopifyTaxonomy.iter_categories() -> Iterator[CategoryRecord]
ShopifyTaxonomy.iter_attributes(*, include_extensions: bool = True) -> Iterator[AttributeRecord | AttributeExtension]
ShopifyTaxonomy.iter_values() -> Iterator[ValueRecord]
ShopifyTaxonomy.attributes_for(category_id: str) -> tuple[CategoryAttributeBinding,...]
ShopifyTaxonomy.values_for(attribute_id_or_handle: str) -> tuple[ValueRecord,...]
ShopifyTaxonomy.extensions_for(attribute_id_or_handle: str) -> tuple[AttributeExtension,...]
ShopifyTaxonomy.ancestors(category_id: str) -> tuple[CategoryRecord,...]
ShopifyTaxonomy.schema_for(value: CategorizedProduct) -> ProductTaxonomySchema
```
Namespace is exactly existing `shopify:standard_product_taxonomy`. Fingerprint is SHA256 of deterministic canonical UTF-8 compact logical catalog with release/commit/schema/ordered records/contextual bindings/extension lineage/source hashes/license identity, excluding fingerprint itself and volatile download time/path. Manifest and packed resource hash bind that fingerprint. Record IDs sorted lexically for iteration; ordered source relation arrays preserved. Identity construction is implemented once and reused by importer/loader/options/schema_for. registry_version encodes release+fingerprint in EXISTING TargetRegistry.version; do not modify CategoryOptions/RuntimeConfig/portable field shapes.

Installed artifact discovery (wheel or published sdist): importlib.resources bundled `taxonomies/shopify/data/manifest.json` selects the SINGLE build-pinned identity for2026-08 and verifies resource compressed/decoded/content hashes before returning cached immutable indexes. No filesystem scan/network/YAML at normal load. Explicit catalog_root discovery uses `<root>/<release>/<fingerprint>/manifest.json` and resource; caller fingerprint selects exact identity. If fingerprint omitted, exactly one validated identity for requested release must exist; multiple candidates raise ambiguity, never choose latest. Failed imports/staging directories are not discoverable. Missing release/fingerprint fails clearly. Existing catalog instances remain immutable and usable after explicit updates; no automatic refresh.

schema_for FIRST calls existing categorized_product_to_record to validate original/nested binding, evidence/facets/codec limits; rejects mutated/dangling companion. For every mapped decision require exact target namespace AND registry_version, scope consistency and all target IDs actually in this catalog. A wrong release/fingerprint/unknown mapped target raises TaxonomyIntegrityError. Ambiguous/unmapped/unavailable decisions remain verbatim in unresolved, never counted as resolved schemas; no mapping recalculation. Resolved schemas sorted/deduplicated by canonical target ID. Metadata lookup cannot upgrade source facts or choose maintenance profiles. No full metadata enters companion serialization.

## Pipeline bridge signatures and existing seams
```
shopify_taxonomy_options(scope: CategoryScope, *, category_ids: Sequence[str],
    mappings: tuple[MappingRule,...] = (), allow_unknown_source_version: bool = False,
    taxonomy: ShopifyTaxonomy | None = None) -> CategoryOptions
normalize_with_shopify_taxonomy(raw: dict, *, platform: Platform, shop_url: str,
    taxonomy: ShopifyTaxonomy | None = None, mappings: tuple[MappingRule,...] = (),
    allow_unknown_source_version: bool = False) -> CategorizedProduct | None
async extract_with_shopify_taxonomy(url: str, *, taxonomy: ShopifyTaxonomy | None = None,
    mappings: tuple[MappingRule,...] = (), allow_unknown_source_version: bool = False,
    max_products: int = 20, storefront: ShopifyStorefrontConfig | None = None
) -> CategorizedExtractionResult
```
Options helper resolves requested known aliases to unique target short IDs; zero IDs yields valid empty registry, duplicates semantic IDs collapse, unknown ID errors. Retain existing1000targets/rules/config caps, no catalog-wide rules. Explicit mappings must already select actual source namespace/scopes and target IDs included in supplied subset; non-Shopify custom labels require these trusted mappings. For known Shopify GIDs, helper generates exact source-ID identity selectors only with explicit unknown-version permission (current adapter version None); False creates no invented source version or permissive rule. Standard vocabulary namespace+catalog registry_version determine target identity. Unknown standard GIDs never become catalog targets by name.

normalize convenience derives relevant bounded target IDs from the SAME shared adapter observation stage and caller mappings, builds finite options, then calls the existing normalizer/map/binder pipeline once. Shared categories/api orchestration may extract an internal normalize-from-observations helper to avoid duplicate adapter/mapper calls; no platform-specific mapper. Empty source remains unavailable. No entire14606-target registry constructed. Caller mappings validated before any network in extract convenience.

extract convenience preserves existing Shopify public product extraction/captures/variants. With storefront=None it adds catalog mapping/schema capability only, not an implicit Storefront request. With explicit storefront config it uses a category-only supplementary query per already captured product, at most max_products and existing request limits, then invokes the same normalize convenience. It NEVER replaces richer Product/Variant observations with the minimal Storefront payload. Domain/source-facing finite job configuration remains caller-created via shopify_taxonomy_options; per-job CategoryOptions digest remains the existing saved Store policy. Convenience per-product output may have different bounded config digests; these are not silently accepted as one job policy. Existing strict parent collection/policy validator remains authoritative.

## Explicit import/update/publication declarations
```
@dataclass(frozen=True)
ShopifyReleaseSource(version:str,commit:str,taxonomy_sha256:str,extensions_sha256:str,license_sha256:str)
async download_shopify_taxonomy_release(source: ShopifyReleaseSource, *, staging_root:Path) -> DownloadedRelease
build_shopify_taxonomy(download: DownloadedRelease, *, staging_root:Path) -> StagedTaxonomy
publish_shopify_taxonomy(staged: StagedTaxonomy, *, catalog_root:Path) -> TaxonomyManifest
```
Downloader owns allowlisted HTTPS/redirect/byte/deadline accounting only; builder owns reproducible full integrity/normalization only; publisher owns atomic filesystem publication only. Explicit updater orchestration composes these three; lookup never imports networking or YAML. Local builder uses documented optional taxonomy-build dependency for PyYAML, no undeclared runtime dependency/install. Source URLs are fixed official release/commit paths derived from validated pinned source descriptor, not arbitrary caller URLs. Limits8HTTP/10s each/60s aggregate/3redirects/8MiB gzip/128MiB decoded, one-time768MiB RSS; default runtime512MiB. Retained boundary fixtures<=1MiB; synthesize large decoded streams without saving128MiB fixtures.

Publish requires validated staged manifest/resource/source hashes and all catalog integrity passed, writes temp sibling directory then os.replace/rename to `<catalog_root>/<release>/<fingerprint>` on same filesystem, with manifest written last inside staging and directory fsync as supported. Existing identical identity is verified/idempotent; different content under same identity rejects. Failed/partial/temp dirs are not candidates; no installed-package mutation or floating active-version pointer. Lock/exclusive reservation prevents two importers publishing partial identities. Loader verifies hash/identity instead of trusting directory name. Crash before rename leaves prior discovered catalog unchanged; after atomic rename complete identity is loadable. No policy/companion migration is inferred from publication.

## Fixed Storefront query/schema/guard contract
Minimal2026-10 producer-owned query in `extractors/shopify_taxonomy.py`:
```
query ShopifyTaxonomyProduct($handle: String!) {
  product(handle: $handle) { id title handle productType category { id name } }
}
```
RootQuery.product(handle:String,id:ID):Product; Product.id ID!,title String!,handle String!,productType String!,category TaxonomyCategory(nullable); TaxonomyCategory.id ID!,name String!. Official2026-10 docs redirect to latest while version selector explicitly displays2026-10; saved compact schema proof captures that observation/date and does not pretend immutable introspection. No variants/price/taxonomy tree fields are queried or claimed observed here. Access scope unauthenticated_read_product_listings/publication visibility applies. Actual category IDs are captured API GIDs; API version is NOT taxonomy release/source observed version.

`ShopifyStorefrontConfig(endpoint:str,access_token:str|None=None[repr=False],api_version:str='2026-10',auth_mode:Literal['token','tokenless']='token')` is trusted runtime-only. Proposed amendment pending review: token mode requires nonempty supplied Storefront token; tokenless requires token=None and explicit auth_mode selection, sends no credential headers and rejects inherited conflicting client credentials. Unknown/contradictory modes fail before public/native HTTP; no retry from token denial to tokenless. Both modes retain all Storefront cache bypass. Endpoint remains HTTPS exact `/api/2026-10/graphql.json`, no embedded credentials/query/fragment; no Admin/private/customer token acquisition. Public calls pass it explicitly; ToolRuntime(...,shopify_storefront=None)/MaintenanceEngine(...,shopify_storefront=None) trusted constructor arguments route it to GuardedSources. No new user-tool payload credential fields or config/companion/job policy codec fields. Secrets never serialized/logged/hashed via asdict. ALL source-cache reads AND writes are disabled whenever Storefront config is enabled, for the complete acquisition including discovery/public-product steps. Do not key a reusable cache by endpoint/API version or credential hash. Existing category policy snapshot still binds taxonomy subset/release/fingerprint and profile config. Scope store/basepath remains merchant identity, endpoint aliases never substitute it; endpoint origin separately requires existing authorization.

Guard NativeReadPolicy gains optional exact Shopify endpoint field, defaultNone. Only explicit category_mode+matching authorized endpoint permits producer constant and body keys exactly query/variables, variables exactly one nonempty<=255-character product handle with no control chars. Wrong method/query/variables/path/version/origin denied BEFORE wire. No dynamic GraphQL, mutations, Store/Shopware association bypass or fallback query. Existing transport provides request/byte/deadline accounting and forbids cross-origin POST redirects; Storefront header additionally treated as credential-bearing for other redirect paths. Default /products.json sequence unchanged.

Supplement source flow: public captured product ID/handle -> one guarded Storefront request -> native_body errors+data with product-local diagnostics -> independently capture returned Product actual URL/time -> verify same public product ID versus returned Shopify Product GID and handle -> category leaf projection with existing `_field_sources` into public raw capture -> shared Shopify adapter/source_fact/mapping/strict binder. ID/handle mismatch, denied/null/errored category cannot overwrite original observations or become known empty; valid public products remain with explicit category-unavailable/partial diagnostics. Failed nonnull category leaves rejected through existing native_source_fact semantics. No independently observed product-attribute facts arise from catalog metadata.

Actual dispatch seams: `_try_api_extraction` Shopify category path calls existing public extractor then the ONE supplementary producer when explicitly configured; existing extract_with_categories accepts reviewed Storefront api_options protocol without changing ordinary default. New extract convenience uses that same raw acquisition seam. GuardedSources uses its existing guarded http client and trusted constructor config to dispatch this producer, then includes captured raw category/support into existing domain.parse payload. Worker normalizes via existing category mode with caller finite options; parent validates exact companion/policy before checkpoint; Storefront-enabled acquisition never reads/writes source cache, while ordinary cache validation remains unchanged. Catalog data and secrets are not sent to worker/LLM. Targeted real transport tests MUST cover producer call through both public extraction and ToolRuntime/worker/parent, not just adapter input.

## Red seam / next gate
Single test tests/test_shopify_taxonomy_skeleton.py::test_full_catalog_normalization_and_context_schema_smoke deliberately fails at missing public API, with a normal collected-test assertion and no import/collection error. Once implemented it checks full14606 count, known GID/alias, actual shared normalizer mapping/strict roundtrip and contextual schema; no taxonomy algorithm is mocked. Red command/results saved in verification.md. Stop after G2 candidate; no source stubs or business behavior, source downloads, full sweep or merchant requests here.


## G2 P1 bounded repair — source caching and checkpoint semantics
The original independent finding and original red remain recorded. Resolve with a single source-cache eligibility decision in existing acquisition orchestration: `source_cache_enabled = (shopify_storefront is None)`. Gate BOTH cache_get and cache_put with it; do not merely omit endpoint/version from cache identity or gate only one direction. Apply the same decision to discovery/public/native operations for a Storefront-enabled runtime, even if a particular supplemental request fails or returns no category. No Storefront-result cache insertion, fallback public-cache reuse, secret hash, persistent access-context schema or new permission framework.

A later runtime tokenB at the same endpoint/version performs fresh guarded acquisition;401/403/GraphQL denial remains unavailable/partial. An earlier tokenA result cannot mask that denial. A later no-Storefront job may use ordinary public cache entries but no A acquisition ever entered it. Ordinary runtimes retain existing source-cache authorization/strict decode/digest behavior and tests.

Committed same-job checkpoint replay is distinct: it may reopen the original immutable captured envelope under matching saved taxonomy policy, retaining actual old URL/time/evidence and replay provenance; it performs no new category HTTP or claim about current token visibility. Replay must not populate source cache. Uncommitted/explicit new acquisition always follows current guarded credentials plus Storefront cache bypass. Removing config does not delete historical authorized evidence or treat it as freshly reacquired. T07/T10 controlled tests assert exact request/capture-time/replay/cache behavior and never save token values.


## Packaging build lifecycle amendment — no large data in Git
Only tiny pinned release/source-hash manifest, MIT notice, importer/build code and small fixtures are tracked. Full source cache lives in existing ignored downloads/; generated resource staging in existing ignored build/shopify-taxonomy. Full compact resource path inside installed package remains taxonomies/shopify/data; repository source tree need not contain it. No .gitignore or build source edit until implementation approval.

`prepare_shopify_taxonomy_build(*, source:ShopifyReleaseSource, source_cache:Path|None, build_root:Path, allow_download:bool=False) -> StagedTaxonomy` is explicit build orchestration over the SAME downloader/builder/validator. With verified local source files it is reproducible/offline. Without inputs and allow_download=False it fails TaxonomyPublicationError with preparation guidance, not a network fallback. allow_download=True is explicit bounded source-build/release authorization; never called by ordinary installed lookup/import.

A small Hatch hook has one responsibility: validate an existing generated resource or invoke explicit opt-in preparation, and supply force_include build mappings. For wheel staging build/shopify-taxonomy/manifest/resource/license map to shopextract/taxonomies/shopify/data/...; for sdist map to src/shopextract/taxonomies/shopify/data/... INSIDE THE ARCHIVE. This includes ignored generated bytes without tracking them or mutating Git src. Both artifacts embed exactly the same catalog identity/content. Hook imports no YAML/network builder when a complete verified resource is already present (published sdist path). Generated resource verification and identity checks reused, not copied in hook.

Published sdist is self-contained for taxonomy: building its wheel consumes embedded data without taxonomy network/optional taxonomy-build dependency; ordinary Hatch tooling requirements remain normal package build dependencies. Clean Git checkout has no data, so explicit preparation/opt-in hook with pinned sources or verified local override is necessary. Missing preparation/offline inputs fail clearly; no pip runtime installation download hook, floating latest request or implicit source-code checkout auto-update.

Default source-checkout load without prepared data raises TaxonomyLookupError('Pinned taxonomy resource unavailable; prepare source build or install published package'); installed wheel/sdist load works offline immediately. Documentation distinguishes developer cold checkout from ready installed distribution. T01/T09/T12 inspect wheel/sdist members and all-record identities, assert no full source/generated bytes are tracked, and rebuild sdist wheel with taxonomy network disabled. Publishing/delivery never uses git add on generated bytes.

G3 refinement proposed: explicit prepare command owns downloads/build; Hatch hook ONLY stdlib-verifies prepared resource and force-includes it. Hook uses the SAME standalone-loadable resource.py by path, avoiding eager shopextract.__init__ application dependencies in isolated builds. Missing cold-checkout preparation fails clearly, as already required. Published sdist embedded resource builds wheel without taxonomy network/YAML. Components.md pins every file/consumer; no runtime implementation yet. Developer smoke later uses explicit session-prepared catalog_root/fingerprint; default-load proof belongs to installed wheel T12, not ignored checkout blobs.

Tokenless amendment review note: original nonempty-token-only contract is refined solely for explicit auth_mode. Official reference lists tokenless Products, but no merchant Product.category support is claimed. Endpoint/version/query/guard/access failure/budgets and runtime-only nonpersistent config remain unchanged. Do not implement producer until affected G1/G2/G3 amendment approval.
