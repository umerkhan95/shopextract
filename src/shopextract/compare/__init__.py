"""Compare products across stores — price comparison, catalog diff, matching."""

from .evaluation import evaluate_matching
from .catalog import compare_catalogs
from .match import fuzzy_match, match_gtin
from .price import compare

__all__ = [
    "MatchDecision", "MatchRelation", "classify_match", "match_products", "normalized_attributes",
    "evaluate_matching",
    "compare",
    "compare_catalogs",
    "fuzzy_match",
    "match_gtin",
]

from .identity_match import MatchDecision, MatchRelation, classify_match, match_products, normalized_attributes
