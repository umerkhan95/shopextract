"""P4 deterministic mechanism, adverse boundary and crossphase cases (seed11025)."""
import asyncio
import copy
import json
import os
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import httpx
import pytest

from tests.test_cli_categories import (STORE,AT,options,raw,dump,fixture_files,invoke,body,
    tree_record,install_transport,resolver)
from shopextract._models import Platform
from shopextract._cli_core import CliFailure
from shopextract._cli_data import read_json_file,catalog_from_value,categorized_from_value
from shopextract.categories._codec import wire,canonical
from shopextract.categories import normalize_with_categories,categorized_product_to_record

@pytest.mark.parametrize('platform',list(Platform))
def test_six_normalize_real_adapters(tmp_path,platform):
    opt=options(platform)
    result=invoke(['categories','normalize',dump(tmp_path/'raw.json',raw(platform)),
        '--options',dump(tmp_path/'options.json',wire(opt))])
    assert result.exit_code==0,(platform,result.output,result.exception)
    data=body(result)['data'];record=data['categorized_products'][0]
    assert data['product_count']==1 and data['dropped_count']==0
    assert record['scope']['platform']==platform.value
    assert record['product']==data['products'][0]
    observations=record['observations']
    assert observations and any(t['label']=='Boots' or t['ref']['native_id'] in ('7','Nw==') for o in observations for t in o['terms'])
    assert any(f['support']=='observed' for o in observations for t in o['terms'] for f in t['facts'])
    assert all(o['scope']==wire(opt.scope) for o in observations)

@pytest.mark.parametrize('platform',list(Platform))
def test_six_extract_real_wire_parsers(tmp_path,monkeypatch,platform):
    original=httpx.AsyncClient;requests=[]
    product=raw(platform);product.pop('_capture',None)
    if platform==Platform.MAGENTO:
        product.update(url_key='boot',price_range={'minimum_price':{'final_price':{'value':99,'currency':'EUR'}}})
    if platform==Platform.SHOPIFY:
        product.update(handle='boot',variants=[{'id':1,'price':'99.00','title':'Boot','available':True}])
    def response(request):
        requests.append(str(request.url))
        if platform==Platform.SHOPIFY:payload={'products':[product]}
        elif platform==Platform.WOOCOMMERCE:payload=[product]
        elif platform==Platform.MAGENTO:payload={'data':{'products':{'items':[product],'total_count':1,'page_info':{'current_page':1,'total_pages':1}}}}
        elif platform==Platform.SHOPWARE:
            payload={'currency':{'isoCode':'EUR'}} if request.url.path.endswith('/context') else {'elements':[product],'total':1}
        elif platform==Platform.BIGCOMMERCE:payload={'data':{'site':{'products':{'edges':[{'node':product}],'pageInfo':{'hasNextPage':False}}}}}
        else:
            return httpx.Response(200,text='<html><script type="application/ld+json">'+json.dumps(product)+'</script></html>',headers={'Content-Type':'text/html'})
        return httpx.Response(200,json=payload,headers={'X-WP-Total':'1','X-WP-TotalPages':'1'})
    def client(*args,**kwargs):
        kwargs.setdefault('transport',httpx.MockTransport(response));return original(*args,**kwargs)
    monkeypatch.setattr(httpx,'AsyncClient',client)
    command=['categories','extract',STORE,'--max-products','1','--options',dump(tmp_path/'opt.json',wire(options(platform)))]
    if platform in (Platform.SHOPWARE,Platform.BIGCOMMERCE):
        command+=['--storefront-config',dump(tmp_path/'api.json',{'endpoint':STORE+('/store-api' if platform==Platform.SHOPWARE else '/graphql'),'access_token':'public-fixture-token'})]
    result=invoke(command)
    assert result.exit_code==(3 if platform in (Platform.GENERIC,Platform.SHOPIFY) else 0),(platform,result.output,result.exception,requests)
    data=body(result)['data'];record=data['categorized_products'][0]
    assert data['product_count']==1 and len(requests)<=2
    assert record['scope']['platform']==platform.value and record['observations']
    assert any(f['support']=='observed' for o in record['observations'] for t in o['terms'] for f in t['facts'])


def test_survivors_order_and_source_states(tmp_path):
    opt=dump(tmp_path/'opt.json',wire(options()))
    a=raw();a['name']='First';b=raw();b['name']='Last';b['id']=502
    result=invoke(['categories','normalize',dump(tmp_path/'raw.json',[b,{},a]),'--options',opt])
    assert result.exit_code==0,result.output
    data=body(result)['data']
    assert data['input_count']==3 and data['dropped_count']==1
    assert [r['product']['product']['title'] for r in data['categorized_products']]==['Last','First']
    for category,state,complete in [(None,'null','unknown'),([], 'empty','complete'),(False,'malformed','unknown')]:
        value=raw();value['categories']=category
        value.pop('_capture',None) # unsupported plain source must never invent observed mapping
        result=invoke(['categories','normalize',dump(tmp_path/'state.json',value),'--options',opt])
        assert result.exit_code==0,result.output
        observation=body(result)['data']['categorized_products'][0]['observations'][0]
        assert (observation['source_state'],observation['completeness'])==(state,complete)
        assert not observation['terms']


def test_native_mapping_roundtrip_and_ambiguity(tmp_path):
    files=fixture_files(tmp_path)
    mapped=invoke(['categories','map',files['categorized'],'--options',files['options']])
    assert mapped.exit_code==0,mapped.output
    data=body(mapped)['data'];record=data['categorized_products'][0]
    assert record['mappings'][0]['status']=='mapped' and record['mappings'][0]['target_ids']==['boots']
    assert record['mappings'][0]['source_pointers']==['/categories/0/id']
    output=tmp_path/'roundtrip.json'
    result=invoke(['categories','record','load','-','--output',str(output)],mapped.output)
    assert result.exit_code==0 and json.loads(output.read_text())==data['categorized_products']
    opt=json.loads(Path(files['options']).read_text());opt['registry']['target_ids']+=['sale']
    rule=copy.deepcopy(opt['rules'][0]);rule.update(rule_id='r2',target_ids=['sale']);opt['rules'].append(rule)
    result=invoke(['categories','map',files['categorized'],'--options',dump(tmp_path/'amb.json',opt)])
    assert result.exit_code==0,result.output
    assert body(result)['data']['categorized_products'][0]['mappings'][0]['status']=='ambiguous'
    assert body(result)['data']['categorized_products'][0]['observations']==record['observations']

@pytest.mark.parametrize('mutation',['projection-null','projection-reorder','projection-count','mixed','tamper','invalid-category'])
def test_category_authority_rejects_no_fallback(tmp_path,mutation):
    files=fixture_files(tmp_path);records=json.loads(Path(files['categorized']).read_text())
    value=dict(schema_version='1.0',data=dict(categorized_products=records,products=[records[0]['product']]))
    if mutation=='projection-null':value['data']['products']=None
    elif mutation=='projection-reorder':value['data']['products']=[dict(records[0]['product'],schema_version=99)]
    elif mutation=='projection-count':value['data']['products']=[]
    elif mutation=='mixed':value=[records[0],records[0]['product']]
    elif mutation=='tamper':value['data']['categorized_products'][0]['scope']['store_url']=STORE+'/other'
    else:value['data']['categorized_products']=False
    path=dump(tmp_path/'bad.json',value)
    for command in (['analyze-file',path],['export',path,'--format','json','--output',str(tmp_path/'out'),'--categories-output',str(tmp_path/'cat')]):
        result=invoke(command);assert result.exit_code==2,result.output
        assert body(result)['error']['code']=='E_USAGE'
    assert not (tmp_path/'out').exists() and not (tmp_path/'cat').exists()


def test_scope_guard_before_output_even_forged_digest(tmp_path):
    from shopextract.categories.portable import bind_product,categorized_product_from_record
    files=fixture_files(tmp_path);record=json.loads(Path(files['categorized']).read_text())[0]
    value=categorized_product_from_record(record)
    # Valid original binding but foreign trusted scope with caller's options digest.
    foreign=CategoryForeign(value)
    path=dump(tmp_path/'foreign.json',[categorized_product_to_record(foreign)])
    out=tmp_path/'existing';out.write_text('old')
    result=invoke(['categories','map',path,'--options',files['options'],'--output',str(out)])
    assert result.exit_code==2 and out.read_text()=='old'
    result=invoke(['categories','policy','review',path,'--config',files['config'],'--profile','footwear'])
    assert result.exit_code==2 and body(result)['error']['code']=='E_USAGE'


def CategoryForeign(value):
    from shopextract.categories.portable import bind_product
    scope=replace(value.scope,store_url=STORE+'/foreign')
    observations=tuple(replace(o,scope=scope) for o in value.observations)
    return bind_product(value.product,scope,observations,value.mappings,value.config_digest)

@pytest.mark.parametrize('mutation',['unknown','null','bool','zero-cap','foreign-url','basepath-escape'])
def test_invalid_config_no_network(tmp_path,monkeypatch,mutation):
    data=wire(options());url=STORE
    if mutation=='unknown':data['mystery']=1
    elif mutation=='null':data['scope']=None
    elif mutation=='bool':data['limits']['terms']=False
    elif mutation=='zero-cap':data['limits']['record_bytes']=0
    elif mutation=='foreign-url':url='https://other.test/shop'
    else:url=STORE+'escape'
    def forbidden(*args,**kwargs):raise AssertionError('network must not start')
    monkeypatch.setattr(httpx,'AsyncClient',forbidden)
    if mutation=='zero-cap':
        result=invoke(['categories','normalize',dump(tmp_path/'raw',raw()),'--options',dump(tmp_path/'opt',data)])
    else:result=invoke(['categories','extract',url,'--options',dump(tmp_path/'opt',data)])
    assert result.exit_code==2,result.output


def test_zero_terms_not_empty_complete(tmp_path):
    opt=wire(options());opt['limits']['terms']=0
    result=invoke(['categories','normalize',dump(tmp_path/'raw',raw()),'--options',dump(tmp_path/'opt',opt)])
    assert result.exit_code==0,result.output
    o=body(result)['data']['categorized_products'][0]['observations'][0]
    assert o['source_state']=='present' and o['completeness']=='partial' and o['terms']==[]

@pytest.mark.parametrize('case',['complete','cycle','partial','unavailable'])
def test_tree_native_outcomes_and_codec_reload(tmp_path,monkeypatch,case):
    rows=[{'id':7,'name':'Boots','slug':'boots','parent':0}]
    if case=='cycle':rows=[dict(rows[0],parent=8),{'id':8,'name':'Sale','slug':'sale','parent':7}]
    if case=='partial':rows=[dict(rows[0],name=None)]
    install_transport(monkeypatch,rows=rows,status=503 if case=='unavailable' else 200)
    files=fixture_files(tmp_path);out=tmp_path/'tree.json'
    result=invoke(['categories','tree','fetch','--options',files['options'],'--output',str(out)])
    expected=1 if case=='unavailable' else 3 if case=='partial' else 0
    assert result.exit_code==expected,(case,result.output,result.exception)
    data=body(result)['data'];assert data['outcome']==('unavailable' if case=='unavailable' else 'partial' if expected==3 else 'complete')
    loaded=invoke(['categories','tree','load',str(out)])
    assert loaded.exit_code==expected,loaded.output
    record=body(loaded)['data']['tree']
    assert record==json.loads(out.read_text())
    if case=='cycle':assert any('cycle' in i['code'] for i in record['payload']['issues'])
    if case=='unavailable':assert not record['payload']['confirmed_empty'] and record['payload']['nodes']==[]


def test_tree_membership_native_scopes_missing_and_unsupported(tmp_path):
    files=fixture_files(tmp_path);tree=dump(tmp_path/'tree',tree_record())
    result=invoke(['categories','tree','link',tree,files['categorized']])
    assert result.exit_code==0 and body(result)['data']['links'][0]['status']=='linked'
    other=tree_record([{'id':8,'name':'Sale','slug':'sale','parent':0}])
    result=invoke(['categories','tree','link',dump(tmp_path/'other',other),files['categorized']])
    assert result.exit_code==0 and body(result)['data']['links'][0]['status']=='missing'
    # Source support is not created by plain raw JSON.
    source=raw();source.pop('_capture',None)
    value=normalize_with_categories(source,Platform.WOOCOMMERCE,STORE,category_options=options())
    path=dump(tmp_path/'unsupported',[categorized_product_to_record(value)])
    result=invoke(['categories','tree','link',tree,path])
    assert result.exit_code==0 and body(result)['data']['links'][0]['status']=='unsupported'
    foreign=dump(tmp_path/'foreign',[categorized_product_to_record(CategoryForeign(value))])
    result=invoke(['categories','tree','link',tree,foreign])
    assert result.exit_code==2 and body(result)['error']['code']=='E_USAGE'


def test_policy_native_digest_reasons_and_export_roundtrip(tmp_path):
    from shopextract.categories.config import runtime_from_record
    from shopextract.categories.maintenance import category_policy_digest
    files=fixture_files(tmp_path)
    inspected=invoke(['categories','policy','inspect','--config',files['config']])
    digest=category_policy_digest(runtime_from_record(json.loads(Path(files['config']).read_text())))
    assert inspected.exit_code==0 and body(inspected)['data']['policy_digest']==digest
    review=invoke(['categories','policy','review',files['categorized'],'--config',files['config'],'--profile','wrong'])
    assert review.exit_code==4,review.output
    data=body(review)['data'];assert data['review_reasons']==[['category_profile_conflict']] and data['policy_digest']==digest
    path=dump(tmp_path/'review.json',body(review));cat=tmp_path/'cat.json'
    exported=invoke(['export',path,'--format','json','--output',str(tmp_path/'out.json'),'--categories-output',str(cat)])
    assert exported.exit_code==0,exported.output
    saved=json.loads(cat.read_text());assert saved['data']['policy_digest']==digest and saved['data']['config']==data['config']
    assert invoke(['analyze-file',str(cat)]).exit_code==0
    assert invoke(['categories','record','load',str(cat)]).exit_code==2
    assert invoke(['categories','policy','review',str(cat),'--config',files['config'],'--profile','footwear']).exit_code==0
    for key in ('policy_digest','config'):
        bad=copy.deepcopy(saved);bad['data'].pop(key)
        assert invoke(['analyze-file',dump(tmp_path/'bad',bad)]).exit_code==2
    saved['data']['policy_digest']='0'*64
    assert invoke(['analyze-file',dump(tmp_path/'bad',saved)]).exit_code==2

@pytest.mark.parametrize('fmt',['json','csv','google_shopping','idealo','parquet'])
def test_export_category_format_matrix(tmp_path,fmt):
    files=fixture_files(tmp_path);out=tmp_path/'payload';cat=tmp_path/'cats'
    result=invoke(['export',files['categorized'],'--format',fmt,'--output',str(out),'--categories-output',str(cat)])
    if result.exit_code==1:
        assert fmt=='parquet' and body(result)['error']['code']=='E_DEPENDENCY' and not out.exists() and not cat.exists()
    else:
        assert result.exit_code==0,result.output
        assert json.loads(cat.read_text())==json.loads(Path(files['categorized']).read_text())
        assert invoke(['categories','record','load',str(cat)]).exit_code==0
    missing=invoke(['export',files['categorized'],'--format',fmt,'--output',str(out)])
    assert missing.exit_code==2
    stdout=invoke(['export',files['categorized'],'--format',fmt,'--output','-','--categories-output',str(cat)])
    assert stdout.exit_code==2


def test_export_three_artifacts_rollback_and_aliases(tmp_path,monkeypatch):
    import shopextract._cli_analysis as analysis
    files=fixture_files(tmp_path);out=tmp_path/'out';evidence=tmp_path/'evidence';cat=tmp_path/'cats'
    for p in (out,evidence,cat):p.write_bytes(b'old-'+p.name.encode())
    command=['export',files['categorized'],'--format','csv','--output',str(out),'--evidence-output',str(evidence),'--categories-output',str(cat)]
    original=analysis.os.replace;attempts=[]
    def replace_file(source,target):
        attempts.append(str(target))
        if str(target)==str(cat):raise OSError('injected final artifact failure')
        return original(source,target)
    monkeypatch.setattr(analysis.os,'replace',replace_file)
    result=invoke(command)
    assert result.exit_code==1 and 'restored' in body(result)['error']['message'],result.output
    assert all(p.read_bytes()==b'old-'+p.name.encode() for p in (out,evidence,cat))
    assert not list(tmp_path.glob('.*'))
    assert len(attempts)==5
    monkeypatch.setattr(analysis.os,'replace',original)
    for left,right in ((out,evidence),(out,cat),(evidence,cat)):
        right.unlink();os.link(left,right)
        result=invoke(command)
        assert result.exit_code==2,result.output
        right.unlink();right.write_text('old-'+right.name)


def test_p4_aliases_all_inputs_and_single_read(tmp_path,monkeypatch):
    files=fixture_files(tmp_path)
    for source in (files['options'],files['raw']):
        alias=tmp_path/'alias';alias.symlink_to(source)
        result=invoke(['categories','normalize',files['raw'],'--options',files['options'],'--output',str(alias)])
        assert result.exit_code==2
        alias.unlink();os.link(source,alias)
        assert invoke(['categories','normalize',files['raw'],'--options',files['options'],'--output',str(alias)]).exit_code==2
        alias.unlink()
    import builtins
    original=builtins.open;reads=[]
    def opened(path,*args,**kwargs):
        if str(path) in (files['raw'],files['options']):reads.append(str(path))
        return original(path,*args,**kwargs)
    monkeypatch.setattr(builtins,'open',opened)
    result=invoke(['categories','normalize',files['raw'],'--options',files['options']])
    assert result.exit_code==0 and reads==[files['options'],files['raw']]
    result=invoke(['categories','normalize','-','--options','-'],input='{}')
    assert result.exit_code==2


def test_p4_byte_structure_record_boundaries(tmp_path,monkeypatch):
    from shopextract import _cli_data as data
    assert (data.MAX_BYTES,data.MAX_NODES)==(33554432,1000000)
    # Full-size boundaries are covered by money reader acceptance; reuse mechanics.
    monkeypatch.setattr(data,'MAX_BYTES',1048576)
    monkeypatch.setattr(data,'MAX_NODES',100000)
    for count,valid in ((1048576,True),(1048577,False)):
        path=tmp_path/'bytes';path.write_bytes(b'{}'+b' '*(count-2))
        if valid:assert read_json_file(str(path))=={}
        else:
            with pytest.raises(CliFailure):read_json_file(str(path))
    for count,valid in ((999,True),(1000,True),(1001,False)):
        if valid:assert len(data.raw_records([{}]*count))==count
        else:
            with pytest.raises(CliFailure):data.raw_records([{}]*count)
    for count,valid in ((99999,True),(100000,False)):
        # Root itself counts as one node.
        if valid:data.bounded_tree([0]*count)
        else:
            with pytest.raises(ValueError):data.bounded_tree([0]*count)
    for depth,valid in ((64,True),(65,False)):
        item=0
        for _ in range(depth):item=[item]
        if valid:data.bounded_tree(item)
        else:
            with pytest.raises(ValueError):data.bounded_tree(item)


def test_p4_output_actual_compact_boundaries(tmp_path,monkeypatch):
    import shopextract._cli_categories as categories
    from shopextract._cli_core import make_response
    from click.testing import CliRunner
    value={'hello':'é'};size=len(categories.encoded(make_response(value)))+1
    for limit,valid in ((size-1,False),(size,True),(size+1,True)):
        monkeypatch.setattr(categories,'MAX_BYTES',limit)
        @__import__('click').command()
        def command():categories.category_output(value)
        result=CliRunner().invoke(command)
        assert result.exit_code==(0 if valid else 1)
        if valid:assert len(result.output.encode())==size
        else:assert result.output=='' and isinstance(result.exception,CliFailure)
    target=tmp_path/'old';target.write_text('old')
    size=len(categories.encoded(value))
    for limit,valid in ((size-1,False),(size,True),(size+1,True)):
        monkeypatch.setattr(categories,'MAX_BYTES',limit)
        if valid:
            categories.write_artifact(value,str(target));assert target.stat().st_size==size
        else:
            with pytest.raises(CliFailure):categories.write_artifact(value,str(target))
            assert target.read_text()=='old'


def test_native_companion_config_byte_edges(tmp_path):
    from shopextract.categories.config import validate_options
    from shopextract.categories.portable import bind_product
    opt=options();value=normalize_with_categories(raw(),Platform.WOOCOMMERCE,STORE,category_options=opt)
    record=categorized_product_to_record(value);size=len(canonical(record).encode())
    for limit,valid in ((size-1,False),(size,True),(size+1,True)):
        limits=replace(opt.limits,record_bytes=limit)
        if valid:bind_product(value.product,value.scope,value.observations,value.mappings,value.config_digest,limits=limits)
        else:
            with pytest.raises(ValueError):bind_product(value.product,value.scope,value.observations,value.mappings,value.config_digest,limits=limits)
    for offset,valid in ((-1,False),(0,True),(1,True)):
        # Find exact canonical size including the cap field itself.
        candidate=replace(opt,limits=replace(opt.limits,config_bytes=1000))
        size=len(canonical(wire(candidate)).encode())
        for _ in range(3):
            candidate=replace(opt,limits=replace(opt.limits,config_bytes=size+offset))
            size=len(canonical(wire(candidate)).encode())
        if valid:validate_options(candidate)
        else:
            with pytest.raises(ValueError):validate_options(candidate)

@pytest.mark.parametrize('seconds,expected',[(0,1),(1,0),(1.0,0),(False,2),('NaN',2)])
def test_tree_seconds_native_numeric_contract(tmp_path,monkeypatch,seconds,expected):
    from shopextract.categories.woo_tree import WooTreeLimits
    files=fixture_files(tmp_path);install_transport(monkeypatch)
    limits=wire(WooTreeLimits(response_bytes=1048576,retained_bytes=1048576));limits['seconds']=seconds
    result=invoke(['categories','tree','fetch','--options',files['options'],'--limits',dump(tmp_path/'limits',limits)])
    assert result.exit_code==expected,result.output
    if seconds==0 and type(seconds) is not bool:
        data=body(result)['data'];assert data['outcome']=='unavailable' and 'zero_budget' in data['reasons']


def test_category_to_p3_snapshot_projection(tmp_path):
    files=fixture_files(tmp_path);db=tmp_path/'snapshots.db'
    result=invoke(['snapshot-save',files['categorized'],'--domain','supplier.test','--db',str(db)])
    assert result.exit_code==0,result.output
    snapshot_id=body(result)['data']['snapshot_id']
    loaded=invoke(['snapshot-load',str(snapshot_id),'--db',str(db)])
    assert loaded.exit_code==0,loaded.output
    expected=[r['product'] for r in json.loads(Path(files['categorized']).read_text())]
    assert graph_order_canonical(body(loaded)['data']['products'])==graph_order_canonical(expected)
    reviewed=invoke(['categories','policy','review',files['categorized'],'--config',files['config'],'--profile','footwear'])
    policy=dump(tmp_path/'policy-result',body(reviewed))
    saved=invoke(['snapshot-save',policy,'--domain','supplier.test','--db',str(db)])
    assert saved.exit_code==0,saved.output
    loaded=invoke(['snapshot-load',str(body(saved)['data']['snapshot_id']),'--db',str(db)])
    assert loaded.exit_code==0 and graph_order_canonical(body(loaded)['data']['products'])==graph_order_canonical(expected)
    # DB owns ordinary Product projection; explicit companion retains policy identity.
    assert body(reviewed)['data']['policy_digest']


def test_module_entrypoint_registered_categories_and_monitor():
    environment=dict(os.environ,PYTHONPATH='src',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',TOKENIZERS_PARALLELISM='false')
    for args,needle in ((['categories','tree','--help'],'fetch'),(['evidence','--help'],'prune')):
        result=subprocess.run([sys.executable,'-m','shopextract.cli',*args],capture_output=True,text=True,env=environment,timeout=15)
        assert result.returncode==0 and needle in result.stdout,result.stderr


def test_categorized_parquet_arrow_readback_lossless(tmp_path):
    pyarrow=pytest.importorskip('pyarrow.parquet')
    from decimal import Decimal
    from shopextract._evidence import decode_value
    from shopextract.categories.portable import bind_product,categorized_product_from_record
    files=fixture_files(tmp_path);record=json.loads(Path(files['categorized']).read_text())[0]
    value=categorized_product_from_record(record)
    # Synthetic native Product fields deliberately cover every empty/null distinction.
    product=copy.deepcopy(value.product);product.gtin='0012345678905'
    product.attributes={'unicode':'Été'}
    synthetic_values={'money':Decimal('1.2300'),'empty':{},'list':[],'null':None}
    product.raw_data['synthetic_values']=synthetic_values
    first=bind_product(product,value.scope,value.observations,value.mappings,value.config_digest)
    second_product=copy.deepcopy(product);second_product.attributes={}
    second=bind_product(second_product,value.scope,value.observations,value.mappings,value.config_digest)
    source=dump(tmp_path/'source',[categorized_product_to_record(first),categorized_product_to_record(second)])
    payload=tmp_path/'catalog.parquet';companion=tmp_path/'categories.json'
    result=invoke(['export',source,'--format','parquet','--output',str(payload),'--categories-output',str(companion)])
    assert result.exit_code==0,result.output
    metadata=body(result)['data']
    assert metadata['structured_json_encoding']=='evidence-json-v1' and 'attributes' in metadata['structured_json_columns']
    rows=pyarrow.read_table(payload).to_pylist()
    assert len(rows)==2 and rows[0]['gtin']=='0012345678905'
    assert decode_value(json.loads(rows[0]['attributes']))==product.attributes
    assert decode_value(json.loads(rows[0]['raw_data']))['synthetic_values']==synthetic_values
    assert rows[1]['attributes']=='{}' and rows[0]['tags']=='[]'
    assert rows[0]['price']==Decimal('99')
    assert json.loads(companion.read_text())==json.loads(Path(source).read_text())
    assert invoke(['categories','record','load',str(companion)]).exit_code==0


def test_woo_nonlist_rejected_support_vs_explicit_empty(tmp_path):
    from shopextract.categories.portable import categorized_product_from_record
    for source,expected in ((False,'malformed'),({},'malformed'),(None,'null'),([],'empty')):
        value=raw();value['categories']=source
        # Retain a genuine synthetic capture of each source state.
        from shopextract._capture import capture
        value=capture({k:v for k,v in value.items() if k!='_capture'},STORE+'/source','synthetic_fixture',observed_at=AT)
        result=invoke(['categories','normalize',dump(tmp_path/'raw',value),'--options',dump(tmp_path/'opt',wire(options()))])
        assert result.exit_code==0,result.output
        wrapped=categorized_product_from_record(body(result)['data']['categorized_products'][0])
        assert wrapped.observations[0].source_state==expected and wrapped.product.category_path==[]
        from shopextract._normalize import _normalize_woocommerce
        outcome=_normalize_woocommerce(value,STORE).outcomes['/category_path']
        assert outcome.accepted is isinstance(source,list)
        assert outcome.source_values==(source,) and wrapped.product.raw_data['categories']==source


def test_p4_oversized_dual_projection_preserves_output(tmp_path):
    from shopextract.categories.portable import bind_product
    opt=options();source=raw();source.pop('_capture',None);source['description']='é'*12000
    value=normalize_with_categories(source,Platform.WOOCOMMERCE,STORE,category_options=opt)
    record=categorized_product_to_record(value)
    record_size=len(json.dumps(record,ensure_ascii=False,separators=(',',':')).encode())
    count=min(1000,1048576//(record_size+1))
    records=[record]*count
    path=dump(tmp_path/'source',records)
    # Use exact compact source within CLI bound while dual projection expands.
    Path(path).write_text(json.dumps(records,ensure_ascii=False,separators=(',',':')))
    assert Path(path).stat().st_size<=1048576
    out=tmp_path/'out';out.write_text('old')
    result=invoke(['categories','record','load',path,'--output',str(out)])
    assert result.exit_code==2 and out.read_text()=='old',result.output
    assert body(result)['error']['code']=='E_USAGE'


def test_export_recovery_failure_retains_backups(tmp_path,monkeypatch):
    import shopextract._cli_analysis as analysis
    files=fixture_files(tmp_path);paths=[tmp_path/name for name in ('out','evidence','cats')]
    for path in paths:path.write_text('old-'+path.name)
    original=analysis.os.replace;count=0
    def fail_replace(source,target):
        nonlocal count
        count+=1
        if count in (3,4):raise OSError('injected publish and restore failure')
        return original(source,target)
    monkeypatch.setattr(analysis.os,'replace',fail_replace)
    result=invoke(['export',files['categorized'],'--format','csv','--output',str(paths[0]),'--evidence-output',str(paths[1]),'--categories-output',str(paths[2])])
    assert result.exit_code==1,result.output
    message=body(result)['error']['message']
    assert 'recovery failed' in message and 'backup=' in message and 'retained stages=' in message
    backups=list(tmp_path.glob('.*.backup'))
    assert backups and any(p.read_text()=='old-evidence' for p in backups)


def test_p4_parser_nested_arity_local_terminator_and_errors(tmp_path):
    files=fixture_files(tmp_path)
    result=invoke(['categories','policy','review',files['categorized'],'--config',files['config'],'--profile','--help'])
    # --help is a value for --profile here, not an eager help flag.
    assert result.exit_code==4 and body(result)['data']['review_reasons']==[['category_profile_conflict']]
    result=invoke(['categories','record','load','--','--help'])
    assert result.exit_code==2 and body(result)['error']['code']=='E_USAGE'
    for command in (['categories','unknown'],['categories','tree','unknown'],['categories','policy','review']):
        result=invoke(command)
        assert result.exit_code==2 and body(result)['error']['code']=='E_USAGE'


def test_storefront_config_alias_and_unknown_before_network(tmp_path,monkeypatch):
    files=fixture_files(tmp_path);api=dump(tmp_path/'api',{'unknown':'secret'})
    def forbidden(*args,**kwargs):raise AssertionError('network must not start')
    monkeypatch.setattr(httpx,'AsyncClient',forbidden)
    command=['categories','extract',STORE,'--options',files['options'],'--storefront-config',api]
    result=invoke(command);assert result.exit_code==2 and 'secret' not in result.output
    result=invoke([*command,'--output',api]);assert result.exit_code==2
    assert json.loads(Path(api).read_text())=={'unknown':'secret'}


def test_tree_malformed_missing_partial_and_artifact_aliases(tmp_path,monkeypatch):
    from shopextract.categories.woo_tree import fetch_woocommerce_category_tree,woo_tree_to_record,WooTreeLimits
    files=fixture_files(tmp_path)
    # Malformed success body is a real parser failure, not empty availability.
    install_transport(monkeypatch,rows='not-an-array')
    result=invoke(['categories','tree','fetch','--options',files['options']])
    assert result.exit_code==1,result.output
    assert body(result)['data']['outcome']=='malformed' and not body(result)['data']['confirmed_empty']
    # Captured incomplete tree lookup does not prove product category absence.
    tree=asyncio.run(fetch_woocommerce_category_tree(options().scope,limits=WooTreeLimits(requests=1),
        resolver=resolver,wire_transport=httpx.MockTransport(lambda request:httpx.Response(200,
        json=[{'id':8,'name':None,'slug':'sale','parent':0}],headers={'X-WP-Total':'1','X-WP-TotalPages':'1'})),utc_now=lambda:AT))
    assert tree.outcome=='partial'
    tree_path=dump(tmp_path/'tree',woo_tree_to_record(tree))
    result=invoke(['categories','tree','link',tree_path,files['categorized']])
    assert result.exit_code==3,result.output
    data=body(result)['data'];assert data['links'][0]['status']=='missing' and data['tree_outcome']=='partial'
    for source in (tree_path,files['categorized']):
        alias=tmp_path/'alias';os.link(source,alias)
        result=invoke(['categories','tree','link',tree_path,files['categorized'],'--output',str(alias)])
        assert result.exit_code==2
        alias.unlink()
    assert invoke(['categories','tree','link','-','-'],input='{}').exit_code==2


def test_category_export_source_alias_no_publish(tmp_path):
    files=fixture_files(tmp_path);source=files['categorized'];before=Path(source).read_bytes()
    alias=tmp_path/'alias';alias.symlink_to(source)
    result=invoke(['export',source,'--format','csv','--output',str(tmp_path/'out'),'--categories-output',str(alias)])
    assert result.exit_code==2 and Path(source).read_bytes()==before and not (tmp_path/'out').exists()

@pytest.mark.parametrize('path',['/shop/../other','/shop/%2e%2e/other','/shop/%252e%252e/other',
    '/shop/.%2e/other','/shop/%2e%2e%2fother','/shop/%5c..%5cother'])
def test_decoded_scope_path_rejects_before_http(tmp_path,monkeypatch,path):
    files=fixture_files(tmp_path)
    def forbidden(*args,**kwargs):raise AssertionError('scope escaped before HTTP')
    monkeypatch.setattr(httpx,'AsyncClient',forbidden)
    result=invoke(['categories','extract','https://supplier.test'+path,'--options',files['options']])
    assert result.exit_code==2 and body(result)['error']['code']=='E_USAGE',result.output


def test_valid_nested_scope_extract(tmp_path,monkeypatch):
    files=fixture_files(tmp_path);install_transport(monkeypatch)
    result=invoke(['categories','extract',STORE+'/nested','--options',files['options']])
    assert result.exit_code==0 and body(result)['data']['product_count']==1,result.output

@pytest.mark.parametrize('control',['enrich','restore'])
def test_shopify_native_flags_change_observed_identifiers(tmp_path,monkeypatch,control):
    original=httpx.AsyncClient;requests=[]
    # Saved native11digitUPCfixture from test_capture_provenance; explicit restore only.
    barcode='29877030712' if control=='restore' else None
    product={'id':501,'title':'Boot','handle':'boot','product_type':'Boots',
        'variants':[{'id':701,'title':'Boot','price':'99','available':True,'barcode':barcode}]}
    def handler(request):
        requests.append(str(request.url))
        if request.url.path.endswith('.js'):
            return httpx.Response(200,json={'id':501,'variants':[{'id':701,'barcode':'0012345678905'}]})
        return httpx.Response(200,json={'products':[product]})
    def client(*args,**kwargs):
        kwargs.setdefault('transport',httpx.MockTransport(handler));return original(*args,**kwargs)
    monkeypatch.setattr(httpx,'AsyncClient',client)
    command=['categories','extract',STORE,'--max-products','1','--options',dump(tmp_path/'opt',wire(options(Platform.SHOPIFY)))]
    default=invoke(command);assert default.exit_code==3,default.output
    first=body(default)['data']['categorized_products'][0]['product']
    assert first['product']['gtin'] is None and not any(url.endswith('.js') for url in requests)
    requests.clear()
    result=invoke([*command,'--enrich-identifiers' if control=='enrich' else '--restore-short-gtin'])
    assert result.exit_code==3,result.output
    native=body(result)['data']['categorized_products'][0]['product']
    if control=='enrich':
        assert native['product']['gtin']=='0012345678905'
        assert sum(url.endswith('.js') for url in requests)==1
        assert native['product']['raw_data']['_identifier_sources'][0]['variant_id']=='701'
    else:
        assert native['product']['gtin']=='0029877030712'
        assert native['product']['raw_data']['_identifier_normalization'][0]['policy']=='restore_upc_leading_zero'
        assert not any(url.endswith('.js') for url in requests)

@pytest.mark.parametrize('stage',['payload','evidence'])
@pytest.mark.parametrize('delta',[-1,0,1])
def test_categorized_actual_staged_file_size_boundary(tmp_path,monkeypatch,stage,delta):
    import shopextract.export as exporter
    files=fixture_files(tmp_path);paths=[tmp_path/name for name in ('out','evidence','cats')]
    for path in paths:path.write_text('old-'+path.name)
    original=exporter.to_csv
    def padded(products,path,**kwargs):
        original(products,path,**kwargs)
        target=Path(path if stage=='payload' else kwargs['evidence_path'])
        size=1048576+delta
        # Deliberate external serialization fault/boundary padding after real native export.
        with target.open('ab') as stream:stream.write(b' '*(size-target.stat().st_size))
    monkeypatch.setattr(exporter,'to_csv',padded)
    result=invoke(['export',files['categorized'],'--format','csv','--output',str(paths[0]),'--evidence-output',str(paths[1]),'--categories-output',str(paths[2])])
    if delta>0:
        assert result.exit_code==2,result.output
        assert body(result)['error']['code']=='E_USAGE'
        assert all(p.read_text()=='old-'+p.name for p in paths)
    else:
        assert result.exit_code==0,result.output
        assert paths[0 if stage=='payload' else 1].stat().st_size==1048576+delta


def graph_order_canonical(records):
    """Native DB orders evidence by identity; facts/values/IDs remain exact."""
    result=copy.deepcopy(records)
    for record in result:
        graph=record.get('evidence_contract')
        if graph:
            for name,key in (('evidence','evidence_id'),('observations','observation_id')):
                if name in graph:graph[name].sort(key=lambda value:value[key])
    return result
