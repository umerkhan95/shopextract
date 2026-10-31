"""Directional source-index acceptance; fixtures use real immutable catalogs."""
from hashlib import sha256
from types import MappingProxyType, SimpleNamespace
import importlib
import json

import pytest

from shopextract.taxonomies.shopify.catalog import ShopifyTaxonomy
from shopextract.taxonomies.shopify.contracts import CategoryRecord


def operation(name):
    module = importlib.import_module('shopextract.taxonomies.google')
    value = getattr(module, name, None)
    assert callable(value), f'Google integration callable {name} is missing'
    return value


def source_catalog(fingerprint='a' * 64):
    categories = {}
    aliases = {}
    for short in ('a', 'b', 'c', 'd'):
        node = CategoryRecord('gid://shopify/TaxonomyCategory/' + short, short,
                              short, short, 0, None, (), (), ())
        categories[node.id] = node
        aliases[node.id] = aliases[short] = node
    empty = MappingProxyType({})
    return ShopifyTaxonomy(SimpleNamespace(release='2026-08', fingerprint=fingerprint),
                           MappingProxyType(categories), empty, empty,
                           MappingProxyType(aliases), empty, empty, empty, empty)


def target_catalog():
    return operation('parse_google_taxonomy')(
        '# Google_Product_Taxonomy_Version: 2021-09-21\n1 - Animals\n2 - Electronics\n')


def row(source, targets):
    return {'input': {'product_category_id': source},
            'output': {'product_category_id': targets}}


def document():
    return {'input_taxonomy': 'shopify/2026-08', 'output_taxonomy': 'google/2021-09-21',
            'rules': [row('a', ['1']), row('b', ['1', '2'])],
            'unmapped_product_category_ids': ['c']}


def load(tmp_path, value=None, *, text=None, expected=None):
    # Assert the intended missing interface before source parser is invoked.
    loader = operation('load_shopify_google_crosswalk')
    data = (json.dumps(document() if value is None else value) if text is None else text).encode()
    path = tmp_path / 'crosswalk.yml'
    path.write_bytes(data)
    return loader(path, source_catalog=source_catalog(), target_catalog=target_catalog(),
                  expected_sha256=expected or sha256(data).hexdigest())


def test_crosswalk_direction_endpoints_and_disjoint_ledger(tmp_path):
    index = load(tmp_path)
    assert index.rules['a'] == ('1',)
    assert index.rules['b'] == ('1', '2')
    with pytest.raises(TypeError):
        index.rules['a'] = ('2',)
    ledger = operation('audit_source_categories')(index, source_catalog())
    assert [(d.source_id, d.status, d.target_ids) for d in ledger] == [
        ('a', 'mapped-single', ('1',)), ('b', 'mapped-multiple', ('1', '2')),
        ('c', 'explicit-upstream-unmapped', ()), ('d', 'missing-rule', ())]


@pytest.mark.parametrize('change', ['source-version', 'target-version', 'source-id', 'target-id',
                                    'empty-target', 'exclusion-conflict', 'extra-root', 'bad-type'])
def test_crosswalk_invalid_source_never_activates(tmp_path, change):
    value = document()
    if change == 'source-version': value['input_taxonomy'] = 'shopify/2025-01'
    elif change == 'target-version': value['output_taxonomy'] = 'google/2020-01-01'
    elif change == 'source-id': value['rules'][0]['input']['product_category_id'] = 'outside'
    elif change == 'target-id': value['rules'][0]['output']['product_category_id'] = ['999']
    elif change == 'empty-target': value['rules'][0]['output']['product_category_id'] = []
    elif change == 'exclusion-conflict': value['unmapped_product_category_ids'].append('a')
    elif change == 'extra-root': value['extra'] = True
    elif change == 'bad-type': value['rules'][0]['output']['product_category_id'] = [True]
    with pytest.raises(ValueError):
        load(tmp_path, value)


def test_crosswalk_identical_duplicate_diagnostic_and_conflicting_duplicate_rejection(tmp_path):
    value = document()
    value['rules'].append(row('a', ['1']))
    index = load(tmp_path, value)
    assert index.duplicate_rows == 1
    value['rules'].append(row('a', ['2']))
    with pytest.raises(ValueError):
        load(tmp_path, value)


@pytest.mark.parametrize('text', [
    '{"input_taxonomy":"shopify/2026-08","input_taxonomy":"shopify/2026-08"}',
    'input_taxonomy: shopify/2026-08\ninput_taxonomy: shopify/2026-08\n',
    'input_taxonomy: &x shopify/2026-08\noutput_taxonomy: *x\n',
    '!!python/object/apply:os.system [false]',
])
def test_crosswalk_duplicate_keys_aliases_and_objects_rejected(tmp_path, text):
    with pytest.raises(ValueError):
        load(tmp_path, text=text)


def test_crosswalk_source_digest_and_ledger_fingerprint_required(tmp_path):
    with pytest.raises(ValueError):
        load(tmp_path, expected='0' * 64)
    index = load(tmp_path)
    with pytest.raises(ValueError):
        operation('audit_source_categories')(index, source_catalog('b' * 64))


def test_crosswalk_source_byte_limit_precedes_parse(tmp_path):
    loader = operation('load_shopify_google_crosswalk')
    path = tmp_path / 'large.yml'
    path.write_bytes(b' ' * (8 * 1024 * 1024 + 1))
    with pytest.raises(ValueError):
        loader(path, source_catalog=source_catalog(), target_catalog=target_catalog(),
               expected_sha256='0' * 64)
