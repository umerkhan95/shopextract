"""Product data quality scoring. Stateless, no side effects."""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

# Fields that make a product minimally useful
_TITLE_FIELDS = ("title", "name", "og:title")
_PRICE_FIELDS = ("price", "og:price:amount", "offers")
_IMAGE_FIELDS = ("image_url", "image", "og:image", "images")
_DESC_FIELDS = ("description", "body_html", "og:description", "short_description")
_SKU_FIELDS = ("sku", "external_id", "id")


class QualityScorer:
    """Score product data quality on a 0.0-1.0 scale.

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
        if self._has_any_field(product, _PRICE_FIELDS):
            score += 0.15
        if self._has_any_field(product, _IMAGE_FIELDS):
            score += 0.15
        if self._has_any_field(product, _DESC_FIELDS):
            score += 0.15
        if self._has_any_field(product, _SKU_FIELDS):
            score += 0.15

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
