# Concrete mechanism/stress inventory — corrected, unexecuted

Exactly48 cases; seed24;120s driver/5s per case; at most5 processes counting client/server resource trackers and one auxiliary worker. Conservative preflight fixture bound14,490,163 bytes <=16MiB. Runtime ledger measures actual constructed HTTP inputs, stream/wire fixtures, full graph representations and generated temp files; repeated physical/boundary representations are conservatively charged. Static JSON inputs counted once separately. Verification logs/source text are retained artifacts, not input fixture bytes. RSS separately measures temporary runtime allocation; input-byte bounds do not claim a memory pass.

| Case | Concrete node | Exact asserted links | Expected outcome |
| --- | --- | --- | --- |
| M01 | `tests/test_tool_lifecycle.py::test_immutable_pages_cursor_binding_expiry_and_release` | FR05,07,11 / SC03,07,12 / R6-release | Replay pages bind size; expiry invalidates real store handles and releases bytes |
| M02 | `tests/test_tool_lifecycle.py::test_aggregate_rejection_and_eviction_releases_graph` | FR07 / SC09,12 / R6 | Aggregate admission rejects oversize; eviction releases prior graph charge |
| M03 | `tests/test_tool_lifecycle.py::test_cancel_queue_and_completed_cancel_winner` | FR06 / SC04,12 | Queued cancellation never runs; succeeded cancellation preserves graph |
| M04 | `tests/test_tool_lifecycle.py::test_retained_charge_includes_products_and_each_real_payload_copy` | FR07,11 / SC07,09 / R5 | Every actual products/collections/owner payload representation is charged |
| M05 | `tests/test_tool_lifecycle.py::test_running_graph_reservation_counts_and_cancel_releases` | FR06,07 / SC04,09 / R6 | Running graph allowance reserves session bytes and cancellation releases it |
| M06 | `tests/test_agent_tool_api.py::test_unknown_version_rejected_before_work` | FR02,04 / SC01 | Unsupported version returns structured error before work |
| M07 | `tests/test_agent_tool_api.py::test_denied_source_is_structured_error_without_network` | FR04,08,09 / SC05,06 | Ungranted metadata origin fails permission before any fetch |
| M08 | `tests/test_agent_tool_api.py::test_existing_evidence_denied_through_other_valid_owner` | FR11 / SC07 / MC01-owner | Actual existing foreign evidence denied; remapping only scope makes same assertion fail |
| M09 | `tests/test_agent_tool_api.py::test_invalid_page_size_rejected` | FR02,05 / SC01,03 | Boolean page_size rejected and real error matches published schema |
| M10 | `tests/test_agent_tool_api.py::test_guard_refuses_nonpublic_dns_before_connect` | FR09 / SC06 | Private resolver answer denied by real guard |
| M11 | `tests/test_agent_tool_api.py::test_complete_domain_flow_uses_native_code_paths` | FR01,02,03,11 / SC01,02,07 | Real domain flow matches supported GTIN and exact captured price pointer/time; schemas reject corrupted price |
| M12 | `tests/test_agent_tool_api.py::test_cancel_running_resolution_publishes_no_catalog` | FR06 / SC04 | Per-job resolver cancellation signal propagates; no successful catalog |
| M13 | `tests/test_tool_shopware_policy.py::test_fixed_native_search_and_denied_redirect_target` | FR08,09 / SC06 / NS02 | Fixed search allowed; POST redirect sends zero bytes to target |
| M14 | `tests/test_tool_shopware_policy.py::test_denied_policy_route_and_body_never_send` | FR08 / SC05,06 / NS02,03 | Missing policy, alternate routes and malformed native body denied before wire |
| M15 | `tests/test_tool_native_modes.py::test_native_mode_guarded_parser_and_retained_evidence[shopify]` | FR03,07,11 / SC02,07 | Specific native parser returns actual price support under20 request cap |
| M16 | `tests/test_tool_native_modes.py::test_native_mode_guarded_parser_and_retained_evidence[woocommerce]` | FR03,07,11 / SC02,07 | Specific native parser returns actual price support under20 request cap |
| M17 | `tests/test_tool_native_modes.py::test_native_mode_guarded_parser_and_retained_evidence[magento]` | FR03,07,11 / SC02,07 | Specific native parser returns actual price support under20 request cap |
| M18 | `tests/test_tool_native_modes.py::test_native_mode_guarded_parser_and_retained_evidence[shopware]` | FR03,07,11 / SC02,07 / NS01 | Specific native parser returns actual price support under20 request cap |
| M19 | `tests/test_tool_native_modes.py::test_native_mode_guarded_parser_and_retained_evidence[bigcommerce]` | FR03,07,11 / SC02,07 | Specific native parser returns actual price support under20 request cap |
| M20 | `tests/test_tool_mechanisms.py::test_contract_missing_null_false_and_nonfinite` | FR02,04 / SC01 | Missing/null/false/nonfinite/deep input rejected; error/job schema corruption detected; config invalid values rejected |
| M21 | `tests/test_tool_mechanisms.py::test_input_byte_limit_edges` | FR02,07 / SC01,09 | Exact UTF8 byte bound accepted and just-above input denied |
| M22 | `tests/test_tool_mechanisms.py::test_cursor_tamper_collection_and_session` | FR05 / SC03 | Tampered cursor or collection/session mismatch cannot read another view |
| M23 | `tests/test_tool_mechanisms.py::test_empty_page_and_zero_total` | FR05 / SC03 | Authoritative empty collection is total0 without cursor |
| M24 | `tests/test_tool_mechanisms.py::test_queue_limit_and_waiting_deadline` | FR06,07 / SC04,09 | Queue excess rejected; waiting deadline counts enqueue time |
| M25 | `tests/test_tool_mechanisms.py::test_resolver_process_stall_is_reaped` | FR06,07,09 / SC04,06,12 / R1 | Real stalled child times out and reaps within bounded cleanup |
| M26 | `tests/test_tool_mechanisms.py::test_repeated_process_cancel_no_accumulation` | FR06,09 / SC04,06,12 / R2 | Three real child late-reply attempts after cancel cannot return results or accumulate workers |
| M27 | `tests/test_tool_mechanisms.py::test_domain_process_deadline_no_success` | FR06,07 / SC04,09 | Noncooperative domain child is killed at absolute deadline |
| M28 | `tests/test_tool_mechanisms.py::test_reaper_failure_stops_replacement` | FR06,07 / SC04,09 / R1-reaper-fault | Injected unreapable OS boundary marks broken and rejects replacement |
| M29 | `tests/test_tool_mechanisms.py::test_graph_default_byte_cap_and_shared_copies` | FR07,11 / SC07,09 / R5 | Actual default4MiB full graph admitted; +1 representation rejected without virtual dedup |
| M30 | `tests/test_tool_mechanisms.py::test_identity_encoding_rejected_before_stream_read` | FR07,09 / SC09,11 / R3 | Unsupported encoding rejected before stream iterator/decoder |
| M31 | `tests/test_tool_mechanisms.py::test_raw_body_multichunk_cap_and_false_length` | FR07,09 / SC09,11 / R4-stream | Actual streamed size enforces below/at/above limit despite false header |
| M32 | `tests/test_tool_mechanisms.py::test_shared_request_and_redirect_budget` | FR07,09 / SC06,09 | Redirects cannot reset cumulative source request budget |
| M33 | `tests/test_tool_mechanisms.py::test_redirect_count_cap` | FR07,09 / SC06,09 | Redirect loop ends at exact finite shared redirect count |
| M34 | `tests/test_tool_mechanisms.py::test_nonpublic_address_family_vectors` | FR09 / SC06 | Explicit IPv4/IPv6/private/mapped/metadata/multicast vectors all denied |
| M35 | `tests/test_tool_mechanisms.py::test_mixed_public_private_dns_denied` | FR09 / SC06 | One public DNS answer never permits a mixed private answer |
| M36 | `tests/test_tool_mechanisms.py::test_origin_idna_trailing_dot_port_and_bypass_syntax` | FR08,09 / SC06 | Origin canonicalization stable; numeric/auth/scheme/escaped bypass syntax denied |
| M37 | `tests/test_tool_mechanisms.py::test_discovered_denied_link_is_diagnostic_only` | FR03,08,09 / SC02,05,06 / R7 | Unallowed sitemap link is diagnostic-only and never fetched |
| M38 | `tests/test_tool_mechanisms.py::test_dns_change_after_discovery_denies_extraction` | FR03,09 / SC02,06 / R8 | Current private DNS invalidates formerly eligible extracted URL |
| M39 | `tests/test_tool_mechanisms.py::test_cross_origin_redirect_no_target_bytes` | FR08,09 / SC06 / MC01-redirect | Actual origin guard blocks target; changing only its origin set makes zero-send assertion fail |
| M40 | `tests/test_tool_mechanisms.py::test_pinned_numeric_tcp_preserves_host_and_tls` | FR09 / SC06 / R4-framing | HTTPCore pins numeric TCP/Host/SNI; framing mismatch fails; controlled TCP denied redirect target untouched |
| M41 | `tests/test_tool_mechanisms.py::test_evidence_response_cap_metadata` | FR07,11 / SC07,09 | Oversize evidence response returns metadata without complete oversized payload |
| M42 | `tests/test_tool_mechanisms.py::test_incomplete_capture_replay_never_confirms_removal` | FR03,11 / SC08,12 / MC02-partial-replay | Real incomplete capture replay cannot promote removal; report/diagnostics stable |
| M43 | `tests/test_tool_mechanisms.py::test_real_changes_replay_and_capture_grants` | FR03,06,11 / SC08,12 | Real report/event IDs replay; killed actual commit boundary rolls SQLite back with integrity intact |
| M44 | `tests/test_tool_mechanisms.py::test_supported_empty_distinct_from_backend_failure` | FR03,04 / SC11 | True native empty is complete; failed source is not success[] or secret leak |
| M45 | `tests/test_tool_mechanisms.py::test_publication_fault_releases_reservation` | FR04,05,06,07 / SC04,09,12 / MC02-dependency-expiry | Publication fault releases bytes; actual match losing source TTL fails expired without graph/handles |
| M46 | `tests/test_tool_mechanisms.py::test_real_evidence_expiry_and_disconnect` | FR05,07,11 / SC03,07,12 / MC02-evidence-expiry | Real extracted page/support expires through tools; restart cannot reuse owner |
| M47 | `tests/test_tool_mechanisms.py::test_feed_static_real_parser_and_evidence` | FR03,11 / SC02,07 | Existing XML feed parser/normalizer supplies observed price evidence |
| M48 | `tests/test_tool_mechanisms.py::test_late_cancelled_domain_cannot_publish` | FR06,07 / SC04,12 / MC01-terminal,MC02-late-publication | Cancellation-catching late domain result cannot publish; removing only actual guard makes same invariant fail |

## Outside this48-case run — separate evidence or still required

- Genuine MCP stdio complete flow/schema interoperability: saved mcp-full-flow-smoke.log and focused-contract-stability.log; not a5s stress case. Additional actual MCP request-cancel-before-ack/error parity/CLI configuration example verification remains planned before final completion, not claimed by direct-domain cancellation tests.
- Existing evidence expiry/pruning, suspicious rechecks/currency/scope/ordering interactions and variant persistence: affected-regressions.log187 passing existing checks; tool integration beyond exact rows above remains a final traceability audit obligation. Artificial tombstone-only stress case was replaced by actual partial capture replay; no claim of new tombstone integration coverage.
- Actual public DNS/TLS/live storefront observation and commercial changes: live plan remains separately pending after offline green; controlled TCP/fixtures are not public live evidence.
- Complete repository suite and CI matrix/no-extra plumbing: pending execution under explicit180s full-suite timeout; optional-extra CI is configured but not claimed run locally. Production load/unlimited-scale capacity is outside declared bounded evidence.
- Exact default request/response limits, malformed IDs and further feature interactions not asserted in a concrete row require applicable existing evidence or supplementary reviewed bounded checks before final completion; blanket FR/SC ranges are not coverage.

Negative controls keep real dispatch/lookup/guard/job publication active, modifying only owner lookup scope, guard origin set, or one in-memory AST cancellation check. Each uses the same invariant assertion as normal path and restores exact original state; no production bypass ships. See test-design MC repair design and tests/tool_faults.py.
