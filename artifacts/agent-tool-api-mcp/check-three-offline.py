"""One affected-only offline run; not a driver continuation or per-case stress proof."""
import json,time,threading,signal
from pathlib import Path

def main():
 start=time.monotonic()
 def stop_timeout(*args):raise TimeoutError('Affected-only 42s internal deadline')
 signal.signal(signal.SIGALRM,stop_timeout);signal.setitimer(signal.ITIMER_REAL,42)
 import pytest,psutil
 from tests.tool_fixture_budget import FixtureBytesPlugin
 caller=psutil.Process();baseline=caller.memory_info().rss;peak=[0];count=[1];stop=threading.Event()
 def monitor():
  while not stop.wait(.02):
   try:
    children=caller.children(recursive=True);peak[0]=max(peak[0],caller.memory_info().rss+sum(p.memory_info().rss for p in children)-baseline);count[0]=max(count[0],1+len(children))
   except (psutil.NoSuchProcess,psutil.AccessDenied):pass
 watcher=threading.Thread(target=monitor,daemon=True);watcher.start();ledger=FixtureBytesPlugin()
 nodes=['tests/test_tool_mechanisms.py::'+n for n in ['test_real_changes_replay_and_capture_grants','test_supported_empty_distinct_from_backend_failure','test_feed_static_real_parser_and_evidence']]
 try:code=int(pytest.main(nodes+['-q','--tb=short','-p','no:cacheprovider'],plugins=[ledger]))
 finally:signal.setitimer(signal.ITIMER_REAL,0);stop.set();watcher.join(timeout=.1)
 result={'nodes':nodes,'exit':code,'total_charged_seconds':time.monotonic()-start,'actual_fixture_bytes':sum(ledger.counts.values()),'fixture_categories':dict(ledger.counts),'peak_additional_rss_bytes':peak[0],'peak_process_count':count[0],'resource_overflow':peak[0]>256*1024*1024 or count[0]>5,'scope':'affected-only offline evidence; no five-second per-case stress claims'}
 Path('artifacts/agent-tool-api-mcp/three-offline-affected.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result));return code
if __name__=='__main__':raise SystemExit(main())
