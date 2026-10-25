"""One scoped history exactness mutation; unconditional byte-identical restore."""
import hashlib,json,os,subprocess,sys
from pathlib import Path
source=Path('src/shopextract/monitor/changes.py');before=source.read_bytes();out=Path('specs/011-cli-feature-parity/p3/evidence')
needle=b'(_safe_decimal(p.get("price", 0)) if exact else float(_safe_decimal(p.get("price", 0))))'
assert before.count(needle)==1
report={'before_sha256':hashlib.sha256(before).hexdigest()}
env=dict(os.environ,PYTHONPATH='src',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',TOKENIZERS_PARALLELISM='false')
cmd=[sys.executable,'-m','pytest','-q','tests/test_cli_monitor.py::test_history_exact_readonly_red']
try:
    source.write_bytes(before.replace(needle,b'float(_safe_decimal(p.get("price", 0)))'))
    with (out/'mutation-detected.log').open('w') as log:report['mutant_exit']=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30).returncode
finally:
    source.write_bytes(before)
    report['restored_sha256']=hashlib.sha256(source.read_bytes()).hexdigest()
with (out/'mutation-restored.log').open('w') as log:report['restored_exit']=subprocess.run(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,timeout=30).returncode
assert report['before_sha256']==report['restored_sha256']
(out/'mutation.json').write_text(json.dumps(report,indent=2))
assert report['mutant_exit']==1 and report['restored_exit']==0,report
print(json.dumps(report))
