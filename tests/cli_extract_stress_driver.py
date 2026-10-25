"""Sequential predeclared P1 stress; run from repository root, no network/models."""
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'specs/011-cli-feature-parity/p1/evidence/stress'
CASES=[
 ('byte-edges','tests/test_cli_extract_limits.py::test_input_byte_edges'),
 ('record-edges','tests/test_cli_extract_limits.py::test_record_count_edges'),
 ('depth-edges','tests/test_cli_extract_limits.py::test_depth_edges'),
 ('node-edges','tests/test_cli_extract_limits.py::test_node_edges'),
 ('typed-mixed','tests/test_cli_extract_limits.py::test_mixed_and_variant_misalignment_rejected'),
 ('money-evidence-eleven','tests/test_cli_extract.py::test_eleven_products_native_transport_and_exact_codec'),
 ('ambient-guard','tests/test_cli_extract.py::test_machine_ambient_keys_never_resolve_or_submit'),
 ('nested-budget','tests/test_cli_extract.py::test_bounded_native_llm_shared_calls_input_output_deadline'),
 ('timeout-cleanup','tests/test_cli_extract.py::test_timeout_cleanup_and_policy_reset'),
 ('atomic-rollback','tests/test_cli_extract.py::test_atomic_output_failure_preserves_old_result'),
 ('optional-browser','tests/test_cli_extract.py::test_browser_preflight_missing_before_fetch'),
 ('provider-secret','tests/test_cli_extract.py::test_provider_error_sanitized_real_native_fallback'),
]
OUT.mkdir(parents=True,exist_ok=True)
state={'seed':11025,'workers':1,'case_timeout_seconds':30,'total_timeout_seconds':180,'rss_limit_bytes':512*1024**2,'raw_record_limit':1001,'normalized_product_limit':100,'cases':[]}
start=time.monotonic()
env={**os.environ,'PYTHONPATH':str(ROOT/'src'),'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','TOKENIZERS_PARALLELISM':'false'}
for name,target in CASES:
 remaining=180-(time.monotonic()-start)
 if remaining<=0:
  state['stop']='total_deadline'
  (OUT/'status.json').write_text(json.dumps(state,indent=2)+'\n')
  raise SystemExit(1)
 with (OUT/f'{name}.log').open('w') as stream:
  try:
   run=subprocess.run([sys.executable,'-m','pytest',target,'-q','--tb=short'],cwd=ROOT,env=env,stdout=stream,stderr=subprocess.STDOUT,timeout=min(30,remaining))
  except subprocess.TimeoutExpired:
   state['cases'].append({'name':name,'returncode':None,'stop':'deadline'})
   state['elapsed_seconds']=round(time.monotonic()-start,3)
   (OUT/'status.json').write_text(json.dumps(state,indent=2)+'\n')
   raise SystemExit(1)
 rss=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
 if sys.platform!='darwin': rss*=1024
 state['cases'].append({'name':name,'returncode':run.returncode,'max_child_rss_bytes':rss})
 state['elapsed_seconds']=round(time.monotonic()-start,3)
 (OUT/'status.json').write_text(json.dumps(state,indent=2)+'\n')
 if run.returncode or rss>state['rss_limit_bytes']: raise SystemExit(1)
print(json.dumps({'cases':len(state['cases']),'passed':True,'elapsed_seconds':state['elapsed_seconds']}))
