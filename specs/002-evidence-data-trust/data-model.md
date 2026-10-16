# Data model and field coverage

## Records
- Evidence: e_UUID, actual source_url, aware UTC observed_at, method, excerpt and/or
  retained_data + resolving pointer; unverified source_role by default; truncation flag.
- FieldObservation: o_UUID, field_path, support state, raw/normalized values, evidence
  IDs, reason, transformation explanations, optional score/kind and validated confidence.
- FieldResolution: field_path, state, all observation IDs, optional selected observation,
  policy/version and rationale. Selected observations must be observed and same-field.
- TrustContract: schema_version=1, evidence, observations, resolutions. IDs unique
  within a contract. A full portable record bundle and persistent ID scope follow later.

## Coverage matrix
All paths below are factual and require observed support or an explicit unavailable
state. `factual_paths` includes collection containers, empty containers and leaf values.

| Record | Factual fields |
| --- | --- |
| Product scalars | title, price, currency, description, image_url, product_url, external_id, sku, gtin, mpn, vendor, product_type, in_stock, condition, compare_at_price, pack_quantity |
| Product collections | variants, tags, additional_images, category_path, attributes, bundle_components |
| Variant scalars | variant_id, title, price, sku, in_stock, gtin |
| Variant collections | attributes |
| Derived metadata (excluded) | canonical_product_id, canonical_variant_id, supplier_id, platform, scraped_at, raw_data |

Source IDs (`external_id`, `variant_id`) are facts; canonical IDs and supplier scope
are derived identities. Platform is detection metadata; scraped_at is a pipeline
clock, never substituted for evidence observation time. raw_data is a source envelope,
not a catalog fact. Source-backed extracted attributes within it must be mapped to
factual fields. No other Product/Variant field is excluded.

Examples: `/price`, `/tags/0`, `/variants/0/price`,
`/variants/0/attributes/color`, `/attributes/size~1color~0`.
Standalone Variant paths are relative to that variant (`/price`, `/attributes/color`).
Container support does not automatically support children. A factual field absent
from a contract appears unsupported, including empty collections. Unknown is explicit
absence determined by capture, not inferred from scalar defaults.
