"""P4 sequential bounded distinct-case stress driver, seed11025; no model work."""
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import psutil

ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'specs/011-cli-feature-parity/p4/evidence/stress'
GROUPS=[
 ('01-six-native-bindings','six_normalize or six_extract or native_flags'),
 ('02-source-states','survivors or nonlist or zero_terms'),
 ('03-map-policy','mapping_roundtrip or policy_native'),
 ('04-authority-scope','authority or scope_guard or decoded_scope or valid_nested'),
 ('05-tree-states','tree_native_outcomes or tree_malformed'),
 ('06-tree-memberships','tree_membership'),
 ('07-export-formats','export_category_format or parquet_arrow'),
 ('08-three-file-recovery','three_artifacts or recovery_failure or staged_file_size'),
 ('09-alias-single-read','aliases_all or source_alias or storefront_config_alias'),
 ('10-byte-output-bounds','byte_structure or output_actual or oversized_dual or companion_config'),
 ('11-options-numeric','invalid_config or tree_seconds'),
 ('12-crossphase-entrypoints','category_to_p3 or module_entrypoint or parser_nested'),
]

def run():
 DEST.mkdir(parents=True,exist_ok=True)
 environment=dict(os.environ,PYTHONPATH=str(ROOT/'src'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',TOKENIZERS_PARALLELISM='false',RAYON_NUM_THREADS='1')
 state=dict(seed=11025,case_timeout_seconds=30,total_timeout_seconds=300,rss_limit_bytes=512*1024*1024,workers=1,groups=[],status='running',max_rss_bytes=0,orphans=0)
 start=time.monotonic()
 for name,expression in GROUPS:
  if time.monotonic()-start>300:raise RuntimeError('total bound')
  command=[sys.executable,'-m','pytest','tests/test_cli_categories_mechanisms.py','-q','--tb=short','-k',expression]
  began=time.monotonic()
  with (DEST/(name+'.log')).open('w') as log:
   process=subprocess.Popen(command,cwd=ROOT,env=environment,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   owned=psutil.Process(process.pid);seen={process.pid};stop=None
   while process.poll() is None:
    try:
     children=owned.children(recursive=True);members=[owned,*children];seen.update(p.pid for p in children)
     rss=sum(p.memory_info().rss for p in members if p.is_running())
     state['max_rss_bytes']=max(state['max_rss_bytes'],rss)
    except (psutil.NoSuchProcess,psutil.AccessDenied):rss=0
    if rss>state['rss_limit_bytes']:stop='rss_limit'
    if time.monotonic()-began>30:stop='timeout'
    if time.monotonic()-start>300:stop='total_timeout'
    if stop:
     os.killpg(process.pid,signal.SIGKILL);process.wait();break
    time.sleep(.05)
  orphans=[pid for pid in seen if pid!=process.pid and psutil.pid_exists(pid)]
  state['orphans']+=len(orphans)
  for pid in orphans:
   try:psutil.Process(pid).kill()
   except psutil.NoSuchProcess:pass
  if orphans:
   try:os.killpg(process.pid,signal.SIGKILL)
   except ProcessLookupError:pass
  record=dict(name=name,command=command,exit_code=process.returncode,seconds=round(time.monotonic()-began,3),stop=stop,orphans=orphans)
  state['groups'].append(record);state['elapsed_seconds']=round(time.monotonic()-start,3)
  state['status']='failed' if process.returncode or stop or orphans else 'running'
  (DEST/'status.json').write_text(json.dumps(state,indent=2))
  if state['status']=='failed':return 1
 state['status']='passed';(DEST/'status.json').write_text(json.dumps(state,indent=2));return 0

if __name__=='__main__':raise SystemExit(run())
