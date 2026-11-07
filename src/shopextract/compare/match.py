"""Shared indexed match decisions and simple GTIN candidate lookup."""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .identity_match import MatchDecision

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
) -> list[MatchDecision]:
    """Return indexed identity decisions for fuzzy title candidates.

    The public result shape matches :func:`identity_match.match_products`.
    Strong shared identifiers can authorize a decision below the title
    threshold; conflicting model codes and incompatible attributes veto it.
    """
    from .identity_match import MatchRelation, classify_match

    if not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    matches = []
    used_b: set[int] = set()

    for index_a, prod_a in enumerate(products_a):
        title_a = prod_a.get("title", "")
        best_sim = 0.0
        best_idx = -1
        best_decision = None

        for idx, prod_b in enumerate(products_b):
            if idx in used_b:
                continue
            decision = classify_match(prod_a, prod_b, threshold=threshold)
            if decision.relation == MatchRelation.UNMATCHED:
                continue
            ambiguous_codes = any(c.startswith("ambiguous model codes:") for c in decision.conflicts)
            if any(not c.startswith(("missing attributes:", "ambiguous model codes:"))
                   for c in decision.conflicts):
                continue
            sim = title_similarity(title_a, prod_b.get("title", ""))
            if decision.relation == MatchRelation.EXACT:
                score = 1.0
            elif ambiguous_codes:
                # Keep overlapping ambiguous-code candidates visible for review
                # even when title similarity alone misses the caller threshold.
                score = decision.confidence
            else:
                if sim < threshold:
                    continue
                score = sim
                decision.confidence = sim
            if score > best_sim:
                best_sim = score
                best_idx = idx
                best_decision = decision

        if best_decision is not None:
            best_decision.index_a = index_a
            best_decision.index_b = best_idx
            best_decision.candidate_method = "fuzzy"
            matches.append(best_decision)
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
