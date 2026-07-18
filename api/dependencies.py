"""API dependency builders."""

from functools import lru_cache

from crm.crm_service import CrmService
from database.json_database import JsonDatabase
from database.repositories import (
    AgentActionRepository,
    AgentMemoryRepository,
    AgentRecommendationRepository,
    CandidateRepository,
    ActivityRepository,
    CareerGoalRepository,
    CompetencyRepository,
    ConsentRepository,
    DataSubjectRequestRepository,
    DevelopmentPlanRepository,
    DevelopmentPlanStepRepository,
    DocumentRepository,
    DynamicInterviewSessionRepository,
    EmployerRepository,
    EmployerCompetencyRequirementRepository,
    MatchRepository,
    OpportunityRepository,
    ProfessionalDNARepository,
    SubscriptionRepository,
    SkillGapRepository,
    UserRepository,
    UserCompetencyRepository,
    UserPreferenceRepository,
    VacancyRepository,
)
from memory.memory_store import JsonMemoryStore
from services.agent_profile_service import AgentProfileService
from services.competency_intelligence import CompetencyIntelligenceRepositories, CompetencyIntelligenceService
from services.country_config_loader import CountryConfigLoader
from services.dynamic_interview import DynamicInterviewService
from services.rodo_service import RodoService
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
