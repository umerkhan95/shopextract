"""shopextract -- Extract, compare, and monitor product data from any e-commerce store.

Public API:
    detect(url) -> PlatformResult
    discover(url, ...) -> list[str]
    extract(url, ..., llm_api_key=, llm_model=) -> ExtractionResult
    extract_one(url, ..., llm_api_key=, llm_model=) -> dict
    from_feed(feed_url, ...) -> ExtractionResult
    compare(query, stores) -> ComparisonResult
    compare_catalogs(store_a, store_b) -> CatalogDiff
    fuzzy_match(products_a, products_b) -> list[tuple]
    match_gtin(gtin, products) -> list[dict]
    snapshot(url) -> int
    changes(domain) -> list[Change]
    price_history(domain, product_title) -> list[tuple]
    watch(url) -> AsyncGenerator[Change]
    analyze(url) -> CatalogStats
    analyze_products(products) -> CatalogStats
    price_distribution(products) -> dict[str, int]
    outliers(products) -> list[dict]
    brand_breakdown(products) -> dict[str, float]
    price_position(my_product, competitors) -> PricePosition
    assortment_gaps(my_store, competitors) -> AssortmentGaps
    brand_coverage(catalogs) -> dict[str, dict[str, int]]
    validate(products, marketplace) -> ValidationReport
    check_images(products) -> list[ImageIssue]
    find_duplicates(products, method, threshold) -> list[tuple]
    to_csv(products, path) -> None
    to_json(products, path, indent) -> None
    to_feed(products, path, format) -> None
    to_dataframe(products) -> pandas.DataFrame
    to_parquet(products, path) -> None
"""

from ._detect import detect
from ._discover import discover
from ._extract import extract, extract_one, from_feed
from ._models import (
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
from ._normalize import normalize
from ._quality import QualityScorer
from .analyze import (
    analyze,
    analyze_products,
    assortment_gaps,
    brand_breakdown,
    brand_coverage,
    outliers,
    price_distribution,
    price_position,
)
from .compare import compare, compare_catalogs, fuzzy_match, match_gtin
from .export import to_csv, to_dataframe, to_feed, to_json, to_parquet
from .monitor import changes, price_history, snapshot, watch
from .validate import check_images, find_duplicates, validate

__version__ = "0.1.1"

__all__ = [
    # Core functions
    "detect",
    "discover",
    "extract",
    "extract_one",
    "from_feed",
    "normalize",
    # Compare functions
    "compare",
    "compare_catalogs",
    "fuzzy_match",
    "match_gtin",
    # Monitor functions
    "snapshot",
    "changes",
    "price_history",
    "watch",
    # Analyze functions
    "analyze",
    "analyze_products",
    "price_distribution",
    "outliers",
    "brand_breakdown",
    # Competitive intelligence
    "price_position",
    "assortment_gaps",
    "brand_coverage",
    # Validate functions
    "validate",
    "check_images",
    "find_duplicates",
    # Export functions
    "to_csv",
    "to_json",
    "to_feed",
    "to_dataframe",
    "to_parquet",
    # Data models
    "AssortmentGaps",
    "CatalogStats",
    "CatalogDiff",
    "Change",
    "ChangeType",
    "ComparisonResult",
    "ExtractionResult",
    "ExtractionTier",
    "ExtractorResult",
    "ImageIssue",
    "Match",
    "NewProduct",
    "Platform",
    "PlatformResult",
    "PriceChange",
    "PricePosition",
    "Product",
    "RemovedProduct",
    "ValidationIssue",
    "ValidationReport",
    "Variant",
    # Utilities
    "QualityScorer",
]
