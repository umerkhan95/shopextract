"""Seed-25 sequential real-path verification; invoke as a module, never import-run."""
import asyncio
from dataclasses import replace
from datetime import timedelta
import json
import os
from pathlib import Path
import resource
import sys
import tempfile
import time
import httpx

from shopextract.maintenance import AdvisorBound, AdvisorResult, AdvisorUsage, Budgets, MaintenanceError
from shopextract.maintenance.engine import MaintenanceEngine, _Accounting
from shopextract.maintenance.store import MaintenanceStore, digest
from tests.test_maintenance_acceptance import Harness, goal, NOW, ORIGIN
from tests.test_maintenance_workflow import (test_cancel_active_wire_releases_owner_before_ack,
    test_cache_exact_expiry_misses_but_report_evidence_survives_eviction,
    test_same_store_second_engine_cannot_release_active_owner,
    test_unknown_retry_is_explicit_new_charge_and_resolves_pending_comparison,
    test_category_specs_remain_visible_without_overriding_matcher)
from tests.test_maintenance_advisor import (test_retry_cancellation_before_publication_keeps_prior_advisory,
    test_retry_publication_failure_preserves_previous_composition_and_charge)
from tests.test_maintenance_review_repairs import test_advisor_retry_preserves_real_native_partial_source_coverage


def gtin(index):
    digits = f'4006381{index:05d}'
    total = sum(int(char) * (3 if i % 2 == 0 else 1) for i, char in enumerate(reversed(digits)))
    return digits + str((10 - total % 10) % 10)


def products(count, mixed=True):
    baseline, source = [], []
    for i in range(count):
        sku, title, after = f'S{i}', f'Sensor model Z{i}', f'Operating temperature: 0–45 C ({i})'
        before = after if not mixed or i < 80 else f'Operating temperature: 0–40 C ({i})'
        left = dict(external_id=sku, sku=sku, title=title, gtin=gtin(i), vendor='Acme',
                    description=before, price='10', currency='EUR', supplier_id=ORIGIN)
        right = {'@context':'https://schema.org','@type':'Product','name':title,'sku':sku,
                 'gtin13':gtin(i),'brand':{'name':'Acme'},'description':after,
                 'offers':{'price':'10','priceCurrency':'EUR'}}
        if mixed and i >= 95:
            left['description'] = after
            left['attributes'], right['attributes'] = {'ram':'8 GB'}, {'ram':'16 GB'}
        elif not mixed and i >= 95:
            left['attributes'], right['attributes'] = {'ram':'16 GB'}, {'ram':'16 GB'}
        baseline.append(left)
        source.append(right)
    return baseline, source


class Spy:
    def __init__(self): self.calls = []
    def bound(self, payload): return AdvisorBound(16, 16, 1, 'fixture-v1', 'fixture-price-v1')
    async def investigate(self, payload, *, reservation, timeout):
        self.calls.append(payload['product_key'])
        return AdvisorResult('fixture-v1', 'fixture-price-v1', {'reason':'Unresolved variant'}, (), AdvisorUsage(16,1,1))


async def batch(path, count, mixed, enabled):
    left, right = products(count, mixed)
    if count == 3:
        left[2]['description'] = 'Old temperature specification'
    body = '<script type="application/ld+json">' + json.dumps(right) + '</script>'
    spy = Spy()
    h = Harness(path / 'jobs.db', investigator=spy if enabled else None)
    h.engine.wire_transport = httpx.MockTransport(lambda request: httpx.Response(200, text=body))
    configured = goal(baseline=tuple(left), profiles={record['external_id']:'hardware-v1' for record in left},
                      budgets=Budgets(products=max(count, 3), tokens=160 if enabled else 0, cost_micros=5 if enabled else 0))
    _, report = await h.run(configured)
    counts = {status:sum(f['status']==status for f in report['findings'])
              for status in ('unchanged','proposed_correction','needs_review')}
    expected = {'unchanged':2,'proposed_correction':1,'needs_review':0} if count == 3 else (
        {'unchanged':80,'proposed_correction':15,'needs_review':5} if mixed else
        {'unchanged':100,'proposed_correction':0,'needs_review':0})
    assert counts == expected, (counts, expected)
    assert spy.calls == ([f'S{i}' for i in range(95,100)] if enabled and mixed else []), spy.calls
    if not enabled:
        assert report['usage']['tokens'] == 0
    return {'counts':counts, 'advisor_calls':len(spy.calls), 'usage':report['usage']}


async def crash_case(path, event):
    class Crash(BaseException): pass
    def inject(actual, payload):
        if actual == event: raise Crash()
    h = Harness(path / 'jobs.db', failure_hook=inject)
    key = h.store.create(goal())
    try:
        await h.engine.run(key)
        raise AssertionError('missing crash boundary')
    except Crash: pass
    sent = len(h.requests)
    reopened = Harness(path / 'jobs.db')
    report = await reopened.engine.resume(key)
    assert reopened.requests == []
    assert report['usage']['requests'] == sent or event in {'intent_committed','before_dispatch'}
    if event == 'after_checkpoint':
        assert report['findings'][0]['status'] == 'proposed_correction'
    else:
        assert report['state'] == 'partial'
    return {'window':event,'sent':sent,'state':report['state']}


def budget_case(path, dimension, edge):
    limits = {} if dimension == 'deadline' else {dimension: 1}
    h = MaintenanceStore(path / 'jobs.db')
    key = h.create(goal(budgets=replace(Budgets(), **limits)))
    h.acquire(); h.begin(key, now=NOW); h.add_step(key,'boundary','test')
    demand = edge
    denied = False
    try:
        if dimension in {'requests','tokens','cost_micros'}:
            h.reserve(key,'boundary',{dimension:demand},now=NOW)
        elif dimension == 'evidence_bytes':
            # Exact encoded payload is 20 bytes. Request caps are set to 1 here;
            # byte family is tested against explicitly configured serialized cap.
            value = {'evidence_id':'e'}
            size = len(json.dumps(value,separators=(',',':')).encode()) + len('null')
            h.close()
            h = MaintenanceStore(path / 'byte.db')
            key = h.create(goal(budgets=Budgets(evidence_bytes=size+demand-1)))
            h.acquire(); h.begin(key,now=NOW); h.add_step(key,'boundary','test')
            h.checkpoint(key,'boundary',None,evidence=[value])
        elif dimension == 'report_bytes':
            value = {'finding_id':'f'}
            size = len(json.dumps(value,separators=(',',':')).encode())
            h.close(); h=MaintenanceStore(path/'report.db')
            key=h.create(goal(budgets=Budgets(report_bytes=size+demand-1)))
            h.acquire();h.begin(key,now=NOW);h.add_step(key,'boundary','test')
            h.checkpoint(key,'boundary',None,findings=[value])
        elif dimension == 'deadline':
            # One second before / at / after fixed persisted deadline.
            h.reserve(key,'boundary',{'requests':0},now=NOW+timedelta(seconds=59+demand))
    except MaintenanceError:
        denied=True
    finally: h.close()
    expected = demand > 1 if dimension in {'requests','tokens','cost_micros'} else (
        demand == 0 if dimension in {'evidence_bytes','report_bytes'} else demand >= 1)
    assert denied == expected, (dimension, edge, denied, expected)
    return {'dimension':dimension,'edge':edge,'denied':denied}


async def checkpoint_reuse(path, *, mutant=False):
    path.mkdir(parents=True,exist_ok=True)
    class Crash(BaseException): pass
    h=Harness(path/'jobs.db')
    configured=goal(freshness_seconds=1)
    # Deliberate failure at the boundary before comparison, after the actual
    # source checkpoint AND cache commit, before overall job completion.
    async def crash_before_comparison(*args,**kwargs): raise Crash()
    h.engine._reconcile=crash_before_comparison
    key=h.store.create(configured)
    try:
        await h.engine.run(key)
        raise AssertionError('missing pre-comparison fault')
    except Crash: pass
    assert h.store.status(key)['state']=='running'
    reopened=Harness(path/'jobs.db')
    reopened.engine.utc_now=lambda: NOW+timedelta(seconds=2)
    original=MaintenanceEngine._source
    if mutant:
        async def broken(self,job,goal,mode,url,maximum,**kwargs):
            if mode=='extract':
                with self.store._transaction() as db:
                    db.execute("UPDATE steps SET state='pending' WHERE job=? AND kind='extract'",(job,))
            return await original(self,job,goal,mode,url,maximum,**kwargs)
        MaintenanceEngine._source=broken
    try:
        await reopened.engine.resume(key)
        assert reopened.requests==[],'checkpoint detector found repeated external work'
    finally: MaintenanceEngine._source=original


async def mutation_case(path, kind):
    detected=False
    if kind=='budget':
        original=_Accounting.before_request
        _Accounting.before_request=lambda self,method,url: None
        try:
            h=Harness(path/'jobs.db'); await h.run(goal(budgets=Budgets(requests=0)))
            assert h.requests==[],'budget detector found uncharged external work'
        except AssertionError: detected=True
        finally: _Accounting.before_request=original
    else:
        try: await checkpoint_reuse(path,mutant=True)
        except AssertionError: detected=True
    assert detected,'critical assertion did not detect temporary mutation'
    return {'mutation':kind,'detected':True,'restored':True}


def case_definitions():
    cases=[('mixed-100-disabled',15),('mixed-100-enabled',15),('exact-100',15)]
    cases += [(f'crash-{window}-{cycle}',10) for window in
        ('intent_committed','before_dispatch','after_dispatch','before_checkpoint','after_checkpoint') for cycle in range(4)]
    cases += [(f'budget-{dimension}-{edge}',5) for dimension in
        ('requests','tokens','cost_micros','evidence_bytes','report_bytes','deadline') for edge in (0,1,2)]
    cases += [(f'interaction-{i}',5) for i in range(8)]
    cases += [(f'category-{i}',5) for i in range(8)]
    cases += [('mutation-budget',10),('mutation-checkpoint',10)]
    return cases


async def execute_case(name,path):
    from tests.test_maintenance_remaining_edges import (test_cancel_during_known_retry_delay_prevents_second_wire,
        test_cache_hit_revalidates_policy_without_touching_saved_report,
        test_custom_color_role_and_footwear_role_remain_distinct,
        test_missing_footwear_size_system_is_unknown_even_equal_sizes)
    if name.startswith('mixed-100') or name=='exact-100':
        return await batch(path,100,name!='exact-100',name!='mixed-100-disabled')
    if name.startswith('crash-'):
        return await crash_case(path,name[len('crash-'):].rsplit('-',1)[0])
    if name.startswith('budget-'):
        dimension,edge=name[len('budget-'):].rsplit('-',1)
        return budget_case(path,dimension,int(edge))
    if name.startswith('interaction-'):
        checks=[test_cancel_during_known_retry_delay_prevents_second_wire,
            test_retry_cancellation_before_publication_keeps_prior_advisory,
            test_advisor_retry_preserves_real_native_partial_source_coverage,
            checkpoint_reuse,test_cache_hit_revalidates_policy_without_touching_saved_report,
            test_unknown_retry_is_explicit_new_charge_and_resolves_pending_comparison,
            test_retry_publication_failure_preserves_previous_composition_and_charge,
            test_cache_exact_expiry_misses_but_report_evidence_survives_eviction]
        return await checks[int(name.rsplit('-',1)[1])](path)
    if name.startswith('category-'):
        cases=[('hardware-v1','attributes/ram','8 GB','16 GB','different'),
            ('hardware-v1','attributes/material','steel','aluminium','different'),
            ('footwear-v1','attributes/size','9','10','different'),
            ('footwear-v1','attributes/material','leather','textile','different'),
            ('hardware-v1','attributes/weight','1000 g','1 kg','equal'),
            ('footwear-v1','attributes/weight','1000 g','1 kg','equal')]
        index=int(name.rsplit('-',1)[1])
        if index<6:return await test_category_specs_remain_visible_without_overriding_matcher(path,*cases[index])
        return await (test_custom_color_role_and_footwear_role_remain_distinct if index==6
                      else test_missing_footwear_size_system_is_unknown_even_equal_sizes)(path)
    return await mutation_case(path,name[len('mutation-'):])


def worker(name,receipt):
    started=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='maintenance-seed25-') as temporary:
        value=asyncio.run(execute_case(name,Path(temporary)))
    rss=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    rss_mib=rss/(1024*1024) if sys.platform=='darwin' else rss/1024
    assert rss_mib<=256,('rss',rss_mib)
    receipt.write_text(json.dumps({'case':name,'state':'passed','seconds':round(time.monotonic()-started,3),
        'rss_mib':round(rss_mib,2),'result':value},indent=2))


def main(out):
    from tests.maintenance_process_guard import run_group
    out.mkdir(parents=True,exist_ok=True)
    history=out/'progress.json'
    results=json.loads(history.read_text()) if history.exists() else []
    # Charge all recorded worker wall time, including failed workers. Reserve
    # one additional second for prior uninstrumented parent startup/dispatch.
    prior_seconds=sum(record.get('execution',{}).get('seconds',0) for record in results)
    startup_reserve=1 if results else 0
    charged=float(os.environ.get('MAINTENANCE_DRIVER_PRIOR_CHARGED',prior_seconds+startup_reserve))
    started=float(os.environ.get("MAINTENANCE_DRIVER_STARTED",time.monotonic()))-charged
    completed={record['case'] for record in results if record['state'] in {'passed','reused'}}
    config={'seed':25,'driver_seconds':180,'large_batch_seconds':15,'case_seconds':5,'crash_seconds':10,
            'kill_reap_grace_seconds':1,'rss_limit_mib':256,'workers':1,'input_bytes':256*1024,
            'evidence_bytes':16*1024*1024,'smoke_reused':'../stress-second-timeout/smoke.json',
            'prior_recorded_worker_seconds':prior_seconds,'prior_parent_startup_reserve_seconds':startup_reserve,'prior_charged_seconds':charged}
    (out/'config.json').write_text(json.dumps(config,indent=2))
    reusable={
        'interaction-1':('advisor-publication-policy-green.log','test_retry_cancellation_before_publication_keeps_prior_advisory'),
        'interaction-2':('completion-retry-green.log','test_advisor_retry_preserves_real_native_partial_source_coverage'),
        'interaction-3':('stress-prerequisites.log','test_checkpoint_mutation_fixture_reaches_real_resume'),
        'interaction-5':('source-retry-discovery.log','test_unknown_retry_is_explicit_new_charge_and_resolves_pending_comparison'),
        'interaction-6':('completion-retry-green.log','test_retry_publication_failure_preserves_previous_composition_and_charge'),
        'interaction-7':('workflow-mechanisms.log','test_cache_exact_expiry_misses_but_report_evidence_survives_eviction')}
    reusable.update({f'category-{i}':('slice-b-refinements.log',f'test_category_specs_remain_visible_without_overriding_matcher[{i}]') for i in range(6)})
    for name,limit in case_definitions():
        if name in completed:continue
        if name in reusable:
            log,check=reusable[name]
            record={'case':name,'state':'reused','saved_log':'../'+log,'check':check,
                'reason':'Exact previously executed real-path invariant; changed matcher dictionaries independently equivalent'}
            results.append(record);history.write_text(json.dumps(results,indent=2));continue
        attempt=1+sum(record['case']==name for record in results)
        remaining=180-(time.monotonic()-started)
        if remaining<=1:raise TimeoutError('global180s limit exhausted before next case')
        receipt=out/(name+f'-attempt{attempt}.json')
        with (out/(name+f'-attempt{attempt}.log')).open('w') as log:
            execution=run_group([sys.executable,'-m','tests.maintenance_stress_driver','--case',name,str(receipt)],
                timeout=min(limit,remaining-1),stdout=log,stderr=log)
        if execution['timed_out'] or execution['returncode']!=0:
            record={'case':name,'state':'failed','execution':execution}
        else:
            record=json.loads(receipt.read_text());record['execution']=execution
        results.append(record);(out/'progress.json').write_text(json.dumps(results,indent=2))
        if record['state']!='passed':raise AssertionError('first failure: '+name)
    elapsed=time.monotonic()-started
    assert elapsed<=180,elapsed
    summary={'state':'passed','recorded_attempts':len(results),'executed_cases':len({r['case'] for r in results if r['state']=='passed'}),'elapsed_seconds':round(elapsed,3),
             'reused_smoke_cases':1,'reused_cases':sum(r['state']=='reused' for r in results),'configuration':config}
    (out/'summary.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--case':worker(sys.argv[2],Path(sys.argv[3]))
    else:main(Path(sys.argv[1]))
