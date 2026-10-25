"""Reconcile frozen public inventory with actual installed grammar and new definitions."""
import ast,hashlib,json
from pathlib import Path
from shopextract.cli import main
from shopextract._cli_discovery import command_inventory
base=Path('specs/011-cli-feature-parity');saved=json.loads((base/'p0/capability-manifest.json').read_text())
exact={}
def bind(names,command):
 for name in names.split():exact[name]=command
for names,command in [
 ('detect','detect'),('discover','discover'),('extract','extract'),('extract_one','extract-one'),('from_feed','feed'),('normalize','normalize'),
 ('QualityScorer.score_product QualityScorer.score_batch','quality'),('factual_paths trust_view','evidence inspect'),('resolve_fields resolution_references','resolve'),
 ('price_position','competitive position'),('assortment_gaps','competitive gaps'),('brand_coverage','competitive brands'),('analyze_products','analyze-file'),('price_distribution','stats distribution'),('outliers','stats outliers'),('brand_breakdown','stats brands'),('analyze','analyze'),
 ('normalize_with_categories','categories normalize'),('extract_with_categories','categories extract'),('map_categories','categories map'),('validate_observations','categories validate'),('fetch_woocommerce_category_tree','categories tree fetch'),('link_tree_memberships','categories tree link'),
 ('compare_catalogs','compare-catalogs'),('evaluate_matching','match-evaluate'),('normalized_attributes','identity inspect'),('classify_match','match-pair'),('match_products fuzzy_match','match'),('match_gtin','match-gtin'),('compare','compare'),('to_csv to_json to_feed to_parquet','export'),
 ('create_evidence_bundle write_evidence_bundle','evidence bundle create'),('load_evidence_bundle read_evidence_bundle','evidence bundle load'),('create_evidence_sidecar','evidence sidecar create'),('load_evidence_sidecar','evidence sidecar load'),('assign_identity','identity assign'),('migrate_snapshot_identities','identity migrate'),
 ('MaintenanceEngine.run','maintenance run'),('MaintenanceEngine.resume','maintenance resume'),('MaintenanceEngine.retry_unknown','maintenance retry'),('MaintenanceEngine.cancel','maintenance cancel'),('MaintenanceStore.create','maintenance create'),('MaintenanceStore.status','maintenance status'),('MaintenanceStore.report','maintenance report'),('MaintenanceStore.evidence','maintenance evidence'),('MaintenanceStore.list_jobs','maintenance list'),
 ('changes','changes'),('price_history','history'),('save_snapshot','snapshot-save'),('load_snapshot','snapshot-load'),('get_evidence','evidence get'),('prune_evidence','evidence prune'),('reliable_changes','changes'),('snapshot','snapshot'),('watch','watch'),('ToolRuntime.call ToolRuntime.bootstrap','tools call'),('ToolRuntime.tool_schemas','tools schemas'),('find_duplicates','duplicates'),('check_images','images check'),('validate','validate')]:bind(names,command)
grammar=command_inventory(main);paths={tuple(v['path']) for v in grammar};rows=[];missing=[];definitions={}
for module in saved['modules']:
 path=Path(module['path']);tree=ast.parse(path.read_text());known=set()
 for classification,names in module['definitions'].items():
  for name in names:
   known.add(name);row={'module':str(path),'name':name,'classification':classification}
   if classification=='workflow':
    target=exact.get(name)
    if target is None or tuple(target.split()) not in paths:missing.append(row)
    row['command']=target
   else:row.update(rationale=module['grouped_classification_links'].get(classification,{}).get('rationale','Native data/helper contract consumed by its parent workflow; no standalone operator action.'),parent=module['parent_target'])
   rows.append(row)
 definitions[str(path)]=known
 # Every root re-export remains classified, independently of command count.
 for name,classification in module['exports'].items():
  row={'module':str(path),'name':name,'classification':classification,'reexport':True}
  if classification=='workflow':
   target=exact.get(name)
   if target is None:missing.append(row)
   row['command']=target
  else:row['rationale']='Native data/config/report schema or Python extension interface; consumed by mapped workflows.'
  rows.append(row)
new=[];hashes={}
for path in sorted(Path('src/shopextract').rglob('*.py')):
 text=path.read_text();hashes[str(path)]=hashlib.sha256(text.encode()).hexdigest();tree=ast.parse(text)
 names=[]
 for n in tree.body:
  if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) and not n.name.startswith('_'):
   names.append(n.name)
   if isinstance(n,ast.ClassDef):names.extend(n.name+'.'+m.name for m in n.body if isinstance(m,(ast.FunctionDef,ast.AsyncFunctionDef)) and not m.name.startswith('_'))
 for name in names:
  if name not in definitions.get(str(path),set()):
   row={'module':str(path),'name':name,'classification':'composed_helper','rationale':'Private CLI binding/native lifecycle helper composed by actual command; no standalone arbitrary function invocation.' if path.name.startswith('_cli') or path.name=='cli.py' else 'Native data/parser/lifecycle helper consumed by mapped workflow.'}
   if name in exact:row.update(classification='workflow',command=exact[name])
   new.append(row)
result={'schema_version':1,'state':'actual_local_delivery_pending_final_review','frozen_inventory':'p0/capability-manifest.json','rows':rows,'new_or_previously_grouped':new,'commands':grammar,'missing_workflow_bindings':missing,'source_sha256':hashes,'schema_resources':json.loads(Path('src/shopextract/schemas/index.json').read_text()),'noncommand_policy':{'callback_protocols':'Python-only, no executable CLI input','to_dataframe':'native CSV/Parquet exports cover tabular conversion','data_models':'typed file/report/config contracts, no constructor-per-command','native_transport_helpers':'reused inside mapped parent commands'},'native_tool_names':['discover','extract','match','changes','evidence','job_status','job_result','job_cancel'],'export_formats':['json','csv','google_shopping','idealo','parquet'],'validation_only_markets':['amazon','ebay'],'phase_evidence':{f'P{i}':f'p{i}/verification.md' for i in range(6)}}
(base/'p5/capability-manifest.json').write_text(json.dumps(result,indent=2)+'\n')
assert not missing,missing
assert 'requires its domain CLI phase' not in Path('src/shopextract/_cli_core.py').read_text()
print(json.dumps({'classified_rows':len(rows),'new_or_previously_grouped':len(new),'commands':len(grammar),'leaves':sum(not v['group'] for v in grammar),'missing':len(missing)}))
