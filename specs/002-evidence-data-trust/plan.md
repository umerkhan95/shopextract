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

Version 1 has contract-local evidence/observation UUID IDs. Persistent lookup uses
snapshot and owner scope. Importers reject duplicate IDs within a contract,
malformed states, non-UTC timestamps and dangling/cross-field references.
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

## #36 resolution policy — planned before implementation
`_resolution.py` resolves a validated TrustContract into a deep independent copy.
It never changes product scalars, evidence timestamps, support states or scores.
An explicit UTC `as_of` is required. Default age windows are 24 hours for supplier
offer fields and 30 days for specifications; configurable positive windows are
recorded in every rationale alongside evaluation time and policy/version. All
referenced evidence must be fresh and not future-dated. Mixed-role support takes
the weakest authority; an unverified component cannot inherit verified authority.

Offer fields at product/variant level: price, compare_at_price, currency, in_stock,
condition, sku, external_id, variant_id and product_url. Supplier evidence outranks
unverified evidence; manufacturer roles are not eligible offer sources. Other
fields use verified_manufacturer > supplier > unverified/manufacturer. No domain
inference or automatic source registration. Source-role labels are explicit caller
assertions, not authentication or verification performed by the library.

Only observed candidates compete. Stale/future/unsupported candidates stay visible
with exclusion explanations. Authority breaks disagreements; recency only determines
eligibility. Tied conflicting normalized values remain unresolved. Equivalent
values choose the lexicographically smallest observation ID, never an arbitrary
input position. Numeric normalized types compare by value with bool kept separate;
strings use NFC and trimmed whitespace, with case folding only for title/vendor/
condition. Identifiers remain case-sensitive and no units/GTINs are guessed. Lists
are ordered, dictionaries order-independent. Currency/money cross-source comparisons
require caller-aligned context; resolver does not convert currencies or join products.

Inputs must describe one already-aligned product revision; indices and JSON pointers
are not cross-store variant identity. Automatic merging/alignment is outside #36.
Public `classify_match`/`match_products` add field-support references for attached
contracts but keep existing relationship/confidence logic and product scalars.
Persistence, retention deletion and full portable bundles remain #37/#38.

## #37–#39 implementation plan — 2026-10-16

Research and issue snapshots are saved in `artifacts/epic-22-production/`.
Remaining scope is #37 persistence/retention, #38 portable exports, and #39
offline acceptance/compatibility; #34–#36 remain existing foundations.

Use additive SQLite tables in the same transaction as snapshots and identity
aliases, while preserving legacy `products_json` for monitoring. Store attached
Product/Variant contracts explicitly; never infer captured support from `asdict`
or historical scalars. Shared typed record serialization lives in `_portable.py`
and preserves Decimal, UTC datetime and reserved mapping keys. Migration is
versioned/idempotent and rejects unsupported newer versions.

Evidence lookup is scoped by snapshot, record owner and evidence ID. Default
retention never automatically deletes support; explicit pruning defaults to dry
run and protection of retained references. Expiring referenced data must create
explicit tombstones and downgrade effective observations/resolutions so trusted
values cannot survive deleted support. Hashes check integrity, not authenticity.

Portable bundle loading validates version, references, typed values and bounds;
legacy dict exports retain their current defaults. Opt-in CSV/feed companions
map rows to bundle records and verify the exact exported file digest.

Three research roles precede three skeleton-owner roles; each skeleton owner
reviews against research before handoff to three separate implementation roles.
The runtime limits concurrent workers; roles run in bounded phases. Small saved
baseline: 74 affected tests passed. Final acceptance requires restart, rollback,
legacy migration, reference-aware retention, lossless export and the offline
E2E matrix. A final full offline suite must pass before completion is claimed.

## #39 implemented verification architecture

The offline `examples/evidence_trust.py:run_demo` is shared by the acceptance tests.
It uses the real feed parser and capture/normalization, fixed UTC resolution,
file-backed SQLite save/load with separate connections, scoped evidence retrieval,
and portable file write/read. Its synthetic fixtures cover explicit zero/false,
missing support, nested GTIN transformation and escaped attribute pointers with
competing supplier/manufacturer observations. Inspection computes all factual paths
for Product and standalone Variant owners; available facts require retained local
support and stored lookups. Counts measure fixture coverage, never accuracy.

Retained expiry metadata travels in optional Product/Variant
`evidence_availability` attachments, separately from valid effective TrustContracts.
Each list entry contains evidence_id, expired status, reason, aware UTC expired_at
and payload-free metadata. Portable records carry product availability plus
index-aligned variant_evidence_availability. Retention declares support unavailable;
it is not secure erasure of raw capture copies, old bundles or backups.
