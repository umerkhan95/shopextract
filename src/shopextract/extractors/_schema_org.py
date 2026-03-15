"""Schema.org JSON-LD structured data extractor (static methods only)."""

from __future__ import annotations

import json
import logging

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

# Fields that may contain PII
_SCHEMA_ORG_PII_FIELDS = frozenset({
    "review", "reviews", "author", "aggregateRating",
    "creator", "contributor", "editor", "publisher",
    "reviewedBy", "commentCount", "comment",
    "interactionStatistic",
})


class SchemaOrgExtractor:
    """Extract JSON-LD structured data from <script type='application/ld+json'> tags."""

    @staticmethod
    def _is_product_type(type_value) -> bool:
        if isinstance(type_value, str):
            return "Product" in type_value
        if isinstance(type_value, list):
            return any("Product" in str(t) for t in type_value)
        return False

    @staticmethod
    def _strip_pii_fields(product: dict) -> dict:
        return {k: v for k, v in product.items() if k not in _SCHEMA_ORG_PII_FIELDS}

    @staticmethod
    def _has_nonzero_price(offers) -> bool:
        if isinstance(offers, dict):
            try:
                return float(offers.get("price", 0)) > 0
            except (ValueError, TypeError):
                return bool(offers.get("price"))
        if isinstance(offers, list):
            for offer in offers:
                if isinstance(offer, dict):
                    try:
                        if float(offer.get("price", 0)) > 0:
                            return True
                    except (ValueError, TypeError):
                        if offer.get("price"):
                            return True
        return False

    @staticmethod
    def _enrich_product_group(product: dict) -> None:
        """Pull first variant's non-zero offers into a ProductGroup with no direct price."""
        offers = product.get("offers")
        if SchemaOrgExtractor._has_nonzero_price(offers):
            return

        variants = product.get("hasVariant", [])
        if not isinstance(variants, list) or not variants:
            return

        for variant in variants:
            if not isinstance(variant, dict):
                continue
            v_offers = variant.get("offers")
            if isinstance(v_offers, dict):
                try:
                    if float(v_offers.get("price", 0)) > 0:
                        product["offers"] = v_offers
                        return
                except (ValueError, TypeError):
                    if v_offers.get("price"):
                        product["offers"] = v_offers
                        return
            if isinstance(v_offers, list):
                for offer in v_offers:
                    if not isinstance(offer, dict):
                        continue
                    try:
                        if float(offer.get("price", 0)) > 0:
                            product["offers"] = [offer]
                            return
                    except (ValueError, TypeError):
                        if offer.get("price"):
                            product["offers"] = [offer]
                            return

    @staticmethod
    def _extract_og_meta(soup: BeautifulSoup) -> dict[str, str]:
        og_data: dict[str, str] = {}
        for meta in soup.find_all("meta", attrs={"property": True}):
            prop = meta.get("property", "")
            content = meta.get("content", "")
            if prop.startswith("og:") and content:
                og_data[prop] = content.strip()
        return og_data

    @staticmethod
    def extract_from_html(html: str, url: str) -> list[dict]:
        """Extract JSON-LD Product data from raw HTML content.

        Args:
            html: Raw HTML content.
            url: URL for logging purposes.

        Returns:
            List of raw Product JSON-LD dicts. Empty list if no Product found.
        """
        try:
            soup = BeautifulSoup(html, "html.parser")
            script_tags = soup.find_all("script", type="application/ld+json")

            if not script_tags:
                return []

            products = []

            for script in script_tags:
                try:
                    data = json.loads(script.string)

                    if isinstance(data, dict):
                        if SchemaOrgExtractor._is_product_type(data.get("@type")):
                            products.append(data)
                        elif "@graph" in data and isinstance(data["@graph"], list):
                            for item in data["@graph"]:
                                if not isinstance(item, dict):
                                    continue
                                if SchemaOrgExtractor._is_product_type(item.get("@type")):
                                    products.append(item)
                                else:
                                    item_type = item.get("@type", "")
                                    page_types = ("WebPage", "ItemPage", "CollectionPage")
                                    is_page_type = (
                                        isinstance(item_type, str) and any(pt in item_type for pt in page_types)
                                    ) or (
                                        isinstance(item_type, list) and any(
                                            any(pt in str(t) for pt in page_types) for t in item_type
                                        )
                                    )
                                    if is_page_type:
                                        for key in ("mainEntity", "mainEntityOfPage"):
                                            nested = item.get(key)
                                            if isinstance(nested, dict) and SchemaOrgExtractor._is_product_type(nested.get("@type")):
                                                products.append(nested)
                                            elif isinstance(nested, list):
                                                for sub in nested:
                                                    if isinstance(sub, dict) and SchemaOrgExtractor._is_product_type(sub.get("@type")):
                                                        products.append(sub)

                    elif isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and SchemaOrgExtractor._is_product_type(item.get("@type")):
                                products.append(item)

                except json.JSONDecodeError:
                    continue
                except Exception as e:
                    logger.debug("Error processing JSON-LD block for %s: %s", url, e)
                    continue

            if not products:
                return products

            for product in products:
                if product.get("@type") == "ProductGroup":
                    SchemaOrgExtractor._enrich_product_group(product)

            products = [SchemaOrgExtractor._strip_pii_fields(p) for p in products]

            og_data = SchemaOrgExtractor._extract_og_meta(soup)
            if og_data:
                for product in products:
                    if not product.get("image") and og_data.get("og:image"):
                        product["image"] = og_data["og:image"]
                    if not product.get("url") and og_data.get("og:url"):
                        product["url"] = og_data["og:url"]
                    if not product.get("description") and og_data.get("og:description"):
                        product["description"] = og_data["og:description"]

            return products

        except Exception as e:
            logger.exception("Schema.org extraction failed for %s: %s", url, e)
            return []
