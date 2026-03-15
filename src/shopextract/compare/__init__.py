"""Compare products across stores — price comparison, catalog diff, matching."""

from .catalog import compare_catalogs
from .match import fuzzy_match, match_gtin
from .price import compare

__all__ = [
    "compare",
    "compare_catalogs",
    "fuzzy_match",
    "match_gtin",
]
