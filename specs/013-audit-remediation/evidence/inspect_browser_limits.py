"""One local SDK capability inspection; no browser launch or HTTP."""
import inspect,json
from pathlib import Path
import crawl4ai
from crawl4ai import BrowserConfig
root=Path(crawl4ai.__file__).parent
names=['async_crawler_strategy.py','browser_manager.py','async_configs.py']
files={name:(root/name).read_text() for name in names if (root/name).exists()}
terms=['on_page_context_created','service_workers','new_context(','disable-background-networking']
result={'sdk_root':str(root),'network_requests':0,'browser_launched':False,'service_worker_config_parameter':'service_workers' in inspect.signature(BrowserConfig.__init__).parameters,'matches':{}}
for name,source in files.items():
 matches=[]
 for number,line in enumerate(source.splitlines(),1):
  if any(term in line for term in terms):matches.append({'line':number,'text':line.strip()[:220]})
 result['matches'][name]=matches[:15]
print(json.dumps(result,indent=2))
