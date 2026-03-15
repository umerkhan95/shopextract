"""Tests for catalog analysis and competitive intelligence."""

from __future__ import annotations

import pytest

from shopextract.analyze.stats import (
    analyze_products,
    brand_breakdown,
    count_categories,
    count_field,
    get_price,
    outliers,
    price_distribution,
)
from shopextract.analyze.competitive import (
    _build_price_position,
    brand_coverage,
)
from shopextract._models import CatalogStats


class TestGetPrice:
    def test_string_price(self):
        assert get_price({"price": "19.99"}) == 19.99

    def test_float_price(self):
        assert get_price({"price": 29.99}) == 29.99

    def test_int_price(self):
        assert get_price({"price": 10}) == 10.0

    def test_zero_returns_none(self):
        assert get_price({"price": 0}) is None

    def test_negative_returns_none(self):
        assert get_price({"price": -5}) is None

    def test_missing_returns_none(self):
        assert get_price({}) is None

    def test_none_value_returns_none(self):
        assert get_price({"price": None}) is None

    def test_invalid_string_returns_none(self):
        assert get_price({"price": "free"}) is None


class TestAnalyzeProducts:
    def test_empty_list(self):
        stats = analyze_products([])
        assert stats.total_products == 0
        assert stats.avg_price == 0.0
        assert stats.completeness_score == 0.0

    def test_single_product(self):
        products = [{"title": "Widget", "price": "29.99", "image_url": "img.jpg", "vendor": "BrandX"}]
        stats = analyze_products(products)
        assert stats.total_products == 1
        assert stats.avg_price == 29.99
        assert stats.median_price == 29.99
        assert stats.price_range == (29.99, 29.99)
        assert stats.in_stock == 1
        assert stats.has_images == 1

    def test_multiple_products(self, sample_products_dicts):
        stats = analyze_products(sample_products_dicts)
        assert stats.total_products == 4
        assert stats.price_range[0] <= stats.price_range[1]
        assert stats.avg_price > 0
        assert stats.in_stock == 3
        assert stats.out_of_stock == 1
        assert "BrandX" in stats.brands
        assert stats.has_images == 4
        assert stats.has_gtin == 2

    def test_currencies_counted(self, sample_products_dicts):
        stats = analyze_products(sample_products_dicts)
        assert "USD" in stats.currencies
        assert "EUR" in stats.currencies

    def test_categories_counted(self, sample_products_dicts):
        stats = analyze_products(sample_products_dicts)
        assert "Electronics" in stats.categories
        assert "Widgets" in stats.categories

    def test_completeness_score_range(self, sample_products_dicts):
        stats = analyze_products(sample_products_dicts)
        assert 0.0 <= stats.completeness_score <= 1.0


class TestPriceDistribution:
    def test_default_buckets(self, sample_products_dicts):
        dist = price_distribution(sample_products_dicts)
        assert isinstance(dist, dict)
        total = sum(dist.values())
        assert total == 4

    def test_custom_buckets(self):
        products = [{"price": "5"}, {"price": "15"}, {"price": "25"}]
        dist = price_distribution(products, buckets=[0, 10, 20, 30])
        assert dist["0-10"] == 1
        assert dist["10-20"] == 1
        assert dist["20-30"] == 1

    def test_empty_products(self):
        dist = price_distribution([])
        total = sum(dist.values())
        assert total == 0

    def test_last_bucket_is_plus(self):
        products = [{"price": "5000"}]
        dist = price_distribution(products)
        assert "1000+" in dist
        assert dist["1000+"] == 1


class TestOutliers:
    def test_finds_outliers(self):
        products = [
            {"title": "Cheap", "price": "10"},
            {"title": "Normal1", "price": "50"},
            {"title": "Normal2", "price": "55"},
            {"title": "Normal3", "price": "48"},
            {"title": "Normal4", "price": "52"},
            {"title": "Expensive", "price": "500"},
        ]
        result = outliers(products, std_multiplier=2.0)
        titles = [p["title"] for p in result]
        assert "Expensive" in titles

    def test_no_outliers_when_uniform(self):
        products = [{"title": f"P{i}", "price": "50"} for i in range(10)]
        result = outliers(products)
        assert len(result) == 0

    def test_too_few_products(self):
        products = [{"title": "A", "price": "10"}]
        result = outliers(products)
        assert result == []

    def test_empty_products(self):
        assert outliers([]) == []


class TestBrandBreakdown:
    def test_basic(self):
        products = [
            {"vendor": "BrandA"},
            {"vendor": "BrandA"},
            {"vendor": "BrandB"},
        ]
        result = brand_breakdown(products)
        assert result["BrandA"] == pytest.approx(66.67)
        assert result["BrandB"] == pytest.approx(33.33)

    def test_no_vendors(self):
        products = [{"title": "A"}, {"title": "B"}]
        assert brand_breakdown(products) == {}

    def test_empty_list(self):
        assert brand_breakdown([]) == {}

    def test_single_brand(self):
        products = [{"vendor": "Only"} for _ in range(5)]
        result = brand_breakdown(products)
        assert result["Only"] == 100.0


class TestCountField:
    def test_counts_values(self):
        products = [{"currency": "USD"}, {"currency": "EUR"}, {"currency": "USD"}]
        result = count_field(products, "currency")
        assert result["USD"] == 2
        assert result["EUR"] == 1

    def test_skips_none_and_empty(self):
        products = [{"currency": None}, {"currency": ""}, {"currency": "USD"}]
        result = count_field(products, "currency")
        assert len(result) == 1


class TestCountCategories:
    def test_from_category_path(self):
        products = [
            {"category_path": ["Electronics", "Phones"]},
            {"category_path": ["Electronics", "Laptops"]},
        ]
        result = count_categories(products)
        assert result["Electronics"] == 2

    def test_from_product_type(self):
        products = [{"product_type": "Coffee"}]
        result = count_categories(products)
        assert result["Coffee"] == 1


class TestBuildPricePosition:
    def test_no_competitors(self):
        pos = _build_price_position("Widget", 29.99, {})
        assert pos.rank == 1
        assert pos.total_competitors == 0
        assert pos.percentile == 100.0

    def test_cheapest(self):
        pos = _build_price_position("Widget", 10.0, {"store1": 20.0, "store2": 30.0})
        assert pos.rank == 1
        assert pos.cheapest == 10.0
        assert pos.most_expensive == 30.0
        assert pos.total_competitors == 2

    def test_most_expensive(self):
        pos = _build_price_position("Widget", 50.0, {"store1": 20.0, "store2": 30.0})
        assert pos.rank == 3
        assert pos.cheapest == 20.0

    def test_middle(self):
        pos = _build_price_position("Widget", 25.0, {"store1": 20.0, "store2": 30.0})
        assert pos.rank == 2


class TestBrandCoverage:
    def test_basic(self):
        catalogs = {
            "store1": [{"vendor": "BrandA"}, {"vendor": "BrandB"}],
            "store2": [{"vendor": "BrandA"}, {"vendor": "BrandC"}],
        }
        result = brand_coverage(catalogs)
        assert result["BrandA"] == {"store1": 1, "store2": 1}
        assert result["BrandB"] == {"store1": 1, "store2": 0}
        assert result["BrandC"] == {"store1": 0, "store2": 1}

    def test_empty_catalogs(self):
        result = brand_coverage({})
        assert result == {}

    def test_no_vendors(self):
        catalogs = {"store1": [{"title": "A"}]}
        result = brand_coverage(catalogs)
        assert result == {}
