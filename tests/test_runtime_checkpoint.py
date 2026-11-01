"""R3 real CLI accepted-buffer timeout; only HTTP is replaced."""
import asyncio,json
from decimal import Decimal
import httpx
import pytest
from click.testing import CliRunner
from shopextract.cli import main
from tests.test_adapter_coverage import URL,parent


def invoke_timeout(monkeypatch,*,before=False):
 original=httpx.AsyncClient;calls=[]
 expected=[parent(id=i+1,is_in_stock=False,permalink=URL+'/p/'+str(i+1)) for i in range(100)]
 async def respond(r):
  calls.append(r)
  if before or len(calls)>1:await asyncio.Event().wait()
  return httpx.Response(200,json=expected)
 def factory(*a,**kw):kw['transport']=httpx.MockTransport(respond);return original(*a,**kw)
 monkeypatch.setattr(httpx,'AsyncClient',factory)
 result=CliRunner().invoke(main,['--output-format','json','extract',URL,'--platform','woocommerce','--max','101','--timeout','0.05'])
 return result,expected,calls


def test_owned_cli_timeout_keeps_accepted_woo_batch(monkeypatch):
 from shopextract._portable import product_from_record
 result,expected,calls=invoke_timeout(monkeypatch)
 assert result.exit_code==3,result.output[:300]
 data=json.loads(result.stdout)['data'];assert data['product_count']==100 and data['catalog_complete'] is False
 assert 'operation_timeout' in data['incompleteness_reasons'] and len(calls)==2
 assert [{k:v for k,v in raw.items() if k!='_capture'} for raw in data['raw_products']]==expected
 products=[product_from_record(row) for row in data['products']]
 assert {p.external_id for p in products}=={str(i+1) for i in range(100)}
 assert [p.canonical_product_id for p in products]==sorted(p.canonical_product_id for p in products)
 assert all(p.price==Decimal('10') and p.currency=='PKR' and p.in_stock is False for p in products)
 assert all(any(o.field_path=='/price' and o.state.value=='observed' for o in p.evidence_contract.observations) for p in products)


def test_owned_cli_timeout_before_acceptance_is_timeout(monkeypatch):
 result,_,calls=invoke_timeout(monkeypatch,before=True)
 payload=json.loads(result.stdout)
 assert result.exit_code==1 and payload['error']['code']=='E_TIMEOUT' and payload['data'] is None and len(calls)==1


def test_checkpoint_not_reused_on_restart(monkeypatch):
 with monkeypatch.context() as m:first,_,_=invoke_timeout(m)
 with monkeypatch.context() as m:second,_,_=invoke_timeout(m,before=True)
 assert first.exit_code==3 and second.exit_code==1
 assert json.loads(second.stdout)['data'] is None


def test_owned_cli_html_probe_before_later_url_timeout(monkeypatch):
 # Warm installed parser imports outside this acceptance timing; import behavior
 # has independent fresh-process tests. No algorithm is replaced.
 import shopextract._discover
 original=httpx.AsyncClient;seen=[]
 a=URL+'/products/a';b=URL+'/products/b'
 async def respond(r):
  seen.append(str(r.url))
  if r.url.path=='/robots.txt':return httpx.Response(200,text='User-agent: *\nAllow: /')
  if 'sitemap' in r.url.path:return httpx.Response(200,text=f'<urlset><url><loc>{a}</loc></url><url><loc>{b}</loc></url></urlset>')
  if str(r.url)==a:
   product={'@type':'Product','name':'HTML accepted','sku':'HTML1','url':a,'image':URL+'/i.jpg','offers':{'price':'12.34','priceCurrency':'PKR'}}
   return httpx.Response(200,text='<script type="application/ld+json">'+json.dumps(product)+'</script>')
  if str(r.url)==b:await asyncio.Event().wait()
  return httpx.Response(404)
 def factory(*args,**kw):kw['transport']=httpx.MockTransport(respond);return original(*args,**kw)
 monkeypatch.setattr(httpx,'AsyncClient',factory)
 r=CliRunner().invoke(main,['--output-format','json','extract',URL,'--platform','magento','--max','2','--timeout','0.3'])
 assert r.exit_code==3,r.output[:300]
 data=json.loads(r.stdout)['data'];assert data['product_count']==1 and b in seen
 from shopextract._portable import product_from_record
 p=product_from_record(data['products'][0]);assert p.title=='HTML accepted' and p.price==Decimal('12.34') and p.sku=='HTML1'
 assert any(o.field_path=='/price' and o.state.value=='observed' for o in p.evidence_contract.observations)
 assert data['catalog_complete'] is False and 'operation_timeout' in data['incompleteness_reasons']
 from shopextract._scope import catalog_scope
 from shopextract._models import Platform
 assert data['tier']=='unified_crawl' and data['platform']=='magento'
 assert data['observation_scope']==catalog_scope(URL,Platform.MAGENTO)


def test_owned_shopify_timeout_preserves_captured_currency(monkeypatch):
 original=httpx.AsyncClient;calls=[]
 rows=[{'id':i+1,'title':'Shopify accepted','handle':'p'+str(i),'body_html':'Source description','images':[{'src':URL+'/i.jpg'}],'variants':[{'id':i+1,'price':'10','available':False}]} for i in range(250)]
 async def respond(r):
  calls.append(r)
  if len(calls)>1:await asyncio.Event().wait()
  return httpx.Response(200,json={'products':rows},headers={'Set-Cookie':'cart_currency=CAD; Path=/'})
 def factory(*a,**kw):kw['transport']=httpx.MockTransport(respond);return original(*a,**kw)
 monkeypatch.setattr(httpx,'AsyncClient',factory)
 r=CliRunner().invoke(main,['--output-format','json','extract',URL,'--platform','shopify','--max','251','--timeout','0.05'])
 assert r.exit_code==3,r.output[:300]
 from shopextract._portable import product_from_record
 products=[product_from_record(row) for row in json.loads(r.stdout)['data']['products']]
 assert len(products)==250 and all(p.currency=='CAD' and p.in_stock is False for p in products)
 assert all(any(o.field_path=='/currency' and o.state.value=='observed' for o in p.evidence_contract.observations) for p in products)

@pytest.mark.asyncio
async def test_external_cancel_propagates_with_active_checkpoint(monkeypatch):
 from shopextract._execution import execution_policy,ExecutionPolicy,ProgressCheckpoint,current_state
 from shopextract._models import Platform
 from shopextract import extract
 second=asyncio.Event();original=httpx.AsyncClient;clients=[];calls=[]
 async def respond(r):
  calls.append(r)
  if len(calls)>1:second.set();await asyncio.Event().wait()
  return httpx.Response(200,json=[parent(id=i+1) for i in range(100)])
 def factory(*a,**kw):
  kw['transport']=httpx.MockTransport(respond);client=original(*a,**kw);clients.append(client);return client
 monkeypatch.setattr(httpx,'AsyncClient',factory)
 with execution_policy(ExecutionPolicy(),2) as state:
  state.progress=ProgressCheckpoint()
  task=asyncio.create_task(extract(URL,platform=Platform.WOOCOMMERCE,max_urls=101))
  await asyncio.wait_for(second.wait(),1)
  task.cancel()
  with pytest.raises(asyncio.CancelledError):await task
 assert current_state() is None and clients and all(c.is_closed for c in clients)

@pytest.mark.parametrize('count',[1000,1001])
def test_checkpoint_product_retention_bound(count):
 from shopextract._execution import ProgressCheckpoint
 from shopextract._models import Product,Platform
 checkpoint=ProgressCheckpoint()
 products=[Product(title='Accepted',external_id=str(i),price=Decimal('10')) for i in range(count)]
 checkpoint.register_source(products,Platform.GENERIC,URL,normalized=True)
 result=checkpoint.snapshot()
 assert len(result.products)==1000 and result.catalog_complete is False
 assert ('checkpoint_budget_reached' in result.incompleteness_reasons) is (count>1000)

@pytest.mark.parametrize('delta',[-1,0])
@pytest.mark.parametrize('dimension',['bytes','nodes','depth'])
def test_checkpoint_reuses_codec_budget_boundaries(dimension,delta):
 from shopextract._execution import ProgressCheckpoint
 from shopextract._models import Product,Platform
 from shopextract._portable import product_to_record
 from shopextract.export._bundle import _json_bytes
 from shopextract._bounded_json import preflight_catalog_json
 product=Product(title='Accepted',external_id='P1',price=Decimal('10'))
 payload=_json_bytes(product_to_record(product));shape=preflight_catalog_json(payload)
 count=2 if dimension=='nodes' else 1
 value=len(payload) if dimension=='bytes' else shape.nodes*2 if dimension=='nodes' else shape.depth
 checkpoint=ProgressCheckpoint(**{'max_'+dimension:value+delta})
 checkpoint.register_source([product]*count,Platform.GENERIC,URL,normalized=True)
 result=checkpoint.snapshot()
 assert (len(result.products) if result else 0)==(count if delta==0 else count-1)
 if result and delta<0:assert 'checkpoint_budget_reached' in result.incompleteness_reasons

@pytest.mark.parametrize('restore',[False,True])
def test_timeout_restore_short_gtin_matches_normal_completion(monkeypatch,restore):
 original=httpx.AsyncClient;phase={'blocked':False,'calls':0}
 rows=[{'id':i+1,'title':'Restore control','handle':'p'+str(i),'body_html':'Source description','images':[{'src':URL+'/i.jpg'}],'variants':[{'id':i+1,'price':'10','barcode':'29877030712','available':False}]} for i in range(250)]
 async def respond(r):
  phase['calls']+=1
  if phase['calls']>1:
   if phase['blocked']:await asyncio.Event().wait()
   return httpx.Response(200,json={'products':[]})
  return httpx.Response(200,json={'products':rows},headers={'Set-Cookie':'cart_currency=USD; Path=/'})
 def factory(*a,**kw):kw['transport']=httpx.MockTransport(respond);return original(*a,**kw)
 monkeypatch.setattr(httpx,'AsyncClient',factory)
 args=['--output-format','json','extract',URL,'--platform','shopify','--max','251','--shop-url','https://supplier.fixture.invalid/catalog']+(['--restore-short-gtin'] if restore else [])
 control=CliRunner().invoke(main,args+['--timeout','10'])
 assert control.exit_code in (0,3),control.output[:200]
 phase.update(blocked=True,calls=0)
 recovered=CliRunner().invoke(main,args+['--timeout','0.05'])
 assert recovered.exit_code==3,recovered.output[:200]
 from shopextract._portable import product_from_record
 before=[product_from_record(p) for p in json.loads(control.stdout)['data']['products']]
 after=[product_from_record(p) for p in json.loads(recovered.stdout)['data']['products']]
 assert len(before)==len(after)==250
 assert [(p.supplier_id,p.product_url) for p in before]==[(p.supplier_id,p.product_url) for p in after]
 assert json.loads(control.stdout)['data']['observation_scope']==json.loads(recovered.stdout)['data']['observation_scope']
 assert [p.gtin for p in before]==[p.gtin for p in after]==(['0029877030712']*250 if restore else [None]*250)
 if restore:
  for p in after:
   obs=next(o for o in p.evidence_contract.observations if o.field_path=='/gtin')
   assert obs.state.value=='observed' and obs.raw_value=='29877030712' and 'restore_upc_leading_zero' in obs.transformations


def test_snapshot_result_metadata_independent_of_source_platform():
 from shopextract._execution import ProgressCheckpoint
 from shopextract._models import Platform,Product,ExtractionTier
 from shopextract._scope import catalog_scope
 checkpoint=ProgressCheckpoint();scope=catalog_scope(URL,Platform.MAGENTO)
 checkpoint.configure_result(Platform.MAGENTO,scope)
 checkpoint.register_source([Product(title='HTML source',platform=Platform.GENERIC)],Platform.GENERIC,URL,normalized=True,tier=ExtractionTier.UNIFIED_CRAWL)
 result=checkpoint.snapshot()
 assert result.platform==Platform.MAGENTO and result.observation_scope==scope and result.tier==ExtractionTier.UNIFIED_CRAWL
 assert result.products[0].platform==Platform.GENERIC

from tests.test_truthful_outcomes import crawl_boundary,crawl_result

@pytest.mark.asyncio
@pytest.mark.parametrize('status',[200,404])
async def test_accepted_browser_view_and_admission_checkpoint(crawl_boundary,status):
 from shopextract._execution import execution_policy,ExecutionPolicy,ProgressCheckpoint
 from shopextract._models import Platform
 from shopextract._scope import catalog_scope
 from shopextract.extractors.unified import UnifiedCrawlExtractor
 browser={'@type':'Product','name':'Browser accepted','sku':'SAME','url':URL,'image':URL+'/i.jpg','offers':{'price':'20','priceCurrency':'USD'}}
 html={'@type':'Product','name':'HTTP partial','sku':'SAME','url':URL,'offers':{'price':'10','priceCurrency':'USD'}}
 r=crawl_result(status=status,html='<script type="application/ld+json">'+json.dumps(browser)+'</script>');r.url=URL;crawl_boundary.append(r)
 async with httpx.AsyncClient(transport=httpx.MockTransport(lambda req:httpx.Response(status,text='<script type="application/ld+json">'+json.dumps(html)+'</script>'))) as client:
  with execution_policy(ExecutionPolicy(browser=True),2) as state:
   state.progress=ProgressCheckpoint();state.progress.configure_result(Platform.GENERIC,catalog_scope(URL,Platform.GENERIC))
   await UnifiedCrawlExtractor(http_client=client).extract(URL)
   snapshot=state.progress.snapshot()
   if status==404:assert snapshot is None
   else:assert len(snapshot.products)==1 and snapshot.products[0].title=='Browser accepted' and snapshot.products[0].price==20
  assert state.progress is None
