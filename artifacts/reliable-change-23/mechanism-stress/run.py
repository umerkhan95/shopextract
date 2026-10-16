"""Bounded sequential mechanism driver with one explicitly reviewed continuation."""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).parent
RAW = OUT / 'raw'
INVOCATIONS = OUT / 'invocations'
CONTINUATION_ID = 'reviewed-continuation-1'
KNOWN_SPENT = 72.586
ATTEMPTS_BEFORE = 19
ALLOWLIST = ['SM05', 'SM06', 'SM09-1701-7'] + [f'SM09-2909-{i}' for i in range(8)]


def write(path, data, exclusive=False):
    with Path(path).open('x' if exclusive else 'w') as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, default=str)
        handle.write('\n')


def load_module():
    spec = importlib.util.spec_from_file_location('mechanism_stress_tests', ROOT / 'tests/test_reliable_changes_stress.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def logical_id(item):
    return item['scenario'] if item['scenario'] != 'SM09' else f"SM09-{item['seed']}-{item['index']}"


def child(config_path):
    config = json.loads(Path(config_path).read_text())
    module = load_module()
    progress_path = INVOCATIONS / (config.get('invocation_id', CONTINUATION_ID) + '-progress.json')
    progress = {'status': 'running', 'attempts': config['attempts_before'], 'completed': [],
                'allowlist': config['allowlist'], 'provenance': 'synthetic'}
    write(progress_path, progress, exclusive=True)
    for case in config['allowlist']:
        if progress['attempts'] >= config['max_attempts']:
            progress.update(status='attempt_budget_exhausted', stopped_at=case)
            write(progress_path, progress)
            return 1
        folder = RAW / case
        if folder.exists():
            raise RuntimeError('Existing case outputs are never silently overwritten: ' + case)
        progress['attempts'] += 1  # persisted BEFORE any fixture executes
        progress['active_case'] = case
        write(progress_path, progress)
        folder.mkdir()
        try:
            if case in {'SM05', 'SM06'}:
                item = module.boundary(folder, byte_limit=case == 'SM06')
            else:
                _, seed, index = case.split('-')
                item = module.seeded_batch(folder, int(seed), int(index))
            progress['completed'].append(item)
            progress['active_case'] = None
            write(progress_path, progress)
        except Exception as exc:
            progress.update(status='failed', stopped_at=case,
                error=f'{type(exc).__name__}: {exc}', traceback=traceback.format_exc(limit=8),
                known_smallest_reproducer=str(folder.relative_to(OUT)))
            write(progress_path, progress)
            return 1
    progress['status'] = 'passed'
    write(progress_path, progress)
    return 0


def approved_continuation():
    started = time.monotonic()
    INVOCATIONS.mkdir(exist_ok=True)
    config_path = INVOCATIONS / (CONTINUATION_ID + '-config.json')
    if config_path.exists():
        raise RuntimeError('This reviewed continuation already ran; no automatic extra chunk')
    remaining = 180 - KNOWN_SPENT
    if remaining <= 0 or ATTEMPTS_BEFORE + len(ALLOWLIST) > 32:
        raise RuntimeError('Execution budget exhausted before launch')
    assert min(60, remaining) == 60 and ATTEMPTS_BEFORE + len(ALLOWLIST) == 30
    smoke = json.loads((OUT / 'smoke.json').read_text())
    previous = json.loads((OUT / 'stress.json').read_text())
    assert smoke['status'] == 'passed'
    assert len(previous['completed']) == 14
    superseded = [x for x in previous['completed'] if x['scenario'] in {'SM05', 'SM06'}]
    reused = [x for x in previous['completed'] if x['scenario'] not in {'SM05', 'SM06'}]
    assert len(reused) + 1 == 13
    config = {'known_spent_seconds': KNOWN_SPENT, 'remaining_wall_seconds': remaining,
        'chunk_hard_timeout_seconds': min(60, remaining), 'allowlist': ALLOWLIST,
        'attempts_before': ATTEMPTS_BEFORE, 'max_attempts': 32, 'expected_final_attempts': 30,
        'conformant_reused_batches': 13, 'original_phase_breach': 'approximately4seconds, preserved',
        'no_automatic_extra_chunk': True, 'threads': 2, 'network_requests': 0}
    write(config_path, config, exclusive=True)  # timer arithmetic saved before launch
    write(INVOCATIONS / (CONTINUATION_ID + '-superseded-boundaries.json'), superseded, exclusive=True)
    for name, suffix in [('SM05', 'superseded-single-event'), ('SM06', 'superseded-single-event'),
                         ('SM09-1701-7', 'interrupted-before-reviewed-continuation')]:
        original = RAW / name
        assert original.exists()
        original.rename(RAW / (name + '-' + suffix))  # preserve exact prior raw evidence
    log_dir = RAW / 'invocations' / CONTINUATION_ID
    log_dir.mkdir(parents=True, exist_ok=False)
    env = dict(os.environ, PYTHONPATH=str(ROOT / 'src'), OMP_NUM_THREADS='2',
        OPENBLAS_NUM_THREADS='2', MKL_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2',
        TOKENIZERS_PARALLELISM='false')
    summary = {'status': 'running', 'invocation_id': CONTINUATION_ID,
               'known_spent_before_seconds': KNOWN_SPENT, 'original_phase_breach': config['original_phase_breach']}
    write(OUT / 'summary.json', summary)
    remaining = 180 - KNOWN_SPENT - (time.monotonic() - started)
    if remaining <= 0:
        raise RuntimeError('Overall budget exhausted before child launch')
    try:
        with (log_dir / 'run.log').open('x') as log:
            result = subprocess.run([sys.executable, str(Path(__file__).resolve()), '--child', str(config_path)],
                cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                timeout=min(60, remaining))
        summary['status'] = 'passed' if result.returncode == 0 else 'stopped_on_failure'
    except subprocess.TimeoutExpired:
        summary['status'] = 'timeout'
    progress_file = INVOCATIONS / (CONTINUATION_ID + '-progress.json')
    progress = json.loads(progress_file.read_text()) if progress_file.exists() else {'completed': [], 'attempts': ATTEMPTS_BEFORE}
    elapsed = round(time.monotonic() - started, 3)
    summary.update(continuation_seconds=elapsed, cumulative_measured_driver_seconds=round(KNOWN_SPENT + elapsed, 3),
        completed_logical_batches=13 + len(progress['completed']), attempted_batches=progress['attempts'],
        reused_logical_batches=13, continuation_completed=len(progress['completed']),
        remaining_allowlist=[x for x in ALLOWLIST if x not in {logical_id(i) for i in progress['completed']}],
        mutation_sensitivity='currency gate detected/killed and restored; prior SM08 reused',
        network_requests=0, local_inference=False, usage_counters='unavailable',
        errors=progress.get('error'), seeds=[1701, 2909])
    write(OUT / 'summary.json', summary)
    all_results = reused + progress['completed']
    write(OUT / 'stress.json', {'status': summary['status'], 'completed': all_results,
        'reused_scenarios': [logical_id(x) for x in reused],
        'remaining_allowlist': summary['remaining_allowlist'],
        'cumulative_measured_driver_seconds': summary['cumulative_measured_driver_seconds']})
    write(INVOCATIONS / (CONTINUATION_ID + '-result.json'), summary, exclusive=True)
    print(json.dumps(summary))
    return 0 if summary['status'] == 'passed' else 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--approved-continuation', action='store_true')
    parser.add_argument('--child', type=Path)
    args = parser.parse_args()
    if args.child:
        return child(args.child)
    if args.approved_continuation:
        return approved_continuation()
    parser.error('Explicit reviewed continuation required; reusable pytest cases are in tests/')


if __name__ == '__main__':
    sys.exit(main())
