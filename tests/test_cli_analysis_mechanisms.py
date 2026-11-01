"""Deterministic P2 mechanisms; mocks replace transport only, never algorithms."""
import asyncio
import importlib
import json
import os
from decimal import Decimal
from pathlib import Path

import pytest
from click.testing import CliRunner
from shopextract.cli import main
from shopextract._models import Product,Variant,ExtractionResult
from shopextract._portable import product_to_record,product_from_record
from shopextract._cli_data import catalog_from_value,MAX_BYTES

GTIN='00012345600012'


def call(args,value=None):
    return CliRunner().invoke(main,args,input=None if value is None else json.dumps(value))


def data(result,exit=0):
    assert result.exit_code==exit,result.output
    return json.loads(result.output)['data']


def record(**kw):
    return dict(title='Widget',price='0.10',currency='USD',gtin=GTIN,**kw)


def extracted(raw,complete=True):
    return ExtractionResult(products=[Product(title=r.get('title','Widget'),price=Decimal(str(r.get('price',0))),currency=r.get('currency','USD'),gtin=r.get('gtin'),raw_data=dict(r)) for r in raw],raw_products=raw,catalog_complete=complete)


@pytest.fixture
def transport(monkeypatch):
    calls=[];responses={}
    async def fetch(url,**options):
        calls.append((url,options))
        response=responses[url]
        if isinstance(response,Exception):raise response
        if callable(response):return await response()
        return response
    for module in ('shopextract','shopextract._extract','shopextract.compare.price','shopextract.compare.catalog'):
        monkeypatch.setattr(importlib.import_module(module),'extract',fetch)
    return calls,responses


def test_compare_groups_provenance_partial_and_controls(transport):
    calls,responses=transport
    responses.update({'https://usd.test':extracted([record()]),'https://eur.test':extracted([dict(title='Widget',price='0.05',currency='EUR')]),'https://unknown.test':extracted([dict(title='Widget',price='0.01')]),'https://bad.test':OSError('source unavailable')})
    args=['--output-format','json','compare','Widget','--max-per-store','2','--threshold','0.6']
    for url in responses:args+=['--stores',url]
    report=data(call(args),3)
    assert set(report['currency_groups'])=={'USD','EUR'}
    assert report['currency_groups']['USD']['cheapest']['price']['value']=='0.10'
    assert report['unranked'][0]['currency']==''
    assert len(report['sources'])==4 and report['sources'][-1]['usable'] is False
    assert len(calls)==4 and all(c[1]['max_urls']==2 for c in calls)
    assert 'cheapest' not in report


def test_compare_all_failure_and_deadline(transport):
    calls,responses=transport
    responses['https://bad.test']=OSError('unavailable')
    result=call(['--output-format','json','compare','Widget','-s','https://bad.test'])
    assert result.exit_code==1 and json.loads(result.output)['error']['code']=='E_OPERATION'
    async def slow():await asyncio.sleep(.1)
    responses['https://slow.test']=slow
    result=call(['--output-format','json','compare','Widget','-s','https://slow.test','--timeout','.001'])
    assert result.exit_code==1 and json.loads(result.output)['error']['code']=='E_TIMEOUT'


def test_position_filters_before_float_loss(transport):
    calls,responses=transport
    responses.update({'https://usd.test':extracted([dict(title='Widget',price='20',currency='USD')]),'https://eur.test':extracted([dict(title='Widget',price='1',currency='EUR')]),'https://unknown.test':extracted([dict(title='Widget',price='1')])})
    args=['competitive','position','-']
    for url in responses:args+=['--competitor',url]
    report=data(call(args,[dict(title='Widget',price='10',currency='USD')]))
    assert report['position']['rank']==1
    assert report['position']['competitor_prices']=={'https://usd.test':20.0}
    assert report['excluded']==[{'store':'https://eur.test','currency':'EUR'},{'store':'https://unknown.test','currency':None}]
    assert report['currency']=='USD'


def test_catalog_urls_no_default_currency_comparison(transport):
    calls,responses=transport
    responses.update({'https://a.test':extracted([dict(title='Widget',price='1',gtin=GTIN)]),'https://b.test':extracted([dict(title='Widget',price='2',gtin=GTIN)])})
    report=data(call(['compare-catalogs','https://a.test','https://b.test','--max-products','3']))
    assert len(report['in_both'])==1 and report['cheaper_in_a']==[]
    assert report['in_both'][0][0]['product']['currency']=='USD' # preserve scalar, never observed comparison
    assert len(calls)==2 and calls[0][1]['max_urls']==3


def test_analyze_machine_full_and_gaps_native(transport):
    calls,responses=transport
    responses.update({'https://a.test':extracted([dict(title='Widget',price='1',vendor='A',product_type='Cat')]*11),'https://b.test':extracted([dict(title='Other',price='2',vendor='B',product_type='Other')])})
    stats=data(call(['--output-format','json','analyze','https://a.test']))
    assert stats['statistics']['total_products']==11 and stats['statistics']['brands']=={'A':11}
    gaps=data(call(['competitive','gaps','https://a.test','--competitor','https://b.test']))
    assert gaps['missing_brands']==['B'] and gaps['missing_categories']==['Other']


def test_matching_identity_ambiguity_variant_evaluation(tmp_path):
    right=tmp_path/'right.json';right.write_text(json.dumps([record(),record()]))
    report=data(call(['match','-',str(right)],[record()]))
    assert len(report['results'])==2 and all(d['needs_review'] for d in report['results'])
    right.write_text(json.dumps([record(attributes={'color':'blue'})]))
    report=data(call(['match-pair','-',str(right)],[record(attributes={'color':'red'})]))
    assert report['relation']=='variant' and report['needs_review']
    report=data(call(['match-evaluate','-'],[dict(id='1',a=record(),b=record(),label='exact')]))
    assert report['true_exact']==1 and report['passed']
    assert data(call(['match-gtin',GTIN,'-'],[record()]))['candidates'][0]['gtin']==GTIN


def test_semantic_indexed_portable_duplicates_skip_rule(tmp_path):
    left=[Product(title='Exact',gtin=GTIN),Product(title='Odd zebra'),Product(title='Odd zebra')]
    right=[Product(title='Exact',gtin=GTIN),Product(title='Unrelated quasar')]
    path=tmp_path/'right.json';path.write_text(json.dumps([product_to_record(p) for p in right]))
    options=tmp_path/'options.json';options.write_text(json.dumps(dict(schema_version=1,semantic_candidates=[[],[1],[0]])))
    report=data(call(['match','-',str(path),'--semantic-candidates',str(options)],[product_to_record(p) for p in left]))
    rows=report['results'];assert rows[0]['relation']=='exact'
    assert [(r['index_a'],r['index_b'],r['candidate_method']) for r in rows[1:]]==[(1,1,'semantic'),(2,0,'semantic')]


def test_native_semantic_dual_input_rejected():
    from shopextract.compare import match_products
    with pytest.raises(ValueError):match_products([],[],semantic_candidates=lambda a,b:[],semantic_candidate_indices=[])


def test_portable_identity_variant_money_and_attrs():
    p=Product(title='A',product_url='https://synthetic.test/a',price=Decimal('0.10'),in_stock=False,
              attributes={'colour':' Blue ','capacity':' 10 GB '},variants=[Variant(price=Decimal('0.00'),in_stock=False)])
    portable=product_to_record(p)
    report=data(call(['identity','assign','-'],[portable]))
    restored=product_from_record(report['products'][0])
    assert str(restored.price)=='0.10' and str(restored.variants[0].price)=='0.00'
    assert restored.in_stock is False and restored.variants[0].in_stock is False
    report=data(call(['identity','inspect','-'],[portable]))
    assert report['normalized_attributes'][0]['color']=='blue'
    assert report['normalized_attributes'][0]['capacity']=='10gb'


@pytest.mark.parametrize('bad',[{'price':True},{'gtin':123},{'attributes':[]},{'variants':[{'price':False}]},{'currency':None},{'in_stock':0}])
def test_malformed_types_before_transport(bad,transport):
    calls,_=transport
    result=call(['competitive','position','-','--competitor','https://target.test'],[dict(title='Widget',**bad)])
    assert result.exit_code==2 and calls==[]


@pytest.mark.parametrize('threshold',['nan','inf','-0.1','1.1'])
def test_bad_threshold_before_transport(threshold,transport):
    calls,_=transport
    result=call(['--output-format','json','compare','Widget','-s','https://a.test','--threshold',threshold])
    assert result.exit_code==2 and calls==[]


def test_valid_threshold_edges_and_store_caps(transport):
    calls,responses=transport
    responses['https://a.test']=extracted([])
    for threshold in ('0','1'):
        assert call(['--output-format','json','compare','Widget','-s','https://a.test','--threshold',threshold]).exit_code==0
    args=['--output-format','json','compare','Widget']
    for i in range(11):args+=['-s','https://a.test']
    before=len(calls);assert call(args).exit_code==2 and len(calls)==before


def test_bad_declarative_files_no_execution(tmp_path):
    right=tmp_path/'right.json';right.write_text('[{"title":"A"}]')
    path=tmp_path/'candidate.json';path.write_text('{"schema_version":1,"semantic_candidates":[[true]]}')
    result=call(['match','-',str(right),'--semantic-candidates',str(path)],[{'title':'A'}]);assert result.exit_code==2
    path.write_text('{"schema_version":1,"publisher_aliases":{"00012345600012":["A"]},"callback":"evil"}')
    assert call(['match','-',str(right),'--publisher-aliases',str(path)],[record()]).exit_code==2
    assert call(['match','-','-'],[]).exit_code==2
    assert call(['match-pair','-',str(right)],[]).exit_code==2


def test_stats_distribution_outliers_brands_and_empty():
    rows=[dict(title=str(i),price=str(price),vendor='A') for i,price in enumerate([1,10,100])]
    assert data(call(['stats','distribution','-','--buckets','0,10,100'],rows))['distribution']=={'0.0-10.0':1,'10.0-100.0':1,'100.0+':1}
    assert data(call(['stats','outliers','-','--std-multiplier','.5'],rows))['products'][-1]['price']=='100'
    assert data(call(['stats','brands','-'],rows))['brands']=={'A':100.0}
    assert data(call(['analyze-file','-'],[]))['statistics']['total_products']==0
    assert call(['stats','distribution','-','--buckets','0,0'],[]).exit_code==2
    assert call(['stats','outliers','-','--std-multiplier','nan'],[]).exit_code==2


def test_native_validation_and_duplicates():
    report=data(call(['--output-format','json','validate','-'],[{'title':'A'}]),4)
    assert report['invalid']==1 and report['issues']
    assert data(call(['--output-format','json','validate','-'],[]))['total']==0
    assert data(call(['duplicates','-','--method','gtin'],[record(),record(),{'gtin':''}]))['duplicates']==[[0,1,1.0]]


@pytest.mark.parametrize('fmt',['json','csv','google_shopping','idealo'])
def test_real_export_payload_and_companion_roundtrip(tmp_path,fmt):
    from shopextract.export import load_evidence_sidecar
    p=Product(title='A',external_id='001',product_url='https://synthetic.test/a',price=Decimal('0.10'),gtin=GTIN,in_stock=False)
    if fmt in ('google_shopping','idealo'):
        from tests.test_downstream_remediation import native_stock_default
        p=native_stock_default(stock=False)
    source=tmp_path/'source.json';source.write_text(json.dumps([product_to_record(p)]))
    target=tmp_path/'out';side=tmp_path/'side'
    args=['export',str(source),'--format',fmt,'-o',str(target)]
    if fmt!='json':args+=['--evidence-output',str(side)]
    report=data(call(args));assert report['product_count']==1 and target.stat().st_size>0
    if fmt!='json':
        restored=load_evidence_sidecar(json.loads(side.read_text()),target.read_bytes())
        assert product_to_record(restored[0])==product_to_record(p)
    else:assert json.loads(target.read_text())[0]['price']=='0.10'


def test_export_stdout_and_optional_engine(tmp_path,monkeypatch):
    import shopextract.export as exports
    result=call(['export','-','--format','json','-o','-'],[record()])
    assert result.exit_code==0 and isinstance(json.loads(result.output),list)
    def missing(*a,**kw):raise ImportError('engine missing')
    monkeypatch.setattr(exports,'to_parquet',missing)
    result=call(['export','-','--format','parquet','-o',str(tmp_path/'out')],[record()])
    assert result.exit_code==1 and 'pyarrow' in result.output and not (tmp_path/'out').exists()


def test_export_aliases_and_stdout_companion_no_writes(tmp_path):
    source=tmp_path/'source.json';source.write_text('[]')
    hard=tmp_path/'hard';os.link(source,hard)
    sym=tmp_path/'sym';sym.symlink_to(source)
    for target in (source,hard,sym):
        assert call(['export',str(source),'--format','json','-o',str(target)]).exit_code==2
        assert source.read_text()=='[]'
    assert call(['export',str(source),'--format','csv','-o','-','--evidence-output',str(tmp_path/'side')]).exit_code==2
    assert not (tmp_path/'side').exists()


def test_export_staging_failure_and_recovery_failure(tmp_path,monkeypatch):
    import shopextract.export as exports
    source=tmp_path/'source.json';source.write_text(json.dumps([product_to_record(Product(title='A'))]))
    target=tmp_path/'out.csv';side=tmp_path/'side';target.write_text('old');side.write_text('old side')
    original=exports.to_csv
    def staging(products,path,**kw):
        Path(path).write_text('staged')
        raise OSError('sidecar stage failed')
    monkeypatch.setattr(exports,'to_csv',staging)
    args=['export',str(source),'--format','csv','-o',str(target),'--evidence-output',str(side)]
    assert call(args).exit_code==1
    assert target.read_text()=='old' and side.read_text()=='old side'
    assert not list(tmp_path.glob('.out.csv.*')) and not list(tmp_path.glob('.side.*'))
    monkeypatch.setattr(exports,'to_csv',original)
    replace=os.replace;attempts=[]
    def fault(src,dst):
        attempts.append(str(dst))
        if str(dst)==str(side) or str(dst)==str(target) and len(attempts)>1:raise OSError('injected')
        replace(src,dst)
    monkeypatch.setattr(os,'replace',fault)
    result=call(args);assert result.exit_code==1
    assert 'retained recovery files' in result.output
    backups=list(tmp_path.glob('.out.csv.*.backup'));assert backups and backups[0].read_text()=='old'


def test_record_and_byte_boundaries():
    for count in (999,1000):
        assert data(call(['analyze-file','-'],[{'title':'A'}]*count))['statistics']['total_products']==count
    assert call(['analyze-file','-'],[{'title':'A'}]*1001).exit_code==2
    for size in (MAX_BYTES-1,MAX_BYTES,MAX_BYTES+1):
        raw='[]'+' '*(size-2)
        result=CliRunner().invoke(main,['analyze-file','-'],input=raw)
        assert result.exit_code==(0 if size<=MAX_BYTES else 2)


def test_controlled_http_images_and_invalid_preflight():
    from http.server import BaseHTTPRequestHandler,HTTPServer
    import threading
    requests=[]
    class Handler(BaseHTTPRequestHandler):
        def do_HEAD(self):
            requests.append(self.path)
            self.send_response(404 if self.path=='/missing' else 200)
            self.send_header('Content-Type','text/plain' if self.path=='/text' else 'image/png')
            self.end_headers()
        def log_message(self,*a):pass
    server=HTTPServer(('127.0.0.1',0),Handler)
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}'
    try:
        rows=[dict(title='A',image_url=base+'/ok'),dict(title='B',image_url=base+'/missing'),dict(title='C',image_url=base+'/text'),dict(title='D')]
        issues=data(call(['images','check','-','--concurrency','1','--timeout','2'],rows))['issues']
        assert len(issues)==3 and any(i['status_code']==404 for i in issues) and any('Non-image' in i['error'] for i in issues)
        assert requests==['/ok','/missing','/text']
        before=len(requests)
        assert call(['images','check','-'],[dict(image_url='file:///etc/passwd')]).exit_code==2
        assert len(requests)==before
    finally:
        server.shutdown();server.server_close();thread.join(2)


@pytest.mark.parametrize('raw',['[{"price":NaN}]','[{"title":"A","title":"B"}]','\ufeff[]','[',json.dumps([{'title':'x','raw_data':{'nested':[]}}])[:-3]])
def test_malformed_stdin(raw):
    result=CliRunner().invoke(main,['analyze-file','-'],input=raw)
    assert result.exit_code==2
    assert json.loads(result.output)['error']['code']=='E_USAGE'


def test_zero_false_null_and_extension_preserved():
    rows=[dict(title='Zero',price='0.00',gtin=None,in_stock=False,extension={'missing':None,'flag':False,'count':0})]
    result=call(['export','-','--format','json','-o','-'],rows)
    assert result.exit_code==0 and json.loads(result.output)==rows
    stats=data(call(['analyze-file','-'],rows))
    assert stats['statistics']['total_products']==1 and stats['statistics']['out_of_stock']==1
    assert stats['statistics']['avg_price']==0


def test_dropped_raw_record_cannot_misassign_currency(transport):
    calls,responses=transport
    from shopextract import normalize
    product=normalize(dict(title='Widget',price='10',currency='USD',gtin=GTIN))
    assert product is not None
    response=ExtractionResult(products=[product],raw_products=[{'currency':'EUR'},product.raw_data],catalog_complete=True)
    responses.update({'https://a.test':response,'https://b.test':extracted([dict(title='Widget',price='20',currency='EUR',gtin=GTIN)])})
    report=data(call(['--output-format','json','compare','Widget','-s','https://a.test']))
    assert set(report['currency_groups'])=={'USD'}
    report=data(call(['compare-catalogs','https://a.test','https://b.test']))
    assert len(report['in_both'])==1 and report['cheaper_in_a']==[]


def test_shared_deadline_expires_second_source_no_third(transport):
    calls,responses=transport
    events=[]
    async def first():
        await asyncio.sleep(.08);events.append('first_done');return extracted([record()])
    async def second():
        try:
            await asyncio.sleep(.08);return extracted([record()])
        except asyncio.CancelledError:
            events.append('second_cancelled');raise
        finally:events.append('second_closed')
    responses.update({'https://first.test':first,'https://second.test':second,'https://third.test':extracted([record()])})
    result=call(['--output-format','json','compare','Widget','-s','https://first.test','-s','https://second.test','-s','https://third.test','--timeout','.12'])
    assert result.exit_code==1 and json.loads(result.output)['error']['code']=='E_TIMEOUT'
    assert [url for url,_ in calls]==['https://first.test','https://second.test']
    assert events==['first_done','second_cancelled','second_closed']


def test_nonempty_product_and_variant_evidence_export_roundtrip(tmp_path):
    from datetime import datetime,timezone
    from shopextract._evidence import Evidence,FieldObservation,TrustContract,FieldResolution
    from shopextract.export import load_evidence_sidecar
    now=datetime(2026,10,25,tzinfo=timezone.utc)
    eid='e_00000000-0000-0000-0000-000000000001'
    oid='o_00000000-0000-0000-0000-000000000001'
    other='o_00000000-0000-0000-0000-000000000002'
    evidence=Evidence(eid,'https://synthetic.test/product',now,'api',retained_data={'price':'0.10'},pointer='/price')
    observed=FieldObservation(oid,'/price','observed','0.10',Decimal('0.10'),[eid])
    competitor=FieldObservation(other,'/price','observed','0.20',Decimal('0.20'),[eid])
    product=Product(title='A',price=Decimal('0.10'),variants=[Variant(price=Decimal('0.10'))])
    product.evidence_contract=TrustContract([evidence],[observed,competitor],[FieldResolution('/price','observed',[oid,other],'API precedence',oid)])
    product.variants[0].evidence_contract=TrustContract([evidence],[observed])
    source=tmp_path/'input';source.write_text(json.dumps([product_to_record(product)]))
    payload=tmp_path/'out.csv';side=tmp_path/'side.json'
    data(call(['export',str(source),'--format','csv','-o',str(payload),'--evidence-output',str(side)]))
    restored=load_evidence_sidecar(json.loads(side.read_text()),payload.read_bytes())[0]
    assert restored.evidence_contract.to_dict()==product.evidence_contract.to_dict()
    assert restored.variants[0].evidence_contract.to_dict()==product.variants[0].evidence_contract.to_dict()
    assert product_to_record(restored)==product_to_record(product)


def test_export_restores_two_existing_outputs_after_second_replace_failure(tmp_path,monkeypatch):
    source=tmp_path/'source';source.write_text(json.dumps([product_to_record(Product(title='A'))]))
    payload=tmp_path/'out.csv';side=tmp_path/'side';payload.write_text('old payload');side.write_text('old side')
    replace=os.replace;attempts=[]
    def fail(src,dst):
        attempts.append(str(dst))
        if str(dst)==str(side):raise OSError('injected companion replacement failure')
        replace(src,dst)
    monkeypatch.setattr(os,'replace',fail)
    result=call(['export',str(source),'--format','csv','-o',str(payload),'--evidence-output',str(side)])
    assert result.exit_code==1 and attempts==[str(payload),str(side),str(payload)]
    assert payload.read_text()=='old payload' and side.read_text()=='old side'
    assert not list(tmp_path.glob('.out.csv.*')) and not list(tmp_path.glob('.side.*'))


@pytest.mark.parametrize('args',[['stats','missing'],['stats'],['identity','missing'],['competitive','missing'],['images','missing']])
def test_new_group_errors_default_envelope(args):
    result=call(args)
    assert result.exit_code==2
    assert json.loads(result.output)['error']['code']=='E_USAGE'
