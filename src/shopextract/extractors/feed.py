"""Google Shopping Feed extractor -- parses XML (RSS 2.0) or CSV/TSV product feeds.

Fetches a merchant's Google Shopping feed URL and parses it into raw product dicts.
No browser, no credentials, no crawling -- just one HTTP GET of a static file.
"""

from __future__ import annotations

import csv
import io
import logging
from typing import Any

import defusedxml.ElementTree as ET
import httpx

from .._models import ExtractorResult

logger = logging.getLogger(__name__)

# Google Shopping XML namespace
_G_NS = "http://base.google.com/ns/1.0"
_NAMESPACES = {"g": _G_NS}

_MAX_RESPONSE_SIZE = 10 * 1024 * 1024

_FEED_HEADERS = {
    "User-Agent": "ShopExtract/1.0 (Feed Parser)",
    "Accept": "application/xml, text/xml, text/csv, text/tab-separated-values, */*",
}


class GoogleFeedExtractor:
    """Extract product data from a Google Shopping feed URL (XML or CSV/TSV)."""

    async def extract(self, feed_url: str) -> ExtractorResult:
        """Fetch and parse a Google Shopping feed.

        Args:
            feed_url: The feed URL.

        Returns:
            ExtractorResult with parsed product dicts.
        """
        try:
            body, content_type = await self._fetch_feed(feed_url)
        except Exception as e:
            logger.warning("Failed to fetch feed %s: %s", feed_url, e)
            return ExtractorResult(products=[], complete=False, error=str(e))

        try:
            if self._is_xml(body, content_type):
                products = self._parse_xml(body, feed_url)
            else:
                products = self._parse_csv(body, feed_url)
        except Exception as e:
            logger.warning("Failed to parse feed %s: %s", feed_url, e)
            return ExtractorResult(products=[], complete=False, error=str(e))

        logger.info("Parsed %d products from feed %s", len(products), feed_url)
        return ExtractorResult(products=products, complete=True)

    async def _fetch_feed(self, url: str) -> tuple[str, str]:
        async with httpx.AsyncClient(
            timeout=60, follow_redirects=True, headers=_FEED_HEADERS
        ) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            if len(resp.content) > _MAX_RESPONSE_SIZE:
                raise ValueError(f"Feed exceeds {_MAX_RESPONSE_SIZE // (1024*1024)}MB size limit")
            content_type = resp.headers.get("content-type", "")
            return resp.text, content_type

    @staticmethod
    def _is_xml(body: str, content_type: str) -> bool:
        ct = content_type.lower()
        if "xml" in ct:
            return True
        if "csv" in ct or "tab-separated" in ct:
            return False
        stripped = body.lstrip()
        return stripped.startswith("<?xml") or stripped.startswith("<rss") or stripped.startswith("<feed")

    @classmethod
    def _parse_xml(cls, body: str, feed_url: str) -> list[dict]:
        root = ET.fromstring(body)
        products: list[dict] = []

        items = root.findall(".//item")
        if not items:
            items = root.findall(".//{http://www.w3.org/2005/Atom}entry")

        for item in items:
            product = cls._parse_xml_item(item)
            if product and product.get("title"):
                products.append(product)

        return products

    @classmethod
    def _parse_xml_item(cls, item: Any) -> dict:
        def g(tag: str) -> str:
            el = item.find(f"g:{tag}", _NAMESPACES)
            if el is not None and el.text:
                return el.text.strip()
            el = item.find(tag)
            if el is not None and el.text:
                return el.text.strip()
            return ""

        price_str, currency = cls._parse_price_string(g("price"))
        sale_price_str, sale_currency = cls._parse_price_string(g("sale_price"))

        additional_images = []
        for el in item.findall("g:additional_image_link", _NAMESPACES):
            if el is not None and el.text and el.text.strip():
                additional_images.append(el.text.strip())

        return {
            "_source": "google_feed",
            "id": g("id"),
            "title": g("title") or (item.findtext("title") or "").strip(),
            "description": (item.findtext("description") or "").strip(),
            "link": (item.findtext("link") or "").strip(),
            "price": price_str,
            "currency": currency or sale_currency,
            "sale_price": sale_price_str,
            "gtin": g("gtin") or g("ean"),
            "brand": g("brand"),
            "image_link": g("image_link"),
            "additional_image_link": additional_images,
            "availability": g("availability"),
            "condition": g("condition"),
            "product_type": g("product_type"),
            "mpn": g("mpn"),
        }

    @classmethod
    def _parse_csv(cls, body: str, feed_url: str) -> list[dict]:
        first_line = body.split("\n", 1)[0]
        delimiter = "\t" if "\t" in first_line else ","

        reader = csv.DictReader(io.StringIO(body), delimiter=delimiter)
        products: list[dict] = []

        for row in reader:
            product = cls._parse_csv_row(row)
            if product and product.get("title"):
                products.append(product)

        return products

    @classmethod
    def _parse_csv_row(cls, row: dict[str, str]) -> dict:
        def s(key: str) -> str:
            val = row.get(key)
            return val.strip() if val else ""

        price_str, currency = cls._parse_price_string(s("price"))
        sale_price_str, sale_currency = cls._parse_price_string(s("sale_price"))

        additional_raw = s("additional_image_link")
        additional_images = [
            url.strip() for url in additional_raw.split(",") if url.strip()
        ] if additional_raw else []

        return {
            "_source": "google_feed",
            "id": s("id"),
            "title": s("title"),
            "description": s("description"),
            "link": s("link"),
            "price": price_str,
            "currency": currency or sale_currency,
            "sale_price": sale_price_str,
            "gtin": s("gtin") or s("ean"),
            "brand": s("brand"),
            "image_link": s("image_link"),
            "additional_image_link": additional_images,
            "availability": s("availability"),
            "condition": s("condition"),
            "product_type": s("product_type"),
            "mpn": s("mpn"),
        }

    @staticmethod
    def _parse_price_string(price_raw: str) -> tuple[str, str]:
        if not price_raw or not price_raw.strip():
            return "", ""

        parts = price_raw.strip().split()
        currency = ""
        amount_str = parts[0]

        if len(parts) >= 2:
            candidate = parts[-1].upper()
            if candidate.isalpha() and len(candidate) == 3:
                currency = candidate
                amount_str = " ".join(parts[:-1])

        if "," in amount_str and "." in amount_str:
            amount_str = amount_str.replace(",", "")
        elif "," in amount_str:
            amount_str = amount_str.replace(",", ".")

        return amount_str, currency
