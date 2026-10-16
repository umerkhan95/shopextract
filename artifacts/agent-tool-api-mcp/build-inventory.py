"""Build exact case traceability, static fixture sizes and finite preflight bounds."""
import ast,json
from pathlib import Path
root=Path(__file__).resolve().parents[2]
# Every entry names only assertions actually present in that concrete function.
LINKS={
'immutable_pages_cursor_binding_expiry_and_release':('FR05,07,11 / SC03,07,12 / R6-release','Replay pages bind size; expiry invalidates real store handles and releases bytes'),
'aggregate_rejection_and_eviction_releases_graph':('FR07 / SC09,12 / R6','Aggregate admission rejects oversize; eviction releases prior graph charge'),
'cancel_queue_and_completed_cancel_winner':('FR06 / SC04,12','Queued cancellation never runs; succeeded cancellation preserves graph'),
'retained_charge_includes_products_and_each_real_payload_copy':('FR07,11 / SC07,09 / R5','Every actual products/collections/owner payload representation is charged'),
'running_graph_reservation_counts_and_cancel_releases':('FR06,07 / SC04,09 / R6','Running graph allowance reserves session bytes and cancellation releases it'),
'unknown_version_rejected_before_work':('FR02,04 / SC01','Unsupported version returns structured error before work'),
'denied_source_is_structured_error_without_network':('FR04,08,09 / SC05,06','Ungranted metadata origin fails permission before any fetch'),
'existing_evidence_denied_through_other_valid_owner':('FR11 / SC07 / MC01-owner','Actual existing foreign evidence denied; remapping only scope makes same assertion fail'),
'invalid_page_size_rejected':('FR02,05 / SC01,03','Boolean page_size rejected and real error matches published schema'),
'guard_refuses_nonpublic_dns_before_connect':('FR09 / SC06','Private resolver answer denied by real guard'),
'complete_domain_flow_uses_native_code_paths':('FR01,02,03,11 / SC01,02,07','Real domain flow matches supported GTIN and exact captured price pointer/time; schemas reject corrupted price'),
'cancel_running_resolution_publishes_no_catalog':('FR06 / SC04','Per-job resolver cancellation signal propagates; no successful catalog'),
'fixed_native_search_and_denied_redirect_target':('FR08,09 / SC06 / NS02','Fixed search allowed; POST redirect sends zero bytes to target'),
'denied_policy_route_and_body_never_send':('FR08 / SC05,06 / NS02,03','Missing policy, alternate routes and malformed native body denied before wire'),
'native_mode_guarded_parser_and_retained_evidence':('FR03,07,11 / SC02,07','Specific native parser returns actual price support under20 request cap'),
'contract_missing_null_false_and_nonfinite':('FR02,04 / SC01','Missing/null/false/nonfinite/deep input rejected; error/job schema corruption detected; config invalid values rejected'),
'input_byte_limit_edges':('FR02,07 / SC01,09','Exact UTF8 byte bound accepted and just-above input denied'),
'cursor_tamper_collection_and_session':('FR05 / SC03','Tampered cursor or collection/session mismatch cannot read another view'),
'empty_page_and_zero_total':('FR05 / SC03','Authoritative empty collection is total0 without cursor'),
'queue_limit_and_waiting_deadline':('FR06,07 / SC04,09','Queue excess rejected; waiting deadline counts enqueue time'),
'resolver_process_stall_is_reaped':('FR06,07,09 / SC04,06,12 / R1','Real stalled child times out and reaps within bounded cleanup'),
'repeated_process_cancel_no_accumulation':('FR06,09 / SC04,06,12 / R2','Three real child late-reply attempts after cancel cannot return results or accumulate workers'),
'domain_process_deadline_no_success':('FR06,07 / SC04,09','Noncooperative domain child is killed at absolute deadline'),
'reaper_failure_stops_replacement':('FR06,07 / SC04,09 / R1-reaper-fault','Injected unreapable OS boundary marks broken and rejects replacement'),
'graph_default_byte_cap_and_shared_copies':('FR07,11 / SC07,09 / R5','Actual default4MiB full graph admitted; +1 representation rejected without virtual dedup'),
'identity_encoding_rejected_before_stream_read':('FR07,09 / SC09,11 / R3','Unsupported encoding rejected before stream iterator/decoder'),
'raw_body_multichunk_cap_and_false_length':('FR07,09 / SC09,11 / R4-stream','Actual streamed size enforces below/at/above limit despite false header'),
'shared_request_and_redirect_budget':('FR07,09 / SC06,09','Redirects cannot reset cumulative source request budget'),
'redirect_count_cap':('FR07,09 / SC06,09','Redirect loop ends at exact finite shared redirect count'),
'nonpublic_address_family_vectors':('FR09 / SC06','Explicit IPv4/IPv6/private/mapped/metadata/multicast vectors all denied'),
'mixed_public_private_dns_denied':('FR09 / SC06','One public DNS answer never permits a mixed private answer'),
'origin_idna_trailing_dot_port_and_bypass_syntax':('FR08,09 / SC06','Origin canonicalization stable; numeric/auth/scheme/escaped bypass syntax denied'),
'discovered_denied_link_is_diagnostic_only':('FR03,08,09 / SC02,05,06 / R7','Unallowed sitemap link is diagnostic-only and never fetched'),
'dns_change_after_discovery_denies_extraction':('FR03,09 / SC02,06 / R8','Current private DNS invalidates formerly eligible extracted URL'),
'cross_origin_redirect_no_target_bytes':('FR08,09 / SC06 / MC01-redirect','Actual origin guard blocks target; changing only its origin set makes zero-send assertion fail'),
'pinned_numeric_tcp_preserves_host_and_tls':('FR09 / SC06 / R4-framing','HTTPCore pins numeric TCP/Host/SNI; framing mismatch fails; controlled TCP denied redirect target untouched'),
'evidence_response_cap_metadata':('FR07,11 / SC07,09','Oversize evidence response returns metadata without complete oversized payload'),
'incomplete_capture_replay_never_confirms_removal':('FR03,11 / SC08,12 / MC02-partial-replay','Real incomplete capture replay cannot promote removal; report/diagnostics stable'),
'real_changes_replay_and_capture_grants':('FR03,06,11 / SC08,12','Real report/event IDs replay; killed actual commit boundary rolls SQLite back with integrity intact'),
'supported_empty_distinct_from_backend_failure':('FR03,04 / SC11','True native empty is complete; failed source is not success[] or secret leak'),
'publication_fault_releases_reservation':('FR04,05,06,07 / SC04,09,12 / MC02-dependency-expiry','Publication fault releases bytes; actual match losing source TTL fails expired without graph/handles'),
'real_evidence_expiry_and_disconnect':('FR05,07,11 / SC03,07,12 / MC02-evidence-expiry','Real extracted page/support expires through tools; restart cannot reuse owner'),
'feed_static_real_parser_and_evidence':('FR03,11 / SC02,07','Existing XML feed parser/normalizer supplies observed price evidence'),
'late_cancelled_domain_cannot_publish':('FR06,07 / SC04,12 / MC01-terminal,MC02-late-publication','Cancellation-catching late domain result cannot publish; removing only actual guard makes same invariant fail'),
}
files=['tests/test_tool_lifecycle.py','tests/test_agent_tool_api.py','tests/test_tool_shopware_policy.py','tests/test_tool_native_modes.py','tests/test_tool_mechanisms.py']
cases=[]
for filename in files:
 for node in ast.parse((root/filename).read_text()).body:
  if isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef)) and node.name.startswith('test_'):
   key=node.name.removeprefix('test_');mapping,expected=LINKS[key]
   variants=['shopify','woocommerce','magento','shopware','bigcommerce'] if filename.endswith('native_modes.py') else [None]
   for variant in variants:
    exact=mapping+(' / NS01' if variant=='shopware' else '')
    size=(8*1024*1024+4096 if 'default_byte_cap' in key else 512*1024 if any(s in key for s in ['real_changes','existing_evidence','incomplete_capture']) else 256*1024 if any(s in key for s in ['native_mode','complete_domain','real_evidence_expiry','publication_fault']) else 128*1024 if 'feed_static' in key else 65536)
    cases.append({'id':f'M{len(cases)+1:02d}','node':filename+'::'+node.name+(f'[{variant}]' if variant else ''),
     'mapping':exact,'expected':expected,'source':filename,'case_timeout_seconds':5,'max_fixture_bytes':size})
static_inputs=[{'path':p,'bytes':(root/p).stat().st_size} for p in ['tests/fixtures/shopify_products.json','tests/fixtures/woocommerce_products.json']]
assert len(cases)==48
bound=sum(c['max_fixture_bytes'] for c in cases)+sum(p['bytes'] for p in static_inputs)
assert bound<=16*1024*1024
manifest={'seed':24,'maximum_cases':48,'driver_seconds':120,'fixture_bytes_limit':16*1024*1024,
 'planned_fixture_bound_bytes':bound,'static_fixture_inputs':static_inputs,'additional_rss_target_bytes':256*1024*1024,
 'max_processes':5,'active_jobs':1,'prerequisite':'independent fixture/coverage review + saved passing MCP smoke','cases':cases}
(root/'artifacts/agent-tool-api-mcp/mechanism-inventory.json').write_text(json.dumps(manifest,indent=2)+'\n')
lines=['# Concrete mechanism/stress inventory — corrected, unexecuted','',
 f'Exactly48 cases; seed24;120s driver/5s per case; at most5 processes counting client/server resource trackers and one auxiliary worker. Conservative preflight fixture bound{bound:,} bytes <=16MiB. Runtime ledger measures actual constructed HTTP inputs, stream/wire fixtures, full graph representations and generated temp files; repeated physical/boundary representations are conservatively charged. Static JSON inputs counted once separately. Verification logs/source text are retained artifacts, not input fixture bytes. RSS separately measures temporary runtime allocation; input-byte bounds do not claim a memory pass.','',
 '| Case | Concrete node | Exact asserted links | Expected outcome |','| --- | --- | --- | --- |']
for c in cases:lines.append(f"| {c['id']} | `{c['node']}` | {c['mapping']} | {c['expected']} |")
lines+=['','## Outside this48-case run — separate evidence or still required','',
 '- Genuine MCP stdio complete flow/schema interoperability: saved mcp-full-flow-smoke.log and focused-contract-stability.log; not a5s stress case. Additional actual MCP request-cancel-before-ack/error parity/CLI configuration example verification remains planned before final completion, not claimed by direct-domain cancellation tests.',
 '- Existing evidence expiry/pruning, suspicious rechecks/currency/scope/ordering interactions and variant persistence: affected-regressions.log187 passing existing checks; tool integration beyond exact rows above remains a final traceability audit obligation. Artificial tombstone-only stress case was replaced by actual partial capture replay; no claim of new tombstone integration coverage.',
 '- Actual public DNS/TLS/live storefront observation and commercial changes: live plan remains separately pending after offline green; controlled TCP/fixtures are not public live evidence.',
 '- Complete repository suite and CI matrix/no-extra plumbing: pending execution under explicit180s full-suite timeout; optional-extra CI is configured but not claimed run locally. Production load/unlimited-scale capacity is outside declared bounded evidence.',
 '- Exact default request/response limits, malformed IDs and further feature interactions not asserted in a concrete row require applicable existing evidence or supplementary reviewed bounded checks before final completion; blanket FR/SC ranges are not coverage.','',
 'Negative controls keep real dispatch/lookup/guard/job publication active, modifying only owner lookup scope, guard origin set, or one in-memory AST cancellation check. Each uses the same invariant assertion as normal path and restores exact original state; no production bypass ships. See test-design MC repair design and tests/tool_faults.py.']
(root/'specs/004-agent-tool-api-mcp/mechanism-inventory.md').write_text('\n'.join(lines)+'\n')
print('saved48 exact cases; fixture preflight bound',bound)
