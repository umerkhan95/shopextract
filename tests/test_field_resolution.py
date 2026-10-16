"""Authority, freshness, conflict preservation and report handoff for #36."""
from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from itertools import permutations
import json
from uuid import UUID

import pytest

from shopextract import (Evidence, FieldObservation, Product, ResolutionPolicy,
                        TrustContract, Variant, classify_match, match_products,
                        resolve_fields, resolution_references)

NOW = datetime(2026, 10, 16, 12, tzinfo=timezone.utc)


def candidate(index, path, value=None, *, role='unverified', age=timedelta(0), state='observed'):
    eid,oid='e_'+str(UUID(int=index)), 'o_'+str(UUID(int=index))
    e=Evidence(eid,'https://manufacturer.example/api',NOW-age,'fixture',
               retained_data={'value':value},pointer='/value',source_role=role)
    o=FieldObservation(oid,path,state,value,value,[eid] if state=='observed' else [],
                       reason='' if state=='observed' else 'Value unavailable')
    return e,o


def contract(*candidates):
    return TrustContract([e for e,o in candidates],[o for e,o in candidates])


def result(c, **kwargs):
    resolved=resolve_fields(c,as_of=NOW,**kwargs)
    assert len(resolved.evidence)==len(c.evidence)
    assert len(resolved.observations)==len(c.observations)
    assert all(o.validated_confidence is None for o in resolved.observations)
    return resolved,resolved.resolutions[0]


@pytest.mark.parametrize('path', ['/title','/gtin','/mpn','/vendor','/attributes/color','/variants/0/attributes/size'])
def test_verified_manufacturer_wins_specs_and_preserves_both_observations(path):
    a=candidate(1,path,'supplier claim',role='supplier')
    b=candidate(2,path,'manufacturer specification',role='verified_manufacturer')
    source=contract(a,b);before=source.to_dict()
    resolved,r=result(source)
    assert r.state=='observed' and r.selected_observation_id==b[1].observation_id
    assert set(r.observation_ids)=={a[1].observation_id,b[1].observation_id}
    assert 'verified_manufacturer' in r.reason and r.policy_version=='1'
    assert source.to_dict()==before and not source.resolutions
    resolved.observations[0].raw_value='changed'
    assert source.to_dict()==before


@pytest.mark.parametrize('path', ['/price','/compare_at_price','/in_stock','/currency','/condition','/variants/0/price'])
def test_supplier_offer_authority_does_not_use_manufacturer_list_values(path):
    manufacturer=candidate(1,path,20,role='verified_manufacturer')
    supplier=candidate(2,path,10,role='supplier')
    _,r=result(contract(manufacturer,supplier))
    assert r.selected_observation_id==supplier[1].observation_id
    assert 'not authoritative for this offer' in r.reason
    _,only_manufacturer=result(contract(manufacturer))
    assert only_manufacturer.state=='unknown' and only_manufacturer.selected_observation_id is None


def test_hostname_and_unverified_manufacturer_never_establish_authority():
    source=contract(candidate(1,'/mpn','a',role='manufacturer'),candidate(2,'/mpn','b'))
    _,r=result(source)
    assert r.state=='conflicting' and r.selected_observation_id is None


def test_supplier_beats_unverified_specification():
    source=contract(candidate(1,'/mpn','a'),candidate(2,'/mpn','b',role='supplier'))
    _,r=result(source)
    assert r.selected_observation_id==source.observations[1].observation_id


def test_newest_equal_authority_disagreement_is_not_an_automatic_winner():
    source=contract(candidate(1,'/price',Decimal(10),role='supplier',age=timedelta(hours=2)),
                    candidate(2,'/price',Decimal(11),role='supplier'))
    _,r=result(source)
    assert r.state=='conflicting' and r.selected_observation_id is None


@pytest.mark.parametrize('left,right,path,equivalent',[
    (Decimal('10.00'),10,'/price',True), (0,False,'/in_stock',False),
    (10,'10','/price',False), (' Product  Name ','product name','/title',True),
    (' Café ','Cafe\u0301','/vendor',True), ('NEW','new','/condition',True),
    ('aB','ab','/mpn',False), ('1 L','1000 ml','/attributes/size',False),
    ({'b':2,'a':1},{'a':1,'b':2},'/attributes',True),
    ([1,2],[2,1],'/tags',False), ([],[],'/tags',True),
])
def test_typed_equivalence_is_conservative(left,right,path,equivalent):
    source=contract(candidate(2,path,left,role='supplier'),candidate(1,path,right,role='supplier'))
    resolved,r=result(source)
    assert (r.state=='observed') is equivalent
    if equivalent:
        assert r.selected_observation_id==source.observations[1].observation_id
    assert resolved.observations[0].normalized_value==right


@pytest.mark.parametrize('path,age,expected',[
    ('/price',timedelta(days=1),'observed'),
    ('/price',timedelta(days=1,microseconds=1),'expired'),
    ('/mpn',timedelta(days=30),'observed'),
    ('/mpn',timedelta(days=30,microseconds=1),'expired'),
    ('/price',timedelta(seconds=-1),'unknown'),
])
def test_freshness_boundaries_and_future_evidence(path,age,expected):
    resolved,r=result(contract(candidate(1,path,0,role='supplier',age=age)))
    assert r.state==expected
    assert resolved.observations[0].state=='observed'
    assert NOW.isoformat() in r.reason


def test_stale_high_authority_does_not_hide_fresh_lower_authority():
    source=contract(candidate(1,'/mpn','old',role='verified_manufacturer',age=timedelta(days=31)),
                    candidate(2,'/mpn','fresh',role='supplier'))
    _,r=result(source)
    assert r.selected_observation_id==source.observations[1].observation_id
    assert 'excluded stale' in r.reason


def test_mixed_source_support_cannot_inherit_strongest_role_or_freshest_time():
    high=candidate(1,'/mpn','high',role='verified_manufacturer')
    weak=candidate(2,'/mpn','weak')
    supplier=candidate(3,'/mpn','supplier',role='supplier')
    high[1].evidence_ids.append(weak[0].evidence_id)
    source=contract(high,weak,supplier)
    _,r=result(source)
    assert r.selected_observation_id==supplier[1].observation_id
    source.evidence[1].observed_at=NOW-timedelta(days=31)
    _,r=result(source)
    assert 'excluded stale' in r.reason
    assert r.selected_observation_id==supplier[1].observation_id


@pytest.mark.parametrize('states,expected',[
    (['unsupported'],'unsupported'), (['unknown'],'unknown'),
    (['expired'],'expired'), (['unsupported','unknown'],'unknown'),
])
def test_no_supported_candidate_exposes_unavailable_state(states,expected):
    _,r=result(contract(*(candidate(i+1,'/price',state=s) for i,s in enumerate(states))))
    assert r.state==expected and r.selected_observation_id is None


def test_policy_configuration_and_score_cannot_change_authority():
    a=candidate(1,'/price',10,role='supplier',age=timedelta(days=2))
    b=candidate(2,'/price',20)
    a[1].score=999;a[1].score_kind='model'
    source=contract(a,b)
    _,r=result(source)
    assert r.selected_observation_id==b[1].observation_id
    resolved,r=result(source,policy=ResolutionPolicy(offer_max_age=timedelta(days=3)))
    assert r.selected_observation_id==a[1].observation_id
    assert resolved.observations[0].score==999 and 'offer_max_age=3 days' in r.reason


@pytest.mark.parametrize('age', [timedelta(0),timedelta(days=-1),1])
def test_invalid_policy_windows_rejected(age):
    with pytest.raises(ValueError):ResolutionPolicy(offer_max_age=age)


@pytest.mark.parametrize('clock', [datetime(2026,10,16),NOW.astimezone(timezone(timedelta(hours=2)))])
def test_evaluation_requires_explicit_utc(clock):
    with pytest.raises(ValueError):resolve_fields(TrustContract(),as_of=clock)


def test_permutations_and_round_trip_have_identical_semantic_results():
    source=contract(candidate(3,'/title','high',role='verified_manufacturer'),
                    candidate(2,'/title','low',role='supplier'),candidate(1,'/title','other'))
    expected=resolve_fields(source,as_of=NOW).to_dict()
    for obs in permutations(source.observations):
        for evidence in permutations(source.evidence):
            shuffled=TrustContract(list(evidence),list(obs))
            assert resolve_fields(shuffled,as_of=NOW).to_dict()==expected
    loaded=TrustContract.from_dict(json.loads(json.dumps(expected)))
    assert loaded.to_dict()==expected
    assert resolve_fields(loaded,as_of=NOW).to_dict()==expected


def test_nested_escaped_paths_trust_view_and_original_values_survive():
    path='/variants/0/attributes/size~1color~0'
    source=contract(candidate(1,path,'red',role='supplier'),
                    candidate(2,path,'blue',role='verified_manufacturer'))
    p=Product(variants=[Variant(attributes={'size/color~':'red'})])
    p.evidence_contract=resolve_fields(source,as_of=NOW)
    view=p.trust_view()[path]
    assert view['value']=='blue' and view['legacy_value']=='red'
    assert p.variants[0].attributes['size/color~']=='red'
    assert set(view['evidence_ids'])=={e.evidence_id for e in source.evidence}


def test_dangling_support_is_rejected_instead_of_resolved():
    source=contract(candidate(1,'/price',10));source.evidence=[]
    with pytest.raises(ValueError,match='Dangling'):resolve_fields(source,as_of=NOW)


def test_matching_reports_link_all_conflicts_without_changing_decisions_or_scores():
    a=Product(title='Product',gtin='4006381333931');b=deepcopy(a)
    before=asdict(classify_match(a,b))
    a.evidence_contract=resolve_fields(contract(candidate(1,'/price',10,role='supplier'),
                                                candidate(2,'/price',11,role='supplier')),as_of=NOW)
    decision=classify_match(a,b)
    after=asdict(decision);support=after.pop('field_support');before.pop('field_support')
    assert after==before and support['a']['/price']['state']=='conflicting'
    references=support['a']['/price']
    assert len(references['evidence_ids'])==2 and references['policy_version']=='1'
    assert references['selected_observation_id'] is None
    assert match_products([a],[b])[0].field_support==support
    assert 'validated_confidence' not in json.dumps(support)


def test_unmatched_and_semantic_candidates_keep_field_references():
    a=Product(title='zzzz');b=Product(title='other')
    a.evidence_contract=resolve_fields(contract(candidate(1,'/title','zzzz')),as_of=NOW)
    report=match_products([a],[],semantic_candidates=None)
    assert report[0].field_support['a']==resolution_references(a.evidence_contract)
    report=match_products([a],[b],semantic_candidates=lambda a,bs:[0])
    assert report[0].field_support['a']['/title']['evidence_ids']


@pytest.mark.parametrize('invalid', [False,{},'latest'])
def test_invalid_policy_argument_is_not_silently_replaced(invalid):
    with pytest.raises(ValueError,match='ResolutionPolicy'):
        resolve_fields(TrustContract(),as_of=NOW,policy=invalid)


def test_validated_confidence_is_retained_but_never_used_for_authority():
    from shopextract import ValidatedConfidence
    high=candidate(1,'/mpn','verified',role='verified_manufacturer')
    low=candidate(2,'/mpn','supplier',role='supplier')
    low[1].validated_confidence=ValidatedConfidence(.99,'fixture validation','fixture-set','1')
    source=contract(high,low)
    resolved=resolve_fields(source,as_of=NOW)
    assert resolved.resolutions[0].selected_observation_id==high[1].observation_id
    assert resolved.observations[1].validated_confidence==low[1].validated_confidence
    assert resolved.observations[0].validated_confidence is None


def test_empty_contract_and_unresolved_single_references_remain_explicit():
    resolved=resolve_fields(TrustContract(),as_of=NOW)
    assert not resolved.resolutions and resolution_references(resolved)=={}
    source=contract(candidate(1,'/price',0))
    refs=resolution_references(source)['/price']
    assert refs['selected_observation_id']==source.observations[0].observation_id
    assert refs['policy'] is None


@pytest.mark.parametrize('platform', ['magento','shopware'])
def test_saved_live_api_html_observations_preserve_support_distinctions(platform):
    from pathlib import Path
    path=Path(__file__).parent/'fixtures/field-resolution'/f'{platform}-live-price.json'
    captured=TrustContract.from_dict(json.loads(path.read_text()))
    clock=max(e.observed_at for e in captured.evidence)+timedelta(seconds=1)
    resolved=resolve_fields(captured,as_of=clock)
    p=Product(price=Decimal(0));p.evidence_contract=resolved
    view=p.trust_view()['/price']
    supported=[o for o in captured.observations if o.state=='observed']
    assert view['value']==supported[0].normalized_value and view['state']=='observed'
    assert view['legacy_value']==0 and len(view['observation_ids'])==2
    assert len(resolved.evidence)==len(captured.evidence)
    if platform=='shopware':
        assert view['value']==Decimal(22)
        assert any(o.state=='unsupported' for o in resolved.observations)
    else:
        assert len(supported)==2 and supported[0].normalized_value==supported[1].normalized_value
