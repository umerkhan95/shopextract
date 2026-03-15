"""Tests for data models."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal

from shopextract._models import (
    AssortmentGaps,
    CatalogDiff,
    CatalogStats,
    Change,
    ChangeType,
    ComparisonResult,
    ExtractionResult,
    ExtractionTier,
    ExtractorResult,
    ImageIssue,
    Match,
    NewProduct,
    Platform,
    PlatformResult,
    PriceChange,
    PricePosition,
    Product,
    RemovedProduct,
    ValidationIssue,
    ValidationReport,
    Variant,
)


class TestPlatformEnum:
    def test_all_values(self):
        assert Platform.SHOPIFY == "shopify"
        assert Platform.WOOCOMMERCE == "woocommerce"
        assert Platform.MAGENTO == "magento"
        assert Platform.BIGCOMMERCE == "bigcommerce"
        assert Platform.SHOPWARE == "shopware"
        assert Platform.GENERIC == "generic"

    def test_string_comparison(self):
        assert Platform.SHOPIFY == "shopify"
        assert str(Platform.SHOPIFY) == "shopify"


class TestExtractionTierEnum:
    def test_all_values(self):
        assert ExtractionTier.API == "api"
        assert ExtractionTier.UNIFIED_CRAWL == "unified_crawl"
        assert ExtractionTier.GOOGLE_FEED == "google_feed"
        assert ExtractionTier.CSS == "css"
        assert ExtractionTier.LLM == "llm"


class TestVariant:
    def test_defaults(self):
        v = Variant()
        assert v.variant_id == ""
        assert v.title == ""
        assert v.price == Decimal("0")
        assert v.sku is None
        assert v.in_stock is True

    def test_custom_values(self):
        v = Variant(variant_id="V1", title="Large", price=Decimal("29.99"), sku="SKU-L", in_stock=False)
        assert v.variant_id == "V1"
        assert v.price == Decimal("29.99")
        assert v.in_stock is False


class TestProduct:
    def test_defaults(self):
        p = Product()
        assert p.title == ""
        assert p.price == Decimal("0")
        assert p.currency == "USD"
        assert p.variants == []
        assert p.tags == []
        assert p.additional_images == []
        assert p.category_path == []
        assert p.platform == Platform.GENERIC
        assert p.in_stock is True
        assert p.gtin is None
        assert p.compare_at_price is None
        assert isinstance(p.scraped_at, datetime)
        assert isinstance(p.raw_data, dict)

    def test_custom_values(self, complete_product):
        p = complete_product
        assert p.title == "Complete Widget"
        assert p.price == Decimal("49.99")
        assert p.compare_at_price == Decimal("59.99")
        assert p.currency == "EUR"
        assert p.gtin == "4006381333931"
        assert p.vendor == "WidgetCorp"
        assert p.platform == Platform.SHOPIFY
        assert len(p.tags) == 2
        assert len(p.additional_images) == 1

    def test_variant_list_isolation(self):
        """Each Product instance should have its own variant list."""
        p1 = Product()
        p2 = Product()
        p1.variants.append(Variant(variant_id="V1"))
        assert len(p2.variants) == 0


class TestPlatformResult:
    def test_creation(self):
        r = PlatformResult(platform=Platform.SHOPIFY, confidence=0.85, signals=["header:x-shopify"])
        assert r.platform == Platform.SHOPIFY
        assert r.confidence == 0.85
        assert len(r.signals) == 1


class TestExtractorResult:
    def test_empty(self):
        r = ExtractorResult()
        assert r.product_count == 0
        assert r.is_empty is True
        assert r.complete is True

    def test_with_products(self):
        r = ExtractorResult(products=[{"title": "A"}], complete=True)
        assert r.product_count == 1
        assert r.is_empty is False


class TestExtractionResult:
    def test_defaults(self):
        r = ExtractionResult()
        assert r.product_count == 0
        assert r.tier == ExtractionTier.UNIFIED_CRAWL
        assert r.platform == Platform.GENERIC
        assert r.quality_score == 0.0

    def test_with_products(self, minimal_product):
        r = ExtractionResult(products=[minimal_product], tier=ExtractionTier.API, quality_score=0.8)
        assert r.product_count == 1
        assert r.tier == ExtractionTier.API


class TestMatch:
    def test_creation(self):
        m = Match(title="Widget", price=Decimal("9.99"), currency="USD", store="https://example.com", product_url="https://example.com/widget")
        assert m.title == "Widget"
        assert m.similarity == 1.0


class TestComparisonResult:
    def test_empty(self):
        r = ComparisonResult(query="test")
        assert r.query == "test"
        assert r.matches == []
        assert r.cheapest is None


class TestCatalogDiff:
    def test_creation(self):
        d = CatalogDiff(store_a="A", store_b="B")
        assert d.store_a == "A"
        assert d.only_in_a == []
        assert d.in_both == []


class TestChangeModels:
    def test_price_change_post_init(self):
        pc = PriceChange(title="Widget", old_price=Decimal("10"), new_price=Decimal("15"))
        assert pc.change_type == ChangeType.PRICE_CHANGE
        assert pc.old_price == Decimal("10")
        assert pc.new_price == Decimal("15")

    def test_new_product_post_init(self):
        np = NewProduct(title="New Widget", price=Decimal("20"))
        assert np.change_type == ChangeType.NEW_PRODUCT

    def test_removed_product_post_init(self):
        rp = RemovedProduct(title="Old Widget", last_price=Decimal("30"))
        assert rp.change_type == ChangeType.REMOVED_PRODUCT


class TestCatalogStats:
    def test_defaults(self):
        s = CatalogStats()
        assert s.total_products == 0
        assert s.price_range == (0.0, 0.0)
        assert s.completeness_score == 0.0


class TestPricePosition:
    def test_defaults(self):
        pp = PricePosition()
        assert pp.rank == 0
        assert pp.percentile == 0.0


class TestAssortmentGaps:
    def test_defaults(self):
        ag = AssortmentGaps()
        assert ag.missing_categories == []
        assert ag.missing_brands == []


class TestValidationModels:
    def test_issue(self):
        i = ValidationIssue(product_index=0, product_title="Widget", field="gtin", error="Missing")
        assert i.severity == "error"

    def test_report_pass_rate_empty(self):
        r = ValidationReport(marketplace="google_shopping", total=0)
        assert r.pass_rate == 0.0

    def test_report_pass_rate(self):
        r = ValidationReport(marketplace="google_shopping", total=10, valid=8, invalid=2)
        assert r.pass_rate == 80.0

    def test_image_issue(self):
        ii = ImageIssue(product_index=0, product_title="Widget", image_url="https://x.com/img.jpg", error="HTTP 404")
        assert ii.status_code is None
        assert ii.error == "HTTP 404"
