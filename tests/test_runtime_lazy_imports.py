"""R1 actual fresh-process import contracts; no module-loader mocks."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

ROOT=Path(__file__).resolve().parents[1]


def fresh(code):
    env=dict(os.environ,PYTHONPATH=str(ROOT/'src'),OMP_NUM_THREADS='2',
             OPENBLAS_NUM_THREADS='2',MKL_NUM_THREADS='2',TOKENIZERS_PARALLELISM='false')
    result=subprocess.run([sys.executable,'-c',code],cwd=ROOT,env=env,
                          capture_output=True,text=True,timeout=15)
    assert result.returncode==0,result.stderr[-500:]
    return json.loads(result.stdout)


@pytest.mark.parametrize('module',['shopextract','shopextract._models',
    'shopextract.tools.domain','shopextract.extractors'])
def test_plain_native_import_avoids_browser(module):
    result=fresh(f"import importlib,sys,json,time;t=time.monotonic();importlib.import_module({module!r});print(json.dumps({{'heavy':[m for m in sys.modules if m.split('.')[0] in ('crawl4ai','playwright')],'seconds':time.monotonic()-t}}))")
    assert result['heavy']==[],result


def test_explicit_browser_export_resolves_actual_cached_class():
    result=fresh("from shopextract import extractors;from shopextract.extractors.unified import UnifiedCrawlExtractor;import sys,json;print(json.dumps({'same':extractors.UnifiedCrawlExtractor is UnifiedCrawlExtractor and extractors.UnifiedCrawlExtractor is extractors.UnifiedCrawlExtractor,'browser_loaded':'crawl4ai' in sys.modules}))")
    assert result=={'same':True,'browser_loaded':True}


@pytest.mark.parametrize('namespace',['root','extractors'])
def test_frozen_public_export_inventory_and_original_identities(namespace):
    fixture=ROOT/'tests/fixtures/runtime_exports'
    source=(fixture/(namespace+'_baseline.py')).read_text()
    expected=json.loads((fixture/'inventory.json').read_text())[namespace]
    package='shopextract' if namespace=='root' else 'shopextract.extractors'
    code="""
import importlib,json,inspect
package=PACKAGE
s=importlib.import_module(package)
expected=EXPECTED
# Resolve production objects before eager reference imports to avoid reference side effects.
actual={name:getattr(s,name) for name in expected['intentional_public']}
reference={'__name__':'frozen_export_reference','__package__':package}
exec(SOURCE,reference)
reference_names={name for name in reference if not name.startswith('_')}
identities=all(actual[name] is reference[name] for name in expected['intentional_public'])
signatures=all(str(inspect.signature(actual[name]))==str(inspect.signature(reference[name]))
 for name in expected['intentional_public'] if inspect.isfunction(reference[name]))
try:
 s.no_such_export
except AttributeError:unknown=True
else:unknown=False
print(json.dumps({'all_exact':s.__all__==expected['all'],
 'all_set':set(s.__all__)==set(expected['all']),
 'intentional_exact':reference_names==set(expected['intentional_public']),
 'dir_coverage':set(expected['all']+expected['intentional_public']).issubset(dir(s)),
 'identities':identities,'signatures':signatures,'unknown':unknown,
 'version':getattr(s,'__version__',None)==expected['version']}))
""".replace('PACKAGE',repr(package)).replace('EXPECTED',repr(expected)).replace('SOURCE',repr(source))
    result=fresh(code)
    assert result=={key:True for key in ('all_exact','all_set','intentional_exact',
        'dir_coverage','identities','signatures','unknown','version')},result
