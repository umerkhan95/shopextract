# Google taxonomy integration

For the configured Pakistani-site workflow and repository Codex skill, see
[Codex Google mapping verification](codex-google-mapping.md).

ShopExtract's Google taxonomy family provides full catalog lookup and category
mapping through the existing category adapters, mapper, evidence binding and
portable codec. It does not require category-specific product formats or
maintenance profiles. Product/Variant constructors, string attributes, Shopify
taxonomy and existing extraction/export defaults stay compatible.

The selected resource route is **operator-provisioned**: no Google category corpus
is bundled or downloaded on import, installation, help or lookup. Supply a full
Google-format TXT resource with its version header, then prepare it explicitly:

```sh
shopextract taxonomy google --catalog-root ./catalogs prepare \
  --source ./taxonomy-with-ids.en-US.txt --expected-sha256 SHA256
shopextract taxonomy google --catalog-root ./catalogs info
shopextract taxonomy google --catalog-root ./catalogs lookup 328
shopextract taxonomy google --catalog-root ./catalogs resolve-path \
  'Electronics > Computers > Laptops'
shopextract taxonomy google --catalog-root ./catalogs list --limit 100
```

Replace SHA256 with the actual trusted file digest. Catalog identity includes
version, locale and content fingerprint. Multiple catalogs with the same version
require explicit `--fingerprint`. List cursors bind that identity and page size.
Preparing a new source adds an immutable catalog directory; it does not rewrite
historical resources. Corrupt, ambiguous or mismatched resources fail explicitly.

For the pinned Shopify-maintained Google snapshot, prepare directly from its
original YAML rather than manually converting it. Obtain the
[pinned full_names.yml](https://github.com/Shopify/product-taxonomy/blob/2e9aa2e9b882383952c63d212add13eb80f46cf9/data/integrations/google/2021-09-21/full_names.yml)
and retain its provenance:

```sh
shopextract taxonomy google --catalog-root ./catalogs prepare-snapshot \
  --source ./full_names.yml \
  --source-commit 2e9aa2e9b882383952c63d212add13eb80f46cf9 \
  --source-url https://raw.githubusercontent.com/Shopify/product-taxonomy/2e9aa2e9b882383952c63d212add13eb80f46cf9/data/integrations/google/2021-09-21/full_names.yml \
  --expected-sha256 4b6fcdaf79f501a4f5cef9d35b95749b021c0cff48baeb3fd8be6733d1e9bee6
```

This explicit source operation requires the `taxonomy-build` extra. The same
strict source decoder serves snapshot and crosswalk preparation; normal lookup
does not parse YAML. Source kind, original YAML hash, commit and derived TXT hash
stay in the resulting manifest. Provenance records operator-supplied source
identity; it is not a signature or independently verified source authority.

## Mapping captured source products

```python
from shopextract import load_google_taxonomy, normalize_with_google_taxonomy, Platform
from shopextract.taxonomies.google import effective_google_category

taxonomy = load_google_taxonomy(catalog_root="./catalogs")
# raw is an actual extractor record with retained source capture.
categorized = normalize_with_google_taxonomy(
    raw, platform=Platform.GENERIC, shop_url="https://your-store.example",
    taxonomy=taxonomy, allow_unknown_source_version=True,
)
classification = effective_google_category(categorized, taxonomy=taxonomy)
```

Google feed declarations retain their observed source version as unknown. The
explicit permission allows exact ID/path resolution against the selected target
catalog; it does not invent a source version. Plain uncaptured dictionaries do
not acquire observed evidence. Unknown, unsupported, conflicting or partial
categories retain the product and expose their actual mapping state. A catalog
category never supplies missing product specifications or proves product identity.

```sh
shopextract taxonomy google --catalog-root ./catalogs normalize raw.json \
  --shop-url https://your-store.example --allow-unknown-source-version > categorized.json
shopextract export categorized.json --format csv --output products.csv \
  --categories-output products.categories.json
```

`normalize --platform` supports the six existing platform families. `--mapping`
accepts an array of native declarative MappingRule records for trusted, scoped
merchant mappings. Numeric merchant IDs and similar labels are not Google IDs.
Source categories and mapping decisions remain separate in native categorized
records. Existing export requires the category companion and verifies its binding.

## Directional Shopify crosswalk

An explicit hash-pinned official forward source can map supported Shopify
standard category assignments to Google targets. It does not infer standard
assignments from Shopify product_type/collections, and cannot be reversed safely.

```sh
shopextract taxonomy google --catalog-root ./catalogs crosswalk audit \
  --source ./from_shopify.yml --expected-sha256 SHA256 \
  --shopify-catalog-root ./shopify-catalogs --limit 100
```

Use `normalize --crosswalk FILE --crosswalk-sha256 SHA256` and optional
`--shopify-catalog-root` to select that same validated index. Explicit YAML source
reading needs `pip install 'shopextract[taxonomy-build]'`; ordinary prepared Google
catalog lookup uses only the standard library. No dependency is installed by CLI.

The source ledger uses separate statuses for single/multiple target mappings,
upstream exclusions and missing rules. Invalid references, contradictory
exclusions or incompatible versions reject activation; invalid diagnostics never
become an active partial crosswalk. Source and target fingerprints are bound.
The full catalog lives outside jobs. Relevant options retain native limits of
1,000 targets/rules, 100 terms and 256 KiB configuration/companion bytes; lower
limits may reject earlier. Catalog enumeration uses bounded pages.

## Source and coverage

The development resource is the pinned Shopify-maintained Google 2021-09-21
snapshot at Shopify commit `2e9aa2e9b882383952c63d212add13eb80f46cf9`.
Its resource manifest explicitly records original YAML and derived TXT hashes.
Direct download from Google's endpoint was blocked by the development network;
this is not a claim that its original bytes were verified directly.

The source contains 5,595 category nodes, 21 roots and 4,719 leaves. The forward
source has 14,528 mapping rules and 78 explicit Shopify exclusions. These source
counts are distinct from actual product classification coverage. In particular,
Google targets without an inbound Shopify rule remain valid direct targets.
Full source corpus and generated resources remain outside Git.

Design, independent reviews and actual execution evidence live in
[the integration feature](../specs/013-aggregation-first/implementation/).
Aggregation of product groups/offers and richer specification comparison remain
separate consumers of these reusable taxonomy components.
