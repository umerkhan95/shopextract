"""Magento Open Source / Adobe Commerce PaaS public storefront GraphQL extraction."""
from datetime import datetime, timezone
import json

from .._capture import capture
from .._models import ExtractorResult
from ._storefront import positive_limits, endpoint_url, json_body, request, storefront_client

_FIELDS = 'sku name url_key url_suffix stock_status description { html } image { url } price_range { minimum_price { final_price { value currency } } }'
_QUERY = '''query Catalog($size:Int!, $page:Int!) {
  products(filter:{}, pageSize:$size, currentPage:$page, sort:{name:ASC}) {
    total_count page_info { current_page total_pages }
    items { __typename FIELDS
      ... on ConfigurableProduct { variants { product { FIELDS } attributes { code value_index } } }
    }
  }
}'''.replace('FIELDS', _FIELDS)


class MagentoGraphQLExtractor:
    def __init__(self, timeout=30, page_size=20, max_pages=100, http_client=None):
        positive_limits(page_size, max_pages)
        self.timeout, self.page_size, self.max_pages = timeout, page_size, max_pages
        self.http_client = http_client

    async def extract(self, shop_url, *, max_products=20, endpoint=None, access_token=None):
        positive_limits(max_products)
        products, seen = [], set()
        try:
            url = endpoint_url(endpoint or shop_url.rstrip('/') + '/graphql')
            headers = {'Authorization': 'Bearer ' + access_token} if access_token else {}
            async with storefront_client(self.http_client, self.timeout) as client:
                for page in range(1, self.max_pages + 1):
                    size = min(self.page_size, max_products)
                    if size <= 0:
                        break
                    response = await request(client, 'GET', url, headers=headers,
                        params={'query': _QUERY, 'variables': json.dumps({'size':size, 'page':page})})
                    at = datetime.now(timezone.utc)
                    catalog = json_body(response)['data']['products']
                    items = catalog['items']
                    if not isinstance(items, list):
                        raise ValueError('Magento items is not a list')
                    budget_clipped = len(items) > max_products - len(products)
                    for item in items[:max_products - len(products)]:
                        sku = item.get('sku')
                        if not sku or sku in seen:
                            raise ValueError('Missing or repeated Magento product SKU')
                        seen.add(sku)
                        products.append(capture(item, str(response.url), 'magento_graphql', observed_at=at))
                    info = catalog.get('page_info') or {}
                    total = catalog.get('total_count')
                    # A last-page marker describes the response, not the retained subset.
                    # Known totals take precedence, and clipped records preclude completeness.
                    exhausted = not budget_clipped and (
                        (isinstance(total, int) and len(products) >= total) or (
                            total is None and isinstance(info.get('total_pages'), int)
                            and page >= info['total_pages']))
                    if exhausted:
                        return ExtractorResult(products=products, complete=True)
                    if not items:
                        raise ValueError('Magento returned an empty page before known catalog exhaustion')
                    if len(products) >= max_products:
                        break
            return ExtractorResult(products=products, complete=False, completeness_reason='product_or_page_budget_reached')
        except Exception as exc:
            return ExtractorResult(products=products, complete=False, error=f'Magento GraphQL unavailable: {type(exc).__name__}', completeness_reason='source_error')
