import asyncio,json,traceback
from shopextract.tools.execution import OwnedProcess
from shopextract.tools.domain import synchronous
from shopextract.tools.contracts import encoded
from tests.test_tool_native_modes import test_native_mode_guarded_parser_and_retained_evidence

async def direct(self,kind,payload,context):
    if kind != 'domain':raise RuntimeError('Unexpected real DNS')
    try:return encoded(synchronous(json.loads(payload)))
    except Exception:
        traceback.print_exc()
        raise

from shopextract.tools.domain import DomainAdapter
original_execute = DomainAdapter.execute
async def diagnostic_execute(self,*args):
    try:return await original_execute(self,*args)
    except Exception:
        traceback.print_exc()
        raise
DomainAdapter.execute=diagnostic_execute

from shopextract.tools.state import SessionStore
original_publish=SessionStore.publish
def diagnostic_publish(self,*args):
    try:return original_publish(self,*args)
    except Exception:
        traceback.print_exc()
        raise
SessionStore.publish=diagnostic_publish

async def main():
    original=OwnedProcess.run
    OwnedProcess.run=direct
    try:
        for platform in ('shopify','magento','shopware','bigcommerce'):
            print('DIAGNOSIS',platform,flush=True)
            try:await test_native_mode_guarded_parser_and_retained_evidence(platform)
            except Exception:traceback.print_exc()
    finally:OwnedProcess.run=original

asyncio.run(main())
