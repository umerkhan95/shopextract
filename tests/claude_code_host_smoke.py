"""Opt-in native smoke and offline trace/supervisor checks; never shipped as plugin code."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import selectors
import shutil
import signal
import subprocess
import sys
import tempfile
import time

from tests.claude_code_recipe import select_product_url

MAX_TURNS = 10
WALL_SECONDS = 120
CLEANUP_SECONDS = 2
TRACE_BYTES = 1024 * 1024
PREFIX = 'mcp__plugin_shopextract_shopextract__'
EXPECTED_TOOLS = {name: PREFIX + name for name in ('discover', 'extract', 'job_status', 'job_result', 'evidence')}
ROOT = Path(__file__).resolve().parents[1]


def _envelope(content):
    if isinstance(content, list):
        content = '\n'.join(value.get('text', '') for value in content if isinstance(value, dict))
    if isinstance(content, str):
        try:
            content = json.loads(content)
        except json.JSONDecodeError:
            return None
    if isinstance(content, dict) and 'structuredContent' in content:
        return content['structuredContent']
    if isinstance(content, dict) and 'content' in content and 'ok' not in content:
        return _envelope(content['content'])
    return content if isinstance(content, dict) else None


def reduce_stream(events, *, expected_tools):
    result = {'domain_count': 0, 'schema_host_count': 0, 'skill_host_count': 0,
              'returned_products': 0, 'evidence_verified': False, 'errors': [], 'outcome': '',
              'domain_denials': []}
    uses, answers, products = {}, {}, []
    operations = {value: key for key, value in expected_tools.items()}
    final = None
    origin = None
    discovered_urls = []
    last_domain_reply = None
    for event in events:
        if not isinstance(event, dict):
            result['errors'].append('invalid_event')
            continue
        kind = event.get('type')
        if kind == 'result':
            if final is not None:
                result['errors'].append('multiple_final_results')
            final = event
        elif kind in {'assistant', 'user'}:
            message = event.get('message')
            if not isinstance(message, dict):
                result['errors'].append('invalid_message')
                continue
            content = message.get('content', [])
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get('type') == 'tool_use':
                    identifier, name, arguments = block.get('id'), block.get('name'), block.get('input', {})
                    if not identifier or not isinstance(arguments, dict):
                        result['errors'].append('invalid_tool_use')
                        continue
                    if identifier in uses:
                        if uses[identifier] != (name, arguments):
                            result['errors'].append('conflicting_tool_id')
                        continue
                    uses[identifier] = (name, arguments)
                    if name in operations:
                        result['domain_count'] += 1
                        operation = operations[name]
                        if arguments.get('schema_version') != '1.0':
                            result['errors'].append('unsupported_schema')
                        if operation == 'discover':
                            origin = arguments.get('url')
                        if operation == 'extract':
                            target = arguments.get('url')
                            if not origin or select_product_url(discovered_urls, origin) != target:
                                result['errors'].append('nonproduct_extract')
                        if operation in {'discover', 'extract'} and (type(arguments.get('max_items')) is not int or not 0 < arguments['max_items'] <= 2):
                            result['errors'].append('item_limit')
                    elif name == 'ToolSearch':
                        result['schema_host_count'] += 1
                        if not isinstance(arguments.get('query'), str) or set(arguments) != {'query'}:
                            result['errors'].append('invalid_schema_search')
                    elif name == 'Skill':
                        result['skill_host_count'] += 1
                    else:
                        result['errors'].append('unexpected_tool:' + str(name))
                elif block.get('type') == 'tool_result':
                    identifier = block.get('tool_use_id')
                    if identifier not in uses:
                        result['errors'].append('orphan_tool_result')
                        continue
                    if identifier in answers:
                        if answers[identifier] != block:
                            result['errors'].append('conflicting_tool_result')
                        continue
                    answers[identifier] = block
                    name, arguments = uses[identifier]
                    if name not in operations:
                        continue
                    envelope = _envelope(block.get('content'))
                    if block.get('is_error') and (not envelope or envelope.get('ok') is not False):
                        result['errors'].append('host_tool_permission_denied')
                        continue
                    if not envelope or type(envelope.get('ok')) is not bool:
                        result['errors'].append('invalid_domain_envelope')
                        continue
                    if not envelope['ok']:
                        error = envelope.get('error')
                        result['domain_denials'].append({'operation': operations[name],
                            'tool_use_id': identifier,
                            'code': error.get('code') if isinstance(error, dict) else None})
                        continue
                    if block.get('is_error'):
                        continue
                    data = envelope.get('data')
                    if not isinstance(data, dict):
                        result['errors'].append('invalid_domain_data')
                        continue
                    last_domain_reply = (operations[name], data)
                    if operations[name] == 'job_result' and arguments.get('collection') == 'urls':
                        values = data.get('items', [])
                        if isinstance(values, list) and all(isinstance(url, str) for url in values):
                            discovered_urls = values
                        else:
                            result['errors'].append('invalid_discovered_urls')
                    if operations[name] == 'job_result' and arguments.get('collection') == 'products':
                        values = data.get('items', [])
                        if not isinstance(values, list):
                            result['errors'].append('invalid_products')
                            continue
                        products.extend(values)
                        result['returned_products'] += len(values)
        elif kind not in {'system', 'rate_limit_event'}:
            result['errors'].append('unsupported_event:' + str(kind))
    if result['domain_count'] > 6:
        result['errors'].append('domain_budget')
    if result['returned_products'] > 2:
        result['errors'].append('product_budget')
    if any(identifier not in answers for identifier in uses):
        result['errors'].append('missing_tool_result')
    if not final or final.get('subtype') != 'success' or final.get('is_error'):
        result['errors'].append('missing_successful_final')
        return result
    summary = _envelope(final.get('result'))
    if not summary or not isinstance(summary.get('outcome'), str):
        result['errors'].append('invalid_final_summary')
        return result
    result['outcome'] = summary['outcome']
    if result['outcome'] == 'complete':
        for identifier, (name, arguments) in uses.items():
            if operations.get(name) != 'evidence' or identifier not in answers:
                continue
            reply = _envelope(answers[identifier].get('content'))
            selected = next((p for p in products if isinstance(p, dict) and p.get('owner_handle') == arguments.get('owner')), None)
            ids = [item for values in (selected or {}).get('field_evidence', {}).values() for item in values]
            if (reply and reply.get('ok') is True and reply.get('data', {}).get('status') == 'available'
                    and not answers[identifier].get('is_error') and selected
                    and arguments.get('evidence_id') in ids
                    and summary.get('owner_handle') == arguments.get('owner')
                    and summary.get('evidence_id') == arguments.get('evidence_id')
                    and summary.get('evidence_status') == 'available'
                    and summary.get('product_url') == selected.get('product_url')):
                result['evidence_verified'] = True
        if not result['evidence_verified']:
            result['errors'].append('unsupported_evidence_completion')
    elif result['outcome'] == 'no product URL discovered':
        if any(operations.get(name) == 'extract' for name, _ in uses.values()):
            result['errors'].append('extract_after_no_product')
        if not origin or select_product_url(discovered_urls, origin) is not None:
            result['errors'].append('unsupported_no_product')
    elif result['outcome'] == 'pending':
        pending = (last_domain_reply is not None and last_domain_reply[0] in {'job_status', 'job_result'}
                   and last_domain_reply[1].get('state') in {'queued', 'running'})
        if not pending or products:
            result['errors'].append('unsupported_pending')
    elif result['outcome'] == 'prerequisite':
        denied = any((_envelope(block.get('content')) or {}).get('ok') is False for block in answers.values())
        if not denied and result['domain_count']:
            result['errors'].append('unsupported_prerequisite')
    elif result['outcome'] == 'unrelated':
        if result['domain_count'] or result['schema_host_count'] or result['skill_host_count']:
            result['errors'].append('activation_for_unrelated_task')
    else:
        result['errors'].append('unknown_outcome')
    return result


def assess_preflight(*, enabled, normal_access, capabilities):
    if not enabled:
        return {'eligible': False, 'reason': 'opt_in_required'}
    if not normal_access:
        return {'eligible': False, 'reason': 'normal_access_unavailable'}
    if not all(capabilities.get(name) is True for name in ('max_turns', 'plugin_dir', 'stream_json', 'restricted_tools')):
        return {'eligible': False, 'reason': 'bounded_cli_capability_unavailable'}
    return {'eligible': True, 'reason': ''}


def build_host_argv(executable, plugin_dir, prompt):
    return [str(executable), '-p', '--plugin-dir', str(plugin_dir), '--output-format', 'stream-json',
            '--verbose', '--max-turns', str(MAX_TURNS), '--tools', 'ToolSearch,Skill',
            '--no-session-persistence', prompt]


def _group_members(group_id, seconds):
    """Inspect only PID/group/state, never command text or user credentials."""
    try:
        os.killpg(group_id, 0)
    except ProcessLookupError:
        return []
    if seconds <= 0:
        return None
    try:
        snapshot = subprocess.run(['ps', '-axo', 'pid=,pgid=,stat='],
            capture_output=True, text=True, timeout=min(.15, seconds))
    except (OSError, subprocess.TimeoutExpired):
        return None
    if snapshot.returncode != 0:
        return None
    members = []
    for line in snapshot.stdout.splitlines():
        fields = line.split()
        if len(fields) == 3 and fields[0].isdigit() and fields[1].isdigit() and int(fields[1]) == group_id:
            members.append((int(fields[0]), fields[2]))
    return members


def _cleanup(process, seconds):
    """Clean this spawn's group even when its leader already exited successfully."""
    started = time.monotonic()
    deadline = started + seconds
    members = _group_members(process.pid, deadline - time.monotonic())
    signals = []
    active = members is None or any(not state.startswith('Z') for _, state in members)
    if active or process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
            signals.append('TERM')
        except ProcessLookupError:
            if process.poll() is None:
                process.terminate()  # Still-owned, unreaped direct child only.
        term_deadline = min(deadline, started + 1)
        try:
            process.wait(timeout=max(0, term_deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            pass
        # An already-exited leader cannot wait for its still-live MCP children.
        time.sleep(max(0, term_deadline - time.monotonic()))
        members = _group_members(process.pid, deadline - time.monotonic())
        if members is None or any(not state.startswith('Z') for _, state in members) or process.poll() is None:
            try:
                os.killpg(process.pid, signal.SIGKILL)
                signals.append('KILL')
            except ProcessLookupError:
                if process.poll() is None:
                    process.kill()
        try:
            process.wait(timeout=max(0, deadline - time.monotonic()))
        except subprocess.TimeoutExpired:
            pass
        members = _group_members(process.pid, deadline - time.monotonic())
    reaped = process.poll() is not None
    return {'verified': reaped and members is not None and not any(
                not state.startswith('Z') for _, state in members),
            'direct_child_reaped': reaped,
            'indirect_zombies': sum(pid != process.pid and state.startswith('Z') for pid, state in members or []),
            'group_disappeared': members == [], 'signals_sent': signals}


def supervise_process(argv, *, env, cwd, wall_seconds=120, cleanup_seconds=2, parse_events=True, domain_tools=None):
    if os.name != 'posix':
        raise RuntimeError('Owned POSIX process groups required')
    if not 0 < wall_seconds <= WALL_SECONDS or not 0 < cleanup_seconds <= CLEANUP_SECONDS:
        raise ValueError('Invalid supervisor bounds')
    process = subprocess.Popen(argv, env=env, cwd=cwd, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, start_new_session=True)
    result = {'events': [], 'returncode': None, 'timed_out': False, 'terminated': False,
              'pid': process.pid, 'diagnostics': [], 'stdout': '', 'stderr': ''}
    outputs = {'stdout': bytearray(), 'stderr': bytearray()}
    pending = bytearray()
    identifiers = set()
    known = set((domain_tools or EXPECTED_TOOLS).values())
    deadline = time.monotonic() + wall_seconds
    reason = None
    selector = selectors.DefaultSelector()
    selector.register(process.stdout, selectors.EVENT_READ, 'stdout')
    selector.register(process.stderr, selectors.EVENT_READ, 'stderr')

    def line_received(line):
        nonlocal reason
        if not line.strip():
            return
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, UnicodeDecodeError):
            reason = 'invalid_stream_json'
            return
        if not isinstance(event, dict):
            reason = 'invalid_stream_event'
            return
        result['events'].append(event)
        if event.get('type') == 'assistant':
            message = event.get('message')
            if not isinstance(message, dict) or not isinstance(message.get('content'), list):
                reason = 'invalid_stream_message'
                return
            for block in message['content']:
                if not isinstance(block, dict) or block.get('type') != 'tool_use':
                    continue
                name = block.get('name')
                if name in known:
                    identifiers.add(block.get('id'))
                    if len(identifiers) > 6:
                        reason = 'domain_budget'
                elif name not in {'ToolSearch', 'Skill'}:
                    reason = 'unexpected_tool'
    try:
        while selector.get_map() and reason is None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                result['timed_out'] = True
                reason = 'timeout'
                break
            for key, _ in selector.select(min(.05, remaining)):
                chunk = os.read(key.fileobj.fileno(), 65536)
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                available = TRACE_BYTES - sum(len(value) for value in outputs.values())
                outputs[key.data].extend(chunk[:available])
                if len(chunk) > available:
                    reason = 'trace_byte_cap'
                    break
                if key.data == 'stdout' and parse_events:
                    pending.extend(chunk)
                    while b'\n' in pending and reason is None:
                        line, _, rest = pending.partition(b'\n')
                        pending[:] = rest
                        line_received(line)
        if parse_events and pending and reason is None:
            line_received(pending)
        if reason is None:
            try:
                process.wait(timeout=max(0, deadline - time.monotonic()))
            except subprocess.TimeoutExpired:
                reason = 'timeout'
                result['timed_out'] = True
    finally:
        result['terminated'] = reason is not None or process.poll() is None
        # Always inspect the owned group: leader exit/pipe EOF does not prove
        # that a redirected MCP descendant exited. Preserve leader returncode.
        result['group_cleanup'] = _cleanup(process, cleanup_seconds)
        if not result['group_cleanup']['verified']:
            result['diagnostics'].append('group_cleanup_unverified')
        selector.close()
        process.stdout.close()
        process.stderr.close()
    result['returncode'] = process.returncode
    for name, value in outputs.items():
        result[name] = bytes(value[:TRACE_BYTES]).decode('utf-8', errors='replace')
    if reason:
        result['diagnostics'].append(reason)
    return result


def _clean_supervision(result):
    return (result.get('returncode') == 0 and result.get('timed_out') is False
            and result.get('terminated') is False and result.get('diagnostics') == []
            and result.get('group_cleanup', {}).get('verified') is True)


def host_preflight(*, enabled=False, executable='claude', profile=None, project=None):
    blocked = {'eligible': False, 'reason': 'opt_in_required', 'probes': []}
    if not enabled:
        return blocked
    if os.name != 'posix':
        blocked['reason'] = 'owned_process_group_unavailable'
        return blocked
    selected = shutil.which(str(executable))
    if not selected:
        blocked['reason'] = 'client_unavailable'
        return blocked
    if os.environ.get('CLAUDE_CODE_SKIP_PLUGIN_MCP_SERVERS'):
        blocked['reason'] = 'reported_plugin_server_skip_flag_set'
        return blocked
    env = dict(os.environ)
    if profile:
        env['CLAUDE_CONFIG_DIR'] = str(profile)
    directory = Path(project or ROOT)
    probes = []
    def probe(argv):
        result = supervise_process(argv, env=env, cwd=directory,
            wall_seconds=5, cleanup_seconds=2, parse_events=False)
        probes.append({'argv_flags': argv[1:], 'returncode': result['returncode'],
                       'timed_out': result['timed_out'], 'terminated': result.get('terminated'),
                       'diagnostics': result.get('diagnostics'),
                       'group_cleanup': result.get('group_cleanup'),
                       'supervision_ok': _clean_supervision(result)})
        return result
    version = probe([selected, '--version'])
    if not _clean_supervision(version):
        return {**blocked, 'reason': 'unsafe_preflight_probe:version', 'probes': probes}
    match = re.search(r'\b(\d+)\.(\d+)\.(\d+)\b', version['stdout'])
    if version['returncode'] != 0 or not match or not (2, 1, 310) <= tuple(map(int, match.groups())) < (3, 0, 0):
        return {**blocked, 'reason': 'known_bounded_client_version_unavailable', 'probes': probes,
                'version': match.group(0) if match else 'unrecognized'}
    # Non-inference argument acceptance plus known-version evidence; help alone is not used.
    flags = build_host_argv(selected, ROOT / 'integrations/claude-code', '')[:-1] + ['--version']
    accepted = probe(flags)
    if not _clean_supervision(accepted):
        return {**blocked, 'reason': 'unsafe_preflight_probe:flags', 'probes': probes}
    if accepted['returncode'] != 0 or match.group(0) not in accepted['stdout']:
        return {**blocked, 'reason': 'bounded_cli_capability_unavailable', 'probes': probes}
    auth = probe([selected, 'auth', 'status'])
    if not _clean_supervision(auth):
        return {**blocked, 'reason': 'unsafe_preflight_probe:auth', 'probes': probes}
    info = _envelope(auth['stdout']) or {}
    access = auth['returncode'] == 0 and info.get('loggedIn') is True
    caps = {name: True for name in ('max_turns', 'plugin_dir', 'stream_json', 'restricted_tools')}
    assessment = assess_preflight(enabled=enabled, normal_access=access, capabilities=caps)
    return {**assessment, 'executable': selected, 'version': match.group(0), 'env': env,
            'capabilities': caps, 'probes': probes, 'auth_method': info.get('authMethod', 'unavailable')}


def run_host_case(*, preflight, plugin_dir, project_dir, prompt, expected_tools, request_log_path, expected_case):
    if expected_case not in {'success', 'unrelated', 'missing-grant'}:
        raise ValueError('Unknown expected case')
    if preflight.get('eligible') is not True:
        return {'status': 'blocked', 'reason': preflight.get('reason', 'preflight_ineligible')}
    assessment = assess_preflight(enabled=True, normal_access=True, capabilities=preflight.get('capabilities', {}))
    if not assessment['eligible']:
        return {'status': 'blocked', 'reason': assessment['reason']}
    process = supervise_process(build_host_argv(preflight['executable'], plugin_dir, prompt),
        env=preflight.get('env', {}), cwd=project_dir, wall_seconds=120, cleanup_seconds=2,
        domain_tools=expected_tools)
    reduced = reduce_stream(process['events'], expected_tools=expected_tools)
    try:
        requests = json.loads(Path(request_log_path).read_text())
        if not isinstance(requests, list):
            raise ValueError('request log must be an array')
    except (OSError, ValueError):
        requests = []
        reduced['errors'].append('missing_source_request_log')
    if len(requests) > 8:
        reduced['errors'].append('source_request_budget')
    if any(not isinstance(value, dict) or not isinstance(value.get('url'), str) for value in requests):
        reduced['errors'].append('invalid_source_request_log')
    elif any('/articles/' in value['url'].lower() or '/blogs/' in value['url'].lower() for value in requests):
        reduced['errors'].append('article_source_request')
    if reduced['outcome'] == 'complete' and not requests:
        reduced['errors'].append('no_source_execution')
    if not _clean_supervision(process):
        reduced['errors'].append('native_process_failure')
    status = 'failed'
    if expected_case == 'success':
        matched = (reduced['outcome'] == 'complete' and reduced['evidence_verified']
                   and reduced['domain_count'] > 0 and bool(requests))
        pending = reduced['outcome'] == 'pending' and reduced['domain_count'] > 0
        if pending and not reduced['errors']:
            status = 'incomplete'
    elif expected_case == 'unrelated':
        matched = (reduced['outcome'] == 'unrelated' and not requests
                   and not any(reduced[key] for key in ('domain_count', 'schema_host_count', 'skill_host_count')))
    else:
        matched = (reduced['outcome'] == 'prerequisite' and any(
            denial['operation'] in {'discover', 'extract'} and denial['code'] == 'permission_denied'
            for denial in reduced['domain_denials']))
    if matched and not reduced['errors']:
        status = 'passed'
    elif status != 'incomplete':
        reduced['errors'].append('case_outcome_mismatch')
    return {'status': status, 'expected_case': expected_case, 'trace': reduced,
            'process': process, 'requests': requests}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--executable', default='claude')
    parser.add_argument('--case', action='append', choices=('success', 'unrelated', 'missing-grant'))
    args = parser.parse_args(argv)
    cases = args.case or ['success', 'unrelated', 'missing-grant']
    if len(cases) > 3 or len(set(cases)) != len(cases):
        parser.error('At most three distinct fixed cases')
    enabled = os.environ.get('SHOPEXTRACT_CLAUDE_HOST_SMOKE') == '1'
    args.output.mkdir(parents=True, exist_ok=True)
    records = []
    with tempfile.TemporaryDirectory(prefix='shopextract-host-') as temp:
        temporary = Path(temp)
        project = temporary / 'project'
        profile = temporary / 'profile'
        project.mkdir()
        profile.mkdir()
        preflight = host_preflight(enabled=enabled, executable=args.executable, profile=profile, project=project)
        # Never serialize inherited environment/credentials to evidence.
        records.append({'preflight': {key: value for key, value in preflight.items() if key != 'env'}})
        if preflight['eligible']:
            import hashlib
            plugin = temporary / 'plugin'
            shutil.copytree(ROOT / 'integrations/claude-code', plugin)
            digests = {str(path.relative_to(plugin)): hashlib.sha256(path.read_bytes()).hexdigest()
                       for path in plugin.rglob('*') if path.is_file()}
            for case in cases:
                log = temporary / (case + '-requests.json')
                log.write_text('[]')
                override = {'mcpServers': {'shopextract': {'type': 'stdio', 'command': sys.executable,
                    'args': ['-m', 'tests.claude_code_fixture', 'index-blog-first'],
                    'env': {'PYTHONPATH': os.pathsep.join([str(ROOT / 'src'), str(ROOT)]),
                        'SHOPEXTRACT_FIXTURE_HOST': '1', 'SHOPEXTRACT_FIXTURE_LOG': str(log),
                        'SHOPEXTRACT_FIXTURE_DENY': '1' if case == 'missing-grant' else '0',
                        'OMP_NUM_THREADS': '2', 'OPENBLAS_NUM_THREADS': '2', 'MKL_NUM_THREADS': '2',
                        'TOKENIZERS_PARALLELISM': 'false'}}}}
                (plugin / '.mcp.json').write_text(json.dumps(override))
                summary = ('Return only JSON with outcome, product_url, owner_handle, evidence_id, evidence_status. '
                           'For pending use outcome pending; for a missing grant use prerequisite. ')
                prompt = ('Return only JSON {"outcome":"unrelated","answer":2} for 1+1; no tools.'
                    if case == 'unrelated' else '/shopextract:shopextract-review Review ' +
                    'https://store.example, at most two products/six domain calls/120 seconds. ' + summary)
                result = run_host_case(preflight=preflight, plugin_dir=plugin, project_dir=project,
                    prompt=prompt, expected_tools=EXPECTED_TOOLS, request_log_path=log, expected_case=case)
                records.append({'case': case, 'provenance': 'actual-native-controlled-source-fixture',
                    'original_package_sha256': digests, 'mcp_fixture_override': override, 'result': result})
                if result['status'] != 'passed':
                    break
    (args.output / 'host-smoke.json').write_text(json.dumps(records, indent=2) + '\n')
    return 0 if preflight['eligible'] and all(item.get('result', {}).get('status') == 'passed' for item in records[1:]) else 2


if __name__ == '__main__':
    raise SystemExit(main())
