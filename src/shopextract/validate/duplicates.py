"""Duplicate product detection.

Supports exact matching (GTIN, SKU) and fuzzy matching (title similarity).
"""

from __future__ import annotations

from difflib import SequenceMatcher
from itertools import combinations
import math
import re
import unicodedata

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

    # Low thresholds can match titles without a shared word, so retain the
    # exhaustive path there. At the normal duplicate threshold, rare-token
    # blocking avoids scoring unrelated catalog rows while preserving exact
    # duplicate groups even when their only words are common.
    if threshold < 0.75:
        candidates = ((i, j) for i in range(len(titles)) for j in range(i + 1, len(titles)))
    else:
        tokens = [set(re.findall(r"[a-z0-9]+", title)) for title in titles]
        grams = [
            {title[offset:offset + 3] for offset in range(max(0, len(title) - 2))}
            for title in titles
        ]
        token_rows: dict[str, list[int]] = {}
        gram_rows: dict[str, list[int]] = {}
        exact_rows: dict[str, list[int]] = {}
        for index, (title, row_tokens) in enumerate(zip(titles, tokens)):
            if title:
                exact_rows.setdefault(title, []).append(index)
            for token in row_tokens:
                token_rows.setdefault(token, []).append(index)
            for gram in grams[index]:
                gram_rows.setdefault(gram, []).append(index)

        common_limit = max(8, math.ceil(math.sqrt(len(titles)) * 2))
        candidate_pairs: set[tuple[int, int]] = set()
        for indexes in exact_rows.values():
            candidate_pairs.update(combinations(indexes, 2))
        checked_pairs: set[tuple[int, int]] = set()
        for indexes in token_rows.values():
            frequent = len(indexes) > common_limit
            for pair in combinations(indexes, 2):
                if pair in checked_pairs:
                    continue
                checked_pairs.add(pair)
                if not frequent:
                    candidate_pairs.add(pair)
                    continue
                i, j = pair
                if SequenceMatcher(None, titles[i], titles[j]).quick_ratio() >= threshold:
                    candidate_pairs.add(pair)
        checked_pairs.clear()
        for indexes in gram_rows.values():
            for pair in combinations(indexes, 2):
                if pair in checked_pairs or pair in candidate_pairs:
                    continue
                checked_pairs.add(pair)
                i, j = pair
                if SequenceMatcher(None, titles[i], titles[j]).quick_ratio() >= threshold:
                    candidate_pairs.add(pair)
        short_rows = [index for index, title in enumerate(titles) if title and len(title) < 3]
        for i in short_rows:
            for j, title in enumerate(titles):
                if i == j or not title:
                    continue
                pair = (i, j) if i < j else (j, i)
                if pair in candidate_pairs:
                    continue
                if SequenceMatcher(None, titles[pair[0]], titles[pair[1]]).quick_ratio() >= threshold:
                    candidate_pairs.add(pair)
        candidates = iter(sorted(candidate_pairs))

    from ..compare.identity_match import classify_match
    for i, j in candidates:
        if not titles[i] or not titles[j]:
            continue
        brand_a = " ".join(unicodedata.normalize(
            "NFKC", str(products[i].get("vendor") or products[i].get("brand") or "")
        ).casefold().split())
        brand_b = " ".join(unicodedata.normalize(
            "NFKC", str(products[j].get("vendor") or products[j].get("brand") or "")
        ).casefold().split())
        if brand_a and brand_b and brand_a != brand_b:
            continue
        matcher = SequenceMatcher(None, titles[i], titles[j])
        if matcher.quick_ratio() < threshold:
            continue
        ratio = matcher.ratio()
        if ratio < threshold:
            continue
        decision=classify_match(products[i],products[j],threshold=threshold)
        if any(not c.startswith('missing attributes:') for c in decision.conflicts):continue
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
