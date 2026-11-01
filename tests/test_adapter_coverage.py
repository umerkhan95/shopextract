"""Native adapter source coverage; synthetic HTTP transport only."""
import json
from decimal import Decimal
import httpx
import pytest
from shopextract._capture import capture
from shopextract._models import Platform
from shopextract._normalize import normalize
from shopextract.extractors.woocommerce import WooCommerceExtractor
from shopextract.extractors.shopify import ShopifyExtractor
from shopextract.extractors.magento_graphql import MagentoGraphQLExtractor

URL='https://fixture.invalid'
def parent(**extra):return {'id':1,'name':'Widget','description':'Source description','images':[{'src':URL+'/i.jpg'}],
 'prices':{'price':'1000','currency_code':'PKR','currency_minor_unit':2},**extra}
def product(raw):return normalize(capture(raw,URL+'/api','woocommerce_api'),Platform.WOOCOMMERCE,URL)

def issue(raw,code):return any(d['code']==code for d in raw.get('_adapter_diagnostics',[]))

@pytest.mark.parametrize('brands,expected',[[[{'name':'Acme'}],'Acme'],[[],None],[[{'name':'Acme'},{'name':'Other'}],None]])
def test_woo_brand_source(brands,expected):
 p=product(parent(brands=brands));assert p.vendor==expected
 if expected:assert any(o.field_path=='/vendor' and o.state.value=='observed' for o in p.evidence_contract.observations)
 if len(brands)>1:assert issue(p.raw_data,'brand_conflict')

@pytest.mark.parametrize('key',['variants','variations'])
def test_woo_supplied_variants_alias_source(key):
 variants=[{'id':2,'name':'Blue','price':'0','in_stock':False,'attributes':{'Color':'Blue'}},
           {'id':3,'name':'Red','prices':{'price':'275','currency_minor_unit':2},'is_in_stock':True,'attributes':[{'name':'Color','value':'Red'}]}]
 p=product(parent(**{key:variants}));assert [v.variant_id for v in p.variants]==['2','3']
 assert [v.price for v in p.variants]==[Decimal('0'),Decimal('2.75')]
 assert [v.in_stock for v in p.variants]==[False,True]
 assert p.variants[1].attributes['Color']=='Red'
 assert any(o.field_path=='/variants/1/price' and o.state.value=='observed' for o in p.evidence_contract.observations)


def test_woo_duplicate_child_id_not_merged():
 p=product(parent(variants=[{'id':2,'price':'1'},{'id':2,'price':'2'}]))
 assert p.variants==[] and issue(p.raw_data,'duplicate_variant_id')

@pytest.mark.asyncio
@pytest.mark.parametrize('kind',['valid','wrong_id','wrong_parent','missing_stock','budget'])
async def test_woo_id_enrichment_bounded(kind):
 calls=[];ids=list(range(2,8)) if kind=='budget' else [2]
 def respond(r):
  calls.append(str(r.url))
  if r.url.path.endswith('/products'):return httpx.Response(200,json=[parent(variations=[{'id':i} for i in ids])])
  ident=int(r.url.path.rsplit('/',1)[-1]);detail={'id':99 if kind=='wrong_id' else ident,'parent_id':99 if kind=='wrong_parent' else 1,'name':'Blue','prices':{'price':'250','currency_minor_unit':2},'is_in_stock':False,'attributes':{'Color':'Blue'}}
  if kind=='missing_stock':detail.pop('is_in_stock')
  return httpx.Response(200,json=detail)
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
  result=await WooCommerceExtractor(http_client=client).extract(URL,enrich_variants=True)
 assert len(result.products)==1 and len(calls)<=6
 p=normalize(result.products[0],Platform.WOOCOMMERCE,URL)
 if kind in ('wrong_id','wrong_parent'):assert p.variants==[] and result.error
 else:
  assert len(p.variants)==(5 if kind=='budget' else 1) and p.variants[0].price==Decimal('2.50')
  if kind=='budget':assert result.complete is False and result.error
  stock=p.variants[0].in_stock
  assert stock is (None if kind=='missing_stock' else False)
  for field,expected in [('/variants/0/price','250'),('/variants/0/attributes/Color','Blue')]+([] if kind=='missing_stock' else [('/variants/0/in_stock',False)]):
   obs=next(o for o in p.evidence_contract.observations if o.field_path==field)
   assert obs.state.value=='observed'
   evidence=[e for e in p.evidence_contract.evidence if e.evidence_id in obs.evidence_ids]
   assert evidence and all(e.source_url==calls[1] for e in evidence)
   assert any(e.resolve_pointer()==expected for e in evidence)
  if kind=='missing_stock':assert all(o.state.value!='observed' for o in p.evidence_contract.observations if o.field_path=='/variants/0/in_stock')

@pytest.mark.asyncio
@pytest.mark.parametrize('kind',['429','variant_mismatch'])
async def test_shopify_missing_identifier_reason(kind):
 def respond(r):
  if r.url.path=='/products.json':return httpx.Response(200,json={'products':[{'id':1,'title':'Widget','handle':'widget','variants':[{'id':2,'price':'1'}]}]})
  if kind=='429':return httpx.Response(429)
  return httpx.Response(200,json={'product':{'id':1,'variants':[{'id':999,'barcode':'4006381333931'}]}})
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
  r=await ShopifyExtractor(http_client=client).extract(URL,max_products=1,enrich_identifiers=True)
 assert len(r.products)==1 and not r.products[0]['variants'][0].get('barcode')
 assert r.products[0].get('_identifier_enrichment_errors')


def mage(optional=False):
 value={'sku':'M1','name':'Magento','url_key':'m1','url_suffix':'.html','description':{'html':'Source'},'stock_status':'IN_STOCK','image':{'url':URL+'/i.jpg'},'price_range':{'minimum_price':{'final_price':{'value':10,'currency':'PKR'}}}}
 if optional:value.update(brand='Acme',gtin='4006381333931',media_gallery=[{'url':URL+'/i.jpg'},{'url':URL+'/gallery.jpg'}])
 return value

def body(item):return {'data':{'products':{'items':[item],'total_count':1,'page_info':{'current_page':1,'total_pages':1}}}}

@pytest.mark.asyncio
@pytest.mark.parametrize('kind',['supported','fallback'])
async def test_magento_optional_capability_core_retry(kind):
 queries=[]
 def respond(r):
  query=r.url.params['query'];queries.append(query)
  if kind=='fallback' and 'media_gallery' in query:return httpx.Response(200,json={'errors':[{'message':'Cannot query field brand'}]})
  return httpx.Response(200,json=body(mage(kind=='supported')))
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
  result=await MagentoGraphQLExtractor(http_client=client).extract(URL,max_products=1,capabilities=('media_gallery','brand','gtin'))
 assert len(result.products)==1 and len(queries)==(2 if kind=='fallback' else 1)
 if kind=='fallback':assert result.error and result.complete is False
 else:
  p=normalize(result.products[0],Platform.MAGENTO,URL)
  assert p.vendor=='Acme' and p.gtin=='4006381333931' and p.additional_images==[URL+'/gallery.jpg']

@pytest.mark.asyncio
async def test_magento_core_default_unchanged():
 queries=[]
 def respond(r):queries.append(r.url.params['query']);return httpx.Response(200,json=body(mage()))
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as c:r=await MagentoGraphQLExtractor(http_client=c).extract(URL,max_products=1)
 assert len(r.products)==1 and len(queries)==1 and 'media_gallery' not in queries[0]

@pytest.mark.asyncio
async def test_public_api_capability_forwarding(monkeypatch):
 import shopextract
 original=httpx.AsyncClient
 def factory(*a,**kw):kw['transport']=httpx.MockTransport(lambda r:httpx.Response(200,json=body(mage(True))));return original(*a,**kw)
 monkeypatch.setattr(httpx,'AsyncClient',factory)
 result=await shopextract.extract(URL,platform=Platform.MAGENTO,max_urls=1,api_options={'protocol':'graphql','capabilities':['media_gallery','brand','gtin']})
 assert result.products[0].vendor=='Acme'

@pytest.mark.asyncio
@pytest.mark.parametrize('kind',['magento','generic'])
async def test_detection_html_or_no_evidence(kind):
 from shopextract._detect import detect
 html='<script type="text/x-magento-init">{}</script><div data-mage-init="{}"></div>' if kind=='magento' else '<html>Home</html>'
 def respond(r):return httpx.Response(200,text=html) if r.url.path=='/' else httpx.Response(404)
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as c:r=await detect(URL+'/',client=c)
 assert r.platform==(Platform.MAGENTO if kind=='magento' else Platform.GENERIC)
 if kind=='generic':assert r.confidence==0


def test_cli_woo_enrichment_forwarding(monkeypatch):
 from click.testing import CliRunner
 from shopextract.cli import main
 original=httpx.AsyncClient
 def respond(r):return httpx.Response(200,json=[parent(variations=[{'id':2}])]) if r.url.path.endswith('/products') else httpx.Response(200,json={'id':2,'parent_id':1,'name':'Child','price':'2','is_in_stock':False})
 def factory(*a,**kw):kw['transport']=httpx.MockTransport(respond);return original(*a,**kw)
 monkeypatch.setattr(httpx,'AsyncClient',factory)
 r=CliRunner().invoke(main,['--output-format','json','extract',URL,'--platform','woocommerce','--max','1','--enrich-variants'])
 assert r.exit_code==3,r.output[:250]
 assert len(json.loads(r.stdout)['data']['products'][0]['product']['variants'])==1


def test_cli_magento_capability_forwarding(monkeypatch,tmp_path):
 from click.testing import CliRunner
 from shopextract.cli import main
 original=httpx.AsyncClient
 def factory(*a,**kw):kw['transport']=httpx.MockTransport(lambda r:httpx.Response(200,json=body(mage(True))));return original(*a,**kw)
 monkeypatch.setattr(httpx,'AsyncClient',factory)
 options=tmp_path/'api.json';options.write_text(json.dumps({'protocol':'graphql','capabilities':['media_gallery','brand','gtin']}))
 r=CliRunner().invoke(main,['--output-format','json','extract',URL,'--platform','magento','--max','1','--storefront',str(options)])
 assert r.exit_code==3,r.output[:250]
 assert json.loads(r.stdout)['data']['products'][0]['product']['vendor']=='Acme'

@pytest.mark.asyncio
async def test_woo_global_extra_detail_cap():
 calls=[];parents=[parent(id=n,variations=[{'id':n*100+i} for i in range(1,6)]) for n in range(1,6)]
 def respond(r):
  calls.append(str(r.url))
  if r.url.path.endswith('/products'):return httpx.Response(200,json=parents)
  ident=int(r.url.path.rsplit('/',1)[-1]);return httpx.Response(200,json={'id':ident,'parent_id':ident//100,'price':'2'})
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as c:r=await WooCommerceExtractor(http_client=c).extract(URL,enrich_variants=True)
 assert len(r.products)==5 and len(calls)==21 and not r.complete and r.error
 values=[normalize(raw,Platform.WOOCOMMERCE,URL) for raw in r.products]
 assert [len(p.variants) for p in values]==[5,5,5,5,0]

@pytest.mark.asyncio
@pytest.mark.parametrize('boundary',['extractor_capability','api_capability','api_platform'])
async def test_invalid_options_before_http(boundary,monkeypatch):
 import shopextract
 calls=[];original=httpx.AsyncClient
 def respond(r):calls.append(r);return httpx.Response(404)
 def factory(*a,**kw):kw['transport']=httpx.MockTransport(respond);return original(*a,**kw)
 monkeypatch.setattr(httpx,'AsyncClient',factory)
 with pytest.raises(ValueError):
  if boundary=='extractor_capability':
   async with httpx.AsyncClient() as c:await MagentoGraphQLExtractor(http_client=c).extract(URL,capabilities=('invented',))
  elif boundary=='api_capability':await shopextract.extract(URL,platform=Platform.MAGENTO,api_options={'capabilities':['invented']})
  else:await shopextract.extract(URL,platform=Platform.SHOPIFY,enrich_variants=True)
 assert calls==[]

def test_cli_unsupported_enrichment_before_http(monkeypatch):
 from click.testing import CliRunner
 from shopextract.cli import main
 calls=[];original=httpx.AsyncClient
 def respond(r):calls.append(r);return httpx.Response(404)
 def factory(*a,**kw):kw['transport']=httpx.MockTransport(respond);return original(*a,**kw)
 monkeypatch.setattr(httpx,'AsyncClient',factory)
 r=CliRunner().invoke(main,['extract',URL,'--platform','shopify','--enrich-variants'])
 assert r.exit_code==2 and 'only' in r.output.lower() and calls==[]

@pytest.mark.asyncio
async def test_magento_core_retry_also_errors():
 calls=[]
 def respond(r):
  calls.append(str(r.url));return httpx.Response(200,json={'errors':[{'message':'Cannot query field brand' if len(calls)==1 else 'Core failure'}]})
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as c:r=await MagentoGraphQLExtractor(http_client=c).extract(URL,capabilities=('brand',))
 assert len(calls)==2 and r.products==[] and r.error and not r.complete

@pytest.mark.asyncio
@pytest.mark.parametrize('kind',['list','null','parent_dict','parent_string','empty','bool','path','query','zero','negative'])
async def test_woo_malformed_detail_retains_base_without_route_escape(kind):
 values={'empty':'','bool':True,'path':'../../admin','query':'2?parent=99','zero':0,'negative':-2}
 variations={'id':2} if kind=='parent_dict' else '2' if kind=='parent_string' else [{'id':values.get(kind,2)}]
 calls=[]
 def respond(r):
  calls.append(str(r.url))
  if r.url.path.endswith('/products'):return httpx.Response(200,json=[parent(variations=variations)])
  return httpx.Response(200,content='null' if kind=='null' else '[]',headers={'content-type':'application/json'})
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as c:r=await WooCommerceExtractor(http_client=c).extract(URL,enrich_variants=True)
 assert len(r.products)==1 and not r.complete and r.error
 assert normalize(r.products[0],Platform.WOOCOMMERCE,URL).title=='Widget'
 assert normalize(r.products[0],Platform.WOOCOMMERCE,URL).variants==[]
 assert len(calls)==(2 if kind in ('list','null') else 1)


# Live m1.com.pk 2026-11-01: Store API names arrive WordPress-encoded ("&#8211;").
def test_woo_display_text_entities_decoded():
 raw=parent(name='Guitar &#8211; Black &amp; Gold',brands=[{'name':'Fender &amp; Co'}],categories=[{'name':'Strings &amp; Keys'}],
  tags=[{'name':'Sale &#038; New'}],description='<p>Rock &amp; roll</p>',variants=[{'id':2,'name':'Black &#8211; S','price':'1'}])
 p=product(raw)
 assert p.title=='Guitar – Black & Gold' and p.vendor=='Fender & Co'
 assert p.category_path==['Strings & Keys'] and p.tags==['Sale & New']
 assert p.description=='Rock & roll' and p.variants[0].title=='Black – S'
 assert any(o.field_path=='/title' and o.state.value=='observed' for o in p.evidence_contract.observations)
