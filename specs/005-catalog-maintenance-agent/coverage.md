# Final requirement evidence map

Mechanism evidence uses real store/engine/native parser/matcher; external HTTP and
advisor boundaries are controlled synthetic fixtures. No real model inference.
All named pytest nodes below occur in full-suite-progress-map.json's 783 confirmed
passes, unless explicitly marked driver/artifact. The first whole-suite run timed
out after783passes; approved suffix receipt confirms the remaining140passes.
923/923 distinct collected nodes now have passing results across these runs;
this is not a claim that the original single240s whole-suite command passed.
Parametrized nodes are expanded verbatim in full-suite-ordered-nodes.txt.
Paths below are repository-relative. `A`=tests/test_maintenance_acceptance.py,
`S`=tests/test_maintenance_store.py, `W`=tests/test_maintenance_workflow.py,
`I`=tests/test_maintenance_advisor.py, `R`=tests/test_maintenance_review_repairs.py,
`E`=tests/test_maintenance_remaining_edges.py, `P`=tests/test_maintenance_stress_prerequisites.py.

| Requirement | Exact executable evidence |
|---|---|
| FR01 | A::test_invalid_goals_rejected_before_dispatch; A::test_custom_profile_is_frozen_with_goal_before_execution |
| FR02 | A::test_supported_spec_correction_and_durable_evidence; W::test_native_sitemap_discovery_then_guarded_extraction; E::test_unique_identifier_candidate_keeps_ambiguous_variant_context |
| FR03 | A::test_deterministic_no_llm_and_unchanged; I::test_payload_is_selected_structured_evidence_without_raw_catalog; A::test_advisory_cannot_authorize_title_only_identity |
| FR04 | S::test_store_smoke_atomic_checkpoint_and_reopen; P::test_checkpoint_mutation_fixture_reaches_real_resume |
| FR05 | S::test_recovery_keeps_unknown_intent_charged_and_blocks_implicit_retry; I::test_explicit_unknown_advisor_retry_preserves_base_finding_and_old_charge; I::test_retry_publication_failure_preserves_previous_composition_and_charge |
| FR06 | W::test_cancel_active_wire_releases_owner_before_ack; S::test_kernel_owner_death_releases_lock_and_recovers_unknown_intent; E::test_cancel_during_known_retry_delay_prevents_second_wire |
| FR07 | S::test_cumulative_exact_reservation_edges; W::test_redirect_requests_cannot_escape_cumulative_budget; I::test_cost_reservation_denies_before_model_dispatch; I::test_overrun_records_actual_violation_and_stops_second_model_dispatch |
| FR08 | W::test_cache_exact_expiry_misses_but_report_evidence_survives_eviction; E::test_cache_hit_revalidates_policy_without_touching_saved_report; E::test_cache_corruption_is_a_miss_not_a_fact_or_silent_success |
| FR09 | A::test_stable_report_pagination_and_resume_ids; R::test_advisor_retry_preserves_real_native_partial_source_coverage; R::test_advisor_success_cannot_complete_unfinished_independent_work |
| FR10 | artifacts/catalog-maintenance-agent/operating-smokes.json; offline-example.log; cli-create.log; cli-status.log. Actual compile/help/create/status/offline example; wheel unavailable (missing build/hatchling). Original tool regression receipts in verification.md |
| FR11 | A::test_category_profile_field_roles; A::test_custom_profile_recovery_rejects_changed_or_missing_registry; E::test_custom_color_role_and_footwear_role_remain_distinct |
| FR12 | W::test_category_specs_remain_visible_without_overriding_matcher; W::test_real_source_category_conflict_vetoes_identifier_match; E::test_footwear_equal_numeral_with_different_size_system_is_unknown |
| SC01 | A::test_supported_spec_correction_and_durable_evidence; W::test_captured_baseline_preserves_evidence_instead_of_defaults |
| SC02 | A::test_deterministic_no_llm_and_unchanged; `mixed-100-disabled` and `exact-100` receipts in stress-resumed/progress.json |
| SC03 | A::test_advisory_cannot_authorize_title_only_identity; `mixed-100-enabled` receipt:5eligible calls, no identity override |
| SC04 | P::test_checkpoint_mutation_fixture_reaches_real_resume; A::test_resume_skips_committed_external_work |
| SC05 | S::test_kernel_owner_death_releases_lock_and_recovers_unknown_intent; I::test_model_crash_resumes_without_replay_or_refunding_unknown_spend; engine-os-crash.json actual OSexit91 before/after checkpoint, both restart0requests; stress20 crash windows |
| SC06 | W::test_same_store_second_engine_cannot_release_active_owner; S::test_control_cancel_while_execution_owner_is_active; W::test_cancel_active_wire_releases_owner_before_ack |
| SC07 | W::test_known_transient_transport_failure_retries_once_with_charged_attempts; A::test_source_auth_failure_has_no_retry; S::test_retry_delay_attempt_count_and_policy_failure_survive_reopen |
| SC08 | S::test_cumulative_exact_reservation_edges; A::test_expired_deadline_resume_cannot_gain_time; W::test_redirect_requests_cannot_escape_cumulative_budget; stress18 budget edges plus accounting mutation |
| SC09 | A::test_fresh_cache_retains_original_capture_time; W::test_cache_exact_expiry_misses_but_report_evidence_survives_eviction; E::test_cache_corruption_is_a_miss_not_a_fact_or_silent_success |
| SC10 | A::test_missing_baseline_never_becomes_default_fact; A::test_missing_supplier_support_never_invents_removal; E::test_explicit_zero_price_is_not_missing_or_boolean; E::test_captured_outdated_or_unsupported_baseline_has_distinct_provenance |
| SC11 | A::test_invalid_goals_rejected_before_dispatch; I::test_invalid_advice_never_changes_authority_or_refunds_unknown_usage; I::test_payload_is_selected_structured_evidence_without_raw_catalog; E::test_escaped_attribute_path_is_literal_and_observed |
| SC12 | A::test_stable_report_pagination_and_resume_ids; R::test_zero_product_budget_never_discovers_or_sends; R::test_product_cap_cannot_hide_captured_duplicate_identity; P::test_full_dictionary_matching_equivalence_and_actual_report_evidence |
| SC13 | I::test_timeout_retains_full_reservation_with_bounded_call; I::test_second_unknown_advisor_attempt_blocks_third_and_keeps_pagination; I::test_missing_trustworthy_bound_never_dispatches_model; I::test_advisor_price_identity_change_invalidates_cached_advice |
| SC14 | R::test_advisor_retry_preserves_real_native_partial_source_coverage; R::test_advisor_success_cannot_complete_unfinished_independent_work; I::test_retry_cancellation_before_publication_keeps_prior_advisory |
| SC15 | W::test_category_specs_remain_visible_without_overriding_matcher (six concrete profile/field cases) |
| SC16 | E::test_custom_color_role_and_footwear_role_remain_distinct |
| SC17 | A::test_exact_mass_conversion_does_not_authorize_identity; A::test_footwear_size_never_converts_between_systems; E::test_missing_footwear_size_system_is_unknown_even_equal_sizes; E::test_footwear_equal_numeral_with_different_size_system_is_unknown |
| SC18 | A::test_missing_category_is_visible_review; W::test_real_source_category_conflict_vetoes_identifier_match; A::test_profile_identity_change_requires_new_job; A::test_custom_profile_recovery_rejects_changed_or_missing_registry |

D sequential driver receipt: stress-resumed/summary-corrected.json records47new
passes,12exact reused proofs,172.427229s charged of180s, peak170.49MiB. Saved
progress identifies each executed/reused case and original log. Three100-item
batches allowed15s each; other5/10s limits unchanged. Original timeout attempts
remain historical and charged. Separate two-window OSdeath edge proof5.798s is
not folded into the completed stress budget. OS process-group cleanup prerequisite
P::test_hung_worker_and_descendant_are_terminated_and_reaped passed; no survivor.
No external exactly-once guarantee: unknown dispatch retains charges and needs
explicit bounded retry. Optional advisor protocol has no concrete paid-provider
integration. Actual counters unavailable; no quota percentage inferred.

Actual-live applicability: live/summary.json confirms native2product comparison,
4physicalHTTP,2unchanged title findings, partial/source_partial, restart0HTTP,
zeroLLM. Phase1 capture durable before phase2. No actual correction event observed;
synthetic SC01 proof is not relabelled live. Final whole-suite result is distributed
923distinctpasses; original240s timeout retained. Wheel remains unverified because
build/hatchling are unavailable. Final review required.
