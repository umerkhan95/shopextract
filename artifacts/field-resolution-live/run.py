"""Sequential live cases with hard process deadlines and saved checkpoints."""
import json,os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
CASES=[
 {'name':'01-shopify-smoke','kind':'shopify','platform':'shopify','url':'https://www.boardgamebliss.com','limit':2,'enrich':True},
 {'name':'02-shopify-bliss','kind':'shopify','platform':'shopify','url':'https://www.boardgamebliss.com','limit':12,'enrich':True,'paired_html':True},
 {'name':'03-shopify-401','kind':'shopify','platform':'shopify','url':'https://store.401games.ca','limit':12,'enrich':True,'paired_html':True},
 {'name':'04-woocommerce','kind':'woo','platform':'woocommerce','url':'https://demo.athemes.com/botiga','limit':40,'max_pages':2,'paired_html':True},
 {'name':'05-magento','kind':'magento','platform':'magento','url':'https://magento2-demo.magebit.com','limit':16,'page_size':3,'paired_html':True},
 {'name':'06-shopware','kind':'shopware','platform':'shopware','url':'https://frontends-demo.vercel.app','limit':16,'page_size':3,'paired_html':True},
 {'name':'07-bigcommerce','kind':'pipeline','platform':'bigcommerce','url':'https://cornerstone-light-demo.mybigcommerce.com','limit':8,'timeout':90},
 {'name':'08-generic-css','kind':'generic_css','platform':'generic','url':'https://books.toscrape.com','limit':8},
 {'name':'09-shopify-public','kind':'pipeline','platform':'shopify','url':'https://www.boardgamebliss.com','limit':6},
 {'name':'10-woo-public','kind':'pipeline','platform':'woocommerce','url':'https://demo.athemes.com/botiga','limit':6},
 {'name':'11-magento-public','kind':'pipeline','platform':'magento','url':'https://magento2-demo.magebit.com','limit':6},
 {'name':'12-shopware-public','kind':'pipeline','platform':'shopware','url':'https://frontends-demo.vercel.app','limit':6},
]
if '--smoke' in sys.argv:CASES=CASES[:1]
for case in CASES:
 p=ROOT/(case['name']+'.json')
 if p.exists():print(case['name'],'cached',flush=True);continue
 env=dict(os.environ);env['PYTHONPATH']='src'
 with (ROOT/(case['name']+'.log')).open('w') as f:
  try:
   r=subprocess.run([sys.executable,str(ROOT/'worker.py'),json.dumps(case)],stdout=f,stderr=f,env=env,timeout=case.get('timeout',75)+55)
   if r.returncode:p.write_text(json.dumps({'case':case,'status':'process_error','code':r.returncode}))
  except subprocess.TimeoutExpired:p.write_text(json.dumps({'case':case,'status':'timeout'}))
 d=json.loads(p.read_text());print(case['name'],json.dumps({k:d.get(k) for k in ['status','seconds','requests','product_count','variant_count','paired_html_count','defects']}),flush=True)
