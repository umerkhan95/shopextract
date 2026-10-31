# Planning source audit

Date: 2026-10-31 (Europe/Berlin). Read-only investigation; no runtime
verification or external changes. Local main HEAD:
`a900599fb17250d00f04b4e310381fdb5bb5a4d7` (merged PR97).

## Current code and draft work

- Main `src/shopextract/_models.py`: Product/Variant attributes are
  `dict[str, str]`. Product has Decimal price, default USD currency and
  supplier-scoped canonical identity. Rich specification transport must be
  additive and explicitly versioned; legacy defaults are not observed facts.
- `compare/identity_match.py`: pairwise classification and one-to-one catalog
  matching already retain conflicts/review states. It treats arbitrary unequal
  attributes as conflicts and asymmetric attributes as missing, even with an
  agreeing identifier. Therefore richer specs must not silently change matcher
  inputs. A new explicit identity projection needs reviewed behavior; missing
  descriptive facts alone must not imply a variant conflict. Known variant/pack
  conflicts remain vetoes. Multi-store grouping is not existing pair matching.
- `compare/catalog.py`: comparison ranks unique accepted exact pairs with the
  same currency. The explicit source-report path uses observed currency and
  records incomplete/failed sources. Reuse protections; do not rank default USD.
- `categories/adapters/generic.py` retains Google category declarations from
  feeds. `categories/mapping.py`, `contracts.py`, `portable.py`, `_codec.py` and
  existing evidence support are reuse candidates. Source observations, mappings
  and classification proposals must remain distinct.
- `docs/shopify-taxonomy.md`: pinned Shopify2026-08 includes 14,606 nodes in
  26 roots. This catalog remains; Google IDs are a separate namespace. Main has
  refrigerator category metadata, not the dedicated refrigerator profile.

Remote PR98 inspected at immutable head
`90d5bd1b7424872223483a2bfff4c811b50908ca`:
https://github.com/umerkhan95/shopextract/pull/98

Fetched changed-file inventory, status.md, pilot-contracts.md,
maintenance/profiles.py and maintenance/reporting.py through GitHub connector.
Draft/open and not merged when inspected. Its reported offline checks passed;
required live integration remains blocked. These are recorded prior outcomes,
not checks rerun in this planning task.

| PR98 element | Proposed disposition for later implementation |
| --- | --- |
| Pinned 4,125-node inventory/evidence | Preserve as historical scoped research; not Google coverage or a profile backlog commitment. |
| refrigerator-v1 and exact Shopify binding | Defer from aggregation critical path; do not merge whole PR to obtain helpers. |
| Exact decimal quantity operations and semantic guards | Evaluate/extract behind generic spec normalization after new red tests; do not assume every physical quantity shares meaning. |
| include_refrigerator_attributes flag threaded through engine/runtime/sources/domain/normalizer and cache identity | Replace proposed dependency with category-independent, explicit capability in a future reviewed slice; no runtime mutation now. |
| Product/Variant QuantityValue annotation union, portable validator/schema widening | Do not silently adopt on main; prefer separately versioned opt-in aggregation/specification projection while preserving existing strings. |
| page_coverage over maintenance finding pages | Reuse ideas only; configured maintenance fields are not aggregated-product completeness. Define denominators over actually observed records/fields. |
| Persisted selected profile/unit/category policy definitions | Preserve historical job semantics; aggregation must not reinterpret existing jobs or require a migration merely to read them. |

No PR closed, merged, rewritten, or superseded externally by this planning task.
Implementation must repeat the disposition audit against actual current heads.

## Official external facts

Read through web tool on2026-10-31:

1. https://www.google.com/basepages/producttype/taxonomy-with-ids.en-US.txt
   returned header `Google_Product_Taxonomy_Version: 2021-09-21` and5,595
   category rows (all levels, excluding one header). This is an observed
   publication, not an assertion Google's internal system is frozen at that date.
   No pinned-byte artifact/hash or redistribution permission was established here.
2. https://support.google.com/merchants/answer/6324436?hl=en
   describes public categorization and accepts a category ID or complete path.
   Public taxonomy is usable as the proposed common classification reference;
   no assumption about Google's internal matching depth or a one-to-one Shopify
   crosswalk follows. Runtime source may be unknown or ambiguous.
3. https://support.google.com/merchants/answer/7052112?hl=en
   distinguishes products and variants and documents identifiers, offers and
   product details. It is a reference for interchange, not permission to claim
   ShopExtract exceeds Google's production coverage or quality.

Do not infer MIT licensing for Google data from the repository or Shopify's MIT
license. The acquisition/redistribution decision must be explicit before a Google
catalog is bundled or fetched by implementation. Keep unknown terms a recorded
blocker for affected distribution only; unrelated offline contract work can proceed.

## Scope and verification limits

Current task authorizes planning files only. No product crawl, model call,
installation, implementation, PR update, publication or destructive cleanup.
No runtime tests required for these planning-only changes; future executable
slices require intended-red tests, independent gates and the configured driver.
Actual incremental session token counters are unavailable; no quota estimate.

## Expanded full-Google scope: pinned official crosswalk discovery

User subsequently explicitly requested a complete implementation plan integrating
ALL Google categories and authorized multiple parallel planning agents. The
earlier G1 and lookup-only interpretation do not approve this amended scope.

Coordinator used the GitHub connector for two exact primary-source documents and
one directory metadata read (no mapping corpus fetched):

- [Pinned Shopify README](https://github.com/Shopify/product-taxonomy/blob/2e9aa2e9b882383952c63d212add13eb80f46cf9/README.md)
  identifies versioned compressed release assets including
  `integrations.all_mappings.en.json.gz`. Committed `dist/` is deprecated with
  removal scheduled2026-10-31, so use immutable source or release artifacts.
- [Pinned integrations README](https://github.com/Shopify/product-taxonomy/blob/2e9aa2e9b882383952c63d212add13eb80f46cf9/data/integrations/README.md)
  lists Google2021-09-21 and directional mapping rules. It explicitly says
  source `unmapped_product_category_ids` are omitted from generated mapping
  distributions; absence of a generated row cannot prove intentional exclusion.
- [Actual pinned directory metadata](https://api.github.com/repos/Shopify/product-taxonomy/contents/data/integrations/google/2021-09-21/mappings?ref=2e9aa2e9b882383952c63d212add13eb80f46cf9)
  contains ONLY `from_shopify.yml`, size1,355,910bytes and Git blob
  `2a57f754fd66a6c09010fac5ca1b93d45be5f629`. No reverse file was listed.
  The blob identifier is not a retained-byte SHA256. Rows, exclusions, complete
  coverage counts and license applicability have not yet been inspected.

The actual source inventory makes official Shopify→Google crosswalk ingestion a
concrete required implementation task. No automatic reverse inversion, label
guessing, implied universal mapping or new per-category formats follow. All
Google target IDs must work; source-mapping outcomes retain their own denominators.
