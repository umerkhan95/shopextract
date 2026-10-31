# Full Google category integration: verification design

Date: 2026-10-31. Author: `/root/google_verification_plan`. Planning only: no
runtime checks, resource acquisition, model calls or category sweep executed.
This amendment's requirements and tests must join spec/test-design before task
breakdown and independent G1; the earlier G1 does not approve this expanded scope.

## Completion denominators and evidence

The observed English upstream file has 5,595 category rows, including parents;
its reported header is2021-09-21. These observations are not a pinned-byte
receipt. Import must independently enumerate exact IDs and count all nodes,
roots and leaves from validated parent/path relations. Let that pinned set be G.
Completion requires `integrated_ids == lookup_ids == pipeline_pass_ids == G`,
zero unknown/duplicate/omitted IDs and100% target coverage, with exact set digests.
No fixed count can conceal a changed upstream version or missed final chunk.

Every target must pass real catalog lookup → bounded relevant options/rules →
source-shaped captured Google declaration → shared mapper → native product/category
binding → strict portable encode/decode → aggregate companion → public read.
Generate one minimal feed product per target, with label/ID and retained capture
through the actual feed/category adapter and normalizer. Use explicit controlled
transport/capture times and synthetic provenance; never fabricate live merchant
assignment evidence. The actual generic feed adapter retains source taxonomy version `None`; the sweep
uses explicit `allow_unknown_source_version=True`, asserts `None` stays in source
observations and verifies the pinned version/digest only in the TARGET projection.
A separate permission-denied case (`allow_unknown_source_version=False`) must not
map an unknown-version declaration. Synthetic provenance does not stamp a target
version into source facts.
Every ID also passes the proposed public batch lookup/resolve API and CLI in
bounded batches, and export/reload retains namespace/version/digest/category ID.
Do not merely compare a parser's own counter to its own expected output.

The full target sweep proves supported target integration, not successful
classification of every merchant product. Separate ledgers report Shopify source
IDs assessed/mapped/ambiguous/unmapped/unavailable against the pinned source set;
many-to-one mappings are valid, many-to-many mappings preserve ambiguity. Missing
official crosswalk entries do not become guessed exact mappings. Preserve source
metadata and incomplete outcomes; no global profile count or product coverage claim.

## Distinct adverse cases and reusable seams

| Case / risk | Required outcome and real mechanism |
| --- | --- |
| Small catalog structural smoke | Predesign2 roots/7 nodes/4 leaves; parser/validator derives exactly those counts. Duplicate ID/path, missing ancestor, cycle, malformed ID, invalid UTF-8 and digest mismatch reject. |
| Registry/rule boundaries | Existing `categories/config.py` and `CategoryLimits` accept admissible999/1000 and reject1001 targets/rules; byte/terms limits can reject earlier. Global G is never placed in one job or rule list. Native limits stay unchanged. |
| Literal labels and locales | Unicode, ampersands, escaped separators, duplicate labels in different paths, locale mismatch and ID-vs-full-path disagreement cannot produce a first/last-wins match. Exact ID/path indices are version/locale scoped. |
| Source support | Six actual adapter families with controlled source-shaped fixtures traverse capture→normalizer→category mapper→companion. Supported Google declarations map; absent/truncated/LLM-only/expired support remains unavailable, never taxonomy-derived product evidence. |
| Crosswalk lifecycle | Unknown source release, mismatched source/target digests, repeated/retired IDs, conflicting rows and one-to-many mappings retain explicit decisions/reasons. New catalog/crosswalk creates a revision; original historical result remains reproducible. |
| Update and publication faults | Real stage/validate/atomic publish/load rejects corrupt/interrupted update; previous catalog and reports remain loadable. Inject one write/rename fault, then retry; no partially valid catalog or dangling companion refs. |
| Packaging | Installed-wheel lookup and complete ID inventory work outside checkout with network denied and no YAML/runtime download. Where redistribution is permitted, wheel/sdist resource membership and offline sdist→wheel rebuild preserve exact resource bytes. Operator-supplied resource route has equivalently complete lookup tests; do not claim bundled data. |
| New aggregation defaults | Google is the common target in the new aggregation route; absent/ambiguous mapping does not reject product/offer/specification ingestion. Legacy Shopify API, Product.attributes strings, defaults, exports, jobs and source categories remain unchanged. |
| Projection and public limits | API/CLI agree for every target in batch receipts; empty input, unknown ID, stale cursor/catalog digest,1MiB−1/at/+1 wire sizes and cancellation have explicit outcomes, no truncation or leaked owned process. |

Existing reuse references: `categories/config.py`, `mapping.py`, `portable.py`,
`_codec.py`, `adapters/*`, `_cli_categories.py`, `_cli_discovery.py` and the
strict taxonomy pipeline/installed-package checks documented in spec008.
Remove one target from a temporary test-only lookup/index and prove the exact-set
assertion fails; restore with digest proof. Likewise test an ambiguity-veto fault
and publication fault. Independent reviewer verifies these are real mechanisms,
not fake mapper responses or tests of duplicate algorithms.

## Bounded full-catalog execution plan

Future verifier first saves the small structural smoke, then3 real target IDs
(root/intermediate/leaf), then one100-target measured batch. Freeze code/catalog/
runner/interpreter/config hashes, exact ordered G and expected outcomes before
the exhaustive run. Seed13031; one sequential driver, CPU-only, no inference or
network,512MiB process-group RSS cap. Proposed dedicated full-sweep ceiling180s,
per-batch15s, output/log ceiling1MiB each; count every CLI/process/pipeline stage.
Proceed only if measured total forecast plus25% reserve fits180s. Otherwise save
diagnosis and stop for a reviewed optimization/design amendment; no cap raising
or a claim that structural validation passed the missing runtime sweep.

Process canonical ID chunks of at most100: observed N5595 would mean55 full
chunks plus95 IDs. Each chunk gets an atomic receipt with attempted/passed exact
IDs, source/code hashes, stage outcomes, time/RSS and rolling set digest. Saved
progress must bind every input and policy; resume verifies the receipts and runs
only pending IDs under the original cumulative time/work budget. New code/pin
requires a new attempt identity; earlier receipts remain historical, not merged
into a false single-revision pass. Timeout/resource/failure stops before next
batch and cleans owned processes. Reuse representative decoder adversarial cases;
do not count every category as an independently tested decoder mechanism.

The existing36-case/12-stress aggregation checks retain their own180s design;
this additional exhaustive target pass is a separately reviewed gate. Required
`python scripts/run_tests.py` still has240s per family/480s shared ceilings.

## Source acquisition and merchant observations are separate gates

Official catalog acquisition: one frozen official URL, at most2 requests including
redirects,2MiB retained UTF-8,30s wall, zero retries; retain bytes/hash/header/source
terms disposition before parser execution. Official crosswalk acquisition, only
if a suitable primary artifact exists, gets a separate pinned manifest and at
most2 requests/2MiB/30s; absence is recorded, not replaced by an assumed crosswalk.
Neither acquisition shares or consumes the two-store product-sample budget.
The merchant sample keeps existing2 product URLs/2 origins,8 requests including
redirects,4 products/120s and independent category/identity/specification assertions.
Offline exhaustive target support and actual merchant classification are reported
separately. Docs-only planning is live N/A; required later live assertions remain
blocked if access or exact supported product facts are unavailable.
