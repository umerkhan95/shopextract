"""Controlled real public acquisition→supplement→normalize→schema timing, no network."""
import asyncio,json,time
from pathlib import Path
from unittest.mock import patch
import httpx
from shopextract.taxonomies.shopify import load_shopify_taxonomy,extract_with_shopify_taxonomy
from shopextract.extractors.shopify_taxonomy import ShopifyStorefrontConfig
from tests.test_shopify_taxonomy_dispatch import STORE,wire

async def main():
    catalog=load_shopify_taxonomy(catalog_root=Path('build/shopify-taxonomy/catalogs'))
    sent=[];original=httpx.AsyncClient
    config=ShopifyStorefrontConfig(STORE+'/api/2026-10/graphql.json',auth_mode='tokenless')
    start=time.perf_counter()
    with patch.object(httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(wire(sent)),**kw)):
        for _ in range(10):
            result=await extract_with_shopify_taxonomy(STORE,taxonomy=catalog,storefront=config,allow_unknown_source_version=True)
            assert len(result.products)==1 and catalog.schema_for(result.products[0]).resolved
    seconds=time.perf_counter()-start
    assert len(sent)==20 and sum(r.method=='POST' for r in sent)==10
    record={'state':'passed','operations':10,'seconds':seconds,'mean_operation_ms':seconds*100,'requests':20,
        'provenance':'controlled MockTransport real producer/public dispatch/normalizer/strict schema; excludes real merchant network latency',
        'llm_calls':0,'catalog_reused':True}
    Path('artifacts/shopify-taxonomy/performance-native.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))

if __name__=='__main__':asyncio.run(asyncio.wait_for(main(),30))
