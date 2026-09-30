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
composition differences suggest bundles. Same-category alternatives suggest
substitutes. These suggestions require review and are not equivalence claims.
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

`evaluate_matching(dataset, threshold=0.8)` is exported by `shopextract`. Each
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
