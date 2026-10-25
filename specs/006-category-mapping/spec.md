# Cross-platform category mapping — behavior draft

2026-10-17. User requested a dedicated agent per platform, direct peer consultation
before category implementation, and a reusable component model based on existing code.
This is design-first; user confirmed component model AND implementation; shared G1/G2/G3 precede code.

## Outcomes and requirements

- FR01 Preserve source category observations: original label/identifier/namespace,
  supplier/store/channel/language scope, available ancestry and captured support.
  Public access and configured credentials remain explicit; no new privilege implied.
- FR02 Distinguish unordered product category memberships, ordered ancestor paths,
  custom product-type strings, standard taxonomy nodes and merchandising collections.
  Never fabricate parent-child paths by joining membership names.
- FR03 Provide one deterministic versioned canonical-category mapping contract shared
  across Shopify, WooCommerce, Magento, Shopware, BigCommerce and generic structured
  HTML/feed sources. Namespaced source IDs and trusted mapping configuration are
  distinct from normalized labels. Unknown/ambiguous/missing/unsupported are visible;
  categories with no reliable correspondence remain unresolved, never guessed facts.
- FR04 Preserve conflicting mappings and mapping basis/version. Reordering memberships
  does not change results. A multi-category product can have multiple observed source
  memberships; conflicting canonical targets must not silently select the first.
- FR05 Reuse captured-evidence, normalization, identity, portable storage and explicit
  maintenance profile contracts. Keep source facts distinct from derived canonical
  assignment and comparison-policy selection. No new calibrated confidence claims.
- FR06 Make profile selection trusted and explicit. A category mapping cannot generate
  missing domain specifications or weaken identity/variant/authority safeguards.
  Missing or conflicting category/profile configuration remains review-only.
- FR07 Preserve existing constructors, API defaults, legacy category_path/feed exports,
  tool source permissions and request/response/graph/time limits. New optional source
  queries stay guarded and count actual requests. No recursive unbounded tree crawl.
- FR08 Every platform author must consult peers and cite a shared-contract decision
  before changing source/category code. Only the shared owner changes common modules;
  platform adapters own source translation only. Review gates precede implementation.

## Acceptance scenarios

SC01 equivalent source labels/IDs map through trusted rules to the same target;
SC02 two sibling memberships never become fake hierarchy;
SC03 same numeric category ID in different stores/platforms remains distinct;
SC04 custom Shopify type/collection never masquerades as observed standard taxonomy;
SC05 missing/empty/null/unknown categories and aliases retain exact support semantics;
SC06 duplicate/reordered/conflicting mappings have stable explicit results;
SC07 malformed/escaped labels, localized paths and invalid/cyclic ancestry fail safely;
SC08 partial/depth-limited category trees preserve incomplete status and request caps;
SC09 source evidence vs derived mapping stays inspectable after portable roundtrip;
SC10 category mapping/profile interaction preserves existing matcher safeguards;
SC11 all existing source APIs/export/defaults and unrelated work remain intact;
SC12 six adapter families share the same contract, evidenced by peer decisions and
actual real-path controlled fixtures, not six copied mappers.

## Boundaries and unresolved decisions

No promise of universal automatic mapping or complete public taxonomy access.
No per-product model calls, training, store writes, admin credential acquisition,
full-market domain-policy catalogue or new distributed orchestration. Registry and
adapter API design follow platform findings and independent G1/G2/G3 reviews.
Common target taxonomy/version and exact additive persistence shape remain design
questions; do not implement a speculative registry before peer consultation.

## Agreed first implementation slice (G1 candidate)

Public opt-in behavior is exposed through `normalize_with_categories(raw, platform,
shop_url, *, category_options)` and async `extract_with_categories(url, *,
category_options, ...existing extraction options)`. The first returns an explicit
categorized-product wrapper or None under existing validity rules; the second
returns an explicit categorized-extraction wrapper containing the existing extraction
result and aligned categorized products. Existing normalize/extract signatures,
Product/Variant constructors and default feeds/bundles remain compatible. Names are
behavior contracts for G1; skeleton review will fix signatures without broadening them.

FR09 Each wrapper contains the ordinary Product plus a separate category companion:
source observations, mapping decisions and category capability/completeness. Capture
original category values before compatibility transformations. Existing retained
capture pointers, SupportState and conversion outcomes determine support; a missing,
truncated, changed, expired or LLM-only source never becomes an observed category.
Source state is `missing|null|empty|present|malformed`; explicit empty text and empty
collection retain their raw representation. Completeness is independently
`complete|partial|unknown` with reason per membership/path/index/graph relation.

FR10 Trusted caller CategoryOptions supplies source scope, target taxonomy namespace
and immutable version, valid target IDs, finite exact mapping rules and limits.
Source term identity comprises taxonomy namespace/version, opaque ID, and merchant
store/catalog ownership when applicable. Global standard taxonomy IDs use their
vocabulary/version identity; assignment scope still retains platform, stable shop
URL/basepath, catalog, known channel and locale. Unknown source version/scope remains
unknown; rules must explicitly permit unknown values rather than substitute defaults.
Store endpoint and supplier identity are separate. Namespace/version and source scope
are not interchangeable. Labels retain original spelling and separators.

FR11 Rules match exact scoped native ID or explicitly configured raw label/path
representation; no implicit casefolding, alias guessing, fuzzy/model inference or
online taxonomy download. Each rule records ID/version, source selector and explicit
target set. Invalid targets, duplicate rule identities or malformed configuration
fail before extraction/network. No matching rule => unmapped; no usable source =>
unavailable; all applicable rules agree on exactly the same nonempty target set => mapped;
different target sets => ambiguous with sorted candidate union. In particular
{A,B} vs {B,C} yields ambiguous candidates {A,B,C}, never intersection {B}. Distinct product memberships may legitimately yield multiple mapped targets;
per-term ambiguity and product target union are both explicit. Mapping is partial if
membership completeness is partial/unknown; it never claims absent targets. A target
registry does not define thousands of maintenance policies.

FR12 `categorized_product_to_record` / `categorized_product_from_record` are explicit
version-one companion codecs. Envelope contains an unchanged portable Product record,
category observations with evidence/support, mapping decisions and config digest.
Unknown envelope versions/keys, mismatched product binding (digest of the entire unchanged portable Product plus
assignment scope; any Product field mutation invalidates it), dangling evidence refs,
invalid IDs/targets or oversized/deep records are rejected. Legacy portable Product
reader rejects a category envelope; callers choose its codec explicitly. The immutable companion stores its original product/scope binding; encoding rejects a
mutated wrapped Product instead of recomputing and blessing stale facts. Explicit
re-extraction/rebuild must validate captured support anew. Ordinary
product export remains ordinary product export; opt-in export uses the new envelope,
so no silently dropped dynamic attachment serves as the category API.

FR13 Maintenance opts in through trusted runtime category configuration, retained by
digest/version with job policy and validated on resume. Guarded source/domain parsing
returns optional categorized envelopes only in this mode; baseline captured envelopes
are decoded explicitly, supplied baselines retain source-supplied status. Cache/checkpoint
validation uses the companion codec and includes category schema, scope and full
registry/rule/profile-binding digest in cache identity. Changed rules/scope invalidate
reuse; replay with unchanged policy preserves observations and prior mapping versions.
Authorization remains checked on cache hits. Invalid category envelope is a cache miss,
not a trusted fallback to legacy data. Legacy jobs/cache behavior remains unchanged.
Canonical mapping can only add a conservative category conflict/review reason when a
trusted explicit target-to-profile binding disagrees with an explicitly selected
profile. For category-enabled jobs, missing/ambiguous categories or absent profile/binding
remain review-only even when an explicit legacy profile exists; ordinary jobs retain
their existing explicit-profile behavior. No category-mode restriction is retroactive.

category agreement grants no identity/variant/field authority or automatic profile.

FR14 Initial native extraction preserves existing default fixed query bodies. Explicit
category mode uses bounded verified category memberships within native product requests,
with zero category follow-up/tree requests. All six adapter families translate actual
source category payloads.
Shopify public custom type is available; standard taxonomy/collections remain unavailable
unless actually supplied. Shopware categoryIds are memberships; categoryTree is a separate
unexpanded index. BigCommerce default category observation is unavailable; opt-in fixed query adds
`categories(first:20) { pageInfo { hasNextPage endCursor } edges { node { entityId name path } } }`.
The saved official embedded schema verifies every selected type/field and first/after
arguments; only first20 memberships/product are fetched, hasNextPage=true stays partial.
Shared security pins the original and this exact reviewed template using producer-owned
constants, and denies all other GraphQL. Magento opt-in appends only verified `categories { uid name }` to public
ProductInterface selections (including configurable child selections where reused);
uid stays opaque, nullable name stays unknown. Saved coordinator schema proof is
`artifacts/category-mapping/findings/magento-schema-minimal.json`. No new Store header,
category tree/Breadcrumb request, SaaS fallback or implicit store-view claim. Generic feed
opt-in parsing retains declared google_product_category and absent/empty state before
capture; Google numeric IDs stay strings and source taxonomy version stays unknown.
Schema.org CategoryCode requires inCodeSet context; URL categories stay opaque. Informal
text separators/backslashes do not establish ancestry. Repeated OpenGraph loss must be
reported incomplete unless raw declaration retention is implemented and captured.
Unverified enrichment is deferred; explicit access and existing finite request/response
limits remain enforced. No arbitrary GraphQL or broadened Shopware association bypass
is in this slice. BigCommerce token denial stays source unavailable; new query support
is verified with controlled real transport independently from live credential availability.

Limits are explicit and fail closed: default max100 category terms, max200 relation
references, max8 explicit ancestry depth, max256KiB companion record. Category limit
zero retains unavailable/partial reason and performs no optional work; truncation
preserves existing supported terms with partial reason, never fabricated empty sets.
Mapping rules/target registry max1000 entries each and max256KiB combined input; oversized
or invalid config fails before any extraction. No recursion beyond explicit depth.


## Native category error contract (G1 revision)

FR14 opt-in queries may return GraphQL errors alongside valid data. Keep valid product
siblings and supported unaffected category leaves; retain bounded source diagnostics
and error paths. An error at categories, its connection/edge/node/selected leaf, or its
completion metadata makes that product's category relation partial when supported
terms remain, otherwise unavailable. A null/failed affected name does not erase a
supported native ID, but the failed name cannot support a label rule. Errors with no
usable path conservatively affect all category relations in that response. An error
whose path is provably outside category data does not by itself invalidate independently
supported categories and valid completion metadata; ordinary product validity rules
still apply. Catalog/source success never overrides these category statuses.

Missing/null category payload is unavailable, never observed empty. Empty membership
is observed only from a schema-valid explicit empty list/connection without relevant
errors; BigCommerce additionally requires pageInfo.hasNextPage=false for complete empty
membership. Missing/malformed BigCommerce pageInfo or nonboolean hasNextPage yields
unknown completeness with completion_metadata_unavailable, retaining supported terms;
a category-affecting GraphQL error takes precedence and yields partial/unavailable as
above. Magento categories is an unpaginated array in the verified product schema, so
an explicit valid array without relevant errors establishes that product's returned
memberships; product page_info does not establish complete taxonomy/graph coverage.

Schema/unsupported-field rejection, HTTP401/403 or GraphQL access denial is explicit
native source/category unavailable; retain previously captured valid products and
valid products in any accompanying data. Never synthesize empty categories or successful
complete source from rejection. Category mode performs no automatic default-query retry,
HTML/model fallback or other additional request to hide category rejection. Existing
ordinary default extraction behavior remains unchanged. Any caller-requested later
attempt remains subject to existing independent request/time/access budgets.
