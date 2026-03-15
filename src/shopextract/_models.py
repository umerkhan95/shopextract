"""Data models for shopextract."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum


class Platform(StrEnum):
    """Supported e-commerce platforms."""

    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"
    MAGENTO = "magento"
    BIGCOMMERCE = "bigcommerce"
    SHOPWARE = "shopware"
    GENERIC = "generic"


class ExtractionTier(StrEnum):
    """Product extraction tier/strategy."""

    API = "api"
    UNIFIED_CRAWL = "unified_crawl"
    GOOGLE_FEED = "google_feed"
    CSS = "css"
    LLM = "llm"


@dataclass
class Variant:
    """Product variant."""

    variant_id: str = ""
    title: str = ""
    price: Decimal = Decimal("0")
    sku: str | None = None
    in_stock: bool = True


@dataclass
class Product:
    """Unified product model across all platforms."""

    title: str = ""
    price: Decimal = Decimal("0")
    currency: str = "USD"
    description: str = ""
    image_url: str = ""
    product_url: str = ""
    external_id: str = ""
    sku: str | None = None
    gtin: str | None = None
    mpn: str | None = None
    vendor: str | None = None
    product_type: str | None = None
    in_stock: bool = True
    condition: str | None = None
    compare_at_price: Decimal | None = None
    variants: list[Variant] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    additional_images: list[str] = field(default_factory=list)
    category_path: list[str] = field(default_factory=list)
    platform: Platform = Platform.GENERIC
    scraped_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    raw_data: dict = field(default_factory=dict)


@dataclass
class PlatformResult:
    """Result of platform detection."""

    platform: Platform
    confidence: float  # 0.0-1.0
    signals: list[str] = field(default_factory=list)


@dataclass
class ExtractorResult:
    """Result from a single extractor call."""

    products: list[dict] = field(default_factory=list)
    complete: bool = True
    error: str | None = None
    pages_completed: int | None = None
    pages_expected: int | None = None

    @property
    def product_count(self) -> int:
        return len(self.products)

    @property
    def is_empty(self) -> bool:
        return len(self.products) == 0


@dataclass
class ExtractionResult:
    """Pipeline-level extraction result with quality metadata."""

    products: list[Product] = field(default_factory=list)
    raw_products: list[dict] = field(default_factory=list)
    tier: ExtractionTier = ExtractionTier.UNIFIED_CRAWL
    quality_score: float = 0.0
    platform: Platform = Platform.GENERIC
    urls_attempted: int = 0
    urls_succeeded: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def product_count(self) -> int:
        return len(self.products)
