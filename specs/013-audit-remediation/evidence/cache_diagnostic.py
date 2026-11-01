import asyncio,tempfile,json
from tests.test_maintenance_acceptance import Harness,goal
async def run():
 h=Harness(tempfile.mktemp(suffix='.db'),category='Shoes');key,_=await h.run(goal())
 print(json.dumps([{'kind':s['kind'],'diagnostics':(s['result'] or {}).get('diagnostics')} for s in h.store.steps(key) if s['kind']=='extract']))
 h.store.close()
if __name__=='__main__':asyncio.run(run())
