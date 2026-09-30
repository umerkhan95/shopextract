"""Offline labeled pair evaluation for product matching."""
from __future__ import annotations

from .identity_match import MatchRelation, classify_match


def evaluate_matching(dataset: list[dict], *, threshold: float = 0.8) -> dict:
    """Report exact precision and recall/coverage, plus review and relation accuracy.

    Rows contain id, a, b, label. Coverage is recovered labeled exact pairs divided
    by all labeled exact pairs; review decisions are abstentions, never positives.
    """
    tp = fp = expected_exact = correct = review = 0
    predictions = []
    for row in dataset:
        label = MatchRelation(row["label"])
        decision = classify_match(row["a"], row["b"], threshold=threshold)
        accepted = decision.relation == MatchRelation.EXACT and not decision.needs_review
        expected_exact += label == MatchRelation.EXACT
        tp += accepted and label == MatchRelation.EXACT
        fp += accepted and label != MatchRelation.EXACT
        correct += decision.relation == label
        review += decision.needs_review
        predictions.append({"id": row["id"], "label": label.value, "prediction": decision.relation.value,
                            "needs_review": decision.needs_review, "evidence": decision.evidence,
                            "conflicts": decision.conflicts})
    total = len(dataset)
    precision = tp / (tp + fp) if tp + fp else 0.0
    coverage = tp / expected_exact if expected_exact else 0.0
    return {"total_pairs": total, "accepted_exact": tp + fp, "true_exact": tp,
            "false_exact": fp, "labeled_exact": expected_exact, "precision": precision,
            "coverage": coverage, "review_rate": review / total if total else 0.0,
            "relation_accuracy": correct / total if total else 0.0,
            "acceptance": {"min_precision": 1.0, "min_coverage": 0.8, "max_false_exact": 0},
            "passed": precision >= 1.0 and coverage >= 0.8 and fp == 0,
            "predictions": predictions}
