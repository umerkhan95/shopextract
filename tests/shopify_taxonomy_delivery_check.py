"""One cached-full-source cold-checkout delivery proof; never downloads sources."""
import hashlib,json,os,shutil,signal,subprocess,sys,threading,time,zipfile,tarfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/shopify-taxonomy'
PROOF=ROOT/'build/shopify-taxonomy/delivery-proof'


def run_stage(name,command,cwd,env,seconds,rss_limit,deadline):
    started=time.monotonic();peak=0;reason=None
    with (OUT/('delivery-'+name+'.log')).open('wb') as log:
        process=subprocess.Popen(command,cwd=cwd,env=env,stdout=log,stderr=log,start_new_session=True)
        def stop():
            try:os.killpg(process.pid,signal.SIGKILL)
            except ProcessLookupError:pass
        timeout=threading.Timer(min(seconds,max(0,deadline-time.monotonic())),stop);timeout.daemon=True;timeout.start()
        try:
            while process.poll() is None:
                if time.monotonic()>=deadline or time.monotonic()-started>=seconds:reason='timeout';break
                listing=subprocess.check_output(['ps','-ax','-o','pgid=,rss='],text=True,timeout=2)
                used=sum(int(r)*1024 for g,r in (line.split() for line in listing.splitlines()) if int(g)==process.pid);peak=max(peak,used)
                if used>rss_limit:reason='rss_limit';break
                if (OUT/('delivery-'+name+'.log')).stat().st_size>65536:reason='log_limit';break
                time.sleep(.05)
        finally:timeout.cancel();timeout.join(timeout=2);stop();process.wait(timeout=2)
    result={'stage':name,'state':'passed' if process.returncode==0 and reason is None else 'failed','reason':reason,
        'exit_code':process.returncode,'seconds':round(time.monotonic()-started,3),'peak_sampled_group_rss_bytes':peak,'command':command,'processgroup_cleanup':True}
    return result


if __name__=='__main__':
    started=time.monotonic();deadline=started+120
    PROOF.mkdir(parents=True,exist_ok=False)
    root=PROOF/'checkout';root.mkdir()
    shutil.copytree(ROOT/'src',root/'src',ignore=shutil.ignore_patterns('__pycache__','data'))
    shutil.copytree(ROOT/'scripts',root/'scripts',ignore=shutil.ignore_patterns('__pycache__'))
    for name in ('hatch_build.py','pyproject.toml','README.md','LICENSE'):shutil.copyfile(ROOT/name,root/name)
    cache=PROOF/'sources';cache.mkdir()
    for name,source in [('taxonomy.en.json.gz',ROOT/'downloads/shopify-taxonomy/2026-08/taxonomy.en.json.gz'),
        ('attributes.yml',ROOT/'downloads/shopify-taxonomy/2026-08/attributes.source.yml'),('LICENSE',ROOT/'artifacts/shopify-taxonomy/LICENSE')]:
        (cache/name).symlink_to(source)
    assert not (root/'build').exists() and not (root/'src/shopextract/taxonomies/shopify/data').exists()
    env=dict(os.environ);env['PYTHONPATH']=str(root/'src');env['PIP_NO_INDEX']='1';env['PIP_DISABLE_PIP_VERSION_CHECK']='1'
    wrapper="""import json,runpy,socket,sys
from pathlib import Path
checkout=Path(sys.argv[1]).resolve().parents[1]
socket.socket.connect=lambda *a,**k:(_ for _ in ()).throw(AssertionError('offline source proof'))
sys.argv=[sys.argv[1],'--offline','--source-cache',sys.argv[2]]
bootstrap_vars=runpy.run_path(sys.argv[0],run_name='__main__')
assert not any(k=='shopextract' or k.startswith('shopextract.') for k in sys.modules)
assert not any(k in sys.modules for k in ['crawl4ai','pandas','litellm'])
p=sys.modules['_shopextract_taxonomy_build.prepare']
assert Path(p.__file__).resolve()==checkout/'src/shopextract/taxonomies/shopify/prepare.py'
print(json.dumps({'application_imported':False,'prepare_file':p.__file__,'python':sys.version,'toml_source':bootstrap_vars['TOML_SOURCE']}))
"""
    stages=[run_stage('full-bootstrap',[sys.executable,'-c',wrapper,str(root/'scripts/bootstrap_taxonomy.py'),str(cache)],root,env,60,768*1024*1024,deadline)]
    if stages[-1]['state']=='passed':
        build="import socket;socket.socket.connect=lambda *a,**k:(_ for _ in ()).throw(AssertionError('offline'));from hatchling.build import build_sdist,build_wheel;print(build_sdist('dist'));print(build_wheel('dist'))"
        stages.append(run_stage('cold-artifacts',[sys.executable,'-c',build],root,env,30,512*1024*1024,deadline))
    if stages[-1]['state']=='passed':
        stages.append(run_stage('editable-metadata',[sys.executable,'-m','pip','install','--dry-run','--no-index','--no-deps','--no-build-isolation','--ignore-installed','-e','.'],root,env,25,512*1024*1024,deadline))
    passed=len(stages)==3 and all(s['state']=='passed' for s in stages)
    record={'state':'passed' if passed else 'failed','seconds':round(time.monotonic()-started,3),'stages':stages,'source_http_requests':0,
        'dependencies':'metadata-derived HTTPX+taxonomy-build(PyYAML), existing environment resolved via pip --no-index; no heavyweight runtime bootstrap',
        'python_scope':sys.version,'matrix_311_312':'workflow configuration; not executed locally','editable':'dry-run metadata only; developer environment unchanged'}
    if passed:
        pin=json.loads((ROOT/'src/shopextract/taxonomies/shopify/pin.json').read_text())
        directory=root/'build/shopify-taxonomy/catalogs'/pin['release']/pin['fingerprint']
        assert json.loads((directory/'manifest.json').read_text())==pin
        wheel=next((root/'dist').glob('*.whl'));sdist=next((root/'dist').glob('*.tar.gz'))
        with zipfile.ZipFile(wheel) as archive:
            assert json.loads(archive.read('shopextract/taxonomies/shopify/data/manifest.json'))==pin
            assert hashlib.sha256(archive.read('shopextract/taxonomies/shopify/data/catalog.json.gz')).hexdigest()==pin['resource_sha256']
        with tarfile.open(sdist) as archive:
            member=next(m for m in archive.getmembers() if m.name.endswith('/src/shopextract/taxonomies/shopify/data/manifest.json'))
            assert json.load(archive.extractfile(member))==pin
        record.update(fingerprint=pin['fingerprint'],counts=pin['counts'],wheel_bytes=wheel.stat().st_size,sdist_bytes=sdist.stat().st_size)
    (OUT/'delivery-full-proof.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items() if k!='stages'}));sys.exit(0 if passed else 1)
