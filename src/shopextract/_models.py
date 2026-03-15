"""Data models for shopextract."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum


class Platform(str, Enum):
    """Supported e-commerce platforms."""

    SHOPIFY = "shopify"
    WOOCOMMERCE = "woocommerce"
    MAGENTO = "magento"
    BIGCOMMERCE = "bigcommerce"
    SHOPWARE = "shopware"
    GENERIC = "generic"


class ExtractionTier(str, Enum):
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
    scraped_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
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
    def product_count(self) -> int:  # noqa: E303
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


# --- Compare models (#8, #9) ---


@dataclass
class Match:
    """A product matched across stores."""

    title: str
    price: Decimal
    currency: str
    store: str
    product_url: str
    similarity: float = 1.0


@dataclass
class ComparisonResult:
    """Result of cross-store price comparison."""

    query: str
    matches: list[Match] = field(default_factory=list)
    cheapest: Match | None = None
    most_expensive: Match | None = None
    avg_price: Decimal = Decimal("0")
    price_spread: Decimal = Decimal("0")


@dataclass
class CatalogDiff:
    """Difference between two store catalogs."""

    store_a: str
    store_b: str
    only_in_a: list[Product] = field(default_factory=list)
    only_in_b: list[Product] = field(default_factory=list)
    in_both: list[tuple[Product, Product]] = field(default_factory=list)
    cheaper_in_a: list[tuple[Product, Product]] = field(default_factory=list)
    cheaper_in_b: list[tuple[Product, Product]] = field(default_factory=list)


# --- Monitor models (#11, #12, #13) ---


class ChangeType(str, Enum):
    """Type of product change between snapshots."""

    PRICE_CHANGE = "price_change"
    NEW_PRODUCT = "new_product"
    REMOVED_PRODUCT = "removed_product"


@dataclass
class Change:
    """Base change between snapshots."""

    change_type: ChangeType = ChangeType.PRICE_CHANGE
    title: str = ""
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class PriceChange(Change):
    """Price changed between snapshots."""

    old_price: Decimal = Decimal("0")
    new_price: Decimal = Decimal("0")
    currency: str = "USD"

    def __post_init__(self) -> None:
        self.change_type = ChangeType.PRICE_CHANGE


@dataclass
class NewProduct(Change):
    """Product appeared in latest snapshot."""

    price: Decimal = Decimal("0")
    currency: str = "USD"

    def __post_init__(self) -> None:
        self.change_type = ChangeType.NEW_PRODUCT


@dataclass
class RemovedProduct(Change):
    """Product disappeared from latest snapshot."""

    last_price: Decimal = Decimal("0")
    currency: str = "USD"

    def __post_init__(self) -> None:
        self.change_type = ChangeType.REMOVED_PRODUCT


# --- Analyze models (#14, #15) ---


@dataclass
class CatalogStats:
    """Aggregate statistics for a product catalog."""

    total_products: int = 0
    price_range: tuple[float, float] = (0.0, 0.0)
    avg_price: float = 0.0
    median_price: float = 0.0
    currencies: dict[str, int] = field(default_factory=dict)
    brands: dict[str, int] = field(default_factory=dict)
    categories: dict[str, int] = field(default_factory=dict)
    in_stock: int = 0
    out_of_stock: int = 0
    has_gtin: int = 0
    has_images: int = 0
    completeness_score: float = 0.0


@dataclass
class PricePosition:
    """Price positioning of a product relative to competitors."""

    product_title: str = ""
    my_price: float = 0.0
    rank: int = 0
    total_competitors: int = 0
    percentile: float = 0.0
    market_avg: float = 0.0
    cheapest: float = 0.0
    most_expensive: float = 0.0
    competitor_prices: dict[str, float] = field(default_factory=dict)


@dataclass
class AssortmentGaps:
    """Categories and brands that competitors have but you don't."""

    missing_categories: list[str] = field(default_factory=list)
    missing_brands: list[str] = field(default_factory=list)
    competitor_category_counts: dict[str, dict[str, int]] = field(default_factory=dict)
    competitor_brand_counts: dict[str, dict[str, int]] = field(default_factory=dict)
    my_categories: list[str] = field(default_factory=list)
    my_brands: list[str] = field(default_factory=list)


# --- Validate models (#16) ---


@dataclass
class ValidationIssue:
    """A single validation issue for a product."""

    product_index: int
    product_title: str
    field: str
    error: str
    severity: str = "error"  # "error" or "warning"


@dataclass
class ValidationReport:
    """Result of marketplace validation."""

    marketplace: str
    total: int = 0
    valid: int = 0
    invalid: int = 0
    issues: list[ValidationIssue] = field(default_factory=list)
    warnings: int = 0

    @property
    def pass_rate(self) -> float:
        """Percentage of products that passed validation."""
        if self.total == 0:
            return 0.0
        return self.valid / self.total * 100.0


@dataclass
class ImageIssue:
    """Issue found during image URL validation."""

    product_index: int
    product_title: str
    image_url: str
    status_code: int | None = None
    content_type: str | None = None
    error: str = ""
