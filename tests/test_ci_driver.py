"""CI amendment: actual bounded subprocess scheduling, assertions kept in native suites."""
import importlib.util
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time
import pytest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'scripts/run_tests.py'


def driver():
    assert SCRIPT.is_file(),'Bounded shared-budget CI driver is not implemented'
    spec=importlib.util.spec_from_file_location('shopextract_ci_driver',SCRIPT)
    module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
    return module


def command(text):return (sys.executable,'-c',text)


def alive(pgid):
    try:os.killpg(pgid,0);return True
    except ProcessLookupError:return False


def test_configured_ci_uses_shared_budget_driver():
    assert 'python scripts/run_tests.py' in (ROOT/'.github/workflows/test.yml').read_text()


def test_plan_semantic_family_partition():
    d=driver();plan=d.build_plan(ROOT,sys.executable)
    assert [g.name for g in plan]==['main','reliable-oracle','maintenance']
    oracle='tests/test_reliable_changes_stress.py'
    assert '--ignore='+oracle in plan[0].command and plan[1].command[-1]==oracle
    assert len(d.MAINTENANCE_FILES)==7
    for path in d.MAINTENANCE_FILES:
        assert '--ignore='+path in plan[0].command and path in plan[2].command
    assert not any('::' in arg for group in plan for arg in group.command)
    for path in ROOT.glob('tests/test_*.py'):
        relative=path.relative_to(ROOT).as_posix()
        memberships=[relative not in (*d.MAINTENANCE_FILES,oracle),relative==oracle,relative in d.MAINTENANCE_FILES]
        assert sum(memberships)==1


def test_sequential_real_children_and_stop_on_failure(tmp_path):
    d=driver();marker=tmp_path/'order'
    first=command(f'from pathlib import Path;Path({str(marker)!r}).write_text("A")')
    second=command(f'from pathlib import Path;p=Path({str(marker)!r});assert p.read_text()=="A";p.write_text("AB")')
    result=d.run_plan((d.TestGroup('a',first),d.TestGroup('b',second)),tmp_path/'passed',group_seconds=2,total_seconds=5)
    assert result['status']=='passed' and result['exit_code']==0 and marker.read_text()=='AB'
    marker.unlink()
    result=d.run_plan((d.TestGroup('fail',command('raise SystemExit(7)')),d.TestGroup('must-not-run',first)),tmp_path/'failed',group_seconds=2,total_seconds=5)
    assert result['exit_code']==7 and result['status']=='failed' and len(result['groups'])==1 and not marker.exists()


def test_per_group_timeout_kills_and_reaps(tmp_path):
    d=driver()
    group=d.TestGroup('slow',command('import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(5)'))
    result=d.run_plan((group,),tmp_path,group_seconds=.3,total_seconds=2)
    assert result['status']=='timeout' and result['exit_code']==1
    row=result['groups'][0]
    assert row['timeout_kind']=='group' and not row['group_alive_after_cleanup'] and not alive(row['pid'])
    assert result['elapsed_seconds']<.7


def test_shared_budget_stops_later_groups(tmp_path):
    d=driver();marker=tmp_path/'not-run'
    groups=(d.TestGroup('quick',command('import time;time.sleep(.12)')),d.TestGroup('shared',command('import time;time.sleep(3)')),
        d.TestGroup('not-run',command(f'from pathlib import Path;Path({str(marker)!r}).touch()')))
    result=d.run_plan(groups,tmp_path/'logs',group_seconds=.5,total_seconds=.6)
    assert result['status']=='timeout' and result['groups'][-1]['timeout_kind']=='total'
    assert len(result['groups'])==2 and not marker.exists() and result['elapsed_seconds']<.9
    assert not any(row['group_alive_after_cleanup'] for row in result['groups'])


@pytest.mark.parametrize('signum,code',[(signal.SIGINT,130),(signal.SIGTERM,143)])
def test_interrupt_cleans_active_group(tmp_path,signum,code):
    d=driver();ready=tmp_path/'ready';out=tmp_path/'out';runner=tmp_path/'runner.py'
    child=command(f'import time;from pathlib import Path;Path({str(ready)!r}).touch();time.sleep(20)')
    runner.write_text(f'import runpy\nfrom pathlib import Path\nm=runpy.run_path({str(SCRIPT)!r})\nr=m["run_plan"]((m["TestGroup"]("active",{child!r}),),Path({str(out)!r}),group_seconds=5,total_seconds=10)\nraise SystemExit(r["exit_code"])\n')
    errlog=open(tmp_path/'runner-stderr.log','w')
    process=subprocess.Popen([sys.executable,str(runner)],stdout=subprocess.DEVNULL,stderr=errlog)
    try:
        end=time.monotonic()+3
        while not ready.exists() and process.poll() is None and time.monotonic()<end:time.sleep(.01)
        assert ready.exists()
        process.send_signal(signum);assert process.wait(timeout=2)==code
        report=json.loads((out/'report.json').read_text())
        assert report['status']=='interrupted' and not report['groups'][0]['group_alive_after_cleanup']
        assert not alive(report['groups'][0]['pid'])
    finally:
        if process.poll() is None:process.kill();process.wait()
        errlog.close()


def test_driver_rejects_raised_or_nonfinite_caps():
    d=driver()
    for args in [('--total-seconds','481'),('--group-seconds','241'),('--total-seconds','nan'),('--group-seconds','inf'),('--total-seconds','0'),('--total-seconds','-1'),('--group-seconds','-1')]:
        with pytest.raises(SystemExit) as error:d.parse_args(args)
        assert error.value.code==2

    maximum=d.parse_args(('--group-seconds','240','--total-seconds','480'))
    assert maximum.group_seconds==240 and maximum.total_seconds==480
    narrower=d.parse_args(('--group-seconds','.5','--total-seconds','.6'))
    assert narrower.group_seconds==.5 and narrower.total_seconds==.6


def test_descendant_group_cleanup(tmp_path):
    d=driver();pidfile=tmp_path/'descendant'
    child='import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(20)'
    leader=f'import subprocess,sys,time;from pathlib import Path;p=subprocess.Popen([sys.executable,"-c",{child!r}]);Path({str(pidfile)!r}).write_text(str(p.pid));time.sleep(20)'
    result=d.run_plan((d.TestGroup('descendant',command(leader)),),tmp_path/'logs',group_seconds=1,total_seconds=3)
    assert result['status']=='timeout' and pidfile.exists()
    row=result['groups'][0]
    assert not row['group_alive_after_cleanup'] and not alive(row['pid'])
    descendant=int(pidfile.read_text())
    try:os.kill(descendant,0)
    except ProcessLookupError:pass
    else:pytest.fail('owned descendant survived group cleanup')


def test_spawn_failure_report_and_no_later_launch(tmp_path):
    d=driver();marker=tmp_path/'later'
    plan=(d.TestGroup('missing',(str(tmp_path/'no-executable'),)),d.TestGroup('later',command(f'from pathlib import Path;Path({str(marker)!r}).touch()')))
    result=d.run_plan(plan,tmp_path/'logs',group_seconds=1,total_seconds=3)
    assert result['status']=='failed' and result['exit_code']==1 and not marker.exists()
    assert len(result['groups'])==1 and result['groups'][0]['error']=='spawn_failed'
    assert json.loads((tmp_path/'logs/report.json').read_text())['status']=='failed'


@pytest.mark.parametrize('signum,code',[(signal.SIGINT,130),(signal.SIGTERM,143)])
def test_inter_group_signal_report_and_no_later_launch(tmp_path,monkeypatch,signum,code):
    d=driver();marker=tmp_path/'later';original=Path.write_text;sent=False
    def report_boundary(path,text,*args,**kwargs):
        nonlocal sent
        if path.name=='report.json' and not sent:
            sent=True;os.kill(os.getpid(),signum)
        return original(path,text,*args,**kwargs)
    monkeypatch.setattr(Path,'write_text',report_boundary)
    groups=(d.TestGroup('first',command('pass')),d.TestGroup('later',command(f'from pathlib import Path;Path({str(marker)!r}).touch()')))
    result=d.run_plan(groups,tmp_path/'logs',group_seconds=2,total_seconds=5)
    assert sent and result['status']=='interrupted' and result['exit_code']==code
    assert len(result['groups'])==1 and not marker.exists()
    assert json.loads((tmp_path/'logs/report.json').read_text())['exit_code']==code
    assert not result['groups'][0]['group_alive_after_cleanup']


def test_unavailable_group_probe_checks_actual_membership(tmp_path,monkeypatch):
    d=driver();process=subprocess.Popen(command('import time;time.sleep(2)'),start_new_session=True)
    original=os.killpg
    try:
        with monkeypatch.context() as changed:
            def unavailable(pgid,signum):
                if signum==0:raise PermissionError('controlled unavailable zero-signal probe')
                return original(pgid,signum)
            changed.setattr(os,'killpg',unavailable)
            assert d._group_exists(process.pid)
            original_run=subprocess.run
            def unavailable_table(*args,**kwargs):raise subprocess.TimeoutExpired('ps',.1)
            changed.setattr(subprocess,'run',unavailable_table)
            assert d._group_exists(process.pid)  # unknown is never proof of absence
            changed.setattr(subprocess,'run',original_run)
            process.terminate();process.wait(timeout=1)
            assert not d._group_exists(process.pid)
    finally:
        if process.poll() is None:process.kill();process.wait()


@pytest.mark.parametrize('signum,code',[(signal.SIGINT,130),(signal.SIGTERM,143)])
def test_signal_during_cleanup_is_latched(tmp_path,monkeypatch,signum,code):
    d=driver();original=d._signal_group;sent=False;marker=tmp_path/'later'
    def cleanup_boundary(pid,operation):
        nonlocal sent
        if operation==signal.SIGTERM and not sent:
            sent=True;os.kill(os.getpid(),signum)
        return original(pid,operation)
    monkeypatch.setattr(d,'_signal_group',cleanup_boundary)
    groups=(d.TestGroup('active',command('import time;time.sleep(3)')),
            d.TestGroup('later',command(f'from pathlib import Path;Path({str(marker)!r}).touch()')))
    result=d.run_plan(groups,tmp_path/'logs',group_seconds=.3,total_seconds=2)
    assert sent and result['status']=='interrupted' and result['exit_code']==code
    assert len(result['groups'])==1 and not marker.exists() and not result['groups'][0]['group_alive_after_cleanup']
    assert json.loads((tmp_path/'logs/report.json').read_text())['exit_code']==code


def test_owned_group_reaping_preserves_unrelated_child():
    """An adopted owned zombie is collected without stealing another child's status."""
    d=driver();reader,writer=os.pipe();pid=os.fork()
    if pid==0:
        os.close(reader);os.setsid();os.write(writer,b'1');os._exit(0)
    os.close(writer)
    unrelated=subprocess.Popen(command('import time;time.sleep(.3);raise SystemExit(7)'),start_new_session=True)
    try:
        assert os.read(reader,1)==b'1'
        deadline=time.monotonic()+1
        while time.monotonic()<deadline:
            d._reap_group(pid,deadline)
            try:os.kill(pid,0)
            except ProcessLookupError:break
            time.sleep(.005)
        else:pytest.fail('owned zombie was not reaped')
        assert unrelated.wait(timeout=1)==7
    finally:
        os.close(reader)
        try:os.kill(pid,signal.SIGKILL);os.waitpid(pid,0)
        except (ProcessLookupError,ChildProcessError):pass
        if unrelated.poll() is None:unrelated.kill();unrelated.wait()


def test_group_reaping_waits_for_popen_leader_status(tmp_path,monkeypatch):
    d=driver();owned=[];original=subprocess.Popen;reap=d._reap_group
    def launch(*args,**kwargs):
        process=original(*args,**kwargs);owned.append(process);return process
    def checked_reap(pgid,deadline):
        assert next(p for p in owned if p.pid==pgid).returncode is not None
        return reap(pgid,deadline)
    monkeypatch.setattr(subprocess,'Popen',launch);monkeypatch.setattr(d,'_reap_group',checked_reap)
    result=d.run_plan((d.TestGroup('exit7',command('raise SystemExit(7)')),),tmp_path,group_seconds=1,total_seconds=2)
    assert result['exit_code']==7 and result['groups'][0]['returncode']==7


def test_subreaper_state_restored_and_setup_failure_stops_launch(tmp_path,monkeypatch):
    d=driver();previous=d._subreaper()
    result=d.run_plan((d.TestGroup('ok',command('pass')),),tmp_path/'ok',group_seconds=1,total_seconds=2)
    assert result['status']=='passed' and d._subreaper()==previous
    def denied(*args):raise OSError('controlled subreaper setup failure')
    monkeypatch.setattr(d,'_subreaper',denied)
    result=d.run_plan((d.TestGroup('never',command('pass')),),tmp_path/'denied',group_seconds=1,total_seconds=2)
    assert result['status']=='failed' and result['groups']==[]
    assert result['error']=='subreaper_unavailable'
