"""Repository interfaces and JSON-backed MVP repositories."""

from dataclasses import fields
from typing import Any, Generic, Protocol, TypeVar

from core.models import (
    ActivityEvent,
    AgentAction,
    AgentCollaborationAuditEvent,
    AgentCollaborationProposal,
    AgentConsentGrant,
    AgentMemoryRecord,
    AgentRecommendation,
    Candidate,
    CareerGoal,
    Competency,
    CompetencyAssessment,
    CompetencyCategory,
    CompetencyConfidenceHistory,
    CompetencyEvidence,
    CompetencyRelationship,
    ConsentRecord,
    CorporateDepartment,
    CorporateEmployeeProfile,
    CorporatePosition,
    CorporateRecommendation,
    DataSubjectRequest,
    DevelopmentPlan,
    DevelopmentPlanStep,
    DevelopmentResource,
    Document,
    DynamicInterviewSession,
    Employer,
    EmployerCompetencyRequirement,
    Match,
    Opportunity,
    ProfessionCompetencyModel,
    ProfessionProfile,
    ProfessionalDNA,
    Certification,
    InternalTrainingProgram,
    MentorshipProgram,
    PracticalAssessment,
    Subscription,
    SkillGap,
    TrainingProgram,
    TrainingProgramCompetency,
    TrainingProvider,
    TrainingRecommendation,
    User,
    UpskillingOpportunity,
    UserCompetency,
    UserPreference,
    Vacancy,
    WorkforceDemandForecast,
    WorkforceCompetencyGap,
)
from database.json_database import JsonDatabase

ModelT = TypeVar("ModelT")


class Repository(Protocol[ModelT]):
    def add(self, item: ModelT) -> ModelT:
        ...

    def get(self, item_id: str) -> ModelT | None:
        ...

    def list(self) -> list[ModelT]:
        ...


class JsonRepository(Generic[ModelT]):
    collection: str
    model_class: type[ModelT]

    def __init__(self, database: JsonDatabase) -> None:
        self.database = database

    def add(self, item: ModelT) -> ModelT:
        self.database.insert(self.collection, self._item_id(item), self._to_dict(item))
        return item

    def update(self, item: ModelT) -> ModelT:
        self.database.update(self.collection, self._item_id(item), self._to_dict(item))
        return item

    def get(self, item_id: str) -> ModelT | None:
        data = self.database.get(self.collection, item_id)
        if data is None:
            return None
        return self._from_dict(data)

    def list(self) -> list[ModelT]:
        return [self._from_dict(item) for item in self.database.list(self.collection)]

    @staticmethod
    def _item_id(item: ModelT) -> str:
        return str(getattr(item, "id"))

    @staticmethod
    def _to_dict(item: ModelT) -> dict[str, Any]:
        to_dict = getattr(item, "to_dict", None)
        if callable(to_dict):
            return to_dict()
        raise TypeError(f"{type(item).__name__} must provide to_dict()")

    def _from_dict(self, data: dict[str, Any]) -> ModelT:
        allowed = {field.name for field in fields(self.model_class)}
        cleaned = {key: value for key, value in data.items() if key in allowed}
        return self.model_class(**cleaned)


class CandidateRepository(JsonRepository[Candidate]):
    collection = "candidates"
    model_class = Candidate


class UserRepository(JsonRepository[User]):
    collection = "users"
    model_class = User


class EmployerRepository(JsonRepository[Employer]):
    collection = "employers"
    model_class = Employer


class VacancyRepository(JsonRepository[Vacancy]):
    collection = "vacancies"
    model_class = Vacancy


class MatchRepository(JsonRepository[Match]):
    collection = "matches"
    model_class = Match


class DocumentRepository(JsonRepository[Document]):
    collection = "documents"
    model_class = Document


class ActivityRepository(JsonRepository[ActivityEvent]):
    collection = "activity"
    model_class = ActivityEvent


class ProfessionalDNARepository(JsonRepository[ProfessionalDNA]):
    collection = "professional_profiles"
    model_class = ProfessionalDNA


class AgentMemoryRepository(JsonRepository[AgentMemoryRecord]):
    collection = "agent_memories"
    model_class = AgentMemoryRecord


class AgentActionRepository(JsonRepository[AgentAction]):
    collection = "agent_actions"
    model_class = AgentAction


class AgentRecommendationRepository(JsonRepository[AgentRecommendation]):
    collection = "agent_recommendations"
    model_class = AgentRecommendation


class CareerGoalRepository(JsonRepository[CareerGoal]):
    collection = "career_goals"
    model_class = CareerGoal


class OpportunityRepository(JsonRepository[Opportunity]):
    collection = "opportunities"
    model_class = Opportunity


class UserPreferenceRepository(JsonRepository[UserPreference]):
    collection = "user_preferences"
    model_class = UserPreference


class ConsentRepository(JsonRepository[ConsentRecord]):
    collection = "consents"
    model_class = ConsentRecord


class DataSubjectRequestRepository(JsonRepository[DataSubjectRequest]):
    collection = "data_subject_requests"
    model_class = DataSubjectRequest


class SubscriptionRepository(JsonRepository[Subscription]):
    collection = "subscriptions"
    model_class = Subscription


class CompetencyCategoryRepository(JsonRepository[CompetencyCategory]):
    collection = "competency_categories"
    model_class = CompetencyCategory


class CompetencyRepository(JsonRepository[Competency]):
    collection = "competencies"
    model_class = Competency


class CompetencyRelationshipRepository(JsonRepository[CompetencyRelationship]):
    collection = "competency_relationships"
    model_class = CompetencyRelationship


class ProfessionProfileRepository(JsonRepository[ProfessionProfile]):
    collection = "profession_profiles"
    model_class = ProfessionProfile


class ProfessionCompetencyModelRepository(JsonRepository[ProfessionCompetencyModel]):
    collection = "profession_competency_models"
    model_class = ProfessionCompetencyModel


class UserCompetencyRepository(JsonRepository[UserCompetency]):
    collection = "user_competencies"
    model_class = UserCompetency


class CompetencyEvidenceRepository(JsonRepository[CompetencyEvidence]):
    collection = "competency_evidence"
    model_class = CompetencyEvidence


class CompetencyAssessmentRepository(JsonRepository[CompetencyAssessment]):
    collection = "competency_assessments"
    model_class = CompetencyAssessment


class CompetencyConfidenceHistoryRepository(JsonRepository[CompetencyConfidenceHistory]):
    collection = "competency_confidence_history"
    model_class = CompetencyConfidenceHistory


class SkillGapRepository(JsonRepository[SkillGap]):
    collection = "skill_gaps"
    model_class = SkillGap


class DevelopmentPlanRepository(JsonRepository[DevelopmentPlan]):
    collection = "development_plans"
    model_class = DevelopmentPlan


class DevelopmentPlanStepRepository(JsonRepository[DevelopmentPlanStep]):
    collection = "development_plan_steps"
    model_class = DevelopmentPlanStep


class EmployerCompetencyRequirementRepository(JsonRepository[EmployerCompetencyRequirement]):
    collection = "employer_competency_requirements"
    model_class = EmployerCompetencyRequirement


class WorkforceCompetencyGapRepository(JsonRepository[WorkforceCompetencyGap]):
    collection = "workforce_competency_gaps"
    model_class = WorkforceCompetencyGap


class UpskillingOpportunityRepository(JsonRepository[UpskillingOpportunity]):
    collection = "upskilling_opportunities"
    model_class = UpskillingOpportunity


class DynamicInterviewSessionRepository(JsonRepository[DynamicInterviewSession]):
    collection = "dynamic_interview_sessions"
    model_class = DynamicInterviewSession


class TrainingProviderRepository(JsonRepository[TrainingProvider]):
    collection = "training_providers"
    model_class = TrainingProvider


class TrainingProgramRepository(JsonRepository[TrainingProgram]):
    collection = "training_programs"
    model_class = TrainingProgram


class TrainingProgramCompetencyRepository(JsonRepository[TrainingProgramCompetency]):
    collection = "training_program_competencies"
    model_class = TrainingProgramCompetency


class CertificationRepository(JsonRepository[Certification]):
    collection = "certifications"
    model_class = Certification


class MentorshipProgramRepository(JsonRepository[MentorshipProgram]):
    collection = "mentorship_programs"
    model_class = MentorshipProgram


class InternalTrainingProgramRepository(JsonRepository[InternalTrainingProgram]):
    collection = "internal_training_programs"
    model_class = InternalTrainingProgram


class PracticalAssessmentRepository(JsonRepository[PracticalAssessment]):
    collection = "practical_assessments"
    model_class = PracticalAssessment


class DevelopmentResourceRepository(JsonRepository[DevelopmentResource]):
    collection = "development_resources"
    model_class = DevelopmentResource


class TrainingRecommendationRepository(JsonRepository[TrainingRecommendation]):
    collection = "training_recommendations"
    model_class = TrainingRecommendation


class CorporateDepartmentRepository(JsonRepository[CorporateDepartment]):
    collection = "corporate_departments"
    model_class = CorporateDepartment


class CorporatePositionRepository(JsonRepository[CorporatePosition]):
    collection = "corporate_positions"
    model_class = CorporatePosition


class CorporateEmployeeProfileRepository(JsonRepository[CorporateEmployeeProfile]):
    collection = "corporate_employee_profiles"
    model_class = CorporateEmployeeProfile


class WorkforceDemandForecastRepository(JsonRepository[WorkforceDemandForecast]):
    collection = "workforce_demand_forecasts"
    model_class = WorkforceDemandForecast


class CorporateRecommendationRepository(JsonRepository[CorporateRecommendation]):
    collection = "corporate_recommendations"
    model_class = CorporateRecommendation


class AgentCollaborationProposalRepository(JsonRepository[AgentCollaborationProposal]):
    collection = "agent_collaboration_proposals"
    model_class = AgentCollaborationProposal


class AgentConsentGrantRepository(JsonRepository[AgentConsentGrant]):
    collection = "agent_consent_grants"
    model_class = AgentConsentGrant


class AgentCollaborationAuditEventRepository(JsonRepository[AgentCollaborationAuditEvent]):
    collection = "agent_collaboration_audit_events"
    model_class = AgentCollaborationAuditEvent
