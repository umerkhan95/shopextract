"""Product validation for marketplace compliance.

Public API:
    validate(products, marketplace) -> ValidationReport
    check_images(products) -> list[ImageIssue]
    find_duplicates(products, method, threshold) -> list[tuple]
"""

from __future__ import annotations

from .duplicates import find_duplicates
from .images import check_images
from .marketplace import validate

__all__ = [
    "check_images",
    "find_duplicates",
    "validate",
]
