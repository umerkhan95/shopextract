# Field source resolution

`resolve_fields(contract, as_of=..., policy=...)` resolves already-aligned evidence
without overwriting observations, Product scalar defaults, identities or scores.
It returns an independent `TrustContract`; assign that contract to
`product.evidence_contract` to inspect selected values through `product.trust_view()`.
All alternative observations and their evidence remain inspectable.

```python
from datetime import datetime, timedelta, timezone
from shopextract import ResolutionPolicy, resolve_fields

resolved = resolve_fields(
    product.evidence_contract,
    as_of=datetime.now(timezone.utc),
    policy=ResolutionPolicy(offer_max_age=timedelta(hours=12)),
)
product.evidence_contract = resolved
print(product.trust_view()["/price"])
```

Use a saved UTC `as_of` when replaying a decision. The resolver never reads the
clock. Naive/non-UTC timestamps and nonpositive age windows are rejected. A replay
with the same observations, evaluation time and policy yields the same result
regardless of evidence or observation ordering.

## Version-one authority

| Field group | Authority, highest first |
| --- | --- |
| Offer: price, compare_at_price, currency, in_stock, condition, sku, external_id, variant_id, product_url | `supplier`, `unverified`; manufacturer roles are ineligible |
| Specifications and other fields | `verified_manufacturer`, `supplier`, then `manufacturer` / `unverified` |

Offer classification applies to exact root and `/variants/<index>/...` fields.
An attribute named `price` is still a specification attribute. Unrecognized roles
have unverified specification authority and no offer authority. The stored policy
is `field-source-authority`, version `1`.

`Evidence.source_role` is an explicit caller assertion. Establish verified
manufacturer authority through your own reviewed source registration; assigning
that string is not verification performed by this package. A manufacturer-looking
hostname, model score or matching score never confers authority. Automatically
captured evidence remains `unverified` until the caller establishes its role.
Manufacturer list prices cannot become supplier offer prices merely because
manufacturer specifications have greater authority.

Each observation uses the weakest role across all its referenced evidence. Every
referenced timestamp must be at or before evaluation time and within the field's
age window. The defaults are 24 hours for offers and 30 days for specifications.
An age exactly equal to the limit is eligible. A stale supporting fragment excludes
the whole observation; a newer fragment cannot conceal it. Future-dated evidence
is excluded. Limits and evaluation time are recorded in the resolution rationale.

Only `observed` candidates compete. The highest eligible authority wins if its
candidates agree; lower-authority disagreements remain retained. Recency determines
eligibility and does not resolve disagreements among peers. Tied differing values
remain `conflicting` with no selected observation. If top values are equivalent,
the smallest observation UUID is a deterministic representative, not a confidence
or correctness claim.

Normalized numeric values compare by numeric value, with booleans distinct from
numbers. Strings use NFC and trimmed whitespace; title, vendor and condition also
collapse whitespace and case. Identifiers remain case-sensitive; textual numeric
values are not silently numbers. Lists retain order; dictionary key order does not
matter. No unit conversion, fuzzy equivalence, currency conversion or GTIN repair
occurs in the resolver. Original raw and normalized values remain unchanged.

No eligible candidate yields an explicit unavailable resolution: stale-only support
is `expired`, wholly unsupported inputs remain `unsupported`, and otherwise it is
`unknown`. Reasons retain every exclusion. These policy-age expirations do not
prune evidence or change stored observation states; storage retention belongs to #37.

## Alignment and operating boundaries

Supply observations for one aligned product revision, offer scope, currency and
field meaning. This API does not merge catalogs, choose a merchant, align variant
array positions across sources, or reinterpret a manufacturer list price as an offer.
Remap variants using their identities before combining contracts. IDs are
bundle-scoped; duplicate/dangling IDs are rejected. Calling `resolve_fields` again
replaces policy decisions using all original observations, including prior losers.
The API does not choose which prior manual resolution to keep.

## Matching report references

`classify_match` and `match_products` now add `MatchDecision.field_support` for
Product objects with attached evidence contracts. Side `a`/`b` entries contain
field state, observation/evidence IDs, selected observation and policy/version/
reason. Unmatched and semantic candidates also retain references. Without a
contract, the side has no fabricated support. Rules and existing matching
`confidence` semantics remain unchanged; field resolution is explanatory, and does
not silently rewrite matching inputs or authorize a cross-store identity match.

These lightweight references resolve through the original Product's contract:

```python
references = decision.field_support["a"]["/price"]
evidence_by_id = {e.evidence_id: e for e in product_a.evidence_contract.evidence}
retained = [evidence_by_id[key] for key in references["evidence_ids"]]
```

`resolution_references(contract)` exposes the same reusable report format.
A single observed input can be referenced before policy is applied; its policy is
null. Existing model/rule scores and genuine validated-confidence metadata remain
on their original observations. The resolver never creates confidence values.

This is an additive MatchDecision report field. Product/Variant constructors and
scalar/asdict shapes are unchanged. Persistence, portable independent report
bundles and restricted-format sidecars remain #37/#38; lightweight IDs alone are
not claimed to be an independent export.

Run the deterministic offline example:

```bash
PYTHONPATH=src python examples/field_resolution.py
```

## Live verification

The 2026-10-16 live matrix passed 12 cases across all six supported families and
seven sites, including five independent API/HTML pairs. It audited 5,282 field
resolutions; synthetic fault probes were labeled separately. Shopware's supported
22 EUR API price correctly outranked an unsupported HTML price default without
fabricating a conflict. Magento retained both supported 69 EUR observations.
See `artifacts/field-resolution-live/review.md` for journals, counts and boundaries.
These two real captures also replay offline in `tests/fixtures/field-resolution/`.
