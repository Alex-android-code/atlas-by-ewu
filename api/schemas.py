"""API request schemas."""

from typing import Any

from pydantic import BaseModel, Field


class CandidateCreate(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone: str
    country_code: str
    profession_code: str
    languages: list[str] = Field(default_factory=list)
    years_of_experience: int = 0
    user_id: str | None = None
    documents: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EmployerCreate(BaseModel):
    company_name: str
    contact_email: str
    contact_phone: str
    country_code: str
    industry: str
    verified: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class VacancyCreate(BaseModel):
    employer_id: str
    title: str
    country_code: str
    profession_code: str
    salary_min: float
    salary_max: float
    currency: str
    required_languages: list[str] = Field(default_factory=list)
    required_documents: list[str] = Field(default_factory=list)
    location: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class MatchRequest(BaseModel):
    minimum_score: int = 60


class StatusUpdate(BaseModel):
    status: str
    actor_id: str = "coordinator"
    note: str = ""


class VerificationUpdate(BaseModel):
    verified: bool = True
    actor_id: str = "coordinator"
    note: str = ""


class ActivityQuery(BaseModel):
    limit: int = 50


class AIChatRequest(BaseModel):
    user_id: str
    agent_type: str = "candidate"
    message: str
    request_id: str | None = None
    browser_language: str | None = None
    saved_language: str | None = None
    ui_language: str | None = None
    conversation_language: str | None = None


class AIMessageRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    language: str = "en"
    role: str = "candidate"
    current_step: str = "start"
    profile_data: dict[str, Any] = Field(default_factory=dict)
    recent_messages: list[dict[str, str]] = Field(default_factory=list)
    task: str = "ask_next_question"


class AnalyticsEventCreate(BaseModel):
    name: str
    params: dict[str, Any] = Field(default_factory=dict)
    actor_id: str = "anonymous"


class LoginRequest(BaseModel):
    password: str


class AgentOnboardingAnswer(BaseModel):
    user_id: str
    field: str
    value: Any
    language: str = "uk"


class AgentOnboardingComplete(BaseModel):
    user_id: str
