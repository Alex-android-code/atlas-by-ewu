"""Vacancy quality analyzer used by the employer coordinator experience."""

from __future__ import annotations

from typing import Any

from market_rules.salary_rules import SalaryRuleProvider


class VacancyAnalyzer:
    """Scores vacancy completeness and competitiveness without country hardcoding."""

    def __init__(self, salary_rules: SalaryRuleProvider | None = None) -> None:
        self.salary_rules = salary_rules or SalaryRuleProvider()

    def analyze(self, vacancy: dict[str, Any]) -> dict[str, Any]:
        checks = []
        suggestions = []
        score = 100

        profession = vacancy.get("profession")
        salary = vacancy.get("salary")
        country = vacancy.get("country")
        quantity = vacancy.get("quantity")
        housing = vacancy.get("housing")
        transport = vacancy.get("transport")
        start_date = vacancy.get("start_date")
        requirements = vacancy.get("requirements") or []

        if not profession:
            score -= 18
            suggestions.append("advisor.missing_profession")
        if not quantity:
            score -= 10
            suggestions.append("advisor.missing_quantity")
        if not country:
            score -= 10
            suggestions.append("advisor.missing_country")
        if salary:
            salary_result = self.salary_rules.evaluate(profession=profession, country=country, salary=salary)
            checks.append(salary_result)
            if salary_result["status"] == "warning":
                score -= 14
                suggestions.append("advisor.salary_below_market")
        else:
            score -= 16
            suggestions.append("advisor.missing_salary")
        if housing is True:
            checks.append({"key": "advisor.housing_available", "status": "ok"})
        else:
            score -= 12
            suggestions.append("advisor.housing_missing")
        if transport:
            checks.append({"key": "advisor.transport_available", "status": "ok"})
        else:
            score -= 6
            suggestions.append("advisor.transport_missing")
        if not start_date:
            score -= 8
            suggestions.append("advisor.missing_start_date")
        if not requirements:
            score -= 8
            suggestions.append("advisor.missing_requirements")
        elif not _has_certificate_requirement(requirements):
            score -= 5
            suggestions.append("advisor.certificates_recommended")

        score = max(0, min(100, score))
        status = "excellent" if score >= 86 else "good" if score >= 70 else "needs_work"
        return {
            "score": score,
            "status": status,
            "checks": checks,
            "suggestions": suggestions[:5],
            "pipeline": build_vacancy_pipeline(vacancy),
        }


def build_vacancy_pipeline(vacancy: dict[str, Any]) -> list[dict[str, Any]]:
    found = min(int(vacancy.get("found", 0) or 0), int(vacancy.get("quantity", 0) or 0))
    return [
        {"key": "pipeline.need", "status": "complete" if vacancy.get("quantity") else "active"},
        {"key": "pipeline.found", "status": "complete" if found else "pending"},
        {"key": "pipeline.verified", "status": "complete" if vacancy.get("verified") else "pending"},
        {"key": "pipeline.recommended", "status": "complete" if vacancy.get("recommended") else "pending"},
        {"key": "pipeline.accepted", "status": "complete" if vacancy.get("accepted") else "pending"},
        {"key": "pipeline.started", "status": "complete" if vacancy.get("started") else "pending"},
    ]


def _has_certificate_requirement(requirements: list[str]) -> bool:
    text = " ".join(str(item).lower() for item in requirements)
    return any(token in text for token in ("cert", "certificate", "license", "uprawn", "сертиф", "допуск"))
