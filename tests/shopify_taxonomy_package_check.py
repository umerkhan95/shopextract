"""Offline wheel/sdist artifact membership and installed default-loader proof."""
import hashlib,json,os,subprocess,sys,tarfile,tempfile,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts/shopify-taxonomy'
PIN=json.loads((ROOT/'src/shopextract/taxonomies/shopify/pin.json').read_text())
START=time.monotonic()

def run(args,*,cwd=None,env=None):
    result=subprocess.run(args,cwd=cwd,env=env,capture_output=True,text=True,timeout=30)
    if result.returncode:raise RuntimeError((result.stdout+result.stderr)[-4000:])
    return result.stdout

if __name__=='__main__':
    wheel=next((ROOT/'dist').glob('*.whl'));sdist=next((ROOT/'dist').glob('*.tar.gz'))
    with zipfile.ZipFile(wheel) as archive:
        for name in ('manifest.json','catalog.json.gz','LICENSE'):
            data=archive.read('shopextract/taxonomies/shopify/data/'+name)
            if name=='manifest.json':assert json.loads(data)==PIN
            if name=='catalog.json.gz':assert hashlib.sha256(data).hexdigest()==PIN['resource_sha256']
    with tempfile.TemporaryDirectory(prefix='taxonomy-package-') as temporary:
        root=Path(temporary);venv=root/'venv'
        run([sys.executable,'-m','venv','--system-site-packages',str(venv)])
        python=str(venv/'bin/python')
        run([python,'-m','pip','install','--no-index','--no-deps','--force-reinstall',str(wheel)],cwd=root)
        env=dict(os.environ);env.pop('PYTHONPATH',None)
        proof='''import socket,json,sys
socket.socket.connect=lambda *a,**k:(_ for _ in ()).throw(AssertionError('offline'))
from shopextract.taxonomies.shopify import load_shopify_taxonomy
c=load_shopify_taxonomy()
assert c.manifest.counts.categories==14606 and c.manifest.counts.extensions==316
assert c.category('el-6-6').name=='Laptops'
assert len(tuple(c.iter_values()))==74820
assert 'yaml' not in sys.modules
print(json.dumps({'fingerprint':c.fingerprint,'categories':c.manifest.counts.categories,'values':c.manifest.counts.values}))'''
        installed=json.loads(run([python,'-c',proof],cwd=root,env=env))
        with tarfile.open(sdist) as archive:
            for member in archive.getmembers():
                path=Path(member.name)
                assert not path.is_absolute() and '..' not in path.parts
            archive.extractall(root/'sdist')
        source=next((root/'sdist').iterdir())
        assert (source/'src/shopextract/taxonomies/shopify/data/catalog.json.gz').is_file()
        # Isolated interpreter does not load application or YAML. Explicit socket
        # denial demonstrates the published sdist wheel build cannot fetch sources.
        built=run([sys.executable,'-c',"import socket;socket.socket.connect=lambda *a,**k:(_ for _ in ()).throw(AssertionError('offline'));from hatchling.build import build_wheel;print(build_wheel('dist'))"],cwd=source,env=env).strip()
        rebuilt=source/'dist'/built
        with zipfile.ZipFile(rebuilt) as archive:
            assert archive.read('shopextract/taxonomies/shopify/data/catalog.json.gz')==zipfile.ZipFile(wheel).read('shopextract/taxonomies/shopify/data/catalog.json.gz')
        result={'state':'passed','seconds':round(time.monotonic()-START,3),'installed':installed,
            'wheel_bytes':wheel.stat().st_size,'sdist_bytes':sdist.stat().st_size,'offline':True,'environment':'fresh venv --system-site-packages for existing application dependencies; wheel --no-index --no-deps','sdist_to_wheel_network':False,'runtime_yaml_import':False}
        (OUT/'package-proof.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
