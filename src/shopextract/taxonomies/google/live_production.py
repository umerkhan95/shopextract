"""Production verification orchestration; source algorithms stay in the core."""
from datetime import datetime, timezone
from hashlib import sha256
import json
import sys
import time
from uuid import uuid4

from ..._cli_data import atomic_json
from ..._models import ExtractionTier, Platform
from ..._owned_process import run_owned


def _now():
    return datetime.now(timezone.utc).isoformat()


def worker_command():
    return [sys.executable, '-m', 'shopextract.taxonomies.google.live_worker']


def _decode(source):
    def invalid(_):
        raise ValueError('Nonfinite worker value')
    return json.loads(source, parse_constant=invalid)


def validate_result(value, maximum, *, declared_platform='auto'):
    fields = {'schema_version', 'raw_products', 'tier', 'urls_attempted', 'urls_succeeded',
              'errors', 'catalog_complete', 'incompleteness_reasons', 'truncated', 'browser', 'llm', 'platform'}
    if not isinstance(value, dict) or set(value) != fields or type(value['schema_version']) is not int or value['schema_version'] != 1:
        raise ValueError('Invalid production worker result')
    raw = value['raw_products']
    Platform(value['platform'])
    if declared_platform != 'auto' and value['platform'] != declared_platform:
        raise ValueError('Worker platform differs from explicit profile platform')
    if (not isinstance(raw, list) or len(raw) > maximum or any(not isinstance(r, dict) for r in raw)
        or value['tier'] not in {tier.value for tier in ExtractionTier}
        or any(type(value[k]) is not int or value[k] < 0 for k in ('urls_attempted', 'urls_succeeded'))
        or value['catalog_complete'] not in (True, False, None)
        or (value['catalog_complete'] is not None and type(value['catalog_complete']) is not bool)
        or type(value['truncated']) is not bool
        or not isinstance(value['browser'], dict) or type(value['browser'].get('enabled')) is not bool
        or not isinstance(value['llm'], dict) or type(value['llm'].get('enabled')) is not bool
        or value['browser'] != {'enabled': True, 'attempted': None}
        or value['llm'] != {'enabled': False, 'reason': 'no_configured_budget'}):
        raise ValueError('Invalid production extraction metadata')
    for key in ('errors', 'incompleteness_reasons'):
        if not isinstance(value[key], list) or len(value[key]) > 20 or any(not isinstance(x, str) for x in value[key]):
            raise ValueError('Invalid production diagnostics')
    return value


def verify_production(profile_path, profile, sites, out, *, live, denied, fingerprint, map_products, controlled=False):
    started = time.monotonic()
    deadline = started + profile['limits']['seconds']
    maximum = profile['limits']['output_bytes']
    report = dict(schema_version=2, run_id=uuid4().hex, started_at=_now(),
        mode='controlled' if controlled else 'live' if live else 'preflight', status='needs_review', live_verified=False,
        profile_sha256=sha256(profile_path.read_bytes()).hexdigest(),
        catalog_fingerprint=profile['catalog_fingerprint'], code_sha256=fingerprint(),
        usage=dict(pipeline_invocations=0, products=0, network_requests=None, network_bytes=None),
        network_limits='native_pipeline_request_bytes_and_redirect_scope_unobserved', sites=[])
    out.mkdir(parents=True)
    cleanup_failed = False

    def save(name, value):
        data = json.dumps(value, ensure_ascii=False, allow_nan=False, separators=(',', ':')).encode()
        if len(data) > maximum:
            raise ValueError('Production artifact exceeds output byte limit')
        atomic_json(str(out / name), value, compact=True)
        return name

    def execute(argv, payload=b''):
        nonlocal cleanup_failed
        if cleanup_failed:
            raise RuntimeError('Prior worker cleanup failed')
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError('Shared production deadline reached')
        result = run_owned(argv, input_bytes=payload, timeout=min(120, remaining), maximum_bytes=maximum)
        if not result['cleanup_complete']:
            cleanup_failed = True
            raise RuntimeError('Worker cleanup failed; no subsequent worker may start')
        if result['timed_out']:
            raise TimeoutError('Production worker timed out')
        if result['output_exceeded']:
            raise ValueError('Production worker output limit exceeded')
        return result

    def command(args, filename):
        argv = [sys.executable, '-m', 'shopextract.cli', '--config', profile['cli_config'], *args]
        result = execute(argv)
        value = _decode(result['stdout'])
        if not isinstance(value, dict):
            raise ValueError('Invalid CLI result')
        save(filename, value)
        return dict(argv=argv, exit_code=result['returncode'], output=filename,
            sha256=sha256((out / filename).read_bytes()).hexdigest(),
            stdout_sha256=sha256(result['stdout']).hexdigest(), cleanup_complete=True), value

    for site in sites:
        item = dict(id=site['id'], url=site['url'], fetch={'status': 'not_applicable'},
            parser={'status': 'not_applicable'}, extraction={'path': 'production', 'status': 'not_run'},
            mapping={'status': 'not_run', 'classifications': []}, export={'verified': False}, artifacts={})
        report['sites'].append(item)
        if not live:
            continue
        policy = denied(site['url'])
        if policy:
            item['fetch'] = dict(status='skipped_network_policy', policy=policy, observed_at=_now())
            continue
        if (cleanup_failed or report['usage']['pipeline_invocations'] >= profile['limits']['invocations']
            or report['usage']['products'] >= profile['limits']['products']
            or time.monotonic() >= deadline):
            item['extraction']['status'] = 'skipped_budget' if not cleanup_failed else 'skipped_cleanup_failure'
            continue
        stage = 'extraction'
        try:
            count = profile['limits']['products'] - report['usage']['products']
            remaining = deadline - time.monotonic()
            payload = dict(url=site['url'], platform=site['platform'], shop_url=site['shop_url'],
                           max_products=count, timeout=max(.001, remaining - min(.75, remaining / 3)))
            report['usage']['pipeline_invocations'] += 1
            result = execute(worker_command(), json.dumps(payload).encode())
            item['extraction']['process'] = dict(returncode=result['returncode'], cleanup_complete=True)
            if result['returncode'] != 0:
                raise ValueError('Native production extraction failed; inspect browser/source configuration')
            value = validate_result(_decode(result['stdout']), count, declared_platform=site['platform'])
            filename = save(site['id'] + '.extraction.json', value)
            item['artifacts']['extraction'] = filename
            raw = value.pop('raw_products')
            item['extraction'].update(value, status='success' if raw else 'unavailable',
                artifact_sha256=sha256((out / filename).read_bytes()).hexdigest(),
                attempts=dict(api='unknown', discovery='unknown', unified='unknown', css='unknown'))
            report['usage']['products'] += len(raw)
            if raw:
                stage = 'mapping_export'
                effective_site = dict(site, platform=value['platform'])
                map_products(effective_site, raw, item, out, profile, save, command)
                item['artifacts']['raw_sha256'] = sha256((out / item['artifacts']['raw']).read_bytes()).hexdigest()
        except (OSError, ValueError, RuntimeError, TimeoutError, TypeError, KeyError) as error:
            if stage == 'extraction':
                item['extraction']['status'] = 'failed'
            elif item['mapping']['status'] in ('not_run', 'needs_review'):
                item['mapping']['status'] = 'failed'
            else:
                item['export']['status'] = 'failed'
            item['error_stage'] = stage
            item['error'] = str(error)[:240]
            item['extraction']['cleanup_complete'] = not cleanup_failed
    success = all(s['mapping']['status'] == 'mapped' and s['export']['verified'] for s in report['sites'])
    blocked = any(s['fetch']['status'] == 'skipped_network_policy' for s in report['sites'])
    failed = any('error' in s or s['extraction']['status'] in ('failed', 'skipped_cleanup_failure') for s in report['sites'])
    report['status'] = 'fail' if failed else 'pass' if success else 'blocked' if blocked else 'needs_review'
    report['live_verified'] = report['status'] == 'pass' and report['mode'] == 'live'
    report['finished_at'] = _now()
    report['elapsed_seconds'] = time.monotonic() - started
    if (report['profile_sha256'] != sha256(profile_path.read_bytes()).hexdigest()
            or report['code_sha256'] != fingerprint()):
        raise ValueError('Profile or runtime changed during production verification')
    # Reports contain up to two separately bounded extraction/mapping results.
    # Use the same1MiB artifact ceiling without truncating classifications.
    save('report.json', report)
    return report
