"""BlinkX storefront: branch resolution, catalog tree walk, product page and price rule.

Payload shapes follow shop.imtiaz.com.pk as observed on 2026-11-07.
"""
import json
from decimal import Decimal

import httpx
import pytest

from shopextract import Platform, normalize
from shopextract._detect import _determine_platform
from shopextract.extractors.blinkx import (BlinkXExtractor, LocationError, catalog_scope, product_url,
                                           resolve_branch, store_config)

SHOP = 'https://shop.blinkx.test'
CONFIG = {'restId': 55126, 'appName': 'teststore', 'currency': 'PKR', 'decimal_places': 2}


def page(page_props=None):
    data = {'props': {'pageProps': page_props or {'session': None},
                      'initialState': {'config': {'config': CONFIG}}}, 'page': '/'}
    return ('<html><head></head><body><div id="__next"></div>'
            f'<script id="__NEXT_DATA__" type="application/json">{json.dumps(data)}</script></body></html>')


GEOFENCE = {'status': 200, 'msg': 'success', 'data': {'cities': [
    {'id': 31594, 'name': 'Karachi', 'geofences': [
        {'id': 1, 'area_name': 'Askari 1', 'rest_brId': 54943},
        {'id': 2, 'area_name': 'Clifton', 'rest_brId': 54950}]},
    {'id': 31595, 'name': 'Lahore', 'geofences': [
        {'id': 3, 'area_name': 'Askari 1', 'rest_brId': 60001}]}]}}

MENU = {'status': 200, 'data': [
    {'id': 4095, 'name': 'Dairy', 'section': [{'id': 40567, 'name': 'Milk'}, {'id': 40565, 'name': 'Flavoured Milk'}]},
    {'id': 4093, 'name': 'Fresh', 'section': [{'id': 40556, 'name': 'Fruits & vegetables'}]}]}


def item(id, name, price='409.00', discount='0.00', stock: int | None = 25, code='8964000707142,691900023001'):
    return {'id': id, 'name': name, 'desc': name, 'brand_name': 'Comelle', 'price': price,
            'base_price': '0.00', 'discount_price': discount, 'img_url': 'https://img.test/p.jpg',
            'tp_product_code': code, 'tp_deal_code': 'DAI180000012', 'availability': 1, 'status': 1,
            'slug': None, 'dish_options': [],
            'dish_branch_stock': None if stock is None else {'rest_brId': 54943, 'stock': stock}}


def server(items_by_sub, *, pages=None, calls=None):
    calls = [] if calls is None else calls

    def respond(request):
        calls.append(request)
        path, query = request.url.path, dict(request.url.params)
        if path.startswith('/api/'):
            assert request.headers['app-name'] == 'teststore' and request.headers['rest-id'] == '55126'
        if path == '/api/geofence':
            return httpx.Response(200, json=GEOFENCE)
        if path == '/api/menu-section':
            assert query['rest_brId'] == '54943'
            return httpx.Response(200, json=MENU)
        if path == '/api/sub-section':
            subs = {'40567': [{'id': 43001, 'name': 'Liquid Milk'}, {'id': 43091, 'name': 'Condensed Milk'}],
                    '40565': [{'id': 43010, 'name': 'Flavoured'}]}[query['sectionId']]
            return httpx.Response(200, json={'status': 200, 'data': [{'id': int(query['sectionId']),
                                                                      'dish_sub_sections': subs}]})
        if path == '/api/items-by-subsection':
            assert query['rest_brId'] == '54943' and query['per_page'] == '24'
            rows = items_by_sub.get(query['sub_section_id'], [])
            start = int(query['start'])
            return httpx.Response(200, json={'status': 200, 'msg': 'success', 'data': rows[start:start + 24]})
        if path.startswith('/product/'):
            # Like the live storefront, the item is rendered only for a chosen branch.
            if 'brId=54943' not in request.headers.get('cookie', ''):
                return httpx.Response(200, text=page({'prefetchedItem': None}))
            return httpx.Response(200, text=page({'prefetchedItem': item(365195, 'Comelle Condensed Milk 397g')}))
        return httpx.Response(200, text=(pages or {}).get(path, page()))
    return respond, calls


async def run(url, items_by_sub=None, location: str | None = 'Askari 1, Karachi', max_products=20, calls=None):
    respond, calls = server(items_by_sub or {}, calls=calls)
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        return await BlinkXExtractor(http_client=client).extract(url, max_products=max_products,
                                                                 location=location), calls


def test_store_config_reads_the_next_data_identity_and_rejects_other_pages():
    config = store_config(page(), SHOP + '/')
    assert (config.origin, config.rest_id, config.app_name, config.currency) == (SHOP, 55126, 'teststore', 'PKR')
    assert store_config('<html><script id="__NEXT_DATA__" type="application/json">{"props":{}}</script>',
                        SHOP) is None
    assert store_config('<html>no app</html>', SHOP) is None


def test_detection_names_blinkx_from_the_store_config_signal():
    signals = {p: [] for p in Platform if p != Platform.GENERIC}
    signals[Platform.BLINKX].append('html:blinkx-store-config')
    assert _determine_platform(signals)[0] == Platform.BLINKX


def test_branch_resolution_needs_an_exact_area_and_names_the_city_when_ambiguous():
    assert resolve_branch(GEOFENCE, 'askari 1, karachi') == (54943, 'Askari 1, Karachi')
    assert resolve_branch(GEOFENCE, 'Clifton') == (54950, 'Clifton, Karachi')
    with pytest.raises(LocationError, match='several branches'):
        resolve_branch(GEOFENCE, 'Askari 1')
    with pytest.raises(LocationError, match='No delivery area'):
        resolve_branch(GEOFENCE, 'Askari, Karachi')


def test_catalog_scope_reads_ids_from_storefront_paths():
    assert catalog_scope(SHOP + '/') == ('store', [])
    assert catalog_scope(SHOP + '/catalog/dairy-4095') == ('catalog', [4095])
    assert catalog_scope(SHOP + '/catalog/dairy-4095/milk-40567/condensed-milk-43091') == ('catalog', [4095, 40567, 43091])
    assert catalog_scope(SHOP + '/product/comelle-condensed-milk-397g-365195') == ('product', [365195])
    assert catalog_scope(SHOP + '/privacy-policy') is None


def test_product_url_mirrors_the_storefront_slug():
    assert product_url(SHOP, {'id': 363483, 'name': "Lay's Yogurt & Herb Chip 72g"}) == \
        SHOP + '/product/lays-yogurt--herb-chip-72g-363483'


@pytest.mark.asyncio
async def test_without_location_nothing_is_requested_and_the_reason_is_location_required():
    result, calls = await run(SHOP + '/catalog/dairy-4095', location=None)
    assert not calls and not result.products and not result.complete
    assert result.completeness_reason == 'location_required' and '--location' in result.error


@pytest.mark.asyncio
async def test_unknown_area_is_reported_not_guessed():
    result, _ = await run(SHOP + '/catalog/dairy-4095', location='Nowhere, Karachi')
    assert not result.products and result.completeness_reason == 'location_unmatched'


@pytest.mark.asyncio
async def test_section_url_walks_only_its_sub_sections_and_pages_items():
    liquid = [item(1000 + i, f'Milk {i}', price='100.00') for i in range(30)]
    result, calls = await run(SHOP + '/catalog/dairy-4095/milk-40567',
                              {'43001': liquid, '43091': [item(2000, 'Condensed', price='409.00')]}, max_products=100)
    assert result.complete and len(result.products) == 31
    sub_calls = [dict(c.url.params) for c in calls if c.url.path == '/api/sub-section']
    assert [c['sectionId'] for c in sub_calls] == ['40567']
    item_pages = [(c.url.params['sub_section_id'], c.url.params['page_no']) for c in calls
                  if c.url.path == '/api/items-by-subsection']
    assert item_pages == [('43001', '1'), ('43001', '2'), ('43091', '1')]
    assert result.products[0]['category_path'] == ['Dairy', 'Milk', 'Liquid Milk']
    assert result.products[-1]['branch'] == {'id': 54943, 'area': 'Askari 1, Karachi'}


@pytest.mark.asyncio
async def test_product_budget_stops_the_walk_and_reports_truncation():
    result, calls = await run(SHOP + '/catalog/dairy-4095', {'43001': [item(i, f'M{i}') for i in range(5)]},
                              max_products=2)
    assert not result.complete and len(result.products) == 3
    assert result.completeness_reason == 'product_or_page_budget_reached'
    assert not any(c.url.params.get('sectionId') == '40565' for c in calls)


@pytest.mark.asyncio
async def test_category_absent_at_the_branch_is_a_scope_failure():
    result, _ = await run(SHOP + '/catalog/frozen-4104')
    assert not result.products and result.completeness_reason == 'category_scope_unavailable'


@pytest.mark.asyncio
async def test_product_url_reads_the_branch_item_from_the_product_page():
    result, calls = await run(SHOP + '/product/comelle-condensed-milk-397g-365195')
    assert result.complete and [p['id'] for p in result.products] == [365195]
    assert not any(c.url.path.startswith('/api/items') for c in calls)


@pytest.mark.asyncio
async def test_rate_limit_from_the_api_is_named():
    def respond(request):
        if request.url.path == '/api/geofence':
            return httpx.Response(429, headers={'retry-after': '60'})
        return httpx.Response(200, text=page())
    async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
        result = await BlinkXExtractor(http_client=client).extract(SHOP + '/', location='Clifton')
    assert result.completeness_reason == 'rate_limited' and 'HTTP 429' in result.error


@pytest.mark.asyncio
async def test_normalized_price_follows_the_storefront_discount_rule_and_branch_stock():
    rows = [item(1, 'Plain', price='409.00'), item(2, 'Sale', price='500.00', discount='450.00'),
            item(3, 'Empty', stock=0), item(4, 'No stock row', stock=None)]
    result, _ = await run(SHOP + '/catalog/dairy-4095/milk-40567/liquid-milk-43001', {'43001': rows})
    products = {p.title: p for p in (normalize(raw, Platform.BLINKX, SHOP) for raw in result.products)}
    assert products['Plain'].price == Decimal('409.00') and products['Plain'].compare_at_price is None
    assert products['Sale'].price == Decimal('450.00') and products['Sale'].compare_at_price == Decimal('500.00')
    assert products['Plain'].in_stock and not products['Empty'].in_stock and not products['No stock row'].in_stock
    plain = products['Plain']
    assert plain.currency == 'PKR' and plain.gtin == '8964000707142' and plain.vendor == 'Comelle'
    assert plain.product_url == SHOP + '/product/plain-1'
    assert plain.category_path == ['Dairy', 'Milk', 'Liquid Milk']
    observed = {o.field_path: o.state.value for o in plain.evidence_contract.observations}
    assert observed['/price'] == 'observed' and observed['/currency'] == 'observed'


def test_missing_or_unmatched_location_is_a_usage_failure_not_a_source_failure():
    from shopextract._cli_extract import _source_failure
    for reason in ('location_required', 'location_unmatched'):
        failure = _source_failure({'errors': ['HTTP 404 https://shop.test/wp-json/', 'pass --location "Area, City"'],
                                   'incompleteness_reasons': [reason]})
        assert failure.code == 'E_USAGE' and failure.cause is None and failure.retryable is False
        assert '--location' in failure.message


@pytest.mark.asyncio
async def test_location_is_rejected_for_platforms_that_have_no_branches():
    from shopextract import extract
    with pytest.raises(ValueError, match='only supported for BlinkX'):
        await extract(SHOP, platform=Platform.SHOPIFY, location='Clifton')
