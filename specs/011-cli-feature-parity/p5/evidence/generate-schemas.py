import json,dataclasses,typing,types,enum,shutil
from pathlib import Path
from shopextract.tools.runtime import Limits,TOOL_NAMES
from shopextract.maintenance import Budgets
p=Path('src/shopextract/schemas')
def obj(props,required=()):return dict(type='object',properties=props,required=list(required),additionalProperties=False)
def arr(items,**kw):return dict(type='array',items=items,**kw)
s={'type':'string','minLength':1}
def type_schema(t):
 o=typing.get_origin(t);a=typing.get_args(t)
 if t is typing.Any:return {}
 if o in (typing.Union,types.UnionType):return {'anyOf':[type_schema(v) for v in a]}
 if o is typing.Literal:return {'enum':list(a)}
 if o in (tuple,list):return arr(type_schema(a[0]) if a else {})
 if o is dict or o in (typing.Mapping, __import__('collections.abc').abc.Mapping):return {'type':'object','additionalProperties':type_schema(a[1])}
 if dataclasses.is_dataclass(t):
  hints=typing.get_type_hints(t)
  return obj({f.name:type_schema(hints[f.name]) for f in dataclasses.fields(t)},[f.name for f in dataclasses.fields(t) if f.default is dataclasses.MISSING and f.default_factory is dataclasses.MISSING])
 if isinstance(t,type) and issubclass(t,enum.Enum):return {'enum':[v.value for v in t]}
 return {'type':{str:'string',int:'integer',float:'number',bool:'boolean',type(None):'null'}.get(t,'object')}
def save(name,value,version='1.0',kind='file'):
 value={'$schema':'https://json-schema.org/draft/2020-12/schema','title':'ShopExtract '+name,'x-contract-version':version,**value}
 (p/(name+'.schema.json')).write_text(json.dumps(value,indent=2)+'\n');index.append(dict(name=name,version=version,kind=kind))
index=[]
for name in ('response','config'):
 value=json.load(open('specs/011-cli-feature-parity/p0/'+name+'.schema.json'));save(name,value,'1' if name=='config' else '1.0')
maxima={'requests':1000,'products':1000,'tokens':1000000,'cost_micros':1000000000,'input_bytes':262144,'evidence_bytes':16777216,'report_bytes':2097152,'attempt_seconds':120}
budget=obj({f.name:{'type':'number' if f.name=='attempt_seconds' else 'integer','minimum':0 if f.name!='attempt_seconds' else 1e-12,'maximum':maxima[f.name],'default':f.default} for f in dataclasses.fields(Budgets)})
save('maintenance-goal',obj({'schema_version':{'const':'1.0'},'baseline':arr({'type':'object'},maxItems=1000),'supplier_origin':s,'product_urls':arr(s,maxItems=1000,uniqueItems=True),'deadline':{'type':'string','format':'date-time'},'fields':arr(s,minItems=1,uniqueItems=True),'profiles':{'type':'object','additionalProperties':s},'baseline_mode':{'enum':['supplied','captured']},'budgets':budget,'freshness_seconds':{'type':'number','minimum':0,'maximum':86400}},('schema_version','baseline','supplier_origin','product_urls','deadline')))
rule=obj({'kind':{'enum':['text','decimal','mass']},'role':{'enum':['comparable','identity_variant','price_context']},'normalization':{'enum':['exact','decimal','mass_kg']}},('kind','role'))
save('maintenance-profiles',obj({'schema_version':{'type':'integer','const':1},'profiles':{'type':'object','additionalProperties':{'type':'object','additionalProperties':rule}}},('schema_version','profiles')),'1')
limits=obj({f.name:{'type':'integer' if type(f.default) is int else 'number','exclusiveMinimum':0,'maximum':f.default,'default':f.default} for f in dataclasses.fields(Limits)})
limits['properties']['active_jobs']['const']=1
save('tool-operator',obj({'allowed_origins':arr(s),'allowed_tools':arr({'enum':list(TOOL_NAMES)},uniqueItems=True),'captures':arr(obj({'alias':s,'db_path':s,'snapshot_id':{'type':'integer','minimum':1},'supplier':s},('alias','db_path','snapshot_id','supplier'))),'limits':limits}),'native-unversioned')
step=obj({'id':{'type':'string','pattern':'^[A-Za-z][A-Za-z0-9_-]{0,63}$'},'tool':{'enum':[*TOOL_NAMES,'bootstrap','poll','pages']},'arguments':{'type':'object'}},('id','tool','arguments'))
step['description']='arguments follow native tool input schema (schema show tool:NAME), or helper contracts documented in docs/cli.md. Values may be whole {$ref:"earlier-id#/json/pointer"} objects; references resolve against earlier step result. Native input validation follows resolution.'
save('tool-session',obj({'schema_version':{'const':'1.0'},'steps':arr(step,minItems=1,maxItems=32)},('schema_version','steps')))
from shopextract.categories.contracts import CategoryOptions,CategoryRuntimeConfig
save('category-options',type_schema(CategoryOptions),'native')
save('category-runtime',type_schema(CategoryRuntimeConfig),'native')
# Catalog is a transport union; nested portable semantic validation remains native.
portable=obj({'schema_version':{'type':'integer','const':1},'product':{'type':'object'},'evidence_contract':{'type':['object','null']},'variant_contracts':arr({'type':['object','null']}),'evidence_availability':arr({'type':'object'}),'variant_evidence_availability':arr({})},('schema_version','product','evidence_contract','variant_contracts'))
save('portable-product',portable,'1')
save('catalog',{'description':'Flat object arrays or native portable arrays; extraction result envelope data.products also accepted. Categorized native record/runtime envelopes use the native category codec; see docs/cli.md. Native codecs validate complete Product fields, Decimal tags, evidence binding and policy digest.', 'anyOf':[arr({'type':'object'},maxItems=1000),{'type':'object','required':['schema_version','data'],'properties':{'schema_version':{'const':'1.0'},'data':{'type':'object','required':['products'],'properties':{'products':arr({'type':'object'},maxItems=1000)}}}},{'type':'object','required':['schema_version','products'],'properties':{'schema_version':{'type':'integer','const':1},'products':arr({'type':'object'},maxItems=1000)}}]})
(p/'index.json').write_text(json.dumps(index,indent=2)+'\n')
# Exact CLI-specific opt-in configuration and dataset contracts.
save('storefront',obj({key:{'type':'string'} for key in ('endpoint','access_token','protocol','token_type','customer_access_token','customer_id')}),'native')
save('publisher-aliases',obj({'schema_version':{'type':'integer','const':1},'publisher_aliases':{'type':'object','maxProperties':1000,'additionalProperties':arr(s,minItems=1,maxItems=100)}},('schema_version','publisher_aliases')),'1')
save('semantic-candidates',obj({'schema_version':{'type':'integer','const':1},'semantic_candidates':arr(arr({'type':'integer','minimum':0,'maximum':999},maxItems=1000),maxItems=1000)},('schema_version','semantic_candidates')),'1')
save('resolution-policy',obj({'schema_version':{'type':'integer','const':1},'offer_max_age_seconds':{'type':'integer','minimum':1,'maximum':31536000},'specification_max_age_seconds':{'type':'integer','minimum':1,'maximum':31536000}},('schema_version',)),'1')
from shopextract.compare import MatchRelation
save('matching-evaluation',arr(obj({'id':{'type':'string'},'a':{'type':'object'},'b':{'type':'object'},'label':{'enum':[r.value for r in MatchRelation]}},('id','a','b','label')),maxItems=1000))
from shopextract.categories.woo_tree import WooTreeLimits
save('tree-limits',type_schema(WooTreeLimits),'native')
# Conditional closed step arguments, with whole-value previous-result references.
from shopextract.tools.contracts import schema as native_schema
ref=obj({'$ref':{'type':'string','pattern':r'^[A-Za-z][A-Za-z0-9_-]{0,63}#(?:/.*)?$'}},('$ref',))
conditions=[]
for tool in [*TOOL_NAMES,'bootstrap','poll','pages']:
 if tool in TOOL_NAMES:shape=native_schema(tool)['inputSchema']
 elif tool=='bootstrap':shape=obj({})
 elif tool=='poll':shape=obj({'job_id':s,'interval_seconds':{'type':'number','minimum':.01,'maximum':1}},('job_id',))
 else:shape=obj({'job_id':s,'collection':s,'page_size':{'type':'integer','minimum':1,'maximum':100},'cursor':s,'max_pages':{'type':'integer','minimum':1,'maximum':10}},('job_id','collection'))
 shape=json.loads(json.dumps(shape))
 for name,prop in list(shape['properties'].items()):
  if name!='schema_version':shape['properties'][name]={'anyOf':[prop,ref]}
 conditions.append({'if':{'properties':{'tool':{'const':tool}}},'then':{'properties':{'arguments':shape}}})
path=p/'tool-session.schema.json';session=json.loads(path.read_text());session['properties']['steps']['items']['allOf']=conditions;path.write_text(json.dumps(session,indent=2)+'\n')
# Native categorized inputs do not have a fabricated file-level version field.
path=p/'catalog.schema.json';catalog=json.loads(path.read_text());catalog['anyOf'][-1]={'type':'object','required':['categorized_products'],'properties':{'categorized_products':arr({'type':'object'},maxItems=1000),'products':arr({'type':'object'},maxItems=1000),'config':type_schema(CategoryRuntimeConfig),'policy_digest':s}}
path.write_text(json.dumps(catalog,indent=2)+'\n')
(p/'index.json').write_text(json.dumps(index,indent=2)+'\n')
