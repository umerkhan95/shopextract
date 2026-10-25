# Implementation plan: category analysis coverage

2026-10-25. Planning deliverable only; implementation and verification remain future work. Read spec.md, test-design.md, research.md and tasks.md together. The task-breaker reviewed SC01–SC11 before breakdown; its findings and FR/SC ownership are recorded in tasks.md.

## Intended result and scope

First produce an honest, reproducible coverage matrix from retained Shopify 2026-08 electronics/apparel/home-garden sources and existing policies. Pin the source denominator and separately report unassessed branches. Review attribute and comparison semantics before counting profile families. The exact remaining profile count is currently unknown. Existing hardware/footwear are partial; generic is common-field support; mapping-platform counts cannot substitute for policy coverage.

Next deliver one refrigerator-v1 pilot for total capacity, product width/height/depth and exact model, with common fields. Physical quantities use exact ml/L→L and mm/cm/m→m normalization. Invalid/ambiguous capacity or dimension semantics remain unknown. Capacity/model/dimension differences are identity_variant-sensitive and cannot authorize unsafe corrections. A successful pilot is selected-field coverage, not complete refrigerator/appliance coverage. Subsequent family packs follow the reviewed matrix, one slice at a time.

## Constitution check and architecture decisions

Preserve Product/Variant constructors, extraction APIs, old feed/report defaults, identity authority and evidence/recheck protections. Retain old built-in/custom profile definitions, source support states, category portable roundtrips and historical snapshots. New capabilities must have explicit persisted unit-policy identity, coherent Python/custom-schema validation and safe resume mismatch behavior. Do not retrofit existing jobs silently. Interfaces and exact serialization/reason enums belong in skeleton.md after G1, before implementation.

Reuse CategoryProfile/FieldRule/compare_field, capture and normalization tracing, category mapper/companions, MaintenanceStore, engine, matcher, public operation and CLI adapters. Inventory output is an offline artifact, not a complete runtime taxonomy registry. Runtime uses an explicit bounded target subset (1000 cap) and trusted per-product profile selection. Category bindings validate selection; automatic selection and ancestor inheritance are out of scope.

Audit extraction first: a comparison test with hand-populated attributes does not prove captured evidence. For each adapter/field, show real raw source pointer → normalized Product.attributes → support companion → persisted product → guarded comparison, or declare unavailable. Only demonstrated missing seams justify extraction changes. Reject refrigerator umbrella metadata as irrelevant. Keep taxonomy metadata, captured facts and reviewed policy semantics distinct.

Coverage diagnostics are additive and bounded: selected definition/version, configured/requested/actually checked fields, unavailable/invalid/unsupported fields and blockers. Do not embed full taxonomy inventory in each product or report. Preserve Store.report paging and existing report budgets. The maintenance CLI has no existing output cap; require a new 1 MiB serialized UTF-8 cap (envelope/newline included) for diagnostics-enabled report output, leaving legacy output unchanged when diagnostics are unused; freeze page-vs-job scope at G2 and verify accurate totals without unbounded materialization. Configured or merely attempted rules do not count as checked support. Generic common fields never count as detailed domain support. Unknown requested rules must fail safely under strong identity/support as well as missing-data cases.

All changes stay MIT/self-hostable, with no paid service dependency. No production writes, model inference, automatic source refresh or Git publication is part of this plan.

## Phases, dependencies and exit criteria

| Phase | Dependency | Deliverable and exit criterion |
| --- | --- | --- |
| Planning | Existing behavior/test design | This roadmap plus research/tasks; independent G1 must review exact artifacts. No runtime completion claim. |
| Inventory | Planning G1, inventory G2/G3 and saved red tests | Three-reference smoke saved first, reproducible pinned rows/denominators, semantic family review and new/extension/binding-only backlog; executable changes verified and independently reviewed. |
| Refrigerator pilot | Accepted inventory, updated pilot G1/G2/G3 + relevant saved red tests | One new policy; exact units and immutable snapshot compatibility; actual extraction/evidence paths; explicit selection/binding safety; bounded maintenance/API/CLI diagnostics; real mechanism and final checks. |
| Next family pack | Pilot final review and reviewed inventory | Small named family scope with independently designed semantics/tests and full workflow; no promised whole-market count. |

The pilot rule/extraction/report tasks are dependent increments within one feature slice; they are not independently claimed as shippable verified products. If extraction changes touch more than three live adapter seams, split into reviewed sub-slices with separate live budgets and repeat affected gates. Family count and delivery estimates are outputs of inventory, not guessed planning commitments.

## Gates and verification

G1 independent behavior/tests/tasks/research review is the current planning endpoint. G2 skeleton, G3 component reuse and final reviews remain pending. APC03–APC17 schedule explicit author/reviewer ownership and acceptance red evidence before implementation. Material behavior changes return to spec/test design and invalidate affected downstream verdicts. A planning review cannot approve nonexistent code or future tests.

Verification uses proposed inventory/quantity/integration/CLI test modules and affected existing maintenance/category regressions, finalized at G2. Execute test-design's fixed seed-26 real-path mechanism plan; one saved smoke then 48 manifest cases, sequential, 120 seconds, 512 MiB memory ceiling, no broad fuzzing. Include malformed units, numeric zero/bool/missing distinctions, alias semantics, identity vetoes, fully supported unknown fields, partial/conflict bindings, expiry, replay, conversion assertion sensitivity, persistence failure/retry, registry 999/1000/1001 and report boundaries. Independent review must confirm distinct risks instead of inflated variation counts.

After focused checks, run the required `python scripts/run_tests.py` driver using configured development environment, without raising its 240-second family or 480-second shared ceilings. Save commands, logs, environment and results in verification.md. No tests were run for this planning assignment. Historical evaluation passes are reusable context only.

Only after offline success, predeclare actual discovered product URLs and expected supported fields. Start with one refrigerator capture; total ≤3 URLs/6 requests (redirects included), one worker, 15 seconds/request and 90 seconds including cleanup, no automatic retries. Stop on access denial/unexpected behavior. A blocked required live extraction check remains blocked; deterministic fixtures must still exercise missing live transitions through actual code. Record mechanism correctness, bounded stress and actual live observation separately; no induced store change or fabricated live values.

Update status.md at each stage with next action, ownership and blockers; reviews.md records actual digest/findings/verdict; verification.md contains actual evidence. Missing required gates/full-driver/mechanism/live coverage blocks implementation completion. Current planning/documentation live status is not applicable. Session token counters are unavailable; no quota estimate is made. No production code, tests or network activity is authorized by this planning-only handoff.

Binding decisions for G1: generic quantity keys do not prove semantics; require source-backed total-volume/product-dimension context or an explicitly reviewed adapter contract, otherwise unknown. Preserve the semantic identifier with source support through persistence. G2 chooses its concrete additive carrier, not whether the evidence is required. Existing *-v1 naming remains; additive volume/length normalization identifiers have immutable versioned meanings stored in profile definitions. Both Python and JSON-schema validation add the same allowlisted identifiers. Any future semantic change needs a different persisted definition and mismatch behavior; old identifiers and custom profiles retain their meanings.
