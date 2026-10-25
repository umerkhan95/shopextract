"""Scoped fault proof; byte-identical restoration even on assertion failures."""
import hashlib,importlib.util,json
from pathlib import Path
here=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('bounded',here/'bounded-driver.py');driver=importlib.util.module_from_spec(spec);spec.loader.exec_module(driver)
source=driver.ROOT/'src/shopextract/_cli_operations.py';before=source.read_bytes();sha=lambda b:hashlib.sha256(b).hexdigest()
needle=b'result=prior[match[1]]';assert before.count(needle)==1
command=[str(driver.PYTHON),'-m','pytest','-q','tests/test_cli_operations.py::test_session_real_bootstrap_match_poll_pages_stale_and_cleanup']
try:
 source.write_bytes(before.replace(needle,b'result={}  # scoped mutation: break same-session reference ownership'))
 mutant=driver.run('mutation-mutant',command,30,512*1024**2)
 assert mutant['returncode']==1 and not mutant['stop'] and not mutant['orphans'],mutant
 assert 'Session reference target is unavailable' in (here/'mutation-mutant.log').read_text()
finally:source.write_bytes(before)
assert source.read_bytes()==before
restored=driver.run('mutation-restored',command,30,512*1024**2)
assert restored['returncode']==0 and not restored['stop'] and not restored['orphans'],restored
report={'status':'passed','target':'same-session reference resolution, real native bootstrap/match acceptance','before_sha256':sha(before),'after_sha256':sha(source.read_bytes()),'restored_byteidentical':True,'mutant':mutant,'restored':restored}
(here/'mutation-report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':'passed','restored_byteidentical':True,'mutant_seconds':mutant['seconds'],'restored_seconds':restored['seconds']}))
