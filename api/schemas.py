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


class ConsentCreate(BaseModel):
    subject_id: str
    language: str = "uk"
    source: str = "web"
    scopes: list[str] = Field(default_factory=list)
    accepted: bool = True


class DataSubjectRequestCreate(BaseModel):
    subject_id: str
    request_type: str
    contact: str
    language: str = "uk"
    note: str = ""


class DataSubjectRequestStatusUpdate(BaseModel):
    status: str
    note: str = ""


class UserCompetencyCreate(BaseModel):
    user_id: str
    competency_name: str
    current_level: int = Field(default=1, ge=0, le=5)
    target_level: int = Field(default=1, ge=0, le=5)
    source: str = "self_declared"
    confidence_score: float | None = Field(default=None, ge=0, le=1)
    evidence_reference: str = ""
    years_of_experience: float = Field(default=0.0, ge=0)
    visibility: str = "private"


class EmployerCompetencyRequirementCreate(BaseModel):
    employer_id: str
    competency_name: str
    required_level: int = Field(default=1, ge=0, le=5)
    vacancy_id: str | None = None
    importance: int = Field(default=3, ge=0, le=5)


class TargetCompetencyRequirement(BaseModel):
    competency_name: str
    required_level: int = Field(default=1, ge=0, le=5)
    importance: int = Field(default=3, ge=0, le=5)
    source: str = "market_requirement"
    employer_id: str | None = None
    vacancy_id: str | None = None


class SkillGapAnalysisRequest(BaseModel):
    user_id: str
    employer_id: str | None = None
    vacancy_id: str | None = None
    career_goal: str = ""
    target_country: str = ""
    target_requirements: list[TargetCompetencyRequirement] = Field(default_factory=list)


class DevelopmentPlanCreate(BaseModel):
    user_id: str
    title: str = "Development plan"
    skill_gap_ids: list[str] = Field(default_factory=list)


class DevelopmentRecommendationCreate(BaseModel):
    user_id: str
    skill_gap_id: str


class CorporateDepartmentCreate(BaseModel):
    employer_id: str
    name: str
    parent_department_id: str | None = None


class CorporatePositionCreate(BaseModel):
    employer_id: str
    title: str
    department_id: str | None = None
    headcount_required: int = Field(default=1, ge=0)
    role_functions: list[str] = Field(default_factory=list)


class CorporateEmployeeCreate(BaseModel):
    employer_id: str
    user_id: str
    position_id: str | None = None
    department_id: str | None = None
    turnover_risk_factors: list[str] = Field(default_factory=list)


class CorporateAnalysisRequest(BaseModel):
    employer_id: str
    horizon_months: int = Field(default=6, ge=1, le=60)


class AgentCollaborationProposalCreate(BaseModel):
    employer_id: str
    user_id: str
    proposal_type: str
    title: str
    data_categories: list[str] = Field(default_factory=list)
    actor_id: str = "corporate_admin"
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentCollaborationConsentGrantCreate(BaseModel):
    proposal_id: str
    user_id: str
    actor_id: str = "user"


class AgentCollaborationConsentRevoke(BaseModel):
    grant_id: str
    actor_id: str = "user"


class CustomerSubscriptionSet(BaseModel):
    customer_id: str
    customer_type: str = "user"
    plan_code: str


class EntitlementCheckRequest(BaseModel):
    customer_id: str
    customer_type: str = "user"
    feature_code: str


class DynamicInterviewStart(BaseModel):
    user_id: str
    role: str = "candidate"
    language: str = "en"


class DynamicInterviewAnswer(BaseModel):
    session_id: str
    answer: str = Field(min_length=1, max_length=4000)


class AgentOnboardingAnswer(BaseModel):
    user_id: str
    field: str
    value: Any
    language: str = "uk"


class AgentOnboardingComplete(BaseModel):
    user_id: str
