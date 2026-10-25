"""APC03 real inventory paths on tiny synthetic source-shaped metadata.

Fixture provenance is synthetic, not retained upstream or live product evidence.
Only trusted pin CONFIGURATION is substituted; parser/hash/sort code stays real.
"""
import hashlib
import json
from types import MappingProxyType

import pytest
from shopextract.maintenance import inventory
from shopextract.maintenance.inventory import BRANCH_FILES, REFERENCE_IDS, InventoryError, build_inventory

EXPECTED_FILES = {
    'el_electronics.yml': (555297, '08f92912aac14164afbd7704067c586499da9f5591df96def1a25adda908469f'),
    'aa_apparel_accessories.yml': (285314, '3746bf9fab3920b9f529caef076f91225b4f954e6f7e238668aaf49ed90419a6'),
    'hg_home_garden.yml': (877783, '355d32fbc787812c83ff5446dbe7d964d798f8508ec95ee5306f07da8e907a35'),
    'attributes.yml': (4769315, '91ef3829a6621fbc98b46c6447c9702e394fd7c55bfbd56fd2df0545ea9e16b6'),
    'LICENSE': (1046, '6a2261660cc6cb406ed6ef788347d8cb35e939f4537def9e699abf88ed025273'),
}


def repin(monkeypatch, directory):
    pins={name:(len(data),hashlib.sha256(data).hexdigest())
          for name in (*BRANCH_FILES,'attributes.yml','LICENSE')
          for data in [(directory/name).read_bytes()]}
    monkeypatch.setattr(inventory,'SOURCE_PINS',MappingProxyType(pins))


@pytest.fixture
def corpus(tmp_path,monkeypatch):
    branches={
        'el_electronics.yml': [('el','Electronics',['el-6-6'],[]),('el-6-6','Laptops',[],['color','memory_technology'])],
        'aa_apparel_accessories.yml': [('aa','Apparel',['aa-8-3'],[]),('aa-8-3','Boots',[],['color','size'])],
        'hg_home_garden.yml': [('hg','Home',['hg-11-7-41'],[]),('hg-11-7-41','Refrigerators',['hg-11-7-41-1'],['color','umbrella_opening_mechanism']),('hg-11-7-41-1','Synthetic child',[],['color'])],
    }
    for name,records in branches.items():
        text='---\n'
        for key,label,children,attributes in records:
            text+=f'- id: {key}\n  name: {label}\n'
            for field,values in [('children',children),('attributes',attributes)]:
                text+=f'  {field}:'+('\n'+''.join(f'  - {v}\n' for v in values) if values else ' []\n')
        (tmp_path/name).write_text(text)
    (tmp_path/'attributes.yml').write_text('---\nbase_attributes:\n'+''.join(
        f'- id: {i}\n  name: Synthetic {name}\n  friendly_id: {name}\n  handle: {name}\n  values: []\n'
        for i,name in enumerate(('color','memory_technology','size','umbrella_opening_mechanism'),1))+'extended_attributes: []\n')
    (tmp_path/'LICENSE').write_text('Synthetic fixture license marker; no upstream provenance claimed.\n')
    repin(monkeypatch,tmp_path)
    return tmp_path


def test_default_source_authority_is_immutable_and_exact():
    assert dict(inventory.SOURCE_PINS)==EXPECTED_FILES
    with pytest.raises(TypeError):inventory.SOURCE_PINS['LICENSE']=(0,'invalid')


def test_reference_smoke_keeps_policy_and_evidence_separate(corpus):
    result=build_inventory(corpus,selected_ids=REFERENCE_IDS)
    assert result==build_inventory(corpus,selected_ids=reversed(REFERENCE_IDS))
    rows={r['category_id']:r for r in result['rows']}
    for key,profile,state,backlog in [('el-6-6','hardware-v1','partial','existing_extension'),('aa-8-3','footwear-v1','partial','existing_extension'),('hg-11-7-41',None,'missing','new_profile')]:
        row=rows[key]
        assert (row['profile'],row['policy_coverage'],row['backlog_kind'])==(profile,state,backlog)
        assert len(row['declared_attributes'])==2
        assert row['semantic_review']=='pending' and row['checked_fields']==[]
        assert row['live_observation']=='not_run' and row['binding_status']=='not_configured'
        assert set(row['extraction_availability'])=={'shopify','woocommerce','magento','shopware','bigcommerce','generic'}
        assert set(row['extraction_availability'].values())=={'not_audited'}
    assert rows['hg-11-7-41']['excluded_attributes']=={'umbrella_opening_mechanism':'irrelevant_to_refrigerator_policy'}
    assert rows['hg-11-7-41']['candidate_fields']==['attributes/capacity','attributes/depth','attributes/height','attributes/model','attributes/width']
    assert rows['el-6-6']['field_gaps']['attributes/ram']=='numeric_capacity_policy_missing'


def test_tiny_full_denominator_order_and_pending_honesty(corpus):
    result=build_inventory(corpus)
    assert result==build_inventory(corpus,branch_files=reversed(BRANCH_FILES))
    assert result['denominator']=={'branch_nodes':{'aa_apparel_accessories.yml':2,'el_electronics.yml':2,'hg_home_garden.yml':3},'category_nodes':7,'selected_rows':7,'selection':'all_saved_branch_nodes'}
    rows=result['rows'];assert [r['category_id'] for r in rows]==sorted({r['category_id'] for r in rows})
    pending=[r for r in rows if r['category_id'] not in REFERENCE_IDS]
    assert len(pending)==4 and all(r['family'] is None and r['profile'] is None and r['backlog_kind']=='review_pending' for r in pending)
    assert result['summary']=={'backlog_counts':{'binding_only':0,'existing_extension':2,'new_profile':1,'review_pending':4},'reviewed_policy_family_count':0,'remaining_profile_count':None,'generic_coverage':'common_fields_only'}
    assert result['unassessed']=={'scope':'all_other_taxonomy_branches','category_count':None}
    assert {f['name']:(f['bytes'],f['sha256']) for f in result['source']['files']}==dict(inventory.SOURCE_PINS)


@pytest.mark.parametrize('names,ids',[(BRANCH_FILES,()),(BRANCH_FILES,('unknown',)),(BRANCH_FILES,('el-6-6','el-6-6')),(('el_electronics.yml',),None),((*BRANCH_FILES,'el_electronics.yml'),None),((*BRANCH_FILES,'../other.yml'),None)])
def test_invalid_selection_fails_closed(corpus,names,ids):
    with pytest.raises(InventoryError) as error:build_inventory(corpus,branch_files=names,selected_ids=ids)
    assert error.value.code=='invalid_selection'


@pytest.mark.parametrize('change',['missing','changed'])
def test_source_integrity_applies_before_partial_selection(corpus,change):
    path=corpus/'hg_home_garden.yml'
    if change=='missing':path.unlink()
    else:path.write_text(path.read_text()+'# changed\n')
    with pytest.raises(InventoryError) as error:build_inventory(corpus,selected_ids=('el-6-6',))
    assert error.value.code=='source_mismatch'


@pytest.mark.parametrize('case',['malformed','duplicate','dangling_child','disconnected_cycle','unresolved_attribute'])
def test_parser_and_graph_reject_invalid_pinned_content(corpus,monkeypatch,case):
    path=corpus/'el_electronics.yml';text=path.read_text()
    if case=='malformed':text='- id: [invalid\n'
    elif case=='duplicate':text+='- id: el-6-6\n  name: Duplicate\n  children: []\n  attributes: []\n'
    elif case=='dangling_child':text=text.replace('  - el-6-6','  - el-missing')
    elif case=='disconnected_cycle':text+='- id: el-cycle\n  name: Synthetic cycle\n  children:\n  - el-cycle\n  attributes: []\n'
    else:text=text.replace('  - memory_technology','  - nonexistent_attribute')
    path.write_text(text);repin(monkeypatch,corpus)
    with pytest.raises(InventoryError) as error:build_inventory(corpus)
    assert error.value.code=='invalid_source'


@pytest.mark.parametrize('count,valid',[(999,True),(1000,True),(1001,False)])
def test_existing_runtime_cap_stays_separate(count,valid):
    from shopextract._models import Platform
    from shopextract.categories.config import validate_options
    from shopextract.categories.contracts import CategoryError,CategoryOptions,CategoryScope,TargetRegistry
    options=CategoryOptions(CategoryScope(Platform.GENERIC,'https://fixture.invalid'),TargetRegistry('synthetic:inventory-test','1',tuple(f't-{n}' for n in range(count))))
    if valid:validate_options(options)
    else:
        with pytest.raises(CategoryError):validate_options(options)


def test_selection_iterable_is_bounded_before_parsing(corpus):
    consumed=[]
    def oversized():
        for number in range(5001):
            consumed.append(number)
            yield f'synthetic-{number}'
        raise AssertionError('Selection read beyond5001-entry admission boundary')
    with pytest.raises(InventoryError) as error:build_inventory(corpus,selected_ids=oversized())
    assert error.value.code=='invalid_selection' and len(consumed)==5001


def test_current_policy_overlay_preserves_baseline_and_never_claims_job_checks(corpus):
    """Shipping the pilot must not leave the requested current view stale/missing."""
    baseline=build_inventory(corpus)
    original=json.dumps(baseline,sort_keys=True)
    current=build_inventory(corpus,include_current_policy=True)
    rows={r['category_id']:r for r in current['rows']}
    fridge=rows['hg-11-7-41']
    assert current['schema_version']==2
    expected=hashlib.sha256(json.dumps(baseline,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
    assert current['baseline_digest']==expected
    from shopextract.maintenance.store import _profile_record,digest
    from shopextract.maintenance.profiles import profile
    assert fridge['profile_definition_digest']==digest(_profile_record(profile('refrigerator-v1')))
    assert fridge['profile']=='refrigerator-v1' and fridge['policy_coverage']=='implemented_selected_fields'
    assert fridge['whole_family_coverage']=='incomplete' and len(fridge['implemented_fields'])==9
    assert fridge['checked_fields']==[] and fridge['live_observation']=='not_run'
    assert current['summary']['remaining_profile_count'] is None
    assert json.dumps(build_inventory(corpus),sort_keys=True)==original


def test_current_overlay_missing_profile_uses_inventory_error(corpus,monkeypatch):
    import shopextract.maintenance.profiles as profiles
    from shopextract.maintenance import MaintenanceError
    original=profiles.profile
    def without_fridge(name):
        if name=='refrigerator-v1':raise MaintenanceError('invalid_argument')
        return original(name)
    monkeypatch.setattr(profiles,'profile',without_fridge)
    assert build_inventory(corpus)['schema_version']==1
    with pytest.raises(InventoryError) as error:build_inventory(corpus,include_current_policy=True)
    assert error.value.code=='invalid_selection'
