"""Complete exact unexecuted collected nodes after preserved 240s local main timeout."""
import hashlib,importlib.util,json,re
from pathlib import Path
here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('bounded',here/'bounded-driver.py');d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
maintenance=['test_maintenance_'+n+'.py' for n in ['acceptance','advisor','remaining_edges','review_repairs','store','stress_prerequisites','workflow']]
collected=(here/'collection.log').read_text();nodes=[l for l in collected.splitlines() if l.startswith('tests/')]
main=[n for n in nodes if n.split('::')[0].split('/')[-1] not in maintenance]
original=(here/'full-existing.log').read_text();glyphs=''.join(m[0] for l in original.splitlines() if (m:=re.match(r'^[.FsEx]+',l)))
assert glyphs and set(glyphs)=={'.'}
completed=len(glyphs);assert completed==1249
account={'original_command_status':'timeout240s, not full pass','collection_sha256':hashlib.sha256(collected.encode()).hexdigest(),'main_collected':len(main),'completed_pass_glyphs':completed,'completed_nodes':main[:completed],'remaining_nodes':main[completed:],'method':'Default pytest serial collection order; no xdist/random/reordering hooks/plugins. Each captured quiet glyph is one passed test. Full log retained; no failed/skipped/xfail glyph. Conservative in-flight node included in remaining set.','diagnosis':'Normal oracle12.63s vs requiredplugins12.85s, unrelated plugin not material; no production/test repair or cap increase.'}
(here/'completed-test-accounting.json').write_text(json.dumps(account,indent=2)+'\n')
results=[]
for name,command in [('full-main-remainder',[str(d.PYTHON),'-m','pytest','-q',*main[completed:]]),('full-maintenance',[str(d.PYTHON),'-m','pytest','-q',*['tests/'+f for f in maintenance]])]:
 result=d.run(name,command,240);results.append(result)
 (here/'full-completion-status.json').write_text(json.dumps({'original_main_invocation':'timeout240.165s; not pass','completed_main_prefix':completed,'main_total':len(main),'maintenance_total':sum(n.split('::')[0].split('/')[-1] in maintenance for n in nodes),'results':results,'status':'passed-complete-case-coverage' if len(results)==2 and all(r['returncode']==0 and not r['stop'] and not r['orphans'] for r in results) else 'running-or-failed','limitation':'Local single main-group240s command did not complete. All exact cases accounted separately; no3.11/3.12 local claim.'},indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='command'}),flush=True)
 if result['returncode'] or result['stop'] or result['orphans']:raise SystemExit(1)
