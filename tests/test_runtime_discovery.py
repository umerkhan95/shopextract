"""R4/R5 real worker lifecycle and real guarded HTTP mechanisms; no live stores."""
import asyncio
from contextlib import contextmanager
import json
import os
from pathlib import Path
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import httpx
import pytest

ROOT='https://catalog.example'

def xml(*paths):
 return '<urlset>'+''.join('<url><loc>'+ROOT+p+'</loc></url>' for p in paths)+'</urlset>'

async def local(routes,*,maximum=100,budget=16,cap=10*1024*1024):
 from shopextract._discovery_runtime import DiscoveryClient
 from shopextract._discover import _discover_local
 from shopextract._models import Platform
 sent=[]
 def respond(r):
  sent.append(str(r.url));value=routes.get(r.url.path,(404,''))
  return httpx.Response(value[0],text=value[1],headers=value[2] if len(value)>2 else {})
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as c:
  guard=DiscoveryClient(c,max_requests=budget,response_bytes=cap)
  result=await _discover_local(ROOT,platform=Platform.GENERIC,max_urls=maximum,timeout=2,client=guard)
 return result,sent

@contextmanager
def server():
 sent=[]
 class Handler(BaseHTTPRequestHandler):
  def do_GET(self):
   sent.append(self.path); origin='http://127.0.0.1:'+str(self.server.server_port)
   body={'/robots.txt':'User-agent: *\nDisallow: /private', '/sitemap.xml':'<sitemapindex><sitemap><loc>'+origin+'/nested.xml</loc></sitemap></sitemapindex>', '/nested.xml':'<sitemapindex><sitemap><loc>'+origin+'/nested.xml</loc></sitemap><sitemap><loc>'+origin+'/leaf.xml</loc></sitemap></sitemapindex>', '/leaf.xml':'<urlset><url><loc>'+origin+'/products/z</loc></url><url><loc>'+origin+'/products/a</loc></url><url><loc>'+origin+'/private</loc></url></urlset>'}.get(self.path,'')
   self.send_response(200 if body else 404);self.end_headers();self.wfile.write(body.encode())
  def log_message(self,*a):pass
 httpd=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=httpd.serve_forever,daemon=True);thread.start()
 try:yield 'http://127.0.0.1:'+str(httpd.server_port),sent
 finally:httpd.shutdown();httpd.server_close();thread.join(2)

def cleanup_owned(*files):
 for file in files:
  if file.exists():
   try:os.kill(int(file.read_text()),9)
   except ProcessLookupError:pass

def descendant_program(pid,child):
 return "import os,time,pathlib,subprocess,signal,sys\n"+"child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(60)'])\n"+"pathlib.Path("+repr(str(child))+ ").write_text(str(child.pid))\n"+"def stop(*args):\n child.wait(timeout=1.5)\n sys.exit(0)\nsignal.signal(signal.SIGTERM,stop)\n"+"pathlib.Path("+repr(str(pid))+").write_text(str(os.getpid()))\ntime.sleep(60)"

@pytest.mark.asyncio
async def test_owned_worker_timeout_reaped(tmp_path):
 from shopextract._discovery_runtime import run_discovery_worker
 pid=tmp_path/'pid';child=tmp_path/'child';code=descendant_program(pid,child)
 try:
  result=await run_discovery_worker({'url':ROOT,'timeout':1},command=[sys.executable,'-c',code])
  assert 'discovery_timeout' in result.reasons and pid.exists() and child.exists()
  for file in (pid,child):
   with pytest.raises(ProcessLookupError):os.kill(int(file.read_text()),0)
 finally:cleanup_owned(pid,child)

@pytest.mark.asyncio
async def test_owned_worker_cancel_reaped(tmp_path):
 from shopextract._discovery_runtime import run_discovery_worker
 pid=tmp_path/'pid';child=tmp_path/'child';code=descendant_program(pid,child)
 task=asyncio.create_task(run_discovery_worker({'url':ROOT,'timeout':5},command=[sys.executable,'-c',code]))
 try:
  for _ in range(100):
   if pid.exists():break
   await asyncio.sleep(.01)
  assert pid.exists();task.cancel()
  with pytest.raises(asyncio.CancelledError):await task
  for file in (pid,child):
   assert file.exists()
   with pytest.raises(ProcessLookupError):os.kill(int(file.read_text()),0)
 finally:
  if not task.done():
   task.cancel()
   try:await task
   except asyncio.CancelledError:pass
  cleanup_owned(pid,child)

@pytest.mark.asyncio
async def test_real_worker_loopback_sorted():
 from shopextract import discover,Platform
 with server() as (origin,sent):
  result=await discover(origin,platform=Platform.GENERIC,timeout=6)
 assert list(result)==[origin+'/products/a',origin+'/products/z']
 assert sent.count('/nested.xml')==1 and sent.count('/leaf.xml')==1
 assert sent.count('/robots.txt')==1 and len(sent)<=16 and '/private' not in sent
 assert 'discovery_coverage_unverified' in result.reasons

@pytest.mark.asyncio
async def test_robots_disallow_before_fetch_and_emit():
 r,s=await local({'/robots.txt':(200,'User-agent: ShopExtract\nDisallow: /private\nDisallow: /sitemap.xml'),'/sitemap.xml':(200,xml('/private'))})
 assert not r and all('/sitemap' not in u for u in s) and 'robots_disallowed' in r.reasons

@pytest.mark.asyncio
async def test_robots_unavailable_fails_closed():
 r,s=await local({'/robots.txt':(503,'')});assert not r and len(s)==1 and 'robots_unavailable' in r.reasons

@pytest.mark.asyncio
@pytest.mark.parametrize('status',[401,403])
async def test_robots_forbidden_fails_closed_as_unavailable(status):
 # Live czone 2026-11-01: a bot challenge answered robots.txt; no rule disallowed anything.
 r,s=await local({'/robots.txt':(status,'challenge')})
 assert not r and len(s)==1 and 'robots_unavailable' in r.reasons and 'robots_disallowed' not in r.reasons

@pytest.mark.asyncio
async def test_concurrent_requests_wait_for_single_robots_read():
 # Live Naheed 2026-11-01: parallel platform probes saw the fail-closed placeholder and were denied.
 from shopextract._discovery_runtime import DiscoveryClient
 sent=[]
 async def respond(r):
  sent.append(r.url.path)
  if r.url.path=='/robots.txt':
   await asyncio.sleep(0.05);return httpx.Response(200,text='User-agent: *\nDisallow: /private')
  return httpx.Response(200,text='ok')
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as c:
  guard=DiscoveryClient(c,max_requests=16)
  results=await asyncio.gather(*(guard.allowed(ROOT+p) for p in ('/a','/b','/c','/private')))
 assert results==[True,True,True,False] and sent.count('/robots.txt')==1
 assert 'robots_unavailable' not in guard.reasons and 'robots_disallowed' in guard.reasons

@pytest.mark.asyncio
async def test_robots_missing_allows():
 r,s=await local({'/sitemap.xml':(200,xml('/products/b','/products/a','/products/a'))})
 assert r==[ROOT+'/products/a',ROOT+'/products/b'] and s.count(ROOT+'/robots.txt')==1

@pytest.mark.asyncio
async def test_redirect_disallowed_not_sent():
 r,s=await local({'/robots.txt':(200,'User-agent: *\nDisallow: /secret'),'/sitemap.xml':(302,'',{'Location':'/secret'})})
 assert not r and ROOT+'/secret' not in s and 'robots_disallowed' in r.reasons

@pytest.mark.asyncio
async def test_cross_origin_redirect_not_sent():
 r,s=await local({'/sitemap.xml':(302,'',{'Location':'https://elsewhere.example/map.xml'})})
 assert not r and all('elsewhere' not in u for u in s) and 'discovery_origin_denied' in r.reasons

@pytest.mark.asyncio
async def test_request_budget_counts_robots_redirect():
 r,s=await local({'/sitemap.xml':(302,'',{'Location':'/nested.xml'}),'/nested.xml':(200,xml('/products/a'))},budget=2)
 assert not r and len(s)==2 and 'discovery_request_budget' in r.reasons

@pytest.mark.asyncio
async def test_streamed_body_cap_stops_consumption():
 from shopextract._discovery_runtime import DiscoveryClient
 class Stream(httpx.AsyncByteStream):
  def __init__(self):self.reads=0
  async def __aiter__(self):
   for _ in range(100):self.reads+=1;yield b'x'*64
 stream=Stream()
 def respond(r):return httpx.Response(404) if r.url.path=='/robots.txt' else httpx.Response(200,stream=stream)
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as c:
  g=DiscoveryClient(c,response_bytes=128)
  with pytest.raises(httpx.HTTPError):await g.get(ROOT+'/sitemap.xml')
 assert stream.reads<=3 and 'discovery_response_budget' in g.reasons

def test_worker_entry_redirects_library_noise(monkeypatch,capsys):
 from shopextract import _discovery_worker as worker
 from shopextract._discovery_runtime import DiscoveryURLs
 async def noisy(*a,**kw):print('LIBRARY PROGRESS');return DiscoveryURLs([ROOT+'/products/a'])
 import shopextract._discover as module
 monkeypatch.setattr(module,'_discover_local',noisy)
 monkeypatch.setattr(sys,'stdin',__import__('io').StringIO(json.dumps({'url':ROOT,'platform':'generic','timeout':2})))
 worker.main();out=capsys.readouterr()
 assert json.loads(out.out)['urls']==[ROOT+'/products/a'] and 'LIBRARY PROGRESS' in out.err and 'LIBRARY' not in out.out

@pytest.mark.asyncio
async def test_worker_bad_protocol_bounded(tmp_path):
 from shopextract._discovery_runtime import run_discovery_worker
 for stream,size in (('stdout',4*1024*1024+1),('stderr',64*1024+1)):
  pid=tmp_path/stream
  code="import os,pathlib,sys,time;pathlib.Path("+repr(str(pid))+").write_text(str(os.getpid()));sys."+stream+".write('x'*"+str(size)+");sys."+stream+".flush();time.sleep(60)"
  started=time.monotonic()
  try:
   r=await run_discovery_worker({'url':ROOT,'timeout':2},command=[sys.executable,'-c',code])
   assert not r and 'discovery_worker_protocol' in r.reasons
   assert time.monotonic()-started<1.8 and pid.exists()
   with pytest.raises(ProcessLookupError):os.kill(int(pid.read_text()),0)
  finally:cleanup_owned(pid)
 r=await run_discovery_worker({'url':ROOT,'timeout':2},command=[sys.executable,'-c',"print('not json')"])
 assert not r and 'discovery_worker_protocol' in r.reasons


def test_serialized_products_stable_across_source_order():
 from shopextract import Product,Platform,ExtractionResult,ExtractionTier
 from shopextract._cli_data import extraction_data
 a=Product(external_id='a',canonical_product_id='a',title='A',product_url=ROOT+'/z');b=Product(external_id='b',canonical_product_id='b',title='B',product_url=ROOT+'/a')
 def result(rows):return ExtractionResult(products=rows,platform=Platform.GENERIC,tier=ExtractionTier.API)
 original=result([b,a]);left=extraction_data(original);right=extraction_data(result([a,b]))
 from shopextract._portable import product_from_record
 assert [product_from_record(r).canonical_product_id for r in left['products']]==['a','b']
 assert left['products']==right['products'] and original.products==[b,a] and original.products[0] is b


def test_cli_and_guarded_tool_discovery_policy(monkeypatch):
 from click.testing import CliRunner
 from shopextract.cli import main
 with server() as (origin,sent):
  r=CliRunner().invoke(main,['--output-format','json','discover',origin,'--platform','generic','--timeout','6'])
 assert r.exit_code==3,r.output
 payload=json.loads(r.stdout);assert payload['data']['urls']==[origin+'/products/a',origin+'/products/z']
 async def tool():
  from shopextract.tools import ToolRuntime,ToolConfig
  from tests.tool_api_fixtures import ORIGIN,resolver
  from tests.test_agent_tool_api import completed
  seen=[]
  def wire(request):
   seen.append(request.url.path)
   if request.url.path=='/robots.txt':return httpx.Response(200,text='User-agent: *\nDisallow: /private')
   return httpx.Response(200,text=xml('/private','/products/a').replace(ROOT,ORIGIN))
  engine=ToolRuntime(ToolConfig(allowed_origins=(ORIGIN,)),resolver=resolver,wire_transport=httpx.MockTransport(wire))
  try:
   jid=await completed(engine.call,'discover',{'url':ORIGIN,'max_items':10})
   result=await engine.call('job_result',{'schema_version':'1.0','job_id':jid,'collection':'urls'})
   assert result['ok'] and '/private' not in json.dumps(result['data']) and seen.count('/robots.txt')==1
  finally:await engine.aclose()
 asyncio.run(tool())

@pytest.mark.asyncio
async def test_borrowed_auto_redirect_client_cannot_bypass_robots():
 from shopextract import discover,Platform
 sent=[]
 def respond(r):
  sent.append(r.url.path)
  if r.url.path=='/robots.txt':return httpx.Response(200,text='User-agent: *\nDisallow: /secret')
  if r.url.path=='/sitemap.xml':return httpx.Response(302,headers={'Location':'/secret'})
  return httpx.Response(200,text=xml('/products/bypassed'))
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond),follow_redirects=True) as c:
  r=await discover(ROOT,platform=Platform.GENERIC,client=c,timeout=2)
 assert '/secret' not in sent and not r and 'robots_disallowed' in r.reasons


def test_duplicate_identity_order_uses_facts_not_timestamps():
 from datetime import datetime,timezone
 from shopextract import Product,ExtractionResult
 from shopextract._portable import product_from_record
 from shopextract._cli_data import extraction_data
 old=datetime(2020,1,1,tzinfo=timezone.utc);new=datetime(2026,1,1,tzinfo=timezone.utc)
 def order(reverse_time):
  a=Product(canonical_product_id='same',product_url=ROOT+'/same',title='Same',vendor='A',scraped_at=new if reverse_time else old)
  b=Product(canonical_product_id='same',product_url=ROOT+'/same',title='Same',vendor='B',scraped_at=old if reverse_time else new)
  original=ExtractionResult(products=[b,a])
  rows=extraction_data(original)['products'];assert original.products==[b,a]
  return [product_from_record(r).vendor for r in rows]
 assert order(False)==order(True)==['A','B']

def terminated(pid):
 # Under a Linux child subreaper (scripts/run_tests.py) a killed orphan stays a
 # zombie until the runner reaps it; signal 0 still succeeds on a zombie.
 try:os.kill(pid,0)
 except ProcessLookupError:return True
 try:
  with open(f'/proc/{pid}/stat') as stat:return stat.read().rsplit(')',1)[1].split()[0]=='Z'
 except FileNotFoundError:return os.path.isdir('/proc')
 except OSError:return False

@pytest.mark.asyncio
async def test_worker_kills_ignoring_descendant_after_leader_exit(tmp_path):
 from shopextract._discovery_runtime import run_discovery_worker
 pid=tmp_path/'leader';child=tmp_path/'ignoring'
 childcode="import signal,os,time,pathlib;signal.signal(signal.SIGTERM,signal.SIG_IGN);pathlib.Path("+repr(str(child))+").write_text(str(os.getpid()));time.sleep(60)"
 code="import subprocess,signal,sys,time,pathlib,os\nsubprocess.Popen([sys.executable,'-c',"+repr(childcode)+"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\nsignal.signal(signal.SIGTERM,lambda *a:sys.exit(0))\nwhile not pathlib.Path("+repr(str(child))+").exists():time.sleep(.01)\npathlib.Path("+repr(str(pid))+").write_text(str(os.getpid()))\ntime.sleep(60)"
 try:
  r=await run_discovery_worker({'url':ROOT,'timeout':1},command=[sys.executable,'-c',code])
  assert 'discovery_timeout' in r.reasons and pid.exists() and child.exists()
  for file in (pid,child):
   for _ in range(50):
    if terminated(int(file.read_text())):break
    await asyncio.sleep(.01)
   assert terminated(int(file.read_text()))
 finally:cleanup_owned(pid,child)


async def native_discovery_wire(handler,maximum=100):
 from shopextract.tools import ToolConfig
 from shopextract.tools.security import SourceGuard
 from shopextract.tools.sources import GuardedSources
 from tests.test_tool_mechanisms import context
 from tests.tool_api_fixtures import ORIGIN,resolver
 config=ToolConfig(allowed_origins=(ORIGIN,))
 source=GuardedSources(config,SourceGuard(config,resolver=resolver),httpx.MockTransport(handler))
 return await source.execute('discover',ORIGIN,maximum,context(timeout=3))

@pytest.mark.asyncio
async def test_native_tool_aggregate_location_boundary():
 from tests.tool_api_fixtures import ORIGIN
 for count,expected in ((4999,True),(5000,False)):
  sent=[]
  def wire(r):
   sent.append(r.url.path)
   if r.url.path=='/robots.txt':return httpx.Response(404)
   if r.url.path=='/sitemap.xml':return httpx.Response(200,text='<sitemapindex>'+('<sitemap><loc>'+ORIGIN+'/leaf.xml</loc></sitemap>')*count+'</sitemapindex>')
   return httpx.Response(200,text=xml('/products/a').replace(ROOT,ORIGIN))
  r=await native_discovery_wire(wire)
  assert r['urls']==([ORIGIN+'/products/a'] if expected else []) and sent.count('/leaf.xml')==1
  assert ('discovery_location_budget' in [d['code'] for d in r['diagnostics']]) is not expected

@pytest.mark.asyncio
async def test_native_tool_budget_retains_urls_and_reason():
 from tests.tool_api_fixtures import ORIGIN
 sent=[]
 def wire(r):
  sent.append(r.url.path)
  if r.url.path=='/robots.txt':return httpx.Response(404)
  if r.url.path=='/sitemap.xml':return httpx.Response(200,text='<sitemapindex>'+''.join('<sitemap><loc>'+ORIGIN+'/map'+str(i)+'.xml</loc></sitemap>' for i in range(15))+'</sitemapindex>')
  return httpx.Response(200,text=xml('/products/'+r.url.path.split('.')[0].strip('/')).replace(ROOT,ORIGIN))
 r=await native_discovery_wire(wire)
 assert len(r['urls'])==14 and len(sent)==16 and '/map14.xml' not in sent
 assert r['complete'] is False and 'discovery_request_budget' in [d['code'] for d in r['diagnostics']]
