"""Reviewed-before-run sequential category mechanism plan. No network/model launcher."""
import json
import hashlib
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'artifacts/category-mapping'
CASES = {
 'C01':['test_category_skeleton.py::test_c01_normalize_preserves_custom_label'],
 'C02':['test_category_woocommerce.py::test_c02_siblings_permutations_and_duplicate_source_support'],
 'C03':['test_category_bigcommerce.py::test_c03_reviewed_query_validates_against_saved_schema','test_category_bigcommerce.py::test_c03_native_mode_default_and_partial_error_keeps_siblings','test_category_bigcommerce.py::test_c03_rejection_is_unavailable_without_retry'],
 'C04':['test_category_bigcommerce.py::test_c04_missing_completion_or_next_page_retains_only_bounded_memberships'],
 'C05':['test_category_shopware.py::test_c07_four_memberships_nine_index_ids_never_path'],
 'C06':['test_category_magento.py::test_magento_native_query_opt_in_and_default_response_compatibility','test_category_magento.py::test_magento_nonzero_product_error_localization_retains_valid_siblings','test_category_review_repairs.py::test_c06_c11_magento_nonnull_failed_facets_cannot_map'],
 'C07':['test_category_generic.py::test_c07_jsonld_memberships_and_opaque_delimiters'],
 'C08':['test_category_generic.py::test_c08_feed_real_parser_retains_separate_namespaces','test_category_generic.py::test_c08_declared_google_path_and_one_xml_decode'],
 'C09':['test_category_generic.py::test_c09_category_code_context_and_thing'],
 'C10':['test_category_generic.py::test_c10_schema_raw_states','test_category_woocommerce.py::test_c10_source_states'],
 'C11':['test_category_skeleton.py::test_c11_source_facets_keep_id_and_label_support_separate','test_category_skeleton.py::test_c11_label_rule_cannot_borrow_supported_id','test_category_generic.py::test_c11_mutation_retention_and_llm_do_not_gain_support'],
 'C12':['test_category_woocommerce.py::test_c12_store_basepath_catalog_and_assignment_context'],
 'C13':['test_category_shopware.py::test_c13_actual_parent_endpoints_only_and_cycle_bounded','test_category_review_repairs.py::test_c13_bound_endpoint_mismatch_rejected','test_category_review_repairs.py::test_c13_orphan_retains_declared_edge_without_root_claim'],
 'C14':['test_category_shared_contract.py::test_c14_three_native_sources_share_one_exact_mapper'],
 'C15':['test_category_skeleton.py::test_c15_overlapping_targets_remain_ambiguous'],
 'C16':['test_category_skeleton.py::test_c16_invalid_target_rejected','test_category_shared_contract.py::test_c16_config_entry_boundary_is_explicit'],
 'C17':['test_category_shared_contract.py::test_c17_real_companion_roundtrip_retains_source_and_derived_history'],
 'C18':['test_category_shared_contract.py::test_c18_nested_mutation_cannot_be_reencoded'],
 'C19':['test_category_skeleton.py::test_c19_real_source_cache_reuse_and_rule_change','test_category_skeleton.py::test_c19_store_creation_persists_canonical_policy','test_category_skeleton.py::test_c19_resume_policy_mismatch_never_retroactively_enables_job','test_category_shared_contract.py::test_c19_corrupt_companion_cache_is_miss_not_legacy_fallback'],
 'C20':['test_category_review_repairs.py::test_c20_real_category_engine_preserves_matcher_safeguards'],
 'C21':['test_category_bigcommerce.py::test_c21_guard_uses_producer_constants_only_in_enabled_mode'],
 'C22':['test_category_shared_contract.py::test_c22_companion_bytes_below_at_above','test_category_shared_contract.py::test_c22_native_member_boundary_preserves_supported_terms','test_category_shopware.py::test_c22_shared_relation_budget_and_zero','test_category_review_repairs.py::test_c13_c22_explicit_depth_boundary'],
 'C23':['test_category_generic.py::test_c10_opengraph_repeats_retained_unknown_and_default_unchanged'],
 'C24':['test_category_shopware.py::test_c24_legacy_shopware_category_projection_unchanged','test_category_review_repairs.py::test_c24_encode_and_checkpoint_failure_atomic_retry'],
}
PLAN = {'schema_version':1,'seed':26,'mechanisms':24,'parameter_invocations_max':100,
        'aggregate_seconds':120,'invocation_seconds':15,'collection_seconds':15,'log_bytes_max':65536,'aggregate_logs_bytes_max':1048576,'workers':1,'fixture_bytes_max':262144,
        'oversize_boundary_bytes':262145,'aggregate_fixtures_bytes_max':8388608,
        'config_boundary_entries':1001,'stop_on_failure':True,'cases':CASES,
        'provenance':'controlled/synthetic/derived offline, never live storefront',
        'state':'exact13_completion_pending_review','execution':'one_fixed_completion_session',
        'first_attempt_invocations':42,'repaired_attempt_invocations':19,'targeted_byte_invocations':3,
        'reused_passes':62,'remaining_invocations':13,'cumulative_invocations_max':77,
        'resume_manifest':'artifacts/category-mapping/mechanism-completion-manifest.json'}


def _cleanup(process):
    # A session is created for every invocation. Kill the complete process group
    # even after its leader exits, so background auxiliary children cannot escape.
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    process.wait(timeout=2)
    # Linux subreaper mode lets this parent also wait adopted descendants. On
    # macOS launchd reaps orphans; the group kill still covers every descendant.
    deadline = time.monotonic() + 2
    while time.monotonic() < deadline:
        try:
            child, _ = os.waitpid(-process.pid, os.WNOHANG)
        except ChildProcessError:
            break
        if child == 0:
            time.sleep(.01)


def run_bounded(command, *, seconds, log_path, env, log_bytes=65536,
                progress_path=None, invocation_seconds=15, collection_seconds=15):
    """One bounded child session; drain output without retaining an unbounded log."""
    if sys.platform == 'linux':
        import ctypes
        ctypes.CDLL(None).prctl(36, 1, 0, 0, 0)  # PR_SET_CHILD_SUBREAPER
    started = time.monotonic()
    process = subprocess.Popen(command, cwd=ROOT, env=env, stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT, start_new_session=True)
    retained, truncated, timed_out = 0, False, False
    timeout_reason = None
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ)
    try:
        with Path(log_path).open('wb') as log:
            while True:
                remaining = seconds - (time.monotonic() - started)
                if remaining <= 0:
                    timed_out, timeout_reason = True, 'aggregate_timeout'
                    break
                if progress_path is not None:
                    progress = None
                    try:
                        if Path(progress_path).exists():
                            data = Path(progress_path).read_bytes()
                            if len(data) > 65536:
                                raise ValueError('progress cap')
                            progress = json.loads(data)
                    except (ValueError, OSError):
                        timed_out, timeout_reason = True, 'progress_invalid'
                        break
                    phase = progress.get('phase') if progress else 'collection'
                    phase_start = progress.get('phase_started', started) if progress else started
                    limit = invocation_seconds if phase == 'invocation' else collection_seconds
                    if phase in ('collection','invocation') and time.monotonic()-phase_start >= limit:
                        timed_out = True
                        timeout_reason = 'invocation_timeout' if phase == 'invocation' else 'collection_timeout'
                        break
                for key, _ in selector.select(min(.05, remaining)):
                    data = os.read(key.fileobj.fileno(), 65536)
                    if not data:
                        selector.unregister(key.fileobj)
                        continue
                    keep = data[:max(0, log_bytes-retained)]
                    log.write(keep)
                    retained += len(keep)
                    truncated = truncated or len(keep) != len(data)
                if process.poll() is not None:
                    # Drain any queued leader output; inherited descendant pipes
                    # do not postpone group cleanup after the leader finishes.
                    for key, _ in selector.select(0):
                        data = os.read(key.fileobj.fileno(), 65536)
                        keep = data[:max(0, log_bytes-retained)]
                        log.write(keep); retained += len(keep)
                        truncated = truncated or len(keep) != len(data)
                    break
    finally:
        _cleanup(process)
        selector.close()
        process.stdout.close()
    return dict(returncode=process.returncode, timed_out=timed_out, timeout_reason=timeout_reason,
        seconds=round(time.monotonic()-started,3), log_bytes=retained, log_truncated=truncated)


def _resume_manifest():
    path = ROOT/PLAN['resume_manifest']
    manifest = json.loads(path.read_text())
    for name, expected in manifest['archived_evidence'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Archived prior evidence changed: '+name)
    for name, expected in manifest['source_hashes'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected:
            raise ValueError('Saved source/test changed; completed evidence cannot be reused: '+name)
    for name, expected in manifest['original_logs_unchanged'].items():
        if hashlib.sha256((ROOT/name).read_bytes()).hexdigest() != expected['sha256']:
            raise ValueError('Archived original evidence changed: '+name)
    if (len(manifest['all_nodes']) != 75 or len(manifest['passed_nodes']) != 62 or
            len(manifest['remaining_nodes']) != 13 or manifest['invocations_started'] != 64 or
            len(set(manifest['passed_nodes']) | set(manifest['remaining_nodes'])) != 75 or
            set(manifest['passed_nodes']) & set(manifest['remaining_nodes']) or
            manifest['invocations_started'] + len(manifest['remaining_nodes']) != 77):
        raise ValueError('Invalid bounded resume manifest')
    return manifest


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    (OUT/'mechanism-plan.json').write_text(json.dumps(PLAN,indent=2)+'\n')
    if '--plan-only' in sys.argv:
        return 0
    manifest = _resume_manifest()
    # One fixed authorized completion; previous attempts remain immutable.
    marker = OUT/'mechanism-completion-started.json'
    with marker.open('x') as handle:
        json.dump({'state':'reserved','remaining_nodes':manifest['remaining_nodes']},handle)
    progress_path = OUT/'mechanism-completion-progress.json'
    env = dict(os.environ,PYTHONPATH=str(ROOT/'src'),PYTHONHASHSEED='26',OMP_NUM_THREADS='2',
               OPENBLAS_NUM_THREADS='1',MKL_NUM_THREADS='1',TOKENIZERS_PARALLELISM='false',
               CATEGORY_MECHANISM_PROGRESS=str(progress_path),
               CATEGORY_MECHANISM_RESUME_MANIFEST=str(ROOT/PLAN['resume_manifest']))
    status = {'state':'running','attempt':'fixed13_completion','seed':26,
              'limits':{k:v for k,v in PLAN.items() if k!='cases'},
              'reused_passed_nodes':manifest['passed_nodes'],'remaining_nodes':manifest['remaining_nodes'],
              'prior_invocations_started':64,'prior_seconds':manifest['seconds'],
              'prior_attempt_reasons':['aggregate_timeout','byte_fixture_construction'],
              'targeted_byte_pytest_seconds':.37,'source_hashes_revalidated':True}
    path = OUT/'mechanism-status.json'
    def save():
        path.write_text(json.dumps(status,indent=2)+'\n')
    save()
    command = [sys.executable,'-m','pytest','-p','tests.category_mechanism_plugin',
               *manifest['remaining_nodes'],'-q','-s','--tb=short','--maxfail=1']
    result = run_bounded(command,seconds=PLAN['aggregate_seconds'],log_path=OUT/'mechanism-completion.log',
        env=env,log_bytes=PLAN['log_bytes_max'],progress_path=progress_path,
        invocation_seconds=PLAN['invocation_seconds'],collection_seconds=PLAN['collection_seconds'])
    progress = json.loads(progress_path.read_text()) if progress_path.exists() else {}
    invocations = progress.get('invocations',[])
    active = progress.get('active')
    started_count = len(invocations) + bool(active)
    successful = [row['node'] for row in invocations if row['passed']]
    complete = (result['returncode'] == 0 and not result['timed_out'] and
                successful == manifest['remaining_nodes'] and progress.get('exitstatus') == 0)
    status.update(state='passed_split_evidence' if complete else 'failed', result=result,
        reason=None if complete else result['timeout_reason'] or 'assertion_or_session_failure',
        invocations=invocations,active_interrupted=active,
        cumulative_invocations_started=manifest['invocations_started']+started_count,
        combined_passed_nodes=manifest['passed_nodes']+successful,
        seconds=result['seconds'],combined_attempt_seconds=round(manifest['seconds']+result['seconds'],3),
        split_evidence_note='First attempt aggregate-limited, second found byte fixture issue;59prior+3targeted passes reused; only13remaining run. Not a clean75-case single run.')
    save()
    return 0 if complete else 1


if __name__ == '__main__':
    raise SystemExit(main())
