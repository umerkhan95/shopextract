"""Magento 2 REST API product extractor."""

from __future__ import annotations

import logging
import math
from typing import Any

import httpx

from .._models import ExtractorResult
from .._capture import capture
from ._browser import DEFAULT_HEADERS, get_default_user_agent

logger = logging.getLogger(__name__)


class MagentoExtractor:
    """Extract products through explicitly selected legacy REST, with optional authentication."""

    def __init__(self, timeout: int = 30, page_size: int = 100, max_pages: int = 100):
        self.timeout = timeout
        self.page_size = page_size
        self.max_pages = max_pages

    async def extract(self, shop_url: str, *, max_products: int | None = None,
                      endpoint: str | None = None, access_token: str | None = None) -> ExtractorResult:
        """Fetch all products from Magento 2 REST API with pagination."""
        all_products: list[dict[str, Any]] = []
        base_url = shop_url.rstrip("/")
        current_page = 1
        complete = True
        error: str | None = None
        total_count: int = 0

        headers = {
            **DEFAULT_HEADERS,
            "User-Agent": get_default_user_agent(),
            "Accept": "application/json",
        }

        if access_token:
            headers['Authorization'] = 'Bearer ' + access_token

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers=headers) as client:
            while current_page <= self.max_pages:
                url = (
                    f"{endpoint or base_url + '/rest/V1/products'}?"
                    f"searchCriteria[pageSize]={self.page_size}&"
                    f"searchCriteria[currentPage]={current_page}"
                )
                logger.info("Fetching page %s from %s", current_page, url)

                try:
                    response = await client.get(url)

                    if response.status_code == 404:
                        if not all_products:
                            complete = False
                            error = "API not available (404)"
                        break

                    if response.status_code == 429:
                        complete = False
                        error = f"Rate limited on page {current_page}"
                        break

                    if response.status_code >= 500:
                        complete = False
                        error = f"Server error {response.status_code} on page {current_page}"
                        break

                    if response.status_code != 200:
                        complete = False
                        error = f"HTTP {response.status_code} on page {current_page}"
                        break

                    try:
                        data = response.json()
                    except Exception as e:
                        complete = False
                        error = f"Invalid JSON on page {current_page}: {e}"
                        break

                    products = data.get("items", [])
                    total_count = data.get("total_count", 0)

                    if not products:
                        break

                    for product in products:
                        capture(product, str(response.url), "magento_api")

                    remaining = max_products - len(all_products) if max_products is not None else len(products)
                    all_products.extend(products[:remaining])

                    if len(all_products) >= total_count:
                        break

                    if max_products is not None and len(all_products) >= max_products:
                        return ExtractorResult(products=all_products, complete=False,
                                               completeness_reason='product_budget_reached')
                    current_page += 1

                except httpx.TimeoutException:
                    complete = False
                    error = f"Timeout on page {current_page}"
                    break
                except httpx.RequestError as e:
                    complete = False
                    error = f"Request error on page {current_page}: {e}"
                    break
                except Exception as e:
                    complete = False
                    error = f"Unexpected error on page {current_page}: {e}"
                    break

        if complete and total_count > len(all_products):
            complete = False

        pages_expected = math.ceil(total_count / self.page_size) if total_count else None

        logger.info("Extraction complete: %d total products from %d pages", len(all_products), current_page)
        return ExtractorResult(
            products=all_products,
            complete=complete,
            error=error,
            pages_completed=current_page - 1 if current_page > 1 else (1 if all_products else 0),
            pages_expected=pages_expected,
            completeness_reason='page_budget_reached' if not complete and not error else None,
        )
