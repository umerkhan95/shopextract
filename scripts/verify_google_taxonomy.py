#!/usr/bin/env python3
"""Bounded, offline full-target integration verifier; never fetches source data."""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

MAX_WIRE = 1048576
SHOP = 'https://synthetic-google-verifier.invalid'


def encoded(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(',', ':'), allow_nan=False).encode()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def write(path, value):
    data = encoded(value) + b'\n'
    if len(data) > MAX_WIRE:
        raise ValueError('Verifier artifact exceeds1MiB')
    path = Path(path)
    stage = path.with_suffix(path.suffix + '.tmp')
    stage.write_bytes(data)
    stage.replace(path)


def read(path):
    data = Path(path).read_bytes()
    if len(data) > MAX_WIRE:
        raise ValueError('Verifier input artifact exceeds1MiB')
    return json.loads(data)


def identity(args):
    root = Path(__file__).resolve().parents[1]
    code = [Path(__file__).resolve(), *sorted((root / 'src/shopextract').rglob('*.py')),
            *sorted((root / 'src/shopextract/schemas').glob('*.json')),
            root / 'specs/013-aggregation-first/implementation/verification-manifest.md']
    actual_crosswalk = digest(Path(args.crosswalk).read_bytes())
    assert actual_crosswalk == args.crosswalk_sha256, 'Crosswalk source hash differs'
    return dict(code=digest(encoded({str(p.relative_to(root)): digest(p.read_bytes()) for p in code})),
                source=digest(Path(args.source_taxonomy).read_bytes()),
                crosswalk=actual_crosswalk,
                fingerprint=args.fingerprint, python=sys.version,
                batch_size=args.batch_size, seed=13031, policy='google-full-target-v1')


def source_oracle(args, taxonomy):
    import yaml  # Verification-only source dependency, not ordinary catalog lookup.
    rows = yaml.safe_load(Path(args.source_taxonomy).read_text())
    paths = {str(row['id']): row['full_name'] for row in rows}
    assert len(paths) == len(rows) == 5595, 'Original source ID set differs'
    assert len(set(paths.values())) == len(paths), 'Original source duplicate path'
    by_path = {path: key for key, path in paths.items()}
    ids = sorted(paths, key=int)
    assert {node.id for node in taxonomy.iter_categories()} == set(ids)
    parents = {key: by_path[path.rsplit(' > ', 1)[0]] if ' > ' in path else None
               for key, path in paths.items()}
    children = {key: set() for key in ids}
    for key, parent in parents.items():
        if parent is not None:
            children[parent].add(key)
    for key in ids:
        node = taxonomy.category(key)
        assert node.full_name == paths[key] and node.parent_id == parents[key]
        assert set(node.child_ids) == children[key]
        assert taxonomy.resolve_path(paths[key]).id == key
        assert {value.id for value in taxonomy.children(key)} == children[key]
        expected, parent = [], parents[key]
        while parent is not None:
            expected.insert(0, parent)
            parent = parents[parent]
        assert [value.id for value in taxonomy.ancestors(key)] == expected
    return ids, paths, dict(categories=len(ids), roots=sum(v is None for v in parents.values()),
                            leaves=sum(not v for v in children.values()))


def invoke(runner, main, arguments):
    result = runner.invoke(main, ['--diagnostics', 'quiet', *arguments], catch_exceptions=False)
    output = result.stdout.encode()
    assert len(output) <= MAX_WIRE, 'CLI response exceeds1MiB'
    assert result.exit_code == 0, (arguments[:3], result.exit_code, output[:500])
    value = json.loads(output)
    assert value['ok'] and value['completeness'] == 'complete', value.get('error')
    return value['data'], len(output)


def batch(args, taxonomy, keys, paths, offset):
    from click.testing import CliRunner
    from shopextract.cli import main
    from shopextract.extractors.feed import GoogleFeedExtractor
    from shopextract.categories.portable import categorized_product_from_record
    from shopextract.taxonomies.google import effective_google_category
    workspace = Path(args.output_dir) / 'work'
    workspace.mkdir(exist_ok=True)
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(['id', 'title', 'price', 'google_product_category'])
    for index, key in enumerate(keys):
        writer.writerow(['synthetic-' + key, 'Synthetic widget ' + key, '1 EUR',
                         paths[key] if (offset + index) % 2 else key])
    raw = GoogleFeedExtractor._parse_csv(buffer.getvalue(), SHOP + '/feed.csv', include_categories=True)
    for record in raw:
        record['_capture']['at'] = '2026-10-31T00:00:00+00:00'
    write(workspace / 'ids.json', keys)
    write(workspace / 'raw.json', raw)
    runner = CliRunner()
    prefix = ['taxonomy', 'google', '--catalog-root', args.catalog_root,
              '--fingerprint', args.fingerprint]
    looked, lookup_bytes = invoke(runner, main, [*prefix, 'lookup-batch', str(workspace / 'ids.json')])
    assert [node['id'] for node in looked['categories']] == keys
    normalized, normalized_bytes = invoke(runner, main, [*prefix, 'normalize', str(workspace / 'raw.json'),
        '--shop-url', SHOP, '--allow-unknown-source-version'])
    assert [value['target_id'] for value in normalized['classifications']] == keys
    assert all(value['status'] == 'mapped' for value in normalized['classifications'])
    assert len(normalized['categorized_products']) == len(keys)
    bindings = []
    for key, wire in zip(keys, normalized['categorized_products'], strict=True):
        restored = categorized_product_from_record(wire)
        assert restored.product.external_id == 'synthetic-' + key
        standard = [o for o in restored.observations if o.taxonomy_kind == 'standard']
        assert standard and all(term.ref.taxonomy_version is None for o in standard for term in o.terms)
        assert any(f.evidence and f.support.value == 'observed' for o in standard for f in o.facts)
        assert all(isinstance(v, str) for v in restored.product.attributes.values())
        bindings.append(restored.original_binding)
    write(workspace / 'normalized.json', normalized['categorized_products'])
    invoke(runner, main, ['export', str(workspace / 'normalized.json'), '--format', 'csv',
        '--output', str(workspace / 'products.csv'), '--categories-output', str(workspace / 'categories.json')])
    values = read(workspace / 'categories.json')
    reload_bytes = (workspace / 'categories.json').stat().st_size
    if args.mode == 'smoke':
        reloaded, _ = invoke(runner, main, ['categories', 'record', 'load', str(workspace / 'categories.json')])
        assert reloaded['categorized_products'] == values
    assert len(values) == len(keys)
    for key, binding, wire in zip(keys, bindings, values, strict=True):
        wrapped = categorized_product_from_record(wire)
        assert wrapped.original_binding == binding and wrapped.product.external_id == 'synthetic-' + key
        assert effective_google_category(wrapped, taxonomy=taxonomy).target_id == key
    return dict(lookup_bytes=lookup_bytes, normalize_bytes=normalized_bytes, reload_bytes=reload_bytes)


def ledger(args, taxonomy):
    import yaml
    from shopextract.taxonomies.shopify import load_shopify_taxonomy
    from shopextract.taxonomies.google import load_shopify_google_crosswalk, audit_source_categories
    source = load_shopify_taxonomy(catalog_root=args.shopify_catalog_root)
    index = load_shopify_google_crosswalk(args.crosswalk, source_catalog=source,
        target_catalog=taxonomy, expected_sha256=args.crosswalk_sha256)
    document = yaml.safe_load(Path(args.crosswalk).read_text())
    original = {row['input']['product_category_id']: tuple(row['output']['product_category_id'])
                for row in document['rules']}
    excluded = set(document['unmapped_product_category_ids'])
    rows = audit_source_categories(index, source)
    assert len(rows) == len({row.source_id for row in rows}) == 14606
    for row in rows:
        assert row.target_ids == tuple(sorted(set(original.get(row.source_id, ())), key=int))
        assert row.status == ('mapped-single' if row.source_id in original else 'explicit-upstream-unmapped')
        assert row.source_id in original or row.source_id in excluded
    counts = dict(Counter(row.status for row in rows))
    assert counts == {'mapped-single': 14528, 'explicit-upstream-unmapped': 78}
    targets = {target for row in rows for target in row.target_ids}
    assert len(targets) == 5455 and len(tuple(taxonomy.iter_categories())) - len(targets) == 140
    return dict(source_categories=len(rows), statuses=counts, targets_with_inbound=len(targets),
                targets_without_inbound=140, source_ids_digest=digest(encoded(sorted(r.source_id for r in rows))))


def worker(args):
    import socket
    def deny_network(*unused, **ignored):
        raise RuntimeError('Offline verifier forbids network connections')
    socket.socket.connect = socket.socket.connect_ex = deny_network
    from shopextract.taxonomies.google import load_google_taxonomy
    start = time.monotonic()
    out = Path(args.output_dir)
    expected_identity = identity(args)
    write(out / 'heartbeat.json', {'started': time.time(), 'stage': 'source-validation'})
    taxonomy = load_google_taxonomy(catalog_root=args.catalog_root, fingerprint=args.fingerprint)
    assert taxonomy.manifest.source_provenance.source_sha256 == expected_identity['source']
    keys, paths, counts = source_oracle(args, taxonomy)
    if args.mode == 'ledger':
        result = ledger(args, taxonomy)
        assert identity(args) == expected_identity, 'Code/source changed during ledger verification'
        write(out / 'worker-report.json', dict(ok=True, identity=expected_identity, phase='ledger',
              seconds=time.monotonic() - start, **result))
        return
    if args.mode == 'smoke':
        root = next(key for key in keys if not taxonomy.category(key).ancestor_ids)
        mid = next(key for key in keys if taxonomy.category(key).parent_id and taxonomy.category(key).child_ids)
        leaf = next(key for key in keys if not taxonomy.category(key).child_ids)
        selected = [root, mid, leaf]
    else:
        selected = keys[:100] if args.mode == 'measure' else keys
    if args.mode == 'sweep':
        smoke, measured = read(args.smoke_report), read(args.measure_report)
        assert all(r['ok'] and r['identity'] == expected_identity for r in (smoke, measured))
        assert smoke['phase'] == 'smoke' and measured['phase'] == 'measure'
        forecast = measured['seconds'] * len(keys) / measured['count'] * 1.25
        assert forecast <= 180, f'Forecast {forecast:.3f}s exceeds180s; stop for reviewed diagnosis'
    completed, receipts = [], []
    for offset in range(0, len(selected), args.batch_size):
        write(out / 'heartbeat.json', {'started': time.time(), 'stage': 'batch', 'offset': offset})
        began = time.monotonic()
        chunk = selected[offset:offset + args.batch_size]
        sizes = batch(args, taxonomy, chunk, paths, offset)
        completed.extend(chunk)
        receipt = dict(offset=offset, ids=chunk, seconds=time.monotonic() - began, **sizes)
        receipts.append(receipt)
        write(out / 'progress.json', dict(identity=expected_identity, passed_ids=completed, receipts=receipts))
    assert completed == selected and len(set(completed)) == len(selected)
    assert identity(args) == expected_identity, 'Code/source changed during verification'
    write(out / 'worker-report.json', dict(ok=True, phase=args.mode, identity=expected_identity,
        count=len(completed), ids_digest=digest(encoded(completed)), source_counts=counts,
        exact_ids=completed, batches=len(receipts), seconds=time.monotonic() - start,
        synthetic=True, actual_merchant_assignments=0))


def supervise(args):
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=False)
    start, peak, reason = time.monotonic(), 0, None
    limit = 120 if args.mode == 'ledger' else 180
    with (out / 'worker.log').open('wb') as log:
        child = subprocess.Popen([sys.executable, str(Path(__file__).resolve()), *sys.argv[1:], '--worker'],
                                 stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
        try:
            while child.poll() is None:
                rss = sum(int(line.split()[1]) * 1024 for line in subprocess.check_output(
                    ['ps', '-eo', 'pgid=,rss='], text=True, timeout=1).splitlines()
                    if len(line.split()) == 2 and int(line.split()[0]) == child.pid)
                peak = max(peak, rss)
                elapsed = time.monotonic() - start
                heartbeat = read(out / 'heartbeat.json') if (out / 'heartbeat.json').exists() else None
                if elapsed > limit: reason = 'total_timeout'
                elif rss > 512 * 1024 * 1024: reason = 'rss_limit'
                elif (out / 'worker.log').stat().st_size > MAX_WIRE: reason = 'log_limit'
                elif heartbeat and heartbeat['stage'] == 'batch' and time.time() - heartbeat['started'] > 15:
                    reason = 'batch_timeout'
                if reason:
                    break
                time.sleep(.1)
        finally:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGTERM)
                try: child.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    os.killpg(child.pid, signal.SIGKILL)
                    child.wait(timeout=1)
        code = child.wait()
    try:
        os.killpg(child.pid, 0)
        os.killpg(child.pid, signal.SIGKILL)
        gone = False
    except ProcessLookupError:
        gone = True
    report_path = out / 'worker-report.json'
    report = read(report_path) if report_path.exists() else {'ok': False, 'phase': args.mode}
    report.update(exit_code=code, resource_failure=reason, group_gone=gone,
                  peak_sampled_rss_bytes=peak, supervisor_seconds=time.monotonic() - start)
    report['ok'] = bool(report['ok'] and code == 0 and reason is None and gone)
    write(out / 'report.json', report)
    print(json.dumps({key: value for key, value in report.items() if key not in ('exact_ids', 'identity')}))
    return 0 if report['ok'] else 1


def arguments():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('catalog-root', 'source-taxonomy', 'crosswalk', 'crosswalk-sha256',
                 'shopify-catalog-root', 'fingerprint', 'output-dir'):
        parser.add_argument('--' + name, required=True)
    parser.add_argument('--mode', choices=('smoke', 'measure', 'sweep', 'ledger'), required=True)
    parser.add_argument('--batch-size', type=int, default=25)
    parser.add_argument('--smoke-report')
    parser.add_argument('--measure-report')
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    args = parser.parse_args()
    if not 1 <= args.batch_size <= 100:
        parser.error('Batch size must be1..100; native byte ceilings may require a smaller batch')
    if args.mode == 'sweep' and not (args.smoke_report and args.measure_report):
        parser.error('Sweep requires passed smoke and measurement report paths')
    return args


if __name__ == '__main__':
    options = arguments()
    if options.worker:
        worker(options)
    else:
        raise SystemExit(supervise(options))
