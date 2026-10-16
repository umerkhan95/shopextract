from pathlib import Path
import sys,json
sys.path.insert(0,str(Path.cwd()/'tests'))
from maintenance_process_guard import run_group
root=Path('artifacts/catalog-maintenance-agent/live')
with (root/'run.log').open('w') as out:
 result=run_group([sys.executable,str(root/'run.py')],timeout=59,stdout=out,stderr=out)
(root/'execution.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
