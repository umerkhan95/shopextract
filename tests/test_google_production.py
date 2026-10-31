"""Versioned production verification and real owned-process lifecycle contracts."""
import importlib
import json
import os
from pathlib import Path
import sys
import signal
import subprocess

import pytest

from tests.test_google_live import profile


def production_profile(profile):
    root, path, value = profile
    value['schema_version'] = 2
    value['sites'][0]['source_kind'] = 'production'
    value['limits'] = dict(invocations=2, products=4, seconds=120, output_bytes=1048576)
    path.write_text(json.dumps(value))
    return root, path, value


def test_production_profile_and_policy_denial(profile, monkeypatch):
    root, path, _ = production_profile(profile)
    module = importlib.import_module('shopextract.taxonomies.google.live')
    monkeypatch.setattr(module, 'policy_denial', lambda url: {'reason': 'host_not_allowed'})
    report = module.verify_google_live(path, root / 'out', project_root=root, live=True)
    assert report['status'] == 'blocked' and not report['live_verified']
    assert report['usage']['pipeline_invocations'] == 0
    assert report['usage']['network_requests'] is None
    assert report['sites'][0]['extraction']['status'] == 'not_run'


@pytest.mark.parametrize('change', [lambda p: p['limits'].update(invocations=True),
    lambda p: p['limits'].update(requests=8), lambda p: p['sites'][0].update(source_kind='html')])
def test_production_profile_rejects_false_network_bounds(profile, change):
    root, path, value = production_profile(profile)
    change(value); path.write_text(json.dumps(value))
    from shopextract.taxonomies.google.live_profile import load_live_profile
    with pytest.raises(ValueError):
        load_live_profile(path, project_root=root)


def supervisor():
    try:
        return importlib.import_module('shopextract._owned_process').run_owned
    except ModuleNotFoundError:
        pytest.fail('Production owned-process supervisor is missing', pytrace=False)


@pytest.mark.parametrize('stream', [1, 2])
@pytest.mark.parametrize('amount,exceeded', [(128, False), (129, True)])
def test_owned_output_exact_boundary(amount, exceeded, stream):
    result = supervisor()([sys.executable, '-c', f'import os;os.write({stream},b"x"*{amount})'],
                          input_bytes=b'', timeout=2, maximum_bytes=128)
    assert result['output_exceeded'] is exceeded
    assert len(result['stdout' if stream == 1 else 'stderr']) <= 128
    assert result['cleanup_complete']


@pytest.mark.parametrize('exit_parent', [False, True])
def test_owned_timeout_and_success_clean_descendants(tmp_path, exit_parent):
    marker = tmp_path / 'pid'
    program = ('import subprocess,sys,time,signal;'
        'signal.signal(signal.SIGTERM,signal.SIG_IGN);'
        'p=subprocess.Popen([sys.executable,"-c",'
        '"import signal,time;signal.signal(signal.SIGTERM,signal.SIG_IGN);time.sleep(60)"]);'
        f'open({str(marker)!r},"w").write(str(p.pid));'
        + ('print("done",flush=True)' if exit_parent else 'time.sleep(60)'))
    result = supervisor()([sys.executable, '-c', program], input_bytes=b'',
                          timeout=1.5, maximum_bytes=128)
    assert result['cleanup_complete'], result
    assert result['timed_out'] is (not exit_parent)
    with pytest.raises(ProcessLookupError):
        os.kill(int(marker.read_text()), 0)


@pytest.mark.parametrize('signum', [signal.SIGINT, signal.SIGTERM])
def test_owned_signal_cleanup_restores_process_state(tmp_path, signum):
    marker = tmp_path / 'pid'
    child = f'import os,time;open({str(marker)!r},"w").write(str(os.getpid()));time.sleep(60)'
    script = '''import json,os,signal,sys,threading
from shopextract._owned_process import run_owned,_subreaper
sig=int(sys.argv[1]);before=signal.getsignal(sig);reaper=_subreaper()
timer=threading.Timer(.4,lambda:os.kill(os.getpid(),sig));timer.start()
try:
 run_owned([sys.executable,'-c',sys.argv[2]],input_bytes=b'',timeout=2,maximum_bytes=128)
except (KeyboardInterrupt,SystemExit):
 print(json.dumps({'signal_restored':signal.getsignal(sig)==before,'reaper_restored':_subreaper()==reaper}))
finally: timer.cancel()
'''
    reply = subprocess.run([sys.executable, '-c', script, str(signum), child],
                           capture_output=True, timeout=4)
    assert reply.returncode == 0, reply.stderr
    assert json.loads(reply.stdout) == dict(signal_restored=True, reaper_restored=True)
    with pytest.raises(ProcessLookupError):
        os.kill(int(marker.read_text()), 0)


@pytest.mark.parametrize('platform', ['shopify', 'auto'])
def test_production_worker_uses_actual_api_and_retains_capture(monkeypatch, platform):
    import asyncio
    import httpx
    from shopextract._execution import current_policy
    try:
        worker = importlib.import_module('shopextract.taxonomies.google.live_worker')
    except ModuleNotFoundError:
        pytest.fail('Native production worker is missing', pytrace=False)
    observed = []
    def respond(request):
        observed.append(current_policy())
        if request.url.path in ('', '/'):
            return httpx.Response(200, headers={'x-shopid':'1'},
                                  text='<meta name="generator" content="shopify">')
        if request.url.path != '/products.json':
            return httpx.Response(404)
        return httpx.Response(200, json={'products': [{'id':1, 'title':'Book',
            'handle':'book','product_type':'Books','images':[{'src':'https://shop.test/image'}],
            'variants':[{'id':2,'price':'1.00','sku':'book'}]}]})
    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, 'AsyncClient', lambda *args, **kw:
        original(*args, **dict(kw, transport=httpx.MockTransport(respond))))
    value = asyncio.run(worker.produce(dict(url='https://shop.test', shop_url='https://shop.test',
        platform=platform, max_products=1, timeout=5)))
    assert value['tier'] == 'api'
    assert value['platform'] == 'shopify'
    assert value['raw_products'][0]['_capture']['values']['/product_type'] == 'Books'
    assert observed and all(p.browser and p.llm is None for p in observed)
    assert value['browser']['attempted'] is None


@pytest.mark.parametrize('category', ['Books', None, 'mapping_failure', 'invocations', 'products'])
def test_owned_worker_to_actual_mapping_export(profile, monkeypatch, category):
    """Real child/native pipeline/CLI/export; only remote HTTP/seeding controlled."""
    root, path, config = production_profile(profile)
    if category in ('invocations', 'products'):
        config['sites'].append(dict(config['sites'][0], id='second'))
        config['limits'][category] = 1
        path.write_text(json.dumps(config))
    product = {'@type':'Product','name':'Book','image':'https://shop.test/book.jpg',
               'offers':{'price':'1.00','priceCurrency':'PKR'}}
    if category:
        product['category'] = 'Books'
    html = '<script type="application/ld+json">' + json.dumps(product) + '</script>'
    script = root / 'controlled_source.py'
    script.write_text('''import sys,json,httpx
from contextlib import redirect_stdout
with redirect_stdout(sys.stderr):
 import shopextract._discover as discovery
 class Seeder:
  async def __aenter__(self): return self
  async def __aexit__(self,*args): pass
  async def urls(self,*args): return [{'url':'https://shop.test/item','status':'valid'}]
 discovery.AsyncUrlSeeder=Seeder
 original=httpx.AsyncClient
 body=''' + repr(html) + '''
 def response(request): return httpx.Response(200,text=body)
 httpx.AsyncClient=lambda *a,**kw: original(*a,**dict(kw,transport=httpx.MockTransport(response)))
 from shopextract.taxonomies.google.live_worker import main
main()
''')
    from shopextract.taxonomies.google import live_production as production
    monkeypatch.setattr(production, 'worker_command', lambda: [sys.executable, str(script)])
    from shopextract.taxonomies.google import live
    monkeypatch.setattr(live, 'policy_denial', lambda _: None)
    if category == 'mapping_failure':
        def fail(*args): raise OSError('Injected mapping artifact failure')
        monkeypatch.setattr(live, 'map_products', fail)
    report = live.verify_google_live(path, root / 'out', project_root=root, live=True, controlled=True)
    expected = 'fail' if category == 'mapping_failure' else 'pass' if category == 'Books' else 'needs_review'
    assert report['status'] == expected, report
    assert report['mode'] == 'controlled' and not report['live_verified']
    assert report['usage'] == dict(pipeline_invocations=1, products=1, network_requests=None, network_bytes=None)
    site = report['sites'][0]
    assert site['extraction']['tier'] == 'unified_crawl'
    assert site['extraction']['status'] == 'success'
    assert site['extraction']['process']['cleanup_complete']
    if category == 'mapping_failure':
        assert site['mapping']['status'] == 'failed'
        assert site['error_stage'] == 'mapping_export'
        return
    assert site['export']['verified']
    raw = json.loads((root / 'out' / site['artifacts']['raw']).read_text())
    assert raw[0]['_capture']['method'] == 'json_ld'
    assert raw[0]['_capture']['url'] == 'https://shop.test/item'
    if category:
        assert site['mapping']['classifications'][0]['target_id'] == '784'
    if category in ('invocations', 'products'):
        assert report['sites'][1]['extraction']['status'] == 'skipped_budget'


@pytest.mark.parametrize('program', ['print("not json")',
    'print("{}")', 'import sys;print("{}");sys.exit(1)'])
def test_invalid_child_protocol_cannot_map(profile, monkeypatch, program):
    root, path, _ = production_profile(profile)
    from shopextract.taxonomies.google import live, live_production
    monkeypatch.setattr(live, 'policy_denial', lambda _: None)
    monkeypatch.setattr(live_production, 'worker_command', lambda: [sys.executable, '-c', program])
    result = live.verify_google_live(path, root / 'out', project_root=root, live=True, controlled=True)
    assert result['status'] == 'fail' and not result['live_verified']
    assert result['sites'][0]['mapping']['status'] == 'not_run'
    assert result['sites'][0]['extraction']['process']['cleanup_complete']


def test_worker_metadata_rejects_integer_boolean():
    from shopextract.taxonomies.google.live_production import validate_result
    value = dict(schema_version=1, platform='shopify', raw_products=[], tier='api', urls_attempted=1,
        urls_succeeded=0, errors=[], catalog_complete=False, incompleteness_reasons=[],
        truncated=False, browser={'enabled':1,'attempted':None},
        llm={'enabled':False,'reason':'no_configured_budget'})
    with pytest.raises(ValueError):
        validate_result(value, 1)


def test_auto_profile_and_unscoped_rule_only(profile, monkeypatch):
    root, path, value = production_profile(profile)
    value['sites'][0]['platform'] = 'auto'
    path.write_text(json.dumps(value))
    from shopextract.taxonomies.google import live
    monkeypatch.setattr(live, 'policy_denial', lambda _: {'reason':'host_not_allowed'})
    report = live.verify_google_live(path, root / 'out', project_root=root, live=True)
    assert report['usage']['pipeline_invocations'] == 0
    assert 'platform' not in report['sites'][0]['extraction']
    value['sites'][0]['mapping_rules'][0]['selector']['scope'] = dict(
        platform='generic',store_url='https://shop.test',catalog=None,channel=None,locale=None)
    path.write_text(json.dumps(value))
    with pytest.raises(ValueError):
        live.verify_google_live(path, root / 'out2', project_root=root, live=True)


def test_explicit_platform_mismatch_rejected():
    from shopextract.taxonomies.google.live_production import validate_result
    value = dict(schema_version=1, platform='shopify', raw_products=[], tier='api', urls_attempted=1,
        urls_succeeded=0, errors=[], catalog_complete=False, incompleteness_reasons=[],
        truncated=False, browser={'enabled':True,'attempted':None},
        llm={'enabled':False,'reason':'no_configured_budget'})
    with pytest.raises(ValueError):
        validate_result(value, 1, declared_platform='generic')
