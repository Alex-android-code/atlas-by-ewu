"""Typed contracts for the ATLAS multimodel AI gateway."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


PROMPT_VERSION = "atlas-constitution-1.0"
ROUTER_VERSION = "atlas-router-1.0"


class TaskType(str, Enum):
    CHAT = "chat"
    FAQ = "faq"
    PROFILE_EXTRACTION = "profile_extraction"
    DOCUMENT_ANALYSIS = "document_analysis"
    MATCHING_PREFILTER = "matching_prefilter"
    MATCHING_FINAL = "matching_final"
    EMPLOYER_ANALYSIS = "employer_analysis"
    TRANSLATION = "translation"
    LEGAL_SENSITIVE = "legal_sensitive"
    SUMMARIZATION = "summarization"


class RiskLevel(str, Enum):
    NORMAL = "normal"
    SENSITIVE = "sensitive"
    HIGH = "high"
    URGENT = "urgent"
    EMERGENCY = "emergency"


@dataclass
class ModelResult:
    content: str
    provider: str
    model: str
    input_tokens: int | None
    output_tokens: int | None
    estimated_cost: float | None
    latency_ms: int
    cached: bool = False


@dataclass
class AIRequest:
    user_id: str
    agent_type: str
    context: dict[str, Any]
    message: str
    request_id: str = field(default_factory=lambda: uuid4().hex)
    tenant_id: str = "default"
    language: str = "en"
    task_type: TaskType = TaskType.CHAT


@dataclass
class AIResponse:
    reply: str
    action: str | None = None
    confidence: float = 0.0
    handoff_required: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GuardDecision:
    level: RiskLevel
    category: str
    reason: str
    requires_human: bool
    allow_ai_response: bool


@dataclass
class RoutingDecision:
    provider: str
    model: str
    reason: str
    max_output_tokens: int
    temperature: float
    fallback_order: list[str]


@dataclass
class EscalationCase:
    case_id: str
    status: str
    priority: str
    created_at: datetime
    assigned_to: str | None = None


@dataclass
class UsageRecord:
    tenant_id: str
    user_id: str
    request_id: str
    provider: str
    model: str
    task_type: str
    input_tokens: int | None
    output_tokens: int | None
    cached_tokens: int
    estimated_cost: float | None
    latency_ms: int
    success: bool
    fallback_used: bool
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AgentResponse(BaseModel):
    role: str
    content: str
    status: str
    source: str
    provider: str | None
    model: str | None
    request_id: str
    cached: bool
    escalated: bool
    escalation_case_id: str | None
    requires_human_review: bool


class MatchingEvaluation(BaseModel):
    candidate_id: str
    vacancy_id: str
    hard_requirements_met: bool
    compatibility_score: int = Field(ge=0, le=100)
    skill_score: int = Field(ge=0, le=100)
    location_score: int = Field(ge=0, le=100)
    language_score: int = Field(ge=0, le=100)
    document_score: int = Field(ge=0, le=100)
    salary_score: int = Field(ge=0, le=100)
    risks: list[str]
    strengths: list[str]
    missing_requirements: list[str]
    recommendation: str
    requires_human_review: bool
