"""Revision acceptance reds; optional native inference is never started here."""
import importlib
import json
from pathlib import Path

import pytest

from tests import claude_code_recipe as recipe
from tests import test_claude_code_plugin as package_tests
from tests.claude_code_fixture import CASES

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'integrations/claude-code'
PREFIX = 'mcp__plugin_shopextract_shopextract__'
ORIGIN = 'https://store.example'
OPERATIONS = ('discover', 'extract', 'job_status', 'job_result', 'evidence')
TOOLS = {name: PREFIX + name for name in OPERATIONS}


def planned_helper(module, name, requirement):
    helper = getattr(module, name, None)
    assert callable(helper), f'Missing {requirement}: callable {module.__name__}.{name}'
    return helper


def host_module():
    path = ROOT / 'tests/claude_code_host_smoke.py'
    assert path.is_file(), 'Missing opt-in real-host stream parser/supervisor module (FR14)'
    return importlib.import_module('tests.claude_code_host_smoke')


def definitions():
    return [{'name': TOOLS[name], 'inputSchema': {'type': 'object', 'properties': {
        'schema_version': {'const': '1.0'}}}} for name in OPERATIONS]


def test_skill_domain_budget_excludes_schema_loading_and_explains_preflight():
    text = (PLUGIN / 'skills/shopextract-review/SKILL.md').read_text()
    assert 'six ShopExtract domain MCP' in text, 'Missing explicit domain-only budget (FR08)'
    assert 'ToolSearch' in text and 'schema-only' in text
    assert 'input schema' in text.lower()
    assert 'Any host tool invoked for preflight also consumes' not in text
    assert 'no product URL discovered' in text


def test_schema_preflight_preserves_exact_server_names_without_domain_probes():
    preflight = planned_helper(recipe, 'preflight_tools', 'schema preflight (FR08)')
    valid = preflight(definitions(), server_prefix=PREFIX)
    assert valid['ok'] is True and valid['tools'] == TOOLS
    for broken in (definitions()[:-1], [dict(v, name='mcp__other__' + v['name']) for v in definitions()]):
        result = preflight(broken, server_prefix=PREFIX)
        assert result['ok'] is False and result['reason']
    unsupported = definitions()
    unsupported[0]['inputSchema']['properties']['schema_version'] = {'const': '9.0'}
    assert preflight(unsupported, server_prefix=PREFIX)['ok'] is False


@pytest.mark.parametrize('urls,expected', [
    ([ORIGIN + '/articles/first', ORIGIN + '/products/widget'], ORIGIN + '/products/widget'),
    ([ORIGIN + '/product/z', ORIGIN + '/products/a'], ORIGIN + '/products/a'),
    ([ORIGIN + '/products/z', ORIGIN + '/products/a'], ORIGIN + '/products/a'),
    ([ORIGIN + '/blogs/product/widget', ORIGIN + '/news/p/widget'], None),
    ([ORIGIN + '/%62logs%2fproducts/widget', ORIGIN + '/ARTICLEs/product/widget'], None),
    ([ORIGIN + '/products%5cwidget', ORIGIN + '/products%2f..%2fblogs/widget'], None),
    ([ORIGIN + '/products/', ORIGIN + '/?product_id=24'], None),
    (['https://other.example/products/widget', ORIGIN + '/p/widget'], ORIGIN + '/p/widget'),
])
def test_deterministic_product_selection_excludes_articles_and_encoded_escape(urls, expected):
    select = planned_helper(recipe, 'select_product_url', 'deterministic product-only selection (FR09)')
    assert select(urls, ORIGIN) == expected


def test_source_setup_and_compatibility_notes_are_actionable_and_attributed():
    text = (PLUGIN / 'README.md').read_text()
    assert 'scripts/bootstrap_taxonomy.py' in text, 'Missing source taxonomy bootstrap prerequisite (FR11)'
    assert '.[mcp]' in text
    assert 'PyPI' in text and '0.1.2' in text
    assert '2.1.310' in text and 'user-reported' in text.lower()
    assert 'CLAUDE_CODE_SKIP_PLUGIN_MCP_SERVERS' in text
    assert 'marketplace' in text and 'icon' in text


@pytest.mark.parametrize('case', ['index-blog-first', 'index-no-product', 'product-redirect',
    'denied-redirect', 'delayed-discover', 'delayed-extract'])
def test_realistic_source_fixture_seams_are_declared(case):
    assert case in CASES, f'Missing real-runtime external source case {case} (SC10/11/15)'


def test_native_report_accepts_nested_manifest_errors_and_retains_listing_warnings():
    parse = planned_helper(package_tests, 'parse_native_report', 'actual nested native validation report (FR12)')
    report = {'manifest': {'errors': [], 'warnings': ['Optional icon missing']},
              'marketplace': {'warnings': ['Optional marketplace README missing']}}
    parsed = parse(json.dumps(report), 0)
    assert parsed['valid'] is True
    assert parsed['manifest_errors'] == []
    assert parsed['manifest_warnings']
    assert parsed['ancillary_warnings']
    for payload, code in [(report, 1), ('Invalid API key · Please run /login', 0),
            ({'success': True, 'errors': []}, 0), ({'manifest': {'errors': ['bad']}}, 0),
            ({'valid': False, 'manifest': {'errors': []}}, 0),
            ({'manifest': {'valid': False, 'errors': []}}, 0)]:
        raw = payload if isinstance(payload, str) else json.dumps(payload)
        assert parse(raw, code)['valid'] is False


def stream_trace():
    """Synthetic parser fixture, not model/host observation or fake runtime test."""
    events = []
    def turn(identifier, name, arguments, data):
        events.append({'type': 'assistant', 'message': {'content': [
            {'type': 'tool_use', 'id': identifier, 'name': name, 'input': arguments}]}})
        events.append({'type': 'user', 'message': {'content': [
            {'type': 'tool_result', 'tool_use_id': identifier,
             'content': json.dumps({'ok': True, 'data': data})}]}})
    turn('schema', 'ToolSearch', {'query': '+shopextract discover extract evidence'}, {'tools': definitions()})
    turn('d', TOOLS['discover'], {'schema_version': '1.0', 'url': ORIGIN, 'max_items': 2}, {'job_id': 'j1'})
    turn('u', TOOLS['job_result'], {'schema_version': '1.0', 'job_id': 'j1', 'collection': 'urls'},
         {'state': 'succeeded', 'items': [ORIGIN + '/articles/first', ORIGIN + '/products/widget']})
    turn('x', TOOLS['extract'], {'schema_version': '1.0', 'url': ORIGIN + '/products/widget', 'max_items': 2}, {'job_id': 'j2'})
    turn('s', TOOLS['job_status'], {'schema_version': '1.0', 'job_id': 'j2'}, {'state': 'succeeded'})
    turn('p', TOOLS['job_result'], {'schema_version': '1.0', 'job_id': 'j2', 'collection': 'products'},
         {'state': 'succeeded', 'items': [{'product_url': ORIGIN + '/products/widget',
          'owner_handle': 'o1', 'canonical_product_id': 'p1', 'price': '10.25', 'field_evidence': {'/price': ['e1']}}]})
    turn('e', TOOLS['evidence'], {'schema_version': '1.0', 'owner': 'o1', 'evidence_id': 'e1'},
         {'status': 'available', 'evidence': {'source_url': ORIGIN + '/products/widget', 'retained_data': {'value': '10.25'}}})
    events.append({'type': 'result', 'subtype': 'success', 'result': json.dumps({
        'outcome': 'complete', 'product_url': ORIGIN + '/products/widget', 'owner_handle': 'o1',
        'evidence_id': 'e1', 'evidence_status': 'available'})})
    return events


def test_host_stream_counter_excludes_schema_and_checks_actual_evidence_correlation():
    reduce = planned_helper(host_module(), 'reduce_stream', 'host/domain/evidence trace reducer (FR14)')
    events = stream_trace()
    # Stream retransmission of identical tool_use IDs does not double count.
    events.insert(3, events[2])
    result = reduce(events, expected_tools=TOOLS)
    assert result['domain_count'] == 6 and result['schema_host_count'] == 1
    assert result['returned_products'] == 1
    assert result['evidence_verified'] is True and result['errors'] == []


@pytest.mark.parametrize('mutation', ['article-extract', 'seventh-domain', 'wrong-owner', 'auth-final', 'truncated', 'shell'])
def test_host_stream_rejects_false_completion_and_unexpected_execution(mutation):
    reduce = planned_helper(host_module(), 'reduce_stream', 'host trace adverse-case detector (FR14)')
    events = stream_trace()
    if mutation == 'article-extract':
        events[6]['message']['content'][0]['input']['url'] = ORIGIN + '/articles/first'
    elif mutation == 'seventh-domain':
        events.insert(-1, {'type': 'assistant', 'message': {'content': [
            {'type': 'tool_use', 'id': 'extra', 'name': TOOLS['job_status'], 'input': {'job_id': 'j2'}}]}})
    elif mutation == 'wrong-owner':
        events[12]['message']['content'][0]['input']['owner'] = 'foreign'
    elif mutation == 'auth-final':
        events[-1]['result'] = 'Please run /login'
    elif mutation == 'truncated':
        events.pop()
    elif mutation == 'shell':
        events.insert(0, {'type': 'assistant', 'message': {'content': [
            {'type': 'tool_use', 'id': 'shell', 'name': 'Bash', 'input': {'command': 'sleep 1'}}]}})
    assert reduce(events, expected_tools=TOOLS)['errors']


@pytest.mark.asyncio
@pytest.mark.parametrize('case,expected_calls', [('delayed-discover', 2), ('delayed-extract', 4)])
async def test_finite_delay_is_observed_before_unsynchronized_pending(case, expected_calls):
    assert case in CASES, f'Missing finite response-delay fixture {case} (SC11)'
    import asyncio
    from tests.claude_code_fixture import fixture_runtime
    engine, requests = fixture_runtime(case)

    async def real_call_with_caller_latency(name, arguments):
        result = await engine.call(name, arguments)
        # Finite caller/transport scheduling, not a job-completion join and not
        # an instruction for the model to invoke a sleep capability.
        await asyncio.sleep(.015)
        return result
    try:
        trace = await asyncio.wait_for(recipe.run_recipe(real_call_with_caller_latency, ORIGIN), 15)
        assert len(trace.calls) == expected_calls
        assert trace.stop in {'queued', 'running'}
        assert requests, 'Pending must follow observed source request, not merely unscheduled queued work'
        assert getattr(requests, 'active_delays', set()), 'Actual finite wire response must still be delayed'
        assert trace.records == [] and trace.evidence is None
        assert not any(name == 'evidence' for name, _, _ in trace.calls)
    finally:
        await asyncio.wait_for(engine.aclose(), 2)


@pytest.mark.asyncio
async def test_no_product_real_recipe_stops_without_extract_or_extra_discovery():
    assert 'index-no-product' in CASES, 'Missing no-product real discovery fixture (SC10b)'
    import asyncio
    from tests.claude_code_fixture import fixture_runtime
    engine, requests = fixture_runtime('index-no-product')
    async def call(name, arguments):
        result = await engine.call(name, arguments)
        await asyncio.sleep(.015)  # Allow only naturally fast discovery progress.
        return result
    try:
        trace = await asyncio.wait_for(recipe.run_recipe(call, ORIGIN), 15)
        assert trace.stop == 'no product URL discovered'
        assert [name for name, _, _ in trace.calls] == ['discover', 'job_result']
        assert not any('/products/' in url for _, url in requests)
    finally:
        await asyncio.wait_for(engine.aclose(), 2)


def test_native_host_gate_requires_opt_in_normal_access_and_known_turn_limit():
    assess = planned_helper(host_module(), 'assess_preflight', 'non-inference host eligibility gate (FR14)')
    for enabled, access, caps in [(False, True, {'max_turns': True}),
            (True, False, {'max_turns': True}), (True, True, {}),
            (True, True, {'max_turns': False})]:
        result = assess(enabled=enabled, normal_access=access, capabilities=caps)
        assert result['eligible'] is False and result['reason']
    # Pure eligibility decision; never actual inference or a claimed host pass.
    assert assess(enabled=True, normal_access=True, capabilities={
        'max_turns': True, 'plugin_dir': True, 'stream_json': True, 'restricted_tools': True})['eligible'] is True


def test_disabled_preflight_and_ineligible_host_runner_launch_nothing(monkeypatch, tmp_path):
    import subprocess
    module = host_module()
    preflight = planned_helper(module, 'host_preflight', 'runnable bounded native preflight (FR14)')
    run_case = planned_helper(module, 'run_host_case', 'runnable opt-in native case (FR14)')
    def forbidden(*args, **kwargs):
        pytest.fail('Disabled/ineligible host path launched a subprocess')
    monkeypatch.setattr(subprocess, 'Popen', forbidden)
    monkeypatch.setattr(subprocess, 'run', forbidden)
    result = preflight(enabled=False, executable='unavailable-client', profile=tmp_path, project=tmp_path)
    assert result['eligible'] is False and result['reason']
    result = run_case(preflight={'eligible': False, 'reason': 'normal_access_unavailable'},
        plugin_dir=PLUGIN, project_dir=tmp_path, prompt='must not run',
        expected_tools=TOOLS, request_log_path=tmp_path / 'source.json', expected_case='success')
    assert result['status'] == 'blocked'


def test_host_argv_and_runner_supervisor_wiring_are_literal_and_bounded(monkeypatch, tmp_path):
    module = host_module()
    build = planned_helper(module, 'build_host_argv', 'bounded literal native invocation (FR14)')
    run_case = planned_helper(module, 'run_host_case', 'native runner supervisor wiring (FR14)')
    planned_helper(module, 'supervise_process', 'actual bounded process supervisor (FR14)')
    executable = str(tmp_path / 'claude space ; $(touch SENTINEL)')
    plugin = tmp_path / 'plugin space "é"'
    prompt = 'Review products; $(touch SENTINEL) is plain fixture text.'
    argv = build(executable, plugin, prompt)
    assert argv[0] == executable and argv[-1] == prompt
    assert argv[argv.index('--plugin-dir') + 1] == str(plugin)
    assert argv[argv.index('--max-turns') + 1] == '10'
    assert argv[argv.index('--output-format') + 1] == 'stream-json'
    assert argv[argv.index('--tools') + 1] == 'ToolSearch,Skill'
    assert '-p' in argv and '--verbose' in argv
    assert not any(value in {'sh', 'bash', '--dangerously-skip-permissions'} for value in argv)
    calls = []
    def unit_supervisor(command, **kwargs):
        calls.append((command, kwargs))
        return {'events': stream_trace(), 'returncode': 0, 'timed_out': False,
                'terminated': False, 'pid': None, 'diagnostics': [], 'group_cleanup': {'verified': True}}
    monkeypatch.setattr(module, 'supervise_process', unit_supervisor)
    request_log = tmp_path / 'source.json'
    request_log.write_text(json.dumps([{'method': 'GET', 'url': ORIGIN + '/products/widget'}]))
    run_case(preflight={'eligible': True, 'reason': '', 'executable': executable,
        'env': {}, 'capabilities': {'max_turns': True, 'plugin_dir': True,
        'stream_json': True, 'restricted_tools': True}}, plugin_dir=plugin,
        project_dir=tmp_path, prompt=prompt, expected_tools=TOOLS, request_log_path=request_log, expected_case='success')
    assert len(calls) == 1, 'A reducer-only/dummy harness must not satisfy runner acceptance'
    assert calls[0][0] == argv
    assert calls[0][1]['wall_seconds'] == 120
    assert calls[0][1]['cleanup_seconds'] == 2
    assert not (tmp_path / 'SENTINEL').exists()
    # This mocked wiring check is not host/model observation.


def test_supervisor_really_terminates_and_reaps_controlled_process(tmp_path):
    import os
    import signal
    import sys
    import time
    if os.name != 'posix':
        pytest.skip('Owned POSIX process-group mechanism; native unsupported platform stays blocked')
    module = host_module()
    supervise = planned_helper(module, 'supervise_process', 'real timeout termination/reaping (FR14)')
    pidfile = tmp_path / 'pid space ; $(touch SENTINEL).txt'
    code = ('import json,os,pathlib,signal,sys,time;'
            'signal.signal(signal.SIGTERM,signal.SIG_IGN);'
            'pathlib.Path(sys.argv[1]).write_text(str(os.getpid()));'
            'print(json.dumps({"type":"system","subtype":"controlled_fixture"}),flush=True);'
            'time.sleep(60)')
    started = time.monotonic()
    pid = None
    def independent_deadline(signum, frame):
        raise TimeoutError('Supervisor escaped independent4second test deadline')
    previous_handler = signal.signal(signal.SIGALRM, independent_deadline)
    previous_timer = signal.setitimer(signal.ITIMER_REAL, 4)
    try:
        result = supervise([sys.executable, '-c', code, str(pidfile)], env=dict(os.environ),
            cwd=tmp_path, wall_seconds=.2, cleanup_seconds=2)
        assert time.monotonic() - started <= 3.2  # .2 wall +2 cleanup +1 scheduling tolerance.
        assert result['timed_out'] is True and result['terminated'] is True
        assert result['returncode'] != 0
        pid = int(pidfile.read_text())
        assert result['pid'] == pid
        with pytest.raises(ProcessLookupError):
            os.kill(pid, 0)
        assert not (tmp_path / 'SENTINEL').exists()
    finally:
        # Test fallback owns this child; never leave one behind on regression.
        signal.setitimer(signal.ITIMER_REAL, *previous_timer)
        signal.signal(signal.SIGALRM, previous_handler)
        if pid is None and pidfile.exists():
            pid = int(pidfile.read_text())
        if pid is not None:
            try:
                waited, _ = os.waitpid(pid, os.WNOHANG)
            except ChildProcessError:
                pass  # Already reaped: never signal a potentially reused PID.
            else:
                if waited == 0:
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    os.waitpid(pid, 0)


@pytest.mark.asyncio
@pytest.mark.parametrize('case,stop', [('index-blog-first', 'complete'),
    ('product-redirect', 'complete'), ('denied-redirect', 'failed')])
async def test_real_index_selection_and_guarded_redirects(case, stop):
    import asyncio
    from tests.claude_code_fixture import fixture_runtime
    engine, requests = fixture_runtime(case)
    async def synchronized_mechanism_only(job_id, operation):
        await asyncio.wait_for(asyncio.shield(engine.jobs.jobs[job_id]['task']), 8)
    try:
        trace = await asyncio.wait_for(recipe.run_recipe(engine.call, ORIGIN,
            after_submit=synchronized_mechanism_only), 15)
        assert trace.stop == stop
        assert len(trace.calls) == (6 if stop == 'complete' else 4)
        assert not any('/articles/' in url or '/blogs/' in url for _, url in requests)
        assert not any('other.example' in url for _, url in requests)
        assert len(requests) <= 8
        if stop == 'complete':
            assert trace.evidence['status'] == 'available'
        else:
            assert trace.calls[-1][2]['data']['error']['code'] == 'permission_denied'
    finally:
        await asyncio.wait_for(engine.aclose(), 2)


def test_source_bootstrap_help_is_offline_and_noninstalling():
    import subprocess
    import sys
    result = subprocess.run([sys.executable, 'scripts/bootstrap_taxonomy.py', '--help'],
        cwd=ROOT, capture_output=True, text=True, timeout=5)
    assert result.returncode == 0, result.stderr
    assert all(flag in result.stdout for flag in ('--source-cache', '--allow-download', '--offline'))
    # argparse help exits before pip/build/download; this is not fresh-install proof.


def test_host_cli_default_block_and_case_limit(tmp_path):
    import os
    import subprocess
    import sys
    env = {**os.environ, 'PYTHONPATH': str(ROOT / 'src')}
    env.pop('SHOPEXTRACT_CLAUDE_HOST_SMOKE', None)
    command = [sys.executable, '-m', 'tests.claude_code_host_smoke', '--output', str(tmp_path / 'out')]
    result = subprocess.run(command + ['--executable', 'must-not-be-probed'], cwd=ROOT,
        env=env, capture_output=True, text=True, timeout=5)
    assert result.returncode == 2
    evidence = json.loads((tmp_path / 'out/host-smoke.json').read_text())
    assert len(evidence) == 1 and evidence[0]['preflight']['reason'] == 'opt_in_required'
    result = subprocess.run(command + ['--case', 'success', '--case', 'success'], cwd=ROOT,
        env=env, capture_output=True, text=True, timeout=5)
    assert result.returncode == 2 and 'At most three distinct fixed cases' in result.stderr


@pytest.mark.parametrize('mutation', ['unreturned-product', 'conflicting-id', 'malformed-message',
    'false-no-product', 'false-pending'])
def test_stream_reducer_rejects_unproven_source_and_state(mutation):
    reduce = host_module().reduce_stream
    events = stream_trace()
    if mutation == 'unreturned-product':
        events[6]['message']['content'][0]['input']['url'] = ORIGIN + '/products/not-discovered'
    elif mutation == 'conflicting-id':
        events.insert(4, {'type': 'assistant', 'message': {'content': [
            {'type': 'tool_use', 'id': 'd', 'name': TOOLS['extract'], 'input': {}}]}})
    elif mutation == 'malformed-message':
        events[0]['message'] = []
    else:
        events[-1]['result'] = json.dumps({'outcome': 'no product URL discovered' if mutation == 'false-no-product' else 'pending'})
    assert reduce(events, expected_tools=TOOLS)['errors']


def test_supervisor_normal_exit_cleans_owned_descendant_preserving_success(tmp_path):
    import os
    import signal
    import subprocess
    import sys
    import time
    if os.name != 'posix':
        pytest.skip('Owned POSIX process-group mechanism')
    supervise = host_module().supervise_process
    child_file = tmp_path / 'owned-child.pid'
    child_code = ('import os,pathlib,signal,sys,time;'
                  'signal.signal(signal.SIGTERM,signal.SIG_IGN);'
                  'pathlib.Path(sys.argv[1]).write_text(str(os.getpid()));time.sleep(30)')
    parent_code = ('import json,os,pathlib,subprocess,sys,time;'
        'pathlib.Path(sys.argv[1]+".group").write_text(str(os.getpid()));'
        'subprocess.Popen([sys.executable,"-c",sys.argv[2],sys.argv[1]],'
        'stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL);'
        'deadline=time.monotonic()+1;'
        '\nwhile not pathlib.Path(sys.argv[1]).exists() and time.monotonic()<deadline: time.sleep(.005)\n'
        'assert pathlib.Path(sys.argv[1]).exists();'
        'print(json.dumps({"type":"system","subtype":"controlled_parent_exit"}),flush=True)')
    result = None
    def watchdog(signum, frame):
        raise TimeoutError('Normal-exit descendant check escaped independent5second deadline')
    previous_handler = signal.signal(signal.SIGALRM, watchdog)
    previous_timer = signal.setitimer(signal.ITIMER_REAL, 5)
    try:
        result = supervise([sys.executable, '-c', parent_code, str(child_file), child_code],
            env=dict(os.environ), cwd=tmp_path, wall_seconds=2, cleanup_seconds=2)
        child = int(child_file.read_text())
        state = subprocess.run(['ps', '-o', 'stat=', '-p', str(child)],
            capture_output=True, text=True, timeout=.5).stdout.strip()
        assert not state or state.startswith('Z'), 'Successful parent left an owned descendant running'
        assert result['returncode'] == 0 and result['timed_out'] is False
        assert result['group_cleanup']['verified'] is True
        # An indirect orphan zombie is not reaped by this controller; record it.
        assert 'indirect_zombies' in result['group_cleanup']
    finally:
        signal.setitimer(signal.ITIMER_REAL, *previous_timer)
        signal.signal(signal.SIGALRM, previous_handler)
        group_file = Path(str(child_file) + '.group')
        if child_file.exists() and group_file.exists():
            child = int(child_file.read_text())
            group = int(group_file.read_text())
            try:
                if os.getpgid(child) == group and os.getsid(child) == group:
                    os.killpg(group, signal.SIGKILL)
            except ProcessLookupError:
                pass
            try:
                os.waitpid(group, os.WNOHANG)
            except ChildProcessError:
                pass


def test_host_permission_rejection_is_explicit_without_bypass():
    events = stream_trace()
    events[13]['message']['content'][0].update(is_error=True,
        content='Permission to call this MCP tool was denied.')
    result = host_module().reduce_stream(events, expected_tools=TOOLS)
    assert 'host_tool_permission_denied' in result['errors']
    assert result['evidence_verified'] is False
