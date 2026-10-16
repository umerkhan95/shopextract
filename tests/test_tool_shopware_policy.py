"""NS01–03 approved fixed Shopware read-search policy, not arbitrary POST."""
import asyncio
from datetime import datetime, timezone
import httpx
import pytest
from shopextract.tools import ToolConfig, Limits
from shopextract.tools.context import OperationContext, OperationBudget
from shopextract.tools.security import SourceGuard, GuardedTransport, NativeReadPolicy
from shopextract.tools.contracts import ToolError
from tests.tool_api_fixtures import ORIGIN, resolver

SEARCH = {'page': 1, 'limit': 20, 'total-count-mode': 1,
          'sort': [{'field': 'id', 'order': 'ASC'}],
          'associations': {'children': {'limit': 50}, 'seoUrls': {},
                           'manufacturer': {}, 'cover': {'associations': {'media': {}}}}}


def transport(sent, policy=True, redirect=False):
    config = ToolConfig(allowed_origins=(ORIGIN,))
    context = OperationContext('ns', asyncio.get_running_loop().time()+5, asyncio.Event(),
        OperationBudget(Limits()), None, datetime.now(timezone.utc))
    def wire(request):
        sent.append(str(request.url))
        return httpx.Response(307, headers={'location': ORIGIN+'/store-api/order'}) if redirect else httpx.Response(200, json={'elements': []})
    return GuardedTransport(config, context, SourceGuard(config, resolver=resolver),
        httpx.MockTransport(wire), policy=NativeReadPolicy(ORIGIN+'/store-api/product') if policy else NativeReadPolicy())


@pytest.mark.asyncio
async def test_fixed_native_search_and_denied_redirect_target():
    sent = []
    async with httpx.AsyncClient(transport=transport(sent)) as client:
        assert (await client.post(ORIGIN+'/store-api/product', json=SEARCH)).status_code == 200
    sent.clear()
    async with httpx.AsyncClient(transport=transport(sent, redirect=True)) as client:
        with pytest.raises(ToolError, match='permission_denied'):
            await client.post(ORIGIN+'/store-api/product', json=SEARCH)
    assert sent == [ORIGIN+'/store-api/product']


@pytest.mark.asyncio
async def test_denied_policy_route_and_body_never_send():
    import copy
    sent = []
    bad = []
    for key, value in [('page', True), ('page', 0), ('limit', 21), ('total-count-mode', False),
                       ('sort', []), ('mutation', 'delete')]:
        body = copy.deepcopy(SEARCH)
        body[key] = value
        bad.append(body)
    nested = copy.deepcopy(SEARCH)
    nested['associations']['children']['delete'] = True
    bad.append(nested)
    async with httpx.AsyncClient(transport=transport(sent)) as client:
        for body in bad:
            with pytest.raises(ToolError, match='permission_denied'):
                await client.post(ORIGIN+'/store-api/product', json=body)
        for path in ['/store-api/order', '/store-api/product/a', '/store-api/product?x=1']:
            with pytest.raises(ToolError, match='permission_denied'):
                await client.post(ORIGIN+path, json=SEARCH)
    async with httpx.AsyncClient(transport=transport(sent, policy=False)) as client:
        with pytest.raises(ToolError, match='permission_denied'):
            await client.post(ORIGIN+'/store-api/product', json=SEARCH)
    assert sent == []
