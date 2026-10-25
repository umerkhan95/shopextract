"""Run every test sequentially within shared480s and per-family240s ceilings."""
import argparse
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

MAINTENANCE_FILES=tuple('tests/test_maintenance_'+name+'.py' for name in (
    'acceptance','advisor','remaining_edges','review_repairs','store','stress_prerequisites','workflow'))
ORACLE_FILE='tests/test_reliable_changes_stress.py'


@dataclass(frozen=True)
class TestGroup:
    name: str
    command: tuple[str,...]


def build_plan(root,python):
    """Semantic files, including all assertions and future ordinary test additions."""
    prefix=(str(python),'-m','pytest','-q')
    return (TestGroup('main',(*prefix,*('--ignore='+path for path in (*MAINTENANCE_FILES,ORACLE_FILE)))),
            TestGroup('reliable-oracle',(*prefix,ORACLE_FILE)),
            TestGroup('maintenance',(*prefix,*MAINTENANCE_FILES)))


class _Interrupted(BaseException):
    def __init__(self,signum):self.signum=signum


def _subreaper(enabled=None):
    """Temporarily adopt orphan descendants on Linux; retain the caller's setting."""
    if sys.platform != 'linux':
        return None
    import ctypes
    libc = ctypes.CDLL(None, use_errno=True)
    previous = ctypes.c_int()
    if libc.prctl(37, ctypes.byref(previous), 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'Cannot query child subreaper')
    if enabled is not None and libc.prctl(36, int(enabled), 0, 0, 0) != 0:
        raise OSError(ctypes.get_errno(), 'Cannot configure child subreaper')
    return previous.value


def _reap_group(pgid, deadline):
    """Reap only adopted children of this group, after Popen reaped its leader."""
    while time.monotonic() < deadline:
        try:
            pid, _ = os.waitpid(-pgid, os.WNOHANG)
        except ChildProcessError:
            break
        except InterruptedError:
            continue
        if pid == 0:
            break


def _group_exists(pid):
    try:os.killpg(pid,0);return True
    except ProcessLookupError:return False
    except PermissionError:
        # Darwin can report EPERM during group teardown; inspect membership rather
        # than treating an unavailable zero-signal probe as proof of disappearance.
        try:result=subprocess.run(['ps','-axo','pgid=,uid=,stat='],capture_output=True,text=True,timeout=.1)
        except (OSError,subprocess.TimeoutExpired):return True
        if result.returncode:return True
        return any(len(parts)==3 and parts[0].isdigit() and int(parts[0])==pid
                   for line in result.stdout.splitlines() if (parts:=line.split()))


def _signal_group(pid,signum):
    try:os.killpg(pid,signum)
    except (ProcessLookupError,PermissionError):pass


def _cleanup(process,deadline):
    """TERM then KILL the whole owned group; reap leader and allow descendant reaping."""
    started=time.monotonic()
    def reap():
        if process.poll() is not None:
            _reap_group(process.pid, deadline)
    reap()
    if _group_exists(process.pid):
        _signal_group(process.pid,signal.SIGTERM)
        term_until=min(deadline,time.monotonic()+min(.5,max(0,deadline-time.monotonic())/2))
        while time.monotonic()<term_until:
            reap()
            if not _group_exists(process.pid):break
            time.sleep(min(.005,max(0,term_until-time.monotonic())))
        if _group_exists(process.pid):
            _signal_group(process.pid,signal.SIGKILL)
        while time.monotonic()<deadline:
            reap()
            if not _group_exists(process.pid):break
            time.sleep(min(.005,max(0,deadline-time.monotonic())))
    try:process.wait(timeout=max(.001,deadline-time.monotonic()))
    except subprocess.TimeoutExpired:pass
    return {'cleanup_seconds':round(time.monotonic()-started,6),
            'group_alive_after_cleanup':_group_exists(process.pid)}


def _environment():
    return {**os.environ,'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1',
            'VECLIB_MAXIMUM_THREADS':'1','NUMEXPR_NUM_THREADS':'1','TOKENIZERS_PARALLELISM':'false',
            'HF_HUB_DOWNLOAD_WORKERS':'1','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1'}


def run_plan(plan,output_dir,*,group_seconds=240,total_seconds=480):
    """Real subprocess scheduling; narrowed limits never increase configured ceilings."""
    if any(type(value) not in (int,float) or not math.isfinite(value) or not 0<value<=cap
           for value,cap in ((group_seconds,240),(total_seconds,480))):
        raise ValueError('Invalid execution ceiling')
    started=time.monotonic();total_deadline=started+total_seconds
    root=Path(__file__).resolve().parents[1];output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    report={'status':'running','exit_code':1,'limits':{'group_seconds':group_seconds,'total_seconds':total_seconds,'workers':1},
            'planned_groups':[{'name':g.name,'command':list(g.command)} for g in plan],'groups':[]}
    def save():
        report['elapsed_seconds']=round(time.monotonic()-started,6)
        (output_dir/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    previous_reaper=None
    previous={sig:signal.getsignal(sig) for sig in (signal.SIGINT,signal.SIGTERM)}
    requested=[None]
    def interrupted(signum,frame):requested[0]=signum
    def checkpoint():
        if requested[0] is not None:raise _Interrupted(requested[0])
    for sig in previous:signal.signal(sig,interrupted)
    try:
        try:
            previous_reaper=_subreaper(True)
        except OSError:
            report.update(status='failed',exit_code=1,error='subreaper_unavailable')
            save()
            return report
        for group in plan:
            checkpoint()
            current=time.monotonic();group_deadline=min(current+group_seconds,total_deadline)
            reserve=min(1,group_seconds/10,total_seconds/10)
            execution_deadline=group_deadline-reserve
            if current>=execution_deadline:
                report.update(status='timeout',exit_code=1);break
            row={'name':group.name,'command':list(group.command),'status':'running','pid':None,
                 'log':str(output_dir/(group.name+'.log')),'group_alive_after_cleanup':False,'cleanup_seconds':0}
            report['groups'].append(row);process=None
            try:
                with open(row['log'],'w') as log:
                    checkpoint()
                    process=subprocess.Popen(group.command,cwd=root,env=_environment(),stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
                    row['pid']=process.pid
                    checkpoint()
                    while process.poll() is None and time.monotonic()<execution_deadline:
                        time.sleep(min(.02,max(0,execution_deadline-time.monotonic())))
                        checkpoint()
                    checkpoint()
                    if process.poll() is None:
                        row.update(status='timeout',exit_code=1,timeout_kind='total' if total_deadline<=current+group_seconds else 'group')
                    else:
                        row.update(status='passed' if process.returncode==0 else 'failed',exit_code=process.returncode if 0<=process.returncode<126 else 1)
            except OSError:
                row.update(status='failed',exit_code=1,error='spawn_failed')
            except _Interrupted as error:
                row.update(status='interrupted',exit_code=128+error.signum)
            finally:
                if process is not None:
                    row.update(_cleanup(process,min(group_deadline,time.monotonic()+1)))
                    row['returncode']=process.returncode
                row['seconds']=round(time.monotonic()-current,6)
            if row['group_alive_after_cleanup']:
                row.update(status='failed',exit_code=1,error='cleanup_failed')
            if row['status']!='passed':
                report.update(status=row['status'],exit_code=row['exit_code']);save();break
            save()
            checkpoint()
        else:
            report.update(status='passed',exit_code=0)
        if time.monotonic()>total_deadline and report['status']=='passed':report.update(status='timeout',exit_code=1)
        save()
        checkpoint()
        return report
    except _Interrupted as error:
        report.update(status='interrupted',exit_code=128+error.signum)
        save()
        return report
    finally:
        try:
            if previous_reaper is not None:
                _subreaper(previous_reaper)
        except OSError:
            report.update(status='failed',exit_code=1,error='subreaper_restore_failed')
            save()
        finally:
            for sig,handler in previous.items():signal.signal(sig,handler)


def _cap(maximum):
    def parse(value):
        try:number=float(value)
        except ValueError:raise argparse.ArgumentTypeError('Expected a positive bounded number') from None
        if not math.isfinite(number) or not 0<number<=maximum:
            raise argparse.ArgumentTypeError('Expected a positive value no greater than '+str(maximum))
        return number
    return parse


def parse_args(args=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=None)
    parser.add_argument('--group-seconds',type=_cap(240),default=240)
    parser.add_argument('--total-seconds',type=_cap(480),default=480)
    return parser.parse_args(args)


def main(args=None):
    options=parse_args(args)
    output=options.output_dir or Path(tempfile.mkdtemp(prefix='shopextract-tests-'))
    report=run_plan(build_plan(Path(__file__).resolve().parents[1],sys.executable),output,
                    group_seconds=options.group_seconds,total_seconds=options.total_seconds)
    for row in report['groups']:
        lines=Path(row['log']).read_text().splitlines()
        summary=next((line for line in reversed(lines) if ' passed' in line or ' failed' in line),'')
        print(json.dumps({'group':row['name'],'status':row['status'],'seconds':row['seconds'],'summary':summary,'log':row['log']}),flush=True)
    print(json.dumps({'status':report['status'],'seconds':report['elapsed_seconds'],'report':str(output/'report.json')}),flush=True)
    return report['exit_code']


if __name__=='__main__':raise SystemExit(main())
