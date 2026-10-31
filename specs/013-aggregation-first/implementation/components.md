# Single-responsibility component and reuse candidate

Date:2026-10-31. Candidate G3 model only; no approval assumed.

| Component | Responsibility / real consumers | Reuse boundary |
| --- | --- | --- |
| Google source parser | Strict pinned source→validated Google records; preparation and fixture verifier | New format adapter, no network/mapper/CLI responsibilities. No Shopify attribute schema copy. |
| Immutable Google catalog/index | ID/path/parent/child lookup; options/crosswalk/CLI | Separate records from Shopify rich taxonomy; reuse narrow hash/serialization utilities only after common consumers proven. |
| Resource integrity and loader | Strict digests/identity/selection; Python+CLI+package | Follow Shopify cache-hit integrity pattern; preserve existing Shopify resource code/defaults. |
| Preparer/publisher | Validate→stage→atomic new immutable directory; build/manual setup | No downloads on import/install, no hidden mutation of old catalog; explicit source provenance. |
| Google options/resolver | Indexed relevant-target/rule selection; normalization/crosswalk | Reuse native CategoryOptions/Selector/Rule and validate_options, caps unchanged. No new mapper engine. |
| Existing category adapters | Capture platform-specific facts only; six routes | Preserve `_observe_categories`, scopes/support/unknown version; no taxonomy lookup in adapters. |
| Existing native mapper/binder/codec | Deterministic mapping+strict portable provenance binding | `_bind_categories`, map_categories, categorized_product_to/from_record reused unchanged. No invented observations. |
| Crosswalk index/source ledger | Directional official mapping lookup and exhaustive diagnostic source partition | Separate from merchant support/effective route conflict; no reverse inversion or hand-written per-device code. |
| Public Python/CLI/package | Thin explicit user access and resource provisioning | CLI uses existing envelopes/schema/capability discovery and same helpers as Python; package preserves Shopify. |

Dependency direction: source/contracts→catalog→resource/load and options/crosswalk;
native platform facts→resolver/options→existing native mapper/binder→portable;
public API/CLI/build preparation depend on these families, not vice versa.
No dependency on refrigerator-v1 or future aggregation/grouping module. Existing
Product/Variant/string attributes and export payloads remain compatibility owners.
Network source acquisition stays explicit coordinator/prepare setup, not catalog I/O.
