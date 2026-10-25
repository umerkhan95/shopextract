"""Small synthetic source fixtures; real parser, support, matcher and SQLite paths."""
from dataclasses import asdict
from datetime import datetime,timedelta,timezone
import json
from shopextract._capture import capture
from shopextract._models import Platform
from shopextract._normalize import normalize
from shopextract._portable import product_to_record
from shopextract.categories import CategoryOptions,CategoryRuntimeConfig,CategoryScope,TargetRegistry,MappingRule,CategorySelector,normalize_with_categories,categorized_product_to_record
from shopextract.extractors._schema_org import SchemaOrgExtractor
from shopextract.maintenance import MaintenanceStore,MaintenanceEngine,Goal
from shopextract.tools import ToolConfig

ORIGIN='https://synthetic-profile.invalid'
NOW=datetime(2026,10,25,12,tzinfo=timezone.utc)


def raw_product(**changes):
    data={'@type':'Product','name':'Synthetic refrigerator','sku':'S1','gtin13':'4006381333931','brand':{'name':'Acme'},'model':'FX250','category':'Refrigerators','offers':{'price':'250','priceCurrency':'EUR'},'additionalProperty':[{'name':'Total capacity','value':'250 L'},{'name':'Product width','value':'60 cm'},{'name':'Product height','value':'180 cm'},{'name':'Product depth','value':'65 cm'}]}
    data.update(changes)
    html='<script type="application/ld+json">'+json.dumps(data,allow_nan=False)+'</script>'
    raw=SchemaOrgExtractor.extract_from_html(html,ORIGIN+'/products/S1')[0]
    capture(raw,ORIGIN+'/products/S1','json_ld',observed_at=NOW)
    return raw


def policy(*,binding=True,bound_profile='refrigerator-v1',label='Refrigerators'):
    options=CategoryOptions(CategoryScope(Platform.GENERIC,ORIGIN),TargetRegistry('shopify:product-taxonomy','2026-08',('hg-11-7-41',)),(MappingRule('exact-fridge','1',CategorySelector('schema.org:category',None,raw_label=label,allow_unknown_version=True),('hg-11-7-41',)),))
    return CategoryRuntimeConfig(options,(('hg-11-7-41',bound_profile),) if binding else ())


def normalized(raw,*,enrich=True,config=None):
    if config:
        return normalize_with_categories(raw,Platform.GENERIC,ORIGIN,category_options=config.options,include_refrigerator_attributes=enrich)
    return normalize(raw,Platform.GENERIC,ORIGIN,include_refrigerator_attributes=enrich)


def configured_goal(*,fields=('attributes/capacity',),profiles=None,baseline=None):
    left={'external_id':'S1','title':'Synthetic refrigerator','sku':'S1','gtin':'4006381333931','vendor':'Acme','supplier_id':ORIGIN,'attributes':{'capacity':{'value':'250 L','semantic':'total_volume'},'model':'FX250'}}
    if baseline:left.update(baseline)
    return Goal(baseline=(left,),supplier_origin=ORIGIN,product_urls=(ORIGIN+'/products/S1',),fields=fields,profiles={'S1':'refrigerator-v1'} if profiles is None else profiles,deadline=(NOW+timedelta(minutes=2)).isoformat())


async def reconcile(path,*,raw=None,config=None,goal=None,clock=NOW):
    """Direct real comparison checkpoint; the separate run test covers source routing."""
    store=MaintenanceStore(path,category_config=config)
    value=normalized(raw or raw_product(),config=config)
    record=categorized_product_to_record(value) if config else product_to_record(value)
    job=store.create(goal or configured_goal());store.acquire();store.begin(job,now=clock)
    engine=MaintenanceEngine(store,tool_config=ToolConfig(),category_config=config,utc_now=lambda:clock)
    # Source acquisition is intentionally omitted in this comparison-only fixture;
    # restore its trusted context from the REAL immutable creation-time snapshot.
    if config:
        from shopextract.categories.config import runtime_from_record
        engine._category_config=runtime_from_record(json.loads(store.category_policy(job).config_json))
    await engine._reconcile(job,store.goal(job),[record]);store.finish(job,'completed')
    result=store.report(job,include_profile_coverage=True)
    await engine.close();store.close()
    return result
