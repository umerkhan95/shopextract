"""Fixed small P01 timings; no exhaustive sweep, HTTP, model or source import."""
import hashlib,json,resource,subprocess,sys,time
from pathlib import Path
from shopextract._capture import capture
from shopextract._models import Platform
from shopextract.categories import categorized_product_to_record,categorized_product_from_record
from shopextract.taxonomies.shopify import load_shopify_taxonomy,normalize_with_shopify_taxonomy

ROOT=Path(__file__).resolve().parents[1]

def steady_rss():
    # Darwin ps KiB; report availability explicitly on other environments.
    try:return int(subprocess.check_output(['ps','-o','rss=','-p',str(__import__('os').getpid())],text=True).strip())*1024
    except Exception:return None

if __name__=='__main__':
    label=sys.argv[1];start=time.perf_counter()
    catalog=load_shopify_taxonomy(catalog_root=ROOT/'build/shopify-taxonomy/catalogs')
    result={'label':label,'cold_load_seconds':time.perf_counter()-start,'steady_after_load_bytes':steady_rss()}
    nodes=list(catalog.iter_categories());chosen=[nodes[0],catalog.category('el-6-6')]+nodes[100:198]
    start=time.perf_counter()
    for _ in range(100):load_shopify_taxonomy(catalog_root=ROOT/'build/shopify-taxonomy/catalogs')
    result['warm_load_100_seconds']=time.perf_counter()-start
    start=time.perf_counter()
    for _ in range(1000):
        catalog.category('el-6-6');catalog.attribute('color');catalog.value('color__blue')
    result['warm_lookups_3000_seconds']=time.perf_counter()-start
    start=time.perf_counter()
    for node in chosen:catalog.attributes_for(node.id)
    result['context_100_seconds']=time.perf_counter()-start
    signatures=[];values=[]
    for size in (10,100):
        start=time.perf_counter()
        for node in chosen[:size]:
            raw=capture({'id':101,'title':'Controlled Δ item > /','handle':'controlled','variants':[],
                'category':{'id':node.id,'name':node.name}},'https://merchant.test/products/controlled','synthetic_fixture',observed_at='2026-10-18T00:00:00+00:00')
            value=normalize_with_shopify_taxonomy(raw,platform=Platform.SHOPIFY,shop_url='https://merchant.test',taxonomy=catalog,allow_unknown_source_version=True)
            schema=catalog.schema_for(value)
            assert schema.resolved[0].category==node
            signatures.append([node.id,[[b.base_attribute_id,b.handle,b.value_ids] for b in schema.resolved[0].attributes],[(m.status,m.target_ids) for m in value.mappings]])
            if size==10:values.append(value)
        result[f'normalize_schema_{size}_seconds']=time.perf_counter()-start
    start=time.perf_counter()
    for value in values:
        record=categorized_product_to_record(value)
        assert categorized_product_to_record(categorized_product_from_record(record))==record
    result['codec_roundtrip_10_seconds']=time.perf_counter()-start
    result.update(peak_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,steady_end_bytes=steady_rss(),
        fingerprint=catalog.fingerprint,semantic_sha256=hashlib.sha256(json.dumps(signatures,sort_keys=True,ensure_ascii=False).encode()).hexdigest(),http_requests=0,
        forecast_14606_seconds=round(result['normalize_schema_100_seconds']/100*14606,3),state='passed')
    from shopextract import _portable
    if hasattr(_portable,'schema_hints'):result['schema_cache']=str(_portable.schema_hints.cache_info())
    (ROOT/f'artifacts/shopify-taxonomy/performance-{label}.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
