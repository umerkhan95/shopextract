"""Budget-limited observations must never certify catalog membership changes."""
import importlib
import json
import sqlite3
from dataclasses import asdict
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from shopextract import ChangeType, ExtractionResult, Platform, Product, changes, extract, snapshot
from shopextract._models import ExtractorResult
from shopextract._scope import catalog_scope
from shopextract.extractors.shopify import ShopifyExtractor

URL = 'https://s.example/collections/catan'
SCOPE = catalog_scope(URL, Platform.SHOPIFY)


def raw_products(count):
    return [{'id': i, 'title': f'Widget {i}', 'handle': f'p{i}', 'vendor': 'Acme',
             'body_html': 'Widget description', 'images': [{'src': 'https://s.example/a.png'}],
             'variants': [{'id': i+100, 'price': '10', 'available': True}]}
            for i in range(count)]


def observation(ids, complete, scope=SCOPE, price='10'):
    from decimal import Decimal
    return ExtractionResult(products=[Product(title=f'Widget {i}', external_id=str(i),
                                               platform=Platform.SHOPIFY, price=Decimal(price)) for i in ids],
                            platform=Platform.SHOPIFY, observation_scope=scope,
                            catalog_complete=complete,
                            incompleteness_reasons=['product_budget_reached'] if complete is False else [])


@pytest.mark.asyncio
async def test_full_to_bounded_snapshot_consumes_real_pipeline_completeness(tmp_path):
    async def respond(request):
        # A server ignoring limit must still be bounded and marked incomplete.
        return httpx.Response(200, json={'products': raw_products(18)})
    client = httpx.AsyncClient
    module = importlib.import_module('shopextract.monitor.snapshot')
    async def known_platform(url, **kwargs):
        return await extract(url, platform=Platform.SHOPIFY, **kwargs)
    path = str(tmp_path / 'snapshots.db')
    with patch('shopextract.extractors.shopify.httpx.AsyncClient', side_effect=lambda **kwargs: client(transport=httpx.MockTransport(respond), **kwargs)), patch.object(module, 'extract', known_platform):
        assert await snapshot(URL, db_path=path, max_urls=19) == 18
        assert await snapshot(URL, db_path=path, max_urls=5) == 5
    assert changes('s.example', db_path=path) == []
    with sqlite3.connect(path) as conn:
        rows = conn.execute('SELECT catalog_complete, observation_scope, max_urls, incompleteness_reasons_json FROM snapshots ORDER BY id').fetchall()
    assert rows[0][:3] == (1, SCOPE, 19)
    assert rows[1][:3] == (0, SCOPE, 5)
    assert json.loads(rows[1][3]) == ['product_budget_reached']


@pytest.mark.asyncio
async def test_existing_legacy_full_snapshot_followed_by_partial_is_safe(tmp_path, monkeypatch):
    path = str(tmp_path / 'legacy.db')
    # Pre-upgrade schema and data; do not assign invented completeness or scope.
    with sqlite3.connect(path) as conn:
        conn.execute('CREATE TABLE snapshots(id INTEGER PRIMARY KEY AUTOINCREMENT, domain TEXT NOT NULL, products_json TEXT NOT NULL, created_at TEXT NOT NULL)')
        conn.execute('INSERT INTO snapshots(domain,products_json,created_at) VALUES(?,?,?)',
                     ('s.example', json.dumps([asdict(p) for p in observation(range(18), None).products], default=str), '2026-01-01'))
    module = importlib.import_module('shopextract.monitor.snapshot')
    monkeypatch.setattr(module, 'extract', AsyncMock(return_value=observation(range(5), False)))
    assert await snapshot(URL, db_path=path, max_urls=5) == 5
    assert changes('s.example', db_path=path) == []
    assert changes('s.example', db_path=path) == []  # migration stays idempotent
    with sqlite3.connect(path) as conn:
        rows = conn.execute('SELECT catalog_complete, observation_scope FROM snapshots ORDER BY id').fetchall()
    assert rows == [(None, None), (0, SCOPE)]


@pytest.mark.asyncio
async def test_partial_membership_rotation_suppresses_additions_and_removals_but_keeps_prices(tmp_path, monkeypatch):
    module = importlib.import_module('shopextract.monitor.snapshot')
    monkeypatch.setattr(module, 'extract', AsyncMock(side_effect=[
        observation(range(5), False), observation(range(2, 7), False, price='11')]))
    path = str(tmp_path / 's.db')
    await snapshot(URL, db_path=path, max_urls=5)
    await snapshot(URL, db_path=path, max_urls=5)
    events = changes('s.example', db_path=path)
    assert len(events) == 3 and all(e.change_type == ChangeType.PRICE_CHANGE for e in events)


@pytest.mark.asyncio
@pytest.mark.parametrize('complete', [False, None])
async def test_failed_or_unknown_empty_snapshot_cannot_remove_products(tmp_path, monkeypatch, complete):
    module = importlib.import_module('shopextract.monitor.snapshot')
    monkeypatch.setattr(module, 'extract', AsyncMock(side_effect=[observation(range(3), True), observation([], complete)]))
    path = str(tmp_path / 's.db')
    await snapshot(URL, db_path=path)
    await snapshot(URL, db_path=path)
    assert changes('s.example', db_path=path) == []


@pytest.mark.asyncio
async def test_complete_same_scope_observations_still_confirm_real_membership_changes(tmp_path, monkeypatch):
    module = importlib.import_module('shopextract.monitor.snapshot')
    monkeypatch.setattr(module, 'extract', AsyncMock(side_effect=[observation([1, 2], True), observation([2, 3], True)]))
    path = str(tmp_path / 's.db')
    await snapshot(URL, db_path=path)
    await snapshot(URL, db_path=path)
    events = changes('s.example', db_path=path)
    assert {(e.change_type, e.title) for e in events} == {
        (ChangeType.REMOVED_PRODUCT, 'Widget 1'), (ChangeType.NEW_PRODUCT, 'Widget 3')}


@pytest.mark.asyncio
async def test_complete_empty_shopify_catalog_is_preserved_in_public_result():
    async def respond(request):
        return httpx.Response(200, json={'products': []})
    client = httpx.AsyncClient
    with patch('shopextract.extractors.shopify.httpx.AsyncClient', side_effect=lambda **kwargs: client(transport=httpx.MockTransport(respond), **kwargs)), patch('shopextract._discover.discover', AsyncMock(side_effect=AssertionError('complete empty API should not fall back'))):
        result = await extract(URL, platform=Platform.SHOPIFY, max_urls=5)
    assert result.products == [] and result.catalog_complete is True
    assert result.observation_scope == SCOPE and not result.incompleteness_reasons


@pytest.mark.asyncio
async def test_complete_empty_snapshot_can_confirm_removals(tmp_path, monkeypatch):
    module = importlib.import_module('shopextract.monitor.snapshot')
    monkeypatch.setattr(module, 'extract', AsyncMock(side_effect=[observation([1, 2], True), observation([], True)]))
    path = str(tmp_path / 's.db')
    await snapshot(URL, db_path=path)
    await snapshot(URL, db_path=path)
    assert len(changes('s.example', db_path=path)) == 2
    assert all(e.change_type == ChangeType.REMOVED_PRODUCT for e in changes('s.example', db_path=path))


@pytest.mark.asyncio
async def test_different_collection_scopes_do_not_compare_even_when_complete(tmp_path, monkeypatch):
    module = importlib.import_module('shopextract.monitor.snapshot')
    monkeypatch.setattr(module, 'extract', AsyncMock(side_effect=[observation([1], True), observation([2], True, scope=catalog_scope('https://s.example/collections/chess', Platform.SHOPIFY))]))
    path = str(tmp_path / 's.db')
    await snapshot(URL, db_path=path)
    await snapshot('https://s.example/collections/chess', db_path=path)
    assert changes('s.example', db_path=path) == []


@pytest.mark.asyncio
@pytest.mark.parametrize('count,budget,expected', [(5, 5, False), (18, 5, False), (4, 5, True)])
async def test_short_page_or_budget_boundary_completeness(count, budget, expected):
    client = httpx.AsyncClient
    with patch('shopextract.extractors.shopify.httpx.AsyncClient', side_effect=lambda **kwargs: client(transport=httpx.MockTransport(lambda request: httpx.Response(200, json={'products': raw_products(count)})), **kwargs)):
        result = await ShopifyExtractor().extract(URL, max_products=budget)
    assert result.complete is expected
    assert result.completeness_reason == (None if expected else 'product_budget_reached')


@pytest.mark.asyncio
@pytest.mark.parametrize('second_status', [404, 503])
async def test_failed_later_page_cannot_certify_completeness(second_status):
    def respond(request):
        return httpx.Response(200, json={'products': raw_products(250)}) if request.url.params['page'] == '1' else httpx.Response(second_status)
    client = httpx.AsyncClient
    with patch('shopextract.extractors.shopify.httpx.AsyncClient', side_effect=lambda **kwargs: client(transport=httpx.MockTransport(respond), **kwargs)):
        result = await ShopifyExtractor().extract(URL)
    assert len(result.products) == 250 and not result.complete and result.completeness_reason == 'source_error'


@pytest.mark.asyncio
async def test_page_budget_is_incomplete():
    client = httpx.AsyncClient
    with patch('shopextract.extractors.shopify.httpx.AsyncClient', side_effect=lambda **kwargs: client(transport=httpx.MockTransport(lambda request: httpx.Response(200, json={'products': raw_products(250)})), **kwargs)):
        result = await ShopifyExtractor(max_pages=1).extract(URL)
    assert not result.complete and result.completeness_reason == 'page_budget_reached'


@pytest.mark.asyncio
async def test_normalization_drops_and_api_truncation_carry_reasons():
    for data, limit, reason in [(raw_products(3), 2, 'product_budget_reached'),
                                 (raw_products(1) + [dict(raw_products(1)[0], title='')], 5, 'normalization_dropped_records')]:
        with patch('shopextract._extract._try_api_extraction', AsyncMock(return_value=ExtractorResult(products=data, complete=True))):
            result = await extract(URL, platform=Platform.SHOPIFY, max_urls=limit)
        assert result.catalog_complete is False and reason in result.incompleteness_reasons


def test_scope_keeps_query_and_collection_context():
    assert catalog_scope('https://S.EXAMPLE/collections/catan/#fragment', Platform.SHOPIFY) == SCOPE
    assert catalog_scope(URL + '?currency=CAD', Platform.SHOPIFY) != catalog_scope(URL + '?currency=USD', Platform.SHOPIFY)
    assert catalog_scope('https://s.example/', Platform.SHOPIFY) != SCOPE


@pytest.mark.asyncio
async def test_legacy_unknown_scope_still_blocks_membership_with_complete_current(tmp_path, monkeypatch):
    path = str(tmp_path / 'legacy.db')
    with sqlite3.connect(path) as conn:
        conn.execute('CREATE TABLE snapshots(id INTEGER PRIMARY KEY AUTOINCREMENT, domain TEXT NOT NULL, products_json TEXT NOT NULL, created_at TEXT NOT NULL)')
        conn.execute('INSERT INTO snapshots(domain,products_json,created_at) VALUES(?,?,?)',
                     ('s.example', json.dumps([asdict(p) for p in observation([1, 2], None).products], default=str), '2026-01-01'))
    module = importlib.import_module('shopextract.monitor.snapshot')
    monkeypatch.setattr(module, 'extract', AsyncMock(return_value=observation([2], True, price='11')))
    await snapshot(URL, db_path=path)
    events = changes('s.example', db_path=path)
    assert len(events) == 1 and events[0].change_type == ChangeType.PRICE_CHANGE


@pytest.mark.asyncio
async def test_short_final_page_at_budget_can_prove_exhaustion():
    def respond(request):
        return httpx.Response(200, json={'products': raw_products(250 if request.url.params['page'] == '1' else 10)})
    client = httpx.AsyncClient
    with patch('shopextract.extractors.shopify.httpx.AsyncClient', side_effect=lambda **kwargs: client(transport=httpx.MockTransport(respond), **kwargs)):
        result = await ShopifyExtractor().extract(URL, max_products=260)
    assert len(result.products) == 260 and result.complete and result.completeness_reason is None


def test_read_time_upgrade_of_existing_full_and_bounded_history_is_safe(tmp_path):
    path = str(tmp_path / 'legacy.db')
    with sqlite3.connect(path) as conn:
        conn.execute('CREATE TABLE snapshots(id INTEGER PRIMARY KEY AUTOINCREMENT, domain TEXT NOT NULL, products_json TEXT NOT NULL, created_at TEXT NOT NULL)')
        for count, ts in [(18, '2026-01-01'), (5, '2026-01-02')]:
            conn.execute('INSERT INTO snapshots(domain,products_json,created_at) VALUES(?,?,?)',
                         ('s.example', json.dumps([asdict(p) for p in observation(range(count), None).products], default=str), ts))
    assert changes('s.example', db_path=path) == []
    with sqlite3.connect(path) as conn:
        assert conn.execute('SELECT catalog_complete, observation_scope FROM snapshots').fetchall() == [(None, None), (None, None)]
    from shopextract import price_history
    assert [price for _, price in price_history('s.example', 'Widget 0', db_path=path)] == [10, 10]
