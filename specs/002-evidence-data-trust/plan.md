# Implementation plan

## Constitution check
Existing dataclass fields and positional constructor signatures are unchanged.
Trust types are re-exported by `_models.py` and the package. Product/Variant gain
methods only; `asdict` and existing snapshot/feed payloads stay compatible. Offline
contract fixtures plus affected regressions verify behavior. No inference or paid
service is required; all source remains under the repository MIT license.

## Architecture
`_evidence.py` owns dataclasses, validators, typed contract serialization, factual
path enumeration and conservative trust inspection. `_models.py` exposes the
contract and adds `Product.trust_view(contract=None)` and the equivalent Variant
method. Contracts are passed explicitly; adapters do not automatically populate
provenance yet. Never infer observed support from constructor arguments.

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
#34 uses bounded offline fixtures only. #35 must implement byte budgets and explicit
truncation, preserve fetched URLs, and retain pointer-resolvable source. Contract
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
