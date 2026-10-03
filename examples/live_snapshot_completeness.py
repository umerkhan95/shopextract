"""Fresh bounded live reproduction, preserving independent review evidence."""
import argparse
import asyncio
import json
import sqlite3
from dataclasses import asdict
from pathlib import Path

import shopextract as s
from shopextract.extractors.shopify import ShopifyExtractor

parser = argparse.ArgumentParser(description="Bounded live snapshot completeness regression")
parser.add_argument("--output-dir", default="artifacts/live-snapshot-completeness")
OUT = Path(parser.parse_args().output_dir)
OUT.mkdir(parents=True, exist_ok=True)
URL = 'https://www.boardgamebliss.com/collections/catan-series'
DOMAIN = 'www.boardgamebliss.com'


async def main():
    db = OUT / 'budget-snapshots.db'
    if db.exists():
        db.unlink()
    # Exact reproduction of the review: 18 -> 5, without probing past the budget.
    counts = [await s.snapshot(URL, db_path=str(db), max_urls=n) for n in (18, 5)]
    events = s.changes(DOMAIN, db_path=str(db))
    full = await s.extract(URL, max_urls=100)
    bounded = await ShopifyExtractor().extract(URL, max_products=5)
    with sqlite3.connect(db) as conn:
        metadata = conn.execute('SELECT catalog_complete, observation_scope, max_urls, incompleteness_reasons_json FROM snapshots ORDER BY id').fetchall()
    assert not any(x.change_type == s.ChangeType.REMOVED_PRODUCT for x in events)
    assert not bounded.complete and bounded.completeness_reason == 'product_budget_reached'
    assert full.catalog_complete is True
    # Prove a complete new observation followed by a limited one is also safe.
    complete_db = OUT / 'complete-to-limited.db'
    if complete_db.exists():
        complete_db.unlink()
    complete_counts = [await s.snapshot(URL, db_path=str(complete_db), max_urls=n) for n in (100, 5)]
    complete_events = s.changes(DOMAIN, db_path=str(complete_db))
    assert not any(x.change_type == s.ChangeType.REMOVED_PRODUCT for x in complete_events)
    with sqlite3.connect(complete_db) as conn:
        complete_metadata = conn.execute("SELECT catalog_complete, observation_scope, max_urls FROM snapshots ORDER BY id").fetchall()
    assert complete_metadata[0][0] == 1 and complete_metadata[1][0] == 0
    # Replay captured full products in the pre-upgrade schema, then make a fresh
    # live limited observation; this does not modify any supplier data.
    legacy_db = OUT / 'legacy-to-limited.db'
    if legacy_db.exists():
        legacy_db.unlink()
    with sqlite3.connect(legacy_db) as conn:
        conn.execute('CREATE TABLE snapshots(id INTEGER PRIMARY KEY AUTOINCREMENT, domain TEXT NOT NULL, products_json TEXT NOT NULL, created_at TEXT NOT NULL)')
        conn.execute('INSERT INTO snapshots(domain, products_json, created_at) VALUES(?,?,?)',
                     (DOMAIN, json.dumps([asdict(p) for p in full.products], default=str), '2026-09-30T00:00:00+00:00'))
    await s.snapshot(URL, db_path=str(legacy_db), max_urls=5)
    legacy_events = s.changes(DOMAIN, db_path=str(legacy_db))
    assert not any(x.change_type == s.ChangeType.REMOVED_PRODUCT for x in legacy_events)
    with sqlite3.connect(legacy_db) as conn:
        legacy_metadata = conn.execute('SELECT catalog_complete, observation_scope FROM snapshots ORDER BY id').fetchall()
    assert legacy_metadata[0] == (None, None)
    report = {'review_reproduction_counts': counts, 'events': [asdict(x) for x in events],
              'fresh_full_count': len(full.products), 'fresh_full_complete': full.catalog_complete,
              'bounded_complete': bounded.complete, 'bounded_reason': bounded.completeness_reason,
              'snapshot_metadata': metadata, 'complete_to_limited_counts': complete_counts,
              'complete_to_limited_events': [asdict(x) for x in complete_events], 'complete_to_limited_metadata': complete_metadata,
              'legacy_to_limited_events': [asdict(x) for x in legacy_events], 'legacy_metadata': legacy_metadata}
    (OUT / 'results.json').write_text(json.dumps(report, default=str, indent=2))
    print(json.dumps(report, default=str, indent=2), flush=True)

asyncio.run(main())
