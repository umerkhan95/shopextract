"""Single bounded read-only live case per process; call only after offline green."""
import json
import sys
from pathlib import Path
from datetime import datetime,timezone
import httpx
from click.testing import CliRunner
from shopextract.cli import main

cases={
 'shopify':['extract','https://www.allbirds.com','--platform','shopify','--max','2'],
 'woo':['extract','https://woocommerce.com','--platform','woocommerce','--max','2'],
 'html':['extract-one','https://www.naheed.pk/max-factor-creme-puff-pressed-powder-42-deep-beige'],
 'missing':['extract-one','https://www.naheed.pk/shopextract-audit-missing-product-20261101'],
}
case=sys.argv[1];requests=[];responses=[];original=httpx.AsyncClient
async def request_hook(request):
 if len(requests)>=3:raise RuntimeError('Live request ceiling reached before send')
 requests.append(str(request.url))
async def response_hook(response):responses.append({'url':str(response.url),'status':response.status_code})
def client(*a,**kw):
 hooks=kw.setdefault('event_hooks',{})
 hooks['request']=[*hooks.get('request',[]),request_hook]
 hooks['response']=[*hooks.get('response',[]),response_hook]
 return original(*a,**kw)
httpx.AsyncClient=client
result=CliRunner().invoke(main,['--output-format','json',*cases[case],'--timeout','20','--no-browser'])
try:data=json.loads(result.stdout)
except ValueError:data={'unparseable_stdout':result.stdout[:300]}
observed={'case':case,'provenance':'actual read-only HTTP observation',
 'at':datetime.now(timezone.utc).isoformat(),'requests':requests,'responses':responses,
 'request_cap':3,'exit_code':result.exit_code,'ok':data.get('ok'),
 'completeness':data.get('completeness'),'error':data.get('error')}
d=data.get('data') or {};observed['product_count']=d.get('product_count',1 if d.get('product') else 0)
if case in ('shopify','woo'):observed['assertion']=result.exit_code==3 and observed['product_count']>0 and d.get('catalog_complete') is False
elif case=='html':observed['assertion']=result.exit_code==0 and bool(d.get('product'))
else:observed['assertion']=any(r['status']==404 for r in responses) and result.exit_code==1 and not d.get('product')
Path(__file__).with_name('live-'+case+'.json').write_text(json.dumps(observed,indent=2)+'\n')
print(json.dumps(observed))
