"""Skill gap analysis services for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from core.models import EmployerCompetencyRequirement, SkillGap, UserCompetency
from services.competency_intelligence import CompetencyIntelligenceService


@dataclass(frozen=True)
class TargetRequirement:
    competency_name: str
    required_level: int
    importance: int = 3
    source: str = "market_requirement"
    employer_id: str | None = None
    vacancy_id: str | None = None


class CompetencyVerificationService:
    def verification_status(self, competency: UserCompetency | None) -> str:
        if competency is None:
            return "missing"
        if competency.expiry_date and _is_past_date(competency.expiry_date):
            return "expired"
        if competency.verification_status == "verified":
            return "verified"
        return "insufficiently_verified"

    def required_action(self, competency: UserCompetency | None, required_level: int) -> str:
        status = self.verification_status(competency)
        if status == "missing":
            return "training"
        if status == "expired":
            return "certification_renewal"
        if status == "insufficiently_verified":
            return "confirmation"
        if competency and competency.current_level < required_level:
            return "practice"
        return "none"


class VacancyFitService:
    def fit_now(self, gap_reports: list[dict[str, Any]]) -> dict[str, Any]:
        if not gap_reports:
            return {"fit": "ready_now", "score": 100, "can_apply_now": True}
        weighted_gap = sum(item["gap_size"] * item["importance"] for item in gap_reports)
        critical_count = sum(1 for item in gap_reports if item["criticality"] == "critical")
        score = max(0, 100 - weighted_gap * 8 - critical_count * 10)
        if score >= 75 and critical_count == 0:
            fit = "apply_with_confirmation"
        elif score >= 50:
            fit = "apply_after_short_preparation"
        else:
            fit = "not_ready_yet"
        return {"fit": fit, "score": score, "can_apply_now": fit in {"ready_now", "apply_with_confirmation"}}


class CareerPathAnalysisService:
    def alternatives_for_gap(self, competency_name: str, action: str) -> list[str]:
        if action == "training":
            return ["supervised_work", "mentorship", "practical_assignment"]
        if action == "practice":
            return ["job_shadowing", "internal_training", "portfolio_project"]
        if action == "certification_renewal":
            return ["license_exam", "document_renewal", "practical_assessment"]
        if action == "confirmation":
            return ["employer_confirmation", "test_verification", "portfolio_evidence"]
        return [f"maintain_{competency_name}"]


class SkillGapService:
    def __init__(
        self,
        competency_service: CompetencyIntelligenceService,
        verification_service: CompetencyVerificationService | None = None,
        vacancy_fit_service: VacancyFitService | None = None,
        career_path_service: CareerPathAnalysisService | None = None,
    ) -> None:
        self.competency_service = competency_service
        self.verification_service = verification_service or CompetencyVerificationService()
        self.vacancy_fit_service = vacancy_fit_service or VacancyFitService()
        self.career_path_service = career_path_service or CareerPathAnalysisService()

    def analyze(
        self,
        user_id: str,
        saved_requirements: list[EmployerCompetencyRequirement] | None = None,
        target_requirements: list[TargetRequirement] | None = None,
        career_goal: str = "",
        target_country: str = "",
    ) -> dict[str, Any]:
        requirements = list(saved_requirements or [])
        requirements.extend(self._materialize_target_requirements(target_requirements or []))
        user_competencies = {
            item.competency_id: item
            for item in self.competency_service.repositories.user_competencies.list()
            if item.user_id == user_id
        }
        competency_names = {item.id: item.name for item in self.competency_service.repositories.competencies.list()}

        existing = []
        missing = []
        insufficient = []
        expired = []
        gap_reports = []

        for requirement in requirements:
            competency = user_competencies.get(requirement.competency_id)
            name = competency_names.get(requirement.competency_id, requirement.competency_id)
            status = self.verification_service.verification_status(competency)
            current_level = competency.current_level if competency else 0
            gap_size = max(0, requirement.required_level - current_level)
            action = self.verification_service.required_action(competency, requirement.required_level)

            if competency and gap_size == 0 and status == "verified":
                existing.append(_competency_summary(name, competency, requirement))
                continue
            if status == "missing":
                missing.append(name)
            elif status == "expired":
                expired.append(_competency_summary(name, competency, requirement))
            elif status == "insufficiently_verified":
                insufficient.append(_competency_summary(name, competency, requirement))

            if gap_size > 0 or status != "verified":
                gap = self._persist_gap(user_id, requirement, current_level, gap_size, action, career_goal, target_country)
                gap_reports.append(
                    {
                        **gap.to_dict(),
                        "competency_name": name,
                        "importance": requirement.importance,
                        "criticality": _criticality(gap_size, requirement.importance, status),
                        "employability_now": _employability(status, gap_size, requirement.importance),
                        "needs_training": action == "training",
                        "needs_practice": action == "practice",
                        "needs_testing": action in {"confirmation", "certification_renewal"},
                        "needs_confirmation_only": action == "confirmation" and gap_size == 0,
                        "estimated_time_to_close": _estimated_time(action, gap_size),
                        "estimated_cost": _estimated_cost(action, gap_size),
                        "salary_impact": _salary_impact(requirement.importance, gap_size, status),
                        "available_vacancies_impact": _vacancy_impact(requirement.importance, gap_size, status),
                        "alternative_paths": self.career_path_service.alternatives_for_gap(name, action),
                    }
                )

        fit = self.vacancy_fit_service.fit_now(gap_reports)
        return {
            "user_id": user_id,
            "career_goal": career_goal,
            "target_country": target_country,
            "existing_competencies": existing,
            "missing_competencies": missing,
            "insufficiently_verified_competencies": insufficient,
            "expired_certificates": expired,
            "skill_gaps": gap_reports,
            "vacancy_fit": fit,
            "training_needed": any(item["needs_training"] for item in gap_reports),
            "practice_needed": any(item["needs_practice"] for item in gap_reports),
            "testing_needed": any(item["needs_testing"] for item in gap_reports),
            "confirmation_only": bool(gap_reports) and all(item["needs_confirmation_only"] for item in gap_reports),
            "alternative_paths": sorted({path for item in gap_reports for path in item["alternative_paths"]}),
        }

    def _materialize_target_requirements(self, target_requirements: list[TargetRequirement]) -> list[EmployerCompetencyRequirement]:
        materialized = []
        for target in target_requirements:
            competency = self.competency_service.get_or_create_competency(target.competency_name)
            materialized.append(
                EmployerCompetencyRequirement(
                    employer_id=target.employer_id or target.source,
                    vacancy_id=target.vacancy_id,
                    competency_id=competency.id,
                    required_level=_clamp_level(target.required_level),
                    importance=_clamp_level(target.importance),
                    metadata={"source": target.source},
                )
            )
        return materialized

    def _persist_gap(
        self,
        user_id: str,
        requirement: EmployerCompetencyRequirement,
        current_level: int,
        gap_size: int,
        action: str,
        career_goal: str,
        target_country: str,
    ) -> SkillGap:
        gap = SkillGap(
            user_id=user_id,
            competency_id=requirement.competency_id,
            current_level=current_level,
            target_level=requirement.required_level,
            gap_size=gap_size,
            priority=_priority(gap_size, requirement.importance, action),
            source=requirement.metadata.get("source", "employer_requirement"),
            metadata={
                "employer_id": requirement.employer_id,
                "vacancy_id": requirement.vacancy_id,
                "required_action": action,
                "career_goal": career_goal,
                "target_country": target_country,
            },
        )
        return self.competency_service.repositories.skill_gaps.add(gap)


def _competency_summary(name: str, competency: UserCompetency, requirement: EmployerCompetencyRequirement) -> dict[str, Any]:
    return {
        "competency_name": name,
        "current_level": competency.current_level,
        "required_level": requirement.required_level,
        "verification_status": competency.verification_status,
        "confidence_score": competency.confidence_score,
        "expiry_date": competency.expiry_date,
    }


def _criticality(gap_size: int, importance: int, status: str) -> str:
    if status == "missing" and importance >= 4:
        return "critical"
    if status == "expired" and importance >= 3:
        return "critical"
    if gap_size >= 3 or gap_size + importance >= 7:
        return "critical"
    if gap_size >= 1 or status == "insufficiently_verified":
        return "moderate"
    return "low"


def _employability(status: str, gap_size: int, importance: int) -> str:
    if status == "missing" and importance >= 4:
        return "blocked"
    if status == "expired":
        return "blocked_until_renewed"
    if gap_size >= 3:
        return "low_fit_now"
    if status == "insufficiently_verified":
        return "possible_after_confirmation"
    return "possible_now"


def _estimated_time(action: str, gap_size: int) -> str:
    if action == "confirmation":
        return "1-7 days"
    if action == "certification_renewal":
        return "2-8 weeks"
    if action == "practice":
        return f"{max(2, gap_size * 2)}-12 weeks"
    if action == "training":
        return f"{max(4, gap_size * 4)}-24 weeks"
    return "0 days"


def _estimated_cost(action: str, gap_size: int) -> str:
    if action == "confirmation":
        return "low"
    if action == "practice":
        return "low-medium"
    if action == "certification_renewal":
        return "medium"
    if action == "training":
        return "medium-high" if gap_size >= 3 else "medium"
    return "none"


def _salary_impact(importance: int, gap_size: int, status: str) -> str:
    if status in {"missing", "expired"} and importance >= 4:
        return "high_negative_until_closed"
    if gap_size >= 2:
        return "medium_negative"
    if status == "insufficiently_verified":
        return "depends_on_confirmation"
    return "low"


def _vacancy_impact(importance: int, gap_size: int, status: str) -> str:
    if status in {"missing", "expired"} and importance >= 4:
        return "many_vacancies_unavailable"
    if gap_size >= 2:
        return "some_vacancies_unavailable"
    if status == "insufficiently_verified":
        return "vacancies_need_manual_review"
    return "limited"


def _priority(gap_size: int, importance: int, action: str) -> str:
    score = gap_size + importance
    if action in {"training", "certification_renewal"}:
        score += 1
    if score >= 7:
        return "high"
    if score >= 4:
        return "medium"
    return "low"


def _is_past_date(value: str) -> bool:
    try:
        return date.fromisoformat(value[:10]) < date.today()
    except ValueError:
        return False


def _clamp_level(value: int) -> int:
    return max(0, min(5, int(value)))
