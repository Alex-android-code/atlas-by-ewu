import tempfile
import unittest
from pathlib import Path

from database.json_database import JsonDatabase
from database.repositories import (
    CompetencyRepository,
    CorporateDepartmentRepository,
    CorporateEmployeeProfileRepository,
    CorporatePositionRepository,
    CorporateRecommendationRepository,
    DevelopmentPlanRepository,
    DevelopmentPlanStepRepository,
    EmployerCompetencyRequirementRepository,
    SkillGapRepository,
    UserCompetencyRepository,
    WorkforceCompetencyGapRepository,
    WorkforceDemandForecastRepository,
)
from services.competency_intelligence import CompetencyIntelligenceRepositories, CompetencyIntelligenceService
from services.corporate_ai import (
    FORBIDDEN_AUTOMATIC_WORKFORCE_ACTIONS,
    CorporateAIAgentService,
    CorporateAIRepositories,
    RetentionRiskService,
    TrainVsHireService,
)


class CorporateAIAgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        database = JsonDatabase(Path(self.tmpdir.name) / "db")
        self.competency_service = CompetencyIntelligenceService(
            CompetencyIntelligenceRepositories(
                competencies=CompetencyRepository(database),
                user_competencies=UserCompetencyRepository(database),
                employer_requirements=EmployerCompetencyRequirementRepository(database),
                skill_gaps=SkillGapRepository(database),
                development_plans=DevelopmentPlanRepository(database),
                development_plan_steps=DevelopmentPlanStepRepository(database),
            )
        )
        self.repositories = CorporateAIRepositories(
            departments=CorporateDepartmentRepository(database),
            positions=CorporatePositionRepository(database),
            employees=CorporateEmployeeProfileRepository(database),
            employer_requirements=EmployerCompetencyRequirementRepository(database),
            user_competencies=UserCompetencyRepository(database),
            workforce_gaps=WorkforceCompetencyGapRepository(database),
            forecasts=WorkforceDemandForecastRepository(database),
            recommendations=CorporateRecommendationRepository(database),
        )
        self.service = CorporateAIAgentService(self.repositories)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_analyze_company_reports_structure_and_headcount_forecast(self):
        department = self.service.add_department("emp-1", "Production")
        position = self.service.add_position(
            "emp-1",
            "Shift Lead",
            department_id=department.id,
            headcount_required=2,
            role_functions=["coordinate shift"],
        )
        self.service.add_employee("emp-1", "user-1", position_id=position.id, department_id=department.id)

        result = self.service.analyze_company("emp-1", horizon_months=6)

        self.assertEqual(result["workforce"]["metrics"]["department_count"], 1)
        self.assertEqual(result["forecast"]["required_positions"][0]["missing_headcount"], 1)
        self.assertTrue(result["safety"]["advisory_only"])

    def test_workforce_gap_generates_train_or_hire_recommendation(self):
        self.service.add_employee("emp-1", "user-1")
        requirement = self.competency_service.add_employer_requirement(
            employer_id="emp-1",
            competency_name="safety leadership",
            required_level=4,
            importance=4,
        )

        result = self.service.analyze_company("emp-1")

        self.assertEqual(result["workforce_gaps"][0]["competency_id"], requirement.competency_id)
        self.assertEqual(result["recommendations"][0]["recommendation_type"], "hire")
        self.assertTrue(result["recommendations"][0]["requires_human_decision"])
        self.assertEqual(
            result["recommendations"][0]["forbidden_automatic_actions"],
            FORBIDDEN_AUTOMATIC_WORKFORCE_ACTIONS,
        )

    def test_verified_employee_competency_reduces_workforce_gap(self):
        self.service.add_employee("emp-1", "user-1")
        self.competency_service.add_user_competency(
            user_id="user-1",
            competency_name="quality control",
            current_level=5,
            source="employer_verified",
        )
        self.competency_service.add_employer_requirement(
            employer_id="emp-1",
            competency_name="quality control",
            required_level=4,
            importance=1,
        )

        result = self.service.analyze_company("emp-1")

        self.assertEqual(result["workforce_gaps"], [])
        self.assertEqual(result["recommendations"], [])

    def test_train_vs_hire_service_uses_deficit_size(self):
        service = TrainVsHireService()

        self.assertEqual(service.recommend(_gap(current=0, required=1)), "train")
        self.assertEqual(service.recommend(_gap(current=0, required=3)), "train_and_hire")
        self.assertEqual(service.recommend(_gap(current=0, required=5)), "hire")

    def test_retention_risk_is_advisory(self):
        employee = self.service.add_employee(
            "emp-1",
            "user-1",
            turnover_risk_factors=["overload", "night_shifts", "commute"],
        )

        risk = RetentionRiskService().assess(employee)

        self.assertEqual(risk["risk_level"], "high")
        self.assertEqual(risk["factors"], ["overload", "night_shifts", "commute"])


def _gap(current: float, required: float):
    from core.models import WorkforceCompetencyGap

    return WorkforceCompetencyGap(
        employer_id="emp-1",
        competency_id="COMP-1",
        current_coverage=current,
        required_coverage=required,
    )


if __name__ == "__main__":
    unittest.main()
