import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from database.json_database import JsonDatabase
from database.repositories import (
    CompetencyRepository,
    DevelopmentPlanRepository,
    DevelopmentPlanStepRepository,
    EmployerCompetencyRequirementRepository,
    SkillGapRepository,
    UserCompetencyRepository,
)
from services.competency_intelligence import CompetencyIntelligenceRepositories, CompetencyIntelligenceService
from services.skill_gap_analysis import SkillGapService, TargetRequirement


class SkillGapAnalysisTests(unittest.TestCase):
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
        self.service = SkillGapService(self.competency_service)

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_missing_critical_competency_blocks_fit_now(self):
        result = self.service.analyze(
            user_id="user-1",
            target_requirements=[
                TargetRequirement("safety leadership", required_level=4, importance=5, source="market_requirement")
            ],
            career_goal="team lead",
            target_country="PL",
        )

        self.assertEqual(result["missing_competencies"], ["safety leadership"])
        self.assertEqual(result["skill_gaps"][0]["criticality"], "critical")
        self.assertEqual(result["skill_gaps"][0]["employability_now"], "blocked")
        self.assertTrue(result["training_needed"])
        self.assertFalse(result["vacancy_fit"]["can_apply_now"])

    def test_insufficiently_verified_competency_requires_confirmation_only(self):
        self.competency_service.add_user_competency(
            user_id="user-1",
            competency_name="inventory control",
            current_level=4,
            source="self_declared",
        )

        result = self.service.analyze(
            user_id="user-1",
            target_requirements=[TargetRequirement("inventory control", required_level=4, importance=3)],
        )

        self.assertEqual(len(result["insufficiently_verified_competencies"]), 1)
        self.assertTrue(result["skill_gaps"][0]["needs_confirmation_only"])
        self.assertTrue(result["testing_needed"])

    def test_expired_certificate_requires_testing_or_renewal(self):
        expired_date = (date.today() - timedelta(days=1)).isoformat()
        user_competency = self.competency_service.add_user_competency(
            user_id="user-1",
            competency_name="forklift operation",
            current_level=5,
            source="certification_verified",
        )
        user_competency.expiry_date = expired_date
        self.competency_service.repositories.user_competencies.update(user_competency)

        result = self.service.analyze(
            user_id="user-1",
            target_requirements=[TargetRequirement("forklift operation", required_level=5, importance=4)],
        )

        self.assertEqual(len(result["expired_certificates"]), 1)
        self.assertEqual(result["skill_gaps"][0]["metadata"]["required_action"], "certification_renewal")
        self.assertEqual(result["skill_gaps"][0]["employability_now"], "blocked_until_renewed")

    def test_lower_level_verified_competency_needs_practice(self):
        self.competency_service.add_user_competency(
            user_id="user-1",
            competency_name="technical drawing",
            current_level=2,
            source="test_verified",
        )

        result = self.service.analyze(
            user_id="user-1",
            target_requirements=[TargetRequirement("technical drawing", required_level=4, importance=4)],
        )

        self.assertEqual(result["skill_gaps"][0]["gap_size"], 2)
        self.assertTrue(result["practice_needed"])
        self.assertIn("job_shadowing", result["alternative_paths"])

    def test_verified_competency_at_required_level_is_existing(self):
        self.competency_service.add_user_competency(
            user_id="user-1",
            competency_name="quality control",
            current_level=4,
            source="employer_verified",
        )

        result = self.service.analyze(
            user_id="user-1",
            target_requirements=[TargetRequirement("quality control", required_level=3, importance=3)],
        )

        self.assertEqual(len(result["existing_competencies"]), 1)
        self.assertEqual(result["skill_gaps"], [])
        self.assertEqual(result["vacancy_fit"]["fit"], "ready_now")


if __name__ == "__main__":
    unittest.main()
