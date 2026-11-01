# Audit remediation specification — planning only

2026-11-01. User requested verification and an implementation plan, not repairs.
Baseline: current checkout 90d5bd1, branch analysis-profile-coverage; supplied audit
claims origin/main 461ec38. Existing working edits and prior specs are out of scope.

## Outcomes and requirements
FR01: Catalog extraction must distinguish failed, partial, unknown coverage and
proved complete. Zero usable products must not report extraction success. A
successful empty discovery can mean no URLs found; it must not prove an empty
catalog. CLI/API/tool contracts must communicate the same underlying outcome.
FR02: Reject HTTP error documents and pages lacking product-specific evidence,
including policy pages with generic OpenGraph metadata. Preserve legitimate free
products; zero alone is not proof of invalidity.
FR03: Emit supported monetary facts only. Missing currency remains unsupported;
never silently promote USD compatibility defaults into observed facts. Parse
locale/separator evidence without guessing ambiguous monetary text. A string
"unknown" is not an ISO currency; choose its representation before implementation.
FR04: Preserve supported fields with source/variant linkage: real images, brand,
identifiers, Woo variants, nested Product JSON-LD, galleries, breadcrumbs and SKU.
Do not fabricate missing Shopify barcodes or assume optional Magento attributes
exist. Enrichment must respect request/deadline budgets.
FR05: Downstream reports must distinguish presence, factual support and destination
eligibility. Export/validation share canonical ID/brand semantics. No claim of
Google approval, ACP compliance or schema.org completeness from a single score.
FR06: Extraction respects item/request/deadline limits, retains useful partial
results where a supported contract allows, emits clean machine stdout, and has
stable output order. Downstream commands must consume bounded extraction output.
FR07: Matching and duplicate detection must distinguish identity, variant/size
conflicts and similarity candidates; unknown stock stays unknown and category
counts must have a stated per-product counting rule.
FR08: Every audit claim is classified as reproduced-current, code-supported,
historical-only, qualified, or unresolved, with locatable evidence and limits.

## Acceptance scenarios
SC01/FR01: zero usable products -> failed extraction; positive results without
coverage proof -> unknown/partial, never complete. Genuine terminal API page ->
complete only with evidence; bounded positive result -> partial. Discovery empty
and capped remain distinct. Replay through CLI/API/tool seams preserves meaning.
SC02/FR01,FR02: HTTP404 with plausible Product/OG/CSS content -> no accepted
product, while HTTP200 supported product survives. Policy OG page -> rejected;
free product with explicit Product/offer evidence -> retained with destination flag.
SC03/FR01,FR06: Woo page1=100, page2=404 -> retain100 and incomplete; normal short
terminal page -> supported termination; limit1 must stop fetching within designed
request budget, not download all pages. Timeout after one accepted batch retains
that batch if recoverable, otherwise reports failure without invented completion.
SC04/FR03: PKR explicit 3,720 ->3720; Rs. 3,720 ->3720 with supported PKR context;
US3,720.00 ->3720; DE3.720,00 ->3720 with DE context. Ambiguous3,720 absent
context -> explicit unresolved outcome. Missing/null/default currency never observed.
SC05/FR03,FR05: zero explicit offer remains observed as zero with eligibility
warning; missing/malformed/negative/nonfinite money cannot become valid zero.
SC06/FR04: top-level ItemPage.mainEntity Product and equivalent @graph Product
retain title/brand/GTIN/SKU once; @id links/cycles have bounded traversal. Placeholder
plus real lazy image -> supported real image; placeholder-only -> warning/unknown.
SC07/FR04: Woo brand and variant fixture preserves parent/variant identities and
prices; Shopify bulk absent barcode stays absent, enrichment429 retains base
product with reason; optional Magento field rejection does not erase core fields.
SC08/FR05: vendor projects to feed brand; absent external ID must not produce an
apparently eligible item without a documented stable identity policy. Invalid
image/price/currency and unsupported stock block or flag appropriate destination
rules. Requirements conditional on country/category/destination are explicit.
SC09/FR07: taupe/white, shampoo/conditioner and500ml/1L stay conflicting candidates,
not automatic identity merges; exact supported identifiers accept compatible pairs.
SC10/FR07: category_path[A,A] counts product once underA; missing/null stock is
unknown, explicit true/false remain distinct.
SC11/FR06: extraction output >1MiB can roundtrip via documented bounded input
contract or compact projection; no unlimited input allowance. JSON stdout remains
parseable, order stable, repeated provenance does not grow quadratically.
SC12/FR06: retry delay beyond remaining deadline stops in budget; cancellation
cleans owned browser/processes; robots-disallowed URLs excluded under declared
policy. Controlled blocked transport cannot hang past outer process deadline.
SC13/FR08: historical timing/count/precision claims keep their original sampling
limits and are not presented as freshly reproduced or universal guarantees.

## Boundaries and compatibility
Planning artifacts and bounded offline verification only. No production repairs,
network store sweeps, commits, pushes or pull requests. Preserve Product/Variant
constructors, identities and default feed formats per constitution. Behavioral
corrections require explicit compatibility notes rather than silent schema changes.
A new readiness command is deferred until outcome and field support foundations
are independently verified. Existing profile pilot gate remains unchanged.

## Workflow
Follow docs/development-workflow.md and templates. This umbrella plan orders
reviewable child slices; it does not grant blanket G2/G3 or implementation approval.
