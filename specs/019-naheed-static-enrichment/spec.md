# Static product enrichment and listing category evidence

## Outcomes
FR1: Unified static and browser HTML paths reject known placeholder images, retain genuine structured images, and enrich a single product from MagicZoom gallery, `.brand-name` link and `span.sku` before fast-path completeness checks. Each enriched value retains distinct HTML provenance; original JSON-LD capture remains unchanged. DOM fields must not leak across multiple products. No phone-number GTIN inference or fabricated shade variants.
FR2: Detect Magento from module/RequireJS HTML signatures even when APIs return 403. Generic no-signal fallback reports confidence zero; confidence remains a heuristic fraction, not probability.
FR3: Provide explicit bounded listing-page acquisition/indexing from saved category URLs. Only product-card links imply product membership; category heading labels and source URL are retained. Pagination stays within the same store; failed/truncated acquisition is partial. Exact product URL matching never infers taxonomy IDs, hierarchy, or negative membership from absence.
FR4: Category CLI can build the listing index and opt-in apply it during `categories normalize`; mapper consumes a separate merchant listing namespace using existing evidence/mapping contracts. Defaults and legacy constructors/feed formats stay unchanged.

## Scenarios
SC1: JSON-LD price + placeholder with MagicZoom gallery/brand/SKU returns static enriched product without browser, genuine images and observed HTML provenance.
SC2: Placeholder-only products remain incomplete/image empty; mixed images keep real entries; valid structured images/brand/SKU win; missing SKU remains missing; multi-product document receives no global DOM fields.
SC3: Magento HTML with blocked APIs is detected; bare prose is not a signal; no-signal generic confidence is zero.
SC4: Two categories list one product, with duplicate links/pagination: index retains both memberships once, no navigation/recommendation links; category URL/heading source evidence survives normalize and portable record validation.
SC5: Unavailable page, pagination cycle, cross-origin link/redirect, missing heading, malformed HTML, page/link/byte budget boundaries: no invented facts; acquisition status and reason remain inspectable and partial when bounded.
SC6: CLI XML/JSON URL input -> index artifact -> normalize --listing-index -> exact taxonomy rule mapping; invalid scope/shape rejected, default normalize remains unaffected.

## Boundaries
Analytics item_category/item_brand are not authoritative category sources and are not scraped in this slice (DOM brand is preferred). No GTIN/variant invention. Live Naheed acquisition is subject to environment network access; synthetic fixtures prove mechanisms only. Saved 757 URL evidence remains input, not completed membership proof.
