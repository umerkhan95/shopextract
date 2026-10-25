"""Narrow final-review regressions; all native-like records here are synthetic."""
import inspect
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

import pytest

from tests import claude_code_host_smoke as host
from tests.claude_code_recipe import select_product_url
from tests.test_claude_code_revision import TOOLS, ORIGIN, PLUGIN, stream_trace


def run_synthetic_case(monkeypatch, tmp_path, events, expected_case, requests=()):
    def supervisor(*args, **kwargs):
        return {'events': events, 'returncode': 0, 'timed_out': False, 'terminated': False,
                'diagnostics': [], 'group_cleanup': {'verified': True}}
    monkeypatch.setattr(host, 'supervise_process', supervisor)
    log = tmp_path / 'requests.json'
    log.write_text(json.dumps(list(requests)))
    kwargs = dict(preflight={'eligible': True, 'executable': 'synthetic-not-launched', 'env': {},
        'capabilities': {key: True for key in ('max_turns', 'plugin_dir', 'stream_json', 'restricted_tools')}},
        plugin_dir=PLUGIN, project_dir=tmp_path, prompt='Case-specific fixed test prompt',
        expected_tools=TOOLS, request_log_path=log)
    # Exercise the old false pass first; after repair bind the new required input.
    if 'expected_case' in inspect.signature(host.run_host_case).parameters:
        kwargs['expected_case'] = expected_case
    return host.run_host_case(**kwargs)


def final_only(outcome):
    return [{'type': 'result', 'subtype': 'success', 'result': json.dumps({'outcome': outcome})}]


@pytest.mark.parametrize('expected_case,outcome', [('success', 'unrelated'),
    ('success', 'prerequisite'), ('missing-grant', 'unrelated'), ('missing-grant', 'prerequisite')])
def test_wrong_or_unexecuted_case_cannot_pass(monkeypatch, tmp_path, expected_case, outcome):
    result = run_synthetic_case(monkeypatch, tmp_path, final_only(outcome), expected_case)
    assert result['status'] == 'failed', 'Runner accepted a different/unexecuted case as passed'


def test_runner_requires_explicit_case_binding():
    parameter = inspect.signature(host.run_host_case).parameters.get('expected_case')
    assert parameter is not None, 'Missing trusted expected_case binding (FR15)'
    assert parameter.default is inspect.Parameter.empty


def test_positive_pending_is_incomplete_not_passed(monkeypatch, tmp_path):
    events = stream_trace()[:6]
    events[5]['message']['content'][0]['content'] = json.dumps({'ok': True, 'data': {'state': 'running'}})
    events += final_only('pending')
    result = run_synthetic_case(monkeypatch, tmp_path, events, 'success')
    assert result['status'] == 'incomplete'
    assert result['trace']['domain_count'] == 2 and not result['trace']['evidence_verified']


def test_missing_grant_can_pass_only_executed_selected_server_denial(monkeypatch, tmp_path):
    events = stream_trace()[:4]
    events[3]['message']['content'][0].update(is_error=True, content=json.dumps({
        'ok': False, 'error': {'code': 'permission_denied', 'message': 'Origin not granted'}}))
    events += final_only('prerequisite')
    result = run_synthetic_case(monkeypatch, tmp_path, events, 'missing-grant')
    assert result['status'] == 'passed'
    assert result['trace'].get('domain_denials'), 'Missing executed denial provenance'


@pytest.mark.parametrize('phase', [0, 1, 2])
@pytest.mark.parametrize('failure', ['timeout', 'terminated', 'diagnostic', 'cleanup'])
def test_preflight_rejects_recognized_text_from_unsafe_probe(monkeypatch, tmp_path, phase, failure):
    monkeypatch.delenv('CLAUDE_CODE_SKIP_PLUGIN_MCP_SERVERS', raising=False)
    monkeypatch.setattr(host.shutil, 'which', lambda value: '/synthetic/claude')
    calls = []
    def probe(argv, **kwargs):
        index = len(calls)
        calls.append(argv)
        result = {'returncode': 0, 'timed_out': False, 'terminated': False, 'diagnostics': [],
                  'group_cleanup': {'verified': True}, 'stdout': '2.1.310 (synthetic test record)'}
        if index == 2:
            result['stdout'] = json.dumps({'loggedIn': True, 'authMethod': 'synthetic'})
        if index == phase:
            if failure == 'timeout':
                result['timed_out'] = True
            elif failure == 'terminated':
                result['terminated'] = True
            elif failure == 'diagnostic':
                result['diagnostics'] = ['controlled_probe_error']
            else:
                result['group_cleanup']['verified'] = False
        return result
    monkeypatch.setattr(host, 'supervise_process', probe)
    result = host.host_preflight(enabled=True, profile=tmp_path, project=tmp_path)
    assert result['eligible'] is False, 'Recognized stdout hid failed probe supervision'
    assert len(calls) == phase + 1, 'Eligibility did not stop at first unsafe probe'
    assert result['probes'][-1].get('supervision_ok') is False


@pytest.mark.parametrize('url,expected', [(ORIGIN + '/products%2Fwidget', None),
    (ORIGIN + '/products%252fwidget', None), (ORIGIN + '/products%5cwidget', None),
    (ORIGIN + '/%70roducts/widget', ORIGIN + '/%70roducts/widget')])
def test_encoded_separator_decision_is_explicit(url, expected):
    assert select_product_url([url], ORIGIN) == expected


def test_toolsearch_optional_payload_is_explicitly_unverified_fail_closed():
    events = stream_trace()
    events[0]['message']['content'][0]['input']['max_results'] = 5
    assert 'invalid_schema_search' in host.reduce_stream(events, expected_tools=TOOLS)['errors']


@pytest.mark.parametrize('mode,diagnostic', [('invalid', 'invalid_stream_json'),
    ('oversize', 'trace_byte_cap'), ('seventh', 'domain_budget'), ('unexpected', 'unexpected_tool')])
def test_live_supervisor_stops_pipe_and_tool_boundary_breaches(tmp_path, mode, diagnostic):
    if os.name != 'posix':
        pytest.skip('Owned POSIX process group required')
    pidfile = tmp_path / 'controlled.pid'
    code = '''import json,os,pathlib,sys,time
pathlib.Path(sys.argv[2]).write_text(str(os.getpid()))
mode=sys.argv[1]
if mode=='invalid': print('not-json',flush=True)
elif mode=='oversize':
    os.write(1,b' '* (600*1024))
    os.write(2,b'x'* (600*1024))
else:
    for i in range(7 if mode=='seventh' else 1):
        name='mcp__plugin_shopextract_shopextract__job_status' if mode=='seventh' else 'Bash'
        print(json.dumps({'type':'assistant','message':{'content':[{'type':'tool_use','id':str(i),'name':name,'input':{}}]}}),flush=True)
time.sleep(30)
'''
    def watchdog(signum, frame):
        raise TimeoutError('Controlled boundary test escaped5second watchdog')
    previous_handler = signal.signal(signal.SIGALRM, watchdog)
    previous_timer = signal.setitimer(signal.ITIMER_REAL, 5)
    started = time.monotonic()
    try:
        result = host.supervise_process([sys.executable, '-c', code, mode, str(pidfile)],
            env=dict(os.environ), cwd=tmp_path, wall_seconds=1, cleanup_seconds=2)
        assert diagnostic in result['diagnostics']
        assert result['terminated'] is True and result['returncode'] != 0
        assert result['group_cleanup']['verified'] and result['group_cleanup']['direct_child_reaped']
        assert time.monotonic() - started <= 4
        assert len(result['stdout'].encode()) + len(result['stderr'].encode()) <= host.TRACE_BYTES
        with pytest.raises(ProcessLookupError):
            os.kill(int(pidfile.read_text()), 0)
    finally:
        signal.setitimer(signal.ITIMER_REAL, *previous_timer)
        signal.signal(signal.SIGALRM, previous_handler)
        if pidfile.exists():
            pid = int(pidfile.read_text())
            try:
                waited, _ = os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                pass
            else:
                if waited == 0:
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    os.waitpid(pid, 0)
