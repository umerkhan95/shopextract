# Category analysis profile coverage expansion

Planning date: 2026-10-25. Author: primary agent. Originally planning; subsequent user instruction authorizes implementation. Based on local spec/test templates. This is a phased roadmap; each implementation slice must pass its own workflow gates.

## Outcomes and requirements

FR01 Produce a reproducible coverage inventory before committing to a market-wide profile count. Rows identify pinned taxonomy/category ID, family, profile/version (or absent), declared attributes, reviewed field roles/units, source extraction availability, binding status and evidence. Keep catalog metadata, extraction capability, implemented rules, executed checks and actual live observation separate. Denominators explicitly name source files/version and selection; no universal coverage claim from three saved taxonomy branches. Separate new profiles, existing-profile extensions, binding-only work and unsupported families. Report unique reviewed policy families, not leaf category or platform counts.

FR02 Start with the three saved reference categories: Laptops el-6-6, Boots aa-8-3, Refrigerators hg-11-7-41, pinned Shopify 2026-08. Record current hardware/footwear profiles as partial policies, generic as common-fields-only, refrigerator as missing. Expand the inventory over saved electronics/apparel/home-garden branches offline, with explicit exclusions and review-pending groups; do not invent final family totals. Other market branches remain unassessed. Exact backlog counts require semantic review of every counted group.

FR03 First implementation pilot proposes one new refrigerator-v1 policy for attributes/capacity (explicit total volume), attributes/width, attributes/height, attributes/depth, attributes/model plus common fields. Capacity and dimensions are identity_variant-sensitive; model exact identity_variant. Dimensions require an explicit common convention (product dimensions, not packaging); total vs usable/freezer-only capacity is not interchangeable. This is a selected-field pilot, not complete appliance coverage. Preserve hardware-v1, footwear-v1, generic-v1 meanings and historical jobs byte-for-byte. New policy capabilities are versioned without silently changing persisted definitions; schema/API/custom-profile/CLI compatibility must be resolved before code.

FR04 Compare supported units deterministically: volume ml/L to L and length mm/cm/m to m, using exact decimal arithmetic and retained input/unit/transform trace. Equal quantities compare equal, distinct quantities remain different. Require finite nonnegative values for capacity/dimensions; zero is a valid numeric input, never missing by truthiness. Reject bool, NaN/infinity, negative, ranges, unitless quantities, unknown/localized units and incompatible dimensions as unknown with an explicit reason; do not infer tolerances. Missing/null/empty remain unavailable and retain their distinct input state. No GB/GiB, size-system or free-text conversions added in the pilot.

FR05 Trace every analyzed attribute through real source capture, normalization, Product.attributes, support evidence, persistence and maintenance comparison. A category definition is not product evidence. Reuse existing supported attribute mechanisms; add a bounded extraction seam only if the audit demonstrates a gap. Product aliases and semantics must be explicitly reviewed and scoped; ambiguous gross/net or packaging/product values remain unknown. No LLM-generated values, fetched taxonomy enums or scalar defaults become captured facts. The saved refrigerator umbrella_opening_mechanism anomaly must be excluded with a recorded reason.

FR06 Preserve explicit trusted profile selection as the default. Existing category bindings validate selection; they do not automatically select. This phase supplies reviewed exact target-to-profile bindings and explicit per-product goal profiles, with an explanation when either is absent or conflicting. Missing/ambiguous/partial categories or conflicting selections remain needs_review and cannot authorize corrections. Automatic resolution is a separately specified later feature, not an implied behavior change.

FR07 Publish additive coverage diagnostics through maintenance report and matching public operation/CLI paths: selected profile/version, configured fields, requested-and-checked fields, unsupported/missing fields, blockers and scoped category coverage. Configured fields alone are not checked coverage. Preserve existing report fields and legacy defaults. Diagnostics-enabled report output has a new 1 MiB serialized UTF-8 ceiling including envelope/newline; reject oversize output before emitting/replacing a result. Legacy output without diagnostics retains its behavior. Preserve identity matching, variant veto, evidence authority and publication/recheck safeguards. A policy comparison never independently authorizes identity or a correction. No changes to generic statistics/competitive-analysis semantics.

FR08 Persist exact profile definitions and category-policy identity at job creation. Resume/recheck with changed definitions must fail safely using existing profile/policy mismatch behavior. Preserve portable category roundtrips, existing custom profiles, profile-name collision rejection and source-evidence support states. No silent fallback to generic as detailed coverage, no automatic ancestor-policy inheritance or combining conflicting profiles.

FR09 Deliver small independently reviewed slices: inventory; refrigerator extraction/rules; maintenance/report/API/CLI integration; subsequent family packs chosen from reviewed inventory. No fixed promise for whole-market profile count or performance. Inventory uses saved sources first; no research downloads, model calls or production writes in planning. Implementation requires G1/G2/G3, saved red tests, bounded real-path checks, live evidence and final review.

## Acceptance scenarios

SC01 Inventory reproduces identical sorted rows/counts from pinned inputs and classifies new/extension/binding-only/unassessed separately; unknown inherited attributes are not counted as reviewed.
SC02 Three reference rows identify hardware/footwear partial and refrigerator missing; refrigerator candidate excludes the irrelevant umbrella attribute and does not claim full leaf coverage.
SC03 Existing profiles, custom profile files, explicit goal selection and existing report fields retain current behavior when new capabilities are unused.
SC04 Supported refrigerator capacities/dimensions normalize exactly; semantic mismatches, invalid or unsupported values remain unknown with traceable reasons.
SC05 Supported captured values survive normalize/persist/compare; absent, expired, truncated or unsupported support never becomes observed; taxonomy metadata supplies no product value.
SC06 Trusted explicit selection + matching exact category binding permits policy comparison only; missing/conflicting/ambiguous/partial configuration remains review-only. Mapping alone cannot select a profile.
SC07 Same identity with different capacity/model/dimensions cannot yield an unsafe proposed correction; agreeing quantities also cannot override conflicting GTIN/MPN/variant evidence.
SC08 Report distinguishes configured, requested, checked, missing, invalid and unsupported fields; common-field generic coverage cannot claim category-specific coverage.
SC09 Resume under changed profile/unit policy or category config is rejected; unchanged replay is stable and preserves evidence and original definitions.
SC10 A bounded six-adapter synthetic category matrix uses one shared refrigerator profile; platforms with unavailable product attributes are reported explicitly rather than marked analyzed.
SC11 Inventory/job subset respects registry 999/1000/1001 boundaries and deterministic ordering. Stress obeys declared budgets, saves smoke first, and stops on failure.

## Boundaries and compatibility

No universal taxonomy importer, exhaustive market taxonomy, auto profile selection, arbitrary profile inheritance, store writes, model training or inference. Future candidate packs include apparel, cosmetics, furniture and other electronics only after inventory/policy review; these are not committed counts. No new application of domain profiles to existing analyze/stats/competitive code.

## Workflow

Design/test design precede task breakdown. Planning stops after independent G1 review; code skeleton, components, red tests and implementation remain future work. Planning review success is not runtime verification. See status.md and reviews.md.
