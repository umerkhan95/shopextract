"""Predesigned interim review gaps, controlled real paths; no live sources/models."""
from dataclasses import replace

import pytest

from shopextract._evidence import SupportState
from shopextract._models import Platform
from shopextract.categories import (
    AdapterContext, CategoryError, CategoryOptions, CategorySelector, MappingRule,
    NativeCategoryError, TargetRegistry, map_categories, normalize_with_categories,
)
from shopextract.categories.validation import validate_observations


@pytest.mark.parametrize('failed', ['uid', 'name', 'categories', 'global'])
def test_c06_c11_magento_nonnull_failed_facets_cannot_map(failed):
    from tests.test_category_magento import captured, SCOPE
    from shopextract.categories.adapters.magento import observe_categories
    raw = captured(categories=[{'uid':'MTI=', 'name':'Boots'}, {'uid':'WA==', 'name':'Other'}])
    path = None if failed == 'global' else ('categories',) if failed == 'categories' else ('categories',0,failed)
    observed = observe_categories(raw,context=AdapterContext(SCOPE,native_errors=(NativeCategoryError(path,'FAILED'),)))
    first, sibling = observed[0].terms
    facts = {f.binding.facet:f for f in first.facts}
    rejected = {'native_id','label'} if failed in ('categories','global') else {'native_id' if failed == 'uid' else 'label'}
    for facet, fact in facts.items():
        assert (fact.support != SupportState.OBSERVED) == (facet in rejected)
        assert fact.outcome.accepted == (facet not in rejected)
    assert all((f.support != SupportState.OBSERVED) == (failed in ('categories','global')) for f in sibling.facts)
    for facet, representation in [('native_id', {'native_id':'MTI='}), ('label', {'raw_label':'Boots'})]:
        configured = CategoryOptions(SCOPE,TargetRegistry('canonical','v1',('boot',)),
            (MappingRule('rule','1',CategorySelector('magento:category',None,allow_unknown_version=True,**representation),('boot',)),))
        decisions = map_categories(observed,options=configured)
        first_decision = next(d for d in decisions if d.term == first.ref)
        assert (first_decision.status == 'mapped') == (facet not in rejected)


@pytest.mark.parametrize('facet', ['parent_id','child_id'])
def test_c13_bound_endpoint_mismatch_rejected(facet):
    from tests.test_category_shopware import captured, observations, IDS, SCOPE
    from shopextract.categories.contracts import CategoryTermRef
    from shopextract.categories.portable import bind_product
    from shopextract.categories.config import options_digest
    raw = captured(categories=[{'id':IDS[0],'parentId':IDS[1],'name':'Child'}, {'id':IDS[1],'name':'Parent'}])
    observed = observations(raw)
    association = observed[2]
    edge = association.parent_edges[0]
    rogue = CategoryTermRef(edge[0].namespace,None,IDS[8],edge[0].merchant_scope)
    new_edge = (rogue,edge[1]) if facet == 'parent_id' else (edge[0],rogue)
    facts = tuple(replace(f,binding=replace(f.binding,edge=new_edge)) if f.binding.edge else f for f in association.facts)
    forged = observed[:2]+(replace(association,parent_edges=(new_edge,),facts=facts),)
    configured = CategoryOptions(SCOPE,TargetRegistry('canonical','1',('boot',)))
    with pytest.raises(CategoryError,match='endpoint'):
        validate_observations(forged)
    with pytest.raises(CategoryError,match='endpoint'):
        map_categories(forged,options=configured)
    good = normalize_with_categories(raw,Platform.SHOPWARE,SCOPE.store_url,category_options=configured)
    with pytest.raises(CategoryError,match='endpoint'):
        bind_product(good.product,SCOPE,forged,(),options_digest(configured))


@pytest.mark.parametrize('edges', [7,8,9])
def test_c13_c22_explicit_depth_boundary(edges):
    from tests.test_category_shopware import captured, observations
    entries = [{'id':f'{i:032x}','name':'N'+str(i),**({'parentId':f'{i-1:032x}'} if i else {})} for i in range(edges+1)]
    observed = observations(captured(categories=entries))
    association = observed[2]
    validate_observations(observed)
    assert len(association.parent_edges) == edges
    assert association.completeness == ('partial' if edges > 8 else 'complete')
    assert association.reason == ('category_ancestry_depth_reached' if edges > 8 else '')
    assert association.relation == 'memberships'  # No invented root or ordered trail.


def test_c13_orphan_retains_declared_edge_without_root_claim():
    from tests.test_category_shopware import captured, observations, IDS
    association = observations(captured(categories=[{'id':IDS[0],'parentId':IDS[8],'name':'Child'}]))[2]
    validate_observations((association,))
    assert association.completeness == 'partial' and association.reason == 'category_parent_unavailable'
    assert len(association.parent_edges) == 1 and association.relation != 'ordered_path'
    assert all(f.support == SupportState.OBSERVED for f in association.facts if f.binding.edge)


def _category_harness(tmp_path, *, profile='hardware-v1', attributes=None, failure_hook=None):
    from tests.test_maintenance_acceptance import Harness, NOW, ORIGIN
    from tests.test_category_skeleton import maintenance_category_config
    from shopextract.maintenance import MaintenanceEngine, MaintenanceStore
    from shopextract.tools import ToolConfig
    config = replace(maintenance_category_config(),profile_bindings=(('A',profile),))
    # Neutral source label avoids the preexisting Shoes->footwear veto masking
    # the matcher/field safeguards this category-enabled case must exercise.
    config = replace(config,options=replace(config.options,rules=tuple(
        replace(rule,selector=replace(rule.selector,raw_label='Declared')) for rule in config.options.rules)))
    h = Harness(tmp_path/'transport.db',category='Declared',attributes=attributes)
    resolver, transport = h.engine.resolver, h.engine.wire_transport
    h.store.close()
    h.store = MaintenanceStore(tmp_path/'categories.db',category_config=config)
    h.engine = MaintenanceEngine(h.store,tool_config=ToolConfig(allowed_origins=(ORIGIN,)),
        resolver=resolver,wire_transport=transport,utc_now=lambda:NOW,
        category_config=config,failure_hook=failure_hook)
    return h, config


@pytest.mark.parametrize('case', ['ram','boot','identity','binding_conflict'])
async def test_c20_real_category_engine_preserves_matcher_safeguards(tmp_path,case):
    from tests.test_maintenance_acceptance import goal, baseline
    profile = 'footwear-v1' if case == 'boot' else 'hardware-v1'
    if case == 'ram':
        field, left, right = 'attributes/ram', {'ram':'8 GB'}, {'ram':'16 GB'}
    elif case == 'boot':
        field, left, right = 'attributes/size', {'size':'8','size_system':'UK'}, {'size':'9','size_system':'UK'}
    else:
        field, left, right = 'description', {}, {}
    h, config = _category_harness(tmp_path,profile=profile,attributes=right)
    record = baseline(attributes=left)
    if case == 'identity':
        record.update(sku='Other',gtin='5901234123457',vendor='Other Brand',title='Unrelated Product')
    if case == 'binding_conflict':
        # Same source mapping, deliberately disagreeing explicitly selected policy.
        profile = 'footwear-v1'
    key, report = await h.run(goal(baseline=(record,),fields=(field,),profiles={'S1':profile}))
    finding, = report['findings']
    assert h.store.category_policy(key).mode == 'enabled'
    assert finding['status'] == 'needs_review'
    if case == 'binding_conflict':
        assert finding['reason'] == 'category_profile_conflict'
        assert finding['category_review_reasons'] == ['category_profile_conflict']
    else:
        assert finding['category_review_reasons'] == []
        assert finding['reason'] in ('identity_unresolved','variant_specification')
        if case in ('ram','boot'):
            assert finding['comparison'] == 'different'
            assert finding['before'] == left[field.split('/')[1]]
            assert finding['after'] == right[field.split('/')[1]]
            assert finding['evidence_ids']
        else:
            assert finding['reason'] == 'identity_unresolved'
    assert not any(f['status'] == 'proposed_correction' for f in report['findings'])
    h.store.close()


@pytest.mark.parametrize('boundary', ['encode','checkpoint'])
async def test_c24_encode_and_checkpoint_failure_atomic_retry(tmp_path,monkeypatch,boundary):
    from tests.test_maintenance_acceptance import goal
    from shopextract.categories.portable import categorized_product_from_record, categorized_product_to_record
    from shopextract.tools.execution import OwnedProcess
    from shopextract.tools.contracts import encoded
    import json
    class CheckpointCrash(BaseException):
        pass
    armed = True
    def crash(event,payload):
        nonlocal armed
        if boundary == 'checkpoint' and armed and event == 'before_checkpoint':
            armed = False
            raise CheckpointCrash('controlled loss immediately before source transaction')
    run_worker = OwnedProcess.run
    async def corrupt_child_reply(self,kind,payload,context):
        nonlocal armed
        result = await run_worker(self,kind,payload,context)
        request = json.loads(payload)
        if boundary == 'encode' and armed and kind == 'domain' and request.get('operation') == 'parse':
            reply = json.loads(result)
            if reply:
                armed = False
                # Return corrupted actual worker output; no codec call in injector.
                reply[0]['original_binding'] = 'invalid'
                return encoded(reply)
        return result
    monkeypatch.setattr(OwnedProcess,'run',corrupt_child_reply)
    h, config = _category_harness(tmp_path,failure_hook=crash)
    key = h.store.create(goal())
    original_policy = h.store.category_policy(key)
    with pytest.raises(CategoryError if boundary == 'encode' else CheckpointCrash):
        await h.engine.run(key)
    sources = [s for s in h.store.steps(key) if s['kind'] == 'extract']
    assert len(sources) == 1 and sources[0]['state'] != 'committed'
    assert sources[0]['result'] is None
    assert h.store._db.execute('SELECT COUNT(*) FROM cache').fetchone()[0] == 0
    resumed = await h.engine.resume(key)
    assert resumed['state'] == 'partial' and resumed['usage']['unknown_requests'] >= 1
    report = await h.engine.retry_unknown(key,sources[0]['id'])
    assert h.store.category_policy(key) == original_policy
    committed = [s for s in h.store.steps(key) if s['kind'] == 'extract' and s['state'] == 'committed']
    assert len(committed) == 1 and len(committed[0]['result']['products']) == 1
    record = committed[0]['result']['products'][0]
    assert categorized_product_to_record(categorized_product_from_record(record)) == record
    assert len(report['findings']) == 1
    assert h.store._db.execute('SELECT COUNT(*) FROM findings WHERE job=?',(key,)).fetchone()[0] == 1
    h.store.close()


def test_driver_timeout_kills_auxiliary_and_bounds_logs(tmp_path):
    import os
    import sys
    import time
    from pathlib import Path
    from tests.category_mechanism_driver import run_bounded
    marker = tmp_path/'auxiliary-survived'
    # If the grandchild survives group cleanup it creates this marker later.
    child = 'import time,pathlib; time.sleep(1); pathlib.Path(' + repr(str(marker)) + ').write_text("escaped")'
    program = ('import subprocess,sys,time; subprocess.Popen([sys.executable,"-c",' + repr(child) + ']); '
               'print("x"*20000,flush=True); time.sleep(10)')
    result = run_bounded([sys.executable,'-c',program],seconds=.2,log_path=tmp_path/'timeout.log',env=os.environ.copy(),log_bytes=1024)
    assert result['timed_out'] and result['returncode'] != 0
    assert result['log_bytes'] == 1024 and result['log_truncated']
    assert (tmp_path/'timeout.log').stat().st_size == 1024
    time.sleep(1.1)
    assert not marker.exists()
