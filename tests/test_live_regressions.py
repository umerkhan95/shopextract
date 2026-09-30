"""Regression checks derived from the September 30 bounded live sample."""
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from shopextract import Platform, classify_match, extract, match_products, normalize
from shopextract.compare.catalog import _diff_catalogs
from shopextract.extractors.shopify import ShopifyExtractor
from shopextract._models import ExtractorResult

ROWS = json.loads((Path(__file__).parent / 'fixtures/live_catan_pairs.json').read_text())
ALIASES = {row['b']['variants'][0]['barcode']: ['Mayfair Games', 'Catan Studio'] for row in ROWS}


def test_explicit_availability_and_observed_currency():
    p = normalize({'title': 'Sold out', 'id': 1, '_shop_currency': 'USD',
                   'variants': [{'id': 1, 'price': '10', 'price_currency': 'CAD', 'available': False, 'inventory_quantity': 9}]}, Platform.SHOPIFY, 'https://s.example')
    assert p.currency == 'CAD' and not p.in_stock and not p.variants[0].in_stock
    p = normalize({'title': 'Mixed', 'id': 1, 'variants': [
        {'id': 1, 'price': '10', 'available': False}, {'id': 2, 'price': '20', 'available': True}]}, Platform.SHOPIFY, 'https://s.example')
    assert p.in_stock and not p.variants[0].in_stock and p.variants[1].in_stock


def test_restored_upc_is_explicit_and_checksum_validated():
    raw = {'title': 'Widget', 'id': 1, 'variants': [{'id': 1, 'price': '10', 'barcode': '29877030712'}]}
    assert normalize(raw, Platform.SHOPIFY, 'https://s.example').gtin is None
    assert normalize(raw, Platform.SHOPIFY, 'https://s.example', restore_short_gtin=True).gtin == '0029877030712'
    raw['variants'][0]['barcode'] = '29877030713'
    assert normalize(raw, Platform.SHOPIFY, 'https://s.example', restore_short_gtin=True).gtin is None


def test_live_corresponding_pairs_and_catalog_with_explicit_policy():
    a = [normalize(row['a'], Platform.SHOPIFY, 'https://a.example', restore_short_gtin=True) for row in ROWS]
    b = [normalize(row['b'], Platform.SHOPIFY, 'https://b.example', restore_short_gtin=True) for row in ROWS]
    assert all(p.currency == 'CAD' for p in a + b)
    assert not classify_match(a[0], b[0]).relation == 'exact'
    report = match_products(a, b, publisher_aliases=ALIASES)
    assert len(report) == 4 and all(d.relation == 'exact' and not d.needs_review for d in report)
    assert all(d.index_a == d.index_b for d in report)
    diff = _diff_catalogs('a', 'b', a, b, .8, publisher_aliases=ALIASES)
    assert len(diff.in_both) == 4
    # Alias approval applies only to the specified GTIN and never to shared local SKUs.
    wrong = {'title': a[0].title, 'vendor': 'Mayfair Games', 'sku': 'LOCAL'}
    other = {'title': a[0].title, 'vendor': 'Catan Studio', 'sku': 'LOCAL'}
    assert classify_match(wrong, other, publisher_aliases=ALIASES).relation != 'exact'
    b[0].attributes['memory'] = '16GB'
    assert classify_match(a[0], b[0], publisher_aliases=ALIASES).relation != 'exact'


@pytest.mark.asyncio
async def test_shopify_budget_and_id_checked_enrichment():
    requests = []
    async def respond(request):
        requests.append(request)
        if request.url.path.endswith('/products.json'):
            return httpx.Response(200, json={'products': [
                {'id': i, 'title': f'Widget {i}', 'handle': f'p{i}', 'variants': [{'id': i + 10, 'price': '10'}]} for i in range(5)]})
        return httpx.Response(200, json={'id': 0 if request.url.path == '/products/p0.js' else 999,
                                       'variants': [{'id': 10, 'barcode': '29877030712', 'price': 999, 'available': False}]})
    transport = httpx.MockTransport(respond)
    factory = httpx.AsyncClient
    with patch('shopextract.extractors.shopify.httpx.AsyncClient', side_effect=lambda **kwargs: factory(transport=transport, **kwargs)):
        result = await ShopifyExtractor().extract('https://s.example/collections/catan', max_products=2, enrich_identifiers=True)
    assert len(result.products) == 2 and len(requests) == 3
    assert requests[0].url.params['limit'] == '2'
    assert result.products[0]['variants'][0]['barcode'] == '29877030712'
    normalized = normalize(result.products[0], Platform.SHOPIFY, 'https://s.example', restore_short_gtin=True)
    decision = classify_match(normalized, normalized)
    assert any('/products/p0.js' in item for item in decision.evidence)
    assert result.products[0]['variants'][0]['price'] == '10'
    assert '_identifier_sources' in result.products[0]
    assert not result.products[1]['variants'][0].get('barcode')


@pytest.mark.asyncio
async def test_public_api_budget_and_invalid_budgets():
    products = [dict(ROWS[0]['a']) for _ in range(8)]
    with patch('shopextract._extract._try_api_extraction', AsyncMock(return_value=ExtractorResult(products=products))) as api:
        result = await extract('https://s.example', platform=Platform.SHOPIFY, max_urls=3)
    assert len(result.products) == len(result.raw_products) == 3
    assert api.call_args.kwargs['max_products'] == 3
    for value in (0, -1, True):
        with pytest.raises(ValueError):
            await extract('https://s.example', max_urls=value)


def test_category_alone_does_not_emit_substitute_candidates():
    a = {'title': 'Catan base game', 'product_type': 'Board Games'}
    b = {'title': 'Chess accessories', 'product_type': 'Board Games'}
    assert classify_match(a, b).relation == 'unmatched'
    report = match_products([a], [b])
    assert len(report) == 2 and all(d.relation == 'unmatched' for d in report)


@pytest.mark.asyncio
async def test_enrichment_failure_retains_products_and_surfaces_error():
    async def respond(request):
        if request.url.path.endswith('/products.json'):
            return httpx.Response(200, json={'products': [
                {'id': 1, 'title': 'Widget', 'handle': 'widget', 'vendor': 'Acme',
                 'images': [{'src': 'https://s.example/a.png'}], 'body_html': 'Widget',
                 'variants': [{'id': 10, 'price': '10', 'available': False}]}]})
        return httpx.Response(503)
    factory = httpx.AsyncClient
    with patch('shopextract.extractors.shopify.httpx.AsyncClient', side_effect=lambda **kwargs: factory(transport=httpx.MockTransport(respond), **kwargs)):
        result = await extract('https://s.example', platform=Platform.SHOPIFY, max_urls=1, enrich_identifiers=True)
    assert len(result.products) == 1 and result.products[0].gtin is None
    assert result.errors and '503' in result.errors[0]
    assert not result.products[0].in_stock


@pytest.mark.asyncio
async def test_budget_across_pages_keeps_constant_page_size():
    requests = []
    async def respond(request):
        requests.append(request)
        page = int(request.url.params['page'])
        return httpx.Response(200, json={'products': [{'id': (page-1)*250+i} for i in range(250)]})
    factory = httpx.AsyncClient
    with patch('shopextract.extractors.shopify.httpx.AsyncClient', side_effect=lambda **kwargs: factory(transport=httpx.MockTransport(respond), **kwargs)):
        result = await ShopifyExtractor().extract('https://s.example', max_products=260)
    assert len(result.products) == 260 and result.pages_completed == 2
    assert len(requests) == 2 and all(r.url.params['limit'] == '250' for r in requests)
    assert len({p['id'] for p in result.products}) == 260


def test_numeric_supplier_upc_repair_is_still_explicit():
    raw = {'title': 'Widget', 'id': 1, 'variants': [{'id': 1, 'price': '10', 'barcode': 29877030712}]}
    assert normalize(raw, Platform.SHOPIFY, 'https://s.example').gtin is None
    assert normalize(raw, Platform.SHOPIFY, 'https://s.example', restore_short_gtin=True).gtin == '0029877030712'
    assert raw['variants'][0]['barcode'] == 29877030712


def test_labeled_selected_live_matrix_with_same_explicit_policy():
    from dataclasses import asdict
    from shopextract import evaluate_matching
    a = [normalize(row['a'], Platform.SHOPIFY, 'https://a.example', restore_short_gtin=True) for row in ROWS]
    b = [normalize(row['b'], Platform.SHOPIFY, 'https://b.example', restore_short_gtin=True) for row in ROWS]
    rows = [{'id': f'{i}:{j}', 'a': asdict(x), 'b': asdict(y), 'label': 'exact' if i == j else 'unmatched'}
            for i, x in enumerate(a) for j, y in enumerate(b)]
    r = evaluate_matching(rows, publisher_aliases=ALIASES)
    assert r['total_pairs'] == 16 and r['labeled_exact'] == 4
    assert r['precision'] == r['coverage'] == 1 and r['false_exact'] == 0
