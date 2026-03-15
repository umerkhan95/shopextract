"""Shopify API product extractor using /products.json endpoint."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from .._models import ExtractorResult
from ._browser import DEFAULT_HEADERS, get_default_user_agent

logger = logging.getLogger(__name__)


class ShopifyExtractor:
    """Extract products from Shopify stores using the public /products.json API."""

    def __init__(self, timeout: int = 30, max_pages: int = 100):
        self.timeout = timeout
        self.max_pages = max_pages

    async def extract(self, shop_url: str) -> ExtractorResult:
        """Fetch all products from /products.json with pagination."""
        all_products: list[dict[str, Any]] = []
        base_url = shop_url.rstrip("/")
        shop_currency: str | None = None
        complete = True
        error: str | None = None

        headers = {
            **DEFAULT_HEADERS,
            "User-Agent": get_default_user_agent(),
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers=headers) as client:
            page = 1

            while page <= self.max_pages:
                url = f"{base_url}/products.json?limit=250&page={page}"
                logger.info("Fetching page %s from %s", page, url)

                try:
                    response = await client.get(url)

                    if response.status_code == 429:
                        retry_after = int(response.headers.get("Retry-After", "2"))
                        await asyncio.sleep(retry_after)
                        response = await client.get(url)
                        if response.status_code == 429:
                            complete = False
                            error = f"Rate limited on page {page}"
                            break

                    if response.status_code == 404:
                        if not all_products:
                            complete = False
                            error = "404 Not Found"
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
                        data = response.json()
                    except Exception as e:
                        complete = False
                        error = f"Invalid JSON on page {page}: {e}"
                        break

                    if shop_currency is None:
                        shop_currency = response.cookies.get("cart_currency")

                    products = data.get("products", [])
                    if not products:
                        break

                    all_products.extend(products)
                    if len(products) < 250:
                        break

                    page += 1

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

        if shop_currency:
            for product in all_products:
                product["_shop_currency"] = shop_currency

        logger.info("Extraction complete: %s total products from %s pages", len(all_products), page - 1)
        return ExtractorResult(
            products=all_products,
            complete=complete,
            error=error,
            pages_completed=page - 1 if page > 1 else (1 if all_products else 0),
        )
