"""Predesigned shared mechanisms/boundaries for independent driver review; no live access."""
from dataclasses import replace
from copy import deepcopy
import json

import pytest

from shopextract._models import Platform
from shopextract.categories import (CategoryError, CategoryLimits, CategoryOptions, CategoryScope,
    CategorySelector, MappingRule, TargetRegistry, categorized_product_to_record,
    categorized_product_from_record, normalize_with_categories, validate_options)
from shopextract.categories._codec import canonical
from shopextract.categories.portable import bind_product
from tests.test_category_skeleton import captured, options, STORE


def wrapper():
    return normalize_with_categories(captured({'id':101,'title':'Laptop','product_type':'Laptop','variants':[]}),
        Platform.SHOPIFY,STORE,category_options=options())


def test_c14_three_native_sources_share_one_exact_mapper():
    from tests.test_category_woocommerce import captured as woo_raw
    from tests.test_category_magento import captured as magento_raw
    cases = [
        (Platform.SHOPIFY,captured({'id':101,'title':'Laptop','product_type':'Laptop','variants':[]}),
         CategorySelector('shopify:product_type',None,raw_label='Laptop',allow_unknown_version=True)),
        (Platform.WOOCOMMERCE,woo_raw(categories=[{'id':12,'name':'Notebooks'}]),
         CategorySelector('woocommerce:product_cat',None,native_id='12',allow_unknown_version=True)),
        (Platform.MAGENTO,magento_raw(categories=[{'uid':'MTI=','name':'Notebook'}]),
         CategorySelector('magento:category',None,native_id='MTI=',allow_unknown_version=True)),
    ]
    for platform,raw,selector in cases:
        configured = CategoryOptions(CategoryScope(platform,STORE),TargetRegistry('operator','v1',('laptop',)),
            (MappingRule('source-'+platform.value,'1',selector,('laptop',)),))
        value = normalize_with_categories(raw,platform,STORE,category_options=configured)
        assert {d.target_ids for d in value.mappings if d.status == 'mapped'} == {('laptop',)}
        assert any(o.terms for o in value.observations)


def test_c17_real_companion_roundtrip_retains_source_and_derived_history():
    value = wrapper()
    record = categorized_product_to_record(value)
    restored = categorized_product_from_record(json.loads(json.dumps(record)))
    assert categorized_product_to_record(restored) == record
    assert restored.observations[0].terms[0].facts[0].outcome.transformations == value.observations[0].terms[0].facts[0].outcome.transformations
    from shopextract._portable import product_from_record
    with pytest.raises(ValueError):
        product_from_record(record)


@pytest.mark.parametrize('mutation',['evidence','history','product'])
def test_c18_nested_mutation_cannot_be_reencoded(mutation):
    value = wrapper()
    fact = value.observations[0].terms[0].facts[0]
    if mutation == 'evidence':
        fact.evidence[0].retained_data['value'] = 'Changed'
    elif mutation == 'history':
        fact.outcome.transformations.append('Forged conversion')
    else:
        value.product.title = 'Changed'
    with pytest.raises(CategoryError):
        categorized_product_to_record(value)


@pytest.mark.parametrize('count',[999,1000,1001])
def test_c16_config_entry_boundary_is_explicit(count):
    selector = CategorySelector('merchant',None,native_id='7',allow_unknown_version=True)
    configured = replace(options(),rules=tuple(MappingRule('r'+str(i),'1',selector,('A',)) for i in range(count)))
    if count > 1000:
        with pytest.raises(CategoryError):
            validate_options(configured)
    else:
        validate_options(configured)


@pytest.mark.parametrize('target_size',[262143,262144,262145])
def test_c22_companion_bytes_below_at_above(target_size):
    value = wrapper()
    initial = len(canonical(categorized_product_to_record(value)).encode())
    # Product trust is attached dynamically; replace() would discard it and
    # shrink the envelope relative to the measured baseline.
    product = deepcopy(value.product)
    product.description = 'x'*(target_size-initial)
    if target_size > 262144:
        with pytest.raises(CategoryError):
            bind_product(product,value.scope,value.observations,value.mappings,value.config_digest)
    else:
        result = bind_product(product,value.scope,value.observations,value.mappings,value.config_digest)
        assert len(canonical(categorized_product_to_record(result)).encode()) == target_size


@pytest.mark.parametrize('count',[99,100,101])
def test_c22_native_member_boundary_preserves_supported_terms(count):
    from shopextract._capture import capture
    from shopextract.categories import AdapterContext
    from shopextract.categories.adapters.bigcommerce import observe_categories
    data = {'categories':{'edges':[{'node':{'entityId':i+1,'name':'N'+str(i)}} for i in range(count)],
                          'pageInfo':{'hasNextPage':False}}}
    observation = observe_categories(capture(data,STORE,'synthetic_fixture'),context=AdapterContext(options(Platform.BIGCOMMERCE).scope))[0]
    assert len(observation.terms) == min(count,100)
    assert observation.completeness == ('partial' if count > 100 else 'complete')


async def test_c19_corrupt_companion_cache_is_miss_not_legacy_fallback(tmp_path):
    from tests.test_maintenance_acceptance import Harness,goal,NOW,ORIGIN
    from tests.test_category_skeleton import maintenance_category_config
    from shopextract.maintenance import MaintenanceStore,MaintenanceEngine
    from shopextract.tools import ToolConfig
    h = Harness(tmp_path/'transport.db',category='Shoes')
    config = maintenance_category_config()
    h.store = MaintenanceStore(tmp_path/'category.db',category_config=config)
    h.engine = MaintenanceEngine(h.store,tool_config=ToolConfig(allowed_origins=(ORIGIN,)),
        resolver=h.engine.resolver,wire_transport=h.engine.wire_transport,utc_now=lambda:NOW,category_config=config)
    await h.run(goal())
    sent = len(h.requests)
    h.store.acquire()
    with h.store._transaction() as db:
        rows = list(db.execute('SELECT key,payload FROM cache'))
        assert rows
        for row in rows:
            payload = json.loads(row['payload'])
            payload['products'][0]['original_binding'] = 'invalid'
            db.execute('UPDATE cache SET payload=? WHERE key=?',(json.dumps(payload),row['key']))
    h.store.release()
    await h.run(goal())
    assert len(h.requests) > sent
    h.store.close()


def test_c20_mapping_cannot_select_or_override_explicit_profile():
    from shopextract.categories.maintenance import category_review_reasons
    from shopextract.categories import CategoryRuntimeConfig
    selector = CategorySelector('shopify:product_type',None,raw_label='Laptop',allow_unknown_version=True)
    configured = replace(options(),rules=(MappingRule('laptop','1',selector,('A',)),))
    value = normalize_with_categories(captured({'id':101,'title':'Laptop','product_type':'Laptop','variants':[]}),
        Platform.SHOPIFY,STORE,category_options=configured)
    runtime = CategoryRuntimeConfig(configured,(('A','footwear-v1'),))
    assert 'category_profile_conflict' in category_review_reasons(value,selected_profile='hardware-v1',config=runtime)
    assert 'category_profile_missing' in category_review_reasons(value,selected_profile=None,config=runtime)
