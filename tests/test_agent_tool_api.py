"""Predesigned acceptance reds; production skeleton must fail, never fabricate success."""
import asyncio
import pytest
from shopextract.tools import ToolConfig, ToolRuntime
from shopextract.tools.security import SourceGuard
from tests.tool_api_fixtures import ORIGIN, runtime, CAPTURE_TIME


@pytest.mark.asyncio
async def test_unknown_version_rejected_before_work():
    result = await ToolRuntime(ToolConfig()).call('discover', {'schema_version': '9.0', 'url': ORIGIN})
    assert result['ok'] is False
    assert result['error']['code'] == 'unsupported_version'


@pytest.mark.asyncio
async def test_denied_source_is_structured_error_without_network():
    result = await ToolRuntime(ToolConfig()).call('extract', {'schema_version': '1.0', 'url': 'http://169.254.169.254/'})
    assert result['ok'] is False
    assert result['error']['code'] == 'permission_denied'


@pytest.mark.asyncio
async def test_existing_evidence_denied_through_other_valid_owner(tmp_path):
    from decimal import Decimal
    from shopextract import Evidence, FieldObservation, Product, TrustContract
    from shopextract.monitor.evidence import save_snapshot, get_evidence
    from shopextract.tools.runtime import CaptureGrant
    db = str(tmp_path / 'owners.db')
    ids = []
    evidence_ids = []
    for index, price in enumerate(('10.25', '99.00'), 1):
        eid = f'e_00000000-0000-0000-0000-{index:012d}'
        evidence_ids.append(eid)
        evidence = Evidence(eid, ORIGIN + f'/products/{index}', CAPTURE_TIME, 'synthetic',
            retained_data={'value': price, 'source_pointer': '/offers/price'}, pointer='/value')
        observation = FieldObservation(f'o_00000000-0000-0000-0000-{index:012d}',
            '/price', 'observed', price, Decimal(price), [eid])
        product = Product(title=f'Widget {index}', price=Decimal(price),
            product_url=ORIGIN + f'/products/{index}', external_id=str(index))
        product.evidence_contract = TrustContract([evidence], [observation])
        ids.append(save_snapshot([product], 'store.example', db_path=db))
    # Establish actual retained foreign evidence before the new API is called.
    assert get_evidence(evidence_ids[0], snapshot_id=ids[0], db_path=db).status == 'available'
    engine = ToolRuntime(ToolConfig(captures=tuple(
        CaptureGrant(f'capture{n}', db, sid, 'store.example') for n, sid in enumerate(ids))))
    grants = (await engine.bootstrap())['captures']
    owners = {grant['alias']: grant['owners'][0]['owner_handle'] for grant in grants}
    authorized = await engine.call('evidence', {'schema_version': '1.0',
        'owner': owners['capture0'], 'evidence_id': evidence_ids[0]})
    assert authorized['ok'] is True, authorized
    assert authorized['data']['evidence']['retained_data']['value'] == '10.25'
    denied = await engine.call('evidence', {'schema_version': '1.0',
        'owner': owners['capture1'], 'evidence_id': evidence_ids[0]})
    assert denied['ok'] is False
    assert denied['error']['code'] == 'not_found'
    again = await engine.call('evidence', {'schema_version': '1.0',
        'owner': owners['capture0'], 'evidence_id': evidence_ids[0]})
    assert again['ok'] is True
    assert again['data']['evidence'] == authorized['data']['evidence']
    # Negative control remaps only actual owner scope; dispatch and retrieval stay real.
    original_lookup = engine.store.lookup
    def remapped_lookup(handle, kind):
        if kind == 'owner' and handle == owners['capture1']:
            handle = owners['capture0']
        return original_lookup(handle, kind)
    engine.store.lookup = remapped_lookup
    try:
        broken = await engine.call('evidence', {'schema_version':'1.0',
            'owner':owners['capture1'], 'evidence_id':evidence_ids[0]})
        with pytest.raises(AssertionError):
            assert broken['ok'] is False and broken['error']['code'] == 'not_found'
    finally:engine.store.lookup=original_lookup
    await engine.aclose()


@pytest.mark.asyncio
async def test_invalid_page_size_rejected():
    result = await ToolRuntime(ToolConfig()).call('job_result', {
        'schema_version': '1.0', 'job_id': 'job_unknown', 'collection': 'products', 'page_size': True})
    assert result['ok'] is False
    assert result['error']['code'] == 'invalid_argument'
    from tests.tool_schema_validation import schema_validate
    from shopextract.tools.contracts import schema
    schema_validate(result, schema('job_result')['outputSchema'])


@pytest.mark.asyncio
async def test_guard_refuses_nonpublic_dns_before_connect():
    calls = []
    async def private_dns(host, context):
        calls.append(host)
        return ['127.0.0.1']
    guard = SourceGuard(ToolConfig(allowed_origins=(ORIGIN,)), resolver=private_dns)
    from shopextract.tools.context import OperationContext, OperationBudget
    from shopextract.tools import Limits
    class UnusedAuxiliary:
        async def run(self, *args):
            pytest.fail('Injected boundary unexpectedly launched a worker')
        async def cancel_and_reap(self, *args):
            pytest.fail('Injected boundary unexpectedly owns a worker')
    context = OperationContext('job_test', asyncio.get_running_loop().time() + 2,
        asyncio.Event(), OperationBudget(Limits()), UnusedAuxiliary(), CAPTURE_TIME)
    try:
        await guard.authorize(ORIGIN, context)
    except NotImplementedError:
        raise
    except Exception as error:
        assert getattr(error, 'code', None) == 'permission_denied'
    else:
        pytest.fail('Nonpublic destination was authorized')
    assert len(calls) == 1


async def completed(call, name, arguments):
    accepted = await call(name, {'schema_version': '1.0', **arguments})
    from tests.tool_schema_validation import schema_validate
    from shopextract.tools.contracts import schema
    schema_validate(accepted, schema(name)['outputSchema'])
    assert accepted['ok'] is True, accepted
    job_id = accepted['data']['job_id']
    for _ in range(100):
        status = await call('job_status', {'schema_version': '1.0', 'job_id': job_id})
        assert status['ok'] is True, status
        schema_validate(status, schema('job_status')['outputSchema'])
        state = status['data']['state']
        if state == 'succeeded':
            return job_id
        assert state in {'queued', 'running'}, status
        await asyncio.sleep(0.02)
    pytest.fail('Controlled job did not finish within 100 bounded polls')


async def reference_flow(call):
    discovered = await completed(call, 'discover', {'url': ORIGIN, 'max_items': 2})
    page = await call('job_result', {'schema_version': '1.0', 'job_id': discovered,
                                   'collection': 'urls', 'page_size': 1})
    assert page['ok'] is True, page
    assert page['data']['items'] == [ORIGIN + '/products/widget']
    url = page['data']['items'][0]
    catalogs = []
    product = None
    for _ in range(2):
        jid = await completed(call, 'extract', {'url': url, 'max_items': 1})
        result = await call('job_result', {'schema_version': '1.0', 'job_id': jid,
                                        'collection': 'products', 'page_size': 1})
        assert result['ok'] is True, result
        from tests.tool_schema_validation import schema_validate
        from shopextract.tools.contracts import schema
        schema_validate(result, schema('job_result')['outputSchema'])
        import copy
        from jsonschema import ValidationError
        broken = copy.deepcopy(result)
        broken['data']['items'][0]['price'] = 10.25
        with pytest.raises(ValidationError):schema_validate(broken, schema('job_result')['outputSchema'])
        product = result['data']['items'][0]
        assert product['price'] == '10.25'
        catalogs.append(result['data']['metadata']['catalog_handle'])
    jid = await completed(call, 'match', {'left_catalog': catalogs[0], 'right_catalog': catalogs[1]})
    matches = await call('job_result', {'schema_version': '1.0', 'job_id': jid,
                                      'collection': 'matches', 'page_size': 1})
    from tests.tool_schema_validation import schema_validate
    from shopextract.tools.contracts import schema
    schema_validate(matches, schema('job_result')['outputSchema'])
    assert matches['ok'] is True, matches
    assert len(matches['data']['items']) == 1
    assert matches['data']['items'][0]['relation'] == 'exact'
    lookup = await call('evidence', {'schema_version': '1.0',
        'owner': product['owner_handle'], 'evidence_id': product['field_evidence']['/price'][0]})
    schema_validate(lookup, schema('evidence')['outputSchema'])
    assert lookup['ok'] is True, lookup
    assert lookup['data']['status'] == 'available'
    assert lookup['data']['evidence']['source_url'] == url
    captured = lookup['data']['evidence']
    assert captured['pointer'] == '/value'
    assert captured['retained_data']['value'] == '10.25'
    assert captured['retained_data']['source_pointer'] == '/offers/price'
    assert captured['method'] == 'json_ld'
    assert captured['observed_at'] == CAPTURE_TIME.isoformat()
    assert captured['truncated'] is False


@pytest.mark.asyncio
async def test_complete_domain_flow_uses_native_code_paths():
    await reference_flow(runtime().call)


@pytest.mark.asyncio
async def test_cancel_running_resolution_publishes_no_catalog():
    started = asyncio.Event()
    released = asyncio.Event()
    contexts = []
    async def slow_resolver(host, context):
        contexts.append(context)
        assert context.deadline > asyncio.get_running_loop().time()
        assert context.job_id
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            released.set()
    engine = ToolRuntime(ToolConfig(allowed_origins=(ORIGIN,)), resolver=slow_resolver)
    submit = await engine.call('extract', {'schema_version': '1.0', 'url': ORIGIN, 'max_items': 1})
    assert submit['ok'] is True, submit
    jid = submit['data']['job_id']
    await asyncio.wait_for(started.wait(), timeout=1)
    cancelled = await engine.call('job_cancel', {'schema_version': '1.0', 'job_id': jid})
    assert cancelled['ok'] is True, cancelled
    assert contexts[0].cancelled.is_set()
    await asyncio.wait_for(released.wait(), timeout=1.5)
    status = await engine.call('job_status', {'schema_version': '1.0', 'job_id': jid})
    assert status['data']['state'] == 'cancelled'
    result = await engine.call('job_result', {'schema_version': '1.0', 'job_id': jid, 'collection': 'products'})
    assert result['ok'] is False
    assert result['error']['code'] == 'cancelled'
    assert 'catalog_handle' not in str(result)
