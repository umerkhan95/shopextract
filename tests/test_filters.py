"""Tests for URL filtering."""

from __future__ import annotations

import pytest

from shopextract._filters import (
    PLATFORM_PRODUCT_SITEMAPS,
    NON_PRODUCT_PATHS,
    NON_PRODUCT_SEGMENTS,
    is_non_product_url,
)


class TestIsNonProductUrl:
    """Test is_non_product_url with various URL patterns."""

    # -- Should be filtered (non-product) --

    @pytest.mark.parametrize("url", [
        "https://example.com/",
        "https://example.com/about",
        "https://example.com/about-us",
        "https://example.com/contact",
        "https://example.com/blog",
        "https://example.com/cart",
        "https://example.com/checkout",
        "https://example.com/account",
        "https://example.com/login",
        "https://example.com/search",
        "https://example.com/faq",
        "https://example.com/privacy",
        "https://example.com/privacy-policy",
        "https://example.com/terms",
        "https://example.com/sitemap",
        "https://example.com/wishlist",
        "https://example.com/help",
    ])
    def test_exact_paths_filtered(self, url):
        assert is_non_product_url(url) is True

    @pytest.mark.parametrize("url", [
        "https://example.com/blog/my-post",
        "https://example.com/checkout/step1",
        "https://example.com/account/orders",
        "https://example.com/help/shipping",
        "https://example.com/support/tickets",
        "https://example.com/careers/engineering",
        "https://example.com/wp-admin/dashboard",
        "https://example.com/category/shoes",
        "https://example.com/tag/sale",
    ])
    def test_segment_paths_filtered(self, url):
        assert is_non_product_url(url) is True

    @pytest.mark.parametrize("url", [
        "https://example.com/2024/03/15/blog-post-title",
        "https://example.com/2023/01/01/new-year-sale",
    ])
    def test_date_paths_filtered(self, url):
        assert is_non_product_url(url) is True

    @pytest.mark.parametrize("url", [
        "https://example.com/sitemap.xml",
        "https://example.com/products.json",
        "https://example.com/image.jpg",
        "https://example.com/style.css",
        "https://example.com/script.js",
        "https://example.com/file.pdf",
        "https://example.com/icon.svg",
    ])
    def test_file_extensions_filtered(self, url):
        assert is_non_product_url(url) is True

    # -- Should NOT be filtered (product-like) --

    @pytest.mark.parametrize("url", [
        "https://example.com/products/blue-widget",
        "https://example.com/product/organic-tea",
        "https://example.com/collections/summer-sale",
        "https://example.com/shop/item/123",
        "https://example.com/p/fancy-shoes",
        "https://example.com/items/leather-jacket",
    ])
    def test_product_urls_not_filtered(self, url):
        assert is_non_product_url(url) is False

    def test_empty_path_filtered(self):
        """Root URL with no path is not a product."""
        assert is_non_product_url("https://example.com") is True

    def test_trailing_slash_handled(self):
        """Trailing slashes should not affect filtering."""
        assert is_non_product_url("https://example.com/about/") is True
        assert is_non_product_url("https://example.com/products/widget/") is False


class TestPlatformProductSitemaps:
    def test_shopify_sitemaps(self):
        assert "/sitemap_products_1.xml" in PLATFORM_PRODUCT_SITEMAPS["shopify"]

    def test_woocommerce_sitemaps(self):
        assert "/product-sitemap.xml" in PLATFORM_PRODUCT_SITEMAPS["woocommerce"]

    def test_generic_empty(self):
        assert PLATFORM_PRODUCT_SITEMAPS["generic"] == []

    def test_all_platforms_present(self):
        for platform in ["shopify", "woocommerce", "magento", "bigcommerce", "shopware", "generic"]:
            assert platform in PLATFORM_PRODUCT_SITEMAPS
