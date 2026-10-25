"""Controlled maintenance transport only; production CLI/engine/store untouched."""
import asyncio
from pathlib import Path
import os
from shopextract.maintenance.engine import MaintenanceEngine
from shopextract.cli import main
import httpx

original=MaintenanceEngine.__init__
async def resolver(host,context):return ['93.184.216.34']
async def slow(request):
    Path(os.environ['CLI_WIRE_ENTERED']).write_text('controlled external transport entered')
    await asyncio.sleep(20)
    return httpx.Response(200,text='<html/>')
def configured(self,*args,**kwargs):
    kwargs.update(resolver=resolver,wire_transport=httpx.MockTransport(slow))
    original(self,*args,**kwargs)
MaintenanceEngine.__init__=configured
if __name__=='__main__':main()
