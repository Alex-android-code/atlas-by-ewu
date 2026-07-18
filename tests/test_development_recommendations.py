import tempfile
import unittest
from pathlib import Path

from core.models import TrainingProgram, TrainingProgramCompetency
from database.json_database import JsonDatabase
from database.repositories import (
    CompetencyRepository,
    DevelopmentPlanRepository,
    DevelopmentPlanStepRepository,
    DevelopmentResourceRepository,
    EmployerCompetencyRequirementRepository,
    PracticalAssessmentRepository,
    SkillGapRepository,
    TrainingProgramCompetencyRepository,
    TrainingProgramRepository,
    TrainingRecommendationRepository,
    UserCompetencyRepository,
)
from services.competency_intelligence import CompetencyIntelligenceRepositories, CompetencyIntelligenceService
from services.development_recommendations import (
    NO_MATCHING_COURSE_MESSAGE,
    DevelopmentRecommendationRepositories,
    DevelopmentRecommendationService,
)
from services.skill_gap_analysis import SkillGapService, TargetRequirement


class DevelopmentRecommendationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        database = JsonDatabase(Path(self.tmpdir.name) / "db")
        self.training_programs = TrainingProgramRepository(database)
        self.training_program_competencies = TrainingProgramCompetencyRepository(database)
        self.recommendations = TrainingRecommendationRepository(database)
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
        self.skill_gap_service = SkillGapService(self.competency_service)
        self.service = DevelopmentRecommendationService(
            DevelopmentRecommendationRepositories(
                training_programs=self.training_programs,
                training_program_competencies=self.training_program_competencies,
                practical_assessments=PracticalAssessmentRepository(database),
                development_resources=DevelopmentResourceRepository(database),
                training_recommendations=self.recommendations,
            ),
            competency_service=self.competency_service,
        )

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_recommends_matching_course_when_program_exists(self):
        gap = self._create_gap("quality control", required_level=3)
        program = self.training_programs.add(
            TrainingProgram(provider_id="provider-1", title="Quality Control Basics", development_method="course")
        )
        self.training_program_competencies.add(
            TrainingProgramCompetency(training_program_id=program.id, competency_id=gap.competency_id, target_level=3)
        )

        result = self.service.recommend_for_skill_gap("user-1", gap.id)

        self.assertEqual(result["recommendation"]["recommended_method"], "course")
        self.assertEqual(len(result["matching_programs"]), 1)

    def test_recommends_alternative_plan_when_no_course_matches(self):
        gap = self._create_gap("safety leadership", required_level=5)

        result = self.service.recommend_for_skill_gap("user-1", gap.id)

        self.assertEqual(result["recommendation"]["recommended_method"], "mentorship")
        self.assertIn("supervised_work", result["recommendation"]["alternatives"])
        self.assertEqual(result["recommendation"]["metadata"]["no_matching_course_message"], NO_MATCHING_COURSE_MESSAGE)

    def test_confirmation_gap_recommends_existing_skill_confirmation(self):
        self.competency_service.add_user_competency(
            user_id="user-1",
            competency_name="inventory control",
            current_level=4,
            source="self_declared",
        )
        result = self.skill_gap_service.analyze(
            user_id="user-1",
            target_requirements=[TargetRequirement("inventory control", required_level=4, importance=3)],
        )

        recommendation = self.service.recommend_for_skill_gap("user-1", result["skill_gaps"][0]["id"])

        self.assertEqual(recommendation["recommendation"]["recommended_method"], "existing_skill_confirmation")
        self.assertIn("portfolio_evidence", recommendation["recommendation"]["alternatives"])

    def test_program_partner_status_does_not_automatically_raise_confidence(self):
        gap = self._create_gap("technical documentation", required_level=2)
        program = self.training_programs.add(
            TrainingProgram(
                provider_id="partner-provider",
                title="Documentation Reading",
                development_method="course",
                metadata={"provider_partner_status": "strategic_partner"},
            )
        )
        self.training_program_competencies.add(
            TrainingProgramCompetency(training_program_id=program.id, competency_id=gap.competency_id, target_level=2)
        )

        result = self.service.recommend_for_skill_gap("user-1", gap.id)

        self.assertEqual(result["recommendation"]["confidence_score"], 0.75)

    def _create_gap(self, competency_name: str, required_level: int):
        result = self.skill_gap_service.analyze(
            user_id="user-1",
            target_requirements=[TargetRequirement(competency_name, required_level=required_level, importance=4)],
        )
        return self.competency_service.repositories.skill_gaps.get(result["skill_gaps"][0]["id"])


if __name__ == "__main__":
    unittest.main()
