"""SDK/process acceptance for actual shipped argv; no host expansion claim."""
import asyncio
import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'integrations' / 'claude-code'


def declared_launch(executable, config):
    path = PLUGIN / '.mcp.json'
    assert path.is_file(), 'Missing native plugin MCP declaration for real SDK launch'
    entry = json.loads(path.read_text())['mcpServers']['shopextract']
    # Exact one-value replacement is test-side SDK setup, never shell evaluation.
    values = {'${SHOPEXTRACT_PYTHON}': str(executable), '${SHOPEXTRACT_CONFIG}': str(config)}
    return values.get(entry['command'], entry['command']), [values.get(v, v) for v in entry['args']]


@pytest.mark.asyncio
async def test_declared_launch_initializes_real_server_with_literal_hostile_paths(tmp_path):
    # Fail on missing declaration before importing optional SDK: intended package red.
    executable = tmp_path / 'python space ; $(touch SENTINEL) "é"'
    config = tmp_path / 'config space ; $(touch SENTINEL) "é".json'
    command, args = declared_launch(executable, config)
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    executable.symlink_to(sys.executable)
    config.write_text(json.dumps({'allowed_origins': [], 'allowed_tools': ['discover']}))
    # A symlink outside a venv loses pyvenv.cfg discovery; retain the test's
    # already installed dependency paths explicitly without installing anything.
    import sysconfig
    import_paths = os.pathsep.join([str(ROOT / 'src'), sysconfig.get_path('purelib')])
    env = {**os.environ, 'PYTHONPATH': import_paths, 'OMP_NUM_THREADS': '2',
           'OPENBLAS_NUM_THREADS': '2', 'MKL_NUM_THREADS': '2',
           'TOKENIZERS_PARALLELISM': 'false'}
    params = StdioServerParameters(command=command, args=args, cwd=str(tmp_path), env=env)

    async def exercise():
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as client:
                initialized = await client.initialize()
                assert initialized.serverInfo.name == 'shopextract'
                tools = await client.list_tools()
                assert {tool.name for tool in tools.tools} == {'discover'}
                denied = await client.call_tool('discover', {
                    'schema_version': '1.0', 'url': 'https://store.example', 'max_items': 2})
                envelope = denied.structuredContent or json.loads(denied.content[0].text)
                assert envelope['ok'] is False
                assert envelope['error']['code'] == 'permission_denied'
    await asyncio.wait_for(exercise(), timeout=15)
    assert not (tmp_path / 'SENTINEL').exists()


async def ready(engine, job_id):
    # Await real owned task: no mock envelope and no extra tool poll.
    await asyncio.wait_for(asyncio.shield(engine.jobs.jobs[job_id]['task']), timeout=8)


@pytest.mark.asyncio
@pytest.mark.parametrize('case,expected_calls,stop', [
    ('success', 6, 'complete'), ('duplicates', 6, 'complete'), ('feed-cap', 6, 'complete'),
    ('failed-discover', 2, 'source_error'), ('failed-extract', 4, 'failed'),
    ('pending-discover', 2, 'queued'), ('pending-extract', 4, 'queued'),
    ('timeout-extract', 4, 'timed_out')])
async def test_real_source_recipe_cases(case, expected_calls, stop):
    from tests.claude_code_fixture import fixture_runtime, CAPTURE_TIME
    from tests.claude_code_recipe import run_recipe
    from tests.tool_api_fixtures import ORIGIN
    engine, requests = fixture_runtime(case)

    async def synchronize(job_id, operation):
        if case == 'pending-discover' or (case == 'pending-extract' and operation == 'extract'):
            return  # Real pending job is intentionally not awaited.
        await ready(engine, job_id)
    try:
        async def observed_call(name, arguments):
            before = len(requests)
            result = await engine.call(name, arguments)
            if name == 'evidence':
                assert len(requests) == before, 'Captured evidence must not refetch source'
            return result
        trace = await asyncio.wait_for(run_recipe(observed_call, ORIGIN, after_submit=synchronize), 15)
        assert len(trace.calls) == expected_calls
        assert trace.stop == stop
        assert len(trace.records) <= 2
        assert all(arguments.get('max_items', 2) == 2 for _, arguments, _ in trace.calls)
        if stop == 'complete':
            product = trace.records[0]
            assert product['price'] == '10.25'
            assert product['currency'] == 'EUR'
            assert product['canonical_product_id']
            assert product['field_evidence']['/price']
            assert trace.evidence['status'] == 'available'
            support = trace.evidence['evidence']
            assert support['retained_data']['value'] == '10.25'
            assert support['observed_at'] == CAPTURE_TIME.isoformat()
            assert product['vendor'] is None  # Missing source field remains unsupported.
            assert not product['field_evidence'].get('/vendor')  # Unknown observations have no support IDs.
            assert not any('169.254.169.254' in url for _, url in requests)
            assert len(requests) <= 4
            if case == 'duplicates':
                assert trace.calls[1][2]['data']['items'] == [ORIGIN + '/products/widget']
            if case == 'feed-cap':
                assert len(trace.records) == 2
                assert trace.calls[4][2]['data']['completeness'] == 'partial'
                assert len({p['canonical_product_id'] for p in trace.records}) == 2
    finally:
        await engine.aclose()
        assert engine.store.used_bytes == 0
        assert not engine.jobs.jobs


@pytest.mark.asyncio
async def test_denial_schema_tool_prerequisites_and_no_source_escape():
    from tests.claude_code_fixture import fixture_runtime
    from tests.tool_api_fixtures import ORIGIN
    engine, requests = fixture_runtime()
    try:
        assert {v['name'] for v in engine.tool_schemas()} == {
            'discover', 'extract', 'match', 'changes', 'evidence', 'job_status', 'job_result', 'job_cancel'}
        for version, url, expected in [('1.0', 'http://169.254.169.254/', 'permission_denied'),
                ('9.0', ORIGIN, 'unsupported_version')]:
            result = await engine.call('discover', {'schema_version': version, 'url': url, 'max_items': 2})
            assert result['error']['code'] == expected
        assert requests == []
    finally:
        await engine.aclose()
    restricted, _ = fixture_runtime(allowed_tools=('discover',))
    try:
        from tests.claude_code_recipe import run_recipe
        trace = await run_recipe(restricted.call, ORIGIN)
        assert trace.stop == 'permission_denied'
        assert len(trace.calls) == 2
    finally:
        await restricted.aclose()


@pytest.mark.asyncio
async def test_real_recipe_pre_call_count_and_deadline_stops():
    from tests.claude_code_fixture import fixture_runtime
    from tests.claude_code_recipe import run_recipe
    from tests.tool_api_fixtures import ORIGIN
    engine, _ = fixture_runtime()
    async def synchronize(job_id, operation):
        await ready(engine, job_id)
    try:
        trace = await run_recipe(engine.call, ORIGIN, max_calls=2, after_submit=synchronize)
        assert trace.stop == 'budget' and len(trace.calls) == 2
        # Clock advances across the actual discovery job; no fabricated tool calls.
        now = [0.0]
        async def cross_deadline(job_id, operation):
            await ready(engine, job_id)
            now[0] = 120
        trace = await run_recipe(engine.call, ORIGIN, after_submit=cross_deadline, clock=lambda: now[0])
        assert trace.stop == 'budget' and len(trace.calls) == 1
    finally:
        await engine.aclose()


@pytest.mark.asyncio
async def test_real_sdk_source_evidence_and_sequential_restart():
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    from tests.claude_code_recipe import run_recipe
    from tests.tool_api_fixtures import ORIGIN
    params = StdioServerParameters(command=sys.executable,
        args=['-m', 'tests.claude_code_fixture', 'success'], cwd=str(ROOT),
        env={**os.environ, 'PYTHONPATH': os.pathsep.join([str(ROOT / 'src'), str(ROOT)]),
             'OMP_NUM_THREADS': '2', 'OPENBLAS_NUM_THREADS': '2', 'MKL_NUM_THREADS': '2',
             'TOKENIZERS_PARALLELISM': 'false'})

    async def exercise():
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as client:
                await client.initialize()
                async def call(name, arguments):
                    result = await client.call_tool(name, arguments)
                    return result.structuredContent or json.loads(result.content[0].text)
                async def wait_offline(job_id, operation):
                    # Explicit bounded synchronization for controlled success only.
                    await asyncio.sleep(.1 if operation == 'discover' else 3)
                trace = await run_recipe(call, ORIGIN, after_submit=wait_offline)
                assert trace.stop == 'complete', trace
                assert [name for name, _, _ in trace.calls] == [
                    'discover', 'job_result', 'extract', 'job_status', 'job_result', 'evidence']
                assert trace.records[0]['price'] == '10.25'
                old_job = trace.calls[2][2]['data']['job_id']
                old_owner = trace.records[0]['owner_handle']
                old_canonical = trace.records[0]['canonical_product_id']
                old_id = trace.records[0]['field_evidence']['/price'][0]
                denied = await call('evidence', {'schema_version': '1.0',
                    'owner': trace.calls[4][2]['data']['metadata']['catalog_handle'], 'evidence_id': old_id})
                assert denied['error']['code'] == 'not_found'
        # No concurrent old process/session; old handles cannot survive restart.
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as client:
                await client.initialize()
                for name, args in [('job_status', {'job_id': old_job}),
                        ('evidence', {'owner': old_owner, 'evidence_id': old_id})]:
                    result = await client.call_tool(name, {'schema_version': '1.0', **args})
                    result = result.structuredContent or json.loads(result.content[0].text)
                    assert result['error']['code'] == 'not_found'
                # New real extraction after restart keeps canonical identity while
                # minting a new owner. Together the two sessions return two products.
                fresh = await client.call_tool('extract', {'schema_version': '1.0',
                    'url': ORIGIN + '/products/widget', 'max_items': 2})
                fresh = fresh.structuredContent or json.loads(fresh.content[0].text)
                assert fresh['ok']
                await asyncio.sleep(3)
                page = await client.call_tool('job_result', {'schema_version': '1.0',
                    'job_id': fresh['data']['job_id'], 'collection': 'products', 'page_size': 2})
                page = page.structuredContent or json.loads(page.content[0].text)
                record = page['data']['items'][0]
                assert record['canonical_product_id'] == old_canonical
                assert record['owner_handle'] != old_owner
    await asyncio.wait_for(exercise(), 20)


@pytest.mark.parametrize('case', ['missing', 'invalid-json', 'invalid-grant', 'unset', 'empty'])
def test_real_config_startup_failure_has_no_fallback(tmp_path, case):
    import subprocess
    path = tmp_path / 'config.json'
    if case == 'invalid-json':
        path.write_text('{invalid')
    elif case == 'invalid-grant':
        path.write_text('{"allowed_origins":["https://store.example/path"]}')
    elif case == 'unset':
        path = '${SHOPEXTRACT_CONFIG}'
    elif case == 'empty':
        path = ''
    command, args = declared_launch(sys.executable, path)
    env = {**os.environ, 'PYTHONPATH': str(ROOT / 'src')}
    result = subprocess.run([command, *args], cwd=tmp_path, env=env,
                            capture_output=True, text=True, timeout=10)
    assert result.returncode == 2
    assert result.stdout == ''
    assert 'Invalid or unavailable operator configuration.' in result.stderr


def test_missing_executable_is_explicit_startup_error(tmp_path):
    import subprocess
    command, args = declared_launch(tmp_path / 'no-python', tmp_path / 'config.json')
    with pytest.raises(FileNotFoundError):
        subprocess.run([command, *args], cwd=tmp_path, timeout=2)


@pytest.mark.asyncio
async def test_bounded_source_stress_capacity_and_disconnect_cleanup():
    """Fixed 9 admitted + 1 denied, no fake jobs; external response held open."""
    from tests.claude_code_fixture import fixture_runtime
    from tests.tool_api_fixtures import ORIGIN
    engine, requests = fixture_runtime('pending-discover')
    try:
        jobs = []
        for _ in range(9):
            accepted = await engine.call('discover', {'schema_version': '1.0',
                'url': ORIGIN, 'max_items': 2})
            assert accepted['ok'] is True
            jobs.append(accepted['data']['job_id'])
        denied = await engine.call('discover', {'schema_version': '1.0',
            'url': ORIGIN, 'max_items': 2})
        assert denied['error']['code'] == 'resource_limit'
        assert len(engine.jobs.jobs) == 9
        # Let the actual single active job reach the controlled wire boundary.
        for _ in range(20):
            if requests:
                break
            await asyncio.sleep(.005)
        assert len(requests) == 1
        assert sum(j['state'] == 'running' for j in engine.jobs.jobs.values()) == 1
        assert sum(j['state'] == 'queued' for j in engine.jobs.jobs.values()) == 8
    finally:
        await asyncio.wait_for(engine.aclose(), 2)
    assert engine.store.used_bytes == 0 and not engine.jobs.jobs
    assert engine.closed
