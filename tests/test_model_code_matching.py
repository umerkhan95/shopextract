"""Focused contract tests for conservative model-code matching (SC-04)."""

import pytest


def test_extract_model_codes_from_title_and_sku():
    from shopextract.compare.identity_match import extract_model_codes

    product = {
        "title": "Anex Air Fryer AG-2017 4 L",
        "sku": "ANX-AG2017-BLK",
        "mpn": "AG-2017",
    }
    assert extract_model_codes(product) == frozenset({"AG2017"})
    assert extract_model_codes({"title": "Anex Air Fryer", "sku": "AG-2017"}) == frozenset({"AG2017"})


def test_extract_model_codes_ignores_capacity_and_generic_words():
    from shopextract.compare.identity_match import extract_model_codes

    product = {"title": "Air Fryer 4 L, 1200 W, 16 GB", "sku": "BLACK-XL"}
    assert extract_model_codes(product) == frozenset()
    assert extract_model_codes({"title": "Anex Air Fryer 2024 Deluxe"}) == frozenset()
    assert extract_model_codes({"title": "Brand A QX 900 air fryer"}) == frozenset({"QX900"})


def test_conflicting_model_codes_are_hard_unmatched_candidates():
    from shopextract.compare.identity_match import MatchRelation, classify_match

    decision = classify_match(
        {"title": "Anex air fryer AG-2121"},
        {"title": "Anex air fryer AG-2123"},
        threshold=0.5,
    )
    assert decision.relation is MatchRelation.UNMATCHED
    assert any("model code" in conflict for conflict in decision.conflicts)


def test_equal_model_code_does_not_override_brand_conflict():
    from shopextract.compare.identity_match import MatchRelation, classify_match

    decision = classify_match(
        {"title": "Brand A QX 900 air fryer", "vendor": "Brand A"},
        {"title": "Brand B QX 900 air fryer", "vendor": "Brand B"},
        threshold=0.5,
    )
    assert decision.relation is not MatchRelation.EXACT
    assert "brand differs" in decision.conflicts


def test_fuzzy_match_returns_indexed_decisions_and_rejects_invalid_threshold():
    from shopextract.compare.identity_match import MatchDecision
    from shopextract.compare.match import fuzzy_match

    result = fuzzy_match(
        [{"title": "Anex air fryer AG-2017"}],
        [{"title": "Anex fryer AG-2017"}],
        threshold=0.5,
    )
    assert result and isinstance(result[0], MatchDecision)
    assert result[0].index_a == 0 and result[0].index_b == 0
    with pytest.raises(ValueError, match="threshold"):
        fuzzy_match([], [], threshold=1.1)
