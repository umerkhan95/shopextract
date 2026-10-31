"""Native CLI policy dispatch, with only the HTTP/provider boundaries controlled."""
import json

import httpx
import pytest
from click.testing import CliRunner

from shopextract.cli import main
from shopextract._execution import current_state


STORE = 'https://supplier.test'
COMMANDS = ('compare', 'analyze', 'compare-catalogs', 'position', 'gaps',
            'snapshot', 'watch', 'categories')


def arguments(name, tmp_path):
    if name == 'compare':
        return ['compare', 'Book', '-s', STORE, '-s', 'https://other.test']
    if name == 'analyze':
        return ['analyze', STORE]
    if name == 'compare-catalogs':
        return ['compare-catalogs', STORE, 'https://other.test']
    if name == 'position':
        path = tmp_path / 'product.json'
        path.write_text('[{"title":"Book","price":"1","currency":"USD"}]')
        return ['competitive', 'position', str(path), '--competitor', STORE]
    if name == 'gaps':
        return ['competitive', 'gaps', STORE, '--competitor', 'https://other.test']
    if name in ('snapshot', 'watch'):
        args = [name, STORE, '--db', str(tmp_path / 'snapshot.db')]
        if name == 'watch':
            args += ['--interval', '0.001', '--max-events', '1']
        return args
    from shopextract._models import Platform
    from shopextract.categories import CategoryOptions, CategoryScope, TargetRegistry
    from shopextract.categories._codec import wire
    options = CategoryOptions(CategoryScope(Platform.SHOPIFY, STORE),
                              TargetRegistry('operator', '1', ('books',)))
    path = tmp_path / 'options.json'
    path.write_text(json.dumps(wire(options)))
    return ['categories', 'extract', STORE, '--options', str(path)]


@pytest.fixture
def source(monkeypatch):
    """Capture the real policy at transport, retaining actual extraction algorithms."""
    observations = []
    def respond(request):
        state = current_state()
        observations.append(state)
        if request.url.path == '/products.json':
            return httpx.Response(200, json={'products': [{
                'id': 1, 'title': 'Book', 'handle': 'book', 'product_type': 'Books',
                'vendor': 'Publisher', 'images': [{'src': STORE + '/book.jpg'}],
                'variants': [{'id': 2, 'price': '1.00', 'sku': 'book',
                              'inventory_quantity': 1}]}]})
        if request.url.path in ('', '/'):
            return httpx.Response(200, headers={'x-shopid': '1'},
                                  text='<meta name="generator" content="shopify">')
        return httpx.Response(404)
    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, 'AsyncClient', lambda *args, **kw:
                        original(*args, **dict(kw, transport=httpx.MockTransport(respond))))
    # Testing policy dispatch does not require a browser; API succeeds first.
    monkeypatch.setattr('shopextract._cli_extract._browser_preflight', lambda: None)
    monkeypatch.setenv('SHOPEXTRACT_LLM_API_KEY', 'synthetic-provider-key')
    return observations


@pytest.mark.parametrize('name', COMMANDS)
@pytest.mark.parametrize('enabled', [False, True])
def test_native_policy_reaches_each_cli_source(name, enabled, tmp_path, source):
    flags = ['--browser', '--allow-llm', '--llm-max-calls', '1'] if enabled else []
    timeout = '0.1' if name == 'watch' else '5'
    result = CliRunner().invoke(main, ['--output-format', 'json',
        *arguments(name, tmp_path), '--timeout', timeout, *flags])
    assert result.exit_code in (0, 3), (result.output, result.exception)
    assert source, 'Expected actual native source requests'
    assert all(state is not None for state in source)
    assert len({id(state) for state in source}) == 1, 'One shared budget per operation'
    state = source[0]
    assert state.policy.browser is enabled
    assert (state.policy.llm is not None) is enabled
    assert state.llm_calls == 0, 'Sufficient API data must not invoke a provider'
    if enabled:
        assert state.policy.llm.max_calls == 1


def test_category_native_mode_rejects_llm_before_source(tmp_path, source):
    result = CliRunner().invoke(main, ['--output-format', 'json',
        *arguments('categories', tmp_path), '--source-mode', 'native', '--allow-llm'])
    assert result.exit_code == 2, result.output
    assert not source
    assert json.loads(result.output)['error']['code'] == 'E_USAGE'


def test_explicit_llm_options_require_enablement(tmp_path, source):
    result = CliRunner().invoke(main, ['--output-format', 'json',
        *arguments('analyze', tmp_path), '--llm-max-calls', '1'])
    assert result.exit_code == 2, result.output
    assert not source


def test_watch_keeps_required_timeout_grammar(tmp_path, source):
    option = next(p for p in main.commands['watch'].params if p.name == 'timeout')
    assert option.required is True
    result = CliRunner().invoke(main, ['--output-format', 'json', *arguments('watch', tmp_path)])
    assert result.exit_code == 2
    assert not source


def test_two_stores_share_one_actual_provider_budget(monkeypatch):
    """Real fallback/LLM budget code; only seeder, HTTP and provider are controlled."""
    from types import SimpleNamespace
    import crawl4ai
    import litellm
    submissions = []
    states = []
    class Seeder:
        async def __aenter__(self): return self
        async def __aexit__(self, *args): pass
        async def urls(self, *args): return []
    async def complete(**kwargs):
        submissions.append(kwargs)
        states.append(current_state())
        return SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=
            '[{"title":"Book","price":"1.00","currency":"USD"}]'))])
    def respond(request):
        if request.url.path in ('', '/'):
            return httpx.Response(200, text='<html><h1>Book</h1><p>USD1.00</p></html>')
        return httpx.Response(404)
    original = httpx.AsyncClient
    monkeypatch.setattr(httpx, 'AsyncClient', lambda *args, **kw:
        original(*args, **dict(kw, transport=httpx.MockTransport(respond))))
    # _discover imports this external discovery provider when first imported.
    import shopextract._discover as discovery
    monkeypatch.setattr(discovery, 'AsyncUrlSeeder', Seeder)
    monkeypatch.setattr(litellm, 'acompletion', complete)
    monkeypatch.setenv('SHOPEXTRACT_LLM_API_KEY', 'synthetic-provider-key')
    result = CliRunner().invoke(main, ['--output-format','json','compare','Book',
        '-s',STORE,'-s','https://other.test','--allow-llm','--llm-max-calls','1','--timeout','5'])
    assert result.exit_code == 3, (result.output, result.exception)
    assert len(submissions) == 1
    assert states[0].llm_calls == 1
    assert 'synthetic-provider-key' not in result.output
