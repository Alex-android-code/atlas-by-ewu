"""Universal competency intelligence foundation for ATLAS."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from core.models import (
    Competency,
    DevelopmentPlan,
    DevelopmentPlanStep,
    EmployerCompetencyRequirement,
    SkillGap,
    UserCompetency,
    utc_now_iso,
)
from database.repositories import (
    CompetencyRepository,
    DevelopmentPlanRepository,
    DevelopmentPlanStepRepository,
    EmployerCompetencyRequirementRepository,
    SkillGapRepository,
    UserCompetencyRepository,
)


COMPETENCY_SOURCES = {
    "self_declared",
    "ai_inferred",
    "document_extracted",
    "document_verified",
    "employer_verified",
    "test_verified",
    "portfolio_verified",
    "training_verified",
    "certification_verified",
    "expired",
    "disputed",
    "rejected",
}
VERIFIED_SOURCES = {
    "document_verified",
    "employer_verified",
    "test_verified",
    "portfolio_verified",
    "training_verified",
    "certification_verified",
}


@dataclass
class CompetencyIntelligenceRepositories:
    competencies: CompetencyRepository
    user_competencies: UserCompetencyRepository
    employer_requirements: EmployerCompetencyRequirementRepository
    skill_gaps: SkillGapRepository
    development_plans: DevelopmentPlanRepository
    development_plan_steps: DevelopmentPlanStepRepository


class CompetencyIntelligenceService:
    def __init__(self, repositories: CompetencyIntelligenceRepositories) -> None:
        self.repositories = repositories

    def get_or_create_competency(self, name: str, category_id: str | None = None) -> Competency:
        normalized = _normalize_competency_name(name)
        for competency in self.repositories.competencies.list():
            names = {competency.name.lower(), *[alias.lower() for alias in competency.aliases]}
            if normalized in names:
                return competency
        competency = Competency(name=normalized, category_id=category_id)
        return self.repositories.competencies.add(competency)

    def add_user_competency(
        self,
        user_id: str,
        competency_name: str,
        current_level: int = 1,
        target_level: int = 1,
        source: str = "self_declared",
        confidence_score: float | None = None,
        evidence_reference: str = "",
        years_of_experience: float = 0.0,
        visibility: str = "private",
    ) -> UserCompetency:
        source = _validate_source(source)
        competency = self.get_or_create_competency(competency_name)
        verified = source in VERIFIED_SOURCES
        confidence = confidence_score if confidence_score is not None else _default_confidence(source)
        user_competency = UserCompetency(
            user_id=user_id,
            competency_id=competency.id,
            current_level=_clamp_level(current_level),
            target_level=_clamp_level(target_level),
            source=source,
            confidence_score=_clamp_confidence(confidence),
            evidence_type=source,
            evidence_reference=evidence_reference,
            years_of_experience=max(0.0, years_of_experience),
            last_verified_at=utc_now_iso() if verified else None,
            verification_status="verified" if verified else "unverified",
            visibility=visibility,
        )
        return self.repositories.user_competencies.add(user_competency)

    def add_employer_requirement(
        self,
        employer_id: str,
        competency_name: str,
        required_level: int,
        vacancy_id: str | None = None,
        importance: int = 3,
    ) -> EmployerCompetencyRequirement:
        competency = self.get_or_create_competency(competency_name)
        requirement = EmployerCompetencyRequirement(
            employer_id=employer_id,
            vacancy_id=vacancy_id,
            competency_id=competency.id,
            required_level=_clamp_level(required_level),
            importance=_clamp_level(importance),
        )
        return self.repositories.employer_requirements.add(requirement)

    def analyze_skill_gaps_for_user(self, user_id: str, requirements: list[EmployerCompetencyRequirement]) -> list[SkillGap]:
        user_competencies = {
            item.competency_id: item for item in self.repositories.user_competencies.list() if item.user_id == user_id
        }
        gaps: list[SkillGap] = []
        for requirement in requirements:
            user_competency = user_competencies.get(requirement.competency_id)
            current_level = user_competency.current_level if user_competency else 0
            gap_size = max(0, requirement.required_level - current_level)
            if gap_size <= 0:
                continue
            gap = SkillGap(
                user_id=user_id,
                competency_id=requirement.competency_id,
                current_level=current_level,
                target_level=requirement.required_level,
                gap_size=gap_size,
                priority=_gap_priority(gap_size, requirement.importance),
                source="employer_requirement",
                metadata={"employer_id": requirement.employer_id, "vacancy_id": requirement.vacancy_id},
            )
            gaps.append(self.repositories.skill_gaps.add(gap))
        return gaps

    def create_development_plan_from_gaps(self, user_id: str, gaps: list[SkillGap], title: str = "Development plan") -> dict:
        plan = self.repositories.development_plans.add(DevelopmentPlan(user_id=user_id, title=title))
        steps = []
        ordered_gaps = sorted(gaps, key=lambda gap: (-_priority_weight(gap.priority), -gap.gap_size))
        competency_names = {item.id: item.name for item in self.repositories.competencies.list()}
        for index, gap in enumerate(ordered_gaps, start=1):
            competency_name = competency_names.get(gap.competency_id, gap.competency_id)
            step = DevelopmentPlanStep(
                development_plan_id=plan.id,
                competency_id=gap.competency_id,
                title=f"Improve {competency_name} from level {gap.current_level} to {gap.target_level}",
                order=index,
                metadata={"skill_gap_id": gap.id, "priority": gap.priority},
            )
            steps.append(self.repositories.development_plan_steps.add(step))
        return {"plan": plan.to_dict(), "steps": [step.to_dict() for step in steps]}

    def competency_map_for_user(self, user_id: str) -> dict[str, Any]:
        competencies = {item.id: item for item in self.repositories.competencies.list()}
        user_items = [item for item in self.repositories.user_competencies.list() if item.user_id == user_id]
        return {
            "user_id": user_id,
            "competencies": [
                {
                    **item.to_dict(),
                    "competency": competencies[item.competency_id].to_dict()
                    if item.competency_id in competencies
                    else None,
                }
                for item in user_items
            ],
            "verified_count": sum(1 for item in user_items if item.verification_status == "verified"),
            "unverified_count": sum(1 for item in user_items if item.verification_status != "verified"),
        }


def _normalize_competency_name(name: str) -> str:
    normalized = re.sub(r"\s+", " ", name.strip().lower())
    if not normalized:
        raise ValueError("Competency name is required")
    return normalized


def _validate_source(source: str) -> str:
    normalized = source.strip().lower()
    if normalized not in COMPETENCY_SOURCES:
        raise ValueError(f"Unsupported competency source: {source}")
    return normalized


def _default_confidence(source: str) -> float:
    if source == "ai_inferred":
        return 0.35
    if source == "self_declared":
        return 0.45
    if source in VERIFIED_SOURCES:
        return 0.9
    return 0.2


def _clamp_level(value: int) -> int:
    return max(0, min(5, int(value)))


def _clamp_confidence(value: float) -> float:
    return max(0.0, min(1.0, float(value)))


def _gap_priority(gap_size: int, importance: int) -> str:
    score = gap_size + importance
    if score >= 7:
        return "high"
    if score >= 4:
        return "medium"
    return "low"


def _priority_weight(priority: str) -> int:
    return {"high": 3, "medium": 2, "low": 1}.get(priority, 0)
