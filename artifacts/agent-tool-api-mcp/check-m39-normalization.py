"""Single charged affected canonical-guard check, no continuation receipt mutation."""
import json,signal,time,threading
from pathlib import Path


def main():
    started=time.monotonic()
    def timeout(signum,frame):raise TimeoutError('Affected M39 five-second limit')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,10)
    import pytest,psutil
    from tests.tool_fixture_budget import FixtureBytesPlugin
    process=psutil.Process();baseline=process.memory_info().rss;peak=[0];count=[1];stop=threading.Event()
    def monitor():
        while not stop.wait(.02):
            try:
                children=process.children(recursive=True)
                peak[0]=max(peak[0],process.memory_info().rss+sum(p.memory_info().rss for p in children)-baseline)
                count[0]=max(count[0],1+len(children))
            except (psutil.NoSuchProcess,psutil.AccessDenied):pass
    watcher=threading.Thread(target=monitor,daemon=True);watcher.start();ledger=FixtureBytesPlugin();before=time.monotonic()
    try:
        signal.setitimer(signal.ITIMER_REAL,5)
        code=int(pytest.main(['tests/test_tool_mechanisms.py::test_cross_origin_redirect_no_target_bytes',
            '-q','--tb=short','-p','no:cacheprovider'],plugins=[ledger]))
    finally:signal.setitimer(signal.ITIMER_REAL,0);stop.set();watcher.join(timeout=.1)
    result={'node':'tests/test_tool_mechanisms.py::test_cross_origin_redirect_no_target_bytes','exit':code,
        'case_seconds':time.monotonic()-before,'total_charged_seconds':time.monotonic()-started,
        'actual_fixture_bytes':sum(ledger.counts.values()),'fixture_categories':dict(ledger.counts),
        'peak_additional_rss_bytes':peak[0],'peak_process_count':count[0],
        'resource_overflow':peak[0]>256*1024*1024 or count[0]>5}
    if result['resource_overflow']:result['exit']=1
    Path('artifacts/agent-tool-api-mcp/m39-normalization-affected.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result));return result['exit']


if __name__=='__main__':raise SystemExit(main())
