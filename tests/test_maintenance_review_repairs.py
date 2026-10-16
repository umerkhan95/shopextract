"""Independent review I-01..03 regression cases, expected before repairs."""
from dataclasses import replace
import json
import httpx
import pytest
from shopextract.maintenance import Budgets
from tests.test_maintenance_acceptance import Harness, goal, supplier_html
from tests.test_maintenance_advisor import Advisor, ambiguous_goal


@pytest.mark.asyncio
@pytest.mark.parametrize('reverse', [False, True])
async def test_product_cap_cannot_hide_captured_duplicate_identity(tmp_path, reverse):
    h = Harness(tmp_path / 'jobs.db')
    first = json.loads(supplier_html().split('>', 1)[1].rsplit('<', 1)[0])
    second = dict(first, description='Different supplier specification')
    products = [first, second]
    if reverse:
        products.reverse()
    body = '<script type="application/ld+json">' + json.dumps(products) + '</script>'
    h.engine.wire_transport = httpx.MockTransport(lambda request: httpx.Response(200, text=body))
    _, report = await h.run(goal(budgets=Budgets(products=1)))
    assert not any(f['status'] == 'proposed_correction' for f in report['findings'])
    assert report['state'] == 'partial'


@pytest.mark.asyncio
async def test_zero_product_budget_never_discovers_or_sends(tmp_path):
    h = Harness(tmp_path / 'jobs.db')
    _, report = await h.run(goal(product_urls=(), budgets=Budgets(products=0, requests=10)))
    assert h.requests == []
    assert report['state'] == 'partial' and report['stop_reason'] == 'product_budget'
    assert report['findings'] == []


@pytest.mark.asyncio
@pytest.mark.parametrize('mode,expected', [('unknown','model_usage_unknown'), ('overrun','budget_violation')])
async def test_unknown_and_violation_remain_partial_on_repeated_reopen_resume(tmp_path, mode, expected):
    advisor = Advisor(mode)
    h = Harness(tmp_path / 'jobs.db', investigator=advisor)
    key, first = await h.run(ambiguous_goal())
    original_tokens = first['usage']['tokens']
    for _ in range(2):
        fresh = Advisor()
        reopened = Harness(tmp_path / 'jobs.db', investigator=fresh)
        report = await reopened.engine.resume(key)
        assert report['state'] == 'partial' and report['stop_reason'] == expected
        assert report['usage']['tokens'] == original_tokens
        assert fresh.calls == 0


@pytest.mark.asyncio
async def test_advisor_retry_preserves_real_native_partial_source_coverage(tmp_path):
    from shopextract.tools import ToolConfig, Limits
    from tests.test_maintenance_acceptance import ORIGIN
    advisor = Advisor('unknown')
    h = Harness(tmp_path / 'jobs.db', investigator=advisor)
    h.engine.tool_config = ToolConfig(allowed_origins=(ORIGIN,), limits=Limits(item_count=1))
    key, previous = await h.run(ambiguous_goal())
    assert previous['coverage']['source_complete'] is False
    original_coverage = previous['coverage']
    step = next(row['id'] for row in h.store.steps(key) if row['kind'].startswith('advisor:'))
    h.engine.investigator = Advisor()
    current = await h.engine.retry_unknown(key, step)
    assert current['findings'][0]['advisory']['status'] == 'available'
    assert current['usage']['tokens'] == 100 and current['usage']['reserved_tokens'] == 64
    assert current['state'] == 'partial' and current['stop_reason'] == 'source_partial'
    assert current['coverage'] == original_coverage


@pytest.mark.asyncio
@pytest.mark.parametrize('kind', ['extract', 'compare'])
async def test_advisor_success_cannot_complete_unfinished_independent_work(tmp_path, kind):
    h = Harness(tmp_path / 'jobs.db', investigator=Advisor('unknown'))
    key, previous = await h.run(ambiguous_goal())
    h.store.acquire()
    h.store.add_step(key, 'independent:' + kind, kind)
    h.store.release()
    step = next(row['id'] for row in h.store.steps(key) if row['kind'].startswith('advisor:'))
    h.engine.investigator = Advisor()
    current = await h.engine.retry_unknown(key, step)
    assert current['state'] == 'partial'
    assert 'independent:' + kind in current['pending_steps']
    assert current['coverage'] == previous['coverage']
