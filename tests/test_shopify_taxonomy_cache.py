"""Real maintenance source cache and historical replay across runtime credentials."""
import json
import httpx
from tests.test_shopify_taxonomy_pipeline import catalog
from tests.test_shopify_taxonomy_dispatch import STORE,resolver,wire
from tests.test_maintenance_acceptance import NOW
from shopextract.maintenance import MaintenanceStore,MaintenanceEngine,Goal
from shopextract.tools import ToolConfig
from shopextract._models import Platform
from shopextract.categories.contracts import CategoryScope,CategoryRuntimeConfig
from shopextract.categories import categorized_product_from_record
from shopextract.taxonomies.shopify import shopify_taxonomy_options
from shopextract.extractors.shopify_taxonomy import ShopifyStorefrontConfig

async def test_token_change_removal_cache_and_checkpoint_replay(tmp_path,catalog):
    sent=[];responses=wire(sent)
    def response(request):
        if request.method=='POST' and request.headers.get('x-shopify-storefront-access-token')=='B':
            sent.append(request);return httpx.Response(403,json={'errors':[{'message':'Denied'}]})
        return responses(request)
    config=CategoryRuntimeConfig(shopify_taxonomy_options(CategoryScope(Platform.SHOPIFY,STORE),category_ids=['el-6-6'],taxonomy=catalog,allow_unknown_source_version=True))
    store=MaintenanceStore(tmp_path/'cache.db',category_config=config)
    def engine(token):
        storefront=None if token is None else ShopifyStorefrontConfig(STORE+'/api/2026-10/graphql.json',token)
        return MaintenanceEngine(store,tool_config=ToolConfig(allowed_origins=(STORE,)),resolver=resolver,
            wire_transport=httpx.MockTransport(response),utc_now=lambda:NOW,category_config=config,shopify_storefront=storefront)
    goal=Goal(baseline=({'external_id':'101','title':'Laptop','sku':'SKU-1','price':'20','currency':'USD'},),supplier_origin=STORE,
        product_urls=(STORE+'/products/laptop',),profiles={'101':'hardware-v1'},deadline='2026-10-16T10:01:00+00:00')
    async def run(token):
        job=store.create(goal);await engine(token).run(job)
        step=next(s for s in store.steps(job) if s['id'].startswith('extract:'))
        return job,step['result']
    # A prior public cache is legitimate, but Storefront-enabled acquisition must
    # bypass reads as well as writes for the whole acquisition.
    _,public=await run(None);before=len(sent)
    cache_before=[tuple(r) for r in store._connect().execute('SELECT * FROM cache')]
    assert cache_before
    first,authorized=await run('A');assert len(sent)>before
    assert any(m.status=='mapped' for m in categorized_product_from_record(authorized['products'][0]).mappings)
    assert [tuple(r) for r in store._connect().execute('SELECT * FROM cache')]==cache_before
    before=len(sent);_,denied=await run('B');assert len(sent)>before
    assert not any(m.status=='mapped' for m in categorized_product_from_record(denied['products'][0]).mappings)
    assert [tuple(r) for r in store._connect().execute('SELECT * FROM cache')]==cache_before
    # Reopening a committed A job under B is historical replay, no current-token
    # assertion and no new cache write/request.
    before=len(sent);await engine('B').resume(first);assert len(sent)==before
    assert next(s for s in store.steps(first) if s['id'].startswith('extract:'))['result']==authorized
    _,removed=await run(None);assert len(sent)==before and removed==public
    assert not any(m.status=='mapped' for m in categorized_product_from_record(removed['products'][0]).mappings)
