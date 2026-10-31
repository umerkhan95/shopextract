"""Pilot quantities: independent exact arithmetic/semantic contracts before code."""
from dataclasses import asdict
from decimal import localcontext
import json
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from shopextract.maintenance import MaintenanceError,MaintenanceStore
from shopextract.maintenance.profiles import CategoryProfile,FieldRule,compare_field,profile


def q(value,semantic='total_volume'):
    return {'value':value,'semantic':semantic}


@pytest.mark.parametrize('kind,policy,semantic,left,right,canonical',[
 ('volume','volume_total_l_v1','total_volume','500 ml','0.5 L','0.5'),
 ('length','length_width_m_v1','product_width','60 cm','0.6 m','0.6'),
 ('length','length_height_m_v1','product_height','1800 mm','1.8 m','1.8'),
 ('length','length_depth_m_v1','product_depth','650 mm','65 cm','0.65'),
 ('volume','volume_total_l_v1','total_volume','0 ml','0 L','0'),
])
def test_quantities_equal_with_explicit_semantics(kind,policy,semantic,left,right,canonical):
    result=compare_field(FieldRule(kind,'identity_variant',policy),q(left,semantic),q(right,semantic))
    assert result['comparison']=='equal'
    assert result['normalized_before']==result['normalized_after']==canonical
    assert result['input_states']=={'before':'value','after':'value'}
    assert result['input_reasons']=={'before':None,'after':None}
    assert result['trace'][0]['operation']==policy


def test_quantity_precision_does_not_depend_on_decimal_context():
    digits='123456789012345678901234567890123456789012345678901234567891'
    with localcontext() as context:
        context.prec=6
        result=compare_field(FieldRule('volume','identity_variant','volume_total_l_v1'),q(digits+' ml'),q(digits[:-3]+'.'+digits[-3:]+' L'))
    assert result['comparison']=='equal'
    assert result['normalized_before']==digits[:-3]+'.'+digits[-3:]


@pytest.mark.parametrize('value,semantic,state,reason',[
 (None,'total_volume','null','null'),('','total_volume','empty','empty'),
 ('   ','total_volume','empty','empty'),(False,'total_volume','value','invalid_type'),
 (0,'total_volume','value','unit_missing'),('250','total_volume','value','unit_missing'),
 ('-1 L','total_volume','value','negative'),('NaN','total_volume','value','non_finite'),
 ('Infinity','total_volume','value','non_finite'),('1-2 L','total_volume','value','range'),
 ('250 kg','total_volume','value','unit_incompatible'),('250 gallons','total_volume','value','unit_unsupported'),
 ('250 L','net_volume','value','semantic_mismatch'),('250 L','gross_volume','value','semantic_mismatch'),
 ('60 cm','package_width','value','semantic_mismatch'),
])
def test_invalid_quantity_is_unknown_with_preserved_state(value,semantic,state,reason):
    result=compare_field(FieldRule('volume','identity_variant','volume_total_l_v1'),q(value,semantic),q('250 L'))
    assert result['comparison']=='unknown'
    assert result['input_states']['before']==state and result['input_reasons']['before']==reason
    json.dumps(result,allow_nan=False)


def test_axis_policy_rejects_height_as_width():
    result=compare_field(FieldRule('length','identity_variant','length_width_m_v1'),q('60 cm','product_height'),q('0.6 m','product_width'))
    assert result['comparison']=='unknown' and result['input_reasons']['before']=='semantic_mismatch'


def test_refrigerator_profile_is_exactly_nine_fields():
    value=profile('refrigerator-v1')
    assert set(value.fields)=={'title','description','price','currency','attributes/capacity','attributes/width','attributes/height','attributes/depth','attributes/model'}
    assert value.fields['attributes/capacity']==FieldRule('volume','identity_variant','volume_total_l_v1')
    for axis in ('width','height','depth'):
        assert value.fields['attributes/'+axis]==FieldRule('length','identity_variant','length_'+axis+'_m_v1')
    assert value.fields['attributes/model']==FieldRule('text','identity_variant')
    for key in ('title','description','price','currency'):
        assert value.fields[key]==profile('generic-v1').fields[key]


def test_old_profiles_keep_exact_definition_and_comparison():
    generic={'title':{'kind':'text','role':'comparable','normalization':'exact'},'description':{'kind':'text','role':'comparable','normalization':'exact'},'price':{'kind':'decimal','role':'comparable','normalization':'decimal'},'currency':{'kind':'text','role':'price_context','normalization':'exact'}}
    assert {k:asdict(v) for k,v in profile('generic-v1').fields.items()}==generic
    assert set(profile('hardware-v1').fields)==set(generic)|{'attributes/'+k for k in ('ram','storage','model','material','weight')}
    assert set(profile('footwear-v1').fields)==set(generic)|{'attributes/'+k for k in ('size','size_system','color','fit','material','construction','weight')}
    assert compare_field(FieldRule('mass','comparable','mass_kg'),'1000 g','1 kg')=={'comparison':'equal','normalized_before':'1','normalized_after':'1','trace':[{'operation':'mass_kg','before':'1000 g','after':'1 kg','unit':'kg'}]}


def test_custom_quantity_profile_python_and_jsonschema_agree(tmp_path):
    custom=CategoryProfile('physical-v1',{'attributes/capacity':FieldRule('volume','identity_variant','volume_total_l_v1')})
    store=MaintenanceStore(tmp_path/'jobs.db',custom_profiles={'physical-v1':custom})
    try:assert store.registry['physical-v1']['fields']['attributes/capacity']['normalization']=='volume_total_l_v1'
    finally:store.close()
    schema=json.loads((Path(__file__).parents[1]/'src/shopextract/schemas/maintenance-profiles.schema.json').read_text())
    payload={'schema_version':1,'profiles':{'physical-v1':{k:asdict(v) for k,v in custom.fields.items()}}}
    Draft202012Validator(schema).validate(payload)
    payload['profiles']['physical-v1']['attributes/capacity']['normalization']='length_width_m_v1'
    assert not Draft202012Validator(schema).is_valid(payload)


@pytest.mark.parametrize('length,expected',[(128,'equal'),(129,'unknown')])
def test_quantity_input_length_boundary(length,expected):
    value='1'*(length-2)+' L'
    result=compare_field(FieldRule('volume','identity_variant','volume_total_l_v1'),q(value),q(value))
    assert result['comparison']==expected
    if length==129:assert result['input_reasons']['before']=='input_too_long'


def test_packaged_schema_admits_new_rule_and_rejects_cross_dimension_pair():
    schema=json.loads((Path(__file__).parents[1]/'src/shopextract/schemas/maintenance-profiles.schema.json').read_text())
    data={'schema_version':1,'profiles':{'physical-v1':{'attributes/capacity':{'kind':'volume','role':'identity_variant','normalization':'volume_total_l_v1'}}}}
    Draft202012Validator(schema).validate(data)
    data['profiles']['physical-v1']['attributes/capacity']['normalization']='length_width_m_v1'
    assert not Draft202012Validator(schema).is_valid(data)


@pytest.mark.parametrize('raw,state,reason',[(q(''),'empty','empty'),(q(None),'null','null'),(q('250 L'),'value',None)])
def test_raw_state_metadata_cannot_upgrade_unsupported_comparison(raw,state,reason):
    result=compare_field(FieldRule('volume','identity_variant','volume_total_l_v1'),q('250 L'),None,raw_after=raw)
    assert result['comparison']=='unknown' and result['normalized_after'] is None
    assert result['input_states']['after']==state and result['input_reasons']['after']==reason
