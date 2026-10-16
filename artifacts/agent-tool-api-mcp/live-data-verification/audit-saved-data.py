"""Independent saved-real-response assertions only; no network/MCP/model calls."""
import json,hashlib,time
from decimal import Decimal
from pathlib import Path
p=Path(__file__).resolve().parent;start=time.monotonic()
r=json.loads((p/'result.json').read_text());receipt=json.loads((p/'receipt.json').read_text());sources=[x for x in receipt['responses'] if '/products.json?' in x['url']]
assert r['outcome']=='passed' and len(sources)==2 and receipt['request_count']==7
for source in receipt['responses']:assert hashlib.sha256((p/source['file']).read_bytes()).hexdigest()==source['sha256']
checks=[]
for number,source in enumerate(sources,1):
 raw=json.loads((p/source['file']).read_text())['products'];items=json.loads((p/f'extract-{number}-response.json').read_text());byid={str(x['id']):x for x in raw};assert len(items)==2
 for product in items:
  actual=byid[product['external_id']];assert len(actual['variants'])==len(product['variants'])<=2
  assert product['title']==actual['title'].strip() and Decimal(product['price'])==Decimal(actual['variants'][0]['price'])
  assert product['product_url']=='https://www.blissworld.com/products/'+actual['handle']
  currency=actual['variants'][0].get('price_currency') or actual.get('currency') or source['cart_currency']
  assert currency=='USD' and product['currency']==currency and product['support']['/currency']['state']=='observed'
  variants=[]
  for output,original in zip(product['variants'],actual['variants']):
   assert output['variant_id']==str(original['id']) and Decimal(output['price'])==Decimal(original['price']) and output['sku']==original.get('sku')
   assert type(original.get('available')) is bool and output['in_stock']==original['available'] and output['support']['/in_stock']['state']=='observed'
   variants.append({k:output.get(k) for k in ['variant_id','price','sku','in_stock']})
  assert product['in_stock']==any(v['available'] for v in actual['variants'])
  assert product['sku']==actual['variants'][0].get('sku')
  if not actual['variants'][0].get('sku'):assert product['sku'] is None and product['support']['/sku']['state']=='unknown'
  assert not actual['variants'][0].get('barcode') and product['gtin'] is None and product['support']['/gtin']['state']=='unsupported'
  checks.append({'sample':number,'title':product['title'],'price':product['price'],'currency':product['currency'],'currency_support':'observed','currency_source':'saved actual cart_currency response cookie','sku':product['sku'],'sku_support':product['support']['/sku']['state'],'stock':product['in_stock'],'stock_support':'observed','gtin':None,'gtin_support':'unsupported','variants':variants,'actual_source':source['file'],'source_sha256':source['sha256']})
assert [(x['index_a'],x['index_b'],x['relation']) for x in r['matches']]==[(0,0,'exact'),(1,1,'exact')]
proof=r['evidence']['evidence'];assert proof['pointer']=='/value' and proof['retained_data']=={'source_pointer':'/variants/0/price','value':json.loads((p/sources[-1]['file']).read_text())['products'][0]['variants'][0]['price']} and proof['source_url']==sources[-1]['url']
assert r['tools'].count('evidence')==2 and r['version_error']['error']['code']=='unsupported_version' and r['changes']['items']==[] and r['changes']['metadata']['status']=='compared'
result={'outcome':'passed','audit_seconds':time.monotonic()-start,'network_requests':0,'fields':checks,'matches':[{k:m[k] for k in ['index_a','index_b','relation','evidence']} for m in r['matches']],'evidence':{'source_url':proof['source_url'],'pointer':proof['pointer'],'retained_data':proof['retained_data']},'wrong_owner':'Live driver asserted not_found and completed successfully; no leaked support','version_error':'unsupported_version','changes':'Actual real captures compared,0events; incomplete2-product catalog, no commercial-transition/full-catalog unchanged claim','captured_response_bytes':sum(x['bytes'] for x in receipt['responses']),'observations':'NoGLM/key/model. Native source supplies currency via response cookie, not default. MissingSKU/GTIN stay unknown/unsupported.'}
(p/'data-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in {'fields','matches'}}))
