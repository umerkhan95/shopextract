"""Predesigned money/compact transport acceptance; no production stubs."""
import hashlib
import importlib
import json
from decimal import Decimal

import pytest
from shopextract._normalization import Normalizer
from shopextract._normalize import _normalize_shopify,normalize
from shopextract._models import Product,Platform,ExtractionResult
from shopextract._capture import capture
from shopextract._cli_data import extraction_data,read_json_file
from shopextract._cli_core import CliFailure


@pytest.mark.parametrize('currency',[None,'','MISSING','USD'])
def test_currency_support_not_default(currency):
    raw={'id':1,'title':'Widget','variants':[{'id':2,'price':'1'}]}
    if currency!='MISSING':raw['currency']=currency
    data=_normalize_shopify(raw,'https://fixture.invalid')
    assert data['currency']==('USD' if currency=='USD' else '')
    assert data.outcomes['/currency'].accepted is (currency=='USD')
    if currency!='USD':assert data.outcomes['/currency'].reason
    else:assert data.outcomes['/currency'].source_paths==('/currency',)


def test_product_constructor_currency_unchanged():
    assert Product().currency=='USD'


@pytest.mark.parametrize('value,currency,locale,expected',[
    ('3,720','PKR',None,'3720'),('Rs. 3,720',None,None,'3720'),
    ('3,720.00','USD',None,'3720'),('3.720,00','EUR','de-DE','3720'),
    ('3,720',None,None,None),('3,720','KWD','de-DE','3.720'),
    ('3,72','EUR','de-DE','3.72')])
def test_css_context_money(value,currency,locale,expected):
    n=Normalizer({'price':value})
    result=n.money('price','/price',css=True,currency=currency,locale=locale)
    outcome=n.outcomes['/price']
    assert outcome.accepted is (expected is not None)
    if expected is not None:assert result==Decimal(expected)
    else:assert outcome.reason


@pytest.mark.parametrize('value',['1,23,4','NaN','-1'])
def test_bad_money_not_observed_zero(value):
    n=Normalizer({'price':value});n.money('price','/price',css=True)
    assert n.outcomes['/price'].accepted is False
    assert n.outcomes['/price'].reason


def test_zero_price_observed_with_diagnostic():
    n=Normalizer({'price':'0'});value=n.money('price','/price',css=True)
    assert value==0 and n.outcomes['/price'].accepted
    assert 'zero' in n.outcomes['/price'].reason.lower()


def codec():return importlib.import_module('shopextract._compact_catalog')
def canonical(value):return json.dumps(value,sort_keys=True,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()

def envelope(body,count=2):
    digest=hashlib.sha256(canonical(body)).hexdigest()
    return {'schema_version':'catalog-1','data':{'products':[],
        'raw_products':[{'_capture':{'$capture_ref':digest}} for _ in range(count)]},
        'captures':{digest:body}}


def test_compact_real_capture_evidence_variant_roundtrip():
    raw=capture({'id':1,'title':'Widget','handle':'widget','currency':'PKR',
        'variants':[{'id':2,'price':'1.20','barcode':'036000291452','available':True}]},
        'https://fixture.invalid/products/widget','shopify_api',observed_at='2026-11-01T00:00:00+00:00')
    product=normalize(raw,Platform.SHOPIFY,'https://fixture.invalid')
    data=extraction_data(ExtractionResult(products=[product],raw_products=[raw]))
    c=codec();wire=c.encode_compact_catalog(data)
    assert json.loads(wire)['schema_version']=='catalog-1'
    assert c.decode_compact_catalog(wire)==data
    assert len(wire)<len(canonical(data))


@pytest.mark.parametrize('delta',[-1,0,1])
def test_expanded_byte_budget_repeated_refs(delta):
    c=codec();body={'values':{'/description':'x'*2048}}
    wire=envelope(body,20);expanded={'products':[],'raw_products':[{'_capture':body} for _ in range(20)]}
    limit=len(canonical(expanded))+delta
    limits=c.CompactLimits(max_expanded_bytes=limit)
    if delta<0:
        with pytest.raises(ValueError):c.decode_compact_catalog(canonical(wire),limits=limits)
    else:assert c.decode_compact_catalog(canonical(wire),limits=limits)==expanded


@pytest.mark.parametrize('limit',[117,118,119])
def test_expanded_node_budget_repeated_refs(limit):
    # Expanded3 +5*(record1+capture1+valueslist1+20leaves)=118;wire<118.
    c=codec();wire=envelope({'values':list(range(20))},5)
    if limit<118:
        with pytest.raises(ValueError):c.decode_compact_catalog(canonical(wire),limits=c.CompactLimits(max_nodes=limit))
    else:assert len(c.decode_compact_catalog(canonical(wire),limits=c.CompactLimits(max_nodes=limit))['raw_products'])==5


@pytest.mark.parametrize('limit',[5,6,7])
def test_expanded_depth_budget(limit):
    # Expanded root0/rawlist1/record2/capture3/values4/nested5/leaf6;wire depth5.
    c=codec();wire=envelope({'values':{'nested':['leaf']}},1)
    if limit<6:
        with pytest.raises(ValueError):c.decode_compact_catalog(canonical(wire),limits=c.CompactLimits(max_depth=limit))
    else:assert c.decode_compact_catalog(canonical(wire),limits=c.CompactLimits(max_depth=limit))['raw_products']


@pytest.mark.parametrize('kind',['dangling','hash','nested','self_cycle','cross_cycle','duplicate'])
def test_compact_invalid_reference_tables(kind):
    c=codec();e=envelope({'values':{'/title':'Widget'}});digest=next(iter(e['captures']))
    if kind=='dangling':e['captures']={}
    elif kind=='hash':e['captures'][digest]['values']['/title']='Changed'
    elif kind=='nested':e=envelope({'values':{'$capture_ref':'external'}})
    elif kind=='self_cycle':e['captures'][digest]={'$capture_ref':digest}
    elif kind=='cross_cycle':e['captures'][digest]={'$capture_ref':'other'};e['captures']['other']={'$capture_ref':digest}
    payload=canonical(e)
    if kind=='duplicate':payload=payload.replace(b'"captures":{',b'"captures":{},"captures":{',1)
    with pytest.raises(ValueError):c.decode_compact_catalog(payload)


@pytest.mark.parametrize('size',[32*1024*1024-1,32*1024*1024,32*1024*1024+1])
def test_reader_wire_byte_boundary(tmp_path,size):
    path=tmp_path/'bounded.json';path.write_bytes(b'"'+b'x'*(size-2)+b'"')
    if size>32*1024*1024:
        with pytest.raises(CliFailure):read_json_file(str(path))
    else:assert len(read_json_file(str(path)))==size-2


def test_compliant_large_legacy_file(tmp_path):
    size=5_400_000;path=tmp_path/'legacy.json'
    path.write_bytes(b'{"products":[],"note":"'+b'x'*size+b'"}')
    result=read_json_file(str(path))
    assert result['products']==[] and len(result['note'])==size


@pytest.mark.parametrize('raw_currency,text,expected_currency',[('PKR','3,720','PKR'),(None,'Rs. 3,720','')])
def test_actual_css_money_currency_projection(raw_currency,text,expected_currency):
    raw={'title':'Widget','price':text}
    if raw_currency:raw['currency']=raw_currency
    p=normalize(raw,Platform.GENERIC,'https://fixture.invalid')
    assert p.price==Decimal('3720') and p.currency==expected_currency
    from shopextract._normalize import _normalize_css_generic
    out=_normalize_css_generic(raw,'https://fixture.invalid').outcomes['/currency']
    assert out.accepted is bool(raw_currency) and out.source_paths==('/currency',)


from tests.test_truthful_outcomes import cli_transport

def test_actual_extract_compact_cli(cli_transport):
    from click.testing import CliRunner
    from shopextract.cli import main
    result=CliRunner().invoke(main,['--output-format','json','extract',
        'https://fixture.invalid','--platform','shopify','--max','2','--compact'])
    assert result.exit_code==0,result.output[:300]
    response=json.loads(result.stdout)
    assert response['schema_version']=='1.0' and response['ok']
    assert response['data']['schema_version']=='catalog-1'
    assert codec().decode_compact_catalog(canonical(response['data']))['product_count']==1


CURRENCY_BRANCHES=[
 ('_normalize_woocommerce',{'name':'Widget','prices':{'price':'100'}},'/prices/currency_code'),
 ('_normalize_woocommerce',{'name':'Widget','price':'1','_source':'woocommerce_admin_api'},'/currency'),
 ('_normalize_magento',{'name':'Widget','price':'1'},'/currency'),
 ('_normalize_magento_graphql',{'name':'Widget','price_range':{'minimum_price':{'final_price':{'value':'1'}}}},'/price_range/minimum_price/final_price/currency'),
 ('_normalize_shopware_store_api',{'name':'Widget','calculatedPrice':{'unitPrice':'1'}},'/currency'),
 ('_normalize_shopware',{'name':'Widget','price':'1'},'/currency'),
 ('_normalize_bigcommerce',{'entityId':1,'name':'Widget','prices':{'price':{'value':'1'}}},'/prices/price/currencyCode'),
 ('_normalize_schema_org',{'@type':'Product','name':'Widget','offers':{'price':'1'}},'/offers/priceCurrency'),
 ('_normalize_opengraph',{'og:type':'product','og:title':'Widget','product:price:amount':'1'},'/product:price:currency'),
 ('_normalize_google_feed',{'title':'Widget','price':'1'},'/currency'),
]


@pytest.mark.parametrize('helper,fixture,path',CURRENCY_BRANCHES)
@pytest.mark.parametrize('present',[False,True])
def test_every_currency_dispatcher_missing_valid(helper,fixture,path,present):
    raw=json.loads(json.dumps(fixture))
    if present:
        owner=raw;tokens=path[1:].split('/')
        for token in tokens[:-1]:owner=owner.setdefault(token,{})
        owner[tokens[-1]]='USD'
    import shopextract._normalize as module
    data=getattr(module,helper)(raw,'https://fixture.invalid')
    assert data['currency']==('USD' if present else '')
    outcome=data.outcomes['/currency']
    assert outcome.accepted is present
    assert outcome.source_paths==(path,)
    if present:assert outcome.source_values==('USD',)
    else:assert outcome.reason


@pytest.mark.parametrize('raw,expected,accepted',[
 ({'title':'Widget','price':'1','currency':'pkR'},'PKR',True),
 ({'title':'Widget','price':'1','currency':'NOPE'},'',False),
 ({'title':'Widget','id':1,'currency':'USD','variants':[{'id':2,'price':'1','price_currency':'PKR'}]},'',False)])
def test_currency_lower_invalid_conflict(raw,expected,accepted):
    from shopextract._normalize import _normalize_css_generic
    conflict='variants' in raw
    data=_normalize_shopify(raw,'https://fixture.invalid') if conflict else _normalize_css_generic(raw,'https://fixture.invalid')
    assert data['currency']==expected
    out=data.outcomes['/currency'];assert out.accepted is accepted
    if conflict:
        assert set(out.source_paths)=={'/variants/0/price_currency','/currency'} and 'conflict' in out.reason.lower()
    else:assert out.source_paths==('/currency',)
    if not accepted:assert out.reason


def test_full_compact_reader_downstream_literal_and_atomic_output(monkeypatch,tmp_path):
    import httpx
    from click.testing import CliRunner
    from shopextract.cli import main
    from shopextract._cli_data import products_from_value
    literal={'$capture_ref':'0'*64};original=httpx.AsyncClient
    raw={'id':1,'title':'Widget','handle':'widget','currency':'PKR','body_html':'Source description',
        'images':[{'src':'https://fixture.invalid/i.png'}],'custom':literal,
        'variants':[{'id':2,'price':'1.20','available':True}]}
    def factory(*a,**kw):
        kw['transport']=httpx.MockTransport(lambda r:httpx.Response(200,json={'products':[raw]}))
        return original(*a,**kw)
    monkeypatch.setattr(httpx,'AsyncClient',factory)
    args=['--output-format','json','extract','https://fixture.invalid','--platform','shopify','--max','2','--compact']
    result=CliRunner().invoke(main,args);assert result.exit_code==0,result.output[:300]
    path=tmp_path/'compact.json';path.write_text(result.stdout)
    projected=products_from_value(read_json_file(str(path)))
    assert len(projected)==1 and projected[0].price==Decimal('1.20')
    assert projected[0].variants[0].variant_id=='2' and projected[0].variants[0].price==Decimal('1.20')
    assert projected[0].evidence_contract.evidence
    assert projected[0].raw_data['custom']==literal
    assert projected[0].raw_data['_capture']['values']['/custom']==literal
    downstream=CliRunner().invoke(main,['--output-format','json','analyze-file',str(path)])
    assert downstream.exit_code==0,downstream.output[:300]
    stats=json.loads(downstream.stdout)['data']['statistics']
    assert stats['total_products']==1 and stats['currencies']=={'PKR':1}
    target=tmp_path/'preserve.json';target.write_text('sentinel')
    def failed_replace(*a):raise OSError('Synthetic filesystem replacement failure')
    monkeypatch.setattr('shopextract._cli_data.os.replace',failed_replace)
    failed=CliRunner().invoke(main,[*args,'-o',str(target)])
    assert failed.exit_code==1 and json.loads(failed.stdout)['error']['code']=='E_OPERATION'
    assert target.read_text()=='sentinel'


def test_invalid_compact_input_preserves_export_target(tmp_path):
    from click.testing import CliRunner
    from shopextract.cli import main
    wire=envelope({'values':[]});wire['captures']={}
    source=tmp_path/'invalid.json';source.write_bytes(canonical(wire))
    target=tmp_path/'existing.json';target.write_text('sentinel')
    result=CliRunner().invoke(main,['--output-format','json','export',str(source),'--format','json','-o',str(target)])
    assert result.exit_code==2 and json.loads(result.stdout)['error']['code']=='E_USAGE'
    assert target.read_text()=='sentinel'
