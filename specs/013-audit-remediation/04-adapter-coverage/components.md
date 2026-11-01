# Adapter components — G3 proposal

A1 `_normalize._normalize_woocommerce` uses existing Normalizer/Variant/evidence builders for
one distinct brand and supplied record aliases. It preserves exact IDs,decimal
prices,tri-state stock and attributes; duplicate IDs rejected with raw adapter
diagnostic. Supplied child source paths prefix parent capture. Detail enrichment
in WooCommerceExtractor is optional and per-extraction state:parent-declared IDs
only,5attempts/parent,20EXTRA detail attempts global excluding catalogcalls.
Identity and parent_id checked before merge. Failed/missing/limited details retain
all base records and explicit incomplete reason. Each detail uses actual HTTP
capture,field-source map keyed normalized childfield; normalizer consumes this
source mapping,never recaptures enriched aggregate as fetched fact.

A2 Shopify existing ID enrichment owns absent unmatchedvariant error alongside
existing429/productmismatch,without fabricated barcode or added defaultrequest.

A3 MagentoGraphQLExtractor owns closed capability allowlist media_gallery/brand/
gtin and core query builder; categories existing optin preserved. Invalid options
fail before HTTP. Unknown optional field triggers ONE core retry; persistent core
error returns explicit partial/error,no loop. Per-extraction capability fallback
state and request accounting. `_normalize._normalize_magento_graphql` maps actual supplied fields/paths,
not arbitrary customattribute guesses. Default core query untouched.

Public `_extract` and CLI own option validation/forwarding; unsupported platform
Woo enrichment rejects before network. Existing dataclasses/constructors and
capture machinery reused,no new cache/lifecycle. `_detect` HTMLmarkers reuse current
fetch response; signal-free generic confidence0.27tests cover these substeps;
implement A1,A2,A3 sequentially,not a runtimearchitecture rewrite.
