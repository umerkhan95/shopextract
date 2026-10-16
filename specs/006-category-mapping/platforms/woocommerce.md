# WooCommerce category discovery (2026-10-17)

Status: bounded research/component proposal only; no production/test changes or execution.
Read AGENTS.md, docs/development-workflow.md, .specify/memory/constitution.md and docs/catalog-maintenance.md.
Session token counters unavailable to this delegate; no inference or storefront requests performed.

## Existing behavior and evidence
- `src/shopextract/extractors/woocommerce.py:46`: public Store API products, pages of 100, injected client, timeout/max_pages; `:91` captures each product before normalization.
- `src/shopextract/_normalize.py:292,330-348`: category objects become a flat name list in legacy `category_path`; IDs/slugs/links are not projected into typed category data. Array order does not establish ancestry.
- `tests/fixtures/woocommerce_products.json` has two memberships per product but no IDs/parent fields; Tea + Green Tea alone cannot prove a parent-child relationship.
- `artifacts/field-resolution-live/10-woo-public.evidence.json.gz`, first record: retained `/categories` contains `{id:18,name:Cosmetics,slug:cosmetics,link:.../product-category/cosmetics/}`; observed name projection exists. This is saved capture reuse, not a fresh observation.
- Companion `10-woo-public.json`: 2026-10-16, 6 products/1 request; extraction partial (`product_budget_reached`, `catalog_coverage_unverified`). Do not equate run status pass with complete taxonomy coverage.
- `04-woocommerce.json`: saved 8 products/2 requests reports complete product extraction; no claim of category graph completeness.
- `src/shopextract/maintenance/engine.py:554`: category labels currently provide only a conflict veto against explicit configured profiles. Profiles remain trusted configuration, never inferred permissions.

## Official API facts (read 2026-10-17)
- [Category resource](https://developer.woocommerce.com/docs/apis/store-api/resources-endpoints/product-categories/): public Store API route `/wp-json/wc/store/v1/products/categories` and `/:id`; term objects include ID/name/slug/parent, root example parent=0. List supports page/per_page (0..100), parent and hide_empty (default true).
- [Products resource](https://developer.woocommerce.com/docs/apis/store-api/resources-endpoints/products/): public published-product data; category filters accept IDs/slugs; unstable custom-taxonomy filters use the registered taxonomy key. This does not establish a stable custom-taxonomy category export.
- Existing extractor supplies no API key or authenticated admin route. Proposed scope remains read-only public Store API; no wc/v3 credentials, mutation, or admin fallback.
- Proposed hierarchy retrieval must use explicit finite page/item/byte/time budgets and report unavailable/partial taxonomy independently. No hierarchy endpoint has been called here.

## Shared reusable component proposal
- Keep Product constructors/default exports and legacy `category_path` behavior compatible; add only an explicitly opt-in category contract after workflow gates.
- Shared `CategoryTermRef`: platform, store/catalog scope, taxonomy namespace, opaque native ID (nullable only for ID-less labels). Woo namespace `product_cat`; term IDs are not cross-store keys. Preserve store base path for subdirectory installs; do not collapse every installation to bare hostname.
- Shared observation: payload kind (`memberships`, `ordered_path`, `label`), taxonomy kind (`merchant`, `standard`), terms/labels, source state, evidence references. Distinguish missing, explicit null, empty list, invalid list; map support through existing trust states rather than fabricate a new probability.
- Shared edges have explicit parent evidence and root/unknown distinction. Woo product memberships do not imply a graph; graph page completeness and product membership completeness are separate.
- Mapping decision (target taxonomy/version, target ID, rationale, policy version, decision status) stays separate from observed categories. Duplicate names across terms/stores never auto-merge; no label alone selects maintenance profile.
- Reuse `_capture.capture` (bounded immutable source projections), `_normalization.Normalizer` (source selection/conversion outcomes), `_evidence` trust contracts, and `_portable.product_to_record/product_from_record` for durable evidence. Do not add a second evidence stack.
- Portable records validate exact Product fields and top-level keys (`_portable.py:145-184`); arbitrary new dynamic attachment would be dropped/rejected. Decide versioned opt-in serialization seam jointly before code; this is a material compatibility gap.
- Retain original pointers for term ID/name/slug/link and each parent edge. Category graph capture must not borrow product URL/time for a separate endpoint response.
- Existing `_field_sources` redirection in `_capture.attach_contract` is a reusable multi-source seam; graph projection still needs explicit contract/codec design and independently validated support.

## Predesigned fixtures and exact outcomes (not executed)
- W1 siblings: memberships IDs 7 Boots, 9 Sale; output two scoped memberships, zero edges, legacy names unchanged; reversing input preserves semantic membership set.
- W2 observed hierarchy: nodes 1 Clothing parent=0, 7 Boots parent=1; output root 1, edge 1->7, derived ordered path [1,7] supported by both terms/edge; product membership remains {7}.
- W3 namespace collision: store A term 7 Boots and store B term 7 Tools produce distinct refs; same store product_tag ID 7 is distinct from product_cat ID 7.
- W4 absent/null/empty/malformed categories: respectively missing/null/explicit empty/unsupported; none creates a node or inferred hierarchy. Missing differs from observed empty.
- W5 missing parent/page failure: node 7 parent=99 without 99 retains edge reference but path unresolved; taxonomy partial, memberships retained; no invented root or orphan label.
- W6 duplicate label IDs 7/8 Boots remain two terms; duplicate identical ID collapses semantic membership but keeps both supporting observations; conflicting names for same scoped ID remain conflict.
- W7 parent cycle 1->7->1 (or self-parent) retains raw observations, marks graph invalid, yields no trusted derived path; no infinite traversal.
- W8 truncation/expiry: missing retained ID or expired parent evidence blocks supported ref/path respectively while preserving supported name/membership facts and compatibility projection.
- W9 policy interaction: category term named Footwear plus hardware-v1 configured profile cannot silently change profile; mapping is advisory/configured and existing conservative veto remains visible.
- Future bounded execution: fixed seed 6006, one sequential driver, smoke W1 then <=9 designed cases, max 100 nodes/200 memberships/8 depth per case, <=1 MiB fixture payload, 30 seconds per case, no model, stop/save first failure. Review limits before execution.

## Recorded peer consultation
- Asked `/root/category_shopify` before implementation about IDs/namespaces, memberships/path and standard/custom taxonomy.
- Shopify answered: product_type is an opaque custom merchant label (including `>` or `/`); Shopify standard category GID is a distinct taxonomy namespace and unavailable in current public extractor; collections are unordered store-scoped membership IDs. Shared ref proposed platform+store+taxonomy+native_id with nullable native IDs for labels; mapping separate from fact.
- Agreed with Shopify: current category_path is compatibility projection only; unknown/missing, null and explicit empty must stay distinct. Woo parent absence remains unknown.
- Sent same proposal/question to `/root/category_magento`; response pending at initial save. Open decision: shared catalog/store scope representation and graph serialization/versioning.

## Remaining gates
Behavior/test design, task breakdown, independent G1, skeleton/G2 and reusable components/G3 precede category code. Live category hierarchy and malformed/stress behavior remain unverified; fixtures above are designs, not results.

## Final contract ACK — implementation wave, 2026-10-17
Read final spec/test-design/research/skeleton/components/contracts and all five peer platform findings (Shopify, Magento, Shopware, BigCommerce, generic); G1/G2/G3 pass recorded in reviews.md. Adopt explicit facets via shared source_fact/Normalizer support, shared CategoryObservation/TermRef, namespace woocommerce:product_cat, store/catalog ownership distinct from channel/locale assignment, unordered memberships and separate derived mapping/codec. Legacy category_path remains unchanged. Woo owns only categories/adapters/woocommerce.py, optional extractors/woocommerce.py, tests/test_category_woocommerce.py and these findings. No extractor change expected: existing capture already retains native categories. No HTTP/tree/admin enrichment or inferred ancestry.
Asked active shared owner category_bigcommerce to confirm common merchant-scope helper and exact namespace before affected source code; helper answer pending. Test execution waits for root serial barrier. Planned controlled capture cases refine C02/C10/C11/C12/C22: siblings/permutations/duplicate support; missing/null/[]/malformed; ID-only vs label-only and rejected ID with supported label; changed capture; subdirectory stores/catalogs; limits and label separators. Source metadata uses explicitly synthetic .test URL/time; all facts must come from real capture/source_fact, never manufactured observed facts.
Shared owner answered before code: namespace confirmed; use categories.helpers.merchant_scope(scope) (platform/store/basepath/catalog, channel/locale excluded) and observation_id(scope,namespace,relation,pointer). Exact duplicate (ref,label) terms merge with concatenated facts; same-ref conflicting labels remain competing terms. Positive integer or exact nonempty string IDs accepted, booleans rejected by conversion. Shared source_fact handles rejected facets independently. Relevant scope/dedup questions resolved; optional slug binding question pending and slug handling blocked until answer.
Shared owner resolved slug question: omit typed slug facet in initial slice; code_context is reserved for taxonomy code-set identity. Original captured categories retain slug, while new term facts bind only independent native_id/label. All relevant peer questions resolved before affected code. Woo adapter and controlled source tests authored; extractor unchanged. Tests deliberately not run while common author writes; root serial barrier required.
