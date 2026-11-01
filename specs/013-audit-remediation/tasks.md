# Dependency-ordered tasks — historical planning roadmap

Current implementation and verification state: [status.md](status.md). The original
roadmap below records planning-stage dependencies; all child functional stages
have since passed, while latest-source full-resource/final gates remain pending.

Behavior/scenario coverage was checked by task-breaker `/root/audit_research`
after reading spec.md and test-design.md. Every FR/SC is assigned below. This is
an umbrella roadmap, not permission to implement an epic as one unchecked task.
Owner roles are explicit; all agents run sequentially. No remote tickets created.

- [x] AR00 / FR08 / SC13 — behavior author `/root`: write behavior and acceptance
  design first; evidence spec.md/test-design.md and saved smoke.json.
- [x] AR01 / FR01–08 / SC01–13 — research/task-breaker `/root/audit_research`:
  inspect current source and selected saved evidence, verify mechanism smoke before
  expanding, classify ALL claims and identify distinct failure modes; evidence
  research.md, diagnostic.py/json, historical-index.json. No live claims invented.
- [x] AR02 / FR01–08 / SC01–13 — primary plan author: record dependencies,
  architecture decisions, compatibility decisions still open, verification and
  precise limits. Independent reviewer checks G1 planning artifacts and evidence.
  Resolve blockers before starting child designs. Evidence: plan.md, reviews.md, evidence/planning-review-digests.json and
  verification.md. Implementation gates below remain
  pending even if this planning review passes.

## Reviewable implementation slices (original planning state)

| Task / order | Dependencies | Owner deliverables and coverage | Completion evidence required |
| --- | --- | --- | --- |
| AR10 cross-cutting runtime children | AR02; slice-specific design/G1 | Runtime author + fixture author: FR06, SC03/11/12; request/item caps, retry remaining deadline, cancellation/partial batch seam, stdout/order/robots diagnostics; isolate suspected seeder blockage before fixing it | Red budget/error/controlled-blockage tests, G2 skeleton, G3 components, real-path mechanism + bounded stress, affected regressions, full repository driver, bounded live smoke, independent final review |
| AR11 first repair: truthful extraction results | AR02; reuse AR10 seams as needed | Outcome author: FR01/02, SC01/02/03; define outcome/coverage projection for API/CLI/tool; empty results, browser HTTP status, product evidence, Woo404 and capped/unknown states | Empty/unknown/terminal/capped matrix plus policy/free/error-page controls, parity tests, saved red/green, G1/G2/G3/final and offline/live evidence |
| AR12 slice2: money and roundtrip | AR11 outcome contract; AR10 input/resource seams | Money author: FR03/06, SC04/05/11; currency unknown representation decision preserving constructors; locale-aware amount parse, zero versus absent/rejected, compact/bounded extraction-to-downstream roundtrip | PKR/USD/EUR/ambiguous fixtures, conversion evidence assertions, cap−1/at/+1, stable identity/provenance roundtrip, review gates/full driver/bounded live |
| AR13 slice3a: HTML field coverage | AR11/12; independent HTML slice design | HTML author: FR04, SC06; root/mainEntity JSON-LD, bounded linked nodes, supported real/lazy image choice, breadcrumb/gallery/SKU/HTML product identity | Sanitized original sources, nested/equivalent/cyclic/adversarial fixtures, no policy regression, source-path support, gates/full driver/bounded live |
| AR14 slice3b: adapter field coverage | AR11/12; independent adapter designs | Adapter author: FR04, SC07; Woo brand/variants, budgeted Shopify ID enrichment, optional Magento capability/category reuse, Magento HTML detection and honest fallback signal semantics | Parent/variant join,429, unavailable fields and optional-schema failure fixtures; request limits; preserved core controls; per-adapter gates/full driver/bounded live |
| AR15 slice4: quality, eligibility and feed contracts | AR11/12; AR13/14 for available field support | Validation/export author: FR05, SC05/08/11; pin official current destination rules, canonical vendor->brand and stable ID decisions, separate presence/support/eligibility, unknown availability, feed preflight semantics | Conditional destination rules, support/default conflicts, XML/validator equivalence, golden compatibility fixtures, gates/full driver/bounded live |
| AR16 slice5: similarity and analysis honesty | AR11 outcome conventions; independent design, does not require all coverage work | Matching/analysis author: FR07, SC09/10; inspect/adjudicate audit pairs, explicit identity/candidate policy, function/quantity/variant conflicts, category counting semantics, tri-state availability | Reviewed positive/negative controls plus incompatible color/function/size cases; actual match/duplicate/analyze paths; identity recall reported separately; gates/full driver/live applicability explained |
| AR17 slice6: readiness interface | AR15 + stable truthful/source contracts; separately authorized feature scope | Product/validation author: FR05, SC08/13; decide whether command adds value over validation reports; separate Google destination eligibility, schema.org model completeness and ACP protocol requirements | New spec/test design, current primary sources, compatibility contract and all gates before command; no “Google approved” or generic compliance score |

AR10 is not a prerequisite epic for AR11: begin with a small bounded verification
harness, then truthful reporting/HTTP admission first. Split runtime fetch, deadline,
partial retention, stdout, robots and ordering work into independently reviewed
children alongside affected adapters. See plan.md for delivery order.

## Mandatory subtasks within each child

1. Behavior author revises that child's FR/SC acceptance design, inventories existing
   tests, names each uncovered risk, and resolves material unknown currency/outcome/
   identity/robots/destination decisions before breakdown. Task-breaker verifies
   coverage; researcher pins current primary external sources only where needed.
2. Separate reviewer G1 checks behavior/tests/tasks/research. Skeleton author then
   defines actual interfaces and acceptance tests; save failures for intended gaps.
   Separate reviewer G2 checks signatures/error paths and testability.
3. Component author reuses Normalizer outcomes, execution state, capture/identity
   and existing category adapters. Separate reviewer G3 checks cohesion and revised
   skeleton. Production author implements only after gates and saved red evidence.
4. Fixture author generates deterministic schema-valid and explicitly malformed
   fixtures with source/variant links. Independent coverage reviewer checks exact
   expected outcomes. Mechanism/stress executor uses real production paths, fixed
   seed0 and reviewed limits from test-design.md; saves first smoke before expansion.
5. Verification owner runs affected regressions then `python scripts/run_tests.py`
   using repository 240s-family/480s-total ceilings or narrower; preserve reports.
   Execute the child's predeclared bounded live smoke only after offline green.
   Report synthetic mechanism, stress and actual live outcomes separately.
6. Independent final reviewer checks actual diff and coverage against artifact
   digest, resolves blocking findings, and updates status/verification/reviews.
   A missing/inconclusive live transition requires real-path synthetic coverage;
   it never becomes a live pass. No push, PR or labels without authorized scope.

## Open decisions blocking implementation, not completion of this plan

- Outcome schema/version and CLI/API/tool parity; operation versus catalog coverage.
- Missing-currency representation while preserving legacy constructors/default feeds.
- Ambiguous-price rejection/context policy and zero eligibility by destination.
- Stable feed ID policy for records with no supported external ID.
- Partial timeout return/checkpoint lifecycle and strict outer process ownership.
- Robots user agent/policy/cache semantics, including unavailable robots responses.
- Bounded input-size/compact-projection contract and provenance retention limits.
- Woo variant sources and Magento optional field capabilities per deployment.
- Candidate versus confirmed match/duplicate semantics; category counting unit.
- Destination/country/category rule versions; distinct ACP/schema.org scope.
