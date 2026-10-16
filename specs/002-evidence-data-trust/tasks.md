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

## Dependent implementation
- [x] #35 FR-01/02: capture API/feed/structured/CSS/mocked LLM evidence; normalization history;
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

## #35 implementation sequence
- [x] FR-01/02: bounded capture contexts and normalization field mappings.
- [x] FR-01: API/feed/structured/CSS/LLM adapter integration, actual URLs/times.
- [x] FR-02: variant-ID enrichment, GTIN history, nested/default coverage.
- [x] FR-01/02/06: offline capture fixtures and affected regression suites.
- [x] Public API/limits documentation and spec/plan/tasks consistency.

#35 acceptance fixture mapping (tests/test_capture_provenance.py):
- FR-01/02: `test_api_response_redirect_and_zero_false` (three API families),
  `test_feed_retains_source_and_transformations` (XML/CSV),
  `test_structured_http_redirect_distinct_items_and_defaults`,
  `test_css_matching_nodes_and_ambiguous_items`.
- FR-02/06: `test_mocked_llm_cannot_assert_support_or_confidence`.
- FR-01/02: `test_variant_enrichment_and_gtin_history`,
  `test_filtered_nested_images_retain_correct_source_item`,
  `test_product_budget_and_standalone_variant_view`,
  `test_layered_fallback_cannot_borrow_jsonld_or_parent_support`.
- FR-01/02: `test_truncation_defaults_original_values_and_nested_escaping`,
  `test_feed_redirect_and_extraction_error`.

## #35 P2 review follow-up
- [x] Shared normalizer selections/outcomes; remove provenance parsing/mapping duplication.
- [x] Rejected API prices: `test_rejected_price_conversion_never_supports_default`
  (Shopify, WooCommerce, Magento, JSON-LD and feed).
- [x] Actual image fallback: `test_image_fallback_tracks_actual_successful_selection`.
- [x] Rejected condition: `test_unrecognized_condition_never_supports_default`.
- [x] Shopware mappings: `test_shopware_variant_uses_its_own_stock_id_and_title_inputs`.
- [x] Browser redirects: `test_browser_redirect_capture_uses_final_url` (JSON-LD/OG).
- [x] Selection/rejection integrity: `test_capture_budget_cannot_change_normalizer_source_selection`,
  `test_platform_fallback_consumes_outcomes_from_actual_normalizer`,
  `test_rejected_conversion_retains_original_input_and_reason`,
  `test_changed_captured_input_cannot_support_later_enrichment`.
- [x] Full compatibility suite and spec/plan/public documentation consistency.

## #35 live verification follow-up
- [x] Discover reachable public stores/sample publishers for all supported families.
- [x] Save eleven sequential live cases, original failures, contracts and source bodies.
- [x] Fix aggregate stock support and capture response-cookie currency at its source.
- [x] Normalize native Magento GraphQL and Shopware Store API/child paths.
- [x] Prioritize leaf capture within existing budgets; do not alter source selection.
- [x] Accept currency-prefix XML/CSV prices and trace CSS currency/image conversions.
- [x] Review actual browser output and exclude the demo's Error404 fallback.
- [x] Full suite: 444 passed; record adapter/ZIP/LLM/live-redirect coverage limitations.

## Subsequent platform-routing follow-up (separate from #35 scope)
- [x] Integrate Magento public GraphQL and explicit legacy REST protocol selection.
- [x] Integrate Shopware/BigCommerce storefront adapters with public config or explicit options.
- [x] Preserve generic-source normalization and failed API reasons on HTML continuation.
- [x] Bound product/page/variant behavior and BigCommerce native card discovery.
- [x] Correct public capability documentation and validate actual public pipeline cases.
- [x] Record BigCommerce token-based live coverage limitation separately from fixture/schema checks.
