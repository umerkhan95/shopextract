"""Shopify API product extractor using /products.json endpoint."""

from __future__ import annotations

import asyncio
import logging
from typing import Any
from urllib.parse import urlsplit

import httpx

from .._models import ExtractorResult
from ._browser import DEFAULT_HEADERS, get_default_user_agent

logger = logging.getLogger(__name__)


class ShopifyExtractor:
    """Extract products from Shopify stores using the public /products.json API."""

    def __init__(self, timeout: int = 30, max_pages: int = 100):
        self.timeout = timeout
        self.max_pages = max_pages

    async def extract(self, shop_url: str, *, max_products: int | None = None,
                      enrich_identifiers: bool = False) -> ExtractorResult:
        """Fetch bounded products; optionally enrich missing variant barcodes by ID."""
        if max_products is not None and (not isinstance(max_products, int) or isinstance(max_products, bool) or max_products <= 0):
            raise ValueError("max_products must be a positive integer")
        all_products: list[dict[str, Any]] = []
        base_url = shop_url.rstrip("/")
        shop_currency: str | None = None
        complete = True
        completeness_reason: str | None = None
        error: str | None = None
        pages_completed = 0

        headers = {
            **DEFAULT_HEADERS,
            "User-Agent": get_default_user_agent(),
            "Accept": "application/json",
        }

        async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True, headers=headers) as client:
            page = 1

            while page <= self.max_pages:
                limit = min(250, max_products) if max_products is not None else 250
                url = f"{base_url}/products.json?limit={limit}&page={page}"
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
                        complete = False
                        error = f"404 Not Found on page {page}"
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
                        if not isinstance(data, dict) or not isinstance(data.get("products"), list) or not all(isinstance(p, dict) for p in data["products"]):
                            raise ValueError("Expected a products list of objects")
                    except Exception as e:
                        complete = False
                        error = f"Invalid JSON on page {page}: {e}"
                        break

                    pages_completed += 1
                    if shop_currency is None:
                        shop_currency = response.cookies.get("cart_currency")

                    products = data.get("products", [])
                    if not products:
                        break

                    remaining = max_products - len(all_products) if max_products is not None else len(products)
                    all_products.extend(products[:remaining])
                    if max_products is not None and len(all_products) >= max_products:
                        # A short final page proves exhaustion only if no records
                        # were discarded. An exactly full page cannot prove it.
                        complete = len(products) < limit and len(products) <= remaining
                        if not complete:
                            completeness_reason = "product_budget_reached"
                        break
                    if len(products) < limit:
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

            else:
                complete = False
                completeness_reason = "page_budget_reached"

            if enrich_identifiers:
                origin = urlsplit(base_url)
                origin_url = f"{origin.scheme}://{origin.netloc}"
                for product in all_products:
                    variants = product.get("variants") or []
                    if not product.get("handle") or not any(not v.get("barcode") for v in variants):
                        continue
                    try:
                        detail = await client.get(f"{origin_url}/products/{product['handle']}.js")
                        detail.raise_for_status()
                        data = detail.json()
                        if data.get("id") is None or product.get("id") is None or str(data["id"]) != str(product["id"]):
                            product.setdefault("_identifier_enrichment_errors", []).append("Product ID mismatch in identifier detail response")
                            continue
                        by_id = {str(v.get("id")): v for v in data.get("variants", []) if v.get("id") is not None}
                        for variant in variants:
                            source = by_id.get(str(variant.get("id")), {})
                            if not variant.get("barcode") and source.get("barcode"):
                                variant["barcode"] = source["barcode"]
                                product.setdefault("_identifier_sources", []).append({
                                    "url": str(detail.url), "variant_id": str(variant.get("id")),
                                    "field": "barcode", "value": source["barcode"],
                                })
                    except (httpx.HTTPError, ValueError, TypeError, AttributeError) as exc:
                        logger.warning("Identifier enrichment failed for %s: %s", product.get("handle"), exc)
                        product.setdefault("_identifier_enrichment_errors", []).append(str(exc))
        if shop_currency:
            for product in all_products:
                product["_shop_currency"] = shop_currency

        logger.info("Extraction complete: %s total products from %s pages", len(all_products), pages_completed)
        return ExtractorResult(
            products=all_products,
            complete=complete,
            error=error,
            pages_completed=pages_completed,
            completeness_reason=completeness_reason or ("source_error" if error else None),
        )
