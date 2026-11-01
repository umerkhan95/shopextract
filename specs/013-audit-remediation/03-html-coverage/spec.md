# 03-html-coverage — behavior specification

2026-11-01; implementation authorized umbrella-wide; this assignment DESIGN ONLY.
AR13; parent FR04,SC06. Preserve available structured/HTML fields without guessing product identity.

## Outcomes and requirements
FR-H1: bounded JSON-LD traversal recognizes exact Product/ProductGroup in root,lists,@graph,ItemPage.mainEntity and same-document @id references; visited-set prevents cycles,256nodes/8depth. Preserve each source path, deduplicate by node identity, no SEO replacement of supplied product title. External @id links are not fetched.
FR-H2: reject known placeholder/spacer/data-image patterns for primary image with explicit diagnostic, then choose supported real image from JSON-LD,OG,lazy data-src/srcset or product gallery; stable source order,exact-URL dedup,max20 images. No extra image HTTP requests needed for semantic placeholder detection; unavailable status remains unverified.
FR-H3: collect product-scoped span.sku/itemprop sku,Magento form product input ID,ordered BreadcrumbList and product gallery. Explicit structured fields outrank fallback; contradictory IDs/brand retained as conflicts. Breadcrumbs retain labels/positions, omit home/product leaf from category projection only by explicit type/link identity, never arbitrary text guess. Source timestamps/paths captured.

## Acceptance scenarios
SC-H1: equivalent root/@graph/ItemPage/linked Product retain title,GTIN,brand,SKU once; cyclic @id stops,externalref no request;257nodes rejected/diagnostic without fabricated product.
SC-H2: placeholder+real lazy/gallery chooses real; placeholder-only image unknown with warning; genuine filename containing generic word alone not auto-rejected; repeatedURL once.
SC-H3: product SKU vs footer unrelated SKU selects scoped product; conflicting authoritative values unresolved; breadcrumb shuffled positions sorted deterministically; malformed/missing positions retain diagnostic and no invented hierarchy.
SC-H4: existing free ProductGroup/policy rejection/native formats remain controls; gallery limits19/20/21 enforce bounded retention with reason.

## Boundaries and compatibility
Child01 functional review passed; full-driver/live gate remains pending. Preserve
constructors,identity,default feed syntax. No production/tests changed here.
Each numbered substep gets executable red tests and independent gates before code.

## Shared-parser refinement before skeleton/tests

FR-H4: browser-free structured parser owns JSON-LD/OG admission and scoped HTML
field enrichment; Unified and native tools.domain consume it. Explicit Unified
browser-class import still loads browser dependencies per runtimeR1 contract;
actual native generic parse must not import crawl4ai/playwright. No parser duplicate
in domain or mock substitute. This targets observed coupling,not guaranteed timing.
Private parser result contains products+diagnostics; legacy Unified static method
continues list projection. Fatal limits reject offending block with diagnostic,
never fabricate product; callers preserve partial/failure semantics.

Traversal counts JSON containers(dict/list),rootdepth0,max256containers/depth8;
preflight block limits before traversal/resolution. Same-document @id index only,
no network. Diagnostics use codes jsonld_budget_exceeded,external_reference_ignored,
placeholder_image,image_budget_reached,breadcrumb_invalid,conflicting_sku.
DOM additions retain _field_sources pointing to actual captured dom projections;
_html_field_conflicts preserves conflicting values. No source default promoted to
observed support. productID is input[name=product] scoped to product add-to-cart
form; SKU scoped to main.product/product-info-main,never footer.

## G2 diagnostic/ownership repair contracts

FR-H5: domain.synchronous parse keeps legacy list return when include_diagnostics
absent/False. Native sources opt in with literalTrue and receive JSON object
{products:[portable records],diagnostics:[{code,message,...}]}; validate shape,
never discard diagnostics or infercomplete from list length. Sources retain issues
in graph diagnostics collection and partial result; empty fatal ->existing
source_error containing diagnostic code,no successful empty catalog. Unified.extract
consumes shared result internally,retains good products but complete=False/error
includes codes on over-budget blocks or invalid breadcrumb; legacy static list
projection remains compatible. One bad block doesn't erase independent good block.

FR-H6: DOM fields belong only to a unique owner: exact pageURL match via explicit
Product.url or exact @id,otherwise exact existing productID/SKU match to scoped
add-to-cart form identity; when only one admitted product,it may own main section.
Multiple matches/no unique match ->all fallback SKU/productID/gallery/category
fields left unset/unsupported,ambiguous_dom_owner diagnostic. No ownership from
position/title/similarity. Main/recommendation structured fields remain independent;
only selected owner gets DOM source maps. Existing structured values untouched.
