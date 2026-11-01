"""Design-first amendment reds; scanner/registry interfaces intentionally absent."""
import importlib
import json
import re
from decimal import Decimal

import pytest
from shopextract._normalization import Normalizer
from shopextract._cli_data import read_json_file,products_from_value
from shopextract._cli_core import CliFailure
from shopextract._compact_catalog import decode_compact_catalog
from tests.test_money_roundtrip import envelope,canonical


@pytest.mark.parametrize('code',['QQQ','ZZZ'])
def test_iso_membership_not_lexical(code):
    n=Normalizer({'currency':code});assert n.currency('currency','/currency')==''
    assert not n.outcomes['/currency'].accepted


def test_iso_registry_traceability():
    registry=importlib.import_module('shopextract._currencies')
    assert 'six-group.com' in registry.REGISTRY_SOURCE
    assert registry.REGISTRY_VERSION=='2026-09-17'
    assert registry.REGISTRY_SHA256=='33139b438657d1cee116ba737807ea71d19d6de4b90f799a09c56f0cc6a1b0ff'
    assert all(registry.is_pricing_currency(c) for c in ('USD','PKR','KWD'))
    for code in ('XXX','XTS'):
        assert not registry.is_pricing_currency(code)
        n=Normalizer({'currency':code})
        assert n.currency('currency','/currency')=='' and not n.outcomes['/currency'].accepted


@pytest.mark.parametrize('slot',['title','price','raw_source'])
def test_transport_reference_forbidden_outside_provenance(slot):
    e=envelope({'values':{'/title':'Widget'}});digest=next(iter(e['captures']))
    from shopextract._models import Product
    from shopextract._portable import product_to_record
    record=product_to_record(Product(title='Widget',price=Decimal('1.25')))
    e['data']['products']=[record]
    if slot=='raw_source':record['product']['raw_data']={'merchant_attribute':{'$capture_ref':digest}}
    else:record['product'][slot]={'$capture_ref':digest}
    with pytest.raises(ValueError):decode_compact_catalog(canonical(e))


def scan(payload,**limits):return importlib.import_module('shopextract._bounded_json').preflight_catalog_json(payload,**limits)

def test_scanner_escape_and_shape():
    result=scan(canonical({'a':['\\"{[}',True,None,1.25]}))
    assert (result.nodes,result.keys,result.tokens,result.depth)==(6,1,7,2)


@pytest.mark.parametrize('nodes',[999999,1000000,1000001])
def test_scanner_hard_node_boundary(nodes):
    payload=b'['+b'0,'*(nodes-2)+b'0]'
    if nodes>1000000:
        with pytest.raises(ValueError):scan(payload)
    else:assert scan(payload).nodes==nodes


@pytest.mark.parametrize('depth',[63,64,65])
def test_scanner_depth_boundary(depth):
    payload=b'['*depth+b'0'+b']'*depth
    if depth>64:
        with pytest.raises(ValueError):scan(payload)
    else:assert scan(payload).depth==depth


def test_dense_input_rejected_before_full_decoder(monkeypatch,tmp_path):
    path=tmp_path/'dense.json';path.write_bytes(b'['+b'{},'*1000000+b'{}]')
    def prohibited(*a,**kw):raise AssertionError('Full decoder allocated before lexical budget rejection')
    monkeypatch.setattr('shopextract._cli_data.json.loads',prohibited)
    with pytest.raises(CliFailure):read_json_file(str(path))


def test_high_node_portable_shaped_real_projection(tmp_path):
    from shopextract._models import Product,Variant
    from shopextract._portable import product_to_record
    p=Product(title='Synthetic bounded catalog',price=Decimal('1.25'),variants=[Variant(variant_id='v1',price=Decimal('1.25'))])
    p.raw_data={'rows':[{'v':i} for i in range(100000)]}
    path=tmp_path/'portable.json';path.write_bytes(canonical([product_to_record(p)]))
    projected=products_from_value(read_json_file(str(path)))
    assert len(projected)==1 and projected[0].price==Decimal('1.25')
    assert projected[0].variants[0].variant_id=='v1' and len(projected[0].raw_data['rows'])==100000


def test_portable_and_catalog_node_budget_aligned():
    from shopextract._portable import MAX_PORTABLE_NODES
    assert MAX_PORTABLE_NODES>=1000000


def test_native_woo_tree_default_not_increased_by_catalog_budget(monkeypatch,tmp_path):
    from click.testing import CliRunner
    from shopextract.cli import main
    from tests.test_cli_categories import fixture_files,install_transport
    files=fixture_files(tmp_path);install_transport(monkeypatch)
    result=CliRunner().invoke(main,['--output-format','json','categories','tree','fetch',
        '--options',files['options'],'--output',str(tmp_path/'tree.json')])
    assert result.exit_code==0,result.output[:300]
    assert (tmp_path/'tree.json').exists()


def test_direct_compact_dense_rejected_before_full_decoder(monkeypatch):
    payload=(b'{"schema_version":"catalog-1","captures":{},"data":{"products":[],"raw_products":['
             +b'{},'*1000000+b'{}]}}')
    def prohibited(*a,**kw):raise AssertionError('Compact decoder allocated before lexical budget rejection')
    monkeypatch.setattr('shopextract._compact_catalog.json.loads',prohibited)
    with pytest.raises(ValueError):decode_compact_catalog(payload)
