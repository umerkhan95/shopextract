"""Magento Open Source / Adobe Commerce PaaS public storefront GraphQL extraction."""
from datetime import datetime, timezone
import json

from .._capture import capture
from .._models import ExtractorResult
from ._storefront import positive_limits, endpoint_url, json_body, request, storefront_client
from ..categories.native import (MAGENTO_CATEGORY_SELECTION, native_body,
                                 attach_category_diagnostics)

_FIELDS = 'sku name url_key url_suffix stock_status description { html } image { url } price_range { minimum_price { final_price { value currency } } }'
_QUERY = '''query Catalog($size:Int!, $page:Int!) {
  products(filter:{}, pageSize:$size, currentPage:$page, sort:{name:ASC}) {
    total_count page_info { current_page total_pages }
    items { __typename FIELDS
      ... on ConfigurableProduct { variants { product { FIELDS } attributes { code value_index } } }
    }
  }
}'''.replace('FIELDS', _FIELDS)

_QUERY_WITH_CATEGORIES = _QUERY.replace(_FIELDS, _FIELDS + ' ' + MAGENTO_CATEGORY_SELECTION)


_CAPABILITIES={'media_gallery':'media_gallery { url }','brand':'brand','gtin':'gtin'}
def validate_capabilities(value):
    if not isinstance(value,(tuple,list)) or any(not isinstance(v,str) or v not in _CAPABILITIES for v in value):
        raise ValueError('Unknown Magento capability; expected media_gallery, brand or gtin')
    return tuple(dict.fromkeys(value))


class MagentoGraphQLExtractor:
    def __init__(self, timeout=30, page_size=20, max_pages=100, http_client=None):
        positive_limits(page_size, max_pages)
        self.timeout, self.page_size, self.max_pages = timeout, page_size, max_pages
        self.http_client = http_client

    async def extract(self, shop_url, *, max_products=20, endpoint=None, access_token=None,
                      include_categories=False, capabilities=()):
        positive_limits(max_products)
        capabilities=validate_capabilities(capabilities)
        query=_QUERY_WITH_CATEGORIES if include_categories else _QUERY
        if capabilities:query=query.replace(_FIELDS,_FIELDS+" "+" ".join(_CAPABILITIES[v] for v in capabilities))
        fallback=False
        products, seen = [], set()
        from .._execution import register_progress_source
        from .._models import Platform
        register_progress_source(products,Platform.MAGENTO,shop_url)
        source_errors = False
        try:
            url = endpoint_url(endpoint or shop_url.rstrip('/') + '/graphql')
            headers = {'Authorization': 'Bearer ' + access_token} if access_token else {}
            async with storefront_client(self.http_client, self.timeout) as client:
                for page in range(1, self.max_pages + 1):
                    size = min(self.page_size, max_products)
                    if size <= 0:
                        break
                    response = await request(client, 'GET', url, headers=headers,
                        params={'query':query, 'variables': json.dumps({'size':size, 'page':page})})
                    payload=response.json()
                    unknown=any('cannot query field' in str(e.get('message','')).lower() for e in payload.get('errors',[]) if isinstance(e,dict)) if isinstance(payload,dict) else False
                    if capabilities and not fallback and unknown:
                        fallback=True;source_errors=True
                        query=_QUERY_WITH_CATEGORIES if include_categories else _QUERY
                        response=await request(client,'GET',url,headers=headers,params={'query':query,'variables':json.dumps({'size':size,'page':page})})
                    at = datetime.now(timezone.utc)
                    body = native_body(response, include_categories=True) if include_categories else json_body(response)
                    errors = body.get('_category_errors', ())
                    source_errors = source_errors or bool(errors)
                    catalog = body['data']['products']
                    items = catalog['items']
                    if not isinstance(items, list):
                        raise ValueError('Magento items is not a list')
                    budget_clipped = len(items) > max_products - len(products)
                    for item_index, item in enumerate(items[:max_products - len(products)]):
                        if include_categories and errors and not isinstance(item, dict):
                            continue
                        sku = item.get('sku')
                        if include_categories and errors and not sku:
                            continue
                        if not sku or sku in seen:
                            raise ValueError('Missing or repeated Magento product SKU')
                        seen.add(sku)
                        captured = capture(item, str(response.url), 'magento_graphql', observed_at=at)
                        if include_categories:
                            attach_category_diagnostics(captured, errors,
                                product_path=('products', 'items', item_index))
                        products.append(captured)
                    info = catalog.get('page_info') or {}
                    total = catalog.get('total_count')
                    # A last-page marker describes the response, not the retained subset.
                    # Known totals take precedence, and clipped records preclude completeness.
                    exhausted = not budget_clipped and (
                        (isinstance(total, int) and len(products) >= total) or (
                            total is None and isinstance(info.get('total_pages'), int)
                            and page >= info['total_pages']))
                    if exhausted or (include_categories and source_errors
                            and isinstance(info.get('total_pages'), int) and page >= info['total_pages']):
                        return ExtractorResult(products=products, complete=not source_errors,
                            error='Magento GraphQL reported partial data' if source_errors else None,
                            completeness_reason='source_error' if source_errors else None)
                    if not items:
                        raise ValueError('Magento returned an empty page before known catalog exhaustion')
                    if len(products) >= max_products:
                        break
            return ExtractorResult(products=products, complete=False,
                error='Magento GraphQL reported partial data' if source_errors else None,
                completeness_reason='source_error' if source_errors else 'product_or_page_budget_reached')
        except Exception as exc:
            return ExtractorResult(products=products, complete=False, error=f'Magento GraphQL unavailable: {type(exc).__name__}', completeness_reason='source_error')
