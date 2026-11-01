"""Compressed wire bytes exercise real HTTPX decoding and owned guard copies."""
import gzip
import httpx
import pytest
from shopextract._discovery_runtime import DiscoveryClient
from shopextract._discover import _discover_local
from shopextract._models import Platform
ROOT='https://compressed.example'

@pytest.mark.asyncio
async def test_gzip_robots_and_sitemap_real_decoder():
 def wire(r):
  text='User-agent: *\nDisallow: /private' if r.url.path=='/robots.txt' else '<urlset><url><loc>'+ROOT+'/products/a</loc></url><url><loc>'+ROOT+'/private</loc></url></urlset>'
  return httpx.Response(200,content=gzip.compress(text.encode()),headers={'Content-Encoding':'gzip','Content-Type':'text/plain' if r.url.path=='/robots.txt' else 'application/xml'})
 async with httpx.AsyncClient(transport=httpx.MockTransport(wire)) as c:
  guard=DiscoveryClient(c);result=await _discover_local(ROOT,platform=Platform.GENERIC,client=guard)
 assert list(result)==[ROOT+'/products/a'] and result.request_count==2
 assert 'robots_unavailable' not in result.reasons

@pytest.mark.asyncio
async def test_gzip_json_copy_retains_headers_status_and_url():
 content=b'{"products":[{"id":1}]}'
 def wire(r):
  if r.url.path=='/robots.txt':return httpx.Response(404)
  return httpx.Response(200,content=gzip.compress(content),headers={'Content-Encoding':'gzip','Content-Type':'application/json','Set-Cookie':'source=seen; Path=/'})
 async with httpx.AsyncClient(transport=httpx.MockTransport(wire)) as c:
  response=await DiscoveryClient(c).get(ROOT+'/products.json?limit=1')
 assert response.json()=={'products':[{'id':1}]} and response.content==content
 assert response.status_code==200 and str(response.url)==ROOT+'/products.json?limit=1'
 assert response.headers['content-type']=='application/json' and 'source=seen' in response.headers['set-cookie']
 assert 'content-encoding' not in response.headers and int(response.headers['content-length'])==len(content)

@pytest.mark.asyncio
async def test_gzip_decoded_budget_remains_enforced():
 def wire(r):return httpx.Response(404) if r.url.path=='/robots.txt' else httpx.Response(200,content=gzip.compress(b'x'*129),headers={'Content-Encoding':'gzip'})
 async with httpx.AsyncClient(transport=httpx.MockTransport(wire)) as c:
  guard=DiscoveryClient(c,response_bytes=128)
  with pytest.raises(httpx.HTTPError):await guard.get(ROOT+'/body')
 assert 'discovery_response_budget' in guard.reasons and guard.request_count==2
