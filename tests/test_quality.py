"""Tests for quality scoring."""

from __future__ import annotations

import pytest

from shopextract._quality import QualityScorer


class TestQualityScorer:
    def setup_method(self):
        self.scorer = QualityScorer()

    # -- score_product --

    def test_no_title_returns_zero(self):
        assert self.scorer.score_product({}) == 0.0
        assert self.scorer.score_product({"price": "19.99"}) == 0.0

    def test_title_only(self):
        score = self.scorer.score_product({"title": "Widget"})
        assert score == 0.4

    def test_title_via_name_field(self):
        score = self.scorer.score_product({"name": "Widget"})
        assert score == 0.4

    def test_title_via_og_title(self):
        score = self.scorer.score_product({"og:title": "Widget"})
        assert score == 0.4

    def test_title_plus_price(self):
        score = self.scorer.score_product({"title": "Widget", "price": "19.99"})
        assert score == pytest.approx(0.55)

    def test_title_plus_image(self):
        score = self.scorer.score_product({"title": "Widget", "image_url": "https://img.jpg"})
        assert score == pytest.approx(0.55)

    def test_title_plus_description(self):
        score = self.scorer.score_product({"title": "Widget", "description": "A widget"})
        assert score == pytest.approx(0.55)

    def test_title_plus_sku(self):
        score = self.scorer.score_product({"title": "Widget", "sku": "W001"})
        assert score == pytest.approx(0.55)

    def test_full_product_perfect_score(self):
        score = self.scorer.score_product({
            "title": "Widget",
            "price": "19.99",
            "image_url": "https://img.jpg",
            "description": "A great widget",
            "sku": "W001",
        })
        assert score == 1.0

    def test_alternative_field_names(self):
        """Test that alternative field names are recognized."""
        score = self.scorer.score_product({
            "name": "Widget",
            "og:price:amount": "19.99",
            "og:image": "https://img.jpg",
            "body_html": "A great widget",
            "id": "12345",
        })
        assert score == 1.0

    def test_empty_string_fields_ignored(self):
        score = self.scorer.score_product({"title": "Widget", "price": "", "image_url": ""})
        assert score == 0.4

    def test_zero_price_ignored(self):
        score = self.scorer.score_product({"title": "Widget", "price": 0})
        assert score == 0.4

    def test_empty_list_images_ignored(self):
        score = self.scorer.score_product({"title": "Widget", "images": []})
        assert score == 0.4

    def test_nonempty_list_images_counted(self):
        score = self.scorer.score_product({"title": "Widget", "images": [{"src": "a.jpg"}]})
        assert score == pytest.approx(0.55)

    def test_dict_offers_counted(self):
        score = self.scorer.score_product({"title": "Widget", "offers": {"price": "10"}})
        assert score == pytest.approx(0.55)

    def test_empty_dict_offers_ignored(self):
        score = self.scorer.score_product({"title": "Widget", "offers": {}})
        assert score == 0.4

    # -- score_batch --

    def test_batch_empty(self):
        assert self.scorer.score_batch([]) == 0.0

    def test_batch_single(self):
        score = self.scorer.score_batch([{"title": "Widget"}])
        assert score == 0.4

    def test_batch_average(self):
        products = [
            {"title": "A", "price": "10"},  # 0.55
            {"title": "B"},                  # 0.4
        ]
        score = self.scorer.score_batch(products)
        assert score == pytest.approx(0.475)

    def test_batch_all_complete(self):
        products = [
            {"title": "A", "price": "10", "image_url": "a.jpg", "description": "desc", "sku": "S1"},
            {"title": "B", "price": "20", "image_url": "b.jpg", "description": "desc", "sku": "S2"},
        ]
        score = self.scorer.score_batch(products)
        assert score == 1.0
