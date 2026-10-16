"""Predeclared bounded native Magento/Woo additional live checks."""
from __future__ import annotations

import asyncio
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import sys

import httpx

from shopextract import Platform, resolve_fields
from shopextract._capture import capture
from shopextract._normalize import normalize
from shopextract.extractors.magento_graphql import _QUERY
from shopextract.monitor.evidence import get_evidence, load_snapshot, save_snapshot
from shopextract.monitor.reliable import reliable_changes

OUT = Path(__file__).parent
RAW = OUT / 'raw'
TARGETS = [
    ('magento', Platform.MAGENTO, 'https://magento2-demo.magebit.com/graphql',
     'https://magento2-demo.magebit.com', 'magento_graphql'),
    ('woo', Platform.WOOCOMMERCE,
     'https://demo.athemes.com/botiga/wp-json/wc/store/v1/products?per_page=2&page=1',
     'https://demo.athemes.com/botiga', 'woocommerce_api'),
]


def write_summary(summary):
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2, default=str) + '\n')


async def fetch(client, endpoint, platform):
    kwargs = {'params': {'query': _QUERY, 'variables': json.dumps({'size': 2, 'page': 1})}} if platform == Platform.MAGENTO else {}
    async with client.stream('GET', endpoint, **kwargs) as response:
        response.raise_for_status()
        if response.is_redirect:
            raise RuntimeError('Redirect stopped without following')
        chunks, size = [], 0
        async for chunk in response.aiter_bytes():
            size += len(chunk)
            if size > 1024 * 1024:
                raise ValueError('Response exceeds 1 MiB')
            chunks.append(chunk)
        return json.loads(b''.join(chunks)), str(response.url), size


def inspect_snapshot(db, sid, source_url, observed_at):
    loaded = load_snapshot(sid, db_path=str(db))
    checks, support = 0, Counter()
    with sqlite3.connect(db) as conn:
        captured_at = datetime.fromisoformat(conn.execute('SELECT created_at FROM snapshots WHERE id=?', (sid,)).fetchone()[0])
    for index, product in enumerate(loaded):
        graph = getattr(product, 'evidence_contract', None)
        states = {r.field_path: r.state.value for r in resolve_fields(graph, as_of=captured_at).resolutions} if graph else {}
        for path in ['/price', '/currency', '/in_stock']:
            support[path + ':' + states.get(path, 'unsupported')] += 1
        owners = [(product, f'product/{index}')] + [(v, f'product/{index}/variant/{j}') for j, v in enumerate(product.variants)]
        for owner, key in owners:
            contract = getattr(owner, 'evidence_contract', None)
            for evidence in contract.evidence if contract else []:
                lookup = get_evidence(evidence.evidence_id, snapshot_id=sid, record_key=key, db_path=str(db))
                assert lookup.status == 'available'
                retained = lookup.evidence
                assert retained.source_url == source_url and retained.observed_at == observed_at
                assert retained.resolve_pointer() == evidence.resolve_pointer()
                checks += 1
    assert checks > 0
    return loaded, checks, dict(support)


def compare(db, domain, old, new):
    report = reliable_changes(domain, previous_snapshot_id=old, current_snapshot_id=new, db_path=str(db))
    assert not any(e['kind'] == 'product_removed' for e in report['events'])
    for candidate in report['candidates']:
        for side in ['old', 'new']:
            for ref in candidate[side]['references']:
                for eid in ref['evidence_ids']:
                    assert get_evidence(eid, snapshot_id=ref['snapshot_id'], record_key=ref['record_key'], db_path=str(db)).status == 'available'
    replay = reliable_changes(domain, previous_snapshot_id=old, current_snapshot_id=new, db_path=str(db))
    assert replay['report_id'] == report['report_id'] and replay['events'] == report['events']
    assert replay['new_events'] == []
    return report


async def main():
    RAW.mkdir(exist_ok=True)
    if any(RAW.iterdir()):
        raise RuntimeError('Raw evidence already exists; preserve prior run, no automatic rerun')
    summary = {'status': 'running', 'maximum_requests': 4, 'requests': 0,
               'retries': 0, 'platforms': []}
    write_summary(summary)
    for name, platform, endpoint, base, method in TARGETS:
        item = {'platform': name, 'endpoint': endpoint, 'status': 'running',
                'requests': 0, 'captures': [], 'commercial_change': 'inconclusive until actual captured differences'}
        summary['platforms'].append(item)
        write_summary(summary)
        domain = httpx.URL(base).host
        scope = 'additional-live:' + name + ':page1-size2'
        db = RAW / (name + '.db')
        metadata = {'observation_scope': scope, 'catalog_complete': False,
                    'incompleteness_reasons': ['bounded_live_sample'], 'max_urls': 1}
        ids = []
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=False,
                limits=httpx.Limits(max_connections=1, max_keepalive_connections=1),
                headers={'Accept': 'application/json', 'User-Agent': 'ShopExtract/0.1 read-only verification'}) as client:
                for number in range(2):
                    summary['requests'] += 1
                    item['requests'] += 1
                    write_summary(summary)
                    payload, source_url, size = await asyncio.wait_for(fetch(client, endpoint, platform), timeout=20)
                    if platform == Platform.MAGENTO:
                        if payload.get('errors'):
                            raise ValueError('GraphQL errors: ' + str(payload['errors'])[:300])
                        rows = payload['data']['products']['items']
                    else:
                        rows = payload
                    if not isinstance(rows, list) or not rows:
                        raise ValueError('Native source returned no products')
                    observed_at = datetime.now(timezone.utc)
                    products = []
                    for row in rows[:2]:
                        raw = deepcopy(row)
                        if 'variants' in raw:
                            raw['variants'] = raw['variants'][:4]
                        capture(raw, source_url, method, observed_at=observed_at)
                        product = normalize(raw, platform, base)
                        if product is None:
                            raise ValueError('Native normalization rejected product')
                        product.variants = product.variants[:4]
                        products.append(product)
                    sid = save_snapshot(products, domain, db_path=str(db), metadata=metadata)
                    loaded, checks, support = inspect_snapshot(db, sid, source_url, observed_at)
                    ids.append(sid)
                    (RAW / f'{name}-{number+1}.json').write_text(json.dumps(payload, ensure_ascii=False))
                    item['captures'].append({'snapshot_id': sid, 'response_bytes': size,
                        'products': len(loaded), 'variants': sum(len(p.variants) for p in loaded),
                        'evidence_checks': checks, 'field_support': support,
                        'canonical_ids': [p.canonical_product_id for p in loaded]})
                    item['smoke'] = 'passed'
                    write_summary(summary)  # persisted before repeat/next platform
            old = load_snapshot(ids[0], db_path=str(db))
            current = load_snapshot(ids[1], db_path=str(db))
            anchored = {p.external_id: p.canonical_product_id for p in old if p.external_id}
            shared = 0
            for product in current:
                if product.external_id in anchored:
                    assert product.canonical_product_id == anchored[product.external_id]
                    shared += 1
            assert shared > 0
            result = compare(db, domain, *ids)
            (RAW / f'{name}-report.txt').write_text(repr(result))
            # Offline-derived partial omission: no source field/value mutations.
            derived = save_snapshot(current[1:], domain, db_path=str(db), metadata=metadata)
            omission = compare(db, domain, ids[1], derived)
            item.update(status='passed', shared_anchored_ids=shared,
                candidates=len(result['candidates']), events=len(result['events']),
                replay_new_events=0, diagnostics=dict(Counter(d['reason'] for d in result['diagnostics'])),
                offline_derived_omission={'label': 'offline derived; not an actual live removal',
                    'snapshot_id': derived, 'confirmed_removals': sum(e['kind'] == 'product_removed' for e in omission['events'])},
                commercial_change='captured differences; inspect retained source' if result['candidates'] else 'inconclusive: repeat captures had no tracked differences')
        except Exception as exc:
            item.update(status='blocked', error=f'{type(exc).__name__}: {exc}')
        write_summary(summary)  # saved before next independent platform
    summary['status'] = 'passed' if all(p['status'] == 'passed' for p in summary['platforms']) else 'partial_or_blocked'
    write_summary(summary)
    print(json.dumps(summary, default=str))
    return 0 if summary['status'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
