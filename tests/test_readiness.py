"""Local informational profile commands; no merchant/network approval claims."""
import json
import httpx
import pytest
from click.testing import CliRunner
from tests.test_downstream_remediation import base,context


def report(products=None,target='google_shopping',**kwargs):
 from shopextract._readiness import readiness_report
 return readiness_report([base()] if products is None else products,target,**kwargs)

@pytest.fixture(autouse=True)
def no_network(monkeypatch):
 async def denied(*a,**kw):raise AssertionError('readiness attempted HTTP')
 monkeypatch.setattr(httpx.AsyncClient,'send',denied)
 monkeypatch.setattr(httpx.Client,'send',lambda *a,**kw:(_ for _ in ()).throw(AssertionError('readiness attempted HTTP')))

@pytest.mark.parametrize('kind',['context','currency','id'])
def test_google_profile_context_and_core_blockers(kind):
 p=base()
 if kind=='currency':p['currency']='QQQ'
 if kind=='id':p.pop('external_id');p.pop('canonical_product_id')
 r=report([p]);assert r['ready'] is False and r['assessment_scope']=='limited_google_catalog_subset'
 expected='unsupported_rule_branch' if kind=='context' else 'invalid_currency' if kind=='currency' else 'missing_id'
 assert any(c['code']==expected for c in r['items'][0]['checks'])

@pytest.mark.parametrize('strict',[False,True])
def test_actual_cli_informational_or_strict_retains_report(tmp_path,strict):
 from shopextract.cli import main
 source=tmp_path/'p.json';source.write_text(json.dumps([base()]))
 r=CliRunner().invoke(main,['--output-format','json','readiness',str(source),'--target','google_shopping',*(['--strict'] if strict else [])])
 assert r.exit_code==(3 if strict else 0),r.output
 payload=json.loads(r.stdout);assert payload['data']['ready'] is False and payload['data']['items']
 assert payload['ok'] is (not strict)


def test_schema_partial_is_coverage_not_vocabulary_invalid():
 r=report([{'@type':'Product','name':'Widget'}],target='schema_org')
 assert r['assessment_scope']=='schema_model_coverage' and r['ready'] is False
 assert r['items'][0]['coverage']['name'] is True and r['items'][0]['coverage']['offer'] is False
 assert all(c['code']!='invalid_schema_vocabulary' for c in r['items'][0]['checks'])


def test_schema_group_and_variant_coverage_separate():
 p={'@type':'ProductGroup','name':'Group','productGroupID':'G1','hasVariant':[{'@type':'Product','name':'Blue','sku':'B1','offers':{'price':'10','priceCurrency':'USD'}}]}
 r=report([p],target='schema_org');item=r['items'][0]
 assert item['kind']=='ProductGroup' and item['coverage']['offer'] is False
 assert len(item['variants'])==1 and item['variants'][0]['coverage']['offer'] is True
 assert 'price' not in item

@pytest.mark.parametrize('kind',['complete','seller','brand','currency'])
def test_openai_basic_fields_unknown_availability_and_missing(kind):
 p=base();p['in_stock']=None
 if kind=='brand':p.pop('vendor')
 if kind=='currency':p['currency']=''
 r=report([p],target='openai_discovery',seller_name='Merchant' if kind!='seller' else None)
 assert r['assessment_scope']=='openai_basic_product_fields' and r['ready'] is (kind=='complete')
 if kind=='complete':assert r['items'][0]['projection']['availability']=='unknown'
 else:assert any(c['field']==('seller_name' if kind=='seller' else kind) for c in r['items'][0]['checks'])


def test_cli_explicit_seller_context_never_domain_guess(tmp_path):
 from shopextract.cli import main
 source=tmp_path/'p.json';source.write_text(json.dumps([base()]))
 r=CliRunner().invoke(main,['--output-format','json','readiness',str(source),'--target','openai_discovery','--seller-name','Explicit Merchant'])
 assert r.exit_code==0,r.output
 data=json.loads(r.stdout)['data'];assert data['items'][0]['projection']['seller_name']=='Explicit Merchant'
 assert 'api_key' not in json.dumps(data).lower()


def test_openai_variants_not_whole_feed_ready_from_basic_fields():
 p=base();p['variants']=[{'variant_id':'V1','price':'10'}]
 r=report([p],target='openai_discovery',seller_name='Merchant')
 assert not r['ready'] and any(c['code']=='variant_grouping_unassessed' and c['state']=='needs_context' for c in r['items'][0]['checks'])


def test_acp_perfect_catalog_protocol_always_unassessed():
 r=report(target='acp',context=context(),seller_name='Merchant')
 assert r['ready'] is False and r['assessment_scope']=='unsupported_protocol_assessment'
 assert r['provenance']['maturity']=='RFCProposal'
 assert any(c['code']=='unsupported_protocol_assessment' for c in r['items'][0]['checks'])


def test_report_deterministic_after_reordering():
 a=base();b=base();b['external_id']='P2';b['title']='Second'
 assert report([a,b],target='acp')==report([b,a],target='acp')


def test_invalid_target_before_file_read(monkeypatch):
 from shopextract.cli import main
 calls=[]
 import shopextract._cli_data as module
 def denied(path):calls.append(path);raise AssertionError('invalid target read a file')
 monkeypatch.setattr(module,'read_json_file',denied)
 r=CliRunner().invoke(main,['--output-format','json','readiness','/unreadable/never.json','--target','made_up'])
 assert r.exit_code==2 and json.loads(r.stdout)['error']['code']=='E_USAGE' and calls==[]


def test_malformed_context_cli_usage(tmp_path):
 from shopextract.cli import main
 source=tmp_path/'p.json';source.write_text(json.dumps([base()]));ctx=tmp_path/'c.json';ctx.write_text('[1]')
 r=CliRunner().invoke(main,['--output-format','json','readiness',str(source),'--target','google_shopping','--context',str(ctx)])
 assert r.exit_code==2 and 'context' in r.output.lower()


def test_google_qualified_subset_positive_scope():
 r=report(context=context())
 assert r['ready'] is True and r['assessment_scope']=='limited_google_catalog_subset'
 assert r['items'][0]['checks']==[]


def test_schema_complete_coverage_positive_scope():
 p={'@type':'Product','name':'Widget','url':'https://fixture.invalid/p','image':'https://fixture.invalid/i.jpg','sku':'P1','offers':{'price':'10','priceCurrency':'USD'}}
 r=report([p],target='schema_org')
 assert r['ready'] is True and all(r['items'][0]['coverage'].values())


def test_portable_native_default_stock_openai_unknown(tmp_path):
 from shopextract.cli import main
 from shopextract._portable import product_to_record
 from tests.test_downstream_remediation import native_stock_default
 p=native_stock_default();assert p.in_stock is True
 source=tmp_path/'p.json';source.write_text(json.dumps([product_to_record(p)]))
 r=CliRunner().invoke(main,['--output-format','json','readiness',str(source),'--target','openai_discovery','--seller-name','Merchant'])
 assert r.exit_code==0,r.output
 data=json.loads(r.stdout)['data'];assert data['ready'] is True and data['items'][0]['projection']['availability']=='unknown'

@pytest.mark.parametrize('target,source_fragment',[('google_shopping','support.google.com/merchants'),('schema_org','schema.org/Product'),('openai_discovery','developers.openai.com/commerce/specs/file-upload/products'),('acp','github.com/agentic-commerce-protocol')])
def test_required_profile_metadata_and_primary_source(target,source_fragment):
 r=report(target=target)
 assert r['schema_version']=='1.0' and r['rule_set'] and r['source_date']=='2026-11-01'
 assert isinstance(r['provenance'],dict) and r['provenance']
 assert any(source_fragment in link for link in r['source_links'])


def diagnostic(result,code):return any(d['code']==code and d['state']=='needs_context' for d in result.get('diagnostics',[]))

@pytest.mark.parametrize('count',[1000,1001])
def test_direct_top_record_budget(count):
 values=[dict(base(),external_id='P'+str(i)) for i in range(count)]
 r=report(values,target='openai_discovery',seller_name='Merchant')
 if count==1000:assert r['ready'] and len(r['items'])==1000
 else:assert not r['ready'] and r['items']==[] and diagnostic(r,'record_budget_exceeded') and r['summary']['omitted_records']==1001

@pytest.mark.parametrize('count',[100,101])
def test_variant_budget_global_across_groups(count):
 groups=[{'@type':'ProductGroup','name':'Group'+str(n),'productGroupID':'G'+str(n),'hasVariant':[{'@type':'Product','name':'Child','sku':f'{n}-{i}'} for i in range(size)]} for n,size in enumerate([50,count-50])]
 r=report(groups,target='schema_org')
 assert diagnostic(r,'variant_budget_exceeded') is (count>100)
 assert len(r['items'])==2
 assert sum(len(i['variants']) for i in r['items'])==100
 if count>100:assert not r['ready'] and r['summary']['omitted_variants']==1

@pytest.mark.parametrize('depth',[8,9])
def test_variant_depth_budget(depth):
 node={'@type':'Product','name':'Leaf','sku':'L1'}
 for n in range(depth):node={'@type':'ProductGroup','name':'Group'+str(n),'hasVariant':[node]}
 r=report([node],target='schema_org')
 assert diagnostic(r,'variant_depth_exceeded') is (depth>8)


def test_active_variant_cycle_is_bounded():
 node={'@type':'ProductGroup','name':'Cycle'};node['hasVariant']=[node]
 r=report([node],target='schema_org')
 assert not r['ready'] and diagnostic(r,'cyclic_variant_graph') and r['items']==[]

@pytest.mark.parametrize('size',[8192,8193])
def test_profile_field_byte_budget(size):
 p=base();p['description']='x'*size
 r=report([p],target='openai_discovery',seller_name='Merchant')
 assert diagnostic(r,'field_byte_budget_exceeded') is (size>8192)
 if size>8192:assert not r['ready'] and r['items']==[]
 else:assert r['ready']


def test_aggregate_projection_byte_budget_bounded_report():
 long='x'*8192;values=[]
 for n in range(200):
  p=base();p.update(external_id=f'{n:04}'+long[4:],title=long,description=long,product_url='https://fixture.invalid/'+long[24:],image_url='https://fixture.invalid/'+long[24:],vendor=long);values.append(p)
 r=report(values,target='openai_discovery',seller_name=long)
 assert not r['ready'] and diagnostic(r,'projection_byte_budget_exceeded')
 assert len(json.dumps(r).encode())<=8*1024*1024


def test_actual_cli_record_boundary(tmp_path):
 from shopextract.cli import main
 values=[dict(base(),external_id='P'+str(i)) for i in range(1001)]
 source=tmp_path/'p.json';source.write_text(json.dumps(values[:1000]))
 args=['--output-format','json','readiness',str(source),'--target','openai_discovery','--seller-name','Merchant']
 r=CliRunner().invoke(main,args)
 assert r.exit_code==0 and len(json.loads(r.stdout)['data']['items'])==1000
 source.write_text(json.dumps(values));r=CliRunner().invoke(main,args)
 assert r.exit_code==2 and json.loads(r.stdout)['error']['code']=='E_USAGE'

@pytest.mark.parametrize('count',[1000,1001])
def test_source_variant_input_budget_separate_from_coverage(count):
 group={'@type':'ProductGroup','name':'Group','hasVariant':[{'@type':'Product','name':'Child','sku':str(i)} for i in range(count)]}
 r=report([group],target='acp')
 assert diagnostic(r,'variant_input_budget_exceeded') is (count>1000)
 assert len(r['items'])==(0 if count>1000 else 1)


def test_multibyte_profile_field_budget_counts_utf8():
 p=base();p['description']='é'*4097
 r=report([p],target='openai_discovery',seller_name='Merchant')
 assert diagnostic(r,'field_byte_budget_exceeded') and not r['ready']


def test_native25_265_variants_deep_provenance_cli_is_valid_input(tmp_path):
 from shopextract.cli import main
 from shopextract._capture import capture
 from shopextract._normalize import normalize
 from shopextract._models import Platform
 from shopextract._portable import product_to_record
 from tests.test_adapter_coverage import parent
 products=[]
 for i in range(25):
  depth={'source':'historical-shape'}
  for _ in range(11):depth={'nested':depth}
  raw=parent(id=i+1,permalink='https://fixture.invalid/p/'+str(i),brands=[{'name':'Acme'}],gtin='4006381333931',is_in_stock=True,
    prices={'price':'1000','currency_minor_unit':2,'currency_code':'USD'},variants=[{'id':(i+1)*100+j,'price':'1.234','is_in_stock':True} for j in range(11 if i<15 else 10)],provenance=depth)
  products.append(normalize(capture(raw,'https://fixture.invalid/api','woocommerce_api'),Platform.WOOCOMMERCE,'https://fixture.invalid'))
 assert len(products)==25 and sum(len(p.variants) for p in products)==265
 source=tmp_path/'p.json';source.write_text(json.dumps([product_to_record(p) for p in products]))
 r=CliRunner().invoke(main,['--output-format','json','readiness',str(source),'--target','openai_discovery','--seller-name','Merchant'])
 assert r.exit_code==0,r.output[:300]
 data=json.loads(r.stdout)['data'];assert len(data['items'])==25 and data['ready'] is False
 assert all(any(c['code']=='variant_grouping_unassessed' for c in item['checks']) for item in data['items'])


def test_omitted_variant_subtree_counts_descendants():
 node={'@type':'ProductGroup','name':'Over','hasVariant':[{'@type':'Product','sku':'A'},{'@type':'Product','sku':'B'}]}
 for n in range(9):node={'@type':'ProductGroup','name':str(n),'hasVariant':[node]}
 r=report([node],target='schema_org')
 assert diagnostic(r,'variant_depth_exceeded') and r['summary']['omitted_variants']==3

@pytest.mark.parametrize('value,code',[('https://fixture.invalid/uncaptured','uncaptured_variant_reference'),(17,'invalid_variant_shape')])
def test_unassessed_variant_shape_returns_bounded_context(value,code):
 r=report([{'@type':'ProductGroup','name':'Group','hasVariant':value}],target='schema_org')
 assert not r['ready'] and diagnostic(r,code) and r['items']==[]


def nested_variant_group(depth):
 node={'@type':'Product','name':'Leaf','sku':'L1'}
 for n in range(depth):node={'@type':'ProductGroup','name':str(n),'hasVariant':[node]}
 return node


def test_sort_key_does_not_recursively_escape_child_json():
 from shopextract._readiness import _key
 key=_key(nested_variant_group(12))
 assert sum(len(part.encode()) for part in (key if isinstance(key,tuple) else (key,)))<20*1024

@pytest.mark.parametrize('depth',[64,65])
def test_source_graph_depth_boundary_after_bounded_key(depth):
 r=report([nested_variant_group(depth)],target='schema_org')
 assert diagnostic(r,'source_variant_depth_exceeded') is (depth>64)
 if depth==64:assert r['items'] and diagnostic(r,'variant_depth_exceeded')
 else:assert r['items']==[]

@pytest.mark.parametrize('override',[False,True])
def test_cli_qualified_google_context_and_country_override(tmp_path,override):
 from shopextract.cli import main
 source=tmp_path/'p.json';source.write_text(json.dumps([base()]));ctx=tmp_path/'c.json';ctx.write_text(json.dumps(context()))
 args=['--output-format','json','readiness',str(source),'--target','google_shopping','--context',str(ctx)]
 if override:args+=['--country','XX']
 r=CliRunner().invoke(main,args);assert r.exit_code==0,r.output
 data=json.loads(r.stdout)['data'];assert data['ready'] is (not override)
 if override:assert any(c['code']=='unsupported_rule_branch' for c in data['items'][0]['checks'])


def test_cli_complete_schema_coverage_positive(tmp_path):
 from shopextract.cli import main
 p={'@type':'Product','name':'Widget','url':'https://fixture.invalid/p','image':'https://fixture.invalid/i.jpg','sku':'P1','offers':{'price':'10','priceCurrency':'USD'}}
 source=tmp_path/'p.json';source.write_text(json.dumps([p]))
 r=CliRunner().invoke(main,['--output-format','json','readiness',str(source),'--target','schema_org'])
 assert r.exit_code==0 and json.loads(r.stdout)['data']['ready'] is True

@pytest.mark.parametrize('field',['item_id','external_id','sku','productGroupID'])
def test_identifier_container_diagnosed_before_materialization(field):
 bad={};bad['cycle']=bad
 if field=='external_id':bad=['x'*8193]*8
 p=base();p[field]=bad
 r=report([p],target='acp')
 assert diagnostic(r,'unsupported_identifier_shape') and not r['ready'] and r['items']==[]


def test_legitimate_schema_containers_keep_bounded_identity_label():
 p={'@type':'Product','name':'Widget','productID':'P1','url':{'@id':'https://fixture.invalid/p'},'image':{'@type':'ImageObject','url':'https://fixture.invalid/i.jpg'},'brand':{'@type':'Brand','name':'Acme'},'offers':{'@type':'Offer','price':'10','priceCurrency':'USD'}}
 r=report([p],target='schema_org')
 assert r['ready'] and r['items'][0]['item_id']=='P1'
 assert not diagnostic(r,'unsupported_identifier_shape')

@pytest.mark.parametrize('priority',['identity','url'])
def test_identity_url_sorting_precedes_differing_brand(priority):
 a=dict(base(),external_id='A',brand='ZZZ',product_url='https://fixture.invalid/a')
 b=dict(base(),external_id='B',brand='AAA',product_url='https://fixture.invalid/b')
 if priority=='url':
  for p in (a,b):p.pop('external_id');p.pop('canonical_product_id')
 r=report([b,a],target='acp')
 assert [i['item_id'] for i in r['items']]==(['A','B'] if priority=='identity' else ['https://fixture.invalid/a','https://fixture.invalid/b'])
 assert r==report([a,b],target='acp')
