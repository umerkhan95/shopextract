"""Bounded schema/inventory design checks; never execute CLI/domain runtime."""
import copy,json,pathlib
from jsonschema import Draft202012Validator
b=pathlib.Path('specs/011-cli-feature-parity/p0')
load=lambda n:json.loads((b/n).read_text())
s=load('response.schema.json');Draft202012Validator.check_schema(s);v=Draft202012Validator(s)
c=load('contracts.json');checks=[]
def check(name,envelope,expected):
 actual=v.is_valid(envelope);checks.append({'name':name,'expected_valid':expected,'actual_valid':actual})
 assert actual==expected,name
success={'schema_version':'1.0','ok':True,'data':[],'warnings':[],'error':None,'completeness':'complete'}
check('success',success,True)
for code,retryable in c['error_retryable'].items():
 env={'schema_version':'1.0','ok':False,'data':[] if code=='E_PARTIAL' else None,'warnings':[],'error':{'code':code,'message':'sanitized','retryable':retryable},'completeness':'partial' if code=='E_PARTIAL' else 'unavailable'}
 check(code+' positive',env,True)
 wrong=copy.deepcopy(env);wrong['error']['retryable']=not retryable;check(code+' retryability inverse',wrong,False)
for witness in load('evidence/reviewer-design-checks.json')['checks']:
 check('reviewer witness: '+witness['name'],witness['envelope'],False)
m=load('capability-manifest.json');lookup={item['path']:item for item in m['modules']}
expected={
 'src/shopextract/maintenance/engine.py':{'MaintenanceEngine.now':'python_only','MaintenanceEngine.hook':'python_only','MaintenanceEngine.close':'composed_helper','MaintenanceEngine.run':'workflow'},
 'src/shopextract/maintenance/store.py':{'MaintenanceStore.acquire':'composed_helper','MaintenanceStore.release':'composed_helper','MaintenanceStore.close':'composed_helper'},
 'src/shopextract/tools/runtime.py':{'ToolRuntime.aclose':'composed_helper','ToolRuntime.bootstrap':'composed_helper','ToolRuntime.call':'workflow'},
 'src/shopextract/_evidence.py':{'TrustContract.validate':'composed_helper'},
 'src/shopextract/tools/contracts.py':{'validate':'composed_helper'},
 'src/shopextract/categories/config.py':{'validate_options':'composed_helper','runtime_record':'composed_helper','runtime_from_record':'composed_helper','options_digest':'composed_helper'}}
for path,names in expected.items():
 for name,kind in names.items():assert name in lookup[path]['definitions'][kind],(path,name,kind)
count=0
for item in m['modules']:
 for name in item['definitions'].get('workflow',[]):
  link=item['definition_links'][name];assert all(link[x] for x in ['phase','target','rationale']);count+=1
 if '/extractors/' in item['path']:assert not item['definitions'].get('workflow'),item['path']
assert len(c['bootstrap_cases'])==15
result={'schema_examples':checks,'schema_examples_passed':len(checks),'classified_workflow_links':count,'named_classification_checks':sum(map(len,expected.values())),'bootstrap_cases_designed':15,'bootstrap_runtime_cases_executed':0,'runtime_acceptance':'not_run','scope':'Design schema/classification checks only; no production runtime mechanism exercised.','actual_session_token_counters':'unavailable'}
(b/'evidence/author-repair-checks.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='schema_examples'}))
