"""Corporate AI-agent foundation for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.models import (
    CorporateDepartment,
    CorporateEmployeeProfile,
    CorporatePosition,
    CorporateRecommendation,
    WorkforceCompetencyGap,
    WorkforceDemandForecast,
)
from database.repositories import (
    CorporateDepartmentRepository,
    CorporateEmployeeProfileRepository,
    CorporatePositionRepository,
    CorporateRecommendationRepository,
    EmployerCompetencyRequirementRepository,
    UserCompetencyRepository,
    WorkforceCompetencyGapRepository,
    WorkforceDemandForecastRepository,
)


FORBIDDEN_AUTOMATIC_WORKFORCE_ACTIONS = ["fire", "demote", "block", "reject", "discipline"]


@dataclass
class CorporateAIRepositories:
    departments: CorporateDepartmentRepository
    positions: CorporatePositionRepository
    employees: CorporateEmployeeProfileRepository
    employer_requirements: EmployerCompetencyRequirementRepository
    user_competencies: UserCompetencyRepository
    workforce_gaps: WorkforceCompetencyGapRepository
    forecasts: WorkforceDemandForecastRepository
    recommendations: CorporateRecommendationRepository


class WorkforceAnalysisService:
    def __init__(self, repositories: CorporateAIRepositories) -> None:
        self.repositories = repositories

    def analyze(self, employer_id: str) -> dict[str, Any]:
        departments = [item for item in self.repositories.departments.list() if item.employer_id == employer_id]
        positions = [item for item in self.repositories.positions.list() if item.employer_id == employer_id]
        employees = [item for item in self.repositories.employees.list() if item.employer_id == employer_id]
        requirements = [item for item in self.repositories.employer_requirements.list() if item.employer_id == employer_id]
        active_employees = [item for item in employees if item.status == "active"]
        return {
            "employer_id": employer_id,
            "departments": [item.to_dict() for item in departments],
            "positions": [item.to_dict() for item in positions],
            "employees": [item.to_dict() for item in employees],
            "metrics": {
                "department_count": len(departments),
                "position_count": len(positions),
                "active_employee_count": len(active_employees),
                "required_headcount": sum(max(0, item.headcount_required) for item in positions),
                "competency_requirement_count": len(requirements),
            },
        }


class CorporateSkillGapService:
    def __init__(self, repositories: CorporateAIRepositories) -> None:
        self.repositories = repositories

    def analyze(self, employer_id: str) -> list[WorkforceCompetencyGap]:
        requirements = [item for item in self.repositories.employer_requirements.list() if item.employer_id == employer_id]
        employees = [item for item in self.repositories.employees.list() if item.employer_id == employer_id and item.status == "active"]
        employee_ids = {item.user_id for item in employees}
        user_competencies = [
            item
            for item in self.repositories.user_competencies.list()
            if item.user_id in employee_ids and item.verification_status == "verified"
        ]
        gaps = []
        for requirement in requirements:
            matching_count = sum(
                1
                for competency in user_competencies
                if competency.competency_id == requirement.competency_id
                and competency.current_level >= requirement.required_level
            )
            required_coverage = max(1, requirement.importance)
            current_coverage = matching_count
            if current_coverage >= required_coverage:
                continue
            gap = WorkforceCompetencyGap(
                employer_id=employer_id,
                competency_id=requirement.competency_id,
                current_coverage=float(current_coverage),
                required_coverage=float(required_coverage),
                priority="high" if required_coverage - current_coverage >= 3 else "medium",
                metadata={"vacancy_id": requirement.vacancy_id, "requirement_id": requirement.id},
            )
            gaps.append(self.repositories.workforce_gaps.add(gap))
        return gaps


class WorkforceDemandForecastService:
    def __init__(self, repositories: CorporateAIRepositories) -> None:
        self.repositories = repositories

    def forecast(self, employer_id: str, horizon_months: int = 6) -> WorkforceDemandForecast:
        positions = [item for item in self.repositories.positions.list() if item.employer_id == employer_id]
        employees = [item for item in self.repositories.employees.list() if item.employer_id == employer_id and item.status == "active"]
        vacancies = []
        for position in positions:
            assigned = sum(1 for employee in employees if employee.position_id == position.id)
            missing = max(0, position.headcount_required - assigned)
            if missing:
                vacancies.append({"position_id": position.id, "title": position.title, "missing_headcount": missing})
        forecast = WorkforceDemandForecast(
            employer_id=employer_id,
            horizon_months=horizon_months,
            required_positions=vacancies,
            confidence_score=0.55,
            metadata={"method": "current_headcount_gap"},
        )
        return self.repositories.forecasts.add(forecast)


class TrainVsHireService:
    def recommend(self, gap: WorkforceCompetencyGap) -> str:
        deficit = gap.required_coverage - gap.current_coverage
        if deficit <= 1:
            return "train"
        if deficit <= 3:
            return "train_and_hire"
        return "hire"


class PromotionPotentialService:
    def evaluate(self, employee: CorporateEmployeeProfile, matched_competency_count: int) -> str:
        if employee.status != "active":
            return "not_applicable"
        if matched_competency_count >= 3:
            return "review_for_promotion_or_internal_move"
        if matched_competency_count >= 1:
            return "review_after_development"
        return "no_signal_yet"


class RetentionRiskService:
    def assess(self, employee: CorporateEmployeeProfile) -> dict[str, Any]:
        factors = employee.turnover_risk_factors
        if len(factors) >= 3:
            level = "high"
        elif factors:
            level = "medium"
        else:
            level = "low"
        return {"employee_id": employee.id, "user_id": employee.user_id, "risk_level": level, "factors": factors}


class WorkforceDevelopmentPlanService:
    def recommendations_for_gaps(
        self,
        employer_id: str,
        gaps: list[WorkforceCompetencyGap],
        train_vs_hire: TrainVsHireService,
    ) -> list[CorporateRecommendation]:
        recommendations = []
        for gap in gaps:
            action = train_vs_hire.recommend(gap)
            recommendation = CorporateRecommendation(
                employer_id=employer_id,
                recommendation_type=action,
                title=f"Workforce action for competency {gap.competency_id}: {action}",
                risk_level=gap.priority,
                confidence_score=0.6,
                requires_human_decision=True,
                forbidden_automatic_actions=FORBIDDEN_AUTOMATIC_WORKFORCE_ACTIONS,
                rationale=(
                    f"Coverage is {gap.current_coverage} of {gap.required_coverage}. "
                    "This is advisory only and requires human review."
                ),
                metadata={"workforce_gap_id": gap.id},
            )
            recommendations.append(recommendation)
        return recommendations


class CorporateAIAgentService:
    def __init__(
        self,
        repositories: CorporateAIRepositories,
        workforce_analysis: WorkforceAnalysisService | None = None,
        demand_forecast: WorkforceDemandForecastService | None = None,
        skill_gap: CorporateSkillGapService | None = None,
        train_vs_hire: TrainVsHireService | None = None,
        promotion_potential: PromotionPotentialService | None = None,
        retention_risk: RetentionRiskService | None = None,
        development_plan: WorkforceDevelopmentPlanService | None = None,
    ) -> None:
        self.repositories = repositories
        self.workforce_analysis = workforce_analysis or WorkforceAnalysisService(repositories)
        self.demand_forecast = demand_forecast or WorkforceDemandForecastService(repositories)
        self.skill_gap = skill_gap or CorporateSkillGapService(repositories)
        self.train_vs_hire = train_vs_hire or TrainVsHireService()
        self.promotion_potential = promotion_potential or PromotionPotentialService()
        self.retention_risk = retention_risk or RetentionRiskService()
        self.development_plan = development_plan or WorkforceDevelopmentPlanService()

    def add_department(self, employer_id: str, name: str, parent_department_id: str | None = None) -> CorporateDepartment:
        return self.repositories.departments.add(
            CorporateDepartment(employer_id=employer_id, name=name, parent_department_id=parent_department_id)
        )

    def add_position(
        self,
        employer_id: str,
        title: str,
        department_id: str | None = None,
        headcount_required: int = 1,
        role_functions: list[str] | None = None,
    ) -> CorporatePosition:
        return self.repositories.positions.add(
            CorporatePosition(
                employer_id=employer_id,
                title=title,
                department_id=department_id,
                headcount_required=max(0, headcount_required),
                role_functions=role_functions or [],
            )
        )

    def add_employee(
        self,
        employer_id: str,
        user_id: str,
        position_id: str | None = None,
        department_id: str | None = None,
        turnover_risk_factors: list[str] | None = None,
    ) -> CorporateEmployeeProfile:
        return self.repositories.employees.add(
            CorporateEmployeeProfile(
                employer_id=employer_id,
                user_id=user_id,
                position_id=position_id,
                department_id=department_id,
                turnover_risk_factors=turnover_risk_factors or [],
            )
        )

    def analyze_company(self, employer_id: str, horizon_months: int = 6) -> dict[str, Any]:
        workforce = self.workforce_analysis.analyze(employer_id)
        gaps = self.skill_gap.analyze(employer_id)
        forecast = self.demand_forecast.forecast(employer_id, horizon_months=horizon_months)
        recommendations = self.development_plan.recommendations_for_gaps(employer_id, gaps, self.train_vs_hire)
        saved_recommendations = [self.repositories.recommendations.add(item) for item in recommendations]
        employees = [item for item in self.repositories.employees.list() if item.employer_id == employer_id]
        retention = [self.retention_risk.assess(item) for item in employees]
        return {
            "employer_id": employer_id,
            "workforce": workforce,
            "workforce_gaps": [item.to_dict() for item in gaps],
            "forecast": forecast.to_dict(),
            "retention_risks": retention,
            "recommendations": [item.to_dict() for item in saved_recommendations],
            "safety": {
                "advisory_only": True,
                "requires_human_decision": True,
                "forbidden_automatic_actions": FORBIDDEN_AUTOMATIC_WORKFORCE_ACTIONS,
            },
        }
