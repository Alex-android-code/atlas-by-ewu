"""API dependency builders."""

from functools import lru_cache

from crm.crm_service import CrmService
from database.json_database import JsonDatabase
from database.repositories import (
    AgentActionRepository,
    AgentCollaborationAuditEventRepository,
    AgentCollaborationProposalRepository,
    AgentConsentGrantRepository,
    AgentMemoryRepository,
    AgentRecommendationRepository,
    CandidateRepository,
    ActivityRepository,
    CareerGoalRepository,
    CompetencyRepository,
    ConsentRepository,
    CorporateDepartmentRepository,
    CorporateEmployeeProfileRepository,
    CorporatePositionRepository,
    CorporateRecommendationRepository,
    DataSubjectRequestRepository,
    CustomerSubscriptionRepository,
    DevelopmentPlanRepository,
    DevelopmentPlanStepRepository,
    DevelopmentResourceRepository,
    DocumentRepository,
    DynamicInterviewSessionRepository,
    EmployerRepository,
    EmployerCompetencyRequirementRepository,
    MatchRepository,
    OpportunityRepository,
    PracticalAssessmentRepository,
    PlanFeatureRepository,
    ProfessionalDNARepository,
    SubscriptionRepository,
    SubscriptionFeatureRepository,
    SubscriptionPlanRepository,
    SkillGapRepository,
    TrainingProgramCompetencyRepository,
    TrainingProgramRepository,
    TrainingRecommendationRepository,
    UpskillingOpportunityRepository,
    UserRepository,
    UserCompetencyRepository,
    UserPreferenceRepository,
    VacancyRepository,
    WorkforceCompetencyGapRepository,
    WorkforceDemandForecastRepository,
)
from memory.memory_store import JsonMemoryStore
from services.agent_profile_service import AgentProfileService
from services.agent_collaboration import AgentCollaborationRepositories, AgentCollaborationService
from services.competency_intelligence import CompetencyIntelligenceRepositories, CompetencyIntelligenceService
from services.country_config_loader import CountryConfigLoader
from services.corporate_ai import CorporateAIAgentService, CorporateAIRepositories
from services.development_recommendations import (
    DevelopmentRecommendationRepositories,
    DevelopmentRecommendationService,
)
from services.dynamic_interview import DynamicInterviewService
from services.entitlements import EntitlementRepositories, EntitlementService
from services.rodo_service import RodoService
from services.skill_gap_analysis import SkillGapService
from services.product_architecture import ProductArchitectureService
from workflows.operations_workflow import OperationsWorkflow


@lru_cache(maxsize=1)
def get_memory_store() -> JsonMemoryStore:
    return JsonMemoryStore()


@lru_cache(maxsize=1)
def get_database() -> JsonDatabase:
    return JsonDatabase()


def get_crm_service() -> CrmService:
    database = get_database()
    return CrmService(
        candidates=CandidateRepository(database),
        employers=EmployerRepository(database),
        vacancies=VacancyRepository(database),
        matches=MatchRepository(database),
        documents=DocumentRepository(database),
        activity=ActivityRepository(database),
        memory_store=get_memory_store(),
    )


def get_operations_workflow() -> OperationsWorkflow:
    return OperationsWorkflow(
        crm=get_crm_service(),
        memory_store=get_memory_store(),
        country_loader=CountryConfigLoader(),
    )


def get_agent_profile_service() -> AgentProfileService:
    database = get_database()
    return AgentProfileService(
        profiles=ProfessionalDNARepository(database),
        memories=AgentMemoryRepository(database),
        actions=AgentActionRepository(database),
        recommendations=AgentRecommendationRepository(database),
        goals=CareerGoalRepository(database),
        preferences=UserPreferenceRepository(database),
        subscriptions=SubscriptionRepository(database),
    )


def get_rodo_service() -> RodoService:
    database = get_database()
    return RodoService(
        consents=ConsentRepository(database),
        data_subject_requests=DataSubjectRequestRepository(database),
        candidates=CandidateRepository(database),
        employers=EmployerRepository(database),
        users=UserRepository(database),
    )


@lru_cache(maxsize=1)
def get_product_architecture_service() -> ProductArchitectureService:
    return ProductArchitectureService()


def get_competency_intelligence_service() -> CompetencyIntelligenceService:
    database = get_database()
    return CompetencyIntelligenceService(
        CompetencyIntelligenceRepositories(
            competencies=CompetencyRepository(database),
            user_competencies=UserCompetencyRepository(database),
            employer_requirements=EmployerCompetencyRequirementRepository(database),
            skill_gaps=SkillGapRepository(database),
            development_plans=DevelopmentPlanRepository(database),
            development_plan_steps=DevelopmentPlanStepRepository(database),
        )
    )


def get_dynamic_interview_service() -> DynamicInterviewService:
    return DynamicInterviewService(
        sessions=DynamicInterviewSessionRepository(get_database()),
        competency_service=get_competency_intelligence_service(),
    )


def get_skill_gap_service() -> SkillGapService:
    return SkillGapService(competency_service=get_competency_intelligence_service())


def get_development_recommendation_service() -> DevelopmentRecommendationService:
    database = get_database()
    return DevelopmentRecommendationService(
        repositories=DevelopmentRecommendationRepositories(
            training_programs=TrainingProgramRepository(database),
            training_program_competencies=TrainingProgramCompetencyRepository(database),
            practical_assessments=PracticalAssessmentRepository(database),
            development_resources=DevelopmentResourceRepository(database),
            training_recommendations=TrainingRecommendationRepository(database),
        ),
        competency_service=get_competency_intelligence_service(),
    )


def get_corporate_ai_agent_service() -> CorporateAIAgentService:
    database = get_database()
    return CorporateAIAgentService(
        CorporateAIRepositories(
            departments=CorporateDepartmentRepository(database),
            positions=CorporatePositionRepository(database),
            employees=CorporateEmployeeProfileRepository(database),
            employer_requirements=EmployerCompetencyRequirementRepository(database),
            user_competencies=UserCompetencyRepository(database),
            workforce_gaps=WorkforceCompetencyGapRepository(database),
            forecasts=WorkforceDemandForecastRepository(database),
            recommendations=CorporateRecommendationRepository(database),
        )
    )


def get_agent_collaboration_service() -> AgentCollaborationService:
    database = get_database()
    return AgentCollaborationService(
        AgentCollaborationRepositories(
            proposals=AgentCollaborationProposalRepository(database),
            grants=AgentConsentGrantRepository(database),
            audit_events=AgentCollaborationAuditEventRepository(database),
            consents=ConsentRepository(database),
            upskilling_opportunities=UpskillingOpportunityRepository(database),
        )
    )


def get_entitlement_service() -> EntitlementService:
    database = get_database()
    return EntitlementService(
        EntitlementRepositories(
            plans=SubscriptionPlanRepository(database),
            features=SubscriptionFeatureRepository(database),
            plan_features=PlanFeatureRepository(database),
            customer_subscriptions=CustomerSubscriptionRepository(database),
        )
    )
