import ast,json,pathlib,hashlib,subprocess
base=pathlib.Path("specs/011-cli-feature-parity/p0")
def save(name,value): (base/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+"\n")
source=pathlib.Path('src/shopextract/cli.py').read_text();tree=ast.parse(source);commands=[]
for n in tree.body:
 if not isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)):continue
 if not any(isinstance(d,ast.Call) and ast.unparse(d.func)=='main.command' for d in n.decorator_list):continue
 command=n.name
 for d in n.decorator_list:
  if isinstance(d,ast.Call) and ast.unparse(d.func)=='main.command':
   command=next((ast.literal_eval(k.value) for k in d.keywords if k.arg=='name'),command)
 commands.append({'command':command,'callback':n.name,'declarations':[ast.unparse(d) for d in n.decorator_list],'dispatch':ast.unparse(n.body[-1])})
save('command-baseline.json',{'source':'src/shopextract/cli.py','sha256':hashlib.sha256(source.encode()).hexdigest(),'commands':commands,'count':len(commands),'legacy_output_notes':{'extract':'stderr summary; stdout first 10 product records; -o writes all and stdout confirmation','detect':'platform/confidence/signals JSON','discover':'one URL per line; stderr count','compare':'query/matches/cheapest/most_expensive/avg_price/results JSON','snapshot':'url/product_count JSON','changes':'per-change pretty JSON or no changes text','history':'timestamp/price array JSON','analyze':'summary JSON; first 20 brands','validate':'text report; issues alone do not set failure exit'}})
# Named workflow map. Values are target FAMILY only until affected phase freeze.
families={}
def add(names,phase,target):
 for name in names.split():families[name]=(phase,target)
add('detect discover extract extract_one from_feed normalize','P1','extraction (detect/discover/extract/extract-one/feed/normalize)')
add('score_product score_batch','P1','quality')
add('compare compare_catalogs fuzzy_match match_gtin match_products classify_match assign_identity normalized_attributes evaluate_matching','P2','comparison/match/identity')
add('analyze analyze_products price_distribution outliers brand_breakdown price_position assortment_gaps brand_coverage','P2','analysis/stats/competitive')
add('validate check_images find_duplicates','P2','validate/images/duplicates')
add('to_csv to_json to_feed to_parquet','P2','export')
add('snapshot changes price_history watch reliable_changes save_snapshot load_snapshot get_evidence prune_evidence migrate_snapshot_identities resolve_fields resolution_references factual_paths trust_view','P3','monitor/history/evidence/identity migrate/resolve')
add('create_evidence_bundle load_evidence_bundle read_evidence_bundle write_evidence_bundle create_evidence_sidecar load_evidence_sidecar','P3','evidence bundle/sidecar')
add('extract_with_categories normalize_with_categories validate_options map_categories validate_observations fetch_woocommerce_category_tree link_tree_memberships categorized_product_from_record categorized_product_to_record woo_tree_to_record woo_tree_from_record category_policy_digest category_review_reasons runtime_record runtime_from_record options_digest bind_product validate_categorized_products','P4','categories extract/normalize/map/validate/record/tree/policy/config')
python_only={'alert','to_dataframe','Investigator','FailureHook','Resolver','AuxiliaryOwner'}
manifest={'state':'classification_complete_pending_G1','scope':'All local public top-level definitions, public class methods, __all__ exports and saved AST inventory entries. Private-module definitions included conservatively; imported third-party names excluded. AST snapshot is current dirty working tree, not release API claim.','classification_rules':{'workflow':'Native entry point represented by target family; exact flags/domain schema reserved','data_schema':'Model/enum/contract/config shape consumed by parent workflow; no constructor command','composed_helper':'Named helper consumed by parent target; no standalone command','implementation_helper':'Adapter/parser/security/lifecycle detail exercised through parent workflow; no standalone command','python_only':'Object/callback injection or in-memory result, cannot encode as portable CLI invocation','entrypoint':'Existing CLI/module invocation retained'},'workflow_targets':{k:{'phase':v[0],'target':v[1],'grammar_state':'reserved'} for k,v in sorted(families.items())},'modules':[]}
# Explicit operator-method allowlist: lifecycle/persistence internals are not workflows.
operator_methods={
 ('MaintenanceEngine','run'):('P5','maintenance run'),
 ('MaintenanceEngine','resume'):('P5','maintenance resume'),
 ('MaintenanceEngine','cancel'):('P5','maintenance cancel'),
 ('MaintenanceEngine','retry_unknown'):('P5','maintenance retry'),
 ('MaintenanceStore','create'):('P5','maintenance create'),
 ('MaintenanceStore','status'):('P5','maintenance status'),
 ('MaintenanceStore','report'):('P5','maintenance report'),
 ('MaintenanceStore','evidence'):('P5','maintenance evidence'),
 ('ToolRuntime','call'):('P5','tools call'),
 ('ToolRuntime','tool_schemas'):('P5','tools schemas'),
 ('QualityScorer','score_product'):('P1','quality'),
 ('QualityScorer','score_batch'):('P1','quality')}
category_composed={'validate_options','categorized_product_from_record','categorized_product_to_record','woo_tree_to_record','woo_tree_from_record','runtime_record','runtime_from_record','options_digest','bind_product','validate_categorized_products','category_policy_digest','category_review_reasons'}
# Name lookup is applied only to top-level domain entry functions, never class methods.
def top_kind(path,node):
 name=node.name
 if name in python_only:return 'python_only'
 if isinstance(node,ast.ClassDef):
  if '/extractors/' in str(path):return 'implementation_helper'
  if name in {'ToolRuntime','MaintenanceEngine','MaintenanceStore','QualityScorer'}:return 'composed_helper'
  # Protocol extensions/injection contracts are not portable operator APIs.
  if any(isinstance(x,ast.Name) and x.id=='Protocol' for x in node.bases):return 'python_only'
  if path.stem in {'_models','contracts','profiles'} or any(isinstance(x,ast.Name) and x.id in {'Enum','StrEnum','IntEnum','Exception','ValueError'} for x in node.bases) or any(isinstance(d,ast.Name) and d.id=='dataclass' or isinstance(d,ast.Call) and ast.unparse(d.func)=='dataclass' for d in node.decorator_list):return 'data_schema'
  return 'implementation_helper'
 if path.name=='cli.py' or path.name=='__main__.py':return 'entrypoint' if name in {'main','execute'} or path.name=='cli.py' else 'composed_helper'
 if '/extractors/' in str(path):return 'implementation_helper'
 if str(path)=='src/shopextract/tools/contracts.py' and name=='validate':return 'composed_helper'
 if name in category_composed:return 'composed_helper'
 if name in families:return 'workflow'
 return 'composed_helper' if '/categories/' in str(path) else 'implementation_helper'
for path in sorted(pathlib.Path('src/shopextract').rglob('*.py')):
 text=path.read_text();t=ast.parse(text);groups={};exports=[];links={};group_links={}
 if '/categories/' in str(path):parent=('P4','categories extraction/mapping/config/records/tree')
 elif '/maintenance/' in str(path):parent=('P5','maintenance lifecycle/job reporting')
 elif '/tools/' in str(path):parent=('P5','tools call/schemas/serve')
 elif '/extractors/' in str(path):parent=('P1','extract/extract-one/feed through native adapters')
 elif '/monitor/' in str(path):parent=('P3','snapshot/changes/history/evidence/watch')
 elif path.name=='cli.py':parent=('P0','nine legacy root commands')
 else:parent=('P0–P5','typed domain reports; concrete workflows linked individually')
 def put(category,name,phase=None,target=None,rationale=None):
  groups.setdefault(category,[]).append(name)
  link={'classification':category,'phase':phase or parent[0],'target':target or parent[1],'grammar_state':'legacy_frozen' if category=='entrypoint' and path.name=='cli.py' else 'reserved','rationale':rationale or {'implementation_helper':'Library adapter/parser/security mechanism exercised through parent; no standalone command.','data_schema':'Typed data/config/result contract of parent workflow; no constructor command.','composed_helper':'Parent workflow owns validation, serialization, persistence or resource lifecycle; no independent operator action.','python_only':'Python callback/protocol/in-memory extension; no executable CLI input.','entrypoint':'Retained module/root registration invocation; domain expansion reserved.'}.get(category,'Native operator entry point; target family only, domain grammar requires phase freeze.')}
  if category=='workflow':links[name]=link
  else:group_links.setdefault(category,link)
 for node in t.body:
  if isinstance(node,(ast.Assign,ast.AugAssign)):
   targets=node.targets if isinstance(node,ast.Assign) else [node.target]
   if any(isinstance(v,ast.Name) and v.id=='__all__' for v in targets):
    try:exports+=ast.literal_eval(node.value)
    except (ValueError,TypeError):pass
  if not isinstance(node,(ast.FunctionDef,ast.AsyncFunctionDef,ast.ClassDef)) or node.name.startswith('_'):continue
  name=node.name;kind=top_kind(path,node)
  phase,target=families[name] if kind=='workflow' else parent
  put(kind,name,phase,target)
  if isinstance(node,ast.ClassDef):
   for member in node.body:
    if not isinstance(member,(ast.FunctionDef,ast.AsyncFunctionDef)) or member.name.startswith('_'):continue
    q=name+'.'+member.name
    if (name,member.name) in operator_methods:
     phase,target=operator_methods[name,member.name];put('workflow',q,phase,target,'Explicit operator action composed by the mapped command, unlike storage or lifecycle internals.')
    elif name=='MaintenanceEngine' and member.name in {'now','hook'}:
     put('python_only',q,rationale='Injected clock/callback hook used by engine; no operator workflow.')
    elif kind=='python_only':put('python_only',q)
    else:put('composed_helper' if kind!='implementation_helper' or name in {'MaintenanceEngine','MaintenanceStore','ToolRuntime'} else 'implementation_helper',q)
 if groups or exports:
  export_kinds={e:('python_only' if e in python_only else 'composed_helper' if e in category_composed or e in {'ToolRuntime','MaintenanceEngine','MaintenanceStore','QualityScorer'} else 'workflow' if e in families else 'data_schema') for e in exports}
  export_links={e:{'classification':k,'phase':families[e][0],'target':families[e][1],'grammar_state':'reserved','rationale':'Re-export of native operator entry point; implementation definition classified in its source module.'} for e,k in export_kinds.items() if k=='workflow'}
  manifest['modules'].append({'path':str(path),'sha256':hashlib.sha256(text.encode()).hexdigest(),'parent_target':{'phase':parent[0],'target':parent[1]},'definitions':groups,'definition_links':links,'grouped_classification_links':group_links,'exports':export_kinds,'export_workflow_links':export_links})
old=json.load(open(base.parent/'evidence/surface-inventory.json'))
manifest['saved_inventory_reconciliation']={p:{'functions':v['functions'],'imports':{n:('entrypoint' if p.endswith('cli.py') else 'composed_helper' if n in category_composed or n in {'ToolRuntime','MaintenanceEngine','MaintenanceStore','QualityScorer'} else 'workflow' if n in families else 'data_schema' if n[:1].isupper() else 'implementation_helper') for n in v['imports']}} for p,v in old.items()}
manifest['callback_policy']={'monitor.watch.alert':'Python-only when/callback registry. No declarative alert feature promised; watch event consumers reserved P3.','maintenance.Investigator/FailureHook':'Python-only callback/investigator injection; trusted declarative goals/profiles remain P5 input schema work.','native context callbacks/transport/resolver/clock':'Python-only test/integration seams; CLI does not import executable user config.','category helpers':'Composed config/portable/native adapter mechanics under categories parent; no helper-per-command requirement.','to_dataframe':'Python-only object; CSV/Parquet export covers portable tabular workflows.'}
workflow_link_count=0
for module in manifest['modules']:
 for name in module['definitions'].get('workflow',[]):
  link=module['definition_links'][name]
  assert link['phase'] and link['target'] and link['rationale'], (module['path'],name)
  workflow_link_count+=1
 for name,kind in module['exports'].items():
  if kind=='workflow':assert name in module['export_workflow_links']
for name,link in manifest['workflow_targets'].items():
 link['classification']='composed_helper' if name in category_composed else 'python_only' if name in python_only else 'workflow'
 link['rationale']='Portable config/codec/policy helper composed by categories parent.' if name in category_composed else 'Native operator entry point; affected-phase domain grammar reserved.'
manifest['audit']={'every_workflow_resolves':True,'local_workflow_links':workflow_link_count,'method_inference':'explicit class+method allowlist; never bare method name','signature_scope':'Reserved: inspect native signatures at affected phase G1; no saved signature claim.'}
save('capability-manifest.json',manifest)
save('evidence/audit-summary.json',{'modules':len(manifest['modules']),'definitions':sum(sum(map(len,m['definitions'].values())) for m in manifest['modules']),'workflow_targets':len(families),'legacy_commands':len(commands),'source_revision':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'scope':'AST classification, not execution or parity pass','actual_session_token_counters':'unavailable'})
print('modules',len(manifest['modules']),'commands',len(commands),'targets',len(families))
