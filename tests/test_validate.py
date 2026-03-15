"""Tests for marketplace validation, image checking, and duplicate detection."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
import httpx

from shopextract.validate.marketplace import validate
from shopextract.validate.duplicates import find_duplicates
from shopextract.validate.images import check_images
from shopextract._models import ImageIssue, ValidationReport


# -- Marketplace validation --

class TestValidateGoogleShopping:
    def test_valid_product(self):
        products = [{
            "title": "Widget",
            "price": "19.99",
            "image_url": "https://img.jpg",
            "product_url": "https://example.com/widget",
            "gtin": "4006381333931",
        }]
        report = validate(products, marketplace="google_shopping")
        assert report.valid == 1
        assert report.invalid == 0
        assert report.pass_rate == 100.0

    def test_missing_required_fields(self):
        products = [{"title": "Widget"}]
        report = validate(products, marketplace="google_shopping")
        assert report.invalid == 1
        errors = [i for i in report.issues if i.severity == "error"]
        fields = {i.field for i in errors}
        assert "price" in fields
        assert "image_url" in fields

    def test_title_too_long(self):
        products = [{
            "title": "x" * 200,
            "price": "10",
            "image_url": "https://img.jpg",
            "product_url": "https://example.com",
        }]
        report = validate(products, marketplace="google_shopping")
        assert any("max length" in i.error for i in report.issues)

    def test_missing_gtin_is_warning(self):
        products = [{
            "title": "Widget",
            "price": "10",
            "image_url": "https://img.jpg",
            "product_url": "https://example.com",
        }]
        report = validate(products, marketplace="google_shopping")
        assert report.warnings >= 1
        assert report.valid == 1  # Warnings don't invalidate


class TestValidateIdealo:
    def test_valid_product(self):
        products = [{
            "title": "Widget",
            "price": "19.99",
            "product_url": "https://example.com/widget",
            "image_url": "https://img.jpg",
            "sku": "W-001",
            "delivery_time": "1-3 days",
            "delivery_cost": "4.99",
        }]
        report = validate(products, marketplace="idealo")
        assert report.valid == 1

    def test_missing_delivery(self):
        products = [{
            "title": "Widget",
            "price": "19.99",
            "product_url": "https://example.com",
            "image_url": "https://img.jpg",
            "sku": "W-001",
        }]
        report = validate(products, marketplace="idealo")
        assert report.invalid == 1
        fields = {i.field for i in report.issues if i.severity == "error"}
        assert "delivery_time" in fields
        assert "delivery_cost" in fields

    def test_sku_or_external_id(self):
        products = [{
            "title": "Widget",
            "price": "19.99",
            "product_url": "https://example.com",
            "image_url": "https://img.jpg",
            "external_id": "EXT-001",
            "delivery_time": "1-3 days",
            "delivery_cost": "4.99",
        }]
        report = validate(products, marketplace="idealo")
        assert report.valid == 1


class TestValidateAmazon:
    def test_valid_product(self):
        products = [{
            "title": "Widget",
            "price": "19.99",
            "image_url": "https://img.jpg",
            "gtin": "4006381333931",
            "brand": "WidgetCo",
            "condition": "NEW",
        }]
        report = validate(products, marketplace="amazon")
        assert report.valid == 1

    def test_missing_gtin_is_error(self):
        products = [{
            "title": "Widget",
            "price": "19.99",
            "image_url": "https://img.jpg",
            "brand": "WidgetCo",
            "condition": "NEW",
        }]
        report = validate(products, marketplace="amazon")
        assert report.invalid == 1


class TestValidateEbay:
    def test_valid_product(self):
        products = [{
            "title": "Widget",
            "price": "19.99",
            "image_url": "https://img.jpg",
            "condition": "NEW",
        }]
        report = validate(products, marketplace="ebay")
        assert report.valid == 1

    def test_title_too_long(self):
        products = [{
            "title": "x" * 100,
            "price": "10",
            "image_url": "https://img.jpg",
            "condition": "NEW",
        }]
        report = validate(products, marketplace="ebay")
        assert any("max length" in i.error for i in report.issues)


class TestValidateEdgeCases:
    def test_unsupported_marketplace(self):
        with pytest.raises(ValueError, match="Unsupported marketplace"):
            validate([], marketplace="unknown_marketplace")

    def test_empty_products(self):
        report = validate([], marketplace="google_shopping")
        assert report.total == 0
        assert report.pass_rate == 0.0

    def test_negative_price(self):
        products = [{
            "title": "Widget",
            "price": -5,
            "image_url": "https://img.jpg",
            "product_url": "https://example.com",
        }]
        report = validate(products, marketplace="google_shopping")
        assert any("negative" in i.error.lower() for i in report.issues)

    def test_multiple_products(self):
        products = [
            {"title": "A", "price": "10", "image_url": "i.jpg", "product_url": "u"},
            {"title": "B"},  # missing required
        ]
        report = validate(products, marketplace="google_shopping")
        assert report.total == 2
        assert report.valid == 1
        assert report.invalid == 1


# -- Duplicate detection --

class TestFindDuplicates:
    def test_title_duplicates(self):
        products = [
            {"title": "Widget A"},
            {"title": "Widget A"},
            {"title": "Widget B"},
        ]
        dupes = find_duplicates(products, method="title", threshold=0.9)
        assert len(dupes) == 1
        assert dupes[0][0] == 0
        assert dupes[0][1] == 1
        assert dupes[0][2] >= 0.9

    def test_fuzzy_title_duplicates(self):
        products = [
            {"title": "Blue Widget Pro 2024"},
            {"title": "Blue Widget Pro 2024 - Large"},
        ]
        dupes = find_duplicates(products, method="title", threshold=0.7)
        assert len(dupes) >= 1

    def test_no_duplicates(self):
        products = [
            {"title": "Apple"},
            {"title": "Banana"},
            {"title": "Cherry"},
        ]
        dupes = find_duplicates(products, method="title", threshold=0.9)
        assert len(dupes) == 0

    def test_gtin_duplicates(self):
        products = [
            {"title": "A", "gtin": "4006381333931"},
            {"title": "B", "gtin": "5901234123457"},
            {"title": "C", "gtin": "4006381333931"},
        ]
        dupes = find_duplicates(products, method="gtin")
        assert len(dupes) == 1
        assert dupes[0][2] == 1.0

    def test_sku_duplicates(self):
        products = [
            {"title": "A", "sku": "SKU-001"},
            {"title": "B", "sku": "SKU-002"},
            {"title": "C", "sku": "SKU-001"},
        ]
        dupes = find_duplicates(products, method="sku")
        assert len(dupes) == 1

    def test_empty_gtin_not_matched(self):
        products = [
            {"title": "A", "gtin": ""},
            {"title": "B", "gtin": ""},
        ]
        dupes = find_duplicates(products, method="gtin")
        assert len(dupes) == 0

    def test_unsupported_method(self):
        with pytest.raises(ValueError, match="Unsupported method"):
            find_duplicates([], method="unknown")

    def test_empty_products(self):
        dupes = find_duplicates([], method="title")
        assert dupes == []


# -- Image checking (mocked HTTP) --

@pytest.mark.asyncio
async def test_check_images_valid():
    """Valid images should produce no issues."""
    products = [{"title": "A", "image_url": "https://example.com/a.jpg"}]

    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, headers={"content-type": "image/jpeg"})
    )
    async with httpx.AsyncClient(transport=transport) as client:
        with patch("shopextract.validate.images.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            issues = await check_images(products)

    assert len(issues) == 0


@pytest.mark.asyncio
async def test_check_images_missing_url():
    """Products with no image_url should produce an issue."""
    products = [{"title": "A", "image_url": ""}]

    transport = httpx.MockTransport(lambda req: httpx.Response(200))
    async with httpx.AsyncClient(transport=transport) as client:
        with patch("shopextract.validate.images.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            issues = await check_images(products)

    assert len(issues) == 1
    assert "No image URL" in issues[0].error


@pytest.mark.asyncio
async def test_check_images_404():
    """Broken image links should produce an issue."""
    products = [{"title": "A", "image_url": "https://example.com/missing.jpg"}]

    transport = httpx.MockTransport(
        lambda req: httpx.Response(404, headers={"content-type": "text/html"})
    )
    async with httpx.AsyncClient(transport=transport) as client:
        with patch("shopextract.validate.images.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            issues = await check_images(products)

    assert len(issues) == 1
    assert "404" in issues[0].error


@pytest.mark.asyncio
async def test_check_images_wrong_content_type():
    """Non-image content type should produce an issue."""
    products = [{"title": "A", "image_url": "https://example.com/page.html"}]

    transport = httpx.MockTransport(
        lambda req: httpx.Response(200, headers={"content-type": "text/html"})
    )
    async with httpx.AsyncClient(transport=transport) as client:
        with patch("shopextract.validate.images.httpx.AsyncClient") as MockClient:
            MockClient.return_value.__aenter__ = AsyncMock(return_value=client)
            MockClient.return_value.__aexit__ = AsyncMock(return_value=False)
            issues = await check_images(products)

    assert len(issues) == 1
    assert "Non-image" in issues[0].error
