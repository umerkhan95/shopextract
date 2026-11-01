import asyncio,json
from pathlib import Path
from datetime import datetime,timezone
import httpx
from shopextract import discover,Platform
from shopextract._discovery_runtime import DiscoveryClient
URL='https://www.khaadi.com'
async def main():
 requests=[];responses=[]
 async def request(r):
  if len(requests)>=5:raise httpx.RequestError('Live request ceiling')
  requests.append(str(r.url))
 async def response(r):responses.append({'url':str(r.url),'status':r.status_code})
 async with httpx.AsyncClient(timeout=20,follow_redirects=False,event_hooks={'request':[request],'response':[response]}) as c:
  guard=DiscoveryClient(c,max_requests=5)
  urls=await discover(URL,platform=Platform.MAGENTO,max_urls=2,timeout=20,client=guard)
 policy=guard.robots.get(URL)
 known=policy is not None and (not isinstance(policy,bool) or policy is True or any(r['url']==URL+'/robots.txt' and r['status'] in (401,403) for r in responses))
 allowed=lambda u: policy if isinstance(policy,bool) else policy.can_fetch('ShopExtract',u) if policy is not None else False
 forbidden=[u for u in requests if not u.endswith('/robots.txt') and not allowed(u)]
 result={'provenance':'actual read-only HTTP discovery; borrowed guarded transport, not live worker timing',
 'at':datetime.now(timezone.utc).isoformat(),'url':URL,'request_cap':5,'requests':requests,'responses':responses,'urls':list(urls),'reasons':urls.reasons,'request_count':guard.request_count,'policy_observed':known,'home_allowed':allowed(URL+'/home'),'forbidden_requests':forbidden,
 'assertion':known and not forbidden and all(allowed(u) for u in urls) and list(urls)==sorted(set(urls)) and len(requests)<=5}
 Path(__file__).with_name('live-discovery.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':asyncio.run(main())
