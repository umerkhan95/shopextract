"""Pilot source/transport/binding/snapshot acceptance; no production fakes."""
from copy import deepcopy
from dataclasses import asdict
import json

import pytest
from shopextract._evidence import trust_view
from shopextract._normalize import normalize
from shopextract._portable import product_from_record,product_to_record
from shopextract.maintenance import MaintenanceStore,MaintenanceError,MaintenanceEngine
from shopextract.maintenance.profiles import FieldRule,CategoryProfile
from shopextract.tools import ToolConfig
from tests.profile_coverage_helpers import raw_product,normalized,policy,configured_goal,reconcile,NOW


def test_source_projection_keeps_label_value_evidence_and_default_unchanged():
    raw=raw_product()
    assert normalize(raw).attributes=={}
    product=normalized(raw)
    assert product.attributes['capacity']=={'value':'250 L','semantic':'total_volume'}
    assert product.attributes['model']=='FX250'
    state=trust_view(product,product.evidence_contract)['/attributes/capacity']
    assert state['state']=='observed'
    ids=set(state['evidence_ids'])
    pointers={e.retained_data['source_pointer'] for e in product.evidence_contract.evidence if e.evidence_id in ids}
    assert {'/additionalProperty/0/name','/additionalProperty/0/value'}<=pointers
    record=product_to_record(product)
    assert product_to_record(product_from_record(json.loads(json.dumps(record))))==record


@pytest.mark.parametrize('value,semantic',[('250 L','total_volume'),(0,'total_volume'),(False,'total_volume'),(None,'total_volume'),('','total_volume'),('250 L','gross_volume'),('60 cm','package_width')])
def test_finite_unknown_wrapper_survives_real_portable(value,semantic):
    raw=raw_product(attributes={'capacity':{'value':value,'semantic':semantic}})
    product=normalize(raw)
    record=product_to_record(product)
    assert product_from_record(record).attributes['capacity']=={'value':value,'semantic':semantic}


@pytest.mark.parametrize('wrapper',[{'value':[],'semantic':'total_volume'},{'value':'250 L','semantic':7},{'value':'250 L','semantic':'total_volume','extra':True}])
def test_malformed_wrapper_transport_stays_rejected(wrapper):
    with pytest.raises(ValueError):product_to_record(normalize(raw_product(attributes={'capacity':wrapper})))


@pytest.mark.parametrize('properties',[
 [{'name':'Capacity','value':'250 L'}],
 [{'name':'Total capacity','propertyID':'Net capacity','value':'250 L'}],
 [{'name':'Total capacity','value':'250 L'},{'name':'Total capacity','value':'300 L'}],
])
def test_ambiguous_semantic_sources_never_create_observed_quantity(properties):
    product=normalized(raw_product(additionalProperty=properties))
    assert trust_view(product,product.evidence_contract).get('/attributes/capacity',{}).get('state')!='observed'


@pytest.mark.asyncio
async def test_changed_capacity_remains_identity_variant_review(tmp_path):
    result=await reconcile(tmp_path/'j.db',raw=raw_product(additionalProperty=[{'name':'Total capacity','value':'300 L'}]),config=policy())
    finding,=result['findings']
    assert finding['comparison']=='different' and finding['status']=='needs_review'
    assert finding['reason']=='identity_unresolved'
    assert any('capacity:' in value for value in finding['match_reason']['conflicts'])
    coverage=result['profile_coverage']['products'][0]
    assert coverage['checked_fields']==['attributes/capacity']


@pytest.mark.asyncio
@pytest.mark.parametrize('value,semantic,reason,state',[(0,'total_volume','unit_missing','value'),(False,'total_volume','invalid_type','value'),(None,'total_volume','null','null'),('250 L','net_volume','semantic_mismatch','value')])
async def test_invalid_captured_fact_is_unknown_not_wholejob_failure(tmp_path,value,semantic,reason,state):
    raw=raw_product(additionalProperty=[],attributes={'capacity':{'value':value,'semantic':semantic}})
    result=await reconcile(tmp_path/'j.db',raw=raw,config=policy())
    finding,=result['findings']
    assert finding['comparison']=='unknown' and finding['status']=='needs_review'
    assert finding['input_reasons']['after']==reason and finding['input_states']['after']==state
    assert result['profile_coverage']['products'][0]['checked_fields']==[]


@pytest.mark.asyncio
@pytest.mark.parametrize('kind',['no_config','no_binding','wrong_binding','boots_label','gtin_conflict','selection_absent'])
async def test_new_profile_never_bypasses_binding_or_identity(tmp_path,kind):
    config=None if kind=='no_config' else policy(binding=kind!='no_binding',bound_profile='footwear-v1' if kind=='wrong_binding' else 'refrigerator-v1')
    raw=raw_product(**({'category':'Boots'} if kind=='boots_label' else {'gtin13':'9780140328721'} if kind=='gtin_conflict' else {}))
    result=await reconcile(tmp_path/'j.db',raw=raw,config=config,goal=configured_goal(profiles={}) if kind=='selection_absent' else None)
    finding,=result['findings'];assert finding['status']=='needs_review'
    if kind=='no_config':assert finding['reason']=='category_policy_missing'
    assert finding['status']!='proposed_correction'


@pytest.mark.asyncio
async def test_persisted_missing_rule_is_review_only_even_with_exact_support(tmp_path):
    # Labelled corrupt/legacy state: public create still rejects this field.
    store=MaintenanceStore(tmp_path/'j.db');key=store.create(configured_goal(fields=('title',),profiles={'S1':'generic-v1'}))
    store.acquire();store.begin(key,now=NOW)
    data=store.goal(key);data['fields']=['attributes/material'];data['baseline'][0]['attributes']={'material':'steel'}
    store._connect().execute('UPDATE jobs SET goal=? WHERE id=?',(json.dumps(data),key))
    raw=raw_product(attributes={'material':'steel'});product=normalize(raw)
    engine=MaintenanceEngine(store,tool_config=ToolConfig(),utc_now=lambda:NOW)
    try:
        await engine._reconcile(key,store.goal(key),[product_to_record(product)])
        finding,=store.report(key)['findings']
        assert finding['comparison']=='unknown' and finding['status']=='needs_review' and finding['reason']=='unsupported_field'
    finally:await engine.close();store.close()


def test_unit_policy_snapshot_mismatch_and_unrelated_registry_addition(tmp_path):
    store=MaintenanceStore(tmp_path/'j.db');key=store.create(configured_goal());snapshot=store.status(key)['profile_definitions'];store.close()
    store=MaintenanceStore(tmp_path/'j.db',custom_profiles={'other-v1':CategoryProfile('other-v1',{'title':FieldRule('text','comparable')})})
    try:
        store.validate_profiles(key);assert store.status(key)['profile_definitions']==snapshot
        store.registry['refrigerator-v1']['fields']['attributes/capacity']['normalization']='length_width_m_v1'
        with pytest.raises(MaintenanceError,match='profile_mismatch'):store.validate_profiles(key)
        assert store.status(key)['profile_definitions']==snapshot
    finally:store.close()


@pytest.mark.asyncio
async def test_trusted_profile_selection_propagates_to_real_source_runtime(tmp_path):
    import httpx
    from tests.profile_coverage_helpers import ORIGIN
    requests=[];config=policy();store=MaintenanceStore(tmp_path/'j.db',category_config=config)
    async def resolver(host,context):return ['93.184.216.34']
    def wire(request):
        requests.append(str(request.url))
        payload={k:v for k,v in raw_product().items() if not k.startswith('_')}
        return httpx.Response(200,text='<script type="application/ld+json">'+json.dumps(payload)+'</script>',headers={'content-type':'text/html'})
    engine=MaintenanceEngine(store,tool_config=ToolConfig(allowed_origins=(ORIGIN,)),category_config=config,resolver=resolver,wire_transport=httpx.MockTransport(wire),utc_now=lambda:NOW)
    try:
        job=store.create(configured_goal());result=await engine.run(job)
        finding,=result['findings']
        assert finding['after']=={'value':'250 L','semantic':'total_volume'}
        assert finding['supplier_support']['state']=='observed' and finding['comparison']=='equal'
        count=len(requests);replayed=await engine.resume(job)
        assert replayed['findings']==result['findings'] and len(requests)==count
    finally:await engine.close();store.close()


@pytest.mark.asyncio
async def test_missing_quantity_retains_missing_not_null_after_engine(tmp_path):
    result=await reconcile(tmp_path/'j.db',raw=raw_product(additionalProperty=[]),config=policy())
    finding,=result['findings']
    assert finding['comparison']=='unknown' and finding['input_states']['after']=='missing'
    assert result['profile_coverage']['products'][0]['unavailable_fields']==['attributes/capacity']


def test_public_goal_still_rejects_field_absent_from_selected_profile(tmp_path):
    store=MaintenanceStore(tmp_path/'j.db')
    try:
        with pytest.raises(MaintenanceError,match='invalid_argument'):
            store.create(configured_goal(fields=('attributes/not_in_policy',),profiles={'S1':'generic-v1'}))
    finally:store.close()


@pytest.mark.asyncio
@pytest.mark.parametrize('value,state',[(None,'null'),('','empty'),('   ','empty')])
async def test_source_empty_state_does_not_become_supported_null(tmp_path,value,state):
    raw=raw_product(additionalProperty=[{'name':'Total capacity','value':value}])
    result=await reconcile(tmp_path/'j.db',raw=raw,config=policy())
    finding,=result['findings']
    assert finding['comparison']=='unknown' and finding['status']=='needs_review'
    assert finding['input_states']['after']==state
    if value is None or value=='':assert finding['supplier_support']['state']!='observed'
    assert result['profile_coverage']['products'][0]['unavailable_fields']==['attributes/capacity']


def test_quantity_wrapper_order_does_not_create_matcher_conflict():
    from shopextract.compare.identity_match import normalized_attributes
    one={'attributes':{'capacity':{'value':'250 L','semantic':'total_volume'}}}
    two={'attributes':{'capacity':{'semantic':'total_volume','value':'250 L'}}}
    assert normalized_attributes(one)==normalized_attributes(two)
    assert normalized_attributes({'attributes':{'ram':'8 GB','color':'Blue'}})=={'memory':'8gb','color':'blue'}
    assert normalized_attributes({'attributes':{'capacity':{'extra':1}}})['capacity']=="{'extra':1}"
    three={'attributes':{'capacity':{'value':'300 L','semantic':'total_volume'}}}
    assert normalized_attributes(one)!=normalized_attributes(three)


def test_variant_quantity_wrapper_order_is_deterministic():
    from shopextract.compare.identity_match import normalized_attributes
    one={'variants':[{'attributes':{'width':{'value':'60 cm','semantic':'product_width'}}}]}
    two={'variants':[{'attributes':{'width':{'semantic':'product_width','value':'60 cm'}}}]}
    assert normalized_attributes(one)==normalized_attributes(two)


@pytest.mark.asyncio
async def test_completed_resume_rejects_changed_selected_policy_before_source(tmp_path):
    store=MaintenanceStore(tmp_path/'j.db');job=store.create(configured_goal())
    store.acquire();store.begin(job,now=NOW);store.finish(job,'completed');store.release()
    before=store.status(job);report=store.report(job)
    engine=MaintenanceEngine(store,tool_config=ToolConfig(),utc_now=lambda:NOW)
    store.registry['refrigerator-v1']['fields']['attributes/capacity']['normalization']='length_width_m_v1'
    try:
        with pytest.raises(MaintenanceError,match='profile_mismatch'):await engine.resume(job)
        assert store.status(job)==before and store.report(job)==report
        assert store.steps(job)==[]
    finally:await engine.close();store.close()
