"""One bounded real-native MCP/data audit. Trusted observers preserve original I/O."""
import asyncio,json,sys,time,hashlib,os
from pathlib import Path
from decimal import Decimal
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT/'src'))
OUT=Path(__file__).resolve().parent;ORIGIN='https://www.blissworld.com'
def save(name,value):(OUT/name).write_text(json.dumps(value,indent=2)+'\n')
def receipt():return json.loads((OUT/'receipt.json').read_text())

if '--server' in sys.argv:
 sys.argv.remove('--server')
 from shopextract.tools.security import GuardedTransport
 from shopextract.tools.contracts import ToolError
 from shopextract.tools.domain import DomainAdapter
 raw=GuardedTransport.raw;handle=GuardedTransport.handle_async_request;domain=DomainAdapter.execute
 async def counted(self,request):
  r=receipt()
  if time.monotonic()-r['start_monotonic']>=115 or r['request_count']>=16:raise ToolError('resource_limit','Live audit budget')
  r['request_count']+=1;r['requests'].append({'number':r['request_count'],'method':request.method,'url':str(request.url),'elapsed':time.monotonic()-r['start_monotonic']});save('receipt.json',r)
  return await raw(self,request)
 async def captured(self,request):
  response=await handle(self,request)  # Original pinning, encoding and byte checks first.
  r=receipt();n=len(r['responses'])+1;body=response.content;file=f'http-{n:02}.body';(OUT/file).write_bytes(body)
  r['responses'].append({'file':file,'url':str(response.request.url),'status':response.status_code,'bytes':len(body),'sha256':hashlib.sha256(body).hexdigest(),'content_type':response.headers.get('content-type'),'cart_currency':response.cookies.get('cart_currency')});save('receipt.json',r)
  if response.status_code>=400:raise ToolError('source_error','Live source HTTP failure')
  return response
 async def recorded(self,name,args,ctx):
  graph=await domain(self,name,args,ctx)
  if name=='extract':
   n=len(list(OUT.glob('portable-*.json')))+1;save(f'portable-{n}.json',graph.products)
  return graph
 GuardedTransport.raw=counted;GuardedTransport.handle_async_request=captured;DomainAdapter.execute=recorded
 from shopextract.tools.__main__ import main
 raise SystemExit(main())

async def flow(result):
 from mcp import ClientSession,StdioServerParameters
 from mcp.client.stdio import stdio_client
 import psutil
 from contextlib import asynccontextmanager
 me=psutil.Process();stop=asyncio.Event()
 async def watch():
  while not stop.is_set():
   total=1+len(me.children(recursive=True));result['peak_process_count']=max(result['peak_process_count'],total)
   if total>5:raise RuntimeError('Process limit exceeded')
   await asyncio.sleep(.02)
 watcher=asyncio.create_task(watch())
 caps={k:'2' for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS','VECLIB_MAXIMUM_THREADS']};caps.update(TOKENIZERS_PARALLELISM='false',PYTHONPATH=str(ROOT/'src'))
 @asynccontextmanager
 async def session(config):
  parameters=StdioServerParameters(command=sys.executable,args=[str(Path(__file__).resolve()),'--server','--config',str(config)],env=caps,cwd=str(ROOT))
  async with stdio_client(parameters) as (read,write):
   async with ClientSession(read,write) as client:
    await client.initialize();yield client
 async def call(client,name,expected_error=None,**args):
  if watcher.done():await watcher
  reply=await client.call_tool(name,{'schema_version':'1.0',**args});value=reply.structuredContent or json.loads(reply.content[0].text)
  if expected_error:
   assert not value['ok'] and value['error']['code']==expected_error,(name,value)
  else:assert value['ok'],(name,value)
  result['tools'].append(name);return value
 async def job(client,name,**args):
  value=await call(client,name,**args);jid=value['data']['job_id']
  while True:
   status=(await call(client,'job_status',job_id=jid))['data']
   if status['state']=='succeeded':return jid
   if status['state'] in {'failed','cancelled','timed_out'}:raise RuntimeError(json.dumps({'tool':name,'status':status}))
   await asyncio.sleep(.1)
 def source_records():
  for response in reversed(receipt()['responses']):
   if '/products.json?' in response['url']:
    return response,json.loads((OUT/response['file']).read_text())['products']
  raise AssertionError('No saved native source JSON')
 def verify(records):
  source,actual=source_records();byid={str(v['id']):v for v in actual};checks=[]
  assert len(records)==2
  for item in records:
   raw=byid[item['external_id']];first=raw['variants'][0]
   assert item['title']==raw['title'].strip()
   assert Decimal(item['price'])==Decimal(first['price'])
   assert item['sku']==first.get('sku')
   assert item['product_url']==ORIGIN+'/products/'+raw['handle']
   assert len(item['variants'])<=2 and len(raw['variants'])<=2
   for variant,original in zip(item['variants'],raw['variants']):
    assert variant['variant_id']==str(original['id']) and variant['sku']==original.get('sku')
    assert Decimal(variant['price'])==Decimal(original['price'])
   if not first.get('barcode'):assert item['gtin'] is None and item['support']['/gtin']['state']!='observed'
   checks.append({'title':item['title'],'external_id':item['external_id'],'price':item['price'],'sku':item['sku'],'product_url':item['product_url'],'variant_ids':[v['variant_id'] for v in item['variants']],'gtin':item['gtin'],'gtin_support':item['support']['/gtin'],'source_file':source['file'],'source_url':source['url']})
  return source,byid,checks
 try:
  async with session(OUT/'config.json') as client:
   jid=await job(client,'discover',url=ORIGIN,max_items=1)
   page=(await call(client,'job_result',job_id=jid,collection='urls',page_size=1))['data'];source=page['items'][0];result['discovered_source']=source
   catalogs=[];samples=[]
   for number in (1,2):
    jid=await job(client,'extract',url=source,max_items=2)
    page=(await call(client,'job_result',job_id=jid,collection='products',page_size=1))['data'];records=page['items'];cursor=page['next_cursor']
    assert cursor
    second=(await call(client,'job_result',job_id=jid,collection='products',page_size=1,cursor=cursor))['data'];records+=second['items'];assert not second['next_cursor']
    saved_source,actual,checks=verify(records);catalogs.append(page['metadata']['catalog_handle']);samples.append(records);result['samples'].append(checks)
    save(f'extract-{number}-response.json',records)
    if number==1:save('first-extract-smoke.json',{'outcome':'passed','elapsed':time.monotonic()-receipt()['start_monotonic'],'fields_verified':checks,'request_count':receipt()['request_count']})
   jid=await job(client,'match',left_catalog=catalogs[0],right_catalog=catalogs[1]);matches=(await call(client,'job_result',job_id=jid,collection='matches',page_size=20))['data'];assert matches['items'];result['matches']=matches['items']
   item=samples[-1][0];eid=item['field_evidence']['/price'][0]
   evidence=(await call(client,'evidence',owner=item['owner_handle'],evidence_id=eid))['data'];proof=evidence['evidence'];saved_source,actual=source_records();raw=next(v for v in actual if str(v['id'])==item['external_id'])
   assert proof['pointer']=='/value' and proof['retained_data']['source_pointer']=='/variants/0/price'
   assert proof['retained_data']['value']==raw['variants'][0]['price'] and proof['source_url']==saved_source['url']
   result['evidence']=evidence
   await call(client,'evidence',expected_error='not_found',owner=samples[-1][1]['owner_handle'],evidence_id=eid)
   bad=await client.call_tool('discover',{'schema_version':'9.0','url':ORIGIN});bad=bad.structuredContent or json.loads(bad.content[0].text);assert bad['error']['code']=='unsupported_version';result['version_error']=bad
  # Operator writes only two actually extracted portable graphs, without changing facts.
  from shopextract._portable import product_from_record
  from shopextract.monitor.evidence import save_snapshot
  db=OUT/'actual-captures.db';ids=[]
  for number in (1,2):
   records=json.loads((OUT/f'portable-{number}.json').read_text());ids.append(save_snapshot([product_from_record(v) for v in records],'www.blissworld.com',db_path=str(db),metadata={'observation_scope':'live:bounded-first-two','catalog_complete':False,'incompleteness_reasons':['product_cap']}))
  config=json.loads((OUT/'config.json').read_text());config['captures']=[{'alias':str(i),'db_path':str(db),'snapshot_id':sid,'supplier':'www.blissworld.com'} for i,sid in enumerate(ids)];save('captures-config.json',config)
  async with session(OUT/'captures-config.json') as client:
   grants=json.loads((await client.read_resource('shopextract://session')).contents[0].text)['captures'];jid=await job(client,'changes',previous_capture=grants[0]['capture_handle'],current_capture=grants[1]['capture_handle'])
   result['changes']=(await call(client,'job_result',job_id=jid,collection='events',page_size=20))['data'];result['changes_interpretation']='Two bounded real captures; no manufactured commercial transition; incomplete catalog cannot confirm removals'
  result['outcome']='passed'
 finally:
  stop.set();watcher.cancel()
  try:await watcher
  except asyncio.CancelledError:pass

if __name__=='__main__':
 start=time.monotonic();save('receipt.json',{'start_monotonic':start,'start_utc':__import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat(),'total_limit_seconds':120,'request_limit':16,'request_count':0,'requests':[],'responses':[]})
 save('config.json',{'allowed_origins':[ORIGIN],'limits':{'requests':16,'timeout_seconds':30,'item_count':2}})
 result={'outcome':'not_finished','tools':[],'samples':[],'peak_process_count':1,'key_read':False}
 try:asyncio.run(asyncio.wait_for(flow(result),timeout=115))
 except BaseException as error:result.update(outcome='failed',exception=type(error).__name__,message=str(error)[:2000])
 result['execution_seconds']=time.monotonic()-start;result['request_count']=receipt()['request_count'];save('result.json',result);print(json.dumps({k:v for k,v in result.items() if k not in {'tools','samples','evidence','matches','changes'}}))
