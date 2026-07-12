"""Modular employer trust scoring engine."""

from __future__ import annotations

from typing import Any

from trust_engine.adapters.base import TrustCheckAdapter
from trust_engine.adapters.internal import InternalHistoryAdapter, ProfileCompletenessAdapter


class EmployerTrustEngine:
    """Runs independent trust checks and returns a non-blocking recommendation."""

    def __init__(self, adapters: list[TrustCheckAdapter] | None = None) -> None:
        self.adapters = adapters or [ProfileCompletenessAdapter(), InternalHistoryAdapter()]

    def evaluate(self, employer: dict[str, Any], vacancy: dict[str, Any] | None = None) -> dict[str, Any]:
        checks = [adapter.check(employer=employer, vacancy=vacancy or {}) for adapter in self.adapters]
        score = 100 - sum(int(check.get("penalty", 0)) for check in checks)
        score = max(0, min(100, score))
        status = _status_for(score, checks)
        return {
            "score": score,
            "status": status,
            "checks": checks,
            "manual_review_recommended": status in {"under_review", "high_risk", "critical_risk"},
        }


def _status_for(score: int, checks: list[dict[str, Any]]) -> str:
    if any(check.get("status") == "critical" for check in checks) or score < 45:
        return "critical_risk"
    if score < 65:
        return "high_risk"
    if score < 85:
        return "under_review"
    return "trusted"
