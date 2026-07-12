"""Market rule adapters for vacancy competitiveness checks."""

from __future__ import annotations

from typing import Any


class SalaryRuleProvider:
    """Configurable market salary evaluator.

    The default values are conservative placeholders. Real country/profession
    benchmarks can later be loaded from files or external providers.
    """

    def __init__(self, rules: dict[str, Any] | None = None) -> None:
        self.rules = rules or {
            "default": {"minimum_competitive_salary": 1800, "currency": "EUR"},
            "welder": {"minimum_competitive_salary": 2200, "currency": "EUR"},
            "warehouse worker": {"minimum_competitive_salary": 1600, "currency": "EUR"},
            "driver": {"minimum_competitive_salary": 2100, "currency": "EUR"},
        }

    def evaluate(self, profession: str | None, country: str | None, salary: int | float | None) -> dict[str, Any]:
        key = str(profession or "default").lower()
        rule = self.rules.get(key, self.rules["default"])
        minimum = int(rule["minimum_competitive_salary"])
        amount = int(salary or 0)
        if amount and amount < minimum:
            return {
                "key": "advisor.salary_below_market",
                "status": "warning",
                "metadata": {"salary": amount, "minimum": minimum, "country": country},
            }
        return {
            "key": "advisor.salary_competitive",
            "status": "ok",
            "metadata": {"salary": amount, "minimum": minimum, "country": country},
        }
