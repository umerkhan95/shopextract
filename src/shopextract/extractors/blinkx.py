"""BlinkX white-label storefronts read through their public storefront API.

BlinkX (EatMubarak) serves grocery and retail stores such as shop.imtiaz.com.pk
as a Next.js app. The page HTML carries the store's ``restId`` and ``appName``
in ``__NEXT_DATA__``; products come from the same-origin ``/api`` endpoints the
storefront calls itself, identified by ``app-name`` and ``rest-id`` headers.

Prices and stock belong to a branch, and the storefront asks the shopper for a
delivery area before it shows any product. The extractor therefore needs a
location; it resolves "Area, City" to the branch through ``/api/geofence`` and
never picks a branch on the caller's behalf.

The catalog is a tree: category -> section -> sub-section -> items, and the
storefront URLs carry each node's id (``/catalog/dairy-4095/milk-40567/...``).
A product URL ends with the item id (``/product/<slug>-365195``); the product
page renders the item for the branch named by the ``brId`` cookie.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlencode, urlsplit

from .._capture import capture
from .._models import ExtractorResult
from ._storefront import json_body, positive_limits, request, storefront_client

# The storefront's own page size for items-by-subsection.
PAGE_SIZE = 24
# Requests one extraction may spend on the catalog tree and item pages.
MAX_REQUESTS = 80

_NEXT_DATA = re.compile(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', re.S)
_CATALOG_IDS = re.compile(r'-(\d+)$')
_PRODUCT_PATH = re.compile(r'^/product/[^/]*-(\d+)/?$')


class LocationError(ValueError):
    """The requested location does not name a delivery area of this store."""


@dataclass(frozen=True)
class StoreConfig:
    origin: str
    rest_id: int
    app_name: str
    currency: str | None


def next_data(html: str) -> dict | None:
    match = _NEXT_DATA.search(html or '')
    if not match:
        return None
    try:
        value = json.loads(match.group(1))
    except ValueError:
        return None
    return value if isinstance(value, dict) else None


def store_config(html: str, page_url: str) -> StoreConfig | None:
    """Read the BlinkX store identity from the page; None when the page is not BlinkX."""
    try:
        config = (next_data(html) or {})['props']['initialState']['config']['config']
    except (KeyError, TypeError):
        return None
    if not isinstance(config, dict):
        return None
    rest_id, app_name = config.get('restId'), config.get('appName')
    if not isinstance(rest_id, int) or isinstance(rest_id, bool) or not isinstance(app_name, str) or not app_name:
        return None
    parts = urlsplit(page_url)
    currency = config.get('currency')
    return StoreConfig(f'{parts.scheme}://{parts.netloc}', rest_id, app_name,
                       currency if isinstance(currency, str) and currency else None)


def resolve_branch(geofence: dict, location: str) -> tuple[int, str]:
    """Match "Area, City" (or a bare area) to the branch serving that area."""
    wanted = [part.strip().casefold() for part in location.split(',') if part.strip()]
    if not wanted:
        raise LocationError('Location is empty')
    area, city = wanted[0], (wanted[-1] if len(wanted) > 1 else None)
    matches = []
    for entry in (geofence.get('data') or {}).get('cities') or []:
        city_name = str(entry.get('name') or '')
        if city is not None and city_name.casefold() != city:
            continue
        for fence in entry.get('geofences') or []:
            branch = fence.get('rest_brId')
            if str(fence.get('area_name') or '').strip().casefold() == area and isinstance(branch, int):
                matches.append((branch, f"{fence['area_name'].strip()}, {city_name}"))
    branches = {branch for branch, _ in matches}
    if not matches:
        raise LocationError(f'No delivery area matches {location!r}')
    if len(branches) > 1:
        raise LocationError(f'{location!r} matches several branches; name the city as "Area, City"')
    return matches[0]


def catalog_scope(url: str) -> tuple[str, list[int]] | None:
    """Classify a storefront URL as ('product', [id]), ('catalog', ids) or ('store', [])."""
    path = urlsplit(url).path
    product = _PRODUCT_PATH.match(path)
    if product:
        return 'product', [int(product.group(1))]
    segments = [segment for segment in path.split('/') if segment]
    if not segments:
        return 'store', []
    if segments[0] != 'catalog' or not 2 <= len(segments) <= 4:
        return None
    ids = []
    for segment in segments[1:]:
        match = _CATALOG_IDS.search(segment)
        if not match:
            return None
        ids.append(int(match.group(1)))
    return 'catalog', ids


def product_url(origin: str, item: dict) -> str:
    """The storefront resolves products by the trailing id; the slug mirrors its own."""
    slug = item.get('slug')
    if not isinstance(slug, str) or not slug:
        slug = re.sub(r'[^a-z0-9 -]', '', str(item.get('name') or '').lower()).strip().replace(' ', '-')
    return f"{origin}/product/{slug}-{item['id']}"


class _Budget(Exception):
    pass


class _ScopeMissing(LookupError):
    pass


class BlinkXExtractor:
    def __init__(self, timeout=30, http_client=None, max_requests=MAX_REQUESTS):
        positive_limits(max_requests)
        self.timeout, self.http_client, self.max_requests = timeout, http_client, max_requests
        self.requests = 0

    async def extract(self, url, *, max_products=20, location=None, page_html=None):
        positive_limits(max_products)
        products: list[dict] = []
        from .._execution import register_progress_source
        from .._models import Platform
        register_progress_source(products, Platform.BLINKX, url)
        scope = catalog_scope(url)
        if scope is None:
            return ExtractorResult(complete=False, error='BlinkX URL is not a store, catalog or product page',
                                   completeness_reason='category_scope_unavailable')
        if not location:
            return ExtractorResult(complete=False, completeness_reason='location_required',
                                   error='BlinkX prices and stock belong to a delivery branch; pass --location "Area, City"')
        try:
            async with storefront_client(self.http_client, self.timeout) as client:
                if page_html is None:
                    page_html = (await self._get(client, url)).text
                config = store_config(page_html, url)
                if config is None:
                    return ExtractorResult(complete=False, error='BlinkX store configuration not found in page',
                                           completeness_reason='source_error')
                headers = {'app-name': config.app_name, 'rest-id': str(config.rest_id),
                           'accept': 'application/json'}
                geofence = json_body(await self._get(client, self._api(config, 'geofence'), headers=headers))
                branch, area = resolve_branch(geofence, location)
                context = {'config': config, 'branch': branch, 'area': area, 'headers': headers,
                           'currency_capture': capture({'currency': config.currency}, url,
                                                       'blinkx_store_config')['_capture']}
                kind, ids = scope
                if kind == 'product':
                    item = await self._product(client, url, branch)
                    if item is not None:
                        products.append(self._record(item, context, url, []))
                    return ExtractorResult(products=products, complete=item is not None,
                                           completeness_reason=None if item else 'source_error',
                                           error=None if item else 'BlinkX product page carried no item for this branch')
                complete = await self._catalog(client, context, ids, products, max_products + 1)
                return ExtractorResult(products=products, complete=complete,
                                       completeness_reason=None if complete else 'product_or_page_budget_reached')
        except LocationError as exc:
            return ExtractorResult(products=products, complete=False, error=str(exc),
                                   completeness_reason='location_unmatched')
        except _ScopeMissing:
            return ExtractorResult(products=products, complete=False,
                                   error='The requested category is not offered at this branch',
                                   completeness_reason='category_scope_unavailable')
        except _Budget:
            return ExtractorResult(products=products, complete=False,
                                   completeness_reason='product_or_page_budget_reached')
        except Exception as exc:
            status = getattr(getattr(exc, 'response', None), 'status_code', None)
            reason = {429: 'rate_limited', 401: 'blocked', 403: 'blocked'}.get(status, 'source_error')
            detail = f'HTTP {status}' if status else type(exc).__name__
            return ExtractorResult(products=products, complete=False,
                                   error=f'BlinkX storefront API unavailable: {detail}', completeness_reason=reason)

    async def _get(self, client, url, **kwargs):
        if self.requests >= self.max_requests:
            raise _Budget()
        self.requests += 1
        return await request(client, 'GET', url, **kwargs)

    @staticmethod
    def _api(config, name, **params):
        query = urlencode({'restId': config.rest_id, **params})
        return f'{config.origin}/api/{name}?{query}'

    async def _product(self, client, url, branch):
        response = await self._get(client, url, headers={'cookie': f'brId={branch}; lang=en'})
        data = next_data(response.text) or {}
        item = (data.get('props') or {}).get('pageProps', {}).get('prefetchedItem')
        return item if isinstance(item, dict) and 'id' in item else None

    async def _catalog(self, client, context, ids, products, limit) -> bool:
        """Walk the requested part of the tree; True only when every item page was read."""
        config, branch, headers = context['config'], context['branch'], context['headers']
        common = {'rest_brId': branch, 'delivery_type': 0, 'source': ''}
        menu = json_body(await self._get(client, self._api(config, 'menu-section', **common), headers=headers))
        categories = [c for c in menu.get('data') or [] if isinstance(c, dict)]
        if ids:
            categories = [c for c in categories if str(c.get('id')) == str(ids[0])]
            if not categories:
                raise _ScopeMissing()
        for category in categories:
            sections = [s for s in category.get('section') or [] if isinstance(s, dict)]
            if len(ids) > 1:
                sections = [s for s in sections if str(s.get('id')) == str(ids[1])]
            for section in sections:
                payload = json_body(await self._get(client, self._api(
                    config, 'sub-section', sectionId=section['id'], **common), headers=headers))
                subs = [sub for node in payload.get('data') or [] if isinstance(node, dict)
                        for sub in node.get('dish_sub_sections') or [] if isinstance(sub, dict)]
                if len(ids) > 2:
                    subs = [sub for sub in subs if str(sub.get('id')) == str(ids[2])]
                for sub in subs:
                    path = [category.get('name'), section.get('name'), sub.get('name')]
                    if not await self._items(client, context, sub['id'], [p for p in path if p], products, limit):
                        return False
        return True

    async def _items(self, client, context, sub_id, path, products, limit) -> bool:
        config, branch, headers = context['config'], context['branch'], context['headers']
        seen = {item.get('id') for item in products}
        for page in range(1, 1000):
            start = (page - 1) * PAGE_SIZE
            url = self._api(config, 'items-by-subsection', rest_brId=branch, sub_section_id=sub_id,
                            delivery_type=0, source='', brand_name='', min_price=0, max_price='',
                            sort_by='', sort='', page_no=page, per_page=PAGE_SIZE, start=start, limit=PAGE_SIZE)
            response = await self._get(client, url, headers=headers)
            items = json_body(response).get('data') or []
            if not isinstance(items, list):
                raise ValueError('BlinkX items is not a list')
            at = datetime.now(timezone.utc)
            for item in items:
                if not isinstance(item, dict) or 'id' not in item or item['id'] in seen:
                    continue
                seen.add(item['id'])
                products.append(self._record(item, context, str(response.url), path, observed_at=at))
                if len(products) >= limit:
                    return False
            if len(items) < PAGE_SIZE:
                return True
        return False

    @staticmethod
    def _record(item, context, source_url, path, *, observed_at=None):
        config = context['config']
        capture(item, source_url, 'blinkx_store_api', observed_at=observed_at)
        item['product_url'] = product_url(config.origin, item)
        # Normalization rebuilds the link from the captured id and slug, so the
        # link's support is the API record, not an uncaptured derived value.
        item['_storefront_origin'] = config.origin
        # Currency is the store's, read from the page configuration.
        item['currency'] = config.currency
        item['_field_sources'] = {'/currency': {'capture_path': '/currency', '_capture': context['currency_capture']}}
        item['branch'] = {'id': context['branch'], 'area': context['area']}
        if path:
            item['category_path'] = path
        return item
