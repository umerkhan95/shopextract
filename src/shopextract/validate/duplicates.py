"""Duplicate product detection.

Supports exact matching (GTIN, SKU) and fuzzy matching (title similarity).
"""

from __future__ import annotations

from difflib import SequenceMatcher

_SUPPORTED_METHODS = ("title", "gtin", "sku")


def find_duplicates(
    products: list[dict],
    method: str = "title",
    threshold: float = 0.9,
) -> list[tuple[int, int, float]]:
    """Find duplicate products using the specified method.

    Args:
        products: List of product dicts to check.
        method: Detection method - "title" (fuzzy), "gtin" (exact), "sku" (exact).
        threshold: Similarity threshold for fuzzy matching (0.0-1.0).

    Returns:
        List of (index_a, index_b, similarity) tuples for duplicate pairs.
    """
    if method not in _SUPPORTED_METHODS:
        raise ValueError(
            f"Unsupported method: {method!r}. Supported: {list(_SUPPORTED_METHODS)}"
        )

    if method == "title":
        return _find_by_title(products, threshold)
    elif method == "gtin":
        return _find_by_exact_field(products, "gtin")
    else:
        return _find_by_exact_field(products, "sku")


def _find_by_title(
    products: list[dict], threshold: float,
) -> list[tuple[int, int, float]]:
    """Find duplicates by fuzzy title matching."""
    duplicates: list[tuple[int, int, float]] = []
    titles = [_normalize_title(p.get("title", "")) for p in products]

    for i in range(len(titles)):
        if not titles[i]:
            continue
        for j in range(i + 1, len(titles)):
            if not titles[j]:
                continue
            ratio = SequenceMatcher(None, titles[i], titles[j]).ratio()
            if ratio >= threshold:
                duplicates.append((i, j, ratio))

    return duplicates


def _find_by_exact_field(
    products: list[dict], field: str,
) -> list[tuple[int, int, float]]:
    """Find duplicates by exact field value match."""
    seen: dict[str, int] = {}
    duplicates: list[tuple[int, int, float]] = []

    for idx, product in enumerate(products):
        value = (product.get(field) or "").strip()
        if not value:
            continue
        if value in seen:
            duplicates.append((seen[value], idx, 1.0))
        else:
            seen[value] = idx

    return duplicates


def _normalize_title(title: str) -> str:
    """Normalize title for comparison."""
    return " ".join(str(title).lower().split())
