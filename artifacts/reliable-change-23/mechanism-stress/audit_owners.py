"""Read-only audit of preserved real reports; no fixture regeneration or DDL."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import sqlite3
import sys
import time

from shopextract._evidence import decode_value
from shopextract.monitor.evidence import _load_snapshot

OUT = Path(__file__).parent
ROOT = OUT.resolve().parents[2]


def main():
    started = time.monotonic()
    spec = importlib.util.spec_from_file_location('stress_assertions', ROOT / 'tests/test_reliable_changes_stress.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    cases = ['SM01'] + [x['scenario'] if x['scenario'] != 'SM09' else f"SM09-{x['seed']}-{x['index']}"
        for x in json.loads((OUT / 'stress.json').read_text())['completed']]
    result = {'status': 'running', 'provenance': 'saved synthetic reports, read-only audit',
              'cases': len(cases), 'completed_cases': 0, 'owner_references_checked': 0}
    try:
        for case in cases:
            db = OUT / 'raw' / case / (case + '.db')
            with sqlite3.connect(db.resolve().as_uri() + '?mode=ro', uri=True) as conn:
                conn.execute('PRAGMA query_only=ON')
                conn.execute('BEGIN')
                before = conn.total_changes
                reports = conn.execute('SELECT payload FROM reliable_reports').fetchall()
                assert reports
                cache = {}
                for (payload,) in reports:
                    report = decode_value(json.loads(payload))['report']
                    for candidate in report['candidates']:
                        for side in ['old', 'new', 'recheck']:
                            value = candidate[side]
                            for ref in value['references'] if value else []:
                                sid = ref['snapshot_id']
                                if sid not in cache:
                                    cache[sid] = _load_snapshot(conn, sid)
                                module.assert_reference_owner(candidate, cache[sid], ref)
                                result['owner_references_checked'] += 1
                assert conn.total_changes == before == 0
            result['completed_cases'] += 1
        result['status'] = 'passed'
    except Exception as exc:
        result.update(status='failed', case=case, error=f'{type(exc).__name__}: {exc}')
    result['elapsed_seconds'] = round(time.monotonic() - started, 3)
    (OUT / 'owner-audit-result.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))
    return 0 if result['status'] == 'passed' else 1


if __name__ == '__main__':
    sys.exit(main())
