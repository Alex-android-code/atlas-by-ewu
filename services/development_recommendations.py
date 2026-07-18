"""Development recommendations that are not limited to courses."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.models import TrainingProgram, TrainingRecommendation
from database.repositories import (
    DevelopmentResourceRepository,
    PracticalAssessmentRepository,
    TrainingProgramCompetencyRepository,
    TrainingProgramRepository,
    TrainingRecommendationRepository,
)
from services.competency_intelligence import CompetencyIntelligenceService


DEVELOPMENT_METHODS = {
    "course",
    "certification",
    "license_exam",
    "practical_test",
    "internship",
    "mentorship",
    "supervised_work",
    "internal_training",
    "equipment_vendor_training",
    "technical_documentation",
    "professional_literature",
    "video_material",
    "online_program",
    "portfolio_project",
    "practical_assignment",
    "self_study",
    "existing_skill_confirmation",
    "process_change",
    "temporary_transfer",
    "shadowing",
    "job_rotation",
}

NO_MATCHING_COURSE_MESSAGE = (
    "No ready-made course was found on the market that fully matches this need."
)


@dataclass
class DevelopmentRecommendationRepositories:
    training_programs: TrainingProgramRepository
    training_program_competencies: TrainingProgramCompetencyRepository
    practical_assessments: PracticalAssessmentRepository
    development_resources: DevelopmentResourceRepository
    training_recommendations: TrainingRecommendationRepository


class DevelopmentRecommendationService:
    def __init__(
        self,
        repositories: DevelopmentRecommendationRepositories,
        competency_service: CompetencyIntelligenceService,
    ) -> None:
        self.repositories = repositories
        self.competency_service = competency_service

    def recommend_for_skill_gap(self, user_id: str, skill_gap_id: str) -> dict[str, Any]:
        gap = self.competency_service.repositories.skill_gaps.get(skill_gap_id)
        if gap is None:
            raise ValueError(f"Skill gap not found: {skill_gap_id}")
        competency = self.competency_service.repositories.competencies.get(gap.competency_id)
        competency_name = competency.name if competency else gap.competency_id
        matching_programs = self._matching_programs(gap.competency_id, gap.target_level)
        method = self._choose_method(gap.metadata.get("required_action", ""), matching_programs)
        alternatives = self._alternatives(method, has_course=bool(matching_programs))
        reason = self._reason(competency_name, gap.current_level, gap.target_level, method, matching_programs)
        recommendation = TrainingRecommendation(
            user_id=user_id,
            competency_id=gap.competency_id,
            reason=reason,
            recommended_method=method,
            current_level=gap.current_level,
            target_level=gap.target_level,
            career_goal_link=gap.metadata.get("career_goal", ""),
            vacancy_link=gap.metadata.get("vacancy_id", "") or "",
            alternatives=alternatives,
            duration=_duration_for(method, gap.gap_size),
            estimated_cost=_cost_for(method, gap.gap_size),
            expected_result=f"Reach level {gap.target_level} in {competency_name}",
            priority=gap.priority,
            confidence_score=_confidence_for(method, matching_programs),
            sources=["skill_gap", "competency_requirement"],
            explanation=_explanation(method, matching_programs),
            metadata={
                "skill_gap_id": skill_gap_id,
                "matching_training_program_ids": [program.id for program in matching_programs],
                "no_matching_course_message": "" if matching_programs else NO_MATCHING_COURSE_MESSAGE,
            },
        )
        saved = self.repositories.training_recommendations.add(recommendation)
        return {"recommendation": saved.to_dict(), "matching_programs": [program.to_dict() for program in matching_programs]}

    def _matching_programs(self, competency_id: str, target_level: int) -> list[TrainingProgram]:
        program_ids = {
            item.training_program_id
            for item in self.repositories.training_program_competencies.list()
            if item.competency_id == competency_id and item.target_level >= target_level
        }
        return [program for program in self.repositories.training_programs.list() if program.id in program_ids]

    @staticmethod
    def _choose_method(required_action: str, matching_programs: list[TrainingProgram]) -> str:
        if matching_programs:
            return matching_programs[0].development_method
        if required_action == "confirmation":
            return "existing_skill_confirmation"
        if required_action == "certification_renewal":
            return "license_exam"
        if required_action == "practice":
            return "supervised_work"
        if required_action == "training":
            return "mentorship"
        return "self_study"

    @staticmethod
    def _alternatives(method: str, has_course: bool) -> list[str]:
        alternatives = {
            "course": ["mentorship", "practical_assignment", "portfolio_project"],
            "mentorship": ["supervised_work", "self_study", "practical_assignment"],
            "supervised_work": ["shadowing", "job_rotation", "practical_test"],
            "license_exam": ["certification", "practical_assessment", "technical_documentation"],
            "existing_skill_confirmation": ["employer_confirmation", "portfolio_evidence", "test_verification"],
            "self_study": ["professional_literature", "video_material", "online_program"],
        }.get(method, ["mentorship", "self_study", "practical_assignment"])
        if not has_course and "course" in alternatives:
            alternatives.remove("course")
        return alternatives

    @staticmethod
    def _reason(competency_name: str, current_level: int, target_level: int, method: str, programs: list[TrainingProgram]) -> str:
        if programs:
            return f"{competency_name} needs to move from level {current_level} to {target_level}; a matching program exists."
        return (
            f"{competency_name} needs to move from level {current_level} to {target_level}; "
            "no fully matching ready-made course is available, so an alternative development path is recommended."
        )


def _duration_for(method: str, gap_size: int) -> str:
    if method == "existing_skill_confirmation":
        return "1-7 days"
    if method in {"license_exam", "certification"}:
        return "2-8 weeks"
    if method in {"supervised_work", "mentorship", "shadowing", "job_rotation"}:
        return f"{max(2, gap_size * 2)}-12 weeks"
    return f"{max(2, gap_size * 3)}-16 weeks"


def _cost_for(method: str, gap_size: int) -> str:
    if method in {"existing_skill_confirmation", "self_study", "shadowing"}:
        return "low"
    if method in {"supervised_work", "mentorship", "practical_assignment"}:
        return "low-medium"
    return "medium-high" if gap_size >= 3 else "medium"


def _confidence_for(method: str, programs: list[TrainingProgram]) -> float:
    if programs:
        return 0.75
    if method in {"existing_skill_confirmation", "supervised_work", "mentorship"}:
        return 0.65
    return 0.55


def _explanation(method: str, programs: list[TrainingProgram]) -> str:
    if programs:
        return "Recommended because a matching development program covers the target competency level."
    return (
        f"Recommended method: {method}. Partner status or provider availability is not used as automatic ranking proof."
    )
