# BigCommerce category discovery (2026-10-17)

Discovery/component proposal only; no production/test edits, execution, storefront or model calls.
Read AGENTS.md, workflow, constitution, feature spec/test-design; preserve existing dirty work.
Actual session token counters unavailable. Reused bounded saved-source excerpts; no broad sweep.

## Existing facts and gaps
- `extractors/bigcommerce.py:_QUERY` queries product/variant fields, no categories/tree/breadcrumbs.
- `BigCommerceExtractor.extract` captures product nodes with response URL/time and method `bigcommerce_graphql`.
- `_normalize.py:_normalize_bigcommerce` produces no category field; Product.category_path defaults to []. This is unavailable category evidence, never observed empty membership.
- `tests/fixtures/bigcommerce/documented-field-types.json` covers only selected current query types; it is not a complete schema and lacks category types.
- Saved `artifacts/api-integration/bigcommerce-schema-types.json`, Product field categories: `CategoryConnection`, described as categories associated with product, with sortBy/before/after/first/last arguments.
- Saved `artifacts/api-integration/bigcommerce-schema-reference.source` Site example separately includes categoryTree nodes entityId/name/path/hasChildren/children and category breadcrumbs with pageInfo/edges. Example is a field inventory, not a validated executable query or a captured storefront result.
- Saved Site return documentation calls categoryTree a list of CategoryTreeItems; no connection pagination implied. Later bounded embedded-type extraction resolved minimal Category/CategoryConnection/CategoryEdge/PageInfo signatures; tree arguments/depth and Breadcrumb remain outside scope. Do not implement speculative parentId/treeId arguments.
- Product.path and category.path are URLs, not ancestry. Product category array/connection order is not a parent relationship.
- Saved `artifacts/api-integration/bigcommerce.json` reports public storefront token unavailable and HTML fallback; `artifacts/field-resolution-live/07-bigcommerce.json` is saved HTML pipeline observation. Neither proves Storefront category or hierarchy retrieval.
- Two official schema pages attempted through web tool, inaccessible; no extra pages attempted. Saved source embedded RSC types subsequently resolved Category.entityId/name/path, CategoryConnection.pageInfo/edges, CategoryEdge.node and PageInfo.hasNextPage/endCursor; compact derived-offline proof: `artifacts/category-mapping/findings/bigcommerce-schema-minimal.json`.

## Scope, authentication and guarded requests
- `_bigcommerce_auth.py` validates storefront/private/impersonation token families explicitly; no JWT inference, issuance or admin fallback.
- Existing storefront token discovery reads published HTML; private and impersonation credentials must be supplied. Customer context remains explicit and must not be copied into evidence.
- Store/site identity must be configured source scope, retaining meaningful shop URL base path. Preserve endpoint origin separately; CDN/GraphQL endpoint alias must not silently become another merchant identity.
- Channel/catalog/tree/language IDs are unknown unless captured or explicitly configured; preserve supplied values, never invent channel 1/tree 1/default locale. Public visibility is scoped to authorized storefront context, not a promise of all store categories.
- `tools/security.py:GuardedTransport.guarded` allows GraphQL POST only when query equals imported `_QUERY` and body has only query/variables. A new opt-in query requires common security owner change and reviewed exact whitelist; never loosen arbitrary GraphQL/mutations.
- Reuse `_storefront.request`: 10MiB response cap, keyed cross-origin redirect rejection, bounded redirects and actual tool request budgets; keep default page_size=20/max_pages=100/timeout=30 behavior.
- Nested categories increase response size/query complexity; no verified vendor cost ceiling available here. Proposed opt-in first=20 per product, max 20 memberships/product initially; hasNextPage=true stays partial. No category cursor follow-up/tree crawl in initial query without separately approved budget and pinned query contract.
- Initial tree proposal is no fetch by default. Future fixed-depth selection must cap roots/nodes/depth and report hasChildren=true at boundary as incomplete; do not claim global tree completeness from product pagination or selected roots.

## Reuse and shared contract proposal
- Reuse `_capture.capture`, `_normalization.Normalizer` exact input/outcome tracking, `_capture.attach_contract` and existing evidence support states; retain ID/name/pageInfo/edge pointers, not only a joined string.
- Reuse `_portable` only through shared owner reviewed additive/versioned codec seam; dynamic Product attributes will not establish durable new contract. No duplicate BigCommerce mapper/dataclass.
- Shared scoped term ref: platform + configured store/catalog scope + taxonomy namespace + opaque native ID; preserve numeric entityId lexically as opaque ID without cross-store numeric identity.
- Relation kinds separate product memberships, explicit ordered breadcrumb path and explicit parent-child tree edges; merchant categories distinct from standard taxonomy IDs/collections/custom labels.
- Per-relation source state distinguishes missing/null/observed empty/malformed; completeness complete/partial/unknown with reason. Product-list, product-membership, breadcrumb and tree completeness remain separate.
- Captured category facts and derived canonical assignment (target taxonomy/version, rule/version, source refs, conflict/unresolved status) have separate provenance. Mapping cannot grant authority or select missing maintenance profiles.
- Default API/query/legacy category_path remain unchanged; opt-in fixed query adds categories(first:20){pageInfo{hasNextPage endCursor} edges{node{entityId name path}}}; no followups/tree crawl. Optional category extraction/persistence require G1/G2/G3 first.

## Predesigned deterministic fixtures (not executed)
- B1 memberships: product 101 categories edges IDs 7 Boots, 9 Sale; pageInfo.hasNextPage=false. Exactly two scoped memberships, complete membership relation, zero hierarchy edges or derived ordered path; default legacy output unchanged. Reverse/duplicate identical edges retains same semantic set with original evidence retained. Risk: fake hierarchy/order dependence.
- B2 pagination: same product only 7 Boots, pageInfo.hasNextPage=true/endCursor=c1. Exactly one supported membership with partial reason category_budget_reached; no claim category 9 absent and no extra request in capped initial slice. Product pagination completion does not change this. Risk: false removal/hidden N+1.
- B3 absent/null/empty/malformed: missing categories, null, {edges:[],pageInfo:{hasNextPage:false}}, and edges string. Respectively missing, null, observed empty complete, unsupported/malformed; none emits invented term/root. Missing pageInfo with valid edges retains memberships but completeness unknown. Risk: unsupported empty claims.
- B4 store/channel collision: same entityId 7 in distinct configured stores must have unequal refs; same store different known channel scopes remains context-distinct. Unknown channel is never equivalent to explicit channel 1 for scoped rules. Risk: identity leakage across shops/channels.
- B5 tree/path: explicit tree Clothing(1)->Boots(7), separate memberships {7,9}; tree edge 1->7 alone supports that ancestry, never edge 7->9. category.path=/boots/ alone yields no parent edge. Risk: URL and membership hallucination.
- B6 depth/cycle: at selected-depth leaf Boots hasChildren=true, children unrequested => partial tree, no known-empty child set. Malformed explicit cycle/self-child => invalid ancestry, raw evidence retained, finite traversal/no trusted path. Risk: unbounded/false complete traversal.
- B7 escaped/localized label: name `Boots > Sale / Été` on ID 7 remains one exact label; locale retained if supplied, no separator splitting or inferred ID translation. Conflicting labels for identical scoped ID remain competing observations. Risk: delimiter/language conflation.
- B8 guarded POST: default fixed query accepted, category-enabled reviewed fixed query accepted only opt-in, arbitrary extra fields/mutation/altered query denied before network; category request cap 0 causes zero optional requests. Requires shared security owner and real guarded transport, not adapter-only mock. Risk: capability/budget bypass.
- B9 provenance/policy: retained membership ID/name/pageInfo supports fact; changed or unretained ID cannot support exact-ID mapping. Trusted rules mapping 7 to conflicting targets stay ambiguous with both rule versions, never choose first or override configured profile. Portable reopen retains separate source and derived provenance. Risk: fabricated support or lost conflicts.
- Proposed bounded execution after review: smoke B1; <=9 case families/fixed variants, seed6006, <=100 tree nodes/200 memberships/8 depth per fixture, <=256KiB/fixture, <=120s aggregate, one sequential process, no inference/live access; save first failure. Minimal membership schema is verified from saved embedded types; breadcrumbs remain unimplemented/outside acquisition scope.

## Direct consultation and ownership
- Asked active `/root/category_shopware` directly before any code about namespace/store scope, membership/path and derived provenance.
- Shopware agreed: platform+store/catalog opaque refs; sales-channel/language separate; memberships vs ancestor-inclusive index vs ordered breadcrumb distinct; completeness per relation complete/partial/unknown with reason; missing association != explicit []; mapping target/version separate from captured fact.
- Reused saved Shopify and WooCommerce findings: custom labels/collections != standard taxonomy, store base path must survive, graph completeness != membership completeness, shared persistence seam required.
- Shared owner/coordinator must finalize scope field names, opt-in transport/query and codec. Later BigCommerce owner changes extractor/adapter only; common normalizer/security/evidence/portable belong to shared owner.
- G1/G2/G3 pending; no platform category implementation authorized before shared gates. Live GraphQL categories unobserved; deterministic mechanism designs above are planned, not passes.

Implementation ACK (after G3 pass): reread all five Shopify/Woo/Magento/Shopware/generic findings and final components/skeleton/contracts. Adopt one shared mapper/codec/support helper, exact facet support, distinct membership/path/index, separate store/basepath/channel/locale vs namespace/version and observed vs derived provenance. BigCommerce membership minimal signatures resolved from saved schema; no open blocking peer question; tree/breadcrumb acquisition outside slice. BigCommerce owns its adapter/extractor only; temporary shared author also owns explicitly assigned common modules, never the other five source files. No tests while other authors write.
