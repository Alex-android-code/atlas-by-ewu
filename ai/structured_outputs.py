"""Structured AI output validation helpers."""

from __future__ import annotations

from typing import Any

from ai.models import MatchingEvaluation


def validate_matching_evaluation(data: dict[str, Any]) -> MatchingEvaluation:
    return MatchingEvaluation.model_validate(data)


def deterministic_top_n(candidates: list[dict[str, Any]], *, top_n: int) -> list[dict[str, Any]]:
    return sorted(candidates, key=lambda item: float(item.get("score", 0)), reverse=True)[: max(0, top_n)]
