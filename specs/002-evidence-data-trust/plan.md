# Implementation plan

## Constitution check
Existing dataclass fields and positional constructor signatures are unchanged.
Trust types are re-exported by `_models.py` and the package. Product/Variant gain
methods and non-dataclass contract attachments; `asdict` signatures and existing
snapshot/feed shapes stay compatible (raw data now includes reserved capture metadata). Offline
contract fixtures plus affected regressions verify behavior. No inference or paid
service is required; all source remains under the repository MIT license.

## Architecture
`_evidence.py` owns dataclasses, validators, typed contract serialization, factual
path enumeration and conservative trust inspection. `_models.py` exposes the
contract and adds `Product.trust_view(contract=None)` and the equivalent Variant
method. Contracts can be passed explicitly; #35 adapters carry capture context and
normalization attaches contracts without extending dataclass constructor fields. Never infer observed support from constructor arguments.

Version 1 has bundle-scoped evidence/observation UUID IDs. Importers reject duplicate
IDs, malformed states, non-UTC timestamps and dangling/cross-field references.
Resolution policy is recorded, not executed here. Multiple observations require a
resolution even if normalized values appear equal; #36 defines equivalence.

An unknown observation means an adapter explicitly found no value. Unsupported
means capture/support is unavailable or a scalar may be a legacy default. Expired
means previously retained support is unavailable. None is never an observed scalar;
empty lists/maps, zero and false can be observed with capture. Legacy values are
shown separately, never selected as trusted values.

## Capture and operating limits
#34 uses bounded offline fixtures only. #35 implements byte budgets and explicit
truncation, preserves fetched URLs, and retains pointer-resolvable source. Contract
validation does not enforce a production byte budget yet. #37 owns storage limits,
reference lifetime and pruning; no deletion/migration defaults are invented here.
Contracts are mutable; validation runs on construction, serialization and inspection
so mutations cannot silently introduce dangling support. Applications should avoid
mutating contracts during inspection/serialization.

## Handoff
#35 consumes the field matrix and appends transformation records. #36 consumes the
resolution interface and records policy decisions. #37 stores these semantic values
atomically. #38 designs the full Product/evidence bundle; this contract's serializer
is not a Product import/export API. #39 adds the end-to-end compatibility proof.

Normalization compatibility: a missing/zero-price record is accepted when it has an
image or identifier; a title-only record is rejected by the existing validity gate.
The missing-field fixture uses a SKU so all three absent fields survive normalization.

## #35 capture architecture
Adapters carry a reserved `_capture` context in raw dictionaries; normalization
creates an attached TrustContract accessible as `product.evidence_contract` and
by `product.trust_view()`. The attachment is not a dataclass field, preserving
existing positional constructors/asdict/snapshot exports. Standalone normalization
also emits explicit unsupported observations when no capture exists.

Capture stores relevant source projections, not complete pages. Each retained
fragment is capped at 4096 UTF-8 JSON bytes and each product capture/contract at
65536 retained payload bytes. Oversized fragments are omitted, never silently
shortened into factual support. Other fields may still be supported; truncation
flags/reasons expose omissions. Budgets apply per product, not per extraction run.
API items are captured before enrichment. Detail barcode captures use matched
variant IDs and their own fetched URL/time. CSS support requires an actual matching
selector node in retained HTML; unsupported mappings are explicit. LLM outputs
without verifiable spans remain unsupported. Layered fallback values without a
retained mapping remain unsupported. No calibrated confidence is generated.

## P2 review corrections: normalization is the source-selection authority
`_normalization.py` supplies selections and typed ConversionOutcome records. Each
platform normalizer returns NormalizedData with outcomes containing actual source
pointers/inputs, conversion success or rejection, normalized results and operations.
Selections use raw input semantics, independently of retained capture availability.
Money conversion is performed once, using adapter-specific rules; only CSS cleans
currency symbols and separators. Variant emitters record source/output positions
while constructing variants, using each platform's stock/ID/title semantics.

`_capture.py` consumes these outcomes and builds contracts; it does not parse prices,
select fallback inputs or interpret platforms. Rejected conversions and default NEW
conditions cannot become observed. Selected inputs must match retained fragments,
and emitted values must match accepted outcomes. Image fallbacks overwrite the
outcome only when the normalizer actually chooses that source. Browser extraction
passes the final result.url to both JSON-LD and OpenGraph capture.

Live validation extends the same outcome abstraction to native Magento GraphQL
final-price/currency/stock fields and Shopware Store API calculatedPrice/available/
children fields. This adds normalization support, not automatic API discovery or
GraphQL fallback adapters. Cookie/context-derived currency has separate captured
source context selected through adapter-provided field-source references. Aggregate
stock tracks individual availability/inventory inputs. Capture retains leaves before
ancestor projections so duplicate nested containers cannot starve later factual
fields within the fixed budget. Feed price tokenization supports currency prefixes
and suffixes; CSS records unambiguous currency-symbol and relative-image conversions.
Saved live sample coverage and limitations are recorded in verification.md.

Subsequent platform routing integrates the native mappings with Magento GraphQL,
Shopware Store API and BigCommerce Storefront GraphQL adapters. API endpoint/token
options and explicit legacy Magento REST selection are documented in
`docs/storefront-apis.md`. This capability integration is separate from #35's
contract-capture deliverable; the earlier live adapter limitations are historical.
All API and fallback HTML observations still use the shared normalization outcomes.
