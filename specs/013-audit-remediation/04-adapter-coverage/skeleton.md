# Adapter coverage documentary skeleton — no implementation

G1PASS. Concrete substeps remain independently traceable,not oneblindrefactor.
A1 Woo normalization reuses Normalizer/Variant/capture:singlebrand->vendor,
variants/variations record aliases preserve child fields/sourceprefix;duplicate
IDs rejected with adapter diagnostics. Woo.extract(shop_url,*,enrich_variants=False)
uses parent-declared IDs,atmost5details/parent and20total,identity checks,retains
base+reason onfailure. Public extract/CLI --enrich-variants forward only toWoo;
unsupported platforms reject flag. Field-source maps point to detailcaptures.
A2 existingShopify ID enrichment records unmatched variant IDs as explicit errors,
base retained,no barcode fabrication,existing429/productID checks reused.
A3 MagentoGraphQL.extract(...,capabilities=()) accepts exact allowlist media_gallery,
brand,gtin; defaultcorequery unchanged. Unknown-field response retries coreONCE,
retains requested-field-unavailable diagnostic. Public API options/CLI storefront
JSON forward closed capability list onlyforMagentoGraphQL. Normalize actual returned
paths,not guessedcustomattributes;categories opt-in unchanged. Detection addsHTML
Magento signals;fallbackgeneric confidence0(no calibratedcertainty claim).

No new constructors/identity scheme;new args optional. Existing errors/ExtractorResult
own partial state;capture/Normalizer own factual support. Acceptance tests exercise
actual HTTP loops/normalization/publicCLI/API,not a duplicated adapter. G2 then
components/G3 required before each bounded production substep.
