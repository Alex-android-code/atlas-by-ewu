"""Core domain models for ATLAS/EWU.

The models use country_code and config-driven fields so the platform can add
new countries without changing business logic.
"""

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4


def new_id(prefix: str) -> str:
    return f"{prefix}-{uuid4().hex[:12].upper()}"


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class UserRole(str, Enum):
    GUEST = "guest"
    CANDIDATE = "candidate"
    EMPLOYER = "employer"
    COORDINATOR = "coordinator"
    ADMIN = "admin"


class DocumentStatus(str, Enum):
    REQUIRED = "required"
    MISSING = "missing"
    SUBMITTED = "submitted"
    VERIFIED = "verified"
    REJECTED = "rejected"


class MatchStatus(str, Enum):
    SUGGESTED = "suggested"
    CONTACTED = "contacted"
    INTERVIEW = "interview"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    HIRED = "hired"


@dataclass
class SerializableModel:
    def to_dict(self) -> dict[str, Any]:
        return _json_ready(asdict(self))


def _json_ready(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, list):
        return [_json_ready(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_ready(item) for key, item in value.items()}
    return value


@dataclass
class User(SerializableModel):
    email: str
    phone: str
    role: UserRole
    preferred_language: str = "en"
    id: str = field(default_factory=lambda: new_id("USR"))
    created_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Country(SerializableModel):
    code: str
    name: str
    currency: str
    languages: list[str]
    emergency_number: str | None = None
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class Candidate(SerializableModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    country_code: str
    profession_code: str
    languages: list[str]
    years_of_experience: int = 0
    id: str = field(default_factory=lambda: new_id("CAN"))
    user_id: str | None = None
    documents: list[str] = field(default_factory=list)
    status: str = "new"
    created_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Employer(SerializableModel):
    company_name: str
    contact_email: str
    contact_phone: str
    country_code: str
    industry: str
    id: str = field(default_factory=lambda: new_id("EMP"))
    verified: bool = False
    created_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Vacancy(SerializableModel):
    employer_id: str
    title: str
    country_code: str
    profession_code: str
    salary_min: float
    salary_max: float
    currency: str
    required_languages: list[str]
    id: str = field(default_factory=lambda: new_id("VAC"))
    location: str | None = None
    required_documents: list[str] = field(default_factory=list)
    status: str = "open"
    created_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Document(SerializableModel):
    owner_id: str
    document_type: str
    country_code: str
    status: DocumentStatus = DocumentStatus.REQUIRED
    id: str = field(default_factory=lambda: new_id("DOC"))
    file_path: str | None = None
    expires_at: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Match(SerializableModel):
    candidate_id: str
    vacancy_id: str
    score: float
    reasons: list[str]
    status: MatchStatus = MatchStatus.SUGGESTED
    id: str = field(default_factory=lambda: new_id("MAT"))
    created_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ActivityEvent(SerializableModel):
    entity_type: str
    entity_id: str
    action: str
    old_value: str | None
    new_value: str | None
    note: str = ""
    actor_id: str = "system"
    id: str = field(default_factory=lambda: new_id("ACT"))
    event_id: str = field(default_factory=lambda: new_id("EVT"))
    correlation_id: str = field(default_factory=lambda: new_id("COR"))
    created_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProfessionalDNA(SerializableModel):
    user_id: str
    personal_information: dict[str, Any] = field(default_factory=dict)
    contact_information: dict[str, Any] = field(default_factory=dict)
    current_location: dict[str, Any] = field(default_factory=dict)
    relocation_preferences: dict[str, Any] = field(default_factory=dict)
    professional_summary: str = ""
    work_experience: list[dict[str, Any]] = field(default_factory=list)
    education: list[dict[str, Any]] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    languages: list[dict[str, Any]] = field(default_factory=list)
    certificates: list[dict[str, Any]] = field(default_factory=list)
    licenses: list[dict[str, Any]] = field(default_factory=list)
    salary_expectations: dict[str, Any] = field(default_factory=dict)
    preferred_roles: list[str] = field(default_factory=list)
    preferred_industries: list[str] = field(default_factory=list)
    preferred_countries: list[str] = field(default_factory=list)
    employment_format: list[str] = field(default_factory=list)
    career_goals: list[dict[str, Any]] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)
    development_areas: list[str] = field(default_factory=list)
    document_status: dict[str, Any] = field(default_factory=dict)
    profile_photo: dict[str, Any] = field(default_factory=dict)
    uploaded_cv: dict[str, Any] = field(default_factory=dict)
    agent_memory: list[str] = field(default_factory=list)
    agent_recommendations: list[str] = field(default_factory=list)
    profile_completeness: int = 0
    verification_status: str = "draft"
    id: str = field(default_factory=lambda: new_id("DNA"))
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentMemoryRecord(SerializableModel):
    user_id: str
    memory_type: str
    content: str
    source: str
    importance: int = 1
    is_active: bool = True
    id: str = field(default_factory=lambda: new_id("MEM"))
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentAction(SerializableModel):
    user_id: str
    action_type: str
    title: str
    status: str = "planned"
    requires_user_confirmation: bool = True
    id: str = field(default_factory=lambda: new_id("ACTN"))
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentRecommendation(SerializableModel):
    user_id: str
    recommendation_type: str
    title: str
    rationale: str = ""
    status: str = "new"
    id: str = field(default_factory=lambda: new_id("REC"))
    created_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CareerGoal(SerializableModel):
    user_id: str
    title: str
    target_country: str | None = None
    target_role: str | None = None
    status: str = "active"
    id: str = field(default_factory=lambda: new_id("GOAL"))
    created_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Opportunity(SerializableModel):
    user_id: str
    title: str
    opportunity_type: str
    status: str = "test_mode"
    id: str = field(default_factory=lambda: new_id("OPP"))
    created_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class UserPreference(SerializableModel):
    user_id: str
    language: str = "uk"
    communication_tone: str = "friendly_professional"
    notification_frequency: str = "important"
    search_countries: list[str] = field(default_factory=list)
    work_types: list[str] = field(default_factory=list)
    proactive_recommendations_allowed: bool = False
    agent_autonomy_level: str = "advisory"
    id: str = field(default_factory=lambda: new_id("PREF"))
    updated_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Subscription(SerializableModel):
    user_id: str
    plan: str = "start"
    status: str = "active"
    feature_flags: dict[str, bool] = field(default_factory=dict)
    id: str = field(default_factory=lambda: new_id("SUB"))
    created_at: str = field(default_factory=utc_now_iso)
    updated_at: str = field(default_factory=utc_now_iso)
    metadata: dict[str, Any] = field(default_factory=dict)
