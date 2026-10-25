"""Explicit last two cases then one direct audit; no automatic next chunk."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time

OUT = Path(__file__).parent.resolve()
ROOT = OUT.parents[2]
ID = 'reviewed-final-diminished-1'


def write(path, value, exclusive=False):
    with path.open('x' if exclusive else 'w') as handle:
        json.dump(value, handle, indent=2)
        handle.write('\n')


def main():
    start = time.monotonic()
    # The old audit wrapper failed before saving elapsed time. Charge its20s hard
    # timeout plus conservative0.100s overhead; do not invent an exact measurement.
    spent = 132.607 + 20 + 0.100
    remaining = 180 - spent
    cap = min(21, remaining - 5 - 1)
    if cap <= 0 or 29 + 2 > 32:
        raise RuntimeError('Budget exhausted; no launch')
    config = dict(invocation_id=ID, known_prior_driver_seconds=132.607,
        audit_timeout_seconds=20, audit_unmeasured_overhead_reserve_seconds=0.100,
        charged_spent_upper_bound_seconds=spent, remaining_seconds=remaining,
        child_timeout_seconds=cap, direct_audit_timeout_seconds=4, safety_reserve_seconds=1,
        allowlist=['SM09-2909-6', 'SM09-2909-7'], attempts_before=29, max_attempts=32,
        expected_final_attempts=31, conformant_reused_batches=22,
        old_audit_status='timeout/incomplete, not passed', no_automatic_next_chunk=True)
    path = OUT / 'invocations' / (ID + '-config.json')
    write(path, config, True)
    old = OUT / 'raw/SM09-2909-6'
    assert old.exists()
    old.rename(OUT / 'raw/SM09-2909-6-interrupted-prior-60s-chunk')
    logdir = OUT / 'raw/invocations' / ID
    logdir.mkdir(parents=True, exist_ok=False)
    prior = json.loads((OUT / 'stress.json').read_text())
    assert len(prior['completed']) == 21
    env = dict(os.environ, PYTHONPATH=str(ROOT / 'src'), OMP_NUM_THREADS='2',
        OPENBLAS_NUM_THREADS='2', MKL_NUM_THREADS='2', NUMEXPR_NUM_THREADS='2', TOKENIZERS_PARALLELISM='false')
    status = 'running'
    try:
        with (logdir / 'generator.log').open('x') as log:
            result = subprocess.run([sys.executable, str(OUT/'run.py'), '--child', str(path)],
                cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                timeout=min(cap, 180-spent-(time.monotonic()-start)-5))
        status = 'passed' if result.returncode == 0 else 'failed'
    except subprocess.TimeoutExpired:
        status = 'timeout'
    progress_path = OUT/'invocations'/(ID+'-progress.json')
    progress = json.loads(progress_path.read_text()) if progress_path.exists() else {'completed': [], 'attempts': 29}
    completed = prior['completed'] + progress['completed']
    write(OUT/'stress.json', dict(status=status, completed=completed,
        remaining_allowlist=[case for case in config['allowlist'] if case not in {f"SM09-{x['seed']}-{x['index']}" for x in progress['completed']}]))
    audit = 'not_run_after_generator_stop'
    if status == 'passed':
        left = 180-spent-(time.monotonic()-start)-1
        if left <= 0:
            audit = 'budget_exhausted'
        else:
            try:
                with (logdir/'direct-audit.log').open('x') as log:
                    checked = subprocess.run([sys.executable,str(OUT/'audit_owners_direct.py')],
                        cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, timeout=min(4,left))
                audit = 'passed' if checked.returncode == 0 else 'failed'
            except subprocess.TimeoutExpired:
                audit = 'timeout'
    elapsed = round(time.monotonic()-start,3)
    summary = dict(status='passed' if status == audit == 'passed' else 'incomplete',
        final_generator_status=status, direct_owner_audit=audit,
        completed_logical_batches=1+len(completed), attempted_batches=progress['attempts'],
        final_chunk_seconds=elapsed, cumulative_charged_execution_seconds=round(spent+elapsed,3),
        accounting='132.607 measured prior driver sec +20s audit timeout +0.100s unmeasured-overhead reserve +measured finalchunk',
        original_phase_breach='approximately4seconds, retained',
        prior_fullgraph_audit='timed out; not passed', network_requests=0,
        local_inference=False, usage_counters='unavailable')
    write(OUT/'summary.json',summary)
    write(OUT/'invocations'/(ID+'-result.json'),summary,True)
    print(json.dumps(summary))
    return 0 if summary['status']=='passed' else 1


if __name__=='__main__':
    raise SystemExit(main())
