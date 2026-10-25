"""One scoped critical guard mutation; always restore original source bytes."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'src/shopextract/_cli_categories.py'
DEST=ROOT/'specs/011-cli-feature-parity/p4/evidence/mutation'

def run():
 DEST.mkdir(parents=True,exist_ok=True)
 original=SOURCE.read_bytes();before=hashlib.sha256(original).hexdigest()
 needle=b'if any(v.scope!=options.scope or digest and v.config_digest!=expected for v in values):'
 assert original.count(needle)==1
 command=[sys.executable,'-m','pytest','tests/test_cli_categories_mechanisms.py','-q','-k','scope_guard_before_output_even_forged_digest','--tb=short']
 environment=dict(os.environ,PYTHONPATH=str(ROOT/'src'),OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',TOKENIZERS_PARALLELISM='false',PYTHONDONTWRITEBYTECODE='1')
 result={}
 try:
  SOURCE.write_bytes(original.replace(needle,b'if False and any(v.scope!=options.scope or digest and v.config_digest!=expected for v in values):'))
  child=subprocess.run(command,cwd=ROOT,env=environment,capture_output=True,text=True,timeout=30)
  (DEST/'mutant.log').write_text(child.stdout+child.stderr)
  result['mutant_exit']=child.returncode
  assert child.returncode==1 and '1 failed' in child.stdout,'critical assertion failed to detect mutant'
 finally:
  SOURCE.write_bytes(original)
  result.update(original_sha256=before,restored_sha256=hashlib.sha256(SOURCE.read_bytes()).hexdigest())
  assert result['restored_sha256']==before
  (DEST/'report.json').write_text(json.dumps(result,indent=2))
 child=subprocess.run(command,cwd=ROOT,env=environment,capture_output=True,text=True,timeout=30)
 (DEST/'restored.log').write_text(child.stdout+child.stderr)
 result['restored_exit']=child.returncode
 (DEST/'report.json').write_text(json.dumps(result,indent=2))
 assert child.returncode==0 and '1 passed' in child.stdout

if __name__=='__main__':run()
