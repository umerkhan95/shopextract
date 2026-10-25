import json, os, pathlib, runpy, subprocess, sys, tempfile, time
mode=sys.argv[1];source='/before/scripts/run_tests.py' if mode=='before' else '/work/scripts/run_tests.py'
m=runpy.run_path(source)
with tempfile.TemporaryDirectory() as tmp:
    root=pathlib.Path(tmp);pidfile=root/'descendant'
    child='import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(20)'
    leader=f'import subprocess,sys,time;from pathlib import Path;p=subprocess.Popen([sys.executable,"-c",{child!r}]);Path({str(pidfile)!r}).write_text(str(p.pid));time.sleep(20)'
    result=m['run_plan']((m['TestGroup']('descendant',(sys.executable,'-c',leader)),),root/'logs',group_seconds=1,total_seconds=3)
    pid=int(pidfile.read_text())
    try:os.kill(pid,0);gone=False
    except ProcessLookupError:gone=True
    print(json.dumps({'mode':mode,'status':result['status'],'descendant_gone':gone,'groups':result['groups'],'seconds':result['elapsed_seconds']}))
    if mode=='before':assert result['status']=='failed' and not gone
    else:
        assert result['status']=='timeout' and gone and not result['groups'][0]['group_alive_after_cleanup']
        assert m['_subreaper']()==0
        exit7=m['run_plan']((m['TestGroup']('exit7',(sys.executable,'-c','raise SystemExit(7)')),),root/'status',group_seconds=1,total_seconds=2)
        assert exit7['exit_code']==7 and exit7['groups'][0]['returncode']==7
