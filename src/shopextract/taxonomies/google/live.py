"""Bounded live orchestration over existing source capture, CLI and codecs."""
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
import time
from uuid import uuid4
from urllib.parse import urljoin

import httpx

from ..._cli_data import atomic_json, categorized_from_value
from .live_policy import policy_denial
from .live_profile import load_live_profile, in_scope
from .loader import load_google_taxonomy


def runtime_fingerprint():
    root = Path(__file__).resolve().parents[2]
    parts = [(str(p.relative_to(root)), sha256(p.read_bytes()).hexdigest()) for p in sorted(root.rglob('*.py'))]
    return sha256(json.dumps(parts,separators=(',',':')).encode()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def parse_source(site, body, url, maximum):
    if site['source_kind'] == 'shopify_products':
        from ..._capture import capture
        value = json.loads(body)
        if not isinstance(value,dict):
            raise ValueError('Shopify response must be an object')
        products = value.get('products', [])
        if not isinstance(products,list) or any(not isinstance(v,dict) for v in products):
            raise ValueError('Invalid Shopify product response')
        return [capture(item,url,'shopify_api') for item in products[:maximum]]
    if site['source_kind'] == 'html_css':
        from types import SimpleNamespace
        from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
        from ...extractors.css import CSSExtractor
        schema = site['css_schema']
        rows = JsonCssExtractionStrategy(schema,verbose=False).extract(url,body)
        return CSSExtractor(schema)._parse_extracted_content(url,SimpleNamespace(
            success=True,extracted_content=json.dumps(rows),html=body,url=url))[:maximum]
    from ...extractors.unified import UnifiedCrawlExtractor
    return UnifiedCrawlExtractor._extract_structured_from_html(body,url,include_categories=True)[:maximum]


def verify_google_live(profile_path, output_dir, *, live=False, site_id=None, project_root=None, transport=None, controlled=False):
    profile_path = Path(profile_path).resolve()
    profile = load_live_profile(profile_path,project_root=project_root)
    sites = [s for s in profile['sites'] if site_id is None or s['id'] == site_id]
    if not sites:
        raise ValueError('Unknown selected site')
    out = Path(output_dir).resolve()
    if out.exists():
        raise ValueError('Output exists; use a new run directory')
    catalog = load_google_taxonomy(catalog_root=profile['catalog_root'],fingerprint=profile['catalog_fingerprint'])
    from ..._models import Platform
    from ...categories._codec import typed
    from ...categories.contracts import MappingRule, CategoryScope
    from .options import google_taxonomy_options
    for site in sites:
        rules=tuple(typed(MappingRule,rule) for rule in site['mapping_rules'])
        targets={target for rule in rules for target in rule.target_ids}
        scope_platform = Platform.GENERIC if site['platform'] == 'auto' else Platform(site['platform'])
        google_taxonomy_options(CategoryScope(scope_platform,site['shop_url']),
            category_ids=targets,mappings=rules,taxonomy=catalog)
    if profile['schema_version'] == 2:
        if transport is not None:
            raise ValueError('HTTP transport injection is only supported for static profiles')
        from .live_production import verify_production
        return verify_production(profile_path,profile,sites,out,live=live,controlled=controlled,
                                 denied=policy_denial,fingerprint=runtime_fingerprint,
                                 map_products=map_products)
    started = time.monotonic(); deadline = started + profile['limits']['seconds']
    report = dict(schema_version=1,run_id=uuid4().hex,started_at=now(),mode='controlled' if transport is not None else 'live' if live else 'preflight',
        status='needs_review',live_verified=False,profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),
        catalog_fingerprint=catalog.manifest.fingerprint,code_sha256=runtime_fingerprint(),
        usage=dict(requests=0,products=0),sites=[])
    out.mkdir(parents=True)

    def save(name, value):
        encoded = json.dumps(value,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode()
        if len(encoded) > 1048576:
            raise ValueError('Artifact exceeds1MiB')
        atomic_json(str(out/name),value,compact=True)
        return name

    def command(args, filename):
        remaining = deadline-time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Shared live deadline reached')
        argv = [sys.executable,'-m','shopextract.cli','--config',profile['cli_config'],*args]
        result = subprocess.run(argv,capture_output=True,timeout=remaining)
        if len(result.stdout)>1048576 or len(result.stderr)>1048576:
            raise ValueError('CLI output exceeds1MiB')
        data = json.loads(result.stdout)
        save(filename,data)
        return dict(argv=argv,exit_code=result.returncode,output=filename,
            sha256=sha256((out/filename).read_bytes()).hexdigest(),stdout_sha256=sha256(result.stdout).hexdigest()),data

    with httpx.Client(transport=transport,follow_redirects=False,timeout=15,headers={'User-Agent':'ShopExtract bounded taxonomy verification'}) as client:
        for site in sites:
            item = dict(id=site['id'],url=site['url'],fetch={'status':'not_run'},parser={'status':'not_run'},
                mapping={'status':'not_run','classifications':[]},export={'verified':False},artifacts={})
            report['sites'].append(item)
            if not live:
                continue
            denied = policy_denial(site['url']) if transport is None else None
            if denied:
                item['fetch'] = dict(status='skipped_network_policy',policy=denied,observed_at=now())
                continue
            try:
                url=site['url'];body=None
                for redirect in range(3):
                    if time.monotonic()>=deadline or report['usage']['requests']>=profile['limits']['requests']:
                        raise TimeoutError('Shared request/time budget reached')
                    report['usage']['requests']+=1
                    with client.stream('GET',url,timeout=min(15,deadline-time.monotonic())) as response:
                        if response.status_code in (301,302,303,307,308):
                            target=urljoin(url,response.headers.get('location',''))
                            if redirect==2 or not response.headers.get('location') or not in_scope(target,site['shop_url']):
                                raise ValueError('Redirect exceeds selected source scope/budget')
                            url=target;continue
                        if response.status_code!=200:
                            item['fetch']=dict(status='blocked' if response.status_code in (401,403,429) else 'failed',http_status=response.status_code,url=url,observed_at=now())
                            break
                        chunks=[];size=0
                        for chunk in response.iter_bytes():
                            size+=len(chunk)
                            if size>profile['limits']['response_bytes'] or time.monotonic()>deadline:
                                raise ValueError('Source exceeds shared byte/time budget')
                            chunks.append(chunk)
                        body=b''.join(chunks)
                        item['fetch']=dict(status='success',http_status=200,url=url,bytes=size,sha256=sha256(body).hexdigest(),observed_at=now())
                        break
                if body is None:
                    continue
                source_name=site['id']+'.source';(out/source_name).write_bytes(body);item['artifacts']['source']=source_name
                remaining=profile['limits']['products']-report['usage']['products']
                if remaining<=0:
                    raise ValueError('Shared product budget reached')
                raw=parse_source(site,body.decode('utf-8'),url,remaining)
                item['parser']=dict(status='success' if raw else 'unavailable',products=len(raw))
                report['usage']['products']+=len(raw)
                if not raw:
                    continue
                map_products(site,raw,item,out,profile,save,command)
            except (httpx.HTTPError,OSError,ValueError,TimeoutError,subprocess.TimeoutExpired) as error:
                item['error']=type(error).__name__+': '+str(error)[:240]
                if item['fetch']['status']=='not_run':
                    item['fetch']=dict(status='blocked',observed_at=now())
    success=all(s['mapping']['status']=='mapped' and s['export']['verified'] for s in report['sites'])
    blocked=any(s['fetch']['status'] in ('blocked','failed','skipped_network_policy') for s in report['sites'])
    report['status']='pass' if success else 'blocked' if blocked else 'needs_review'
    if any('error' in s and s['fetch']['status']=='success' for s in report['sites']):
        report['status']='fail'
    report['live_verified']=report['status']=='pass' and report['mode']=='live'
    report['finished_at']=now();report['elapsed_seconds']=time.monotonic()-started
    if report['profile_sha256']!=sha256(profile_path.read_bytes()).hexdigest() or report['code_sha256']!=runtime_fingerprint():
        raise ValueError('Profile or runtime changed during verification')
    save('report.json',report)
    return report


def map_products(site, raw, item, out, profile, save, command):
    """Shared raw-capture → actual Google CLI → export/sidecar verification."""
    raw_file=save(site['id']+'.raw.json',raw);rules_file=save(site['id']+'.rules.json',site['mapping_rules'])
    item['artifacts']['raw']=raw_file
    args=['taxonomy','google','--catalog-root',profile['catalog_root'],'--fingerprint',profile['catalog_fingerprint'],
        'normalize',str(out/raw_file),'--shop-url',site['shop_url'],'--platform',site['platform'],
        '--mapping',str(out/rules_file),'--allow-unknown-source-version']
    invocation,data=command(args,site['id']+'.normalized.json');item['cli']=invocation
    if invocation['exit_code']!=0 or not data.get('ok'):
        item['mapping']['status']='failed';return
    categorized_from_value(data)
    classifications=data['data']['classifications']
    item['mapping']=dict(status='mapped' if classifications and all(c['status']=='mapped' for c in classifications) else 'needs_review',classifications=classifications)
    csv=site['id']+'.csv';sidecar=site['id']+'.categories.json'
    exported,export_data=command(['export',str(out/invocation['output']),'--format','csv','--output',str(out/csv),
        '--categories-output',str(out/sidecar)],site['id']+'.export.json')
    if exported['exit_code']==0 and export_data.get('ok'):
        from ..._cli_data import categorized_from_value as decode
        loaded=decode(json.loads((out/sidecar).read_text()))
        item['export']=dict(verified=len(loaded)==len(raw),cli=exported,payload=csv,companion=sidecar,
            payload_sha256=sha256((out/csv).read_bytes()).hexdigest(),companion_sha256=sha256((out/sidecar).read_bytes()).hexdigest())
