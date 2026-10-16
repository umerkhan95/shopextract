"""Pure driver-state regression. No mechanism/SDK/network/worker execution."""
import importlib.util
import json
from pathlib import Path
import pytest

path=Path(__file__).resolve().parents[1]/'artifacts/agent-tool-api-mcp/run-mechanisms.py'
spec=importlib.util.spec_from_file_location('mechanism_driver_state',path)
driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)


def synthetic_receipt():
    cases=[{'id':f'M{i:02d}','node':f'synthetic::{i}'} for i in range(1,49)]
    manifest={'cases':cases,'additional_rss_target_bytes':100,'max_processes':5}
    progress={'cases':{},'elapsed_seconds':2.25,'fixture_bytes':123,'revision':'unchanged'}
    # Tiny injected runner boundary; it never calls pytest or production code.
    for case in cases:
        exit_code=0
        progress['cases'][case['id']]={'node':case['node'],'status':'passed' if exit_code==0 else 'failed','exit':exit_code}
    return progress,manifest


@pytest.mark.parametrize('rss,processes,reason',[(101,5,'rss_limit'),(100,6,'process_limit')])
def test_final_overflow_persisted_before_success_or_resume(tmp_path,rss,processes,reason):
    progress,manifest=synthetic_receipt()
    assert driver.successful(progress,manifest)
    assert driver.apply_resource_observations(progress,manifest,'M48',rss,processes)
    receipt=tmp_path/'receipt.json';receipt.write_text(json.dumps(progress))
    saved=json.loads(receipt.read_text())
    assert saved['cases']['M48']['status']=='failed_resource'
    assert saved['cases']['M48']['exit']=='resource_limit'
    assert saved['cases']['M48']['resource_reasons']==[reason]
    assert saved['resource_failures']['M48']['reasons']==[reason]
    assert not driver.successful(saved,manifest)
    assert driver.resource_resume_blocked(saved,manifest)
    assert saved['elapsed_seconds']==2.25 and saved['fixture_bytes']==123


def test_legacy_violating_passes_block_without_resetting_budget(tmp_path):
    progress,manifest=synthetic_receipt()
    progress.update(peak_process_count=6,peak_additional_rss_bytes=10)
    assert all(row['status']=='passed' for row in progress['cases'].values())
    assert driver.resource_resume_blocked(progress,manifest)
    receipt=tmp_path/'receipt.json';receipt.write_text(json.dumps(progress))
    saved=json.loads(receipt.read_text())
    assert saved['resource_failures']['__saved_receipt__']['reasons']==['process_limit']
    assert not driver.successful(saved,manifest)
    assert saved['elapsed_seconds']==2.25 and saved['fixture_bytes']==123 and saved['revision']=='unchanged'


def test_success_requires_all_exact_nodes_and_zero_resource_history():
    progress,manifest=synthetic_receipt()
    assert driver.successful(progress,manifest)
    progress['resource_failures']={'M01':{'reasons':['rss_limit']}}
    assert not driver.successful(progress,manifest)
    progress['resource_failures'].clear();progress['cases']['M48']['node']='different-node'
    assert not driver.successful(progress,manifest)
    progress['cases'].pop('M48')
    assert not driver.successful(progress,manifest)
