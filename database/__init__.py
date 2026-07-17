"""Database adapters and repositories."""

from .json_database import JsonDatabase
from .repositories import (
    AgentActionRepository,
    AgentMemoryRepository,
    AgentRecommendationRepository,
    ActivityRepository,
    CandidateRepository,
    CareerGoalRepository,
    DocumentRepository,
    EmployerRepository,
    MatchRepository,
    OpportunityRepository,
    ProfessionalDNARepository,
    Repository,
    SubscriptionRepository,
    UserRepository,
    UserPreferenceRepository,
    VacancyRepository,
)

__all__ = [
    "CandidateRepository",
    "AgentActionRepository",
    "AgentMemoryRepository",
    "AgentRecommendationRepository",
    "ActivityRepository",
    "CareerGoalRepository",
    "DocumentRepository",
    "EmployerRepository",
    "JsonDatabase",
    "MatchRepository",
    "OpportunityRepository",
    "ProfessionalDNARepository",
    "Repository",
    "SubscriptionRepository",
    "UserRepository",
    "UserPreferenceRepository",
    "VacancyRepository",
]
