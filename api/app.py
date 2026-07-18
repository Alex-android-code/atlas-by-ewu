"""FastAPI application for ATLAS/EWU."""

import os
import hashlib
import json
import secrets
from pathlib import Path
from time import time

from fastapi import FastAPI, File, HTTPException, Request, Response, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from ai.ai_gateway import get_default_ai_gateway, send_message_to_ai
from api.agent import AGENT_DASHBOARD_HTML, AGENT_ONBOARDING_HTML
from api.chat import AI_CHAT_HTML
from api.dashboard import DASHBOARD_HTML
from api.dependencies import (
    get_agent_profile_service,
    get_agent_collaboration_service,
    get_competency_intelligence_service,
    get_corporate_ai_agent_service,
    get_crm_service,
    get_development_recommendation_service,
    get_dynamic_interview_service,
    get_entitlement_service,
    get_operations_workflow,
    get_rodo_service,
    get_skill_gap_service,
)
from api.employer import EMPLOYER_HTML
from api.ewu_bot_webhook import configure_ewu_bot_webhook, router as ewu_bot_router
from api.landing import LANDING_HTML
from api.login import LOGIN_HTML
from api.schemas import (
    AIChatRequest,
    AIMessageRequest,
    AgentOnboardingAnswer,
    AgentOnboardingComplete,
    AnalyticsEventCreate,
    CandidateCreate,
    ConsentCreate,
    DataSubjectRequestCreate,
    DataSubjectRequestStatusUpdate,
    AgentCollaborationConsentGrantCreate,
    AgentCollaborationConsentRevoke,
    AgentCollaborationProposalCreate,
    CorporateAnalysisRequest,
    CorporateDepartmentCreate,
    CorporateEmployeeCreate,
    CorporatePositionCreate,
    CustomerSubscriptionSet,
    DevelopmentPlanCreate,
    DevelopmentRecommendationCreate,
    DynamicInterviewAnswer,
    DynamicInterviewStart,
    EntitlementCheckRequest,
    EmployerCreate,
    EmployerCompetencyRequirementCreate,
    LoginRequest,
    MatchRequest,
    SkillGapAnalysisRequest,
    StatusUpdate,
    TargetCompetencyRequirement,
    UserCompetencyCreate,
    VacancyCreate,
    VerificationUpdate,
)
from chat import build_public_reply, get_next_question, validate_one_question_rule
from chat.public_tone import acknowledgement_for, tone_profile_for
from chat.intents import SCENARIO_TO_INTENT, ChatIntent
from core.models import Candidate, Employer, Vacancy, new_id, utc_now_iso
from employer_analysis import update_employer_profile_from_message
from recommendations import RecruitmentAdvisor
from services.country_config_loader import CountryConfigLoader
from services.demo_data import is_demo_record
from services.gemini_service import (
    GeminiService,
    build_structured_prompt,
    fallback_message,
    normalize_language,
    sanitize_user_text,
)
from services.intent_detector import IntentDetectorService
from services.language_detector import LanguageDetectorService
from services.language_policy import normalize_language_code
from services.language_service import LanguageService
from services.profile_builder import update_user_profile_from_message
from services.analytics import record_event
from services.dialogue_state import build_gemini_dialogue_context, process_candidate_dialogue
from trust_engine import EmployerTrustEngine
from vacancy_analysis import VacancyAnalyzer


def _init_sentry() -> None:
    dsn = os.getenv("SENTRY_DSN") or os.getenv("NEXT_PUBLIC_SENTRY_DSN")
    if not dsn:
        return
    try:
        import sentry_sdk

        sentry_sdk.init(
            dsn=dsn,
            traces_sample_rate=0.05,
            send_default_pii=False,
            before_send=_sanitize_sentry_event,
        )
    except Exception:
        return


def _sanitize_sentry_event(event: dict, hint: dict | None = None) -> dict:
    request = event.get("request")
    if isinstance(request, dict):
        request.pop("cookies", None)
        request.pop("headers", None)
        request.pop("data", None)
    return event


_init_sentry()


app = FastAPI(
    title="ATLAS/EWU API",
    description="MVP API for EWU candidates, employers, vacancies, matching, and coordinator dashboard.",
    version="0.1.0",
)
app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).resolve().parent / "static"),
    name="static",
)
UPLOADS_DIR = Path(os.getenv("ATLAS_DATA_DIR", "data")) / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.include_router(ewu_bot_router)


@app.on_event("startup")
def startup_configure_ewu_bot_webhook() -> None:
    configure_ewu_bot_webhook()

_AI_MESSAGE_RATE_LIMIT: dict[str, list[float]] = {}
AI_MESSAGE_LIMIT_PER_MINUTE = 20
_ADMIN_SESSIONS: dict[str, float] = {}
ADMIN_SESSION_TTL_SECONDS = 8 * 60 * 60
_ADMIN_LOGIN_ATTEMPTS: dict[str, list[float]] = {}
ADMIN_LOGIN_LIMIT_PER_MINUTE = 5
DEFAULT_ADMIN_PASSWORD_HASH = (
    "pbkdf2_sha256$390000$3718cc9fa2b49721cfd498b96f3cb11e$"
    "e268e03b0899da5dd638b5a9d7ee5560e267d0734ab5d37daeeef6cfb7e5955c"
)


@app.get("/", response_class=HTMLResponse)
def landing() -> str:
    return LANDING_HTML


@app.get("/ai", response_class=HTMLResponse)
def ai_chat() -> str:
    return AI_CHAT_HTML


@app.get("/agent/onboarding", response_class=HTMLResponse)
def agent_onboarding() -> str:
    return AGENT_ONBOARDING_HTML


@app.get("/{language_code}/agent/onboarding", response_class=HTMLResponse)
def localized_agent_onboarding(language_code: str) -> str:
    return AGENT_ONBOARDING_HTML


@app.get("/agent/dashboard", response_class=HTMLResponse)
def agent_dashboard_page() -> str:
    return AGENT_DASHBOARD_HTML


@app.get("/{language_code}/agent/dashboard", response_class=HTMLResponse)
def localized_agent_dashboard_page(language_code: str) -> str:
    return AGENT_DASHBOARD_HTML


@app.get("/health")
def root_health() -> dict:
    return {"status": "ok", "app": "atlas", "gemini_configured": GeminiService().is_configured()}


@app.get("/health/ai")
def root_ai_health() -> dict:
    return GeminiService().health_check(ping=True)


@app.get("/{language_code}/ai", response_class=HTMLResponse)
def localized_ai_chat(language_code: str) -> str:
    return AI_CHAT_HTML


@app.get("/employer", response_class=HTMLResponse)
def employer_experience() -> str:
    return EMPLOYER_HTML


@app.get("/{language_code}/employer", response_class=HTMLResponse)
def localized_employer_experience(language_code: str) -> str:
    return EMPLOYER_HTML


@app.get("/login", response_class=HTMLResponse)
def login() -> str:
    return LOGIN_HTML


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request) -> str:
    if not _is_admin_authorized(request):
        return LOGIN_HTML
    return DASHBOARD_HTML


@app.post("/api/login")
def api_login(payload: LoginRequest, request: Request, response: Response) -> dict[str, str]:
    client_id = request.client.host if request.client else "unknown"
    _enforce_admin_login_rate_limit(client_id)
    if not _valid_admin_password(payload.password):
        raise HTTPException(status_code=401, detail="Invalid access code")
    session_id = secrets.token_urlsafe(32)
    _ADMIN_SESSIONS[session_id] = time() + ADMIN_SESSION_TTL_SECONDS
    response.set_cookie(
        "atlas_session",
        session_id,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite="lax",
        max_age=ADMIN_SESSION_TTL_SECONDS,
    )
    return {"status": "ok", "role": "admin"}


@app.post("/api/logout")
def api_logout(request: Request, response: Response) -> dict[str, str]:
    session_id = request.cookies.get("atlas_session")
    if session_id:
        _ADMIN_SESSIONS.pop(session_id, None)
    response.delete_cookie("atlas_session")
    return {"status": "ok"}


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "atlas_ewu"}


@app.get("/api/privacy/notice")
def privacy_notice(language: str = "uk") -> dict:
    return get_rodo_service().privacy_notice(language=language)


@app.post("/api/rodo/consents")
def create_rodo_consent(payload: ConsentCreate, request: Request) -> dict:
    consent = get_rodo_service().record_consent(
        subject_id=payload.subject_id,
        language=payload.language,
        source=payload.source,
        scopes=payload.scopes or None,
        accepted=payload.accepted,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent", ""),
    )
    return {"status": "ok", "consent": consent.to_dict()}


@app.post("/api/rodo/requests")
def create_rodo_request(payload: DataSubjectRequestCreate) -> dict:
    try:
        data_request = get_rodo_service().create_data_subject_request(
            subject_id=payload.subject_id,
            request_type=payload.request_type,
            contact=payload.contact,
            language=payload.language,
            note=payload.note,
        )
        return {"status": "ok", "request": data_request.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/admin/rodo/requests")
def list_rodo_requests(request: Request) -> list[dict]:
    _require_admin(request)
    return [item.to_dict() for item in get_rodo_service().list_data_subject_requests()]


@app.patch("/api/admin/rodo/requests/{request_id}")
def update_rodo_request_status(
    request_id: str,
    payload: DataSubjectRequestStatusUpdate,
    request: Request,
) -> dict:
    _require_admin(request)
    try:
        data_request = get_rodo_service().update_data_subject_request_status(
            request_id=request_id,
            status=payload.status,
            note=payload.note,
        )
        return {"status": "ok", "request": data_request.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/api/admin/rodo/export/{subject_id}")
def export_rodo_subject_data(subject_id: str, request: Request) -> dict:
    _require_admin(request)
    return get_rodo_service().export_subject_data(subject_id)


@app.get("/api/competencies/users/{user_id}")
def get_user_competency_map(user_id: str, request: Request) -> dict:
    _require_admin(request)
    return get_competency_intelligence_service().competency_map_for_user(user_id)


@app.post("/api/competencies/users")
def create_user_competency(payload: UserCompetencyCreate, request: Request) -> dict:
    _require_admin(request)
    try:
        user_competency = get_competency_intelligence_service().add_user_competency(
            user_id=payload.user_id,
            competency_name=payload.competency_name,
            current_level=payload.current_level,
            target_level=payload.target_level,
            source=payload.source,
            confidence_score=payload.confidence_score,
            evidence_reference=payload.evidence_reference,
            years_of_experience=payload.years_of_experience,
            visibility=payload.visibility,
        )
        return {"status": "ok", "user_competency": user_competency.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/competencies/employer-requirements")
def create_employer_competency_requirement(
    payload: EmployerCompetencyRequirementCreate,
    request: Request,
) -> dict:
    _require_admin(request)
    requirement = get_competency_intelligence_service().add_employer_requirement(
        employer_id=payload.employer_id,
        competency_name=payload.competency_name,
        required_level=payload.required_level,
        vacancy_id=payload.vacancy_id,
        importance=payload.importance,
    )
    return {"status": "ok", "requirement": requirement.to_dict()}


@app.post("/api/competencies/skill-gaps")
def analyze_skill_gaps(payload: SkillGapAnalysisRequest, request: Request) -> dict:
    _require_admin(request)
    competency_service = get_competency_intelligence_service()
    requirements = [
        item
        for item in competency_service.repositories.employer_requirements.list()
        if (not payload.employer_id or item.employer_id == payload.employer_id)
        and (not payload.vacancy_id or item.vacancy_id == payload.vacancy_id)
    ]
    target_requirements = [
        _target_requirement_from_payload(item)
        for item in payload.target_requirements
    ]
    analysis = get_skill_gap_service().analyze(
        user_id=payload.user_id,
        saved_requirements=requirements,
        target_requirements=target_requirements,
        career_goal=payload.career_goal,
        target_country=payload.target_country,
    )
    return {"status": "ok", **analysis}


@app.post("/api/competencies/development-plans")
def create_development_plan(payload: DevelopmentPlanCreate, request: Request) -> dict:
    _require_admin(request)
    service = get_competency_intelligence_service()
    selected_gap_ids = set(payload.skill_gap_ids)
    gaps = [
        item
        for item in service.repositories.skill_gaps.list()
        if item.user_id == payload.user_id and (not selected_gap_ids or item.id in selected_gap_ids)
    ]
    return service.create_development_plan_from_gaps(payload.user_id, gaps, title=payload.title)


@app.post("/api/development/recommendations")
def create_development_recommendation(payload: DevelopmentRecommendationCreate, request: Request) -> dict:
    _require_admin(request)
    try:
        return get_development_recommendation_service().recommend_for_skill_gap(
            user_id=payload.user_id,
            skill_gap_id=payload.skill_gap_id,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/api/corporate/departments")
def create_corporate_department(payload: CorporateDepartmentCreate, request: Request) -> dict:
    _require_admin(request)
    department = get_corporate_ai_agent_service().add_department(
        employer_id=payload.employer_id,
        name=payload.name,
        parent_department_id=payload.parent_department_id,
    )
    return {"status": "ok", "department": department.to_dict()}


@app.post("/api/corporate/positions")
def create_corporate_position(payload: CorporatePositionCreate, request: Request) -> dict:
    _require_admin(request)
    position = get_corporate_ai_agent_service().add_position(
        employer_id=payload.employer_id,
        title=payload.title,
        department_id=payload.department_id,
        headcount_required=payload.headcount_required,
        role_functions=payload.role_functions,
    )
    return {"status": "ok", "position": position.to_dict()}


@app.post("/api/corporate/employees")
def create_corporate_employee(payload: CorporateEmployeeCreate, request: Request) -> dict:
    _require_admin(request)
    employee = get_corporate_ai_agent_service().add_employee(
        employer_id=payload.employer_id,
        user_id=payload.user_id,
        position_id=payload.position_id,
        department_id=payload.department_id,
        turnover_risk_factors=payload.turnover_risk_factors,
    )
    return {"status": "ok", "employee": employee.to_dict()}


@app.post("/api/corporate/analyze")
def analyze_corporate_ai(payload: CorporateAnalysisRequest, request: Request) -> dict:
    _require_admin(request)
    return get_corporate_ai_agent_service().analyze_company(
        employer_id=payload.employer_id,
        horizon_months=payload.horizon_months,
    )


@app.post("/api/agent-collaboration/proposals")
def create_agent_collaboration_proposal(payload: AgentCollaborationProposalCreate, request: Request) -> dict:
    _require_admin(request)
    try:
        proposal = get_agent_collaboration_service().create_proposal(
            employer_id=payload.employer_id,
            user_id=payload.user_id,
            proposal_type=payload.proposal_type,
            title=payload.title,
            data_categories=payload.data_categories,
            actor_id=payload.actor_id,
            metadata=payload.metadata,
        )
        return {"status": "ok", "proposal": proposal.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/agent-collaboration/consents/grant")
def grant_agent_collaboration_consent(payload: AgentCollaborationConsentGrantCreate) -> dict:
    try:
        grant = get_agent_collaboration_service().grant_consent(
            proposal_id=payload.proposal_id,
            user_id=payload.user_id,
            actor_id=payload.actor_id,
        )
        return {"status": "ok", "grant": grant.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/agent-collaboration/consents/revoke")
def revoke_agent_collaboration_consent(payload: AgentCollaborationConsentRevoke) -> dict:
    try:
        grant = get_agent_collaboration_service().revoke_consent(
            grant_id=payload.grant_id,
            actor_id=payload.actor_id,
        )
        return {"status": "ok", "grant": grant.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/api/agent-collaboration/proposals/{proposal_id}")
def get_agent_collaboration_status(proposal_id: str, request: Request) -> dict:
    _require_admin(request)
    try:
        return get_agent_collaboration_service().collaboration_status(proposal_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


def _target_requirement_from_payload(payload: TargetCompetencyRequirement):
    from services.skill_gap_analysis import TargetRequirement

    return TargetRequirement(
        competency_name=payload.competency_name,
        required_level=payload.required_level,
        importance=payload.importance,
        source=payload.source,
        employer_id=payload.employer_id,
        vacancy_id=payload.vacancy_id,
    )


@app.post("/api/interview/start")
def start_dynamic_interview(payload: DynamicInterviewStart) -> dict:
    return get_dynamic_interview_service().start_or_resume(
        user_id=payload.user_id,
        role=payload.role,
        language=payload.language,
    )


@app.post("/api/interview/answer")
def answer_dynamic_interview(payload: DynamicInterviewAnswer) -> dict:
    try:
        return get_dynamic_interview_service().answer_step(payload.session_id, payload.answer)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/{language_code}", response_class=HTMLResponse)
def localized_landing(language_code: str) -> str:
    return LANDING_HTML


@app.get("/api/ai/health")
def ai_health() -> dict:
    return get_default_ai_gateway().health()


@app.post("/api/ai/message")
def ai_message(payload: AIMessageRequest, request: Request) -> dict:
    client_id = request.client.host if request.client else "unknown"
    _enforce_ai_message_rate_limit(client_id)
    language = normalize_language(payload.language)
    message = sanitize_user_text(payload.message)
    if not message:
        raise HTTPException(status_code=400, detail="Message is empty")
    ai_response = send_message_to_ai(
        user_id=client_id,
        agent_type=payload.role,
        context={
            "user_id": client_id,
            "role": payload.role,
            "language": language,
            "current_step": payload.current_step,
            "profile": payload.profile_data,
            "recent_messages": payload.recent_messages,
            "task": payload.task,
            "metadata": {"source": "api_ai_message", "current_step": payload.current_step},
        },
        message=message,
    )
    metadata = ai_response.get("metadata", {})
    return {
        "success": metadata.get("status") == "ok",
        "message": ai_response.get("reply") or fallback_message(language),
        "next_field": None,
        "profile_updates": {},
        "warnings": [] if metadata.get("status") == "ok" else ["ai_unavailable"],
        "confidence": ai_response.get("confidence", 0.0),
        "provider": metadata.get("provider"),
        "model": metadata.get("model"),
        "fallback_used": bool(metadata.get("fallback_used", metadata.get("source") != "model")),
        "request_id": metadata.get("request_id"),
    }


@app.get("/api/public/market-map")
def public_market_map() -> dict:
    countries = CountryConfigLoader().load_all()
    vacancies = get_crm_service().vacancies.list()
    open_counts: dict[str, int] = {code: 0 for code in countries}
    for vacancy in vacancies:
        code = vacancy.country_code.upper()
        if not is_demo_record(vacancy) and vacancy.status in {"open", "published"} and code in open_counts:
            open_counts[code] += 1
    return {
        "countries": [
            {
                "code": code,
                "name": config["name"],
                "currency": config["currency"],
                "open_vacancies": open_counts.get(code, 0),
                "presence": True,
            }
            for code, config in sorted(countries.items())
        ],
        "has_live_metrics": any(count > 0 for count in open_counts.values()),
    }


def _enforce_ai_message_rate_limit(client_id: str) -> None:
    now = time()
    recent = [stamp for stamp in _AI_MESSAGE_RATE_LIMIT.get(client_id, []) if now - stamp < 60]
    if len(recent) >= AI_MESSAGE_LIMIT_PER_MINUTE:
        raise HTTPException(status_code=429, detail="Too many AI requests")
    recent.append(now)
    _AI_MESSAGE_RATE_LIMIT[client_id] = recent


@app.get("/api/languages")
def list_languages() -> list[dict]:
    return LanguageService().get_available_languages()


@app.get("/api/translations/{code}")
def get_translations(code: str) -> dict[str, str]:
    language_service = LanguageService()
    current_language = language_service.set_language(code)
    return language_service.load_translations(current_language)


@app.get("/api/agent/onboarding/schema")
def get_agent_onboarding_schema(language: str = "uk") -> dict:
    return get_agent_profile_service().onboarding_schema(language=language)


@app.post("/api/agent/onboarding/answer")
def save_agent_onboarding_answer(payload: AgentOnboardingAnswer) -> dict:
    try:
        return get_agent_profile_service().save_onboarding_answer(
            user_id=payload.user_id,
            field=payload.field,
            value=payload.value,
            language=payload.language,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/agent/onboarding/complete")
def complete_agent_onboarding(payload: AgentOnboardingComplete) -> dict:
    result = get_agent_profile_service().complete_onboarding(payload.user_id)
    professional_dna = result.get("dashboard", {}).get("professional_dna", {})
    crm_sync = _sync_agent_profile_to_crm(payload.user_id, professional_dna)
    result["crm_sync"] = crm_sync
    return result


@app.get("/api/agent/dashboard/{user_id}")
def get_agent_dashboard(user_id: str) -> dict:
    return get_agent_profile_service().agent_dashboard(user_id)


@app.get("/api/subscriptions/features/{plan}")
def get_subscription_features(plan: str) -> dict:
    return {
        "plan": plan,
        "features": {
            item["code"]: item["features"]
            for item in get_entitlement_service().catalog()["plans"]
        }.get(plan, get_entitlement_service().catalog()["plans"][0]["features"]),
    }


@app.get("/api/subscriptions/catalog")
def get_subscription_catalog() -> dict:
    return get_entitlement_service().catalog()


@app.post("/api/admin/subscriptions/sync")
def sync_subscription_catalog(request: Request) -> dict:
    _require_admin(request)
    return {"status": "ok", **get_entitlement_service().sync_catalog()}


@app.post("/api/admin/subscriptions/customers")
def set_customer_subscription(payload: CustomerSubscriptionSet, request: Request) -> dict:
    _require_admin(request)
    try:
        subscription = get_entitlement_service().set_customer_subscription(
            customer_id=payload.customer_id,
            customer_type=payload.customer_type,
            plan_code=payload.plan_code,
        )
        return {"status": "ok", "subscription": subscription.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/admin/subscriptions/entitlements/check")
def check_customer_entitlement(payload: EntitlementCheckRequest, request: Request) -> dict:
    _require_admin(request)
    return {
        "customer_id": payload.customer_id,
        "customer_type": payload.customer_type,
        "feature_code": payload.feature_code,
        "allowed": get_entitlement_service().has_entitlement(
            customer_id=payload.customer_id,
            customer_type=payload.customer_type,
            feature_code=payload.feature_code,
        ),
    }


@app.get("/api/i18n/bootstrap")
def i18n_bootstrap(
    selected_language: str | None = None,
    browser_language: str | None = None,
) -> dict:
    return LanguageService().bootstrap(
        selected_language=selected_language,
        browser_language=browser_language,
    )


@app.post("/api/ai/chat")
def ai_chat_message(payload: AIChatRequest) -> dict:
    memory_store = get_operations_workflow().memory_store
    memory = memory_store.load(payload.user_id)
    request_id = payload.request_id or new_id("CHATREQ")
    conversation_preference = (
        normalize_language_code(payload.conversation_language)
        or normalize_language_code(payload.ui_language)
        or normalize_language_code(payload.saved_language)
        or memory.preferences.get("conversation_language")
        or memory.preferences.get("preferred_language")
    )
    language = LanguageDetectorService().detect(
        browser_language=payload.browser_language,
        saved_preference=conversation_preference,
        first_message=payload.message,
    )
    cached_response = (memory.profile_data.get("request_cache") or {}).get(request_id)
    if isinstance(cached_response, dict):
        return {
            "reply": cached_response.get("reply") or "",
            "ai": {"fallback_used": True, "duplicate_request": True, "request_id": request_id},
            "profile": memory.profile_data,
            "employer_experience": memory.profile_data.get("employer_experience"),
            "intent": memory.profile_data.get("detected_intent"),
            "language": {
                "ui_language": normalize_language_code(payload.ui_language) or normalize_language_code(payload.saved_language),
                "conversation_language": language,
            },
            "request_id": request_id,
            "duplicate": True,
            "reply_validation": {"valid": True, "warnings": []},
        }
    intent_result = IntentDetectorService().detect(
        payload.message,
        requested_agent_type=payload.agent_type,
        previous_intent=memory.profile_data.get("scenario") or memory.profile_data.get("intent"),
    )
    agent_type = intent_result.agent_type
    dialogue_result = None
    if agent_type == "employer":
        profile = update_employer_profile_from_message(memory, payload.message, language=language)
        if intent_result.profession:
            profile.setdefault("vacancy", {})["profession"] = profile.get("vacancy", {}).get("profession") or intent_result.profession
        employer_experience = _build_employer_experience(profile)
        profile["employer_experience"] = employer_experience
    else:
        profile = update_user_profile_from_message(memory, payload.message, language=language)
        if intent_result.profession:
            profile["profession"] = profile.get("profession") or intent_result.profession
        dialogue_result = process_candidate_dialogue(
            profile=profile,
            message=payload.message,
            language=language,
            request_id=request_id,
        )
        profile = dialogue_result.profile
        employer_experience = None
    profile["scenario"] = intent_result.scenario
    profile["tone_profile"] = tone_profile_for(intent_result.scenario)
    profile["detected_intent"] = {
        "scenario": intent_result.scenario,
        "agent_type": intent_result.agent_type,
        "confidence": intent_result.confidence,
        "signals": intent_result.signals,
        "profession": intent_result.profession,
    }
    translations = LanguageService().load_translations(language)
    ai_response = send_message_to_ai(
        user_id=payload.user_id,
        agent_type=agent_type,
        context={
            "profile": profile,
            "memory": memory.to_dict(),
            "source": "ai_chat",
            "language": language,
            "ui_language": normalize_language_code(payload.ui_language) or normalize_language_code(payload.saved_language),
            "conversation_language": language,
            "tone_profile": profile["tone_profile"],
            "translations": translations,
            "employer_experience": employer_experience,
            "intent": profile["detected_intent"],
            "dialogue": build_gemini_dialogue_context(
                profile=profile,
                language=language,
                role=agent_type,
                last_user_message=payload.message,
                next_field=dialogue_result.next_field if dialogue_result else None,
            ) if agent_type != "employer" else None,
        },
        message=payload.message,
    )
    assistant_reply = dialogue_result.reply if dialogue_result else _natural_reply(profile, ai_response, employer_experience, translations, language)
    validation = validate_one_question_rule(assistant_reply, language=language)
    if not validation.valid and validation.safe_fallback:
        assistant_reply = validation.safe_fallback
    profile.setdefault("messages", []).append({"role": "assistant", "content": assistant_reply})
    memory.profile_data = profile
    memory_store.save(memory)
    crm_sync = _sync_chat_profile_to_crm(payload.user_id, profile, agent_type)
    return {
        "reply": assistant_reply,
        "ai": ai_response,
        "profile": profile,
        "crm_sync": crm_sync,
        "employer_experience": employer_experience,
        "intent": profile["detected_intent"],
        "language": {
            "ui_language": normalize_language_code(payload.ui_language) or normalize_language_code(payload.saved_language),
            "conversation_language": language,
        },
        "request_id": request_id,
        "duplicate": False,
        "dialogue": {
            "current_step": dialogue_result.current_step if dialogue_result else None,
            "completed_fields": dialogue_result.completed_fields if dialogue_result else [],
            "next_field": dialogue_result.next_field if dialogue_result else None,
            "field": dialogue_result.field if dialogue_result else None,
            "profile_updated": dialogue_result.profile_updated if dialogue_result else False,
        },
        "reply_validation": {
            "valid": validation.valid,
            "warnings": validation.warnings,
        },
    }


@app.get("/api/dashboard")
def get_dashboard(request: Request) -> dict:
    _require_admin(request)
    _sync_existing_public_profiles_to_crm()
    return get_crm_service().coordinator_dashboard()


@app.post("/api/analytics/event")
def create_analytics_event(payload: AnalyticsEventCreate) -> dict:
    event = record_event(
        get_crm_service().activity,
        payload.name,
        payload.params,
        actor_id=payload.actor_id or "anonymous",
    )
    return {"status": "ok", "event": event.to_dict()}


@app.get("/api/admin/analytics")
def get_admin_analytics(
    request: Request,
    days: int = 1,
    country: str | None = None,
    language: str | None = None,
    profession: str | None = None,
    traffic_source: str | None = None,
    user_role: str | None = None,
) -> dict:
    _require_admin(request)
    return get_crm_service().internal_analytics(
        days=days,
        country=country,
        language=language,
        profession=profession,
        traffic_source=traffic_source,
        user_role=user_role,
    )


@app.get("/api/admin/first-vacancies-report")
def get_first_vacancies_report(request: Request, limit: int = 5) -> list[dict]:
    _require_admin(request)
    return get_crm_service().first_vacancies_report(limit=limit)


@app.get("/api/candidates")
def list_candidates(request: Request) -> list[dict]:
    _require_admin(request)
    return [candidate.to_dict() for candidate in get_crm_service().candidates.list()]


@app.post("/api/candidates")
def create_candidate(payload: CandidateCreate) -> dict:
    candidate = Candidate(**payload.model_dump())
    return get_operations_workflow().onboard_candidate(candidate)


@app.post("/api/candidates/{candidate_id}/photo")
def upload_candidate_photo(candidate_id: str, request: Request, file: UploadFile = File(...)) -> dict:
    _require_admin(request)
    candidate = get_crm_service().candidates.get(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found")
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(status_code=400, detail="Only JPG, PNG or WebP photos are allowed")
    extension = _safe_photo_extension(file.filename, file.content_type)
    photo_dir = UPLOADS_DIR / "candidate_photos"
    photo_dir.mkdir(parents=True, exist_ok=True)
    target_name = f"{candidate_id}{extension}"
    target_path = photo_dir / target_name
    max_bytes = 5 * 1024 * 1024
    written = 0
    with target_path.open("wb") as handle:
        while True:
            chunk = file.file.read(1024 * 1024)
            if not chunk:
                break
            written += len(chunk)
            if written > max_bytes:
                handle.close()
                target_path.unlink(missing_ok=True)
                raise HTTPException(status_code=413, detail="Photo is too large. Maximum size is 5 MB")
            handle.write(chunk)
    candidate.metadata["profile_photo"] = {
        "filename": file.filename or target_name,
        "content_type": file.content_type,
        "size_bytes": written,
        "url": f"/uploads/candidate_photos/{target_name}",
        "uploaded_at": utc_now_iso(),
    }
    get_crm_service().candidates.update(candidate)
    return {"candidate": candidate.to_dict(), "profile_photo": candidate.metadata["profile_photo"]}


@app.patch("/api/candidates/{candidate_id}/status")
def update_candidate_status(candidate_id: str, payload: StatusUpdate, request: Request) -> dict:
    _require_admin(request)
    try:
        candidate = get_crm_service().update_candidate_status(
            candidate_id,
            payload.status,
            actor_id=payload.actor_id,
            note=payload.note,
        )
        return {"candidate": candidate.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.patch("/api/candidates/{candidate_id}/documents-received")
def mark_candidate_documents_received(candidate_id: str, request: Request, payload: StatusUpdate | None = None) -> dict:
    _require_admin(request)
    status_update = payload or StatusUpdate(status="ready_for_matching", note="Documents received")
    try:
        candidate = get_crm_service().mark_candidate_documents_received(
            candidate_id,
            actor_id=status_update.actor_id,
            note=status_update.note or "Documents received",
        )
        return {"candidate": candidate.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/api/employers")
def list_employers(request: Request) -> list[dict]:
    _require_admin(request)
    return [employer.to_dict() for employer in get_crm_service().employers.list()]


@app.post("/api/employers")
def create_employer(payload: EmployerCreate, request: Request) -> dict:
    employer = Employer(**payload.model_dump())
    request_id = request.headers.get("x-request-id") or new_id("REQ")
    employer.metadata["request_log"] = {
        "request_id": request_id,
        "employer_id": employer.id,
        "timestamp": utc_now_iso(),
        "ip": request.client.host if request.client else "unknown",
        "user_agent": request.headers.get("user-agent", "unknown"),
    }
    employer.metadata["correlation_id"] = request_id
    return get_operations_workflow().onboard_employer(employer)


@app.patch("/api/employers/{employer_id}/verify")
def verify_employer(employer_id: str, request: Request, payload: VerificationUpdate | None = None) -> dict:
    _require_admin(request)
    verification = payload or VerificationUpdate()
    try:
        employer = get_crm_service().set_employer_verified(
            employer_id,
            verified=verification.verified,
            actor_id=verification.actor_id,
            note=verification.note,
        )
        return {"employer": employer.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/api/vacancies")
def list_vacancies(request: Request) -> list[dict]:
    _require_admin(request)
    return [vacancy.to_dict() for vacancy in get_crm_service().vacancies.list()]


@app.post("/api/vacancies")
def create_vacancy(payload: VacancyCreate) -> dict:
    vacancy = Vacancy(**payload.model_dump())
    return get_operations_workflow().publish_vacancy(vacancy)


@app.patch("/api/vacancies/{vacancy_id}/status")
def update_vacancy_status(vacancy_id: str, payload: StatusUpdate, request: Request) -> dict:
    _require_admin(request)
    try:
        vacancy = get_crm_service().update_vacancy_status(
            vacancy_id,
            payload.status,
            actor_id=payload.actor_id,
            note=payload.note,
        )
        return {"vacancy": vacancy.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.post("/api/admin/vacancies/{vacancy_id}/publish")
def publish_vacancy(vacancy_id: str, request: Request) -> dict:
    _require_admin(request)
    try:
        verified = get_crm_service().update_vacancy_status(
            vacancy_id,
            "verified",
            actor_id="admin",
            note="Verified before publication",
        )
        published = get_crm_service().update_vacancy_status(
            verified.id,
            "published",
            actor_id="admin",
            note="Published from admin moderation",
        )
        return {"vacancy": published.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.post("/api/vacancies/{vacancy_id}/match")
def match_vacancy(vacancy_id: str, request: Request, payload: MatchRequest | None = None) -> dict:
    _require_admin(request)
    match_request = payload or MatchRequest()
    try:
        return get_operations_workflow().run_matching_for_vacancy(
            vacancy_id,
            minimum_score=match_request.minimum_score,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/api/matches")
def list_matches(request: Request) -> list[dict]:
    _require_admin(request)
    return [match.to_dict() for match in get_crm_service().matches.list()]


@app.patch("/api/matches/{match_id}/status")
def update_match_status(match_id: str, payload: StatusUpdate, request: Request) -> dict:
    _require_admin(request)
    try:
        match = get_crm_service().update_match_status(
            match_id,
            payload.status,
            actor_id=payload.actor_id,
            note=payload.note,
        )
        return {"match": match.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/api/activity")
def list_activity(request: Request, limit: int = 50) -> list[dict]:
    _require_admin(request)
    return [event.to_dict() for event in get_crm_service().list_activity(limit=limit)]


def _valid_admin_password(password: str) -> bool:
    password_hash = os.getenv("ATLAS_ADMIN_PASSWORD_HASH", "").strip()
    if password_hash and _verify_pbkdf2_sha256(password, password_hash):
        return True
    configured_password = os.getenv("ATLAS_ADMIN_PASSWORD", "").strip() or os.getenv("ATLAS_ADMIN_TOKEN", "").strip()
    if configured_password and secrets.compare_digest(password, configured_password):
        return True
    return _verify_pbkdf2_sha256(password, DEFAULT_ADMIN_PASSWORD_HASH)


def _enforce_admin_login_rate_limit(client_id: str) -> None:
    now = time()
    recent = [timestamp for timestamp in _ADMIN_LOGIN_ATTEMPTS.get(client_id, []) if now - timestamp < 60]
    if len(recent) >= ADMIN_LOGIN_LIMIT_PER_MINUTE:
        _ADMIN_LOGIN_ATTEMPTS[client_id] = recent
        raise HTTPException(status_code=429, detail="Too many login attempts")
    recent.append(now)
    _ADMIN_LOGIN_ATTEMPTS[client_id] = recent


def _verify_pbkdf2_sha256(password: str, encoded_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected = encoded_hash.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), int(iterations))
        return secrets.compare_digest(digest.hex(), expected)
    except (TypeError, ValueError):
        return False


def _is_admin_authorized(request: Request) -> bool:
    _expire_admin_sessions()
    session_id = request.cookies.get("atlas_session")
    if session_id and _ADMIN_SESSIONS.get(session_id, 0) > time():
        return True
    token = request.headers.get("x-atlas-admin-token")
    expected_token = os.getenv("ATLAS_ADMIN_TOKEN")
    if expected_token and token and secrets.compare_digest(token, expected_token):
        return True
    return False


def _expire_admin_sessions() -> None:
    now = time()
    expired = [session_id for session_id, expires_at in _ADMIN_SESSIONS.items() if expires_at <= now]
    for session_id in expired:
        _ADMIN_SESSIONS.pop(session_id, None)


def _require_admin(request: Request) -> None:
    if _is_admin_authorized(request):
        return
    raise HTTPException(status_code=403, detail="Admin access required")


def _safe_photo_extension(filename: str | None, content_type: str | None) -> str:
    allowed_by_type = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }
    if content_type in allowed_by_type:
        return allowed_by_type[content_type]
    suffix = Path(filename or "").suffix.lower()
    return suffix if suffix in {".jpg", ".jpeg", ".png", ".webp"} else ".jpg"


@app.post("/api/demo/seed")
def seed_demo() -> dict:
    workflow = get_operations_workflow()
    candidate_result = workflow.onboard_candidate(
        Candidate(
            first_name="Oleh",
            last_name="Bondar",
            email="oleh.bondar@example.com",
            phone="+380991112233",
            country_code="UA",
            profession_code="welder",
            languages=["uk", "pl"],
            years_of_experience=6,
            user_id="candidate-oleh",
            metadata={
                "desired_country_code": "PL",
                "desired_salary": 6400,
                "salary_currency": "PLN",
                "ready_from": "2026-07-20",
                "document_types": ["passport_or_id", "cv"],
            },
        )
    )
    employer_result = workflow.onboard_employer(
        Employer(
            company_name="North Steel Group",
            contact_email="jobs@north-steel.example",
            contact_phone="+48111222333",
            country_code="PL",
            industry="manufacturing",
            verified=False,
        )
    )
    vacancy = Vacancy(
        employer_id=employer_result["employer"]["id"],
        title="Welder",
        country_code="PL",
        profession_code="welder",
        salary_min=5800,
        salary_max=7200,
        currency="PLN",
        required_languages=["pl"],
        required_documents=["passport_or_id", "cv"],
        location="Poznan",
        metadata={
            "contract_type": "umowa_o_prace",
            "work_permission_status": "to_be_verified",
            "housing": True,
            "housing_terms": "Employer provides shared housing with written terms.",
            "salary_confirmed": True,
            "people_needed": 4,
            "requirements": ["mig_mag", "technical_drawing"],
        },
    )
    pipeline_result = workflow.process_vacancy_pipeline(vacancy)
    return {
        "candidate": candidate_result,
        "employer": employer_result,
        "pipeline": pipeline_result,
    }


def _candidate_reply(profile: dict, ai_response: dict) -> str:
    reply = ai_response.get("reply")
    if reply:
        return reply
    return "coordinator.welcome"


def _sync_chat_profile_to_crm(user_id: str, profile: dict, agent_type: str) -> dict:
    if agent_type == "employer":
        return _sync_employer_chat_profile_to_crm(user_id, profile)
    return _sync_candidate_chat_profile_to_crm(user_id, profile)


def _sync_existing_public_profiles_to_crm() -> dict:
    synced: list[dict] = []
    memory_store = get_operations_workflow().memory_store
    storage_dir = getattr(memory_store, "storage_dir", None)
    if storage_dir:
        for path in storage_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            user_id = str(data.get("user_id") or path.stem)
            profile = data.get("profile_data") if isinstance(data.get("profile_data"), dict) else {}
            if not profile:
                continue
            detected = profile.get("detected_intent") if isinstance(profile.get("detected_intent"), dict) else {}
            role = detected.get("agent_type") or profile.get("scenario") or "candidate"
            result = _sync_chat_profile_to_crm(user_id, profile, str(role))
            if result.get("status") == "created":
                synced.append(result)
    try:
        for profile in get_agent_profile_service().profiles.list():
            result = _sync_agent_profile_to_crm(profile.user_id, profile.to_dict())
            if result.get("status") == "created":
                synced.append(result)
    except Exception:
        pass
    return {"synced": synced, "count": len(synced)}


def _sync_candidate_chat_profile_to_crm(user_id: str, profile: dict) -> dict:
    crm = get_crm_service()
    existing = _candidate_by_source_user_id(user_id)
    if existing:
        return {"status": "already_exists", "entity": "candidate", "id": existing.id}
    if not _candidate_profile_has_lead_signal(profile):
        return {"status": "not_ready", "entity": "candidate"}

    first_name, last_name = _split_full_name(
        profile.get("full_name")
        or profile.get("name")
        or profile.get("contact_name")
        or f"ATLAS Lead {str(user_id)[-4:]}"
    )
    candidate = Candidate(
        first_name=first_name,
        last_name=last_name,
        email=str(profile.get("email") or f"{_safe_id_fragment(user_id)}@atlas.local"),
        phone=str(profile.get("phone") or profile.get("phone_number") or profile.get("contact") or "not_provided"),
        country_code=_country_code_from_value(profile.get("country") or profile.get("current_country") or "UA"),
        profession_code=_profession_code_from_value(profile.get("profession") or "general"),
        languages=_language_list(profile.get("languages")),
        years_of_experience=_safe_int(profile.get("experience_years"), 0),
        user_id=user_id,
        metadata={
            "source": "public_ai_chat",
            "source_user_id": user_id,
            "preferred_language": profile.get("preferred_language"),
            "desired_country_code": _country_code_from_value(
                profile.get("desired_country")
                or profile.get("preferred_destination")
                or profile.get("country")
                or "PL"
            ),
            "desired_salary": _safe_int(profile.get("desired_salary"), 0),
            "ready_from": profile.get("ready_from"),
            "document_types": _string_list(profile.get("documents")),
            "profile_snapshot": _compact_profile_snapshot(profile),
        },
    )
    result = get_operations_workflow().onboard_candidate(candidate)
    return {"status": "created", "entity": "candidate", "id": result["candidate"]["id"]}


def _sync_agent_profile_to_crm(user_id: str, professional_dna: dict) -> dict:
    existing = _candidate_by_source_user_id(user_id)
    if existing:
        return {"status": "already_exists", "entity": "candidate", "id": existing.id}
    if not _agent_profile_has_lead_signal(professional_dna):
        return {"status": "not_ready", "entity": "candidate"}
    first_name, last_name = _split_full_name(
        professional_dna.get("personal_information", {}).get("full_name")
        or f"ATLAS Agent {str(user_id)[-4:]}"
    )
    location = professional_dna.get("current_location") or {}
    contact = professional_dna.get("contact_information") or {}
    salary = professional_dna.get("salary_expectations") or {}
    candidate = Candidate(
        first_name=first_name,
        last_name=last_name,
        email=str(contact.get("email") or f"{_safe_id_fragment(user_id)}@atlas.local"),
        phone=str(contact.get("phone") or "not_provided"),
        country_code=_country_code_from_value(location.get("country") or "UA"),
        profession_code=_profession_code_from_value(
            professional_dna.get("professional_summary")
            or (professional_dna.get("preferred_roles") or ["general"])[0]
        ),
        languages=_language_list(professional_dna.get("languages")),
        years_of_experience=_safe_int(len(professional_dna.get("work_experience") or []), 0),
        user_id=user_id,
        metadata={
            "source": "agent_onboarding",
            "source_user_id": user_id,
            "desired_country_code": _country_code_from_value(
                professional_dna.get("relocation_preferences", {}).get("preferred_country")
                or location.get("country")
                or "PL"
            ),
            "desired_salary": salary.get("expected"),
            "document_types": ["cv"] if professional_dna.get("uploaded_cv") else [],
            "profile_photo": professional_dna.get("profile_photo") or {},
            "professional_dna_id": professional_dna.get("id"),
        },
    )
    result = get_operations_workflow().onboard_candidate(candidate)
    return {"status": "created", "entity": "candidate", "id": result["candidate"]["id"]}


def _sync_employer_chat_profile_to_crm(user_id: str, profile: dict) -> dict:
    employer_profile = profile.get("employer") or {}
    vacancy_profile = profile.get("vacancy") or {}
    if not any(employer_profile.get(key) for key in ("company_name", "contact_email", "contact_phone")) and not vacancy_profile:
        return {"status": "not_ready", "entity": "employer"}
    crm = get_crm_service()
    employer = Employer(
        company_name=str(employer_profile.get("company_name") or f"ATLAS Employer {str(user_id)[-4:]}"),
        contact_email=str(employer_profile.get("contact_email") or f"{_safe_id_fragment(user_id)}@atlas.local"),
        contact_phone=str(employer_profile.get("contact_phone") or "not_provided"),
        country_code=_country_code_from_value(employer_profile.get("country") or vacancy_profile.get("country") or "PL"),
        industry=str(employer_profile.get("industry") or "unknown"),
        metadata={"source": "public_ai_chat", "source_user_id": user_id, "actor_id": "employer"},
    )
    saved_employer = crm.create_employer(employer)
    if vacancy_profile and not _vacancy_by_source_user_id(user_id):
        salary = _safe_int(vacancy_profile.get("salary"), 0)
        vacancy = Vacancy(
            employer_id=saved_employer.id,
            title=str(vacancy_profile.get("profession") or "Recruitment request"),
            country_code=_country_code_from_value(vacancy_profile.get("country") or employer.country_code),
            profession_code=_profession_code_from_value(vacancy_profile.get("profession") or "general"),
            salary_min=salary,
            salary_max=salary,
            currency="PLN",
            required_languages=[],
            required_documents=[],
            location=vacancy_profile.get("location"),
            metadata={
                "source": "public_ai_chat",
                "source_user_id": user_id,
                "people_needed": _safe_int(vacancy_profile.get("quantity"), 1),
                "housing": vacancy_profile.get("housing"),
                "requirements": _string_list(vacancy_profile.get("requirements")),
            },
        )
        saved_vacancy = get_operations_workflow().publish_vacancy(vacancy)["vacancy"]
        return {"status": "created", "entity": "employer_vacancy", "id": saved_employer.id, "vacancy_id": saved_vacancy["id"]}
    return {"status": "created", "entity": "employer", "id": saved_employer.id}


def _candidate_by_source_user_id(user_id: str) -> Candidate | None:
    for candidate in get_crm_service().candidates.list():
        if candidate.user_id == user_id or candidate.metadata.get("source_user_id") == user_id:
            return candidate
    return None


def _vacancy_by_source_user_id(user_id: str) -> Vacancy | None:
    for vacancy in get_crm_service().vacancies.list():
        if vacancy.metadata.get("source_user_id") == user_id:
            return vacancy
    return None


def _candidate_profile_has_lead_signal(profile: dict) -> bool:
    return any(profile.get(key) for key in ("profession", "country", "phone", "phone_number", "email", "documents", "desired_salary"))


def _agent_profile_has_lead_signal(profile: dict) -> bool:
    return any(
        (
            profile.get("personal_information", {}).get("full_name"),
            profile.get("professional_summary"),
            profile.get("current_location"),
            profile.get("contact_information", {}).get("phone"),
            profile.get("contact_information", {}).get("email"),
            profile.get("work_experience"),
            profile.get("skills"),
        )
    )


def _compact_profile_snapshot(profile: dict) -> dict:
    allowed = {"profession", "country", "languages", "documents", "desired_salary", "ready_from", "current_step", "completed_fields"}
    return {key: profile.get(key) for key in allowed if profile.get(key)}


def _split_full_name(value: object) -> tuple[str, str]:
    parts = [part for part in str(value or "").strip().split() if part]
    if not parts:
        return "ATLAS", "Lead"
    if len(parts) == 1:
        return parts[0], "Lead"
    return parts[0], " ".join(parts[1:])


def _country_code_from_value(value: object) -> str:
    text = str(value or "").strip().upper()
    aliases = {
        "POLAND": "PL",
        "POLSCHA": "PL",
        "ПОЛЬША": "PL",
        "ПОЛЬЩА": "PL",
        "GERMANY": "DE",
        "ГЕРМАНИЯ": "DE",
        "НІМЕЧЧИНА": "DE",
        "UKRAINE": "UA",
        "УКРАИНА": "UA",
        "УКРАЇНА": "UA",
    }
    if len(text) == 2 and text.isalpha():
        return text
    return aliases.get(text, "PL")


def _profession_code_from_value(value: object) -> str:
    text = str(value or "general").strip().lower()
    aliases = {
        "welder": "welder",
        "зварювальник": "welder",
        "сварщик": "welder",
        "driver": "driver",
        "водитель": "driver",
        "водій": "driver",
        "electrician": "electrician",
        "електрик": "electrician",
    }
    return aliases.get(text, "".join(char if char.isalnum() else "_" for char in text).strip("_") or "general")


def _language_list(value: object) -> list[str]:
    if isinstance(value, list):
        result = []
        for item in value:
            if isinstance(item, dict):
                item = item.get("name")
            if str(item or "").strip():
                result.append(str(item).strip().lower()[:12])
        return result
    return _string_list(value)


def _string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value or "").split(",") if item.strip()]


def _safe_int(value: object, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def _safe_id_fragment(value: object) -> str:
    fragment = "".join(char for char in str(value or "lead") if char.isalnum() or char in ("-", "_"))
    return fragment[:48] or "lead"


def _natural_reply(
    profile: dict,
    ai_response: dict,
    employer_experience: dict | None,
    translations: dict[str, str],
    language: str,
) -> str:
    scenario = profile.get("scenario") or "consultation"
    intent = SCENARIO_TO_INTENT.get(scenario, ChatIntent.GENERAL_CONSULTATION)
    known_fields = _known_fields_for_reply(profile, employer_experience, scenario)
    next_question = get_next_question(intent, known_fields=known_fields, language=language)
    summary = _understood_summary(profile, scenario, language, translations)
    if next_question:
        return build_public_reply(
            acknowledgement=_acknowledgement(language, scenario),
            understood_summary=summary,
            next_question=next_question,
            language=language,
            audience=scenario,
        )
    if scenario == "employer":
        return build_public_reply(
            acknowledgement=_acknowledgement(language, scenario),
            understood_summary=_localized_text(
                language,
                {
                    "pl": "Mam juz podstawowe informacje o ofercie.",
                    "uk": "\u0423 \u043c\u0435\u043d\u0435 \u0432\u0436\u0435 \u0454 \u0431\u0430\u0437\u043e\u0432\u0430 \u0456\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0456\u044f \u043f\u043e \u0432\u0430\u043a\u0430\u043d\u0441\u0456\u0457.",
                    "ru": "\u0423 \u043c\u0435\u043d\u044f \u0443\u0436\u0435 \u0435\u0441\u0442\u044c \u0431\u0430\u0437\u043e\u0432\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043f\u043e \u0432\u0430\u043a\u0430\u043d\u0441\u0438\u0438.",
                    "en": "I already have the basic vacancy details.",
                },
            ),
            next_question=None,
            language=language,
            audience=scenario,
        )
    if scenario == "candidate":
        return build_public_reply(
            acknowledgement=_acknowledgement(language, scenario),
            understood_summary=_localized_text(
                language,
                {
                    "pl": "Mam juz podstawowe informacje o Twoim profilu.",
                    "uk": "\u0423 \u043c\u0435\u043d\u0435 \u0432\u0436\u0435 \u0454 \u0431\u0430\u0437\u043e\u0432\u0430 \u0456\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0456\u044f \u043f\u043e \u0432\u0430\u0448\u043e\u043c\u0443 \u043f\u0440\u043e\u0444\u0456\u043b\u044e.",
                    "ru": "\u0423 \u043c\u0435\u043d\u044f \u0443\u0436\u0435 \u0435\u0441\u0442\u044c \u0431\u0430\u0437\u043e\u0432\u0430\u044f \u0438\u043d\u0444\u043e\u0440\u043c\u0430\u0446\u0438\u044f \u043f\u043e \u0432\u0430\u0448\u0435\u0439 \u043a\u0430\u0440\u0442\u0435.",
                    "en": "I already have the basic profile details.",
                },
            ),
            next_question=None,
            language=language,
            audience=scenario,
        )
    reply = ai_response.get("reply")
    if reply and validate_one_question_rule(reply, language=language).valid:
        return reply
    return build_public_reply(
        acknowledgement=_acknowledgement(language, scenario),
        understood_summary=None,
        next_question=translations.get("intent.consultation.reply", "Describe the situation, and I will suggest the next step."),
        language=language,
        audience=scenario,
    )


def _known_fields_for_reply(profile: dict, employer_experience: dict | None, scenario: str) -> dict:
    if scenario == "employer":
        vacancy = profile.get("vacancy", {})
        employer = profile.get("employer", {})
        return {
            "workLocation": vacancy.get("location") or vacancy.get("country"),
            "workersCount": vacancy.get("quantity"),
            "requiredSkills": vacancy.get("requirements") or vacancy.get("profession"),
            "salaryOrRate": vacancy.get("salary"),
            "contractType": vacancy.get("contract_type"),
            "workingHours": vacancy.get("working_hours"),
            "accommodationProvided": vacancy.get("housing"),
            "startDate": vacancy.get("start_date"),
            "trainingPossibility": vacancy.get("training_possibility"),
            "companyName": employer.get("company_name"),
            "contactPerson": employer.get("contact_person"),
            "phoneOrEmail": employer.get("contact_phone") or employer.get("contact_email"),
            "nipOrRegon": employer.get("nip") or employer.get("regon") or employer.get("vat_id"),
        }
    return {
        "skills": profile.get("profession") or profile.get("skills"),
        "currentLocation": profile.get("country") or profile.get("city") or _last_message_mentions_current_location(profile),
        "experience": profile.get("experience_years"),
        "documentsLegalStatus": profile.get("documents")
        or profile.get("documents_status")
        or profile.get("residence_document_status"),
        "preferredContactMethod": profile.get("preferred_contact_method"),
        "phoneOrContact": profile.get("phone") or profile.get("phone_number") or profile.get("contact"),
        "drivingLicense": profile.get("driving_license"),
        "certificates": profile.get("certificates"),
        "relocationReadiness": profile.get("relocation_readiness"),
        "preferredDestination": profile.get("preferred_destination") or profile.get("desired_country"),
        "learningReadiness": profile.get("learning_readiness"),
        "desiredSalary": profile.get("desired_salary"),
        "startAvailability": profile.get("ready_from"),
        "accommodationNeed": profile.get("accommodation_need") or profile.get("housing"),
        "photoUpload": profile.get("photo"),
        "documentUpload": profile.get("document_files"),
    }


def _last_message_mentions_current_location(profile: dict) -> bool:
    messages = profile.get("messages") or []
    if not messages:
        return False
    text = str(messages[-1].get("content", "")).lower()
    location_markers = (
        "currently in",
        "now in",
        "i am in",
        "jestem w",
        "teraz w",
        "obecnie w",
        "\u0441\u0435\u0439\u0447\u0430\u0441 \u0432",
        "\u0441\u0435\u0439\u0447\u0430\u0441 \u0432\u043e",
        "\u044f \u0432 ",
        "\u0437\u0430\u0440\u0430\u0437 \u0443",
        "\u0437\u0430\u0440\u0430\u0437 \u0432",
        "\u044f \u0443 ",
    )
    return any(marker in text for marker in location_markers)


def _understood_summary(profile: dict, scenario: str, language: str, translations: dict[str, str]) -> str | None:
    if scenario == "employer":
        vacancy = profile.get("vacancy", {})
        profession = _display_profession(vacancy.get("profession"), language, translations)
        quantity = vacancy.get("quantity")
        if profession and quantity:
            return _localized_text(
                language,
                {
                    "pl": f"Szukasz: {profession}, liczba osob: {quantity}.",
                    "uk": f"\u0412\u0438 \u0448\u0443\u043a\u0430\u0454\u0442\u0435: {profession}, \u043a\u0456\u043b\u044c\u043a\u0456\u0441\u0442\u044c: {quantity}.",
                    "ru": f"\u0412\u044b \u0438\u0449\u0435\u0442\u0435: {profession}, \u043a\u043e\u043b\u0438\u0447\u0435\u0441\u0442\u0432\u043e: {quantity}.",
                    "en": f"You are looking for: {profession}, quantity: {quantity}.",
                },
            )
        if profession:
            return _localized_text(
                language,
                {
                    "pl": f"Szukasz specjalistow: {profession}.",
                    "uk": f"\u0412\u0438 \u0448\u0443\u043a\u0430\u0454\u0442\u0435 \u0444\u0430\u0445\u0456\u0432\u0446\u0456\u0432: {profession}.",
                    "ru": f"\u0412\u044b \u0438\u0449\u0435\u0442\u0435 \u0441\u043f\u0435\u0446\u0438\u0430\u043b\u0438\u0441\u0442\u043e\u0432: {profession}.",
                    "en": f"You are looking for specialists: {profession}.",
                },
            )
    if scenario == "candidate":
        profession = _display_profession(profile.get("profession"), language, translations)
        country = profile.get("country")
        if profession and country:
            return _localized_text(
                language,
                {
                    "pl": f"Zapisalem: {profession}, obecnie {country}.",
                    "uk": f"\u0417\u0430\u0444\u0456\u043a\u0441\u0443\u0432\u0430\u0432: {profession}, \u0437\u0430\u0440\u0430\u0437 {country}.",
                    "ru": f"\u0417\u0430\u0444\u0438\u043a\u0441\u0438\u0440\u043e\u0432\u0430\u043b: {profession}, \u0441\u0435\u0439\u0447\u0430\u0441 {country}.",
                    "en": f"I saved: {profession}, currently {country}.",
                },
            )
        if profession:
            return _localized_text(
                language,
                {
                    "pl": f"Zapisalem zawod: {profession}.",
                    "uk": f"\u0417\u0430\u0444\u0456\u043a\u0441\u0443\u0432\u0430\u0432 \u043f\u0440\u043e\u0444\u0435\u0441\u0456\u044e: {profession}.",
                    "ru": f"\u0417\u0430\u0444\u0438\u043a\u0441\u0438\u0440\u043e\u0432\u0430\u043b \u043f\u0440\u043e\u0444\u0435\u0441\u0441\u0438\u044e: {profession}.",
                    "en": f"I saved the profession: {profession}.",
                },
            )
    return None


def _acknowledgement(language: str, audience: str | None = None) -> str:
    return acknowledgement_for(language, audience)


def _localized_text(language: str | None, values: dict[str, str]) -> str:
    return values.get(language or "en") or values.get("en") or next(iter(values.values()))


def _display_profession(value: str | None, language: str | None, translations: dict[str, str]) -> str:
    if not value:
        return translations.get("crm.profession_unknown", "specialists")
    normalized = value.lower()
    labels = {
        "welder": {
            "pl": "spawaczy",
            "uk": "зварювальників",
            "ru": "сварщиков",
            "en": "welders",
            "de": "Schweisser",
            "es": "soldadores",
            "pt": "soldadores",
        },
        "construction worker": {
            "pl": "monterów",
            "uk": "монтажників",
            "ru": "монтажников",
            "en": "construction workers",
            "de": "Monteure",
            "es": "montadores",
            "pt": "montadores",
        },
        "production worker": {
            "pl": "pracowników produkcji",
            "uk": "працівників виробництва",
            "ru": "работников производства",
            "en": "production workers",
            "de": "Produktionsmitarbeiter",
            "es": "operarios de produccion",
            "pt": "operarios de producao",
        },
    }
    return labels.get(normalized, {}).get(language or "en", value)


def _build_employer_experience(profile: dict) -> dict:
    vacancy = profile.get("vacancy", {})
    employer = profile.get("employer", {})
    analysis = VacancyAnalyzer().analyze(vacancy)
    trust = EmployerTrustEngine().evaluate(employer=employer, vacancy=vacancy)
    advice_cards = RecruitmentAdvisor().build_cards(analysis)
    return {
        "vacancy_card": vacancy,
        "vacancy_quality": analysis,
        "advice_cards": advice_cards,
        "trust_score": trust,
        "dashboard": {
            "active_vacancies": 1 if vacancy else 0,
            "candidates_in_progress": int(vacancy.get("found", 0) or 0),
            "ready_to_start": int(vacancy.get("accepted", 0) or 0),
            "interviews": int(vacancy.get("interviews", 0) or 0),
            "document_risks": len([card for card in advice_cards if card["key"] == "advisor.certificates_recommended"]),
            "completed_projects": int(employer.get("completed_recruitments", 0) or 0),
            "match_progress": analysis["pipeline"],
        },
    }
