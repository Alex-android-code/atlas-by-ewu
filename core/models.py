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
