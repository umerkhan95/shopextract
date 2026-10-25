"""Predesigned initial red seams, not complete C01–24 mechanism verification."""
from datetime import datetime, timezone
import importlib

import httpx
import pytest

from shopextract._capture import capture
from shopextract._evidence import Evidence, SupportState
from shopextract._models import Platform, Product
from shopextract.categories import (
    AdapterContext, CategorizedProduct, CategoryError, CategoryFact, CategoryObservation,
    CategoryFactBinding, CategoryOptions, CategoryRuntimeConfig, CategoryScope, CategorySelector,
    CategoryTerm, CategoryTermRef, MappingRule, TargetRegistry,
    categorized_product_from_record, categorized_product_to_record,
    extract_with_categories, map_categories, normalize_with_categories, validate_options,
)
from shopextract.categories.maintenance import category_review_reasons
from shopextract._normalization import ConversionOutcome
from shopextract.categories.evidence import source_fact
from shopextract.categories.native import localize_category_errors
from shopextract.categories import NativeCategoryError

AT = datetime(2026, 10, 17, tzinfo=timezone.utc)
STORE = 'https://merchant.test/shop'


def options(platform=Platform.SHOPIFY, rules=()):
    return CategoryOptions(CategoryScope(platform, STORE),
                           TargetRegistry('operator-category', 'v1', ('A', 'B', 'C')), rules)


def captured(raw):
    return capture(raw, STORE + '/products/101', 'synthetic_fixture', observed_at=AT)


def test_c01_normalize_preserves_custom_label():
    value = normalize_with_categories(captured({'id': 101, 'title': 'Boots',
        'product_type': 'Boots > Sale/Outdoor', 'variants': []}), Platform.SHOPIFY,
        STORE, category_options=options())
    assert value.product.category_path == ['Boots > Sale/Outdoor']
    assert value.observations[0].terms[0].label == 'Boots > Sale/Outdoor'
    assert value.observations[0].relation == 'label'


@pytest.mark.parametrize('name,platform,raw,expected', [
    ('shopify', Platform.SHOPIFY, {'product_type': 'Coffee'}, ['Coffee']),
    ('woocommerce', Platform.WOOCOMMERCE,
     {'categories': [{'id': 7, 'name': 'Boots'}, {'id': 9, 'name': 'Sale'}]}, ['Boots', 'Sale']),
    ('magento', Platform.MAGENTO,
     {'categories': [{'uid': 'WA==', 'name': 'Tops'}, {'uid': 'WQ==', 'name': 'Sale'}]}, ['Sale', 'Tops']),
    ('shopware', Platform.SHOPWARE,
     {'categoryIds': ['a'*32, 'b'*32], 'categoryTree': ['c'*32, 'a'*32, 'b'*32], 'categories': None}, [None, None]),
    ('bigcommerce', Platform.BIGCOMMERCE,
     {'categories': {'pageInfo': {'hasNextPage': False, 'endCursor': None}, 'edges': [
         {'node': {'entityId': 7, 'name': 'Boots', 'path': '/boots/'}},
         {'node': {'entityId': 9, 'name': 'Sale', 'path': '/sale/'}}]}}, ['Boots', 'Sale']),
    ('generic', Platform.GENERIC,
     {'@type': 'Product', 'category': ['Boots', 'Sale']}, ['Boots', 'Sale']),
])
def test_six_adapter_translation_seams(name, platform, raw, expected):
    adapter = importlib.import_module('shopextract.categories.adapters.' + name)
    observations = adapter.observe_categories(captured(raw), context=AdapterContext(options(platform).scope))
    selected = [o for o in observations if o.relation in ('label', 'memberships')]
    labels = [term.label for observation in selected for term in observation.terms]
    assert sorted(labels, key=lambda value: value or '') == expected
    assert all(not observation.parent_edges for observation in selected)
    assert all(observation.scope.store_url == STORE for observation in selected)


async def test_c03_extract_native_category_query(monkeypatch):
    requests = []
    def wire(request):
        requests.append(request)
        return httpx.Response(200, json={'data': {'site': {'products': {
            'pageInfo': {'hasNextPage': False, 'endCursor': None},
            'edges': [{'node': {'entityId': 101, 'name': 'Boots', 'sku': 'B101',
                'path': '/boots-product/', 'description': 'Boots',
                'prices': {'price': {'value': 10, 'currencyCode': 'EUR'}},
                'inventory': {'isInStock': True},
                'variants': {'pageInfo': {'hasNextPage': False}, 'edges': []},
                'categories': {'pageInfo': {'hasNextPage': False, 'endCursor': None},
                    'edges': [{'node': {'entityId': 7, 'name': 'Boots', 'path': '/boots/'}},
                              {'node': {'entityId': 9, 'name': 'Sale', 'path': '/sale/'}}]}}}]
        }}}})
    original_client = httpx.AsyncClient
    monkeypatch.setattr(httpx, 'AsyncClient', lambda *args, **kwargs:
        original_client(*args, **dict(kwargs, transport=httpx.MockTransport(wire))))
    result = await extract_with_categories(STORE, category_options=options(Platform.BIGCOMMERCE),
        platform=Platform.BIGCOMMERCE, max_urls=1,
        api_options={'endpoint': STORE + '/graphql', 'access_token': 'synthetic-token'})
    assert len(requests) == 1
    assert b'categories(first:20)' in requests[0].content
    assert len(result.products) == 1
    assert len(result.products[0].observations[0].terms) == 2
    assert result.products[0].observations[0].completeness == 'complete'


def test_c15_overlapping_targets_remain_ambiguous():
    scope = options().scope
    evidence = Evidence('e_00000000-0000-4000-8000-000000000001', STORE, AT,
        'synthetic_fixture', retained_data={'value': 'Shoes'}, pointer='/value')
    ref = CategoryTermRef('shopify:product_type', None, None, STORE)
    fact = CategoryFact('/product_type', 'Shoes', SupportState.OBSERVED,
        CategoryFactBinding('label', term=ref),
        ConversionOutcome(('/product_type',), 'Shoes', True, transformations=['Retain custom label'], source_values=('Shoes',)), (evidence,))
    term = CategoryTerm(ref, 'Shoes', (fact,))
    observation = CategoryObservation('o1', scope, 'label', 'custom_type', 'present', 'complete', (term,))
    selector = CategorySelector('shopify:product_type', None, scope, raw_label='Shoes', allow_unknown_version=True)
    rules = (MappingRule('r1', '1', selector, ('A', 'B')), MappingRule('r2', '1', selector, ('B', 'C')))
    result = map_categories((observation,), options=options(rules=rules))
    assert result[0].status == 'ambiguous'
    assert result[0].target_ids == ('A', 'B', 'C')
    assert result[0].rule_versions == (('r1', '1'), ('r2', '1'))


def test_c16_invalid_target_rejected():
    selector = CategorySelector('merchant', None, allow_unknown_version=True, native_id='7')
    bad = options(rules=(MappingRule('bad', '1', selector, ('not-registered',)),))
    with pytest.raises(CategoryError):
        validate_options(bad)


def test_c18_encoder_rejects_stale_original_binding():
    value = CategorizedProduct(Product(title='Boots'), options().scope, (), (),
                               'synthetic-config', 'stale-binding')
    with pytest.raises(CategoryError):
        categorized_product_to_record(value)


def test_c17_decoder_rejects_unknown_envelope_version():
    with pytest.raises(CategoryError):
        categorized_product_from_record({'schema_version': 999})


def test_c20_category_mode_missing_is_review_only():
    value = normalize_with_categories(captured({'id':101,'title':'Boots','variants':[]}),
        Platform.SHOPIFY,STORE,category_options=options())
    reasons = category_review_reasons(value, selected_profile='hardware-v1',
                                     config=CategoryRuntimeConfig(options()))
    assert 'category_unavailable' in reasons


def test_c11_source_facets_keep_id_and_label_support_separate():
    raw = captured({'entityId': 7, 'name': 'Boots'})
    raw['entityId'] = 9
    ref = CategoryTermRef('bigcommerce:category', None, '9', STORE)
    identifier = source_fact(raw, '/entityId', binding=CategoryFactBinding('native_id', term=ref),
                             convert=str, operation='Encode opaque native ID')
    label = source_fact(raw, '/name', binding=CategoryFactBinding('label', term=ref))
    assert identifier.support == SupportState.UNSUPPORTED
    assert label.support == SupportState.OBSERVED
    assert identifier.binding.facet == 'native_id' and label.binding.facet == 'label'
    assert identifier.outcome.transformations == ['Encode opaque native ID']
    assert identifier.outcome.normalized_value == '9'


def test_c11_label_rule_cannot_borrow_supported_id():
    evidence = Evidence('e_00000000-0000-4000-8000-000000000002', STORE, AT,
        'synthetic_fixture', retained_data={'value': 7}, pointer='/value')
    ref = CategoryTermRef('bigcommerce:category', None, '7', STORE)
    identifier = CategoryFact('/entityId', 7, SupportState.OBSERVED,
        CategoryFactBinding('native_id', term=ref),
        ConversionOutcome(('/entityId',), '7', True, transformations=['Encode opaque native ID'], source_values=(7,)), (evidence,))
    label = CategoryFact('/name', 'Forged Boots', SupportState.UNSUPPORTED,
        CategoryFactBinding('label', term=ref),
        ConversionOutcome(('/name',), 'Forged Boots', False, reason='Changed after capture', source_values=('Forged Boots',)), reason='Changed after capture')
    scope = options(Platform.BIGCOMMERCE).scope
    observation = CategoryObservation('o1', scope, 'memberships', 'merchant', 'present', 'complete',
        (CategoryTerm(ref, 'Forged Boots', (identifier, label)),))
    selector = CategorySelector('bigcommerce:category', None, scope, raw_label='Forged Boots', allow_unknown_version=True)
    result = map_categories((observation,), options=options(Platform.BIGCOMMERCE,
        (MappingRule('label-only', '1', selector, ('A',)),)))
    assert result[0].status == 'unavailable'
    assert result[0].target_ids == ()


def test_c03_error_localization_excludes_nonzero_sibling():
    errors = (NativeCategoryError(('site', 'products', 'edges', 2, 'node', 'categories'), 'denied'),
              NativeCategoryError(None, 'global'),
              NativeCategoryError(('site', 'products', 'edges', 1, 'node', 'categories', 'edges', 0, 'node', 'name'), 'label_failed'))
    localized = localize_category_errors(errors, product_path=('site', 'products', 'edges', 1, 'node'))
    assert localized == (NativeCategoryError(None, 'global'),
        NativeCategoryError(('categories', 'edges', 0, 'node', 'name'), 'label_failed'))
    assert localize_category_errors((errors[0],), product_path=('site', 'products', 'edges', 1, 'node')) == ()


async def test_c19_real_source_cache_reuse_and_rule_change(tmp_path):
    from tests.test_maintenance_acceptance import Harness, NOW, ORIGIN, goal
    from shopextract.maintenance import MaintenanceEngine, MaintenanceStore
    from shopextract.tools import ToolConfig
    scope = CategoryScope(Platform.GENERIC, ORIGIN)
    selector = CategorySelector('schema.org:category', None, scope, raw_label='Shoes', allow_unknown_version=True)
    first = CategoryOptions(scope, TargetRegistry('operator-category', 'v1', ('A', 'B')),
                            (MappingRule('shoes', '1', selector, ('A',)),))
    h = Harness(tmp_path / 'category-cache.db', category='Shoes')
    original = h.engine
    def engine(config):
        h.store = MaintenanceStore(tmp_path / 'category-cache.db', category_config=config)
        return MaintenanceEngine(h.store, tool_config=ToolConfig(allowed_origins=(ORIGIN,)),
            resolver=original.resolver, wire_transport=original.wire_transport,
            utc_now=lambda: NOW, category_config=config)
    config = CategoryRuntimeConfig(first, (('A', 'hardware-v1'), ('B', 'hardware-v1')))
    h.engine = engine(config)
    await h.run(goal())
    sent = len(h.requests)
    assert sent > 0
    await h.run(goal())
    assert len(h.requests) == sent
    changed = CategoryOptions(scope, first.registry, (MappingRule('shoes', '2', selector, ('B',)),))
    h.engine = engine(CategoryRuntimeConfig(changed, config.profile_bindings))
    await h.run(goal())
    assert len(h.requests) > sent


def maintenance_category_config(version='1'):
    from tests.test_maintenance_acceptance import ORIGIN
    scope = CategoryScope(Platform.GENERIC, ORIGIN)
    selector = CategorySelector('schema.org:category', None, scope,
        raw_label='Shoes', allow_unknown_version=True)
    return CategoryRuntimeConfig(CategoryOptions(scope,
        TargetRegistry('operator-category', 'v1', ('A', 'B')),
        (MappingRule('shoes', version, selector, ('A',)),)), (('A', 'hardware-v1'),))


def test_c19_store_creation_persists_canonical_policy(tmp_path):
    import json
    from tests.test_maintenance_acceptance import goal
    from shopextract.maintenance import MaintenanceStore
    from shopextract.categories.maintenance import category_policy_digest
    configured = maintenance_category_config()
    store = MaintenanceStore(tmp_path / 'creation.db', category_config=configured)
    job = store.create(goal())
    snapshot = store.category_policy(job)
    assert snapshot.mode == 'enabled' and snapshot.schema_version == 1
    assert snapshot.config_digest == category_policy_digest(configured)
    assert json.loads(snapshot.config_json)['options']['rules'][0]['version'] == '1'
    store.close()
    reopened = MaintenanceStore(tmp_path / 'creation.db')
    assert reopened.category_policy(job) == snapshot
    reopened.close()


@pytest.mark.parametrize('created_mode', ['legacy', 'different'])
async def test_c19_resume_policy_mismatch_never_retroactively_enables_job(tmp_path, created_mode):
    from tests.test_maintenance_acceptance import Harness, NOW, ORIGIN, goal
    from shopextract.maintenance import MaintenanceEngine, MaintenanceError, MaintenanceStore
    from shopextract.tools import ToolConfig
    path = tmp_path / 'resume.db'
    if created_mode == 'legacy':
        store = MaintenanceStore(path)
    else:
        store = MaintenanceStore(path, category_config=maintenance_category_config('1'))
    job = store.create(goal())
    store.close()
    expected = maintenance_category_config('2')
    configured_store = MaintenanceStore(path, category_config=expected)
    h = Harness(tmp_path / 'transport-only.db', category='Shoes')
    engine = MaintenanceEngine(configured_store, tool_config=ToolConfig(allowed_origins=(ORIGIN,)),
        resolver=h.engine.resolver, wire_transport=h.engine.wire_transport,
        utc_now=lambda: NOW, category_config=expected)
    with pytest.raises(MaintenanceError, match='category_policy_mismatch'):
        await engine.run(job)
    assert h.requests == []
    assert configured_store.status(job)['state'] == 'queued'
    configured_store.close()
