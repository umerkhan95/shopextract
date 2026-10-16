# Magento discovery and component proposal

Status: discovery only, 2026-10-17. No source/test changes or execution.
Structured evidence: `artifacts/category-mapping/findings/magento.json`.

## Existing seams and reuse
- `extractors/magento_graphql.py:9`: fixed `_FIELDS` contains no category fields;
  configurable children reuse these fields. Reuse bounded product pagination,
  response capture/source time, duplicate SKU rejection and partiality behavior.
- `extractors/magento.py`: explicitly selected legacy REST product extraction;
  no category lookup. Raw fields may be retained but are not newly observed here.
- `_normalize.py:352` has dedicated GraphQL normalizer and Magento dispatcher;
  retain central normalizer ownership and existing Product/Variant signatures.
- `tools/sources.py` reuses guarded native extraction. Central security owner
  must verify Magento fixed-query authorization before changing any query.
- Preserve default public API/portable records; proposed categories use an opt-in
  companion record. `category_path` remains a legacy projection.

## Verified official semantics
[Adobe categories](https://developer.adobe.com/commerce/webapi/graphql/schema/products/queries/categories/)
returns paginated CategoryResult items, immediate children, and parent breadcrumbs.
No filters means the store default root. Its example selects uid/name/level/path;
recursive tree selection has explicit depth, with default queryDepth 20.
Adobe Commerce SaaS does not support this PaaS query.
[Product interfaces](https://developer.adobe.com/commerce/webapi/graphql/schema/products/interfaces/)
was navigation only: exact product category selection is unresolved.
No new live category observation is claimed; saved prior query captures omit it.

## Shared contract proposal
- Opaque UID preferred when observed; legacy numeric ID retained separately as
  text. Never decode/equate UID and ID without explicit evidence.
- Term identity: platform + taxonomy namespace + native ID. Observation scope:
  supplier origin + shop/base path + optional store-view/catalog/locale.
  Taxonomy namespace/version remains distinct from observation scope.
- Memberships are unordered; ordered ancestor chains require explicit source
  hierarchy. Do not turn membership order, depth, URL or labels into ancestry.
- Preserve missing/null/empty/malformed separately; membership and category graph
  coverage are independent. Mapping decisions/rule versions remain derived data.
- Preserve source evidence and competing labels; no deepest-category heuristic.
- Exact ProductInterface categories selection, ID deprecation, breadcrumb schema,
  Store header scope/auth and native guard query acceptance remain unresolved.
  Verify these before implementing opt-in fixed queries; no dynamic GraphQL.

## Predesigned fixture risks and exact outcomes
1. MG01: memberships X/Tops,Y/Sale then reverse; identical memberships, no path.
2. MG02: UID X on two store views with localized names; retain distinct scope,
   no implicit cross-store identity or ID replacement by label.
3. MG03: omitted/null/[]/scalar category fields; four states, only [] observed empty.
4. MG04: explicit ancestor A/B/member C plus unrelated D; only A/B/C chain,
   D ancestry unknown; graph and membership completeness stay separate.
5. MG05: ID 7 plus UID Nw==, malformed/empty UID and conflicting duplicate labels;
   no decoding/equality inference, invalid ID unsupported, conflicts preserved.
6. MG06: product budget clips page2 with partial category evidence and replay;
   extraction remains partial, taxonomy completeness unknown, deterministic replay.
These are designs, not executed tests or verification evidence.

## Peer consultation and decisions
Shopify and WooCommerce received direct questions on scoped opaque IDs and ordered
hierarchy before implementation. Both agree memberships are unordered and scope
is explicit. Shopify requires global taxonomy namespace/version separate from
store assignment; raw product_type has no ID. Woo requires product_cat namespace,
explicit parent=0 root versus missing parent unknown and separate graph coverage.
Generic requested the same explicit path/source-vs-mapping separation; no conflict.
BigCommerce shared synthesis agrees companion codec and separate observation scope.
Adopt those common contracts; Magento store-view details remain an explicit gap.
No implementation until shared G1/G2/G3. Token counters unavailable to this agent.

## Final contract ACK — implementation gate
Read final spec/test design/skeleton/components/contracts, own findings, coordinator
magento-schema-minimal and all five peer findings. Accept final shared source_fact,
merchant_scope/observation_id, facet binding, companion codec and shared mapper.
Magento adapter emits only unordered magento:category memberships, UID opaque text,
labels independent, no Store header/root/path inference. Existing default query stays
unchanged; opt-in finite categories { uid name } verified by coordinator schema.
Nonzero product error localization/response metadata remains shared core ownership.
Asked shared core exact response helper and query flag before extractor edits;
asked Shopify peer for final helper/scope constraints. No tests run before serial barrier.

Implementation authored: dedicated adapter/extractor/test files only. Shared core
confirmed include_categories flag, _QUERY_WITH_CATEGORIES, native_body and
attach_category_diagnostics signatures. Shopify confirmed helpers, exact(ref,label)
dedup preserving facts and conflicting labels. Default query untouched; opt-in GET
adds UID/name only, category errors preserve valid products and localized siblings.
Tests cover facets, source states, scope/dedup/caps, exact query flags, nonzero item
error paths, partial-data retention and default error rejection. Await serial barrier;
no tests/compile/network executed by this author.
