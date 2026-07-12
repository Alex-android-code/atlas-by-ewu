"""Live recruitment advice composition."""

from __future__ import annotations

from typing import Any


class RecruitmentAdvisor:
    """Turns vacancy quality analysis into short advisor cards."""

    def build_cards(self, analysis: dict[str, Any]) -> list[dict[str, str]]:
        cards = []
        for key in analysis.get("suggestions", []):
            severity = "warning" if key in {
                "advisor.salary_below_market",
                "advisor.housing_missing",
                "advisor.transport_missing",
                "advisor.missing_start_date",
            } else "info"
            cards.append({"key": key, "severity": severity})
        if not cards:
            cards.append({"key": "advisor.vacancy_strong", "severity": "ok"})
        return cards[:5]
