"""Five bounded APC14 auxiliary risks; prepared for independent coverage review."""
import json,os,subprocess,sys
from types import MappingProxyType
import pytest
from shopextract._evidence import trust_view
from shopextract._models import Platform
from shopextract._normalize import normalize
from shopextract._portable import product_to_record
from tests.profile_coverage_helpers import raw_product,normalized,NOW


def fixed_record(raw,platform=Platform.GENERIC,*,enrich=True):
    # Fixture controls only nondeterministic clock/IDs; preserve allocation order,
    # full portable structure, evidence pointers and every support reference.
    from itertools import count
    from uuid import UUID
    from unittest.mock import patch
    ids=count(1)
    with patch('shopextract._capture.uuid4',side_effect=lambda:UUID(int=next(ids))):
        product=normalize(raw,platform,include_refrigerator_attributes=enrich)
    product.scraped_at=NOW
    return product_to_record(product)


def test_duplicate_equivalent_evidence_keeps_both_sources():
    product=normalized(raw_product(additionalProperty=[{'name':'Total capacity','value':'250 L'},{'name':'Total volume','value':'250 L'}]))
    support=trust_view(product,product.evidence_contract)['/attributes/capacity']
    assert support['state']=='observed'
    pointers={e.retained_data['source_pointer'] for e in product.evidence_contract.evidence if e.evidence_id in support['evidence_ids']}
    assert {'/additionalProperty/0/name','/additionalProperty/0/value','/additionalProperty/1/name','/additionalProperty/1/value'}<=pointers


def test_competing_raw_and_projected_sources_reject_field():
    for key,changes in [('capacity',{'attributes':{'capacity':{'value':'300 L','semantic':'total_volume'}}}),('model',{'additionalProperty':[{'name':'Model','value':'FX300'}]})]:
        product=normalized(raw_product(**changes))
        assert key not in product.attributes
        assert trust_view(product,product.evidence_contract).get('/attributes/'+key,{}).get('state')!='observed'


def test_native_schemaorg_lookalike_does_not_enable_projection():
    raw=raw_product(title='Native refrigerator',id=7,variants=[])
    default=fixed_record(raw,Platform.SHOPIFY,enrich=False)
    opted=fixed_record(raw,Platform.SHOPIFY,enrich=True)
    assert default==opted
    assert default['product']['attributes']=={}


def test_fresh_process_hash_seeds_preserve_portable_bytes():
    code="from tests.profile_coverage_helpers import raw_product;from tests.profile_coverage_mechanism_checks import fixed_record;import json;print(json.dumps(fixed_record(raw_product()),ensure_ascii=False,separators=(',',':')))"
    outputs=[]
    for seed in ('1','26'):
        result=subprocess.run([sys.executable,'-c',code],env={**os.environ,'PYTHONHASHSEED':seed,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1'},capture_output=True,timeout=10,check=True)
        assert len(result.stdout)<=65536 and len(result.stderr)<=65536
        outputs.append(result.stdout)
    assert outputs[0]==outputs[1]


def test_conversion_assertion_detects_temporary_fault_and_restores():
    import shopextract.maintenance.profiles as module
    rule=module.FieldRule('volume','identity_variant','volume_total_l_v1')
    def result():return module.compare_field(rule,{'value':'500 ml','semantic':'total_volume'},{'value':'0.5 L','semantic':'total_volume'})
    assert result()['comparison']=='equal'
    original=module.QUANTITY_POLICIES
    changed=dict(original);kind,semantic,unit,units=changed['volume_total_l_v1']
    changed['volume_total_l_v1']=(kind,semantic,unit,MappingProxyType({**units,'ml':-2}))
    try:
        module.QUANTITY_POLICIES=MappingProxyType(changed)
        with pytest.raises(AssertionError):assert result()['comparison']=='equal'
    finally:module.QUANTITY_POLICIES=original
    assert module.QUANTITY_POLICIES is original and result()['comparison']=='equal'
