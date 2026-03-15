"""shopextract -- Extract, compare, and monitor product data from any e-commerce store.

Public API:
    detect(url) -> PlatformResult
    discover(url, ...) -> list[str]
    extract(url, ...) -> ExtractionResult
    extract_one(url) -> dict
    from_feed(feed_url, ...) -> ExtractionResult
"""

from ._detect import detect
from ._discover import discover
from ._extract import extract, extract_one, from_feed
from ._models import (
    ExtractionResult,
    ExtractionTier,
    ExtractorResult,
    Platform,
    PlatformResult,
    Product,
    Variant,
)
from ._normalize import normalize
from ._quality import QualityScorer

__version__ = "0.1.0"

__all__ = [
    # Core functions
    "detect",
    "discover",
    "extract",
    "extract_one",
    "from_feed",
    "normalize",
    # Data models
    "ExtractionResult",
    "ExtractionTier",
    "ExtractorResult",
    "Platform",
    "PlatformResult",
    "Product",
    "Variant",
    # Utilities
    "QualityScorer",
]
