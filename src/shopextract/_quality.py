"""Product data quality scoring. Stateless, no side effects."""

from __future__ import annotations

import logging
from decimal import Decimal, InvalidOperation

from ._shopify_price import has_explicit_request_price_marker

logger = logging.getLogger(__name__)

# Fields that make a product minimally useful
_TITLE_FIELDS = ("title", "name", "og:title")
_PRICE_FIELDS = ("price", "og:price:amount", "offers", "prices", "price_range", "calculatedPrice")
_IMAGE_FIELDS = ("image_url", "image", "og:image", "images", "defaultImage", "cover")
_DESC_FIELDS = ("description", "body_html", "og:description", "short_description")
_SKU_FIELDS = ("sku", "external_id", "id")


class QualityScorer:
    """Score field presence on a 0.0-1.0 scale; not eligibility or factual support.

    Standalone component -- takes raw product dicts, returns numeric scores.
    """

    def score_product(self, product: dict) -> float:
        """Score a single product dict.

        Scoring:
            - 0.0 if no title/name found
            - 0.4 base for having a title
            - +0.15 each for: price, image, description, sku (max +0.60)

        Returns:
            Quality score 0.0-1.0
        """
        if not self._has_any_field(product, _TITLE_FIELDS):
            return 0.0

        score = 0.4
        if self._has_any_field(product, _PRICE_FIELDS) or (
                self._is_shopify_record(product) and self._has_shopify_price(product)):
            score += 0.15
        if self._has_any_field(product, _IMAGE_FIELDS):
            score += 0.15
        if self._has_any_field(product, _DESC_FIELDS):
            score += 0.15
        if self._has_any_field(product, _SKU_FIELDS):
            score += 0.15

        if self._is_shopify_record(product):
            if not self._has_shopify_currency(product):
                score -= 0.05
            if not self._has_shopify_stock(product):
                score -= 0.05
        return min(score, 1.0)

    def score_batch(self, products: list[dict]) -> float:
        """Score a batch of products. Returns average quality 0.0-1.0."""
        if not products:
            return 0.0

        scores = [self.score_product(p) for p in products]
        avg = sum(scores) / len(scores)
        logger.debug(
            "Batch quality: %.2f avg across %d products (min=%.2f, max=%.2f)",
            avg, len(scores), min(scores), max(scores),
        )
        return avg

    @staticmethod
    def _has_any_field(product: dict, field_names: tuple[str, ...]) -> bool:
        """Check if product has any of the given fields with a non-empty value."""
        for name in field_names:
            val = product.get(name)
            if val is None:
                continue
            if isinstance(val, (int, float)):
                if val != 0:
                    return True
                continue
            if isinstance(val, list):
                if val:
                    return True
                continue
            if isinstance(val, dict):
                if val:
                    return True
                continue
            if str(val).strip():
                return True
        return False

    @staticmethod
    def _is_shopify_record(product: dict) -> bool:
        return isinstance(product.get("handle"), str) and isinstance(product.get("variants"), list)

    @staticmethod
    def _numeric_price(values) -> bool:
        for value in values:
            try:
                amount = Decimal(str(value))
                if amount.is_finite() and amount >= 0:
                    return True
            except (InvalidOperation, ValueError, TypeError):
                continue
        return False

    @classmethod
    def _has_shopify_price(cls, product: dict) -> bool:
        if has_explicit_request_price_marker(product):
            return False
        variants = product.get("variants") or []
        values = [variant.get("price") for variant in variants if isinstance(variant, dict)]
        return cls._numeric_price(values)

    @staticmethod
    def _has_shopify_currency(product: dict) -> bool:
        from ._currencies import is_pricing_currency

        values = [product.get("currency"), product.get("_shop_currency")]
        values.extend(variant.get("price_currency") for variant in product.get("variants", [])
                      if isinstance(variant, dict))
        present = [value.strip().upper() for value in values
                   if isinstance(value, str) and value.strip()]
        return bool(present) and all(is_pricing_currency(value) for value in present) and len(set(present)) == 1

    @staticmethod
    def _has_shopify_stock(product: dict) -> bool:
        if isinstance(product.get("available"), bool):
            return True
        variants = product.get("variants") or []
        return bool(variants) and all(
            isinstance(variant, dict) and (
                isinstance(variant.get("available"), bool)
                or isinstance(variant.get("inventory_quantity"), (int, float))
            ) for variant in variants)
