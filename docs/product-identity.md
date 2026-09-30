# Product identity and matching

Epic #21 is split into #30 (identity/migration), #31 (matching reports), and #32
(evaluation/example). This implementation is an evidence-backed reporting MVP.
All code is MIT, runs locally, and requires no paid service or semantic model.

## Public API

```python
from shopextract import Product, assign_identity, classify_match, match_products

p = assign_identity(Product(external_id="42", sku="LOCAL-42"), "https://shop.example")
print(p.canonical_product_id, p.supplier_id)

report = match_products(catalog_a, catalog_b, threshold=0.8)
for decision in report:
    print(decision.index_a, decision.index_b, decision.relation,
          decision.evidence, decision.conflicts, decision.needs_review)
```

`assign_identity(product, supplier_id="")` mutates and returns a `Product`.
`normalize(raw, platform, shop_url)` also assigns identity when a supplier scope
is available. The additive fields are `Product.canonical_product_id`,
`Product.supplier_id`, `Product.attributes`, `Product.pack_quantity`,
`Product.bundle_components`, and `Variant.canonical_variant_id`,
`Variant.attributes`, `Variant.gtin`. Existing source fields `external_id` and
`variant_id` remain intact. Product IDs identify supplier records, not a universal
manufacturer master catalog. Exact cross-supplier equivalence is reported without
merging or rewriting their IDs.

Stateless IDs use a versioned-by-prefix UUID namespace (`p_` or `v_`) derived from
supplier plus platform/source ID, then supplier SKU, then a product URL. Variant
IDs use the parent product ID as scope. URL identities keep variant query
parameters and drop fragments and common tracking parameters. Root shop URLs
are not product identifiers. With no anchor, IDs are randomly allocated; retain
that ID or use monitoring's persistent registry for subsequent observations.
Titles, prices and descriptions never contribute to anchored identity.
URL suppliers normalize to a lower-case host (including port); explicit keys
are case sensitive except dotted host keys. `www` aliases are not collapsed.
Use a consistent supplier key; changing it changes the identity namespace.

`classify_match(a, b, threshold=0.8)` accepts `Product` objects or dictionaries
and returns `MatchDecision`. `match_products(list_a, list_b, threshold=0.8,
semantic_candidates=None)` reports indexed decisions, including unmatched
sources and targets. `normalized_attributes(product)` exposes the attribute
normalization used by matching. Reports can be serialized with
`dataclasses.asdict`; the relationship enum is a string enum.

Matching starts with checksum-valid GTIN (8/12/13/14 digits, normalized to 14),
brand plus MPN, or supplier-scoped canonical/source IDs and SKUs. Conflicts take
precedence over identifier agreement. Attribute keys and values normalize
Unicode, case and whitespace; `colour` and `ram` alias `color` and `memory`.
Explicit memory/storage/capacity values normalize spaces; conservative title
cues recognize quantities with GB/TB/MB/ml/kg/liter units and pack/set quantities.
Missing attributes produce review decisions. Missing pack size means unknown.
Variant option sets on parent records also participate in conflict checks.

Relationships are `exact`, `variant`, `bundle`, `substitute`, `uncertain`, and
`unmatched`. Capacity/color/size differences suggest variants. Pack or bundle
composition differences suggest bundles. Same-category alternatives with explicit shared purpose or compatibility
attributes suggest substitutes; category alone does not. These suggestions require review and are not equivalence claims.
A title similarity score only generates a review candidate. Identifier conflicts,
missing discriminating attributes, and multiple exact candidates require review.
`confidence` is a rule score, not a calibrated probability. Every decision
includes the evidence and conflicts used by the rules.

An optional semantic callback receives a source dictionary and all target
dictionaries and returns target indices. It runs only when no rule candidate is
available. Semantic similarity alone cannot authorize exact equivalence.
No built-in model, embeddings or network provider is configured. Pair scans are
quadratic and intended for the existing bounded catalog sizes.

## Comparison compatibility

`compare_catalogs(..., threshold=0.8, semantic_candidates=None)` keeps its
existing result fields and adds `CatalogDiff.match_report`. Only unique exact
pairs enter `in_both` and its price lists. Price lists require equal currencies;
no exchange-rate conversion is performed. `only_in_a/b` now mean records lacking
an accepted exact pair, including records awaiting review. Title-only catalogs
will therefore produce fewer accepted price comparisons. Review decisions in
`match_report` before interpreting these as confirmed assortment differences.

`fuzzy_match` and `match_gtin` retain their return shapes as legacy lookup helpers.
`fuzzy_match` rejects observed attribute/identifier conflicts but its tuples are
still candidates. `match_gtin` retains its old unvalidated GTIN/EAN/UPC/SKU lookup
semantics and does not scope SKUs. Use `match_products` for equivalence decisions.
`compare(query, stores)` remains a title search, excludes observed capacity/pack
conflicts, and does not certify exact identity or currency comparability.

## Snapshot migration and history

Snapshot writes, `changes`, and `price_history` migrate legacy snapshot JSON in
chronological order. New `identity_aliases` rows persist supplier/source/SKU/URL
aliases. Existing snapshot timestamps and prices remain intact. Each operation
uses a transaction; conflicts stop the operation instead of guessing or silently
collapsing duplicate records. Read APIs now require a writable SQLite database
for migration and alias registration. Back up the database before upgrading; changes are additive,
but older versions still use title-based change detection.

For explicit migration:

```python
import sqlite3
from shopextract import migrate_snapshot_identities

with sqlite3.connect("snapshots.db") as conn:
    updated = migrate_snapshot_identities(conn)  # optional domain="shop.example"
```

The caller owns commit/rollback. Migration is idempotent. A unique unchanged
legacy title can bridge an identifier-free record to a later identified record;
that title bridge is consumed on promotion to avoid linking later title reuse.
Duplicate display titles remain separate; duplicate identities and conflicting
aliases raise `ValueError` for manual reconciliation. A title-only rename cannot
be reconstructed without an anchor. Recycled source IDs/SKUs, product URL reuse,
and coincidentally identical legacy titles can conflate unrelated records;
review these histories manually. This MVP does not offer a merge/split review UI.

`price_history(domain, product_title="", db_path=..., canonical_product_id=None)`
resolves any historical title to its identity and includes prices from all its
renames. If a title belongs to multiple identities it raises `ValueError`; use
`canonical_product_id` explicitly. `changes` compares canonical IDs, so a rename
with a stable source/SKU/URL does not emit spurious removal/addition events.
Existing change types and title fields are preserved. Alerts registered by title
still follow that display title; monitoring variant prices separately is outside
this epic's identity foundation.

## Evaluation and acceptance

`evaluate_matching(dataset, threshold=0.8, publisher_aliases=None)` is exported by `shopextract`. Each
row has `id`, `a`, `b`, and a human-assigned `label` relationship. The checked-in
`tests/fixtures/matching_evaluation.json` is a 32-pair synthetic labeled regression
set, including 8GB/16GB variants, single/multipack conflicts, reused local SKUs,
invalid GTIN checksums, missing attributes, and exact identifier/title renames.
Two known-exact pairs intentionally lack enough observed evidence to automate.

Acceptance on this fixture: **exact precision 100%, exact coverage at least
80%, and zero false exact matches**. Precision is correct accepted exact pairs
/ all accepted exact pairs. Coverage (exact recall) is correct accepted exact
pairs / labeled exact pairs. Empty denominators report zero; abstaining on all
pairs cannot pass. Also report relation accuracy, review rate, and per-pair
predictions/evidence. `pytest` checks the thresholds and additional catalog
ambiguity scenarios. Fixture results are regression evidence, not production
accuracy estimates. Evaluate representative supplier data before deployment.

Run the full offline example, including normalized extraction results through
real snapshot storage, renamed price history, exact/variant reports, and metrics:

```sh
PYTHONPATH=src python examples/identity_matching.py
PYTHONPATH=src pytest
```

The example substitutes extraction results so it is repeatable without internet
or a supplier account. Existing mocked extraction, export, comparison, and
monitoring tests verify compatibility. No catalog mutation, autonomous action,
MCP wrapper, or other roadmap workstream is introduced.

## Live validation follow-up (30 September 2026)

The original 32-pair synthetic dataset's 80% exact coverage was **not** a live
accuracy estimate. The selected four corresponding Catan pairs initially had
0/4 exact acceptance. Real source data revealed stock, currency, missing
identifiers and extraction-budget gaps. The fixes and explicit policies below
are covered by `tests/test_live_regressions.py` with compact captured source
fields in `tests/fixtures/live_catan_pairs.json`.

Shopify explicit variant `available` takes precedence over inventory quantity
and the previous optimistic fallback. Product-level `available`, when supplied,
is also respected. Missing availability/inventory still defaults to the legacy
boolean `True`; this model cannot represent unknown stock. Currency for the
first variant price comes from observed `price_currency`, then product currency,
then observed shop cookie currency, then the legacy USD default. Localized EUR
responses remain EUR; the pipeline does not convert CAD to EUR or claim that
separate requests use the same market context.

Public `extract(..., max_urls=N)` bounds Shopify products and pagination;
other API results are truncated to N retained records. Crawl paths still bound
URLs, which may return multiple products. This is not a universal HTTP-request
budget. `ShopifyExtractor.extract(..., max_products=N)` uses a constant page
size and stops when N records have been retained, even if a server ignores its
page limit. A bounded result is not a complete merchant catalog.

`extract` and `compare_catalogs` add two options (both default to `False`):

- `enrich_identifiers=True`: fetch at most one `.js` detail per retained Shopify
  product with missing variant barcodes. Product and variant IDs must agree.
  Only missing barcodes are copied; detail prices, currency and stock do not
  overwrite catalog observations from a potentially different market context.
  `raw_data._identifier_sources` records URL, variant ID and copied value.
  Failures preserve products and surface in extraction errors; missing evidence
  continues to require review.
- `restore_short_gtin=True`: for Shopify source barcodes of exactly 11 digits,
  restore a single leading zero only if the resulting UPC passes its check digit.
  Original source values remain unchanged; `raw_data._identifier_normalization`
  records the applied policy. Other shortened lengths and bad checksums are not
  repaired. A valid checksum alone does not prove a barcode is assigned to a
  product; enable this only for suppliers whose zero-dropping behavior has been
  independently checked.

`normalize(..., restore_short_gtin=True)` exposes the same explicit policy for
captured direct records. `classify_match`, `match_products`, and `compare_catalogs`
and `evaluate_matching` also accept `publisher_aliases`, mapping **specific validated GTINs** to a list
of approved publisher names. Alias approval can resolve a brand discrepancy
only when both records already have the same validated GTIN and both names
appear in that GTIN's list. It cannot authorize global SKU equivalence, bypass
capacity/pack conflicts, or authorize unrelated publisher products. Reports
include the explicit approval and identifier provenance when available.

```python
aliases = {
    "029877030712": ["Mayfair Games", "Catan Studio"],  # reviewed Catan fifth edition
}
report = match_products(catalog_a, catalog_b, publisher_aliases=aliases)
```

Fresh selected live checks accepted 4/4 corresponding pairs with checksum
restoration and explicitly reviewed GTIN-scoped aliases, with no off-diagonal
accepted pairs in the 4-by-4 catalog. Restoration without publisher approval
accepted 1/4 and left the three publisher conflicts for review. Bounded public
collection/demo reads returned 5/3 products, observed CAD on direct selected
records, and preserved explicit out-of-stock flags. Public same-source catalog
comparison accepted 5/5, independent snapshots preserved IDs with no false
changes, and controlled rename/+1 price replay retained history. This small
selected sample still does not establish production matching precision or coverage.

Run fresh bounded checks (live source data may change):

```sh
PYTHONPATH=src python examples/live_identity_check.py --output-dir artifacts/live-identity
```

The example keeps a fixed four-GTIN approval list from the manually reviewed
sample and saves source observations, policy decisions and budget/stock checks.
It performs public reads only, with no paid model, login or catalog changes.
