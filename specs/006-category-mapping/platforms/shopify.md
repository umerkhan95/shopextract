# Shopify category discovery — 2026-10-17

Status: discovery ready; no implementation, test execution, storefront probe, or model call.
Read AGENTS.md, workflow, constitution and docs/catalog-maintenance.md; existing work preserved.
Actual session token counters unavailable; no quota estimate. Investigation bounded to local reads and two official pages.

## Existing behavior and reuse
- `src/shopextract/extractors/shopify.py:23,56,102`: bounded public `/products.json`, per-product capture, no category/collection enrichment; optional `.js` enrichment is identifiers only.
- `_normalize.py:269,283,288`: merchant `product_type` copied verbatim and projected to legacy single-item `category_path`; delimiters are not split.
- `_models.py:52,72,79`: preserve Product/Variant constructors and default exports; no new required fields.
- `_capture.py:19,64`, `_normalization.py:13,31`, `_evidence.py:14,64,117`: reuse capture, conversion outcomes, support states and evidence links, avoiding a second provenance system.
- `_portable.py:145,166`: reuse portable product/trust records; keep any new category contract explicit and opt-in.
- `maintenance/profiles.py:15` and `maintenance/engine.py:554`: trusted versioned comparison profiles and alias-based conflict veto already exist; neither is a taxonomy mapper. No category label grants policy or identity authority.
- `tests/fixtures/shopify_products.json` contains `Coffee`; `tests/test_normalize.py:94` asserts unchanged product_type.

## Saved evidence inspected
`artifacts/field-resolution-live/09-shopify-public.json`: saved 2026-10-16 public BoardGameBliss capture, limit6, one request, bounded partial catalog (`product_budget_reached`).
Its `.evidence.json.gz` has six product contracts; first product observes `Board Games` at `/product_type` and legacy `/category_path/0`, with transform `Project product category`.
This proves merchant label capture, not standard taxonomy assignment or collection membership. No fresh storefront observation was performed.

## Capability and access distinctions
Verified 2026-10-17, official API reference version 2026-10:
- [Admin Product](https://shopify.dev/docs/api/admin-graphql/latest/objects/Product): `productType` is merchant-defined; `category` is Standard Product Taxonomy; `collections` lists product memberships; requires `read_products`. Admin access requires authorized credentials, absent in this work.
- [Storefront Product](https://shopify.dev/docs/api/storefront/latest/objects/Product): also exposes `category`, `productType`, and `collections`; docs state `unauthenticated_read_product_listings` scope. GraphQL access/publication visibility must be established separately; no credential or tokenless access assumption.
These schemas do not establish the fields available through public `/products.json`. Existing extractor cannot claim standard category availability.
Custom product_type, standard taxonomy ID (opaque TaxonomyCategory GID), and merchandising collections are three distinct meanings.
No undocumented public category endpoint, graph completeness, ancestor chain, or taxonomy version is inferred.

## Proposed shared contract needs — consultation before code
- Reuse a single shared opt-in `CategoryObservation`/term-reference contract; platform adapters only project their native payloads.
- Distinguish label, unordered memberships, ordered path; carry taxonomy kind `merchant|standard|merchandising`, namespace and opaque native ID (nullable for ID-less labels).
- Term identity separates taxonomy namespace/version from observation scope (platform, supplier/store, optional catalog/store-view, locale). Global standard taxonomy terms may be shared; product assignments retain source scope.
- Preserve raw label, native pointer, actual capture URL/time, support state/evidence IDs and source completeness. A compatibility `category_path` does not prove ancestry.
- Separate missing/not observed, explicit null, explicit empty and malformed; mapping decision status is separate from observation state. Product memberships and graph completeness are independent.
- Canonical mapping is a versioned derived assertion with rule/source refs and conflict/ambiguous/unmapped outcomes; never relabel inferred mapping as source fact or select a maintenance profile silently.
- Reordering or deduplicating collection memberships does not create parent-child relationships; term ID collisions across stores/namespaces cannot merge accidentally.

## Predesigned deterministic outcomes (planned, not executed)
1. `product_type="Boots > Sale/Outdoor"`: exact label retained; legacy path remains one element; no inferred ancestry/standard ID. Risk: delimiter hallucination.
2. product_type missing vs null vs empty vs `{}`: distinct raw observation conditions; no canonical match/profile; malformed object unsupported. Risk: false known-empty/coercion.
3. custom `Shoes` plus authorized standard category GID and collections `Sale`,`Summer`: three separate assertions; standard exact-ID rule may resolve only its namespace, collections stay memberships. Risk: mixing merchandising and taxonomy.
4. collection IDs `[2,1,2]` vs `[1,2]`: same membership set with retained source ordering/evidence, no path; same IDs in another store unequal. Risk: order instability/collision.
5. partial collection page returns one item with hasNextPage=true: one supported membership, completeness=false; never infer absent memberships. Risk: false removal.
6. public product has no standard category field: standard state unavailable, even when merchant type equals a taxonomy label. Risk: public/Admin capability conflation.
7. supplied mapping maps Shoes to footwear but explicit trusted hardware-v1 remains selected: conflict/review; no identity promotion/profile mutation. Risk: bypass policy/matcher.
8. retained product_type capture changed after capture or exceeds retention: unsupported category source; no evidence-backed exact mapping. Risk: fabricated provenance.
9. competing scoped rules produce different canonical targets: ambiguous/conflict with retained rule IDs, deterministic order; no first-match success. Risk: hidden rule precedence.

## Peer exchange and remaining decisions
WooCommerce agent consulted directly before code: agreed unknown/missing/null/empty/malformed separation, memberships != ancestry, graph completeness != membership completeness, shared observation with namespace/scoped term references.
Magento agent consulted directly before code: agrees opaque supplier/store/catalog-scoped IDs and unordered memberships vs ordered breadcrumb chains; asked how collections differ; Shopify response above supplied.
Shared contract owner/coordinator must settle exact field names, versioning and malformed-state encoding; no duplicate platform dataclasses proposed.
Unresolved: whether first slice permits authorized GraphQL input fixtures only or adds a new authorized GraphQL extractor; minimum mapping registry schema and explicit policy linkage. No new network integration assumed.

## Final contract ACK — implementation stage, 2026-10-17
Read final spec/test-design/research/skeleton/components/contracts and all five peer findings (WooCommerce, Magento, Shopware, BigCommerce, generic); G1/G2/G3 independently passed in reviews.md.
Adopt shared CategoryObservation/TermRef/FactBinding/source_fact, exact skeleton namespaces, scoped merchant terms vs global standard refs, no inferred ancestry, independent source state/support/completeness and one shared mapper/codec.
Direct consultation with active shared owner category_bigcommerce resolved helpers: `categories.helpers.merchant_scope(scope)` and `observation_id(scope,namespace,relation,pointer='')`; Normalizer.select provides source presence/value, source_fact alone supplies support. Empty captured [] may be observed; empty/null text is UNKNOWN with distinct source state and no term. WooCommerce active peer confirmed same convention.
Own only categories/adapters/shopify.py, tests/test_category_shopify.py and these Shopify artifacts; extractor needs no change. Public product_type is opaque; supplied standard `category{id,name}` and merchandising `collections{edges{node{id,title}},pageInfo{hasNextPage}}` are translated only from actual raw captures. Missing fields stay explicit unavailable. No Admin/Storefront requests or credential work.
Implementation tests remain unexecuted until root serial test barrier; no compile/test/inference/network/Git commands by this author.

Implementation saved: adapter uses shared helpers/Normalizer/source_fact only; all three namespaces emitted, typed ID/label/state/completion bindings, source-state distinctions, scoped collections, global standard refs, partial bounds and capture facet isolation. Exact duplicate collection refs/labels merge while retaining pointers; conflicting labels remain competing terms (shared-owner confirmation).
`tests/test_category_shopify.py` contains 14 fixed invocations across C01/C10/C11/C12/C22 variants: real normalize wrapper/custom delimiters; five raw states; standard/custom/collection separation; changed ID vs retained label; three completion states; duplicate/order/store scope; zero cap; malformed boolean ID/nullable label. No tests/compile executed by this author; root owns serial barrier and results. No extractor edit was needed.
