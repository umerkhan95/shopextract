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


def test_native_manifest_and_component_layout():
    manifest = json.loads(required(PLUGIN / '.claude-plugin' / 'plugin.json'))
    assert manifest['name'] == 'shopextract'
    assert manifest['version'] == '0.1.0'
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
    result = subprocess.run([client, 'plugin', 'validate', '--strict', '--json', str(PLUGIN)],
                            capture_output=True, text=True, timeout=20, check=False,
                            env={**os.environ, 'CLAUDE_CONFIG_DIR': str(tmp_path / 'native-profile')})
    assert result.returncode == 0, (result.stdout + result.stderr)[-2000:]
    # Some unavailable clients return an auth message or generic response with
    # exit0. Require a structured validation report, never an exit-only pass.
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        pytest.fail('Native parser did not produce a JSON validation report: ' + result.stdout[:300])
    assert isinstance(report, dict) and isinstance(report.get('errors'), list), report
    assert report.get('valid', report.get('success')) is True, report
    assert report['errors'] == [], report


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
    manifest['version'] = '0.1.1'
    manifest_path.write_text(json.dumps(manifest))
    assert package_policy(copy)['files'] == first['files']
    assert json.loads(manifest_path.read_text())['version'] == '0.1.1'
    assert json.loads((PLUGIN / '.claude-plugin/plugin.json').read_text())['version'] == '0.1.0'
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
