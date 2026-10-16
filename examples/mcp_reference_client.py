"""Runnable official MCP client. Only calls read-only tools, never Python dispatch."""
import argparse
import asyncio
import json
import sys
import time
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def run(config, url):
    parameters = StdioServerParameters(command=sys.executable,
        args=['-m', 'shopextract.tools', '--config', config])
    async with stdio_client(parameters) as (read, write):
        async with ClientSession(read, write) as client:
            await client.initialize()
            async def call(name, **arguments):
                reply = await client.call_tool(name, {'schema_version':'1.0', **arguments})
                value = reply.structuredContent or json.loads(reply.content[0].text)
                if not value['ok']:
                    raise RuntimeError(value['error']['code']+': '+value['error']['message'])
                return value['data']
            async def job(name, **arguments):
                accepted = await call(name, **arguments)
                deadline = time.monotonic()+35
                while time.monotonic()<deadline:
                    status = await call('job_status', job_id=accepted['job_id'])
                    if status['state']=='succeeded':return accepted['job_id']
                    if status['state'] in {'failed','cancelled','timed_out'}:
                        raise RuntimeError(str(status.get('error',status)))
                    await asyncio.sleep(.05)
                await call('job_cancel',job_id=accepted['job_id'])
                raise RuntimeError('Reference client polling deadline reached')
            discovered = await job('discover',url=url,max_items=2)
            page = await call('job_result',job_id=discovered,collection='urls',page_size=1)
            if not page['items']:raise RuntimeError('No source URL discovered')
            source = page['items'][0]
            catalogs=[];product=None
            for _ in range(2):
                extracted=await job('extract',url=source,max_items=1)
                records=await call('job_result',job_id=extracted,collection='products',page_size=1)
                if not records['items']:raise RuntimeError('Source has no supported product')
                product=records['items'][0];catalogs.append(records['metadata']['catalog_handle'])
            matched=await job('match',left_catalog=catalogs[0],right_catalog=catalogs[1])
            matches=await call('job_result',job_id=matched,collection='matches',page_size=1)
            evidence_ids=product['field_evidence'].get('/price', product['evidence_ids'])
            if not evidence_ids:raise RuntimeError('No captured support available')
            evidence=await call('evidence',owner=product['owner_handle'],evidence_id=evidence_ids[0])
            # Optional configured-capture report; inputs come from operator-granted resource.
            resource=await client.read_resource('shopextract://session')
            grants=json.loads(resource.contents[0].text)['captures']
            changes=None
            if len(grants)>=2:
                report=await job('changes',previous_capture=grants[0]['capture_handle'],current_capture=grants[1]['capture_handle'])
                changes=await call('job_result',job_id=report,collection='events',page_size=20)
            # Runnable documented structured error, no forbidden source request is sent.
            invalid=await client.call_tool('discover',{'schema_version':'9.0','url':url})
            print(json.dumps({'source':source,'matches':matches,'evidence':evidence,
                'changes':changes,'version_error':invalid.structuredContent},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--config',required=True);parser.add_argument('--url',required=True)
    args=parser.parse_args()
    asyncio.run(asyncio.wait_for(run(args.config,args.url),timeout=120))
