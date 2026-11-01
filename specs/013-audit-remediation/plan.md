# Audit remediation implementation plan

## Decision and scope
Verify and plan only, as requested2026-11-01. The audit's central conclusion holds
on current90d5bd1: reporting can claim success/completeness without usable products
or proved coverage, and monetary/field/downstream defects remain. See35 classified
findings in research.md and reproducible diagnostics in evidence/. No repairs have
been made; no current store performance or availability is claimed.

## Constitution check
Keep Product/Variant constructors, identity semantics and default feed formats.
Reuse captured source support and Normalizer conversion outcomes rather than
inventing observed facts. No paid dependency, inference, parallel agent run or
unbounded crawl. Existing unrelated edits and profile pilot status remain intact.
This umbrella is a roadmap; each child is independently designed and gated.

## Ordered delivery

| Priority | Reviewable change | Acceptance before implementation | Dependency / limit |
| --- | --- | --- | --- |
| 1a | Truthful empty/unknown/capped outcomes, consistent CLI/API/tool projection, Woo later-page404 | SC01/03: zero products fails; unknown coverage never claims catalog complete; later404 retains batch and incomplete reason | First actual repair; no broad runtime refactor prerequisite |
| 1b | Browser HTTP status and product-page evidence | SC02:404 HTML never product; policy OG rejected; genuine free product retained | Shares outcome contract; transport fixture first |
| 2a | Currency support and monetary parsing | SC04/05: supported PKR/US/EU cases correct; ambiguous inputs unresolved; missing currency never observed USD | Resolve legacy projection and locale-context decision first |
| 2b | Extraction/downstream roundtrip | SC11: bounded large extraction accepted via explicit contract or compact projection, with source/identity preserved | Profile byte composition; keep hard resource caps |
| 3a | Nested JSON-LD and real image selection, then breadcrumb/gallery/SKU | SC06: root/@graph equivalent; placeholder does not hide supported real image; bounded linked nodes | Split root/image from broader HTML additions if independently reviewable |
| 3b | Adapter field coverage, one adapter per child | SC07: Woo vendor/variants; budgeted Shopify enrichment; Magento existing category route and optional fields | No promised barcode where source absent;429 stays explicit |
| 4 | Quality/support/eligibility and export consistency | SC08: canonical vendor->brand, stable supported ID policy, validator/XML agreement | Pin official current rules before implementation; country/category conditions explicit |
| 5 | Similarity/duplicate honesty and unbiased statistics | SC09/10: incompatible variants not automatic identity; category once/product; stock unknown preserved | Can follow money independently of all adapter coverage |
| 6 | Decide readiness command scope | Separate destination eligibility, schema.org modeling and ACP protocol requirements | Deferred new feature; depends on trusted contracts, separately scoped |

AR10 runtime work in tasks.md is cross-cutting, not a single blocking first epic.
Before priority1, use only a small outer-process timeout and saved-fixture harness
to bound verification. Diagnose source-specific deadline/fetch/stdout/order/robots
issues as individual reviewed children alongside the relevant priority. Woo fetch
caps/partial retention must land before increasing live item counts; do not postpone
the empty-result or404 repairs until all resilience work is finished.

## Architecture and open decisions
1. Define one operation outcome and separate catalog-coverage evidence. Existing
   errors, catalog_complete and reasons must project consistently; discovery
   operation completion does not prove full catalog coverage. Outcome derivation
   belongs in shared extraction/reporting logic, not repeated CLI conditionals.
2. Reuse Normalizer accepted/reason/source_paths, capture and canonical identity.
   Legacy scalar defaults may remain for compatibility, while truthful projections
   must carry unsupported/unknown state. Missing currency representation and schema
   version are blocking child-design decisions. Literal "unknown" must not be
   exported as an ISO currency code; avoid silently changing default feed formats.
3. Product admission requires positive source-specific evidence and acceptable
   transport status, not a quality-score threshold or price>0 heuristic. JSON-LD,
   OG and browser CSS paths need their own admissibility controls.
4. Adapter budgets need remaining item/request/time state and a recoverable batch
   seam. Cooperative coroutine cancellation is insufficient proof against a blocked
   native/library call; outer process ownership and reaping require their own tests.
5. Centralize canonical field projection for feed/validation/analysis after source
   support is preserved. Stable feed IDs are not GTINs/MPNs; do not invent authority.
   Name presence, support and eligibility separately; keep matching candidate and
   confirmed identity contracts distinct.
6. Actual function signatures, ownership and shared component decisions belong in
   each child's skeleton.md/components.md after G1. They are deliberately not
   invented or treated as approved by this planning exercise.

## Required gates
Planning G1 reviews this spec, test design, research, tasks, plan and diagnostics.
It can pass planning while child product decisions remain explicitly open. Child
implementation requires resolved contracts, G1, executable intended-red acceptance
results, G2 skeleton, G3 components and an independent final review. No future
verdict is implied. Authors cannot review their own artifacts.

## Verification and handoff
Current evidence: one saved money/quality smoke followed by bounded synthetic
production-function diagnostics and selected hashed historical artifacts. These
are diagnostic reproductions, not a complete CLI regression suite or acceptance
pass. No live requests were needed for planning. Exact session counters unavailable.

Each child follows test-design.md: first smoke saved before expansion; deterministic
real-path fixtures/adversarial checks; scoped stress then affected regressions and
`python scripts/run_tests.py` with required240s-family/480s-total ceiling. Only then
one predeclared live smoke, max3 requests/5 products/30s, zero retries, before any
bounded expansion. Missing live transitions retain inconclusive status and require
reviewed synthetic mechanism evidence. Relevant edge cases include free products,
root versus graph products, explicit versus unsupported money/stock,429 after base
success, later-page404, timeout after progress, and byte/deadline boundaries.

Historical raw captures are in temporary storage; preserve minimal sanitized,
source-linked fixtures inside each child before repairs. The hash index is an
inventory, not a backup. No new tickets, branch, commit, push, PR or labels created.
