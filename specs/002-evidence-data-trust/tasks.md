# Dependency-ordered work and requirement coverage

## #34 foundation
- [x] FR-01/02/06: constitution, templates, shared spec, plan, research, matrix and contract.
- [x] FR-01: Evidence IDs/UTC/retained pointers and graph validation.
  Checks: `test_malformed_evidence_rejected`, `test_references_versions_and_confidence_validation`.
- [x] FR-02: explicit states and factual nested coverage; preserve scalar compatibility.
  Checks: `test_missing_normalized_and_literal_zero_false_are_distinct`,
  `test_nested_coverage_and_derived_fields`, `test_legacy_constructors_identity_and_serialization_unchanged`.
- [x] FR-06: score/confidence separation and typed serialization.
  Checks: `test_typed_round_trip_and_uncalibrated_scores`, `test_malformed_observation_rejected`.
- [x] Interface handoff FR-03/07: resolution alternatives and unavailable-state contracts.
  Checks: `test_conflicts_preserved_and_explicit_selection`,
  `test_expired_unknown_and_unsupported_reasons_survive`.
- [x] P2 review FR-06/serialization: recursive Enum codec validation/escaping and
  observed-only validated confidence. Checks: `test_enum_values_use_recursive_codec`,
  `test_enum_values_cannot_bypass_validation`,
  `test_only_observed_state_accepts_validated_confidence`.
- [x] Verify affected compatibility suites and save outcomes in verification.md.
- [x] Check spec/plan/tasks consistency against #34 acceptance criteria.

## Dependent implementation (not completed by #34)
- [ ] #35 FR-01/02: capture API/feed/structured/CSS/mocked LLM evidence; normalization history;
  adapter coverage fixtures including GTIN restoration, absent and zero/false values.
- [ ] #36 FR-02/03/06: authority, freshness, equivalence/ties, deterministic resolution;
  table-driven conflict/matching fixtures. Depends on #34/#35.
- [ ] #37 FR-04/07: atomic SQLite, retrieval, idempotent migration, pruning limits;
  restart/rollback/retention fixtures. Depends on #34/#35.
- [ ] #38 FR-05/06: portable Product/evidence bundle, sidecars and report references;
  lossless semantic round trips. Depends on #35/#36/#37.
- [ ] #39 FR-01–07, SC-01–04: offline end-to-end demonstration and documented limits;
  map full factual coverage, retained conflicts, restart/export semantics and legacy
  regressions to named tests before closing #22. Depends on #36/#37/#38.
