# Full Shopify taxonomy

Published ShopExtract wheels and source distributions include the pinned English Shopify 2026-08 catalog: **14,606 categories, 8,240 base attributes, all 316 attribute extensions and 74,820 values**. Normal lookup works offline immediately after installation. It makes no taxonomy request and does not require PyYAML. The upstream MIT notice is included with the generated resource.

```python
from shopextract.taxonomies.shopify import load_shopify_taxonomy

# Load once at application startup; reuse this immutable object across products.
taxonomy = load_shopify_taxonomy()
laptop = taxonomy.category('el-6-6')
assert laptop == taxonomy.category('gid://shopify/TaxonomyCategory/el-6-6')
attributes = taxonomy.attributes_for(laptop.id)
values = taxonomy.values_for('memory-technology')
parents = taxonomy.ancestors(laptop.id)  # root to immediate parent
```

`iter_categories()`, `iter_attributes(include_extensions=True)` and `iter_values()` expose the complete catalog. Singular category/attribute/value lookup returns `None` for unknown nonempty IDs; empty/ambiguous aliases raise `TaxonomyLookupError`, and wrong argument types raise `TypeError`. Category IDs accept exact GIDs or their short suffixes; attribute aliases include actual GIDs, handles, friendly IDs and numeric suffixes. Extensions have handles/friendly IDs and a `values_from` relation to a canonical base attribute; they do not have invented GIDs. `attributes_for` preserves each category's declared context, extension labels and allowed values. It does not union attributes from ancestors or grant permission to correct a product.

## Normalize, map and read a product's schema

```python
from shopextract import Platform
from shopextract.taxonomies.shopify import normalize_with_shopify_taxonomy

# raw is captured by an actual source extractor. Ordinary dicts alone cannot
# acquire observed support just because their category text matches the catalog.
value = normalize_with_shopify_taxonomy(
    raw, platform=Platform.SHOPIFY, shop_url='https://merchant.example',
    taxonomy=taxonomy, allow_unknown_source_version=True,
)
if value is not None:
    schema = taxonomy.schema_for(value)
    for resolved in schema.resolved:
        print(resolved.category.name, resolved.attributes)
```

The helper derives a small relevant registry and exact-ID rules, then uses the existing category mapper, evidence binder and strict companion codec. `schema_for` validates that bound companion before returning metadata. It rejects changed bindings, another catalog identity and unknown mapped targets. Ambiguous/unmapped/unavailable decisions remain in `schema.unresolved`.

Shopify Storefront category GIDs do not declare a taxonomy release. Therefore automatic identity mapping requires the explicit `allow_unknown_source_version=True` choice above; the source version still remains unknown. The pinned catalog release/fingerprint describes the mapping target. Custom merchant labels require explicit trusted `MappingRule`s; labels never guess a standard category.

`shopify_taxonomy_options(scope, category_ids=[...], taxonomy=taxonomy, ...)` creates finite options for existing tool/maintenance jobs. Keep the original limits: 100 source terms, 1,000 targets/rules and 256 KiB configuration/companion envelopes. The full catalog is never put into a job, companion or model prompt. Target `registry.version` combines release and SHA256 fingerprint using existing codec fields. Existing category correction/identity/variant safeguards still apply; full metadata is not a correction-rule factory.

## Optional Storefront category acquisition

```python
from shopextract.extractors.shopify_taxonomy import ShopifyStorefrontConfig
from shopextract.taxonomies.shopify import extract_with_shopify_taxonomy

storefront = ShopifyStorefrontConfig(
    endpoint='https://merchant.example/api/2026-10/graphql.json',
    auth_mode='tokenless',  # explicit; default token mode requires a supplied token
)
result = await extract_with_shopify_taxonomy(
    'https://merchant.example', taxonomy=taxonomy, storefront=storefront,
    max_products=2, allow_unknown_source_version=True,
)
```

Without `storefront`, extraction uses the ordinary rich public product source and does not make an implicit Storefront request. With it, one fixed category-only query supplements each captured product after checking its actual Product GID and handle. Prices, variants and independent public type/collection facts remain intact. Null/denied/error-affected categories remain unavailable; there is no credential fallback, browser or model fallback. Token mode accepts a runtime `access_token` (excluded from repr); explicit tokenless mode requires `None` and rejects inherited client credentials. Credentials never enter jobs, policy codecs or companions.

The same producer is used by `ToolRuntime(..., category_config=..., shopify_storefront=storefront)` and `MaintenanceEngine(..., category_config=..., shopify_storefront=storefront)`. Existing origin authorization/request/byte budgets and the exact POST/query/variable gate apply. Every source-cache read and write is bypassed for Storefront-enabled acquisition. A committed job replay is historical evidence, not a claim about present token access; it does not populate the source cache.

## Source checkout and release preparation

Full source/generated catalog bytes are ignored under `downloads/` and `build/`; they are not committed to Git. The repository tracks importer code, small pinned hash/identity metadata, the MIT notice and small fixtures. A cold Git checkout has no installed data: default loading/building fails clearly until explicit preparation. Published wheels and sdists already contain the generated resource, so ordinary installation does not fetch a taxonomy or run an installation download hook.

Explicit preparation needs the `taxonomy-build` extra's PyYAML dependency and normal package runtime dependencies. A release builder can install these tooling dependencies first, then use the checkout with `PYTHONPATH=src:.`:

```sh
# Offline source override directory contains taxonomy.en.json.gz, attributes.yml,
# and LICENSE, each matching the tracked pinned hashes.
PYTHONPATH=src:. python -m shopextract.taxonomies.shopify.prepare \
  --source-cache /path/to/verified-sources

# Alternatively explicitly authorize the pinned official download, with fixed
# HTTPS sources, hash checks, <=8 requests and a 60-second acquisition limit:
PYTHONPATH=src:. python -m shopextract.taxonomies.shopify.prepare --allow-download

# A declared Hatch backend verifies prepared bytes and embeds the same complete
# resource in BOTH wheel and sdist. It performs no network/import normalization.
python -m hatchling build
```

The installed package and a wheel rebuilt from the published sdist need no taxonomy networking or YAML. Publication verifies the complete staged manifest, logical identity and copied temporary resource before atomic directory publication. Updates are explicit pinned builds, not floating automatic refreshes; existing catalog objects and saved job policies retain their identity.

## Measured limits and coverage

On the saved CPU-only run, static type-schema reuse reduced 100 real normalize-plus-strict-schema calls from 6.05 s to 2.89 s (about 2.09×); recursive validation remains enabled. Cold loading was about 3.58 s and resident memory about 434–438 MB. Reusing one loaded catalog avoids repeated cold initialization. A warm lookup batch of 3,000 queries took about 1.63 ms; explicit repeated loads still verify resource bytes (~9.47 ms each). These are local measurements, not network latency or universal response guarantees.

The exhaustive controlled sweep passed all 14,606 actual catalog IDs and all 93,007 contextual bindings through capture, normalization, mapping, binding and strict schema projection in 395.459 s, with sampled peak group RSS 433,688,576 bytes. Representative Unicode/context and adversarial decoding checks are reported separately; there are not 14,606 independent decoder mechanisms. Complete official-source validation and actual merchant observations are distinct. A bounded merchant probe can establish only the product assignments it actually observes, never assignments for every taxonomy category. See `specs/008-shopify-taxonomy/verification.md` for exact results and limitations.

The bounded merchant probe also observed one actual assignment: BoardGameBliss returned `gid://shopify/TaxonomyCategory/tg-2-5` (Board Games) through the tokenless 2026-10 producer, then the shared mapper/schema resolved it. The combined ledger contains one GET200 and one POST200, with no retries. The Product ID/handle join used retained public evidence acquired on October 16; the independent native category observation was acquired on October 18. This establishes one observed assignment, not merchant coverage of the full catalog. Cookie-bearing public pages use an independent stateless metadata client with the same guarded transport/accounting; public and metadata cookie state never provide category-query authority.

A dependency-free storage experiment retained the current dictionary backend. With equal canonical JSON schema materialization for 128 actual IDs, unique reads took 17.32 ms with dictionaries versus 37.87 ms with a read-only SQLite prototype. Prototype resident memory was 91.1 MiB versus 415.5 MiB, but its startup used a weaker file-hash-only integrity check and a 106 MB database (current packaged gzip: 2.49 MB). These prototype numbers do not justify replacing the verified production loader; reuse one catalog for warm responses. Exact timings, preparation costs and integrity differences are saved under `artifacts/shopify-taxonomy/index-benchmark/`.

Cold checkout CI/release preparation uses `python scripts/bootstrap_taxonomy.py --allow-download` after installing the declared Hatch build tooling. This standalone entry reads build requirements from project metadata and calls the same importer under a build-only namespace, without importing the application. Use `--offline --source-cache PATH` with already installed build dependencies for verified local sources. Both workflows share this step before editable installation/package build. Direct source-tree lookup uses `catalog_root=Path('build/shopify-taxonomy/catalogs')`; installed default lookup reads the embedded artifact.
