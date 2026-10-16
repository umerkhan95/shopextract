"""Real SQLite/flock lifecycle checks; external mechanisms are not faked."""
from datetime import datetime, timezone
import pytest
from shopextract.maintenance import Goal, MaintenanceStore

NOW = datetime(2026, 10, 16, 10, tzinfo=timezone.utc)


def make_goal(**changes):
    data = dict(baseline=({'external_id': 'S1', 'description': 'Old'},),
                supplier_origin='https://supplier.example',
                product_urls=('https://supplier.example/products/S1',),
                profiles={'S1': 'hardware-v1'}, deadline='2026-10-16T10:01:00+00:00')
    data.update(changes)
    return Goal(**data)


def test_store_smoke_atomic_checkpoint_and_reopen(tmp_path):
    store = MaintenanceStore(tmp_path / 'jobs.db')
    key = store.create(make_goal())
    store.acquire()
    assert store.begin(key, now=NOW)
    store.add_steps(key, [('http:1', 'http')])
    attempt = store.reserve(key, 'http:1', {'requests': 1}, now=NOW)
    store.checkpoint(key, 'http:1', {'value': 'New'},
        evidence=[{'evidence_id': 'e1', 'source_url': 'https://supplier.example/products/S1'}],
        findings=[{'finding_id': 'f1', 'status': 'proposed_correction', 'before': 'Old', 'after': 'New'}],
        settlements={attempt: {'requests': 1}})
    store.finish(key, 'completed')
    store.close()
    reopened = MaintenanceStore(tmp_path / 'jobs.db')
    assert reopened.status(key)['state'] == 'completed'
    assert reopened.report(key)['usage']['requests'] == 1
    assert reopened.report(key)['findings'][0]['after'] == 'New'
    assert reopened.evidence(key, 'e1')['source_url'].startswith('https://supplier.example')
    reopened.close()


from datetime import timedelta
import os
from pathlib import Path
import subprocess
import sys
from shopextract.maintenance import Budgets, MaintenanceError


def started(tmp_path, **changes):
    store = MaintenanceStore(tmp_path / 'jobs.db')
    key = store.create(make_goal(**changes))
    store.acquire()
    assert store.begin(key, now=NOW)
    store.add_steps(key, [('http:1', 'http'), ('http:2', 'http')])
    return store, key


def test_recovery_keeps_unknown_intent_charged_and_blocks_implicit_retry(tmp_path):
    store, key = started(tmp_path, budgets=Budgets(requests=2))
    store.reserve(key, 'http:1', {'requests': 1}, now=NOW)
    store.close()
    reopened = MaintenanceStore(tmp_path / 'jobs.db')
    reopened.acquire()
    assert reopened.status(key)['state'] == 'paused'
    assert reopened.usage(key)['unknown_requests'] == 1
    reopened.begin(key, now=NOW)
    with pytest.raises(MaintenanceError, match='outcome_unknown'):
        reopened.reserve(key, 'http:1', {'requests': 1}, now=NOW)
    attempt2 = reopened.reserve(key, 'http:1', {'requests': 1}, now=NOW, explicit_retry=True)
    assert reopened.usage(key)['requests'] == 2
    with pytest.raises(MaintenanceError, match='retry_exhausted'):
        reopened.reserve(key, 'http:1', {'requests': 1}, now=NOW, explicit_retry=True)
    reopened.checkpoint(key, 'http:1', {'ok': True}, settlements={attempt2: {'requests': 1}})
    assert reopened.usage(key)['unknown_requests'] == 1
    reopened.close()


@pytest.mark.parametrize('dimension,reason', [('requests','request_budget'), ('tokens','token_budget'),
                                             ('cost_micros','cost_budget')])
def test_cumulative_exact_reservation_edges(tmp_path, dimension, reason):
    from dataclasses import replace
    store, key = started(tmp_path, budgets=replace(Budgets(), **{dimension: 1}))
    store.reserve(key, 'http:1', {dimension: 1}, now=NOW)
    with pytest.raises(MaintenanceError, match=reason):
        store.reserve(key, 'http:2', {dimension: 1}, now=NOW)
    assert store.usage(key)[dimension] == 1
    store.close()


def test_transaction_failure_rolls_back_evidence_findings_and_settlement(tmp_path):
    store, key = started(tmp_path)
    attempt = store.reserve(key, 'http:1', {'requests': 1}, now=NOW)
    with pytest.raises(MaintenanceError, match='budget_violation'):
        store.checkpoint(key, 'http:1', {'ok': True}, evidence=[{'evidence_id': 'e1'}],
                         findings=[{'finding_id': 'f1'}], settlements={attempt: {'requests': 2}})
    assert store.steps(key)[0]['state'] == 'pending'
    assert store.report(key)['findings'] == []
    with pytest.raises(MaintenanceError, match='not_found'):
        store.evidence(key, 'e1')
    assert store.usage(key)['requests'] == 1
    store.close()


def test_control_cancel_while_execution_owner_is_active(tmp_path):
    owner, key = started(tmp_path)
    attempt = owner.reserve(key, 'http:1', {'requests': 1}, now=NOW)
    control = MaintenanceStore(tmp_path / 'jobs.db')
    assert control.request_cancel(key)['cancel_requested']
    with pytest.raises(MaintenanceError, match='cancelled'):
        owner.checkpoint(key, 'http:1', {'late': True}, settlements={attempt: {'requests': 1}})
    owner.finish(key, 'cancelled')
    assert control.status(key)['state'] == 'cancelled'
    assert control.report(key)['findings'] == []
    control.close()
    owner.close()


@pytest.mark.parametrize('terminal', ['completed', 'cancelled', 'failed'])
def test_terminal_winner_and_resume_rules(tmp_path, terminal):
    store, key = started(tmp_path)
    store.finish(key, terminal)
    store.finish(key, 'partial', 'late')
    assert store.status(key)['state'] == terminal
    if terminal == 'completed':
        assert store.begin(key, now=NOW) is False
    else:
        with pytest.raises(MaintenanceError, match='invalid_state'):
            store.begin(key, now=NOW)
    store.close()


def test_retry_delay_attempt_count_and_policy_failure_survive_reopen(tmp_path):
    store, key = started(tmp_path)
    attempt = store.reserve(key, 'http:1', {'requests': 1}, now=NOW)
    store.fail_attempt(attempt, 'timeout', retry_at=NOW + timedelta(seconds=1))
    denied = store.reserve(key, 'http:2', {'requests': 1}, now=NOW)
    store.fail_attempt(denied, 'permission_denied')
    store.close()
    store = MaintenanceStore(tmp_path / 'jobs.db')
    store.acquire()
    store.begin(key, now=NOW)
    with pytest.raises(MaintenanceError, match='retry_wait'):
        store.reserve(key, 'http:1', {'requests': 1}, now=NOW)
    store.reserve(key, 'http:1', {'requests': 1}, now=NOW + timedelta(seconds=1))
    with pytest.raises(MaintenanceError, match='retry_exhausted'):
        store.reserve(key, 'http:2', {'requests': 1}, now=NOW)
    store.close()


def test_deadline_is_fixed_and_expired_resume_is_partial(tmp_path):
    store, key = started(tmp_path)
    store.finish(key, 'partial', 'source_partial')
    assert not store.begin(key, now=NOW + timedelta(minutes=2))
    assert store.status(key)['stop_reason'] == 'deadline'
    assert store.usage(key)['requests'] == 0
    store.close()


def test_kernel_owner_death_releases_lock_and_recovers_unknown_intent(tmp_path):
    store = MaintenanceStore(tmp_path / 'jobs.db')
    key = store.create(make_goal())
    code = '''import sys
from datetime import datetime,timezone
from shopextract.maintenance import MaintenanceStore
s=MaintenanceStore(sys.argv[1]);s.acquire();s.begin(sys.argv[2],now=datetime(2026,10,16,10,tzinfo=timezone.utc))
s.add_steps(sys.argv[2],[('http:1','http')]);s.reserve(sys.argv[2],'http:1',{'requests':1},now=datetime(2026,10,16,10,tzinfo=timezone.utc))
print('locked',flush=True)
sys.stdin.read()
'''
    process = subprocess.Popen([sys.executable, '-c', code, str(tmp_path / 'jobs.db'), key],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        import select
        assert select.select([process.stdout], [], [], 5)[0], 'owner startup timed out'
        assert process.stdout.readline().strip() == 'locked'
        with pytest.raises(MaintenanceError, match='owner_busy'):
            store.acquire()
        process.kill()
        process.wait(timeout=3)
        store.acquire()
        assert store.status(key)['state'] == 'paused'
        assert store.usage(key)['unknown_requests'] == 1
    finally:
        if process.poll() is None:
            process.kill()
            process.wait(timeout=3)
        store.close()


def test_discovered_request_steps_append_stably_without_resetting_attempts(tmp_path):
    store, key = started(tmp_path)
    store.add_step(key, 'wire:3', 'http')
    store.add_step(key, 'wire:3', 'http')
    assert [row['id'] for row in store.steps(key)] == ['http:1', 'http:2', 'wire:3']
    store.reserve(key, 'wire:3', {'requests': 1}, now=NOW)
    assert store.usage(key)['requests'] == 1
    store.close()
