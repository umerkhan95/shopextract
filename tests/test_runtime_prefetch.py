"""RuntimeR1b/R2 boundaries; actual imports/API/native transport paths."""
import asyncio,json,os,subprocess,sys
import httpx
import pytest
from shopextract.extractors.woocommerce import WooCommerceExtractor
from shopextract._execution import execution_policy,ExecutionPolicy
from tests.test_adapter_coverage import URL,parent

@pytest.mark.parametrize('module',['shopify','woocommerce','magento'])
def test_native_api_import_has_no_browser(module):
 code=f"import sys;__import__('shopextract.extractors.{module}');assert 'crawl4ai' not in sys.modules;assert 'playwright' not in sys.modules"
 r=subprocess.run([sys.executable,'-c',code],capture_output=True,text=True,timeout=15)
 assert r.returncode==0,r.stderr[-500:]


def test_browser_http_exports_are_same_objects():
 from shopextract.extractors import _browser,_http_defaults
 assert _browser.DEFAULT_HEADERS is _http_defaults.DEFAULT_HEADERS
 assert _browser.get_default_user_agent is _http_defaults.get_default_user_agent
 assert _browser.HTTPX_USER_AGENT==_http_defaults.HTTPX_USER_AGENT

@pytest.mark.asyncio
@pytest.mark.parametrize('maximum',[1,99,100,101])
async def test_woo_bound_before_fetch(maximum):
 calls=[]
 def respond(r):
  size=int(r.url.params['per_page']);page=int(r.url.params['page']);offset=int(r.url.params.get('offset',(page-1)*size));calls.append((size,page,offset))
  dataset=[parent(id=i) for i in range(1,maximum+2)]
  if (r.url.params.get('orderby'),r.url.params.get('order'))!=('id','asc'):dataset.reverse()
  return httpx.Response(200,json=dataset[offset:offset+size])
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as c:r=await WooCommerceExtractor(http_client=c).extract(URL,max_products=maximum)
 assert len(r.products)==maximum and calls==([(maximum,1,0)] if maximum<=100 else [(100,1,0),(1,1,100)])
 assert [p['id'] for p in r.products]==list(range(1,maximum+1))
 assert len({p['id'] for p in r.products})==maximum
 assert not r.complete and r.completeness_reason=='product_budget_reached'
 # A caller's budget is a bound, not a source failure.
 assert r.error is None

@pytest.mark.asyncio
@pytest.mark.parametrize('kind',['total','short'])
async def test_woo_known_exhaustion(kind):
 calls=[]
 def respond(r):calls.append(r);return httpx.Response(200,json=[parent()],headers={'X-WP-Total':'1'} if kind=='total' else {})
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as c:r=await WooCommerceExtractor(http_client=c).extract(URL,max_products=1 if kind=='total' else 2)
 assert len(r.products)==1 and r.complete and len(calls)==1

@pytest.mark.asyncio
async def test_woo_page2_failure_keeps_first_batch():
 calls=[]
 def respond(r):
  calls.append(r)
  return httpx.Response(200,json=[parent(id=i) for i in range(100)]) if len(calls)==1 else httpx.Response(500)
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as c:r=await WooCommerceExtractor(http_client=c).extract(URL,max_products=101)
 assert len(r.products)==100 and not r.complete and '500' in r.error and len(calls)==2

@pytest.mark.asyncio
@pytest.mark.parametrize('header,retries',[('60',0),('bad',0),('-3',0),('Wed, 21 Oct 2099 07:28:00 GMT',0),('0',1),('Wed, 21 Oct 2015 07:28:00 GMT',1)])
async def test_retry_respects_remaining_deadline(header,retries):
 calls=[]
 def respond(r):
  calls.append(r)
  return httpx.Response(429,headers={'Retry-After':header}) if len(calls)==1 else httpx.Response(200,json=[parent()])
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as c:
  with execution_policy(ExecutionPolicy(),.05):r=await asyncio.wait_for(WooCommerceExtractor(http_client=c).extract(URL,max_products=1),.2)
 assert len(calls)==1+retries and len(r.products)==retries
 if not retries:assert not r.complete and r.error

@pytest.mark.asyncio
@pytest.mark.parametrize('maximum',[0,-1,True,1.5])
async def test_invalid_woo_bound_before_http(maximum):
 calls=[]
 def respond(r):calls.append(r);return httpx.Response(404)
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as c:
  with pytest.raises(ValueError):await WooCommerceExtractor(http_client=c).extract(URL,max_products=maximum)
 assert calls==[]

@pytest.mark.asyncio
async def test_public_api_woo_prefetch_bound(monkeypatch):
 import shopextract
 from shopextract._models import Platform
 calls=[];original=httpx.AsyncClient
 def respond(r):calls.append(r);return httpx.Response(200,json=[parent(id=i) for i in range(100)])
 def factory(*a,**kw):kw['transport']=httpx.MockTransport(respond);return original(*a,**kw)
 monkeypatch.setattr(httpx,'AsyncClient',factory)
 result=await shopextract.extract(URL,platform=Platform.WOOCOMMERCE,max_urls=1)
 assert len(result.products)==1 and len(calls)==1 and calls[0].url.params['per_page']=='1'

@pytest.mark.asyncio
async def test_native_tool_woo_prefetch_bound():
 from shopextract.tools import ToolConfig,ToolRuntime
 from tests.tool_api_fixtures import ORIGIN,resolver
 from tests.test_agent_tool_api import completed
 calls=[]
 def respond(r):
  if r.url.path=='/':return httpx.Response(200,text='<meta name="generator" content="wordpress">')
  if r.url.path.endswith('/products'):
   calls.append(r);return httpx.Response(200,json=[parent(id=i) for i in range(100)])
  return httpx.Response(404)
 engine=ToolRuntime(ToolConfig(allowed_origins=(ORIGIN,)),resolver=resolver,wire_transport=httpx.MockTransport(respond))
 try:
  jid=await completed(engine.call,'extract',{'url':ORIGIN,'max_items':1})
  result=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'products'})
  assert result['ok'] and len(result['data']['items'])==1
  assert len(calls)==1 and calls[0].url.params['per_page']=='1'
 finally:await engine.aclose()

@pytest.mark.asyncio
async def test_shopify_retry_uses_remaining_deadline():
 from shopextract.extractors.shopify import ShopifyExtractor
 calls=[]
 def respond(r):calls.append(r);return httpx.Response(429,headers={'Retry-After':'60'})
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as c:
  with execution_policy(ExecutionPolicy(),.05):r=await asyncio.wait_for(ShopifyExtractor(http_client=c).extract(URL,max_products=1),.2)
 assert calls and len(calls)==1 and r.products==[] and not r.complete and r.error
