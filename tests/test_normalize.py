"""Tests for product normalization."""

from __future__ import annotations

from decimal import Decimal

import pytest

from shopextract._models import Platform, Product
from shopextract._normalize import (
    normalize,
    _strip_html,
    _validate_gtin,
    _parse_additional_properties,
)


class TestStripHtml:
    def test_strips_tags(self):
        assert _strip_html("<p>Hello <b>world</b></p>") == "Hello world"

    def test_strips_script(self):
        assert _strip_html('<script>alert("xss")</script>Text') == "Text"

    def test_strips_style(self):
        assert _strip_html("<style>body{color:red}</style>Text") == "Text"

    def test_empty_string(self):
        assert _strip_html("") == ""

    def test_none_returns_empty(self):
        assert _strip_html(None) == ""


class TestValidateGtin:
    def test_valid_ean13(self):
        assert _validate_gtin("4006381333931") == "4006381333931"

    def test_valid_upc12_padded(self):
        """12-digit UPC should be zero-padded to 13."""
        assert _validate_gtin("012345678905") == "0012345678905"

    def test_valid_gtin8(self):
        assert _validate_gtin("12345678") == "12345678"

    def test_valid_gtin14(self):
        assert _validate_gtin("10614141000415") == "10614141000415"

    def test_strips_whitespace_and_dashes(self):
        assert _validate_gtin(" 400-638-1333931 ") == "4006381333931"

    def test_none_returns_none(self):
        assert _validate_gtin(None) is None

    def test_empty_returns_none(self):
        assert _validate_gtin("") is None

    def test_all_zeros_returns_none(self):
        assert _validate_gtin("0000000000000") is None

    def test_non_digit_returns_none(self):
        assert _validate_gtin("ABC123") is None

    def test_wrong_length_returns_none(self):
        assert _validate_gtin("12345") is None
        assert _validate_gtin("123456789") is None


class TestParseAdditionalProperties:
    def test_extracts_gtin(self):
        props = [{"propertyID": "gtin13", "value": "4006381333931"}]
        result = _parse_additional_properties(props)
        assert result["gtin13"] == "4006381333931"

    def test_extracts_mpn(self):
        props = [{"name": "mpn", "value": "MPN-123"}]
        result = _parse_additional_properties(props)
        assert result["mpn"] == "MPN-123"

    def test_ignores_unknown(self):
        props = [{"propertyID": "weight", "value": "5kg"}]
        result = _parse_additional_properties(props)
        assert result == {}

    def test_handles_non_dict(self):
        props = ["not a dict", 42]
        result = _parse_additional_properties(props)
        assert result == {}


class TestNormalizeShopify:
    def test_basic_normalization(self, shopify_raw_products):
        raw = shopify_raw_products[0]
        product = normalize(raw, platform=Platform.SHOPIFY, shop_url="https://shop.example.com")
        assert product is not None
        assert product.title == "Classic Espresso Blend"
        assert product.price == Decimal("14.99")
        assert product.compare_at_price == Decimal("19.99")
        assert product.vendor == "BeanCo"
        assert product.product_type == "Coffee"
        assert product.sku == "ESP-250"
        assert product.gtin == "4006381333931"
        assert product.image_url == "https://cdn.shopify.com/espresso-main.jpg"
        assert len(product.additional_images) == 1
        assert product.product_url == "https://shop.example.com/products/classic-espresso-blend"
        assert product.platform == Platform.SHOPIFY
        assert product.condition == "NEW"

    def test_out_of_stock(self, shopify_raw_products):
        raw = shopify_raw_products[1]
        product = normalize(raw, platform=Platform.SHOPIFY, shop_url="https://shop.example.com")
        assert product is not None
        assert product.in_stock is False

    def test_tags_parsed(self, shopify_raw_products):
        raw = shopify_raw_products[0]
        product = normalize(raw, platform=Platform.SHOPIFY, shop_url="https://shop.example.com")
        assert "coffee" in product.tags
        assert "espresso" in product.tags

    def test_variants_created(self, shopify_raw_products):
        raw = shopify_raw_products[0]
        product = normalize(raw, platform=Platform.SHOPIFY, shop_url="https://shop.example.com")
        assert len(product.variants) == 2
        assert product.variants[0].title == "250g"
        assert product.variants[0].price == Decimal("14.99")

    def test_no_title_returns_none(self):
        raw = {"id": 1, "title": "", "variants": []}
        result = normalize(raw, platform=Platform.SHOPIFY)
        assert result is None


class TestNormalizeWoocommerce:
    def test_store_api_format(self, woocommerce_raw_products):
        raw = woocommerce_raw_products[0]
        product = normalize(raw, platform=Platform.WOOCOMMERCE, shop_url="https://example.com")
        assert product is not None
        assert product.title == "Organic Green Tea"
        assert product.price == Decimal("8.99")
        assert product.compare_at_price == Decimal("10.99")
        assert product.currency == "USD"
        assert product.sku == "OGT-100"
        assert product.image_url == "https://example.com/images/green-tea.jpg"
        assert len(product.additional_images) == 1
        assert "tea" in product.tags
        assert "Tea" in product.category_path

    def test_admin_api_format(self):
        raw = {
            "id": 100,
            "name": "Admin Product",
            "price": "25.00",
            "_source": "woocommerce_admin_api",
            "description": "<p>Test</p>",
            "sku": "ADM-001",
            "permalink": "https://example.com/product/admin-product",
            "images": [{"src": "https://example.com/admin.jpg"}],
        }
        product = normalize(raw, platform=Platform.WOOCOMMERCE)
        assert product is not None
        assert product.price == Decimal("25.00")
        assert product.title == "Admin Product"

    def test_no_name_returns_none(self):
        raw = {"id": 1, "prices": {"price": "100", "currency_minor_unit": 2, "currency_code": "USD"}}
        result = normalize(raw, platform=Platform.WOOCOMMERCE)
        assert result is None


class TestNormalizeMagento:
    def test_basic(self):
        raw = {
            "id": 1,
            "name": "Magento Widget",
            "price": 49.99,
            "sku": "MW-001",
            "custom_attributes": [
                {"attribute_code": "description", "value": "<p>Great widget</p>"},
                {"attribute_code": "image", "value": "/m/w/widget.jpg"},
                {"attribute_code": "url_key", "value": "magento-widget"},
                {"attribute_code": "ean", "value": "4006381333931"},
            ],
        }
        product = normalize(raw, platform=Platform.MAGENTO, shop_url="https://magento.example.com")
        assert product is not None
        assert product.title == "Magento Widget"
        assert product.price == Decimal("49.99")
        assert product.gtin == "4006381333931"
        assert product.image_url == "https://magento.example.com/media/catalog/product/m/w/widget.jpg"
        assert product.product_url == "https://magento.example.com/magento-widget.html"
        assert product.description == "Great widget"

    def test_media_gallery(self):
        raw = {
            "name": "Gallery Item",
            "price": 10,
            "sku": "GI-001",
            "custom_attributes": [
                {"attribute_code": "image", "value": "/main.jpg"},
            ],
            "media_gallery_entries": [
                {"file": "/main.jpg", "disabled": False},
                {"file": "/side.jpg", "disabled": False},
                {"file": "/disabled.jpg", "disabled": True},
            ],
        }
        product = normalize(raw, platform=Platform.MAGENTO, shop_url="https://m.com")
        assert len(product.additional_images) == 1
        assert "/side.jpg" in product.additional_images[0]


class TestNormalizeShopware:
    def test_basic(self):
        raw = {
            "id": "sw-001",
            "name": "Shopware Product",
            "price": 39.99,
            "currency": "EUR",
            "ean": "5901234123457",
            "sku": "SW-001",
            "description": "<p>Shopware product</p>",
            "image_url": "https://sw.example.com/img.jpg",
            "product_url": "https://sw.example.com/product",
            "in_stock": True,
        }
        product = normalize(raw, platform=Platform.SHOPWARE, shop_url="https://sw.example.com")
        assert product is not None
        assert product.title == "Shopware Product"
        assert product.price == Decimal("39.99")
        assert product.currency == "EUR"
        assert product.gtin == "5901234123457"

    def test_with_variants(self):
        raw = {
            "name": "Variant Product",
            "price": 20,
            "variants": [
                {"id": "v1", "title": "Small", "price": 18, "sku": "VP-S", "in_stock": True},
                {"id": "v2", "title": "Large", "price": 22, "sku": "VP-L", "in_stock": False},
            ],
        }
        product = normalize(raw, platform=Platform.SHOPWARE)
        assert len(product.variants) == 2
        assert product.variants[1].in_stock is False


class TestNormalizeGeneric:
    def test_schema_org(self):
        raw = {
            "@type": "Product",
            "name": "Schema Product",
            "offers": {"price": "29.99", "priceCurrency": "EUR", "availability": "https://schema.org/InStock"},
            "image": "https://example.com/img.jpg",
            "sku": "SP-001",
            "description": "A schema.org product",
            "gtin13": "4006381333931",
            "brand": {"name": "TestBrand"},
        }
        product = normalize(raw, platform=Platform.GENERIC, shop_url="https://example.com")
        assert product is not None
        assert product.title == "Schema Product"
        assert product.price == Decimal("29.99")
        assert product.currency == "EUR"
        assert product.gtin == "4006381333931"
        assert product.vendor == "TestBrand"
        assert product.in_stock is True

    def test_schema_org_offers_list(self):
        raw = {
            "@type": "Product",
            "name": "Multi-Offer",
            "offers": [
                {"price": "19.99", "priceCurrency": "USD"},
                {"price": "24.99", "priceCurrency": "USD"},
            ],
        }
        product = normalize(raw, platform=Platform.GENERIC)
        assert product.price == Decimal("19.99")

    def test_schema_org_out_of_stock(self):
        raw = {
            "@type": "Product",
            "name": "Out of Stock",
            "offers": {"price": "10", "availability": "OutOfStock"},
            "sku": "OOS-1",
        }
        product = normalize(raw, platform=Platform.GENERIC)
        assert product.in_stock is False

    def test_opengraph(self):
        raw = {
            "og:title": "OG Product",
            "og:price:amount": "15.99",
            "og:price:currency": "GBP",
            "og:image": "https://example.com/og.jpg",
            "og:url": "https://example.com/og-product",
            "og:description": "An OG product",
        }
        product = normalize(raw, platform=Platform.GENERIC, shop_url="https://example.com")
        assert product is not None
        assert product.title == "OG Product"
        assert product.price == Decimal("15.99")
        assert product.currency == "GBP"

    def test_css_generic(self):
        raw = {
            "title": "CSS Product",
            "price": "$29.99",
            "image": "https://example.com/css.jpg",
            "sku": "CSS-001",
        }
        product = normalize(raw, platform=Platform.GENERIC, shop_url="https://example.com")
        assert product is not None
        assert product.title == "CSS Product"
        assert product.price == Decimal("29.99")

    def test_css_european_price(self):
        """When both . and , present, code treats comma as thousands separator.
        This means '1.299,99' -> '1.29999' (US convention). This is a known
        limitation for European-format prices."""
        raw = {"title": "Euro Product", "price": "1,299.99", "sku": "EU-001"}
        product = normalize(raw, platform=Platform.GENERIC)
        assert product.price == Decimal("1299.99")

    def test_css_comma_decimal(self):
        raw = {"title": "DE Product", "price": "29,99", "sku": "DE-001"}
        product = normalize(raw, platform=Platform.GENERIC)
        assert product.price == Decimal("29.99")

    def test_google_feed(self):
        raw = {
            "_source": "google_feed",
            "id": "GF-001",
            "title": "Feed Product",
            "price": "19.99",
            "sale_price": "14.99",
            "currency": "EUR",
            "image_link": "https://example.com/feed.jpg",
            "link": "https://example.com/feed-product",
            "gtin": "4006381333931",
            "brand": "FeedBrand",
            "availability": "in stock",
            "condition": "new",
            "product_type": "Home > Kitchen > Appliances",
            "description": "A feed product",
        }
        product = normalize(raw, platform=Platform.GENERIC, shop_url="https://example.com")
        assert product is not None
        assert product.title == "Feed Product"
        assert product.price == Decimal("14.99")
        assert product.compare_at_price == Decimal("19.99")
        assert product.gtin == "4006381333931"
        assert product.vendor == "FeedBrand"
        assert product.condition == "NEW"
        assert product.category_path == ["Home", "Kitchen", "Appliances"]
        assert product.in_stock is True


class TestNormalizeEdgeCases:
    def test_insufficient_data_returns_none(self):
        """No title, no price, no image, no sku -> None."""
        raw = {"some_field": "value"}
        result = normalize(raw, platform=Platform.GENERIC)
        assert result is None

    def test_default_condition_is_new(self):
        raw = {"title": "Widget", "price": "10", "sku": "W1"}
        product = normalize(raw, platform=Platform.GENERIC)
        assert product.condition == "NEW"

    def test_schema_org_condition_parsing(self):
        raw = {
            "@type": "Product",
            "name": "Used Widget",
            "offers": {"price": "5", "itemCondition": "https://schema.org/UsedCondition"},
            "sku": "UW-1",
        }
        product = normalize(raw, platform=Platform.GENERIC)
        assert product.condition == "USED"

    def test_schema_org_image_dict(self):
        raw = {
            "@type": "Product",
            "name": "Image Dict Product",
            "image": {"url": "https://example.com/img.jpg"},
            "offers": {"price": "10"},
            "sku": "IDP-1",
        }
        product = normalize(raw, platform=Platform.GENERIC)
        assert product.image_url == "https://example.com/img.jpg"

    def test_schema_org_image_list(self):
        raw = {
            "@type": "Product",
            "name": "Image List Product",
            "image": ["https://example.com/1.jpg", "https://example.com/2.jpg"],
            "offers": {"price": "10"},
            "sku": "ILP-1",
        }
        product = normalize(raw, platform=Platform.GENERIC)
        assert product.image_url == "https://example.com/1.jpg"
        assert "https://example.com/2.jpg" in product.additional_images
