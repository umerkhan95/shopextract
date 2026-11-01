# 04-adapter-coverage — behavior specification

2026-11-01; implementation authorized umbrella-wide; this assignment DESIGN ONLY.
AR14; parent FR04,SC07. Separate adapter substeps, shared parent/variant ownership and honest absence.

## Outcomes and requirements
FR-A1: Woo brands[].name maps vendor deterministically (one distinct brand accepted,multiple conflicting brands diagnostic). Normalize supplied variations/variants using existing Variant model, exact IDs,prices,stock,attributes and source support. Where public API only lists variant IDs, opt-in detail enrichment bounded at5 extra requests/product and global request limit; unavailable details remain absent with reason.
FR-A2: Shopify missing bulk barcode remains absent. Existing opt-in enrichment matches product+variant IDs, validates GTIN, preserves leading zeros;429/mismatch retains base product and explicit missing reason. No bypass of throttling or “100% coverage” promise.
FR-A3: Magento GraphQL core query remains schema-safe. Reuse opt-in native categories; request gallery/brand/GTIN only via explicit capability allowlist and fallback core once on unknown-field response, budget accounted. Normalize actual returned attributes with original paths; unknown custom attribute names not guessed. Add HTML Magento signals; generic no-signals fallback confidence0, not calibrated probability.

## Acceptance scenarios
SC-A1: Woo singlebrand/empty/multiple, parent2variants distinct IDs/options/prices, missing stock unsupported; repeated child IDs reject with diagnostic instead of merging.
SC-A2: Shopify detail429/productID mismatch/variant mismatch leaves base data and no inventedGTIN; supported barcode accepted; max enrichment request boundary stops with partial reason.
SC-A3: Magento optional field rejected ->one core retry retains core; supported gallery/brand/GTIN/categories preserve paths; categories opt-in unaffected; no schema capability ->no speculative query.
SC-A4: Magento HTML markers plus blocked APIs detectsMagento; no signals generic/confidence0; existing Shopify/Woo positive detection controls.

## Boundaries and compatibility
Child01 functional review passed; full-driver/live gate remains pending. Preserve
constructors,identity,default feed syntax. No production/tests changed here.
Each numbered substep gets executable red tests and independent gates before code.

Portable compatibility amendment: unknown supplied/enriched variant stock isNone as
already specified,so Variant.in_stock must accept bool|None. Keep defaultTrue and
positional fields unchanged. Existing real bool values and source contracts must
roundtrip; text'unknown' stays invalid. Product stock/model migration is outofscope.
