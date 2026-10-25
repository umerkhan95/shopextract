"""One sequential process group, deadline/RSS/orphan checks and compact saved status."""
import json,os,signal,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
PYTHON=ROOT/'.venv/bin/python'
ENV={**os.environ,'PYTHONPATH':str(ROOT/'src')+os.pathsep+str(ROOT),'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','VECLIB_MAXIMUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1','TOKENIZERS_PARALLELISM':'false','HF_HUB_DOWNLOAD_WORKERS':'1','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'}

def group_members(pgid):
    raw=subprocess.run(['ps','-axo','pid=,pgid=,rss='],capture_output=True,text=True,timeout=2).stdout
    return [(int(parts[0]),int(parts[2])*1024) for line in raw.splitlines() if len(parts:=line.split())==3 and int(parts[1])==pgid]

def run(name,command,timeout,rss_limit=None):
    started=time.monotonic();stop=None;maximum=0
    with (OUT/(name+'.log')).open('w') as log:
        child=subprocess.Popen(command,cwd=ROOT,env=ENV,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
        while child.poll() is None:
            members=group_members(child.pid);maximum=max(maximum,sum(amount for pid,amount in members))
            if time.monotonic()-started>timeout:stop='timeout'
            if rss_limit and maximum>rss_limit:stop='rss_limit'
            if stop:
                try:os.killpg(child.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:child.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid,signal.SIGKILL);child.wait(timeout=1)
                break
            time.sleep(.05)
        child.wait()
    orphans=group_members(child.pid)
    if orphans:
        try:os.killpg(child.pid,signal.SIGKILL)
        except ProcessLookupError:pass
    lines=(OUT/(name+'.log')).read_text().splitlines()
    return {'name':name,'command':command,'returncode':child.returncode,'seconds':round(time.monotonic()-started,3),'stop':stop,'max_group_rss_bytes':maximum,'orphans':[p for p,_ in orphans],'summary':next((line for line in reversed(lines) if ' passed' in line or ' failed' in line),'')}


def main():
    mode=sys.argv[1];started=time.monotonic();results=[]
    if mode=='stress':
        groups=[('p5-stress-origin','denied_origin or malformed_numeric_objects or reduced_operator_limits'),
                ('p5-stress-session','real_bootstrap_match or page_cap_partial'),
                ('p5-stress-durable','real_separate_processes or native_list_pagination or foreign_maintenance_category'),
                ('p5-stress-deadlines','deadline_interrupt or session_deadline'),
                ('p5-stress-protocol','real_sdk_root_stdio or missing_sdk or static_and_help')]
        commands=[(name,[str(PYTHON),'-m','pytest','-q','tests/test_cli_operations.py','-k',select],30,512*1024**2) for name,select in groups]
    elif mode=='full':
        files=['test_maintenance_'+name+'.py' for name in ['acceptance','advisor','remaining_edges','review_repairs','store','stress_prerequisites','workflow']]
        commands=[('full-existing',[str(PYTHON),'-m','pytest','-q',*['--ignore=tests/'+f for f in files]],240,None),
                  ('full-maintenance',[str(PYTHON),'-m','pytest','-q',*['tests/'+f for f in files]],240,None)]
    else:raise ValueError(mode)
    target=OUT/(mode+'-status.json')
    for name,command,seconds,rss in commands:
        if time.monotonic()-started>720:raise RuntimeError('total limit')
        result=run(name,command,seconds,rss);results.append(result)
        target.write_text(json.dumps({'mode':mode,'seed':11025,'workers':1,'max_input_bytes':1048576,'max_products':100,'total_limit_seconds':720,'results':results,'seconds':round(time.monotonic()-started,3),'status':'passed' if len(results)==len(commands) and all(r['returncode']==0 and not r['stop'] and not r['orphans'] for r in results) else 'running-or-failed','actual_session_token_counters':'unavailable'},indent=2)+'\n')
        print(json.dumps({k:v for k,v in result.items() if k!='command'}),flush=True)
        if result['returncode'] or result['stop'] or result['orphans']:raise SystemExit(1)

if __name__=='__main__':main()
