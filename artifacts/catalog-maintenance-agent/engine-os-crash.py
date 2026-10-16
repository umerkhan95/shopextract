"""Selected SC04/05 OS-death checks; controlled HTTP, real native engine/SQLite."""
import asyncio
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from tests.test_maintenance_acceptance import Harness,goal
from tests.maintenance_process_guard import run_group


async def worker(db,key,event):
    def die(actual,payload):
        if actual==event:os._exit(91)
    h=Harness(db,failure_hook=die)
    await h.engine.run(key)
    raise AssertionError('OS fault boundary not reached')


async def resume(db,key,event):
    h=Harness(db);report=await h.engine.resume(key)
    assert h.requests==[]
    if event=='after_checkpoint':
        assert report['findings'][0]['status']=='proposed_correction'
    else:assert report['state']=='partial' and report['usage']['unknown_requests']==2
    return {'state':report['state'],'usage':report['usage'],'restart_requests':len(h.requests)}


def main():
    started=time.monotonic();results=[];out=Path(__file__).parent
    with tempfile.TemporaryDirectory(prefix='engine-os-crash-') as temporary:
        for event in ('before_checkpoint','after_checkpoint'):
            db=Path(temporary)/(event+'.db');h=Harness(db);key=h.store.create(goal());h.store.close()
            with (out/('os-crash-'+event+'.log')).open('w') as log:
                execution=run_group([sys.executable,__file__,'--worker',str(db),key,event],timeout=10,stdout=log,stderr=log)
            assert execution['returncode']==91 and not execution['timed_out'],execution
            result=asyncio.run(resume(db,key,event));result.update(window=event,os_exit=91,execution=execution)
            results.append(result)
    summary={'state':'passed','provenance':'synthetic-controlled-http','cases':results,'seconds':time.monotonic()-started}
    (out/'engine-os-crash.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary))


if __name__=='__main__':
    if len(sys.argv)>1 and sys.argv[1]=='--worker':asyncio.run(worker(Path(sys.argv[2]),sys.argv[3],sys.argv[4]))
    else:main()
