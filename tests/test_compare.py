"""Tests for comparison, catalog diff, and matching."""

from __future__ import annotations

from decimal import Decimal

import pytest

from shopextract._models import CatalogDiff, ComparisonResult, Match, Product, Platform
from shopextract.compare.match import fuzzy_match, match_gtin, title_similarity
from shopextract.compare.catalog import _diff_catalogs
from shopextract.compare.price import _collect_matches, _build_result


class TestTitleSimilarity:
    def test_identical(self):
        assert title_similarity("Widget A", "Widget A") == 1.0

    def test_case_insensitive(self):
        assert title_similarity("Widget A", "widget a") == 1.0

    def test_similar(self):
        sim = title_similarity("Blue Widget Pro", "Blue Widget Pro Max")
        assert sim > 0.7

    def test_completely_different(self):
        sim = title_similarity("Widget", "Banana")
        assert sim < 0.5


class TestFuzzyMatch:
    def test_exact_matches(self):
        products_a = [{"title": "Widget A"}, {"title": "Widget B"}]
        products_b = [{"title": "Widget B"}, {"title": "Widget A"}]
        matches = fuzzy_match(products_a, products_b)
        assert len(matches) == 2
        for prod_a, prod_b, sim in matches:
            assert sim >= 0.8

    def test_partial_matches(self):
        products_a = [{"title": "Widget A"}, {"title": "Unique Product"}]
        products_b = [{"title": "Widget A - Large"}, {"title": "Something Else"}]
        matches = fuzzy_match(products_a, products_b, threshold=0.6)
        assert len(matches) >= 1
        assert matches[0][0]["title"] == "Widget A"

    def test_no_matches(self):
        products_a = [{"title": "Apple"}]
        products_b = [{"title": "Banana"}]
        matches = fuzzy_match(products_a, products_b, threshold=0.8)
        assert len(matches) == 0

    def test_empty_lists(self):
        assert fuzzy_match([], []) == []
        assert fuzzy_match([{"title": "A"}], []) == []

    def test_no_reuse_of_b(self):
        """Each product_b should only be matched once."""
        products_a = [{"title": "Widget"}, {"title": "Widget"}]
        products_b = [{"title": "Widget"}]
        matches = fuzzy_match(products_a, products_b, threshold=0.8)
        assert len(matches) == 1

    def test_custom_threshold(self):
        products_a = [{"title": "Blue Widget Pro"}]
        products_b = [{"title": "Blue Widget Pro Max"}]
        high = fuzzy_match(products_a, products_b, threshold=0.99)
        low = fuzzy_match(products_a, products_b, threshold=0.5)
        assert len(low) >= len(high)


class TestMatchGtin:
    def test_exact_gtin_match(self):
        products = [
            {"title": "A", "gtin": "4006381333931"},
            {"title": "B", "gtin": "5901234123457"},
            {"title": "C"},
        ]
        result = match_gtin("4006381333931", products)
        assert len(result) == 1
        assert result[0]["title"] == "A"

    def test_sku_match(self):
        products = [{"title": "A", "sku": "SKU-123"}]
        result = match_gtin("SKU-123", products)
        assert len(result) == 1

    def test_ean_match(self):
        products = [{"title": "A", "ean": "4006381333931"}]
        result = match_gtin("4006381333931", products)
        assert len(result) == 1

    def test_upc_match(self):
        products = [{"title": "A", "upc": "012345678905"}]
        result = match_gtin("012345678905", products)
        assert len(result) == 1

    def test_no_match(self):
        products = [{"title": "A", "gtin": "1111111111111"}]
        result = match_gtin("9999999999999", products)
        assert len(result) == 0

    def test_empty_products(self):
        assert match_gtin("123", []) == []

    def test_whitespace_handling(self):
        products = [{"title": "A", "gtin": "4006381333931"}]
        result = match_gtin(" 4006381333931 ", products)
        assert len(result) == 1


class TestDiffCatalogs:
    def _make_product(self, title: str, price: float) -> Product:
        return Product(
            title=title,
            price=Decimal(str(price)),
            external_id=title.lower().replace(" ", "-"),
            platform=Platform.GENERIC,
        )

    def test_identical_catalogs(self):
        products = [self._make_product("Widget", 10.0)]
        diff = _diff_catalogs("A", "B", products, products, 0.8)
        assert len(diff.in_both) == 1
        assert len(diff.only_in_a) == 0
        assert len(diff.only_in_b) == 0

    def test_disjoint_catalogs(self):
        a = [self._make_product("Widget A", 10.0)]
        b = [self._make_product("Widget B", 20.0)]
        diff = _diff_catalogs("A", "B", a, b, 0.9)
        assert len(diff.only_in_a) == 1
        assert len(diff.only_in_b) == 1
        assert len(diff.in_both) == 0

    def test_price_classification(self):
        a = [self._make_product("Widget", 10.0)]
        b = [self._make_product("Widget", 20.0)]
        diff = _diff_catalogs("A", "B", a, b, 0.8)
        assert len(diff.cheaper_in_a) == 1
        assert len(diff.cheaper_in_b) == 0

    def test_mixed_catalog(self):
        a = [
            self._make_product("Widget A", 10.0),
            self._make_product("Banana Split Sundae", 15.0),
        ]
        b = [
            self._make_product("Widget A", 12.0),
            self._make_product("Titanium Drill Press", 25.0),
        ]
        diff = _diff_catalogs("StoreA", "StoreB", a, b, 0.8)
        assert diff.store_a == "StoreA"
        assert diff.store_b == "StoreB"
        assert len(diff.in_both) == 1
        assert len(diff.only_in_a) == 1
        assert len(diff.only_in_b) == 1
        assert len(diff.cheaper_in_a) == 1


class TestBuildResult:
    def test_empty_matches(self):
        result = _build_result("query", [])
        assert result.query == "query"
        assert result.cheapest is None
        assert result.most_expensive is None

    def test_sorted_by_price(self):
        matches = [
            Match(title="B", price=Decimal("30"), currency="USD", store="s1", product_url="u1"),
            Match(title="A", price=Decimal("10"), currency="USD", store="s2", product_url="u2"),
            Match(title="C", price=Decimal("20"), currency="USD", store="s3", product_url="u3"),
        ]
        result = _build_result("widget", matches)
        assert result.cheapest.price == Decimal("10")
        assert result.most_expensive.price == Decimal("30")
        assert result.price_spread == Decimal("20")
        assert float(result.avg_price) == pytest.approx(20.0)
