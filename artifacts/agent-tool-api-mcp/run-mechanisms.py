"""Sequential resumable driver; requires explicit reviewed invocation.

Run only after independent fixture/coverage approval is recorded:
PYTHONPATH=src:. .venv/bin/python artifacts/agent-tool-api-mcp/run-mechanisms.py --reviewed
"""
import argparse
import contextlib
import hashlib
import json
import os
from pathlib import Path
import signal
import sys
import threading
import time


def resource_reasons(progress, manifest):
    reasons=[]
    rss=progress.get('peak_additional_rss_bytes')
    processes=progress.get('peak_process_count')
    if rss is not None and rss>manifest['additional_rss_target_bytes']:reasons.append('rss_limit')
    if processes is not None and processes>manifest['max_processes']:reasons.append('process_limit')
    return reasons


def apply_resource_observations(progress, manifest, case_id, rss=None, processes=None):
    """Finalize resource verdict before persistence; retain failures across resume."""
    if rss is not None:
        progress['peak_additional_rss_bytes']=max(progress.get('peak_additional_rss_bytes') or 0,rss)
    if processes is not None:
        progress['peak_process_count']=max(progress.get('peak_process_count') or 0,processes)
    reasons=resource_reasons(progress,manifest)
    if reasons:
        key=case_id or '__saved_receipt__'
        progress.setdefault('resource_failures',{})[key]={
            'reasons':reasons,'peak_additional_rss_bytes':progress.get('peak_additional_rss_bytes'),
            'peak_process_count':progress.get('peak_process_count')}
        if case_id in progress.get('cases',{}):
            progress['cases'][case_id].update(status='failed_resource',exit='resource_limit',resource_reasons=reasons)
    return bool(progress.get('resource_failures'))


def resource_resume_blocked(progress, manifest):
    # A legacy global overflow cannot be attributed honestly to an individual row.
    # Persist an explicit barrier and stop instead of skipping its old passed rows.
    return apply_resource_observations(progress,manifest,None)


def successful(progress, manifest):
    if progress.get('resource_failures') or resource_reasons(progress,manifest):return False
    return all(progress.get('cases',{}).get(case['id'],{}).get('status')=='passed'
               and progress['cases'][case['id']].get('node')==case['node']
               for case in manifest['cases'])


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--reviewed',action='store_true');parser.add_argument('--reviewed-m11-continuation',action='store_true');args=parser.parse_args()
    if not args.reviewed:raise SystemExit('Independent fixture/coverage review is required before execution')
    root=Path(__file__).resolve().parents[2];os.chdir(root)
    manifest_path=root/'artifacts/agent-tool-api-mcp/mechanism-inventory.json'
    manifest=json.loads(manifest_path.read_text())
    receipt=root/'artifacts/agent-tool-api-mcp/mechanism-progress.json'
    logfile=root/'artifacts/agent-tool-api-mcp/mechanism-run.log'
    if args.reviewed_m11_continuation:
        receipt=root/'artifacts/agent-tool-api-mcp/mechanism-continuation.json'
        logfile=root/'artifacts/agent-tool-api-mcp/mechanism-continuation.log'
    # Conservative complete production/test source identity, exact selected input files,
    # driver/build/accounting helpers and dependency versions. No glob can omit a
    # changed parser/normalizer/reliable/evidence algorithm and reuse stale results.
    import importlib.metadata
    paths=set((root/'src').rglob('*.py')) | set((root/'tests').rglob('*.py'))
    paths |= set((root/'artifacts/agent-tool-api-mcp').glob('*.py'))
    paths |= {manifest_path,root/'pyproject.toml',root/'.github/workflows/test.yml'}
    paths |= {root/item['path'] for item in manifest['static_fixture_inputs']}
    digest=hashlib.sha256()
    identity=[]
    for path in sorted(paths):
        data=path.read_bytes();name=str(path.relative_to(root))
        digest.update(json.dumps([name,len(data)]).encode());digest.update(data)
        identity.append({'path':name,'sha256':hashlib.sha256(data).hexdigest()})
    environment={'python':sys.version,'platform':sys.platform}
    for name in ('pytest','pytest-asyncio','mcp','httpx','httpcore','anyio','jsonschema'):
        try:environment[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:environment[name]=None
    environment['installed_distributions']=sorted((dist.metadata.get('Name','unknown'),dist.version) for dist in importlib.metadata.distributions())
    digest.update(json.dumps(environment,sort_keys=True).encode())
    revision=digest.hexdigest()
    progress=json.loads(receipt.read_text()) if receipt.exists() else {}
    if args.reviewed_m11_continuation:
        reviewed={
          'artifacts/agent-tool-api-mcp/mechanism-progress.json':'59163f1839c85f22cdf12ff558fca0a3a9fa2acab2304f42027392eb9c943453',
          'artifacts/agent-tool-api-mcp/validator-cache-repair.json':'e5674dc84254d546dd0089e7cc357e7f04b294d47dcfa0a1cfac45bf643d586d',
          'artifacts/agent-tool-api-mcp/m11-cache-affected.json':'ed7a95aeb0f5aac37839a80712f28110ec8aa035f284b70b42c7f1c0550abf00',
          'tests/test_agent_tool_api.py':'466c79afcdfa8d6993f6eace639c3332c8e3267d50cdb7ebb0c36ef7d61013c5',
          'tests/tool_schema_validation.py':'211ffc69d7d6d43fe6f88a6321f213b335889c0e0b83b48b6139f09bffbcd48a'}
        for name,expected in reviewed.items():
            if hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected:
                raise SystemExit('M11 carry-forward provenance changed; independent audit required')
        review_ref='reviews.md: Bounded timing/carry-forward audit after M11 (2026-10-16)'
        if progress and progress['revision']!=revision:
            raise SystemExit('Derived continuation identity changed; audit before carrying further results')
        if not progress:
            original=json.loads((root/'artifacts/agent-tool-api-mcp/mechanism-progress.json').read_text())
            audit=json.loads((root/'artifacts/agent-tool-api-mcp/validator-cache-repair.json').read_text())
            retry=json.loads((root/'artifacts/agent-tool-api-mcp/m11-cache-affected.json').read_text())
            progress=json.loads(json.dumps(original))
            progress.update(revision=revision,elapsed_seconds=audit['additive_charged_seconds'],
                fixture_bytes=audit['additive_fixture_bytes'],carry_forward_review=review_ref,
                original_receipt_sha256=reviewed['artifacts/agent-tool-api-mcp/mechanism-progress.json'])
            for key,row in progress['cases'].items():
                if key!='M11':
                    assert key in [f'M{i:02d}' for i in range(1,11)] and row['status']=='passed'
                    row['provenance']={'original_revision':original['revision'],'review':review_ref}
            failed=json.loads(json.dumps(original['cases']['M11']))
            progress['cases']['M11'].update(status='blocked_timing_after_one_repair',
                reason='Two reviewed five-second failures; no further stress retry authorized',
                observations=[failed,retry],review=review_ref)
            progress['peak_additional_rss_bytes']=max(original['peak_additional_rss_bytes'],retry['peak_additional_rss_bytes'])
            progress['peak_process_count']=max(original['peak_process_count'],retry['peak_process_count'])
            receipt.write_text(json.dumps(progress,indent=2)+'\n')
    if progress and resource_resume_blocked(progress,manifest):
        receipt.write_text(json.dumps(progress,indent=2)+'\n')
        raise SystemExit('Saved resource failure: diagnose and record a reviewed repair before resuming')
    if progress and 'fixture_bytes' not in progress:
        raise SystemExit('Legacy receipt lacks actual fixture usage; reconcile saved usage before resuming')
    if progress.get('revision')!=revision:
        old=progress
        progress={'revision':revision,'seed':24,'cases':{},'elapsed_seconds':old.get('elapsed_seconds',0),
            'fixture_bytes':old.get('fixture_bytes',0),'prior_revision':old.get('revision'),
            'prior_cases':old.get('cases',{}),'resource_failures':old.get('resource_failures',{})}
    progress['identity']=identity;progress['environment']=environment
    static=sum((root/item['path']).stat().st_size for item in manifest['static_fixture_inputs'])
    assert static==sum(item['bytes'] for item in manifest['static_fixture_inputs'])
    assert static+sum(c['max_fixture_bytes'] for c in manifest['cases'])<=manifest['fixture_bytes_limit']
    if not progress.get('static_inputs_charged'):
        progress['fixture_bytes']+=static;progress['static_input_bytes']=static;progress['static_inputs_charged']=True
    if progress['elapsed_seconds']>=manifest['driver_seconds']:raise SystemExit('Saved total driver budget exhausted')
    if progress['fixture_bytes']>=manifest['fixture_bytes_limit']:raise SystemExit('Saved total fixture-byte budget exhausted')
    from tests.tool_fixture_budget import FixtureBytesPlugin
    import pytest
    peak=[0];peak_processes=[1];baseline=0;monitor_stop=threading.Event();memory='unavailable'
    try:
        import psutil
        process=psutil.Process();baseline=process.memory_info().rss
        def monitor():
            while not monitor_stop.wait(.05):
                try:
                    children=process.children(recursive=True)
                    peak_processes[0]=max(peak_processes[0],1+len(children))
                    rss=process.memory_info().rss+sum(p.memory_info().rss for p in children)
                    peak[0]=max(peak[0],rss-baseline)
                except (psutil.NoSuchProcess,psutil.AccessDenied):pass
        watcher=threading.Thread(target=monitor,daemon=True);watcher.start();memory='measured'
    except ImportError:watcher=None
    started=time.monotonic();base_elapsed=progress['elapsed_seconds'];remaining=manifest['driver_seconds']-base_elapsed
    def alarm(signum,frame):raise TimeoutError('Bounded mechanism case deadline')
    previous=signal.signal(signal.SIGALRM,alarm)
    last_executed=None
    try:
        for case in manifest['cases']:
            if progress['cases'].get(case['id'],{}).get('status')=='passed':continue
            if (args.reviewed_m11_continuation and case['id']=='M11'
                and progress['cases'].get('M11',{}).get('status')=='blocked_timing_after_one_repair'
                and progress.get('carry_forward_review')==review_ref):continue
            if time.monotonic()-started>=remaining:break
            if logfile.exists() and logfile.stat().st_size>1024*1024:break
            if progress['fixture_bytes']+case['max_fixture_bytes']>manifest['fixture_bytes_limit']:break
            ledger=FixtureBytesPlugin()
            before=time.monotonic()
            signal.setitimer(signal.ITIMER_REAL,min(case['case_timeout_seconds'],remaining-(before-started)))
            try:
                with logfile.open('a') as log,contextlib.redirect_stdout(log),contextlib.redirect_stderr(log):
                    print('\nCASE',case['id'],case['node'],flush=True)
                    code=pytest.main([case['node'],'-q','--tb=short','-p','no:cacheprovider'],plugins=[ledger])
                status='passed' if code==0 else 'failed'
            except BaseException as error:
                status='failed';code=type(error).__name__
            finally:signal.setitimer(signal.ITIMER_REAL,0)
            elapsed=time.monotonic()-before
            actual_fixture_bytes=sum(ledger.counts.values())
            progress['fixture_bytes']+=actual_fixture_bytes
            if actual_fixture_bytes>case['max_fixture_bytes'] or progress['fixture_bytes']>manifest['fixture_bytes_limit']:
                status='failed';code='fixture_byte_limit'
            progress['cases'][case['id']]={'node':case['node'],'status':status,'exit':code,'seconds':elapsed,
                'actual_fixture_bytes':actual_fixture_bytes,'fixture_categories':dict(ledger.counts)}
            progress['elapsed_seconds']=base_elapsed+time.monotonic()-started
            progress['memory_measurement']=memory
            last_executed=case['id']
            blocked=apply_resource_observations(progress,manifest,case['id'],
                peak[0] if watcher else None,peak_processes[0] if watcher else None)
            status=progress['cases'][case['id']]['status']
            receipt.write_text(json.dumps(progress,indent=2)+'\n')
            print(case['id'],status,round(elapsed,2),flush=True)
            if status!='passed' or blocked:break
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);signal.signal(signal.SIGALRM,previous)
        monitor_stop.set()
        if watcher:watcher.join(timeout=.2)
    # Include the final monitor sample before deciding success, including the last case.
    apply_resource_observations(progress,manifest,last_executed,
        peak[0] if watcher else None,peak_processes[0] if watcher else None)
    receipt.write_text(json.dumps(progress,indent=2)+'\n')
    passed=sum(c['status']=='passed' for c in progress['cases'].values())
    print(json.dumps({'passed':passed,'planned':len(manifest['cases']),'seconds':progress['elapsed_seconds'],'remaining':len(manifest['cases'])-passed}))
    return 0 if successful(progress,manifest) else 1


if __name__=='__main__':raise SystemExit(main())
