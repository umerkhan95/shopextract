"""Progress-only pytest plugin; independent parent enforces all wall deadlines."""
import json
import os
from pathlib import Path
import time

import pytest

_STATE = None
_PATH = None
_EXPECTED = ()


def _save():
    data = json.dumps(_STATE, sort_keys=True).encode()
    if len(data) > 65536:
        raise pytest.UsageError('Category progress byte cap exceeded')
    temporary = _PATH.with_suffix('.tmp')
    with temporary.open('wb') as handle:
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, _PATH)


def pytest_configure(config):
    global _PATH, _EXPECTED
    _PATH = Path(os.environ['CATEGORY_MECHANISM_PROGRESS'])
    manifest = json.loads(Path(os.environ['CATEGORY_MECHANISM_RESUME_MANIFEST']).read_text())
    _EXPECTED = tuple(manifest['remaining_nodes'])
    if not _EXPECTED or len(_EXPECTED) + manifest['invocations_started'] > 100:
        raise pytest.UsageError('Category cumulative invocation cap exceeded')


def pytest_sessionstart(session):
    global _STATE
    _STATE = dict(phase='collection', phase_started=time.monotonic(), collected=[], invocations=[], active=None)
    _save()


def pytest_collection_finish(session):
    actual = tuple(item.nodeid for item in session.items)
    if actual != _EXPECTED or len(actual) > 100:
        raise pytest.UsageError('Category collection differs from exact remaining plan')
    _STATE.update(phase='idle', phase_started=time.monotonic(), collected=list(actual))
    _save()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_protocol(item, nextitem):
    _STATE.update(phase='invocation', phase_started=time.monotonic(),
                  active=dict(node=item.nodeid, started=time.monotonic(), reports=[]))
    _save()
    try:
        yield
    finally:
        active = _STATE['active']
        reports = active['reports']
        active.update(seconds=round(time.monotonic()-active['started'],3),
                      passed=all(r['outcome'] == 'passed' for r in reports) and
                             {r['when'] for r in reports} == {'setup','call','teardown'})
        _STATE['invocations'].append(active)
        _STATE.update(phase='idle', phase_started=time.monotonic(), active=None)
        _save()


def pytest_runtest_logreport(report):
    if _STATE and _STATE['active'] and report.nodeid == _STATE['active']['node']:
        _STATE['active']['reports'].append(dict(when=report.when,outcome=report.outcome))
        _save()


def pytest_sessionfinish(session, exitstatus):
    if _STATE is not None:
        _STATE.update(phase='finished', phase_started=time.monotonic(), exitstatus=int(exitstatus))
        _save()
