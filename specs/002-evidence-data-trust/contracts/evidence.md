# Public evidence contract v1

Import Evidence, FieldObservation, FieldResolution, SupportState, TrustContract,
ValidatedConfidence, factual_paths and trust_view from `shopextract` or `_models`.
`Product.trust_view(contract=None)` and `Variant.trust_view(contract=None)` return
path-indexed support states with reason, trusted value, legacy_value, observation IDs
and evidence IDs. IDs are `e_` or `o_` followed by a canonical lowercase UUID.

## State invariants
- observed: non-null normalized value and captured evidence IDs. Zero/false and
  supported empty collections are permitted.
- unknown: explicit absence, with reason. Trusted value is unavailable.
- unsupported: source support unavailable, including legacy/default values, with reason.
- conflicting: competing observations require explicit resolution; no selected fact.
- expired: previously captured support unavailable, with reason.

All non-observed observations, including conflicting ones, require reasons and cannot
carry validated confidence. Only observed observations may carry it.
Multiple observations yield conflicting until a resolution is supplied. Resolution
alternatives remain retained even after selection. A conflicting resolution needs at
least two distinct candidates; unresolved states cannot select a fact. A supported
selection must reference an observed candidate on the same field path.

Evidence has absolute HTTP(S) URL, aware UTC timestamp, nonempty method and excerpt
or retained-data pointer. JSON Pointers resolve against retained data; empty pointer
selects the retained root. A source URL alone is insufficient. Capture authenticity
and source-role authority require adapter/policy verification in #35/#36.

## Serialization
`TrustContract.to_dict()` validates the graph and returns JSON-safe data;
`TrustContract.from_dict(payload)` reconstructs it and validates schema version,
IDs and references. A missing/unsupported schema version is rejected. Decimal and
UTC datetime values are tagged with `$type` and `value`; raw maps containing `$type`
are escaped with a mapping tag. Enum values recursively use the same codec, including
validation and tag escaping. Nonfinite numbers and non-JSON values are rejected.
This serializes the trust contract only; the lossless portable Product bundle is #38.

Scores are finite optional raw numbers with score_kind=model or rule. They do not
create validated confidence. ValidatedConfidence requires a finite [0,1] value and
nonempty method, dataset and version. Metadata records a validation claim; callers
remain responsible for supplying real validation artifacts.

Legacy Product dicts remain ordinary Product constructor input. Construct them and
inspect `.trust_view()` for explicit unsupported provenance. No migration timestamp,
synthetic evidence ID or guessed calibration is manufactured.

## Automatic capture (#35)
`normalize()` attaches `product.evidence_contract` and variant-relative contracts
outside dataclass fields. `trust_view()` uses attached contracts by default. API,
feed, JSON-LD/OpenGraph and verified CSS mappings carry source context. Fields with
no retained mapping (including unverified LLM outputs) have explicit unsupported
reasons; explicit empty scalar values have unknown observations.

Retained source payloads use a 4096-byte fragment cap and 65536-byte per-product
capture/contract cap measured as UTF-8 JSON. Omitted support is explicit. Original
values remain in `raw_value` and pointer-resolvable evidence; `transformations`
explain normalization, ID-checked enrichment and opt-in GTIN restoration. The
retained object may be a projection: `source_pointer` identifies its original item
location, while the evidence `pointer` resolves locally against retained data.
Raw dataclass export is not lossless contract export; use the explicit portable
bundle APIs. `resolve_fields` applies the versioned #36 authority policy to explicit
source roles; the caller must establish verified manufacturer roles. Source domains
never verify authority. See `docs/field-resolution.md` for freshness and equivalence.

For response-cookie or API-context fields, a field observation may reference a
separate capture with that response's URL/time; it cannot borrow the product body's
source. Aggregate stock retains its individual contributing input pointers. Native
Shopware Store API children and Magento GraphQL final-price fields use their native
nested paths. Leaf fragments are attempted before duplicate ancestor projections.

## Durable and portable contracts (#37–#38)

`monitor.evidence.save_snapshot(products, domain, *, db_path, metadata=None)` returns
an integer snapshot ID. `load_snapshot(snapshot_id, *, db_path)` returns reconstructed
Product/Variant objects with effective attached contracts. Metadata accepts existing
observation_scope, catalog_complete, incompleteness_reasons and max_urls fields.
`get_evidence(evidence_id, *, snapshot_id=None, record_key=None, db_path)` returns
available/expired/missing/unsupported lookup status; corruption is an error. Owner
record_key is `product/N` or `product/N/variant/M`; IDs alone do not identify an owner.
`prune_evidence(*, db_path, before, protect_references=True, dry_run=True,
batch_size=100)` is explicit and bounded. Default retained references are protected.

Shared `_portable.product_to_record`/`product_from_record` preserve typed model
values and dynamic product/aligned variant contracts. `export._bundle` supplies
create/load_evidence_bundle and write/read_evidence_bundle. Envelope and record
versions are separate from TrustContract schema_version. Optional product
`evidence_availability` and index-aligned `variant_evidence_availability` contain
payload-free expired ID/time/reason metadata and survive transport. Effective
contracts never select facts whose required retained evidence has expired.

Ordinary CSV/JSON/feed defaults remain compatible. Opt-in companions contain
exact-byte SHA-256 and row-to-record mapping. Row positions require verified bytes;
checksums do not authenticate the publisher. Import never refreshes policy decisions
or recreates missing evidence. Raw copies/backups mean pruning is not secure erasure.
