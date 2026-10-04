"""BigCommerce Storefront GraphQL using published or caller-supplied storefront tokens."""
from datetime import datetime, timezone
from urllib.parse import urljoin, urlsplit
import httpx

from .._capture import capture
from .._models import ExtractorResult
from ._storefront import endpoint_url, positive_limits, json_body, request, resolve_config, storefront_client
from ._bigcommerce_auth import auth_headers, validate_auth

_QUERY = '''query Catalog($size:Int!, $after:String) {
  site { products(first:$size, after:$after) {
    pageInfo { hasNextPage endCursor }
    edges { node { entityId name sku path description upc
      defaultImage { urlOriginal }
      brand { name }
      prices { price { value currencyCode } }
      inventory { isInStock }
      variants(first:50) { pageInfo { hasNextPage } edges { node {
        entityId sku upc prices { price { value currencyCode } } inventory { isInStock }
      } } }
    } }
  } }
}'''


class BigCommerceExtractor:
    def __init__(self, timeout=30, page_size=20, max_pages=100, http_client=None):
        positive_limits(page_size, max_pages)
        self.timeout, self.page_size, self.max_pages = timeout, page_size, max_pages
        self.http_client = http_client

    async def extract(self, shop_url, *, max_products=20, endpoint=None, access_token=None,
                      token_type='storefront', customer_access_token=None, customer_id=None):
        positive_limits(max_products)
        validate_auth(token_type, access_token, customer_access_token, customer_id)
        products, seen, cursors = [], set(), set()
        try:
            async with storefront_client(self.http_client, self.timeout) as client:
                if token_type != 'storefront':
                    url, token = endpoint_url(endpoint or urljoin(shop_url, '/graphql')), access_token
                else:
                    url, token = await resolve_config(client, shop_url, 'bigcommerce', endpoint, access_token)
                if not url or not token:
                    return ExtractorResult(complete=False, error='BigCommerce public storefront token unavailable')
                origin = urlsplit(shop_url if endpoint else url)
                headers = auth_headers(token, token_type, f'{origin.scheme}://{origin.netloc}',
                                       customer_access_token, customer_id)
                cursor = None
                for _ in range(self.max_pages):
                    size = min(self.page_size, max_products - len(products))
                    if size <= 0:
                        break
                    response = await request(client, 'POST', url, headers=headers,
                        json={'query':_QUERY, 'variables':{'size':size, 'after':cursor}})
                    at = datetime.now(timezone.utc)
                    catalog = json_body(response)['data']['site']['products']
                    edges = catalog['edges']
                    if not isinstance(edges, list):
                        raise ValueError('BigCommerce edges is not a list')
                    for edge in edges:
                        item = edge['node']
                        identifier = item.get('entityId')
                        if identifier is None or identifier in seen:
                            raise ValueError('Missing or repeated BigCommerce product ID')
                        seen.add(identifier)
                        products.append(capture(item, str(response.url), 'bigcommerce_graphql', observed_at=at))
                    info = catalog['pageInfo']
                    if info.get('hasNextPage') is False:
                        variants_truncated = any((p.get('variants') or {}).get('pageInfo', {}).get('hasNextPage') is True for p in products)
                        return ExtractorResult(products=products, complete=not variants_truncated,
                            completeness_reason='variant_budget_reached' if variants_truncated else None)
                    cursor = info.get('endCursor')
                    if not edges or not cursor or cursor in cursors:
                        raise ValueError('BigCommerce pagination did not advance')
                    cursors.add(cursor)
            return ExtractorResult(products=products, complete=False, completeness_reason='product_or_page_budget_reached')
        except httpx.HTTPStatusError as exc:
            return ExtractorResult(products=products, complete=False,
                error=f'BigCommerce GraphQL unavailable: HTTP {exc.response.status_code}',
                completeness_reason='source_error')
        except Exception as exc:
            return ExtractorResult(products=products, complete=False, error=f'BigCommerce GraphQL unavailable: {type(exc).__name__}', completeness_reason='source_error')
