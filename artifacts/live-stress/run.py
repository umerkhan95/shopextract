"""Sequential subprocess driver, one case at a time, hard deadlines and saved checkpoints."""
import json,os,subprocess,sys
from pathlib import Path
P=Path(__file__).resolve().parent
BASE=[
 {'name':'01-magento-smoke','kind':'magento','platform':'magento','url':'https://magento2-demo.magebit.com','page_size':3,'limit':7},
 {'name':'02-shopware-smoke','kind':'shopware','platform':'shopware','url':'https://frontends-demo.vercel.app','page_size':3,'limit':7},
 {'name':'03-magento-pagination','kind':'magento','platform':'magento','url':'https://magento2-demo.magebit.com','page_size':5,'limit':31},
 {'name':'04-shopware-pagination','kind':'shopware','platform':'shopware','url':'https://frontends-demo.vercel.app','page_size':5,'limit':31},
 {'name':'05-magento-pipeline','kind':'pipeline','platform':'magento','url':'https://magento2-demo.magebit.com','limit':25},
 {'name':'06-shopware-pipeline','kind':'pipeline','platform':'shopware','url':'https://frontends-demo.vercel.app','limit':25},
 {'name':'07-shopify-bliss','kind':'shopify','platform':'shopify','url':'https://www.boardgamebliss.com','limit':20,'enrich':True},
 {'name':'08-shopify-401','kind':'shopify','platform':'shopify','url':'https://store.401games.ca','limit':20,'enrich':True},
 {'name':'09-woocommerce','kind':'woo','platform':'woocommerce','url':'https://demo.athemes.com/botiga','limit':100,'max_pages':2},
 {'name':'10-bigcommerce-html','kind':'pipeline','platform':'bigcommerce','url':'https://cornerstone-light-demo.mybigcommerce.com','limit':6,'timeout':75},
 {'name':'11-magento-repeat','repeats':3,'kind':'pipeline','platform':'magento','url':'https://magento2-demo.magebit.com','limit':25},
 {'name':'12-shopware-repeat','repeats':3,'kind':'pipeline','platform':'shopware','url':'https://frontends-demo.vercel.app','limit':25},
 {'name':'13-bigcommerce-repeat','repeats':3,'kind':'pipeline','platform':'bigcommerce','url':'https://cornerstone-light-demo.mybigcommerce.com','limit':6,'timeout':75},
 {'name':'15-magento-full-catalog','kind':'magento','platform':'magento','url':'https://magento2-demo.magebit.com','page_size':19,'limit':220,'timeout':90},
 {'name':'16-shopware-page-budget','kind':'shopware','platform':'shopware','url':'https://frontends-demo.vercel.app','page_size':5,'limit':40,'max_pages':1},
 {'name':'17-magento-page-budget','kind':'magento','platform':'magento','url':'https://magento2-demo.magebit.com','page_size':5,'limit':40,'max_pages':1},
 {'name':'18-generic-css-repeat','kind':'generic_css','platform':'generic','url':'https://books.toscrape.com','limit':6,'repeats':3,'timeout':60},
]
if '--smoke' in sys.argv:BASE=BASE[:2]
if '--boundary' in sys.argv:
 d=json.loads((P/'01-magento-smoke.json').read_text())
 BASE=[{'name':'14-magento-boundary','kind':'magento_boundary','platform':'magento','url':'https://magento2-demo.magebit.com','page_size':3,'limit':4,'skus':[x['id'] for x in d['products'][:5]]}]
for case in BASE:
 target=P/(case['name']+'.json')
 if target.exists():print(case['name'],'cached',flush=True);continue
 env=dict(os.environ);env['PYTHONPATH']='src'
 with (P/(case['name']+'.log')).open('w') as log:
  try:
   completed=subprocess.run([sys.executable,str(P/'worker.py'),json.dumps(case)],env=env,stdout=log,stderr=log,timeout=case.get('timeout',60)+15)
   if completed.returncode:target.write_text(json.dumps({'case':case,'status':'process_error','exit_code':completed.returncode}))
  except subprocess.TimeoutExpired:target.write_text(json.dumps({'case':case,'status':'process_timeout'}))
 result=json.loads(target.read_text())
 print(case['name'],json.dumps({k:result.get(k) for k in ['status','seconds','requests','product_count','variant_count','peak_rss_mib','defects']}),flush=True)
