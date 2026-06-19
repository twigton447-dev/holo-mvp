from __future__ import annotations

from typing import Any


def weighted_scores(score: dict[str, Any]) -> tuple[float | None, float | None]:
    try:
        return (
            float(score["document_x"]["weighted_score_1_10"]),
            float(score["document_y"]["weighted_score_1_10"]),
        )
    except Exception:
        return None, None


def score_verdict_consistency_flags(
    score: dict[str, Any],
    *,
    tolerance: float = 0.05,
) -> list[str]:
    x_score, y_score = weighted_scores(score)
    if x_score is None or y_score is None:
        return ["missing_weighted_score_for_verdict_check"]

    verdict = str(score.get("comparative_verdict", {}).get("stronger_document", "")).strip().lower()
    if x_score > y_score + tolerance and verdict != "document_x":
        return [f"verdict_score_contradiction:score_favors_document_x:{x_score:.3f}>{y_score:.3f}:verdict={verdict or 'missing'}"]
    if y_score > x_score + tolerance and verdict != "document_y":
        return [f"verdict_score_contradiction:score_favors_document_y:{y_score:.3f}>{x_score:.3f}:verdict={verdict or 'missing'}"]
    if abs(x_score - y_score) <= tolerance and verdict not in {"document_x", "document_y", "tie"}:
        return [f"verdict_score_contradiction:near_tie:{x_score:.3f}~{y_score:.3f}:verdict={verdict or 'missing'}"]
    return []
