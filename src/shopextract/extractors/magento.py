"""Magento 2 REST API product extractor."""

from __future__ import annotations

import logging
import math
from typing import Any

import httpx

from .._models import ExtractorResult
from ._browser import DEFAULT_HEADERS, get_default_user_agent

logger = logging.getLogger(__name__)


class MagentoExtractor:
    """Extract products from Magento 2 stores using the public REST API."""

    def __init__(self, timeout: int = 30, page_size: int = 100, max_pages: int = 100):
        self.timeout = timeout
        self.page_size = page_size
        self.max_pages = max_pages

    async def extract(self, shop_url: str) -> ExtractorResult:
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

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers=headers) as client:
            while current_page <= self.max_pages:
                url = (
                    f"{base_url}/rest/V1/products?"
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

                    all_products.extend(products)

                    if len(all_products) >= total_count:
                        break

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

        pages_expected = math.ceil(total_count / self.page_size) if total_count else None

        logger.info("Extraction complete: %d total products from %d pages", len(all_products), current_page)
        return ExtractorResult(
            products=all_products,
            complete=complete,
            error=error,
            pages_completed=current_page - 1 if current_page > 1 else (1 if all_products else 0),
            pages_expected=pages_expected,
        )
