# #39 skeleton and research review handoff

Status: planning skeleton only; no tests or end-to-end example have passed here.
Owner files created: `examples/evidence_trust.py` and this handoff. No test stubs.
Read research-verification.md before skeleton creation; subsequently reviewed the
skeleton against research-persistence.md, research-portability.md and
research-verification.md. Existing implementation remains #34–36.

## Requirement/scenario map for implementer

| Requirement | Concrete implementation and planned verification |
| --- | --- |
| FR-01 retained field evidence | `examples/evidence_trust.py:run_demo`; `tests/test_evidence_trust_e2e.py:test_trust_e2e_extract_restart_bundle` and `test_trust_e2e_nested_and_transformed`; every factual path has support with locally dereferenceable evidence or explicit unavailable reason. |
| FR-02 states/raw transformations | Same example; `test_trust_e2e_missing_and_literal_values`, `test_trust_e2e_nested_and_transformed`; present zero/false/empty differs from missing/default; escaped pointers and variant ownership survive. |
| FR-03 alternatives/policy | `test_trust_e2e_conflicts`; selected, tied, stale and excluded alternatives survive with original rationale and policy version. |
| FR-04 persistence/migration | `test_trust_e2e_extract_restart_bundle`, `test_trust_e2e_legacy_and_restricted_export`, `test_trust_e2e_reject_corrupt_bundle`; use #37 restart/rollback/migration unit checks, never copy storage code into example. |
| FR-05 portability/sidecars | `test_trust_e2e_extract_restart_bundle`, `test_trust_e2e_legacy_and_restricted_export`; use #38 shared typed codec; preserve dictionary export defaults; companion mapping binds to verified exported bytes. |
| FR-06 score meanings | `test_trust_e2e_unverified_llm_score`; synthetic ungrounded score remains unsupported; explicitly supplied validated metadata is preserved without claiming empirical calibration. |
| FR-07 retention/caps | `test_trust_e2e_expiry_and_pruning`; explicit dry run and protected refs, separate forced expiry, affected effective views cannot remain observed; reuse existing capture caps. |
| SC-01 all fixture factual paths | Compute denominator with factual_paths for every bounded fixture, including containers and nested variants; report explicit unavailable reasons separately from retrievable supported evidence. |
| SC-02 retained conflicts | Assert all candidate IDs/evidence and reasons before/after persistence and bundle import, not just winner presence. |
| SC-03 semantic round trips | Assert typed Decimal, aware UTC microseconds, Product/Variant classes, Platform, tagged literal maps, IDs and full product/variant contracts after independent reopening/loading. |
| SC-04 compatibility/score semantics | Existing constructors, identities, compare/monitor outputs and default feeds remain compatible; scores never acquire validated-confidence meaning. |

Planned test names above are recommendations from saved research, not existing or
passing results. Tiny fixtures belong in `tests/fixtures/evidence-trust/` if external
files improve readability; deterministic Python literals are also sufficient.

## Documentation and spec delivery

Implementer owns `docs/evidence-trust.md`, README links and the #39 portions of
`specs/002-evidence-data-trust/{spec,plan,tasks,verification}.md`. Map final actual
test names to FR-01–07 and SC-01–04 in tasks.md; update APIs in the evidence contract
and data model consistently with #37/#38. Explain states, fixed UTC policy time,
legacy unsupported behavior, authority assertions, score/confidence distinction,
retention, sidecar identity limits, fragment caps and source truth limitations.

## Separate post-research review and fixes

- Persistence review: skeleton now names settled save/load/scoped retrieval APIs;
  requires real close/reopen and separate protected versus forced expiry. Never
  construct Evidence from a payload-less tombstone or rerun policy on import.
- Portability review: skeleton now names shared _portable APIs and requires both
  dynamic contract scopes, typed semantic comparisons and stable evidence IDs.
  Do not apply encode_value twice to TrustContract.to_dict output. Do not equate
  dataclass asdict with complete provenance serialization.
- Verification review: skeleton now requires a reusable run_demo, factual_paths
  denominator, no network/model dependencies, explicit non-calibration language
  and bounded fixtures. The current CLI exits honestly as a planning skeleton.

No executable integration is claimed until #37/#38 land. This is the concrete
handoff to the third implementer; replace the intentional planning exception and
CLI exit with working workflow, add meaningful tests and public documentation.

## Bounded validation order

Run the new example and E2E test first. Then affected contract/capture/resolution,
export/monitor/identity/comparison regressions. Run the full offline suite once
post-integration. Save commands, versions, counts, fixture scope and limitations
in `artifacts/epic-22-production/verification.md`; do not label fixture coverage as
accuracy or validated confidence. Parent coordinates shared spec edits to avoid
parallel overwrites. No live crawl, inference, broad sweeps or model downloads.
