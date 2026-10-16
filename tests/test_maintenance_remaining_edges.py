"""Distinct predesigned SC gaps: category roles, typed support and cache failure."""
import asyncio
from dataclasses import replace
from datetime import timedelta
import time
import httpx
import pytest
from shopextract.maintenance import MaintenanceStore
from shopextract.maintenance.profiles import CategoryProfile, FieldRule
from shopextract.tools import ToolConfig
from tests.test_maintenance_acceptance import Harness, goal, baseline, NOW, ORIGIN, supplier_html


@pytest.mark.asyncio
async def test_cancel_during_known_retry_delay_prevents_second_wire(tmp_path):
    h=Harness(tmp_path/'jobs.db'); sent=[]; entered=asyncio.Event(); start=time.monotonic()
    h.engine.utc_now=lambda: NOW+timedelta(seconds=time.monotonic()-start)
    def fail(request):
        sent.append(str(request.url));entered.set()
        raise httpx.ConnectError('synthetic transient')
    h.engine.wire_transport=httpx.MockTransport(fail)
    key=h.store.create(goal()); task=asyncio.create_task(h.engine.run(key))
    await asyncio.wait_for(entered.wait(),2)
    result=await h.engine.cancel(key); await task
    assert result['state']=='cancelled' and len(sent)==1
    assert h.store.report(key)['usage']['requests']==1


@pytest.mark.asyncio
async def test_cache_hit_revalidates_policy_without_touching_saved_report(tmp_path):
    h=Harness(tmp_path/'jobs.db'); key,original=await h.run(goal()); sent=len(h.requests)
    h.engine.tool_config=ToolConfig(allowed_origins=())
    _,blocked=await h.run(goal())
    assert len(h.requests)==sent and blocked['state']=='partial'
    assert blocked['stop_reason']=='permission_denied'
    assert h.store.report(key)['findings']==original['findings']


@pytest.mark.asyncio
async def test_custom_color_role_and_footwear_role_remain_distinct(tmp_path):
    profile=CategoryProfile('accessory-v1',{'attributes/color':FieldRule('text','comparable')})
    for name,expected in [('accessory-v1','comparable'),('footwear-v1','identity_variant')]:
        path=tmp_path/name;h=Harness(path/'jobs.db',attributes={'color':'white'})
        h.store=MaintenanceStore(path/'jobs.db',custom_profiles={'accessory-v1':profile});h.engine.store=h.store
        _,report=await h.run(goal(baseline=(baseline(attributes={'color':'black'}),),
            profiles={'S1':name},fields=('attributes/color',)))
        finding,=report['findings']
        assert finding['role']==expected and finding['status']=='needs_review'
        assert finding['comparison']=='different' and finding['reason']=='identity_unresolved'


@pytest.mark.asyncio
async def test_missing_footwear_size_system_is_unknown_even_equal_sizes(tmp_path):
    h=Harness(tmp_path/'jobs.db',attributes={'size':'9'})
    _,report=await h.run(goal(baseline=(baseline(attributes={'size':'9'}),),
        profiles={'S1':'footwear-v1'},fields=('attributes/size',)))
    finding,=report['findings']
    assert finding['status']=='needs_review' and finding['comparison']=='unknown'
    assert finding['reason']=='size_system_unknown'


@pytest.mark.asyncio
async def test_unique_identifier_candidate_keeps_ambiguous_variant_context(tmp_path):
    import json
    from tests.maintenance_stress_driver import products,Spy
    from shopextract.maintenance import Budgets
    left,right=products(3,False)
    left[-1]['attributes']={'ram':'8 GB'};right[-1]['attributes']={'ram':'16 GB'}
    body='<script type="application/ld+json">'+json.dumps(right)+'</script>'
    spy=Spy();h=Harness(tmp_path/'jobs.db',investigator=spy)
    h.engine.wire_transport=httpx.MockTransport(lambda request:httpx.Response(200,text=body))
    _,report=await h.run(goal(baseline=(left[-1],),profiles={'S2':'hardware-v1'},
        budgets=Budgets(tokens=32,cost_micros=1)))
    finding,=report['findings']
    assert finding['status']=='needs_review' and finding['reason']=='identity_unresolved'
    assert finding['after']==right[-1]['description'] and finding['evidence_ids']
    assert spy.calls==['S2']


@pytest.mark.asyncio
@pytest.mark.parametrize('supported', [True,False])
async def test_captured_outdated_or_unsupported_baseline_has_distinct_provenance(tmp_path,supported):
    from tests.test_maintenance_stress_prerequisites import parsed
    from shopextract._portable import product_to_record
    captured=parsed('Old captured specification')
    if not supported:captured.evidence_contract=None
    h=Harness(tmp_path/'jobs.db')
    _,report=await h.run(goal(baseline=(product_to_record(captured),),baseline_mode='captured'))
    finding,=report['findings']
    if supported:
        assert finding['status']=='proposed_correction' and finding['before']=='Old captured specification'
        assert finding['baseline_support']['kind']=='captured' and finding['baseline_support']['evidence_ids']
    else:
        assert finding['status']=='needs_review' and finding['reason']=='baseline_unsupported'
        assert finding['baseline_support']['evidence_ids']==[]


@pytest.mark.asyncio
async def test_captured_baseline_expiry_during_pause_cannot_become_correction(tmp_path):
    from tests.test_maintenance_stress_prerequisites import parsed
    from shopextract._portable import product_to_record
    h=Harness(tmp_path/'jobs.db');h.engine.utc_now=lambda:NOW+timedelta(seconds=2)
    _,report=await h.run(goal(baseline=(product_to_record(parsed('Old captured specification')),),
        baseline_mode='captured',freshness_seconds=1))
    finding,=report['findings']
    assert finding['status']=='needs_review' and finding['reason']=='baseline_unsupported'
    assert finding['baseline_support']['state']=='expired'


@pytest.mark.asyncio
async def test_escaped_attribute_path_is_literal_and_observed(tmp_path):
    name='attributes/a~1b~0c'
    configured=CategoryProfile('escaped-v1',{name:FieldRule('text','comparable')})
    h=Harness(tmp_path/'jobs.db',attributes={'a/b~c':'aluminium'})
    h.store=MaintenanceStore(tmp_path/'jobs.db',custom_profiles={'escaped-v1':configured});h.engine.store=h.store
    _,report=await h.run(goal(baseline=(baseline(attributes={'a/b~c':'steel'}),),
        profiles={'S1':'escaped-v1'},fields=(name,)))
    finding,=report['findings']
    assert finding['before']=='steel' and finding['after']=='aluminium'
    assert finding['status']=='needs_review' and finding['supplier_support']['state']=='observed'


@pytest.mark.asyncio
async def test_footwear_equal_numeral_with_different_size_system_is_unknown(tmp_path):
    h=Harness(tmp_path/'jobs.db',attributes={'size':'9','size_system':'UK'})
    _,report=await h.run(goal(baseline=(baseline(attributes={'size':'9','size_system':'US'}),),
        profiles={'S1':'footwear-v1'},fields=('attributes/size',)))
    finding,=report['findings']
    assert finding['status']=='needs_review' and finding['comparison']=='unknown'
    assert finding['before']==finding['after']=='9'


@pytest.mark.asyncio
@pytest.mark.parametrize('corruption',['scalar','version'])
async def test_cache_corruption_is_a_miss_not_a_fact_or_silent_success(tmp_path,corruption):
    import json
    h=Harness(tmp_path/'jobs.db');await h.run(goal());sent=len(h.requests)
    h.store.acquire()
    with h.store._transaction() as db:
        rows=list(db.execute('SELECT key,payload FROM cache'))
        assert rows
        for row in rows:
            value=json.loads(row['payload'])
            if corruption=='scalar':value=[]
            else:value['products'][0]['schema_version']=999
            db.execute('UPDATE cache SET payload=? WHERE key=?',(json.dumps(value),row['key']))
    h.store.release()
    _,report=await h.run(goal())
    assert len(h.requests)>sent and report['findings'][0]['status']=='proposed_correction'


@pytest.mark.asyncio
@pytest.mark.parametrize('before,expected',[(0,'unchanged'),(False,'needs_review')])
async def test_explicit_zero_price_is_not_missing_or_boolean(tmp_path,before,expected):
    import json
    raw=json.loads(supplier_html().split('>',1)[1].rsplit('<',1)[0]);raw['offers']['price']='0'
    body='<script type="application/ld+json">'+json.dumps(raw)+'</script>'
    h=Harness(tmp_path/'jobs.db');h.engine.wire_transport=httpx.MockTransport(lambda request:httpx.Response(200,text=body))
    record=baseline();record['price']=before
    _,report=await h.run(goal(baseline=(record,),fields=('price',)))
    finding,=report['findings']
    assert finding['before'] is before and finding['status']==expected
    assert finding['after']=='0'
