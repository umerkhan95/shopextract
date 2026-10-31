"""Public taxonomy CLI integration; data fixtures are explicitly synthetic."""
import json

from click.testing import CliRunner
import pytest

from shopextract.cli import main

TEXT = '# Google_Product_Taxonomy_Version: 2021-09-21\n1 - Animals\n2 - Animals > Cats\n3 - Electronics\n'


@pytest.fixture
def prepared(tmp_path):
    source = tmp_path / 'taxonomy.txt'
    source.write_text(TEXT)
    root = tmp_path / 'catalog'
    args = ['taxonomy', 'google', '--catalog-root', str(root)]
    result = CliRunner().invoke(main, [*args, 'prepare', '--source', str(source)])
    assert result.exit_code == 0, result.output
    return tmp_path, args, json.loads(result.output)['data']['manifest']


def test_google_taxonomy_help_is_static_and_registered():
    result = CliRunner().invoke(main, ["taxonomy", "google", "--help"])
    assert result.exit_code == 0, result.output
    assert "prepare" in result.output and "normalize" in result.output


def test_google_taxonomy_capabilities_include_public_paths():
    result = CliRunner().invoke(main, ["capabilities"])
    assert result.exit_code == 0, result.output
    paths = [row["path"] for row in json.loads(result.output)["data"]["commands"]]
    assert ["taxonomy", "google", "lookup"] in paths
    assert ["taxonomy", "google", "normalize"] in paths


def test_google_cli_prepare_manifest_schema_and_offline_lookup(prepared):
    import jsonschema
    from shopextract._cli_discovery import packaged_schema
    _, args, manifest = prepared
    jsonschema.validate(manifest, packaged_schema('google-taxonomy-manifest'))
    info = CliRunner().invoke(main, [*args, 'info'])
    assert info.exit_code == 0, info.output
    assert json.loads(info.output)['data']['manifest'] == manifest
    for command, value in [('lookup', '2'), ('resolve-path', 'Animals > Cats')]:
        result = CliRunner().invoke(main, [*args, command, value])
        assert result.exit_code == 0, result.output
        assert json.loads(result.output)['data']['category']['id'] == '2'


def test_google_cli_pagination_binds_identity_and_page_size(prepared):
    _, args, manifest = prepared
    seen, token = [], None
    while True:
        result = CliRunner().invoke(main, [*args, 'list', '--limit', '1', *(['--cursor', token] if token else [])])
        assert result.exit_code == 0, result.output
        data = json.loads(result.output)['data']
        seen.extend(n['id'] for n in data['categories'])
        assert data['fingerprint'] == manifest['fingerprint']
        token = data['next_cursor']
        if not token:
            break
        bad = CliRunner().invoke(main, [*args, 'list', '--limit', '2', '--cursor', token])
        assert bad.exit_code == 2 and json.loads(bad.output)['error']['code'] == 'E_USAGE'
    assert seen == ['1', '2', '3']


def test_google_cli_batch_misses_and_expected_errors(prepared):
    path, args, _ = prepared
    values = path / 'ids.json'
    values.write_text('["2","999"]')
    result = CliRunner().invoke(main, [*args, 'lookup-batch', str(values)])
    assert result.exit_code == 0, result.output
    nodes = json.loads(result.output)['data']['categories']
    assert nodes[0]['id'] == '2' and nodes[1] is None
    bad = CliRunner().invoke(main, [*args, 'lookup', '999'])
    assert bad.exit_code == 2
    missing = CliRunner().invoke(main, ['taxonomy', 'google', '--catalog-root', str(path / 'missing'), 'info'])
    assert missing.exit_code == 1
    assert json.loads(missing.output)['error']['code'] == 'E_OPERATION'


def test_google_cli_prepare_rejects_wrong_version_before_publication(tmp_path):
    source = tmp_path / 'source.txt'
    source.write_text(TEXT)
    root = tmp_path / 'catalog'
    result = CliRunner().invoke(main, ['taxonomy', 'google', '--catalog-root', str(root),
        '--version', '2020-01-01', 'prepare', '--source', str(source)])
    assert result.exit_code == 2, result.output
    assert not root.exists()


def test_google_cli_normalize_roundtrip_existing_export(prepared):
    from shopextract.extractors.feed import GoogleFeedExtractor
    path, args, _ = prepared
    raw = GoogleFeedExtractor._parse_csv('id,title,price,google_product_category\nP1,Cat food,1 EUR,2\n',
        'https://merchant.test/feed.csv', include_categories=True)
    source = path / 'raw.json'
    source.write_text(json.dumps(raw))
    normalized = CliRunner().invoke(main, [*args, 'normalize', str(source), '--shop-url', 'https://merchant.test',
        '--allow-unknown-source-version'])
    assert normalized.exit_code == 0, normalized.output
    data = json.loads(normalized.output)['data']
    assert data['classifications'][0]['target_id'] == '2'
    observations = data['categorized_products'][0]['observations']
    standard = next(o for o in observations if o['taxonomy_kind'] == 'standard')
    assert standard['terms'][0]['ref']['taxonomy_version'] is None
    catalog = path / 'normalized.json'
    catalog.write_text(normalized.output)
    output, companion = path / 'products.csv', path / 'categories.json'
    exported = CliRunner().invoke(main, ['export', str(catalog), '--format', 'csv', '--output', str(output),
        '--categories-output', str(companion)])
    assert exported.exit_code == 0, exported.output
    assert output.exists() and companion.exists()


def test_google_cli_missing_yaml_is_an_actionable_dependency(monkeypatch):
    import builtins
    from shopextract._cli_core import CliFailure
    from shopextract._cli_google import native_errors
    from shopextract.taxonomies.google.crosswalk import _decode
    original = builtins.__import__

    def no_yaml(name, *args, **kwargs):
        if name == 'yaml':
            raise ImportError('Deliberately unavailable optional YAML parser')
        return original(name, *args, **kwargs)

    monkeypatch.setattr(builtins, '__import__', no_yaml)

    @native_errors
    def source_operation():
        return _decode(b'input_taxonomy: shopify/2026-08\n')

    with pytest.raises(CliFailure) as error:
        source_operation()
    assert error.value.code == 'E_DEPENDENCY'
    assert 'taxonomy-build' in error.value.message


def test_google_cli_prepares_explicit_snapshot_with_provenance(tmp_path):
    from hashlib import sha256
    source = tmp_path / 'full_names.yml'
    source.write_text('- id: 1\n  full_name: Animals\n- id: 2\n  full_name: Animals > Cats\n')
    result = CliRunner().invoke(main, ['taxonomy', 'google', '--catalog-root', str(tmp_path / 'catalog'),
        'prepare-snapshot', '--source', str(source), '--source-commit', 'a' * 40,
        '--source-url', 'https://example.test/pinned/full_names.yml',
        '--expected-sha256', sha256(source.read_bytes()).hexdigest()])
    assert result.exit_code == 0, result.output
    manifest = json.loads(result.output)['data']['manifest']
    assert manifest['source_kind'] == 'shopify_google_snapshot'
    assert manifest['source_provenance']['source_sha256'] == sha256(source.read_bytes()).hexdigest()
    assert manifest['counts']['categories'] == 2
