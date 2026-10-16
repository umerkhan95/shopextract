"""One affected M11 check in the warm state it has after M01–M10; no driver resume."""
import json,signal,threading,time
from pathlib import Path


def main():
    started=time.monotonic()
    def timeout(signum,frame):raise TimeoutError('Affected check five-second case limit')
    signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,12)
    import pytest,psutil
    parent=psutil.Process();baseline=parent.memory_info().rss;peak=[0];count=[1];stop=threading.Event()
    def monitor():
        while not stop.wait(.02):
            try:
                children=parent.children(recursive=True)
                peak[0]=max(peak[0],parent.memory_info().rss+sum(p.memory_info().rss for p in children)-baseline)
                count[0]=max(count[0],1+len(children))
            except (psutil.NoSuchProcess,psutil.AccessDenied):pass
    watcher=threading.Thread(target=monitor,daemon=True);watcher.start()
    try:
        # These modules were already loaded by the ten completed driver cases.
        import tests.test_agent_tool_api
        from tests.tool_fixture_budget import FixtureBytesPlugin
        ledger=FixtureBytesPlugin();before=time.monotonic()
        signal.setitimer(signal.ITIMER_REAL,5)
        code=int(pytest.main(['tests/test_agent_tool_api.py::test_complete_domain_flow_uses_native_code_paths',
                             '-q','--tb=short','-p','no:cacheprovider'],plugins=[ledger]))
        elapsed=time.monotonic()-before
    finally:
        signal.setitimer(signal.ITIMER_REAL,0);stop.set();watcher.join(timeout=.1)
    result={'node':'tests/test_agent_tool_api.py::test_complete_domain_flow_uses_native_code_paths',
        'exit':code,'case_seconds':elapsed,'total_charged_seconds':time.monotonic()-started,
        'actual_fixture_bytes':sum(ledger.counts.values()),'fixture_categories':dict(ledger.counts),
        'peak_additional_rss_bytes':peak[0],'peak_process_count':count[0],
        'resource_overflow':peak[0]>256*1024*1024 or count[0]>5,
        'original_driver_receipt_modified':False}
    if result['resource_overflow']:result['exit']=1
    Path('artifacts/agent-tool-api-mcp/m11-cache-affected.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result));return result['exit']


if __name__=='__main__':raise SystemExit(main())
