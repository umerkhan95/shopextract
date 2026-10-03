"""Legacy candidate lookup helpers; use match_products for identity decisions."""

from __future__ import annotations

from difflib import SequenceMatcher

_DEFAULT_THRESHOLD = 0.8


def title_similarity(a: str, b: str) -> float:
    """Compute normalized title similarity using SequenceMatcher."""
    return SequenceMatcher(
        None,
        a.lower().strip(),
        b.lower().strip(),
    ).ratio()


def fuzzy_match(
    products_a: list[dict],
    products_b: list[dict],
    *,
    threshold: float = _DEFAULT_THRESHOLD,
) -> list[tuple[dict, dict, float]]:
    """Match products by fuzzy title similarity.

    Returns list of (product_a, product_b, similarity) tuples
    where similarity >= threshold.
    """
    from .identity_match import classify_match

    matches: list[tuple[dict, dict, float]] = []
    used_b: set[int] = set()

    for prod_a in products_a:
        title_a = prod_a.get("title", "")
        best_sim = 0.0
        best_idx = -1
        best_prod = None

        for idx, prod_b in enumerate(products_b):
            if idx in used_b:
                continue
            decision = classify_match(prod_a, prod_b, threshold=threshold)
            if any(not c.startswith("missing attributes:") for c in decision.conflicts):
                continue
            sim = title_similarity(title_a, prod_b.get("title", ""))
            if sim > best_sim:
                best_sim = sim
                best_idx = idx
                best_prod = prod_b

        if best_sim >= threshold and best_prod is not None:
            matches.append((prod_a, best_prod, best_sim))
            used_b.add(best_idx)

    return matches


def match_gtin(gtin: str, products: list[dict]) -> list[dict]:
    """Find products with an exact GTIN or SKU match.

    Checks the 'gtin', 'ean', 'upc', and 'sku' fields. This legacy
    lookup neither validates GTINs nor scopes SKUs; results are candidates,
    not evidence of cross-store equivalence.
    """
    gtin_clean = gtin.strip()
    matched: list[dict] = []
    for product in products:
        for key in ("gtin", "ean", "upc", "sku"):
            value = product.get(key)
            if value and str(value).strip() == gtin_clean:
                matched.append(product)
                break
    return matched
