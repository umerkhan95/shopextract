"""Native package acceptance. Missing package is the intended preimplementation red."""
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'integrations' / 'claude-code'


def required(path):
    assert path.is_file(), f'Missing native plugin acceptance artifact: {path.relative_to(ROOT)}'
    return path.read_text(encoding='utf-8')


def parse_native_report(stdout, returncode):
    """Native private-manifest result; ancillary listing warnings stay separate."""
    result = {'valid': False, 'manifest_errors': [], 'manifest_warnings': [], 'ancillary_warnings': []}
    try:
        report = json.loads(stdout)
    except (json.JSONDecodeError, TypeError):
        result['manifest_errors'] = ['Missing JSON native validation report']
        return result
    manifest = report.get('manifest') if isinstance(report, dict) else None
    if not isinstance(manifest, dict) or not isinstance(manifest.get('errors'), list):
        result['manifest_errors'] = ['Missing nested manifest.errors list']
        return result
    result['manifest_errors'] = list(manifest['errors'])
    result['manifest_warnings'] = manifest.get('warnings', [])
    for section, value in report.items():
        if section != 'manifest' and isinstance(value, dict):
            for warning in value.get('warnings', []):
                result['ancillary_warnings'].append({'section': section, 'warning': warning})
    false_flag = any(value.get(key) is False for value in (report, manifest) for key in ('valid', 'success'))
    result['valid'] = returncode == 0 and not result['manifest_errors'] and not false_flag
    return result


def test_native_manifest_and_component_layout():
    manifest = json.loads(required(PLUGIN / '.claude-plugin' / 'plugin.json'))
    assert manifest['name'] == 'shopextract'
    assert manifest['version'] == '0.1.1'
    assert manifest['license'] == 'MIT'
    assert manifest['description']
    assert manifest['author']['name']
    assert not ({'hooks', 'agents', 'commands', 'mcpServers', 'experimental'} & manifest.keys())
    assert sorted(p.relative_to(PLUGIN).as_posix() for p in PLUGIN.rglob('SKILL.md')) == [
        'skills/shopextract-review/SKILL.md']
    assert not any((PLUGIN / name).exists() for name in ('hooks', 'agents', 'scripts', 'monitors'))


def test_direct_mcp_declaration_has_only_trusted_operator_placeholders():
    mcp = json.loads(required(PLUGIN / '.mcp.json'))
    assert set(mcp) == {'mcpServers'}
    assert set(mcp['mcpServers']) == {'shopextract'}
    entry = mcp['mcpServers']['shopextract']
    assert entry['command'] == '${SHOPEXTRACT_PYTHON}'
    assert entry['args'] == ['-m', 'shopextract.tools', '--config', '${SHOPEXTRACT_CONFIG}']
    assert set(entry) <= {'type', 'command', 'args'}
    assert entry.get('type', 'stdio') == 'stdio'


def test_skill_preserves_instruction_and_permission_boundaries():
    skill = required(PLUGIN / 'skills' / 'shopextract-review' / 'SKILL.md')
    assert skill.startswith('---\n')
    frontmatter = skill.split('---', 2)[1]
    assert 'name: shopextract-review' in frontmatter
    assert 'description:' in frontmatter
    assert 'allowed-tools:' not in frontmatter
    assert 'context: fork' not in frontmatter
    assert '!`' not in skill
    for required_term in ('discover', 'extract', 'job_status', 'job_result', 'evidence',
                          'schema_version', '1.0', '120', 'owner', 'partial', 'session'):
        assert required_term in skill, required_term
    # These are policy acceptance assertions, not proof of model compliance.
    text = skill.lower()
    assert 'six' in text or '6 tool' in text
    assert 'two products' in text or '2 products' in text
    assert 'untrusted' in text
    assert 'permission' in text


@pytest.mark.skipif(os.environ.get("SHOPEXTRACT_NATIVE_CLAUDE") != "1",
                    reason="Native Claude parser opt-in; skipped is not compatibility evidence")
def test_native_parser_accepts_shipped_package(tmp_path):
    required(PLUGIN / '.claude-plugin' / 'plugin.json')
    client = shutil.which('claude')
    assert client, 'Native parser unavailable; record blocker rather than count a skip as pass'
    result = subprocess.run([client, 'plugin', 'validate', '--json', str(PLUGIN)],
                            capture_output=True, text=True, timeout=20, check=False,
                            env={**os.environ, 'CLAUDE_CONFIG_DIR': str(tmp_path / 'native-profile')})
    assert result.returncode == 0, (result.stdout + result.stderr)[-2000:]
    parsed = parse_native_report(result.stdout, result.returncode)
    assert parsed['valid'], parsed


def package_policy(root):
    """Project-only distribution audit; not an emulation of Claude's loader."""
    entries = list(root.rglob('*'))
    if any(path.is_symlink() for path in entries):
        raise ValueError('symlink forbidden')
    files = [path for path in entries if path.is_file()]
    if len(files) > 32 or sum(path.stat().st_size for path in files) > 1024 * 1024:
        raise ValueError('package size cap')
    expected = {'.claude-plugin/plugin.json', '.mcp.json', 'skills/shopextract-review/SKILL.md', 'README.md', 'LICENSE'}
    if {path.relative_to(root).as_posix() for path in files} != expected:
        raise ValueError('unexpected or missing package file')
    for path in files:
        path.resolve().relative_to(root.resolve())
        text = path.read_text(encoding='utf-8')
        if 'sk-ant-fixture-secret' in text or '/Users/' in text or '/home/' in text:
            raise ValueError('embedded secret or operator path')
    manifest = json.loads((root / '.claude-plugin/plugin.json').read_text())
    if set(manifest) != {'name', 'version', 'description', 'author', 'license'}:
        raise ValueError('forbidden manifest field')
    if any(not isinstance(manifest[field], str) or not manifest[field]
           for field in ('name', 'version', 'description', 'license')):
        raise ValueError('manifest type')
    if manifest['name'] != 'shopextract' or manifest['license'] != 'MIT':
        raise ValueError('manifest identity')
    if not isinstance(manifest['author'], dict) or not manifest['author'].get('name'):
        raise ValueError('manifest author')
    mcp = json.loads((root / '.mcp.json').read_text())
    if mcp != {'mcpServers': {'shopextract': {'type': 'stdio', 'command': '${SHOPEXTRACT_PYTHON}',
            'args': ['-m', 'shopextract.tools', '--config', '${SHOPEXTRACT_CONFIG}']}}}:
        raise ValueError('MCP declaration')
    return {'files': len(files), 'bytes': sum(path.stat().st_size for path in files)}


def test_shipped_package_policy_and_private_copy_update(tmp_path):
    first = package_policy(PLUGIN)
    copy = tmp_path / 'private-copy'
    shutil.copytree(PLUGIN, copy)
    assert package_policy(copy) == first
    manifest_path = copy / '.claude-plugin/plugin.json'
    manifest = json.loads(manifest_path.read_text())
    manifest['version'] = '0.1.2'
    manifest_path.write_text(json.dumps(manifest))
    assert package_policy(copy)['files'] == first['files']
    assert json.loads(manifest_path.read_text())['version'] == '0.1.2'
    assert json.loads((PLUGIN / '.claude-plugin/plugin.json').read_text())['version'] == '0.1.1'
    # Copy/update/version integrity only; not actual host installation/update proof.


@pytest.mark.parametrize('mutation', ['json', 'type', 'traversal', 'absolute', 'missing',
    'mcp-command', 'hooks', 'symlink', 'secret', 'operator-path', 'oversize', 'too-many-files'])
def test_unsafe_package_policy_rejects_before_distribution(tmp_path, mutation):
    root = tmp_path / 'package'
    shutil.copytree(PLUGIN, root)
    manifest_path = root / '.claude-plugin/plugin.json'
    manifest = json.loads(manifest_path.read_text())
    if mutation == 'json':
        manifest_path.write_text('{broken')
    elif mutation == 'type':
        manifest['name'] = []
        manifest_path.write_text(json.dumps(manifest))
    elif mutation in {'traversal', 'absolute'}:
        manifest['skills'] = '../escape' if mutation == 'traversal' else '/tmp/escape'
        manifest_path.write_text(json.dumps(manifest))
    elif mutation == 'missing':
        (root / 'skills/shopextract-review/SKILL.md').unlink()
    elif mutation == 'mcp-command':
        (root / '.mcp.json').write_text('{"mcpServers":{"shopextract":{"command":[]}}}')
    elif mutation == 'hooks':
        (root / 'hooks').mkdir()
        (root / 'hooks/hooks.json').write_text('{}')
    elif mutation == 'symlink':
        (root / 'README.md').unlink()
        outside = tmp_path / 'outside.md'
        outside.write_text('must not follow this outside file')
        (root / 'README.md').symlink_to(outside)
    elif mutation == 'secret':
        (root / 'README.md').write_text('sk-ant-fixture-secret')
    elif mutation == 'operator-path':
        (root / 'README.md').write_text('/Users/operator/private/config.json')
    elif mutation == 'oversize':
        (root / 'README.md').write_text('x' * (1024 * 1024 + 1))
    elif mutation == 'too-many-files':
        for i in range(33):
            (root / f'extra{i}').write_text('x')
    with pytest.raises(ValueError):
        package_policy(root)
