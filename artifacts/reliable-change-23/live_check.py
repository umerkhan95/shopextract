"""Bounded live pipeline smoke for #23. Run only after offline checks pass."""
from __future__ import annotations

import asyncio
from collections import Counter
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

import httpx

from shopextract import Platform
from shopextract._capture import capture
from shopextract._normalize import normalize
from shopextract.monitor.evidence import get_evidence, load_snapshot, save_snapshot
from shopextract.monitor.reliable import reliable_changes

URL = 'https://www.boardgamebliss.com/products.json?limit=2&page=1'
DOMAIN = 'www.boardgamebliss.com'
SCOPE = 'live-smoke:boardgamebliss:products-page-1-limit-2'
OUT = Path(__file__).parent / 'live'


async def fetch(client):
    chunks, size = [], 0
    async with client.stream('GET', URL) as response:
        response.raise_for_status()
        if response.is_redirect:
            raise RuntimeError('Redirect stopped; no extra request made')
        async for chunk in response.aiter_bytes():
            size += len(chunk)
            if size > 1024 * 1024:
                raise RuntimeError('Response exceeds 1 MiB')
            chunks.append(chunk)
        return json.loads(b''.join(chunks)), str(response.url), size


async def main():
    OUT.mkdir(exist_ok=True)
    db = OUT / 'snapshots.db'
    if db.exists():
        raise RuntimeError('Existing live database: preserve prior evidence; choose fresh output directory')
    summary = {'status': 'running', 'requests': 0, 'network_retries': 0,
               'removal_coverage': 'partial; no confirmed removals allowed',
               'commercial_change': 'inconclusive until captured differences', 'captures': []}
    def save_summary():
        (OUT / 'summary.json').write_text(json.dumps(summary, indent=2, default=str) + '\n')
    save_summary()
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=False,
            limits=httpx.Limits(max_connections=1, max_keepalive_connections=1),
            headers={'Accept': 'application/json', 'User-Agent': 'ShopExtract/0.1 read-only verification'}) as client:
            ids = []
            for attempt in range(2):
                summary['requests'] += 1
                payload, source_url, size = await asyncio.wait_for(fetch(client), timeout=20)
                rows = payload.get('products')
                if not isinstance(rows, list) or not rows:
                    raise RuntimeError('No products returned')
                at = datetime.now(timezone.utc)
                products = []
                for row in rows[:2]:
                    raw = deepcopy(row)
                    raw['variants'] = raw.get('variants', [])[:4]
                    capture(raw, source_url, 'api', observed_at=at)
                    p = normalize(raw, Platform.SHOPIFY, 'https://' + DOMAIN)
                    if p is None:
                        raise RuntimeError('Live normalization rejected product')
                    products.append(p)
                sid = save_snapshot(products, DOMAIN, db_path=str(db), metadata={
                    'observation_scope': SCOPE, 'catalog_complete': False,
                    'incompleteness_reasons': ['bounded_live_sample'], 'max_urls': 1})
                loaded = load_snapshot(sid, db_path=str(db))
                assert len(loaded) == len(products)
                supported = 0
                for p in loaded:
                    for owner, key in [(p, f'product/{loaded.index(p)}')] + [
                        (v, f'product/{loaded.index(p)}/variant/{j}') for j, v in enumerate(p.variants)]:
                        graph = getattr(owner, 'evidence_contract', None)
                        if graph:
                            for e in graph.evidence:
                                lookup = get_evidence(e.evidence_id, snapshot_id=sid,
                                                       record_key=key, db_path=str(db))
                                assert lookup.status == 'available'
                                assert lookup.evidence.source_url == source_url
                                assert lookup.evidence.observed_at == at
                                assert lookup.evidence.resolve_pointer() == e.resolve_pointer()
                                supported += 1
                assert supported > 0
                ids.append(sid)
                (OUT / f'capture-{attempt+1}.json').write_text(json.dumps(payload, ensure_ascii=False))
                summary['captures'].append({'snapshot_id': sid, 'response_bytes': size,
                    'products': len(loaded), 'variants': sum(len(p.variants) for p in loaded),
                    'retained_evidence_checks': supported,
                    'canonical_ids': [p.canonical_product_id for p in loaded], 'source_url': source_url})
                save_summary()  # initial smoke evidence saved before second request
            report = reliable_changes(DOMAIN, previous_snapshot_id=ids[0],
                                      current_snapshot_id=ids[1], db_path=str(db))
            assert not any(e['kind'] == 'product_removed' for e in report['events'])
            first_ids = {p.external_id: p.canonical_product_id for p in load_snapshot(ids[0], db_path=str(db))}
            for p in load_snapshot(ids[1], db_path=str(db)):
                if p.external_id in first_ids:
                    assert p.canonical_product_id == first_ids[p.external_id]
            for c in report['candidates']:
                for side in ['old', 'new']:
                    for ref in c[side]['references']:
                        for eid in ref['evidence_ids']:
                            assert get_evidence(eid, snapshot_id=ref['snapshot_id'],
                                record_key=ref['record_key'], db_path=str(db)).status == 'available'
            replay = reliable_changes(DOMAIN, previous_snapshot_id=ids[0],
                                      current_snapshot_id=ids[1], db_path=str(db))
            assert replay['report_id'] == report['report_id']
            assert replay['events'] == report['events'] and replay['new_events'] == []
            summary.update(status='passed', report_id=report['report_id'],
                           candidates=len(report['candidates']), events=len(report['events']),
                           replay_new_events=len(replay['new_events']),
                           diagnostics=dict(Counter(d['reason'] for d in report['diagnostics'])))
            if report['candidates']:
                summary['commercial_change'] = 'captured differences; inspect report and sources'
            (OUT / 'report.txt').write_text(repr(report))
    except Exception as exc:
        summary.update(status='blocked', error=f'{type(exc).__name__}: {exc}')
        save_summary()
        print(json.dumps(summary, default=str))
        return 1
    save_summary()
    print(json.dumps(summary, default=str))
    return 0


if __name__ == '__main__':
    sys.exit(asyncio.run(main()))
