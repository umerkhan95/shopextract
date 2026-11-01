"""WooCommerce Store API product extractor."""

from __future__ import annotations

import asyncio
import logging
import re
from typing import Any

import httpx
from ._storefront import storefront_client

from .._models import ExtractorResult
from .._capture import capture
from ._http_defaults import DEFAULT_HEADERS, get_default_user_agent

logger = logging.getLogger(__name__)


class WooCommerceExtractor:
    """Extract products from WooCommerce stores using the public Store API."""

    def __init__(self, timeout: int = 30, max_pages: int = 100, http_client=None):
        self.timeout = timeout
        self.max_pages = max_pages
        self.http_client = http_client

    async def extract(self, shop_url: str, *, max_products: int | None = None, enrich_variants: bool = False) -> ExtractorResult:
        """Fetch all products from WooCommerce Store API with pagination."""
        if max_products is not None:
            from ._storefront import positive_limits
            positive_limits(max_products)
        all_products: list[dict[str, Any]] = []
        from .._execution import register_progress_source
        from .._models import Platform
        register_progress_source(all_products,Platform.WOOCOMMERCE,shop_url)
        base_url = shop_url.rstrip("/")
        complete = True
        error: str | None = None
        reason=None
        pages_completed=0

        headers = {
            **DEFAULT_HEADERS,
            "User-Agent": get_default_user_agent(),
            "Accept": "application/json",
        }

        async with storefront_client(self.http_client, self.timeout, headers=headers) as client:
            page = 1

            while page <= self.max_pages:
                size=min(100,max_products-len(all_products)) if max_products is not None else 100
                if size<=0:break
                query=f'per_page={size}&page=1&offset={len(all_products)}&orderby=id&order=asc' if max_products is not None else f'per_page=100&page={page}'
                url = f'{base_url}/wp-json/wc/store/v1/products?{query}'
                logger.info("Fetching page %s from %s", page, url)

                try:
                    response = await client.get(url)

                    if response.status_code == 429:
                        from ._retry import wait_for_retry
                        if not await wait_for_retry(response.headers.get('Retry-After','2')):
                            complete=False;error='Retry delay exceeds remaining execution budget';break
                        response = await client.get(url)
                        if response.status_code == 429:
                            complete = False
                            error = f"Rate limited on page {page}"
                            break

                    if response.status_code == 404:
                        complete = False
                        error = f"Store API HTTP 404 on page {page}"
                        break

                    if response.status_code >= 500:
                        complete = False
                        error = f"Server error {response.status_code} on page {page}"
                        break

                    if response.status_code != 200:
                        complete = False
                        error = f"HTTP {response.status_code} on page {page}"
                        break

                    try:
                        products = response.json()
                    except Exception as e:
                        complete = False
                        error = f"Invalid JSON on page {page}: {e}"
                        break

                    if not isinstance(products, list):
                        complete = False
                        error = f"Unexpected response format on page {page}"
                        break

                    pages_completed+=1
                    received=len(products)
                    if not products:break
                    clipped=max_products is not None and received>max_products-len(all_products)
                    retained=products[:max_products-len(all_products)] if max_products is not None else products
                    for product in retained:capture(product,str(response.url),'woocommerce_api')
                    all_products.extend(retained)
                    total_text=response.headers.get('X-WP-Total','')
                    total=int(total_text) if total_text.isascii() and total_text.isdigit() else None
                    exhausted=not clipped and (total is not None and total>=len(all_products) and len(all_products)==total or received<size)
                    if exhausted:break
                    if max_products is not None and len(all_products)>=max_products:
                        complete=False;reason='product_budget_reached';break
                    page+=1
                    if page>self.max_pages:
                        complete=False;reason='page_budget_reached'

                except httpx.TimeoutException:
                    complete = False
                    error = f"Timeout on page {page}"
                    break
                except httpx.RequestError as e:
                    complete = False
                    error = f"Request error on page {page}: {e}"
                    break
                except Exception as e:
                    complete = False
                    error = f"Unexpected error on page {page}: {e}"
                    break

        if enrich_variants:
            attempts=0
            async with storefront_client(self.http_client,self.timeout,headers=headers) as client:
                for parent in all_products:
                    records=parent.get('variations',[])
                    if not isinstance(records,list):
                        complete=False;error='Woo variant declarations are not a list';continue
                    parent_attempts=0
                    descriptors=[v for v in records if isinstance(v,(int,str)) or isinstance(v,dict) and 'price' not in v and 'prices' not in v]
                    for descriptor in descriptors:
                        ident=descriptor.get('id') if isinstance(descriptor,dict) else descriptor
                        valid=isinstance(ident,int) and not isinstance(ident,bool) and ident>0 or isinstance(ident,str) and bool(re.fullmatch(r'[0-9]+',ident)) and bool(ident.strip('0'))
                        if not valid:
                            complete=False;error='Woo variant declaration has invalid route ID';continue
                        if parent_attempts>=5 or attempts>=20:
                            complete=False;error='Woo variant detail budget reached';break
                        attempts+=1;parent_attempts+=1
                        try:
                            response=await client.get(f'{base_url}/wp-json/wc/store/v1/products/{ident}')
                            response.raise_for_status();child=response.json()
                            if not isinstance(child,dict):raise ValueError('Woo variant detail is not an object')
                            if str(child.get('id'))!=str(ident) or str(child.get('parent_id'))!=str(parent.get('id')):
                                raise ValueError('Woo variant identity or parent mismatch')
                            capture(child,str(response.url),'woocommerce_variant_api')
                            # Replace only the declared child; source values belong to detailcapture.
                            position=records.index(descriptor);records[position]=child
                            def bind(value,path=''):
                                if isinstance(value,dict):
                                    for k,v in value.items():
                                        if k!='_capture':bind(v,path+'/'+str(k).replace('~','~0').replace('/','~1'))
                                elif isinstance(value,list):
                                    for j,v in enumerate(value):bind(v,path+'/'+str(j))
                                else:parent.setdefault('_field_sources',{})[f'/variations/{position}'+path]={'capture_path':path,'_capture':child['_capture']}
                            bind(child)
                        except (httpx.HTTPError,ValueError,TypeError,KeyError) as exc:
                            complete=False;error=f'Woo variant detail unavailable: {exc}'

        logger.info("Extraction complete: %s total products from %s pages", len(all_products), page - 1)
        return ExtractorResult(
            products=all_products,
            complete=complete,
            error=error,
            pages_completed=pages_completed,
            completeness_reason=reason,
        )
