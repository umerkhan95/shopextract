from pathlib import Path
import json,sys,time,os
sys.path.insert(0,str(Path.cwd()/'tests'))
from maintenance_process_guard import run_group
p=Path('artifacts/catalog-maintenance-agent')
nodes=(p/'full-suite-unconfirmed-nodes.txt').read_text().splitlines()
assert len(nodes)==140
started=time.monotonic();results=[]
for label,selection,limit in [('seed',nodes[:1],59),('remaining',nodes[1:],179)]:
 remaining=239-(time.monotonic()-started)
 if remaining<=0:break
 with (p/f'suffix-{label}.log').open('w') as out:
  result=run_group([sys.executable,'-m','pytest','-q',*selection],timeout=min(limit,remaining),stdout=out,stderr=out)
 results.append({'phase':label,'node_count':len(selection),**result})
 (p/'suffix-receipt.json').write_text(json.dumps({'results':results,'seconds':time.monotonic()-started,'aggregate_limit_seconds':240,'complete':len(results)==2 and all(r['returncode']==0 for r in results)},indent=2))
 if result['returncode']!=0:break
print((p/'suffix-receipt.json').read_text())
