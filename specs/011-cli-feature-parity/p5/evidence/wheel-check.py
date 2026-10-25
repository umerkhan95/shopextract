"""Genuine wheel install outside checkout, no dependency installation or runtime activation for discovery."""
import json,os,subprocess,sys,tempfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4];OUT=Path(__file__).resolve().parent
PYTHON=ROOT/'.venv/bin/python'
env={**os.environ,'PYTHONPATH':'','OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','TOKENIZERS_PARALLELISM':'false','PIP_DISABLE_PIP_VERSION_CHECK':'1','PIP_NO_INDEX':'1','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'}
results=[]
def run(command,cwd,timeout=60,expected=0):
 start=time.monotonic();r=subprocess.run(command,cwd=cwd,env=env,capture_output=True,text=True,timeout=timeout)
 results.append({'command':command,'returncode':r.returncode,'seconds':round(time.monotonic()-start,3)})
 if r.returncode!=expected:raise AssertionError((command,r.returncode,r.stdout[-1500:],r.stderr[-1000:]))
 return r.stdout
with tempfile.TemporaryDirectory(prefix='shopextract-wheel-') as folder:
 work=Path(folder);wheels=work/'wheels';wheels.mkdir();venv=work/'env'
 run([str(PYTHON),'-m','pip','wheel','--no-deps','--no-build-isolation',str(ROOT),'--wheel-dir',str(wheels)],work,120)
 wheel=next(wheels.glob('*.whl'))
 run([str(PYTHON),'-m','venv','--system-site-packages',str(venv)],work,60)
 python=venv/'bin/python';console=venv/'bin/shopextract'
 run([str(python),'-m','pip','install','--no-deps',str(wheel)],work,60)
 # One installed Python process inspects every nested help path without optional runtime.
 runner=work/'inspect-installed.py'
 runner.write_text('''import json,sys\nfrom pathlib import Path\nimport shopextract\nfrom shopextract.cli import main\nfrom click.testing import CliRunner\nfrom shopextract._cli_discovery import command_inventory,packaged_schema\nfrom shopextract.tools import ToolRuntime\norigin=Path(shopextract.__file__).resolve()\nassert str(origin).startswith(sys.prefix), (origin,sys.prefix)\ndef forbidden(*a,**kw):raise AssertionError("discovery started runtime")\nToolRuntime.__init__=forbidden\nrows=command_inventory(main)\nfor row in rows:\n r=CliRunner().invoke(main,[*row['path'],'--help']);assert r.exit_code==0,(row['path'],r.output)\nr=CliRunner().invoke(main,['schema','list']);assert r.exit_code==0,r.output\nschemas=json.loads(r.stdout)['data']['schemas']\nfor schema in schemas:assert packaged_schema(schema['name'])\nprint(json.dumps({'origin':str(origin),'prefix':sys.prefix,'commands':len(rows),'leaves':sum(not r['group'] for r in rows),'schema_resources':len(schemas),'all_nested_help':'passed','runtime_constructors':0}))\n''')
 inspected=json.loads(run([str(python),str(runner)],work,60))
 cap=json.loads(run([str(console),'capabilities'],work))
 module_cap=json.loads(run([str(python),'-m','shopextract.cli','capabilities'],work))
 assert cap==module_cap
 for args in [['--help'],['tools','serve','--help'],['maintenance','run','--help'],['categories','tree','link','--help'],['evidence','bundle','create','--help'],['schema','show','tool:match']]:run([str(console),*args],work)
 import shutil
 examples=work/'examples';shutil.copytree(ROOT/'examples/cli',examples)
 normalize=run([str(console),'--config',str(examples/'cli.json'),'normalize',str(examples/'raw-products.json')],work)
 assert json.loads(normalize)['data']['product_count']==1
 normalized=work/'normalized.json';normalized.write_text(normalize)
 assert json.loads(run([str(console),'quality',str(normalized)],work))['ok']
 assert json.loads(run([str(console),'tools','call','--config',str(examples/'operator.json'),'--request',str(examples/'session.json'),'--timeout','10'],work))['data']['steps'][0]['result']['captures']==[]
 db=str(work/'jobs.db')
 made=json.loads(run([str(console),'maintenance','--db',db,'create',str(examples/'goal.json')],work));key=made['data']['job_id']
 assert json.loads(run([str(console),'maintenance','--db',db,'list','--limit','10'],work))['data']['jobs'][0]['id']==key
 partial=json.loads(run([str(console),'maintenance','--db',db,'run',key,'--timeout','10'],work,expected=3));assert partial['data']['stop_reason']=='product_budget'
 import zipfile,hashlib
 with zipfile.ZipFile(wheel) as z:packaged=[n for n in z.namelist() if '/schemas/' in n]
 result={'status':'passed','python_version':sys.version.split()[0],'wheel_name':wheel.name,'wheel_sha256':hashlib.sha256(wheel.read_bytes()).hexdigest(),'wheel_schema_files':len(packaged),'installed':inspected,'console_module_capabilities_equal':True,'commands':results,'dependencies_installed':False,'cwd_outside_checkout':True,'pythonpath_cleared':True,'limitations':'Python3.10.11 only; no3.11/3.12 local claim; MCP real SDK verified separately in .venv, discovery intentionally no runtime activation.'}
 (OUT/'wheel-report.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k not in ('commands','installed')}))
