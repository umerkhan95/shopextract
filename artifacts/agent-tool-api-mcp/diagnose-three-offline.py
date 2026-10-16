import asyncio,json,tempfile,time
from pathlib import Path
from collections import Counter
import httpx
from tests import tool_fixture_budget as budget
from tests.tool_fixture_budget import FixtureBytesPlugin
from tests.test_reliable_changes import product,save,DOMAIN
from tests.tool_api_fixtures import ORIGIN,resolver
from shopextract.tools.domain import synchronous
from shopextract.tools.contracts import encoded
from shopextract.tools.runtime import ToolRuntime,ToolConfig

async def main():
 start=time.monotonic();ledger=FixtureBytesPlugin();ledger.pytest_sessionstart(None);out={}
 try:
  with tempfile.TemporaryDirectory() as directory:
   db=str(Path(directory)/'changes.db');a=save(db,[product()],0);b=save(db,[product('11',tick=1)],1)
   try: encoded(synchronous({'operation':'changes','arguments':{'domain':DOMAIN,'db_path':db,'previous_snapshot_id':a,'current_snapshot_id':b}}))
   except Exception as error: out['M43']={'exception':type(error).__name__,'message':str(error)}
   budget.charge('generated_fixture_files',sum(p.stat().st_size for p in Path(directory).rglob('*') if p.is_file()))
  try:synchronous({'operation':'parse','mode':'xml','raw':None,'html':'<rss><channel/></rss>','url':ORIGIN+'/feed.xml','origin':ORIGIN,'platform':'generic','maximum':2,'observed_at':'2026-10-16T10:00:00+00:00'})
  except Exception as error:out['M47']={'exception':type(error).__name__,'message':str(error)}
  def response(req):return httpx.Response(200,text='<meta name="generator" content="wordpress">') if req.url.path=='/' else httpx.Response(500,json={'error':'secret_canary'})
  engine=ToolRuntime(ToolConfig(allowed_origins=(ORIGIN,)),resolver=resolver,wire_transport=httpx.MockTransport(response))
  try:
   accepted=await engine.call('extract',{'schema_version':'1.0','url':ORIGIN});args={'schema_version':'1.0','job_id':accepted['data']['job_id'],'collection':'products'}
   await asyncio.sleep(.3);out['M44_at_300ms']=await engine.call('job_result',args)
   for _ in range(150):
    reply=await engine.call('job_result',args)
    if not reply['ok'] or reply['data']['state']=='succeeded':break
    await asyncio.sleep(.02)
   out['M44_terminal']=reply
  finally:await engine.aclose()
 finally:ledger.pytest_sessionfinish(None,0)
 out.update(total_charged_seconds=time.monotonic()-start,actual_fixture_bytes=sum(ledger.counts.values()),fixture_categories=dict(ledger.counts))
 Path('artifacts/agent-tool-api-mcp/three-offline-diagnosis.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':asyncio.run(main())
