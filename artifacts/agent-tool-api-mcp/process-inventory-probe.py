"""One bounded process-tree observation, not stress or live source verification."""
import asyncio,json,os,sys,time
from pathlib import Path
import psutil
from mcp import ClientSession,StdioServerParameters
from mcp.client.stdio import stdio_client
from tests.tool_api_fixtures import runtime,ORIGIN

async def wait_job(call):
    job=await call('extract',{'schema_version':'1.0','url':ORIGIN+'/products/widget','max_items':1})
    for _ in range(150):
        status=await call('job_status',{'schema_version':'1.0','job_id':job['data']['job_id']})
        if status['data']['state']=='succeeded':return
        if status['data']['state'] in {'failed','cancelled','timed_out'}:raise RuntimeError('Controlled process probe failed')
        await asyncio.sleep(.02)
    raise TimeoutError('Probe polling limit')

async def main():
    root=Path(__file__).resolve().parents[2];parent=psutil.Process();snapshots=[];done=asyncio.Event()
    async def observe():
        while not done.is_set():
            rows=[{'pid':parent.pid,'role':'client'}]
            for child in parent.children(recursive=True):
                try:
                    command=' '.join(child.cmdline())
                    role='resource_tracker' if 'resource_tracker' in command else 'mcp_server' if 'mcp_fixture_server' in command else 'auxiliary_worker'
                    rows.append({'pid':child.pid,'ppid':child.ppid(),'role':role})
                except psutil.NoSuchProcess:pass
            snapshots.append(rows)
            await asyncio.sleep(.02)
    monitor=asyncio.create_task(observe())
    try:
        engine=runtime()
        try:await wait_job(engine.call)
        finally:await engine.aclose()
        parameters=StdioServerParameters(command=sys.executable,args=['-m','tests.mcp_fixture_server'],cwd=str(root),
            env={**os.environ,'PYTHONPATH':str(root/'src')+os.pathsep+str(root)})
        async with stdio_client(parameters) as (read,write):
            async with ClientSession(read,write) as client:
                await client.initialize()
                async def call(name,args):return (await client.call_tool(name,args)).structuredContent
                await wait_job(call)
        await asyncio.sleep(.2)
    finally:done.set();await monitor
    maximum=max(snapshots,key=len)
    final=snapshots[-1]
    print(json.dumps({'maximum_count':len(maximum),'maximum_inventory':maximum,
        'after_runtime_and_server_close':final,
        'note':'Client-owned tracker can persist until client interpreter exits; no active auxiliary worker after close. Trackers are counted support processes, not inference.'},indent=2))

if __name__=='__main__':asyncio.run(asyncio.wait_for(main(),timeout=12))
