"""Shopware Store API extraction using explicit or publicly exposed channel config."""
from datetime import datetime, timezone

from .._capture import capture
from .._models import ExtractorResult
from ._storefront import positive_limits, json_body, request, resolve_config, storefront_client


class ShopwareExtractor:
    def __init__(self, timeout=30, page_size=20, max_pages=100, http_client=None):
        positive_limits(page_size, max_pages)
        self.timeout, self.page_size, self.max_pages = timeout, page_size, max_pages
        self.http_client = http_client

    async def extract(self, shop_url, *, max_products=20, endpoint=None, access_token=None):
        positive_limits(max_products)
        products, seen = [], set()
        try:
            async with storefront_client(self.http_client, self.timeout) as client:
                base, token = await resolve_config(client, shop_url, 'shopware', endpoint, access_token)
                if not base or not token:
                    return ExtractorResult(complete=False, error='Shopware public Store API endpoint/access key unavailable')
                headers = {'sw-access-key':token}
                response = await request(client, 'GET', base + '/context', headers=headers)
                context = json_body(response)
                currency = context['currency']['isoCode']
                currency_context = capture({'currency':context['currency']}, str(response.url), 'shopware_context')['_capture']
                if response.headers.get('sw-context-token'):
                    headers['sw-context-token'] = response.headers['sw-context-token']
                for page in range(1, self.max_pages + 1):
                    response = await request(client, 'POST', base + '/product', headers=headers, json={
                        'page':page, 'limit':self.page_size, 'total-count-mode':1,
                        'sort':[{'field':'id','order':'ASC'}],
                        'associations':{'children':{'limit':50}, 'seoUrls':{}, 'manufacturer':{},
                                        'cover':{'associations':{'media':{}}}}})
                    at = datetime.now(timezone.utc)
                    catalog = json_body(response)
                    items = catalog['elements']
                    if not isinstance(items, list):
                        raise ValueError('Shopware elements is not a list')
                    for item in items:
                        identifier = item.get('id')
                        if not identifier or identifier in seen:
                            raise ValueError('Missing or repeated Shopware product ID')
                        seen.add(identifier)
                        capture(item, str(response.url), 'shopware_store_api', observed_at=at)
                        item['currency'] = currency
                        item['_field_sources'] = {'/currency':{'capture_path':'/currency/isoCode','_capture':currency_context}}
                        products.append(item)
                        if len(products) >= max_products:
                            break
                    total = catalog.get('total')
                    if isinstance(total, int) and len(products) >= total:
                        variants_truncated = any(isinstance(p.get('childCount'), int) and p['childCount'] > len(p.get('children') or []) for p in products)
                        return ExtractorResult(products=products, complete=not variants_truncated,
                            completeness_reason='variant_budget_reached' if variants_truncated else None)
                    if not items:
                        if isinstance(total, int) and total > len(products):
                            raise ValueError('Shopware empty page before catalog exhaustion')
                        variants_truncated = any(isinstance(p.get('childCount'), int) and p['childCount'] > len(p.get('children') or []) for p in products)
                        return ExtractorResult(products=products, complete=not variants_truncated,
                            completeness_reason='variant_budget_reached' if variants_truncated else None)
                    if len(products) >= max_products:
                        break
            return ExtractorResult(products=products, complete=False, completeness_reason='product_or_page_budget_reached')
        except Exception as exc:
            return ExtractorResult(products=products, complete=False, error=f'Shopware Store API unavailable: {type(exc).__name__}', completeness_reason='source_error')
