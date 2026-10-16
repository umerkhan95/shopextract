"""Read-only owner-ID audit of saved scalar identity records; standard library."""
import json
from pathlib import Path
import sqlite3
import time

OUT = Path(__file__).parent


def main():
    started = time.monotonic()
    cases = ['SM01'] + [x['scenario'] if x['scenario'] != 'SM09' else f"SM09-{x['seed']}-{x['index']}"
        for x in json.loads((OUT / 'stress.json').read_text())['completed']]
    result = {'status': 'running', 'mode': 'read-only standard-library identity records',
        'cases': len(cases), 'completed_cases': 0, 'reports': 0, 'owner_references_checked': 0}
    target = OUT / 'owner-audit-direct-result.json'
    try:
        for case in cases:
            db = OUT / 'raw' / case / (case + '.db')
            with sqlite3.connect(db.resolve().as_uri() + '?mode=ro', uri=True) as conn:
                conn.execute('PRAGMA query_only=ON')
                conn.execute('BEGIN')
                cache = {}
                reports = conn.execute('SELECT payload FROM reliable_reports').fetchall()
                assert reports
                for (payload,) in reports:
                    report = json.loads(payload)['report']
                    for candidate in report['candidates']:
                        for side in ['old', 'new', 'recheck']:
                            value = candidate[side]
                            for ref in value['references'] if value else []:
                                sid = ref['snapshot_id']
                                if sid not in cache:
                                    row = conn.execute('SELECT products_json FROM snapshots WHERE id=?', (sid,)).fetchone()
                                    assert row is not None
                                    cache[sid] = json.loads(row[0])
                                parts = ref['record_key'].split('/')
                                assert len(parts) in (2, 4) and parts[0] == 'product'
                                product = cache[sid][int(parts[1])]
                                assert product['canonical_product_id'] == candidate['canonical_product_id']
                                if len(parts) == 4:
                                    assert parts[2] == 'variant'
                                    assert product['variants'][int(parts[3])]['canonical_variant_id'] == candidate['canonical_variant_id']
                                else:
                                    assert candidate['canonical_variant_id'] is None
                                result['owner_references_checked'] += 1
                    result['reports'] += 1
                assert conn.total_changes == 0
            result['completed_cases'] += 1
            target.write_text(json.dumps(result, indent=2) + '\n')
        result['status'] = 'passed'
    except Exception as exc:
        result.update(status='failed', case=case, error=f'{type(exc).__name__}: {exc}')
    result['elapsed_seconds'] = round(time.monotonic() - started, 3)
    target.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    raise SystemExit(main())
