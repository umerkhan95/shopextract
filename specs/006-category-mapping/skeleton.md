# Category code skeleton — G2 candidate, 2026-10-17

G1 passed by category_reviewer (reviews.md). This revision contains typed declarations,
explicit NotImplementedError stubs and executable intended red seams only; no mapper,
parser, source-support algorithm, codec, query dispatch or maintenance business behavior.
No components.md is written before G2. Existing common code/default APIs untouched.

## Public and typed contracts

The explicit namespace is `shopextract.categories`; importing it must not replace any
legacy top-level entry point or Product/Variant fields. `contracts.py` is the single
source of dataclass field signatures, literal enums and frozen container declarations.
- `normalize_with_categories(raw, platform=GENERIC, shop_url='', *, category_options,
  restore_short_gtin=False) -> CategorizedProduct | None`: ordinary Product validity,
  source translation and shared mapping, preserving raw support before compatibility loss.
- `async extract_with_categories(url, *, category_options, **extraction_options) ->
  CategorizedExtractionResult`: whitelist the existing extract keyword options; reject
  unknown keywords/invalid config before network. Existing ordinary extract unchanged.
  Category mode uses native optional templates, retains raw capture into normalization,
  disables category-error-triggered fallback/retry; never invokes an extra model classifier.
- `validate_options(CategoryOptions) -> None`: raises CategoryError(ValueError) on invalid
  config/targets/limits/selectors; entry points validate even frozen dataclass instances.
- `map_categories(tuple[CategoryObservation,...], *, options) -> tuple[MappingDecision,...]`:
  exactly one shared mapping entry point, all adapters independent of it.
- `categorized_product_to_record(CategorizedProduct) -> dict` and reverse decoder:
  explicit schema_version1 envelope containing ordinary portable Product record, scope,
  observations, mappings, config_digest and original_binding. Exact keys/version/bounds
  validated; record never accepted by unchanged legacy product_from_record.

CategoryScope(platform,store_url,catalog?,channel?,locale?) is observation scope. Preserve
configured shop/basepath/catalog; endpoint is not identity. Unknown channel/locale stays
None. Term ref(namespace,taxonomy_version?,native_id?,merchant_scope?) separates vocabulary
identity from observation scope. Merchant ownership is canonical configured shop/catalog;
standard global vocabulary ownership is None. Opaque IDs retain exact text, no UID decode.
Selectors carry exact namespace/version plus optional scope/native_id/raw_label/raw_path;
exactly one representation selector is valid, unknown version requires explicit permission.
Optional selector scope None explicitly means all assignment scopes; non-None scope is
exact equality including unknown values. No implicit wildcard string or missing-field match.
Registry(namespace,version,target_ids) is caller trusted; rules(rule_id,version,selector,
target_ids) finite. MappingDecision records source observation/ref, target namespace/version,
matched rule versions, per-term status and partial flag. Canonical target set disagreement
is ambiguous union, not intersection; independent terms may map to multiple targets.

CategoryFact(pointer,raw_value,SupportState,evidence tuple,reason) reuses existing Evidence,
including actual URL/time and retained support. `source_fact(raw,pointer)` is a shared stub
for capture/Normalizer resolution; absence/truncation/mutation/LLM does not gain support.
Source term facts cover ID/label/code context; observation facts cover field state and
completion metadata. New evidence attaches to companion through these fact tuples,
never an unrelated Product field masquerading as category. Codec deduplicates/validates
refs using existing evidence semantics; it preserves competing support and transformations.
Source facts do not contain mapping rule claims. Mapping decisions retain source pointers.

CategoryObservation stores observation_id, scope, relation label/memberships/ordered_path/
parent_edges/index, taxonomy_kind, source_state, completeness, terms, proven edges,
facts and reason. Tuple order means ancestry only for ordered_path. Other semantic sets
are order invariant while original leaf pointers/raw source facts retain capture ordering.
CategorizedProduct is frozen but Product remains compatible/mutable: immutable original_binding
must bind full strict portable Product+scope and be checked at both encode/decode; encoder
rejects changed wrapped Product, never silently recomputes. Explicit rebuild revalidates
source support. Config digest excludes credentials and includes exact full rules/registry.

## Stable platform adapter contract and file ownership

Each dedicated author owns only `categories/adapters/<platform>.py` and their existing
extractor/parser modules after G3. All six implement exactly:
`observe_categories(raw:dict, *, context:AdapterContext) -> tuple[CategoryObservation,...]`.
Context supplies scope/limits and bounded NativeCategoryError(path tuple-or-None,code)
operation diagnostics. No callback/model/HTTP/registry/mapper/storage in adapters.
Adapter emits facts with shared source_fact; it cannot infer hierarchy or grant support.
Missing category input yields explicit unavailable/missing observation, not empty tuple
with fabricated complete status. Exact source field shapes are in platform findings.

| Adapter | Namespaces / semantics | Native acquisition |
| --- | --- | --- |
| shopify | shopify:product_type custom; shopify:standard_product_taxonomy standard; shopify:collection merchandising | Existing public type; other namespaces unavailable unless captured |
| woocommerce | woocommerce:product_cat merchant | Existing product categories membership |
| magento | magento:category merchant opaque UID | Optional categories { uid name }; no Store header/tree |
| shopware | shopware:category merchant membership and separate index observation | Existing categoryIds/categoryTree; no new association |
| bigcommerce | bigcommerce:category merchant | Optional categories(first:20), pageInfo and entityId/name/path |
| generic | schema.org:category; exact CategoryCode inCodeSet URI; google:product_category standard; google:product_type custom; opengraph:product_category merchant | Captured declarations only; feed retention before collapse; no URL crawl |

No standard taxonomy release invented. Schema.org vocabulary version is not merchant
term version. Explicit CategoryCode without inCodeSet remains unresolved namespace claim.
Legacy category_path/default source exports remain unchanged, including existing splitting.

Shared author alone owns `categories/contracts,api,evidence,mapping,portable,maintenance,
native.py`, common `_normalize.py`, `_extract.py`, `_portable.py`, security/tool/domain
process/cache/checkpoints and public package integration. Platform files import shared
contracts/helpers, never mutate core or register separate mappers. Parent schedules
implementation to avoid shared-file collisions; adapters acknowledge research decisions.

## Native request and error seams (declarations only)

native.py declares verified selection fragments. G3 extractor producers compose separate
complete `_CATEGORY_QUERY` constants; `_QUERY` defaults remain byte-for-byte compatible.
Shared guard imports producer constants directly and permits optional constant only in
trusted category mode. NativeReadPolicy gains default-false category mode seam under
shared ownership. No duplicated producer/validator body, arbitrary GraphQL or new tree API.
BigCommerce first20 no followups; limit0 uses ordinary product query with category unavailable.
Magento GET optional fields stay inside current bounded request; no POST conversion.

`_category_diagnostics` is reserved ephemeral raw operation metadata (tuple of bounded
path/code records), attached after source capture by native extractor/shared response
handling and carried into AdapterContext. It is never a category source field, evidence,
URL/time claim, identity input or way to raise SupportState. It can only downgrade
completeness. Code/path length and count consume existing byte/category caps; arbitrary
messages/tokens/credentials are excluded. Normalize wrapper consumes this metadata;
companion retains sanitized reason/facts while source_fact selects original capture only.
Thus valid product siblings survive GraphQL errors+data; relevant category errors partial
with retained terms or unavailable without; missing/malformed pageInfo unknown; no-path
errors conservative; rejected query/access denial no hidden fallback. Current json_body
legacy behavior changes only through a new reviewed opt-in response seam, not globally.

## Maintenance / child-process / cache seams (declarations only)

`CategoryRuntimeConfig(options,profile_bindings tuple[(target_id,profile_name),...])` is
trusted runtime configuration. Shared owner adds optional `category_config=None` to
MaintenanceEngine runtime construction; legacy Goal dataclass/default schema unchanged.
Persist validated config digest/version in job policy on creation; resume requires same
runtime digest or explicit category-policy mismatch, never silent remap of old checkpoints.
`category_policy_digest(config)->str` includes schema/scope/full registry/rules/profile
bindings, excludes credentials. `category_review_reasons(value,*,selected_profile,config)`
returns category_unavailable/category_ambiguous/category_unmapped/profile_binding_missing/
category_profile_conflict as applicable; mapping agreement never grants matching authority.
Ordinary jobs do not call this seam and retain old explicit-profile behavior/veto.

GuardedSources optional category config -> domain parse payload explicit category mode +
validated config, original captures + bounded diagnostics -> categorized envelopes only
when enabled. Parent validates via companion decoder; ordinary source Product records
unchanged. Source cache key adds category schema/config/scope digest; invalid envelope
misses without legacy fallback, origin authorization still precedes reuse. Cache/checkpoint
store existing bounded JSON, no new datastore. Captured baseline envelope uses companion
codec in category mode; supplied baseline remains supplied. Report adds review reasons,
never silently selects profiles or overwrites evidence/identity/variant authority.

## Red acceptance evidence and remaining checks

Smoke C01: 1 intentional failure/0.25s. Bounded file:13 collected,13 intended stub failures/
0.35s (C01; six adapter seams; native C03 wrapper; C15 mapper; C16 config; C17/C18 codec;
C20 maintenance). No imports/syntax fail in saved final logs; native MockTransport boundary
would exercise real extractor after implementation, no actual HTTP/storefront performed.
Initial runner lacked PYTHONPATH; one diagnosed environment repair sets PYTHONPATH=src.
Saved commands/results: verification.md, artifacts/category-mapping/red-smoke.log, red.log.
These are stub seam reds, not native parser/guard/mechanism proof, nor C19 cache proof.
G2 reviewer must validate exact contracts/ownership/error flow. After G2 shared author
writes reusable components/refines skeleton; G3 before business implementation. Remaining
C01–24 tests/fixtures and actual native error/guard/cache paths precede relevant code.


## G2 author repairs — explicit facets, localized errors and real cache red

CategoryFact now requires CategoryFactBinding and existing ConversionOutcome, alongside
captured raw pointer/value, SupportState and existing Evidence. Binding.facet is explicit:
native_id/label/code_context/raw_path/parent_id/child_id/source_state/completion. Binding
identifies exact term ref and/or exact ordered(parent,child) edge; no pointer-name/value
heuristic chooses a facet. Label selector requires observed accepted label outcome;
ID selector requires observed accepted native_id outcome equal to selected native ID;
code namespace requires separately supported code_context. A supported ID cannot support
a rejected label, and a supported label survives a rejected ID. Retain normalized value,
source values/paths, acceptance/reason and transformations through ConversionOutcome,
produced by the real Normalizer bridge rather than duplicating conversion history logic.

Each trusted parent edge needs facts explicitly bound to that exact edge: supported
parent_id/child_id evidence (or a captured ordered-path conversion with both endpoints
and declared grammar). A term label or raw URL never supplies edge support. Collection
state/completion facts have no term binding; term/edge facets require matching binding
and bounded source evidence. Codec validates/snapshots outcomes, facet/term/edge alignment
and transformation lists, retaining all history on roundtrip. Unsupported facts may
retain proposed normalized values/history but cannot grant mapping support.

Why CategoryFact exists instead of replacing FieldObservation: existing FieldObservation
binds one normalized Product JSON field_path and requires observed nonnull value; source
category facets include missing/null/completion/index/edge endpoints that are not Product
fields. CategoryFact is a category-only binding adapter, not a generic observation engine:
it reuses Evidence, SupportState and ConversionOutcome. G3 must confirm concrete consumers
and whether a thin composition of existing observations can further reduce duplication.
No confidence, alternative trust policy or independent pointer resolver is introduced.

`localize_category_errors(errors,*,product_path)->tuple[NativeCategoryError,...]` is a
shared explicit stub. Extractor supplies exact operation product origin path, including
actual nonzero page-edge/item index, BEFORE attaching metadata. Descendant errors strip
that product prefix; another product's errors are excluded. Ancestor errors and errors
with no usable path become conservative no-path diagnostics for every affected product.
Adapters receive ONLY localized paths (categories/... or unrelated local product field),
never operation-global indices. Noncategory local errors do not invalidate independently
supported category data. Global/no-path errors remain conservative. Reserved diagnostic
metadata downgrades only and never upgrades support. C03 fixed localization red uses
product index1, sibling error atindex2, local category label error and global error.

C19 now has executable real source/cache interface acceptance: actual MaintenanceEngine,
MaintenanceStore and existing controlled HTTP Harness; category-configured job twice
must reuse source cache, then rule version/target change must force a new source request.
Only external transport is synthetic; cache/engine/source/SQLite remain production paths.
Engine accepts optional typed category_config but explicitly raises NotImplementedError
when enabled; None follows prior constructor behavior. This is a minimal G2 integration
stub, not cache behavior or a fake result. C19 currently fails at this intended stub,
not unexpected keyword/import/syntax, before any storefront/network dispatch.

Revision smoke C19:1 intended NI failure0.39s, saved before bounded rerun. Revised file:
17 collected/17 intended NI failures0.48s; added C11 separate ID/label support and failed
label cannot borrow ID, C03 error-localization, required C19 cache. Actual logs:
artifacts/category-mapping/red-cache-smoke.log and red-g2-revision.log. All remain within
existing24 mechanism/100 parameter/120s envelope; no full suite or native live run.

## G3 component refinement (documentation only, no changed signatures)

components.md is authoritative on concrete reuse and lifecycle. Shared source_fact and
ordinary attach_contract consume one extracted private `_capture._support_outcome`
helper, never duplicate source support. Facet-specific facts retain existing
ConversionOutcome history. original_binding includes full portable Product+scope+
canonical observation/mapping/config snapshot, not just outer frozen dataclass state.
All consumers revalidate before trust; nested dict/list/Evidence/outcome mutation rejects
binding rather than blessing stale data. Digest is integrity, not authority. Independent
G3 reviewer assesses this refinement; source algorithms and further tests remain gated.
Each platform author must acknowledge all five other findings and final shared contracts
before editing only its owned adapter/extractor files. Open relevant peer questions must
be resolved or explicitly block the affected implementation.


## G3 durable policy lifecycle repair (declarations/stubs only)

Store constructor now has optional typed category_config registry; future create(goal)
atomically persists explicit mode plus full bounded canonical config/version/digest.
CategoryPolicySnapshot(mode,schema_version=1,config_json?,config_digest?) stores immutable
JSON string, not caller aliases. `MaintenanceStore.category_policy(job_id)` returns exact
creation policy; currently explicit NI stub. Category-enabled Store construction also NI
until G3 implementation; None preserves existing constructor behavior. Engine category_config
is expected identity only, not activation. Exact ownership/migration/legacy semantics are
in components.md: store schema2 policy table on enabled creation, old rows missing policy
permanently legacy, no retroactive opt-in, validate saved policy before state/dispatch.
Engine with no expected config consumes saved snapshot; explicit mode/digest mismatch
fails category_policy_mismatch before network/recovery. New job with changed config is
cache miss; same job changed config rejects. C19 setup creates category-configured Store,
not merely engine; additional fixed variants verify durable snapshot/reopen and legacy/
changed-policy resume rejection without request/state transition. No business algorithms.
