"""Reviewed Google subset, projection and independent downstream regressions."""
from copy import deepcopy
from decimal import Decimal
from pathlib import Path
import json
import xml.etree.ElementTree as ET
import pytest

URL='https://fixture.invalid'
def base():return {'external_id':'P1','canonical_product_id':'canon1','title':'Widget','description':'Source description','product_url':URL+'/p','image_url':URL+'/i.jpg','price':'10','currency':'USD','in_stock':True,'vendor':'Acme','gtin':'4006381333931','condition':'new'}
def context():return {'destination':'shopping_ads','country':'US','condition':'new','category':'general','variant':False,'identifier_status':'present'}
def assess(p=None,c=None):
 from shopextract.validate._destination import assess_google
 return assess_google(base() if p is None else p,context=context() if c is None else c)

@pytest.mark.parametrize('case,rule,status',[
 ('G-ID1',None,'subset_pass'),('G-ID2',None,'subset_pass'),('G-ID3',None,'subset_pass'),('G-ID4','identifiers_need_context','needs_context'),('G-ID5','contradictory_identifiers','blocked'),
 ('G-BR1','missing_brand','blocked'),('G-BR2',None,'subset_pass'),('G-CO1',None,'subset_pass'),('G-CO2','missing_condition','blocked'),('G-CO3','condition_need_context','needs_context'),
 ('G-V1','missing_item_group_id','blocked'),('G-V2',None,'subset_pass'),('G-V3','missing_item_group_id','blocked'),('G-AP1','apparel_profile_not_implemented','needs_context'),('G-U1','unsupported_rule_branch','needs_context')])
def test_google_conditional_table(case,rule,status,tmp_path):
 p=base();c=context()
 if case=='G-ID2':p.pop('gtin');p['mpn']='M1'
 if case in ('G-ID3','G-ID4'):p.pop('gtin');c['identifier_status']='absent' if case=='G-ID3' else 'unknown'
 if case in ('G-ID3','G-ID5'):p['identifier_exists']='no'
 if case=='G-BR1':p.pop('vendor')
 if case=='G-BR2':p.pop('vendor');c['category']='books'
 if case=='G-CO1':p['condition']='refurbished';c['condition']='refurbished'
 if case=='G-CO2':p.pop('condition');c['condition']='used'
 if case=='G-CO3':p.pop('condition');c['condition']='unknown'
 if case.startswith('G-V'):c['variant']=True
 if case=='G-V2':p.update(item_group_id='G1',color='Blue')
 if case=='G-V3':c.update(destination='free_listings',country='PK')
 if case=='G-AP1':c['category']='1604'
 if case=='G-U1':c['country']='XX'
 result=assess(p,c);assert result['subset_status']==status
 if rule:
  i=next(i for i in result['issues'] if i['rule_id']==rule)
  assert i['severity']==('error' if status=='blocked' else 'warning')
 else:assert not result['issues']
 assert result['unassessed_checks'] and result['rules_version']=='google-catalog-subset-2026-11-01'
 if case=='G-ID3':assert result['projection']['identifier_exists']=='no'
 if case=='G-ID4':assert 'identifier_exists' not in result['projection']
 from shopextract.validate.marketplace import validate
 from shopextract.export import to_feed
 report=validate([p],context=c)
 assert report.subset_status==status and {i.rule_id for i in report.issues}=={i['rule_id'] for i in result['issues']}
 feed=to_feed([p],str(tmp_path/'feed.xml'),context=c)
 assert feed['retained']==(0 if status=='blocked' else 1)
 assert {i['rule_id'] for i in feed['issues']}=={i['rule_id'] for i in result['issues']}

@pytest.mark.parametrize('case',['negative','nonfinite','placeholder','no_id','unknown_stock','unsupported_currency'])
def test_invalid_core_never_eligible(case):
 p=base()
 if case=='negative':p['price']='-1'
 if case=='nonfinite':p['price']='NaN'
 if case=='placeholder':p['image_url']=URL+'/placeholder/i.jpg'
 if case=='no_id':p.pop('external_id');p.pop('canonical_product_id')
 if case=='unknown_stock':p.pop('in_stock')
 if case=='unsupported_currency':
  from shopextract._normalize import normalize
  from shopextract._models import Platform
  from dataclasses import asdict
  native=normalize({'id':1,'title':'Widget','variants':[{'id':2,'price':'10'}]},Platform.SHOPIFY,URL)
  p=asdict(native)
 result=assess(p);assert result['subset_status']=='blocked' and any(i['severity']=='error' for i in result['issues'])


def test_vendor_canonical_feed_projection_stable(tmp_path):
 from shopextract.export import to_feed
 p=base();p.pop('external_id');target=tmp_path/'feed.xml'
 result=to_feed([p],str(target),context=context())
 ns={'g':'http://base.google.com/ns/1.0'};item=ET.parse(target).find('./channel/item')
 assert item.find('g:id',ns).text=='canon1' and item.find('g:brand',ns).text=='Acme'
 p.update(title='Changed',price='11');assert assess(p)['projection']['external_id']=='canon1'
 assert result['retained']==1 and result['skipped']==0

def test_unknown_stock_projection_omits_default():
 p=base();p.pop('in_stock');r=assess(p)
 assert 'in_stock' not in r['projection'] and any(i['rule_id']=='missing_availability' for i in r['issues'])

def test_missing_id_feed_skipped(tmp_path):
 from shopextract.export import to_feed
 p=base();p.pop('external_id');p.pop('canonical_product_id');target=tmp_path/'f.xml'
 r=to_feed([base(),p],str(target),context=context())
 assert r['retained']==1 and r['skipped']==1 and len(ET.parse(target).findall('./channel/item'))==1

def test_cli_feed_export_counts(tmp_path):
 from click.testing import CliRunner
 from shopextract.cli import main
 p=base();p.pop('external_id');p.pop('canonical_product_id')
 source=tmp_path/'p.json';source.write_text(json.dumps([base(),p]));target=tmp_path/'f.xml'
 r=CliRunner().invoke(main,['--output-format','json','export',str(source),'--format','google_shopping','-o',str(target)])
 assert r.exit_code==0,r.output
 data=json.loads(r.stdout)['data'];assert data['retained']==1 and data['skipped']==1 and data['issues']

@pytest.mark.parametrize('a,b',[('Widget shampoo 500ml','Widget shampoo 1L'),('Widget shampoo 500ml','Widget conditioner 500ml'),('Widget taupe 500ml','Widget white 500ml')])
@pytest.mark.parametrize('operation',['fuzzy','duplicates'])
def test_incompatible_title_candidates_veto(a,b,operation):
 from shopextract.compare.match import fuzzy_match
 from shopextract.validate.duplicates import find_duplicates
 left={'title':a};right={'title':b}
 result=fuzzy_match([left],[right],threshold=.3) if operation=='fuzzy' else find_duplicates([left,right],threshold=.3)
 assert result==[]

def test_supported_identifier_positive():
 from shopextract.compare.identity_match import classify_match
 assert classify_match(base(),base()).relation.value=='exact'

def test_categories_once_per_product():
 from shopextract.analyze.stats import analyze_products
 assert analyze_products([{'category_path':['A','A'],'product_type':'A'}]).categories=={'A':1}

def test_stock_three_way_reconciles():
 from shopextract.analyze.stats import analyze_products
 r=analyze_products([{}, {'in_stock':None},{'in_stock':True},{'in_stock':False}])
 assert (r.in_stock,r.out_of_stock,r.unknown_stock)==(1,1,2) and r.total_products==4

def test_empty_stats_unknown_zero():
 from shopextract.analyze.stats import analyze_products
 r=analyze_products([]);assert r.unknown_stock==0 and r.in_stock==r.out_of_stock==0

def test_one_serialization_per_export_with_evidence(tmp_path,monkeypatch):
 from shopextract._normalize import normalize
 from shopextract._models import Platform
 from shopextract.export import to_csv
 import shopextract.export._bundle as module
 from shopextract.export._bundle import load_evidence_sidecar
 product=normalize({'id':1,'title':'Widget','currency':'USD','variants':[{'id':2,'price':'10'}]},Platform.SHOPIFY,URL)
 original=module.product_to_record;calls=[]
 def tracked(p):calls.append(p);return original(p)
 monkeypatch.setattr(module,'product_to_record',tracked)
 target=tmp_path/'p.csv';side=tmp_path/'e.json';to_csv([product],str(target),evidence_path=str(side))
 assert len(calls)==1
 restored=load_evidence_sidecar(json.loads(side.read_text()),target.read_bytes())
 assert restored==[product]


def test_presence_rich_policy_not_product_eligible():
 p=base();p['raw_data']={'og:type':'website','og:title':'Returns policy'}
 r=assess(p)
 assert r['subset_status']=='blocked' and any(i['rule_id']=='product_evidence' for i in r['issues'])


def native_stock_default(stock=None,ident=1,amount="1000",sku=None):
 from shopextract._capture import capture
 from shopextract._normalize import normalize
 from shopextract._models import Platform
 raw={'id':ident,'name':'Widget','description':'Source description','images':[{'src':URL+'/i.jpg'}],'permalink':URL+'/p','prices':{'price':amount,'currency_code':'USD','currency_minor_unit':2},'brands':[{'name':'Acme'}],'gtin':'4006381333931'}
 if stock is not None:raw['is_in_stock']=stock
 if sku is not None:raw['sku']=sku
 return normalize(capture(raw,URL+'/api','woocommerce_api'),Platform.WOOCOMMERCE,URL)

@pytest.mark.parametrize('command',['analyze','validate','feed'])
def test_native_unsupported_stock_cli_preserves_unknown(tmp_path,command):
 from click.testing import CliRunner
 from shopextract.cli import main
 from shopextract._portable import product_to_record
 product=native_stock_default();assert product.in_stock is True and product.currency=='USD'
 source=tmp_path/'p.json';source.write_text(json.dumps([product_to_record(product)]))
 args=['analyze-file',str(source)] if command=='analyze' else ['validate',str(source)] if command=='validate' else ['export',str(source),'--format','google_shopping','-o',str(tmp_path/'f.xml')]
 r=CliRunner().invoke(main,['--output-format','json',*args]);data=json.loads(r.stdout)['data']
 if command=='analyze':assert r.exit_code==0 and data['statistics']['unknown_stock']==1 and data['statistics']['in_stock']==0
 elif command=='validate':assert r.exit_code==4 and data['subset_status']=='blocked' and any(i['rule_id']=='missing_availability' for i in data['issues'])
 else:assert r.exit_code==0 and data['retained']==0 and data['skipped']==1 and any(i['rule_id']=='missing_availability' for i in data['issues'])


def test_cli_subset_report_fields_not_dropped(tmp_path):
 from click.testing import CliRunner
 from shopextract.cli import main
 source=tmp_path/'p.json';source.write_text(json.dumps([base()]))
 r=CliRunner().invoke(main,['--output-format','json','validate',str(source)])
 data=json.loads(r.stdout)['data']
 assert data['subset_status']=='needs_context' and data['rules_version']=='google-catalog-subset-2026-11-01' and data['unassessed_checks']
 assert any(i['rule_id']=='unsupported_rule_branch' for i in data['issues'])


def test_two_exports_same_product_do_not_cache_stale_snapshot(tmp_path):
 from shopextract.export import to_csv
 from shopextract.export._bundle import load_evidence_sidecar
 product=native_stock_default();target=tmp_path/'p.csv';side=tmp_path/'e.json'
 to_csv([product],str(target),evidence_path=str(side));before=target.read_bytes()
 product.title='Changed';product.price=Decimal('11.234')
 to_csv([product],str(target),evidence_path=str(side))
 restored=load_evidence_sidecar(json.loads(side.read_text()),target.read_bytes())
 assert target.read_bytes()!=before and restored==[product] and restored[0].price==Decimal('11.234')

@pytest.mark.parametrize('kind',['nan','pointer'])
def test_invalid_producer_preserves_both_existing_artifacts(tmp_path,kind):
 from shopextract.export import to_csv
 product=native_stock_default();target=tmp_path/'p.csv';side=tmp_path/'e.json';target.write_bytes(b'old CSV');side.write_bytes(b'old evidence')
 if kind=='nan':product.price=Decimal('NaN')
 else:product.evidence_contract.evidence[0].pointer='/absent'
 with pytest.raises(ValueError):to_csv([product],str(target),evidence_path=str(side))
 assert target.read_bytes()==b'old CSV' and side.read_bytes()==b'old evidence'

@pytest.mark.parametrize('all_skipped',[False,True])
def test_filtered_native_feed_companion_exact_retained_subset(tmp_path,all_skipped):
 from shopextract.export import to_feed
 from shopextract.export._bundle import load_evidence_sidecar
 valid=native_stock_default(stock=True,ident=3);second=native_stock_default(stock=True,ident=1);blocked=native_stock_default(ident=2)
 products=[blocked] if all_skipped else [blocked,valid,second]
 expected=[] if all_skipped else [valid,second]
 target=tmp_path/'feed.xml';side=tmp_path/'evidence.json'
 result=to_feed(products,str(target),evidence_path=str(side),context=context())
 restored=load_evidence_sidecar(json.loads(side.read_text()),target.read_bytes())
 assert result['retained']==len(expected) and result['skipped']==1
 assert restored==expected
 assert [p.evidence_contract for p in restored]==[p.evidence_contract for p in expected]
 assert len(ET.parse(target).findall('./channel/item'))==len(expected)


def test_uncontracted_typed_default_stock_is_unknown():
 from shopextract._models import Product
 from shopextract.analyze.stats import analyze_products
 p=Product(title='Widget',price=Decimal('10'),external_id='P1',description='Source',product_url=URL+'/p',image_url=URL+'/i.jpg',vendor='Acme',gtin='4006381333931')
 assert p.in_stock is True
 r=analyze_products([p]);assert r.unknown_stock==1 and r.in_stock==0
 assert any(i['rule_id']=='missing_availability' for i in assess(p)['issues'])


def test_explicit_zero_amount_is_not_invalid_money():
 p=base();p['price']='0';r=assess(p)
 assert not any(i['rule_id']=='invalid_price' for i in r['issues']) and r['subset_status']=='needs_context'
 assert any(i['rule_id']=='zero_price_needs_context' and i['severity']=='warning' for i in r['issues'])
 assert r['unassessed_checks']

@pytest.mark.parametrize('kind',['gtin','condition'])
def test_invalid_identifier_or_condition_conflict(kind):
 p=base();c=context()
 if kind=='gtin':p['gtin']='abc'
 else:c['condition']='used'
 r=assess(p,c)
 assert r['subset_status']=='blocked' and any(i['rule_id']==('invalid_gtin' if kind=='gtin' else 'condition_conflict') for i in r['issues'])


def test_unsupported_native_condition_default_is_absent():
 p=native_stock_default(stock=True);c=context();c['condition']='used'
 r=assess(p,c)
 assert any(i['rule_id']=='missing_condition' for i in r['issues'])
 assert not any(i['rule_id']=='condition_conflict' for i in r['issues']) and not r['projection'].get('condition')

@pytest.mark.parametrize('field',['gtin','mpn'])
def test_unsourced_identifier_cannot_satisfy_assignment(field):
 p=native_stock_default(stock=True)
 p.gtin='00012345600012' if field=='gtin' else None
 if field=='mpn':p.mpn='M1'
 r=assess(p)
 assert r['subset_status']=='blocked' and field not in r['projection']
 assert any(i['rule_id']=='unsupported_'+field for i in r['issues'])


def test_context_variant_type_cannot_bypass_grouping():
 c=context();c['variant']='true'
 r=assess(c=c)
 assert r['subset_status']=='needs_context' and any(i['rule_id']=='unsupported_rule_branch' for i in r['issues'])


def test_zero_price_source_observed_but_eligibility_needs_context():
 p=native_stock_default(stock=True,amount='0');r=assess(p)
 assert p.trust_view()['/price']['state']=='observed' and p.price==0
 assert r['subset_status']=='needs_context' and any(i['rule_id']=='zero_price_needs_context' for i in r['issues'])
 assert not any(i['rule_id']=='invalid_price' for i in r['issues'])

@pytest.mark.parametrize('native',[False,True])
def test_idealo_sku_only_identity_retained(tmp_path,native):
 import csv
 from shopextract.export import to_feed
 from shopextract.export._bundle import load_evidence_sidecar
 if native:
  product=native_stock_default(stock=True,sku='SKU1');product.external_id='';product.canonical_product_id=''
 else:product={'sku':'SKU1','title':'Widget','price':'10','currency':'USD'}
 target=tmp_path/'feed.tsv';side=tmp_path/'side.json'
 r=to_feed([product],str(target),format='idealo',evidence_path=str(side) if native else None)
 assert r['retained']==1 and r['skipped']==0
 assert not any(i['rule_id']=='missing_id' for i in r['issues'])
 assert list(csv.DictReader(target.open(),delimiter='\t'))[0]['sku']=='SKU1'
 if native:
  restored=load_evidence_sidecar(json.loads(side.read_text()),target.read_bytes())
  assert restored==[product] and restored[0].evidence_contract==product.evidence_contract


def test_mutated_stock_scalar_cannot_borrow_prior_observation():
 from shopextract.analyze.stats import analyze_products
 p=native_stock_default(stock=False);p.in_stock=True
 r=analyze_products([p]);assert r.unknown_stock==1 and r.in_stock==0 and r.out_of_stock==0
