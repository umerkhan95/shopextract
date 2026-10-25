"""One authorized read-only P1 smoke; original HTTP transport sends are counted."""
import json
from pathlib import Path
import time

import httpx
from click.testing import CliRunner
from shopextract.cli import main

OUT=Path('specs/011-cli-feature-parity/p1/evidence/live')
OUT.mkdir(parents=True,exist_ok=True)
HOST='www.boardgamebliss.com'
class LiveStop(BaseException): pass
original=httpx.AsyncHTTPTransport.handle_async_request
attempts=[]
started=time.monotonic()
async def counted(self,request):
 if request.method!='GET' or request.url.host!=HOST or len(attempts)>=5 or any(r['url']==str(request.url) for r in attempts):
  raise LiveStop('undeclared host/method, request cap, or retry prevented before send')
 if time.monotonic()-started>=30: raise LiveStop('deadline')
 record={'method':request.method,'url':str(request.url)}
 attempts.append(record)
 response=await original(self,request)
 record['status']=response.status_code
 if response.status_code>=400: raise LiveStop('first source HTTP failure; retry/fallback stopped')
 return response
report={'domain':HOST,'request_limit':5,'product_limit':2,'timeout_seconds':30,'retries':0,'attempts':attempts,'actual_observation':'pending'}
httpx.AsyncHTTPTransport.handle_async_request=counted
try:
 result=CliRunner().invoke(main,['--output-format','json','extract',f'https://{HOST}','--platform','shopify','--max','2','--timeout','30','--no-browser'])
 (OUT/'stdout.json').write_text(result.stdout)
 (OUT/'stderr.log').write_text(result.stderr)
 report['exit_code']=result.exit_code
 response=json.loads(result.stdout)
 data=response.get('data')
 assert result.exit_code in (0,3) and data is not None,'no usable extraction result'
 assert 0<data['product_count']<=2,'nonempty bounded products'
 assert len(data['products'])==data['product_count'],'portable record count'
 for record in data['products']:
  assert record['product']['title'],'nonempty title'
  assert record['evidence_contract'] is not None,'captured native evidence'
 report['products_retained']=data['product_count']
 report['actual_observation']='passed'
 report['catalog_complete']=data['catalog_complete']
except (Exception,LiveStop) as exc:
 report['actual_observation']='failed_or_blocked'
 report['limitation']=str(exc)[:250]
finally:
 httpx.AsyncHTTPTransport.handle_async_request=original
 report['elapsed_seconds']=round(time.monotonic()-started,3)
 report['actual_http_attempts']=len(attempts)
 (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='attempts'}))
