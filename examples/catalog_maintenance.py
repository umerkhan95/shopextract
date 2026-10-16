"""Offline synthetic native-source example: no network, model or store writes.

Run: PYTHONPATH=src python examples/catalog_maintenance.py /tmp/maintenance-example.db
"""
import asyncio
from datetime import datetime,timedelta,timezone
import json
import sys
import httpx
from shopextract.maintenance import Budgets,Goal,MaintenanceEngine,MaintenanceStore
from shopextract.tools import ToolConfig


async def main(path):
    origin='https://supplier.example'
    now=datetime.now(timezone.utc)
    product={'@context':'https://schema.org','@type':'Product','name':'Industrial Sensor','sku':'S1',
        'gtin13':'4006381333931','brand':{'name':'Acme'},'description':'Operating temperature: 0–45 C',
        'offers':{'price':'10','priceCurrency':'EUR'}}
    html='<script type="application/ld+json">'+json.dumps(product)+'</script>'
    async def resolver(host,context):return ['93.184.216.34']
    wire=httpx.MockTransport(lambda request:httpx.Response(200,text=html))
    store=MaintenanceStore(path)
    goal=Goal(baseline=({'external_id':'S1','sku':'S1','gtin':'4006381333931','vendor':'Acme',
        'title':'Industrial Sensor','supplier_id':origin,'description':'Operating temperature: 0–40 C'},),
        supplier_origin=origin,product_urls=(origin+'/products/sensor',),profiles={'S1':'hardware-v1'},
        deadline=(now+timedelta(seconds=30)).isoformat(),budgets=Budgets(requests=3,tokens=0,cost_micros=0))
    engine=MaintenanceEngine(store,tool_config=ToolConfig(allowed_origins=(origin,)),resolver=resolver,
        wire_transport=wire,utc_now=lambda:now)
    try:
        job=store.create(goal)
        result=await engine.run(job)
        assert result['findings'][0]['status']=='proposed_correction'
        assert result['usage']['tokens']==0
        print(json.dumps({'provenance':'synthetic-offline','report':result},ensure_ascii=False,indent=2))
    finally:await engine.close()


if __name__=='__main__':asyncio.run(main(sys.argv[1]))
