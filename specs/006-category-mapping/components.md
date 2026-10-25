# Reusable category components — G3 candidate, 2026-10-17

G1/G2 independently passed in reviews.md. This document defines implementation boundaries
and concrete reuse; no source algorithm is implemented in this stage. Existing common
code/default outputs remain stable. Skeleton signatures/red evidence remain applicable.

## Reuse matrix and consumers

| Existing component/helper | Category consumer | Reuse/change boundary |
| --- | --- | --- |
| `_capture.capture` | Native producers, feed/structured parsers, normalize wrapper | Existing bounded JSON snapshot before enrichment/default collapse, original URL/time/method; no category-specific capture engine |
| `_normalization.Normalizer.select/record/emit`, `ConversionOutcome` | shared categories.evidence.source_fact | Select original JSON pointer once, record actual conversion acceptance/values/paths/transformations; adapters do not repeat conversion/support logic |
| `_capture.attach_contract`, `_same_source`, `_size`, source redirection rules | ordinary Product trust and categories.evidence | Extract the existing support-for-outcome block into one private helper reused by both; preserve original retained-match/LLM/null/truncation/byte checks and `_field_sources` semantics |
| `_evidence.Evidence`, SupportState, pointer/value codecs | CategoryFact, companion codec | Existing evidence identity/URL/time/pointer validation; no new confidence or authority system |
| `_evidence.FieldObservation/TrustContract` | ordinary Product remains unchanged | Category bridge binds native facets instead of inventing Product field paths; reuse observations where applicable, never alter factual_paths(Product) to fake category fields |
| `_portable.product_to_record/product_from_record`, validate_tree, encode/decode values | categories.portable | Unchanged Product record embedded in new explicit envelope; same bounded primitive codec/type checks, category schema extension validated separately |
| `_scope.catalog_scope` semantics | CategoryScope construction/selectors | Stable configured store/basepath/catalog identity, known assignment context; never per-product URL or GraphQL endpoint alias identity |
| `_extract.extract` orchestration, `_normalize.normalize` dispatch/validity | explicit category wrappers | Refactor shared internal flow to retain original captures when opted in; old entry points and fallback behavior unchanged when mode off |
| Native extractor paging/request/capture | six source adapters/native mode | Preserve existing transport limits/auth; BigCommerce/Magento fixed category selection only; no hierarchy crawl/new credential acquisition |
| `_storefront.request`, GuardedTransport/NativeReadPolicy/OperationBudget | native category mode | Existing byte/origin/redirect/time/request accounting; shared guard permits producer-owned reviewed optional constant only when enabled |
| `tools.domain.synchronous`, encoded payload/auxiliary runtime | explicit child-process category parse | Same real parser/normalizer; bounded category config/diagnostics input, companion envelope output, parent strict decoder |
| maintenance.store packed/digest/cache/checkpoint/transaction/expiry | category runtime policy/source cache | Existing SQLite storage and lifecycle; cache identity adds schema/config/scope/bindings; no new datastore or duplicate persistence engine |
| maintenance.engine/profile/matcher | categories.maintenance review | Add only explicit category-mode conservative review; profile, identity/variant and field role gates remain existing mechanisms |

## Source support bridge: one implementation of existing checks

`categories.evidence.source_fact(raw,pointer,*,binding,convert?,operation)` is a thin adapter:
Normalizer creates ConversionOutcome; the shared `_capture` private support helper consumes
that outcome and actual normalized value. Planned helper extraction (common owner only):
`_support_outcome(raw,outcome,*,normalized_value,remaining_bytes)` returns state, Evidence
tuple, reason, transformations and used bytes. It encapsulates the existing attach_contract
source selection/redirection, retained equality, LLM rejection, explicit-empty support,
source URL/time and fragment budget checks. attach_contract continues assembling its
existing FieldObservation/TrustContract from the same result. Category source_fact stores
the same outcome/history plus native binding. No copied trust algorithm, new pointer
walker, second source selector or permissive fallback. Focused provenance regressions
must verify the extraction preserves old behavior before category implementation expands.

CategoryFact is justified by concrete adapter/mapper/codec consumers: a native ID, label,
code-set context, completion flag or edge endpoint is not a normalized Product field.
FieldObservation.field_path binds Product factual paths and observed nonnull values;
inventing Product paths would conflate source relations and normalized fields. CategoryFact
adds only typed facet+term/edge binding and source-only state around existing Evidence,
SupportState and ConversionOutcome. It introduces no new support states, probabilities,
source authority, score, competing resolution policy or generic provenance framework.
The mapper checks the selected facet only: an observed ID never authorizes an unsupported
label, observed label never upgrades unsupported ID; parent edge requires matching bound
endpoint support, code-set identity requires its own code_context support. Transformations
remain exact Normalizer history, not recomputed from labels or pointer names.

## Lifecycle, nested mutability and derived data

1. Validate trusted options/registry/rules/limits and source scope before dispatch; copy
   accepted logical configuration to a canonical bounded value snapshot/digest. Do not
   retain references to caller-owned mutable payloads as policy authority.
2. Capture raw source before enrichment/default coercion; product and categories consume
   the same captured evidence support rules. Parse bounded native diagnostics and localize
   each operation error by actual product path before adapter invocation. Global/ancestor
   errors remain conservative; other siblings excluded; no extra fallback request.
3. Adapter translates source semantics only, bounded by CategoryLimits and actual capture.
   Shared wrapper validates facet/term/edge consistency, source states and completeness,
   retaining unknown/partial/unavailable. No dynamic Product category attachment is API.
4. Shared mapper alone applies exact trusted selectors/target sets. Source observations
   remain unchanged; MappingDecision records derived target/version/rule/source refs.
   Different applicable sets => ambiguous union; different memberships can map to multiple
   targets. Agreement never selects a maintenance profile or strengthens source authority.
5. Construct categorized wrapper with canonical snapshots of nested raw values, Evidence,
   ConversionOutcome and mapping data. Frozen dataclasses alone do not make their dicts/
   lists/Evidence/outcomes immutable. No API promises that Python object mutation is
   impossible: never trust a cached validation result on subsequent consumption.
6. original_binding covers the unchanged strict portable Product, scope AND canonical
   category observations/mapping/config digest, excluding original_binding itself. Encoder,
   wrapper review consumers and decoder revalidate bound canonical state and facet/evidence/
   outcome consistency; mutation of Product, nested source values/retained evidence/history/
   selected targets invalidates binding instead of silently recomputing it. Standalone map_categories receives observations before a wrapper binding exists; it
   validates facet/evidence/outcome snapshots before deriving decisions and grants no
   source authentication. Build through supported source revalidation or reject CategoryError; no unsafe object alias survives
   decode. Digest detects integrity changes, not source authentication or merchant authority.
7. Explicit codec snapshots primitive trees/Existing Evidence and outcomes with strict keys,
   types, enum/version/ref/byte/depth limits. Decoder validates before returning fresh objects;
   old Product reader deliberately rejects category envelope. Default exporters stay legacy;
   explicit codec stores/reopens observations and derived decision history separately.

NativeCategoryError contains only bounded code/localized path. `_category_diagnostics`
metadata can downgrade completeness, never become evidence/support. Unsupported native
category fields/access errors preserve valid products and diagnostics without query retry,
HTML/model fallback or known-empty category. Missing/malformed BigCommerce pageInfo remains
unknown; explicit empty needs valid completion and no category-affecting errors. Actual
source/catalog page completeness is independent of category membership/graph completeness.

## Shared boundary / six platform ownership and acknowledgment

Shared author category_bigcommerce alone owns category contracts/API/evidence/mapper/codec/
maintenance/native declarations; `_extract`, `_normalize`, `_capture`, `_portable`, package
exports; tools/security/sources/domain/runtime; maintenance engine/store policy/cache.
Root coordinates shared owner scheduling; dedicated authors never edit these files.

| Platform author | Exclusive adapter file | Other permitted platform files after G3 |
| --- | --- | --- |
| Shopify | categories/adapters/shopify.py | extractors/shopify.py if needed |
| WooCommerce | categories/adapters/woocommerce.py | extractors/woocommerce.py if needed |
| Magento | categories/adapters/magento.py | extractors/magento_graphql.py,magento.py |
| Shopware | categories/adapters/shopware.py | extractors/shopware.py |
| BigCommerce | categories/adapters/bigcommerce.py | extractors/bigcommerce.py |
| Generic | categories/adapters/generic.py | extractors/feed.py,_schema_org.py,_opengraph.py or explicitly configured CSS parser |

Before category code, EACH platform author reads all FIVE other platform findings plus
research.md/skeleton.md/components.md and records acknowledgment in their platform file:
shared semantics adopted, files owned, relevant open peer questions resolved or precise
blocking limitation. Existing exchanges establish initial consultation but do not replace
this final contract acknowledgment. Ask active relevant peers directly; reuse saved
answers for inactive peers and identify still-pending questions honestly. Shared owner
checks acknowledgment before integrating each adapter. Adapter implementation remains
observe_categories(raw,*,context) -> tuple observations; no rules/mapper/network/database.
No agents or parallel code launches beyond root's authorized schedule.

## Query producer, guard and child-process lifecycle

Platform extractor owns `_QUERY` and optional `_CATEGORY_QUERY`, composed from reviewed
native fragments once. Guard imports producer constants, never duplicates request text.
NativeReadPolicy optional mode defaults false; tool/runtime passes explicit validated
category mode. Default query/body stays identical; altered query/mutation/Shopware
association stays denied. BigCommerce first20 membership with no followups; Magento
categories{uid name} only, no Store header/tree. Source errors localized before raw
metadata attachment; actual requests/response bytes/time remain accounted by guard.

Trusted CategoryRuntimeConfig is owned by MaintenanceStore constructor registry:
`MaintenanceStore(path,*,custom_profiles=None,category_config=None)`. Constructor validates
and canonically snapshots the complete bounded options/rules/target registry/profile
bindings for FUTURE create(goal) calls; unchanged create(goal) signature atomically
stores job + exact creation-time mode/snapshot/digest with existing profile policy.
Engine config is an optional EXPECTED identity, never the operation that enables a job.
`store.category_policy(job_id)->CategoryPolicySnapshot(mode,schema_version,config_json,
config_digest)` reads that durable record; enabled snapshot includes full validated
canonical JSON, not mutable Python aliases or only a digest. Reopen requires no original
caller object to reconstruct policy. Invalid snapshot/version/digest rejects recovery.

Store owns a small additive `category_job_policies` table keyed/FK to jobs, storing mode,
category schema version, canonical config JSON and digest in the SAME create transaction.
Initialize/migrate transactionally on first category-enabled creation with store schema
version2; existing schema1/legacy rows preserved, current reader supports both. Old code
that cannot interpret category policy rejects unsupported schema2 instead of silently
running enabled jobs as legacy. Existing missing-policy row means LEGACY permanently;
new legacy jobs record legacy mode where policy table exists, with no enabled snapshot.
A configured Store changes defaults for future jobs only and cannot opt in an old row.
No Goal fields, default create signature or category permission change on legacy jobs.

Before acquire/begin attempts, dispatch, cache reuse, retry or recovery, Engine reads the
saved policy and verifies expected runtime config if supplied. Mode/digest mismatch
raises MaintenanceError(category_policy_mismatch), no network/reservation/state advance.
With no expected config it consumes the exact saved policy (including legacy mode),
not current Store constructor defaults. Explicit expected enabled policy on legacy job
rejects; same-job changed config rejects; changed config with NEW job stores new snapshot
and naturally misses old cache. Persisted full snapshot is validated before reconstruction
and again across child-process serialization; credentials never enter it.

Saved enabled policy flows through guarded source->domain child payload->shared
normalization->companion codec->parent strict decoder. Existing encoded payload/auxiliary
runtime remains the process boundary; malformed child envelope rejected, malformed cache
misses without legacy fallback. No dynamic sidecar outside codec. Cache key includes
saved schema/source scope/full registry/rules/profile bindings digest plus existing
origin/profiles/fields/freshness policy. Authorize before cache hit; unchanged hit/replay
preserves original source time/mapping version. Existing checkpoint atomically stores
envelope/accounting; failure before commit leaves no fabricated successful companion.
Supplied baseline stays supplied, captured baseline uses companion decoder. Category-enabled
missing/ambiguous/unmapped/profile conflict adds review reasons; profile/identity/variant/
field safeguards run unchanged. C19 real store/engine tests cover creation snapshot,
reopen, same-policy hit, new-policy new-job miss, legacy/same-job mismatch before dispatch.

## Verification / gate state

No source algorithms implemented. Initial G2 reds remain historical; G3 lifecycle
repair added required fixed C19 creation/recovery variants and actual red rerun. Latest:
creation smoke1 NI0.36s, then20 collected/20 intended NI failures0.76s, no import/syntax
failures, artifacts/category-mapping/red-policy-smoke.log and red-g3-policy.log. G3 reviewer must inspect reuse helper extraction,
facet binding/history, nested integrity, producer/guard mode, child codec/cache ownership
and author acknowledgments. After G3 add missing real-path cases BEFORE implementing
each related task, then bounded C01–24 mechanisms/stress/regressions/live as planned.
No current red result proves cache/native mechanism correctness or live capability.

Implementation reuse refinement authorized by root: categories.helpers.nonblank_text and native_id now replace byte-equivalent (error wording noncontractual) private converter bodies in completed Woo/Magento/Shopware/BigCommerce adapters. Generic consumes nonblank_text already; Shopify whitespace semantics differ and remain explicit. Shared merchant_scope/observation_id also eliminate duplicate formatters. No source semantics changed by mechanical imports.
