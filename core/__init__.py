"""Core domain models and shared platform types."""

from .agent_context import AgentContext
from .languages import DEFAULT_LANGUAGE, SUPPORTED_LANGUAGES
from .language_state import UserLanguageMetadata
from .models import ActivityEvent, Candidate, Country, Document, Employer, Match, User, Vacancy
from .project_identity import ADMIN_PROJECT_METADATA, FOUNDER, PROJECT_NAME, PUBLIC_PROJECT_METADATA, SUCCESSORS
from .roles import ALL_ROLES, ROLE_ADMIN, ROLE_CANDIDATE, ROLE_COORDINATOR, ROLE_EMPLOYER, ROLE_GUEST
from .user_identity import UserProfile
from .user_profile import CandidateProfile, EmployerProfile, VacancyProfile

__all__ = [
    "AgentContext",
    "ActivityEvent",
    "ADMIN_PROJECT_METADATA",
    "ALL_ROLES",
    "Candidate",
    "CandidateProfile",
    "Country",
    "DEFAULT_LANGUAGE",
    "Document",
    "Employer",
    "EmployerProfile",
    "FOUNDER",
    "Match",
    "PROJECT_NAME",
    "PUBLIC_PROJECT_METADATA",
    "ROLE_ADMIN",
    "ROLE_CANDIDATE",
    "ROLE_COORDINATOR",
    "ROLE_EMPLOYER",
    "ROLE_GUEST",
    "SUCCESSORS",
    "SUPPORTED_LANGUAGES",
    "User",
    "UserLanguageMetadata",
    "UserProfile",
    "Vacancy",
    "VacancyProfile",
]
