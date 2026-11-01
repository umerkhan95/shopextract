"""Bounded offline audit diagnostics; external transport only is replaced."""
import asyncio
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import httpx
from shopextract._normalize import _normalize_shopify, _normalize_woocommerce
from shopextract.extractors._schema_org import SchemaOrgExtractor
from shopextract.extractors.unified import UnifiedCrawlExtractor
from shopextract.extractors.woocommerce import WooCommerceExtractor
from shopextract._cli_extract import emit_result
from shopextract._cli_core import make_response
from shopextract.analyze.stats import count_categories, _is_in_stock
from shopextract.export._feed import _add_google_item_fields
from shopextract.validate.marketplace import validate
from unittest.mock import patch
out={'provenance':'synthetic offline, no network; current production paths','seed':0,'network_requests':0}
root={'@type':'ItemPage','mainEntity':{'@type':'Product','name':'Real product','sku':'SKU1'}}
def html(data):return '<script type="application/ld+json">'+json.dumps(data)+'</script>'
out['jsonld']={'root_itempage_count':len(SchemaOrgExtractor.extract_from_html(html(root),'https://example.invalid/p')),'graph_itempage_count':len(SchemaOrgExtractor.extract_from_html(html({'@graph':[root]}),'https://example.invalid/p'))}
og='<meta property="og:title" content="Returns and Exchanges"><meta property="og:type" content="website">'
out['policy_page']={'extracted':UnifiedCrawlExtractor._extract_structured_from_html(og,'https://example.invalid/policy')}
s=_normalize_shopify({'id':1,'title':'Thing','handle':'thing','variants':[{'id':2,'price':'10'}]},'https://example.invalid')
out['currency']={'value':s['currency'],'accepted':s.outcomes['/currency'].accepted}
w=_normalize_woocommerce({'id':1,'name':'Woo','brands':[{'name':'Acme'}],'variants':[{'id':2,'price':'10'}],'prices':{'price':'0','currency_code':'PKR','currency_minor_unit':2}},'https://example.invalid')
out['woo_fields']={'vendor':w.get('vendor'),'variants':w.get('variants'),'price':str(w['price']),'price_accepted':w.outcomes['/price'].accepted}
out['analysis']={'categories':count_categories([{'category_path':['A'],'product_type':'A'}]),'missing_stock':_is_in_stock({}),'null_stock':_is_in_stock({'in_stock':None})}
item=ET.Element('item');_add_google_item_fields(item,{'title':'Thing','vendor':'Acme','price':'10'})
out['feed']={'xml':ET.tostring(item,encoding='unicode')}
v=validate([{'title':'Thing','price':'10','image_url':'https://example.invalid/placeholder.jpg','product_url':'https://example.invalid/p','currency':'NOPE','description':''}])
out['validation']={'valid':v.valid,'invalid':v.invalid,'warnings':v.warnings}
for complete in (None,False,True):
 data={'products':[],'catalog_complete':complete,'errors':[]}
 partial=bool(data['errors']) or data['catalog_complete'] is False
 try:
  with patch('shopextract._cli_extract.emit_response') as emit: emit_result(data,partial=partial)
  out['empty_'+str(complete)]=emit.call_args.args[0]
 except Exception as e: out['empty_'+str(complete)]={'exception':type(e).__name__,'code':getattr(e,'code',None)}
async def woo():
 calls=[]
 def respond(req):
  calls.append(str(req.url))
  return httpx.Response(200,json=[{'id':i,'name':'Thing'} for i in range(100)]) if len(calls)==1 else httpx.Response(404)
 async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
  r=await WooCommerceExtractor(http_client=client,max_pages=3).extract('https://example.invalid')
 return {'calls':len(calls),'products':len(r.products),'complete':r.complete,'error':r.error}
out['woo_midstream_404']=asyncio.run(woo())
Path(__file__).with_name('diagnostic.json').write_text(json.dumps(out,indent=2,default=str)+'\n')
print(json.dumps({k:v for k,v in out.items() if k not in ('policy_page','feed')},default=str))
