"""Shared fixtures for shopextract tests."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path

import pytest

from shopextract._models import Product, Platform

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def shopify_raw_products() -> list[dict]:
    """Raw Shopify product dicts as returned by /products.json."""
    data = json.loads((FIXTURES_DIR / "shopify_products.json").read_text())
    return data["products"]


@pytest.fixture
def woocommerce_raw_products() -> list[dict]:
    """Raw WooCommerce Store API product dicts."""
    return json.loads((FIXTURES_DIR / "woocommerce_products.json").read_text())


@pytest.fixture
def minimal_product() -> Product:
    """A product with minimal data."""
    return Product(
        title="Test Product",
        price=Decimal("9.99"),
        external_id="TP-001",
        platform=Platform.GENERIC,
    )


@pytest.fixture
def complete_product() -> Product:
    """A product with all fields populated."""
    return Product(
        title="Complete Widget",
        price=Decimal("49.99"),
        compare_at_price=Decimal("59.99"),
        currency="EUR",
        description="A fully-specified widget for testing.",
        image_url="https://example.com/widget.jpg",
        product_url="https://example.com/products/widget",
        external_id="WDG-100",
        sku="WDG-100-SKU",
        gtin="4006381333931",
        mpn="MPN-WDG-100",
        vendor="WidgetCorp",
        product_type="Widgets",
        in_stock=True,
        condition="NEW",
        tags=["widget", "premium"],
        additional_images=["https://example.com/widget-2.jpg"],
        category_path=["Hardware", "Widgets"],
        platform=Platform.SHOPIFY,
    )


@pytest.fixture
def sample_products_dicts() -> list[dict]:
    """List of raw product dicts for analysis/validation tests."""
    return [
        {
            "title": "Widget A",
            "price": "29.99",
            "currency": "USD",
            "image_url": "https://example.com/a.jpg",
            "product_url": "https://example.com/a",
            "vendor": "BrandX",
            "gtin": "4006381333931",
            "sku": "WA-001",
            "description": "A great widget.",
            "in_stock": True,
            "category_path": ["Electronics", "Widgets"],
        },
        {
            "title": "Widget B",
            "price": "49.99",
            "currency": "USD",
            "image_url": "https://example.com/b.jpg",
            "product_url": "https://example.com/b",
            "vendor": "BrandX",
            "gtin": "5901234123457",
            "sku": "WB-002",
            "description": "Another widget.",
            "in_stock": True,
            "category_path": ["Electronics", "Widgets"],
        },
        {
            "title": "Gadget C",
            "price": "199.99",
            "currency": "USD",
            "image_url": "https://example.com/c.jpg",
            "product_url": "https://example.com/c",
            "vendor": "BrandY",
            "sku": "GC-003",
            "description": "Premium gadget.",
            "in_stock": False,
            "category_path": ["Electronics", "Gadgets"],
        },
        {
            "title": "Widget D",
            "price": "15.00",
            "currency": "EUR",
            "image_url": "https://example.com/d.jpg",
            "product_url": "https://example.com/d",
            "vendor": "BrandX",
            "sku": "WD-004",
            "description": "",
            "in_stock": True,
        },
    ]


@pytest.fixture
def product_dicts_for_export() -> list[dict]:
    """Products specifically for export tests."""
    return [
        {
            "external_id": "P001",
            "title": "Export Product 1",
            "price": "19.99",
            "currency": "USD",
            "image_url": "https://example.com/p1.jpg",
            "product_url": "https://example.com/p1",
            "gtin": "4006381333931",
            "description": "First product",
            "brand": "TestBrand",
            "condition": "new",
            "in_stock": True,
        },
        {
            "external_id": "P002",
            "title": "Export Product 2",
            "price": "39.99",
            "currency": "EUR",
            "image_url": "https://example.com/p2.jpg",
            "product_url": "https://example.com/p2",
            "description": "Second product",
            "in_stock": False,
        },
    ]
