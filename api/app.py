"""FastAPI application for ATLAS/EWU."""

import os
from pathlib import Path
from time import time

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from ai.ai_gateway import get_default_ai_gateway, send_message_to_ai
from api.agent import AGENT_DASHBOARD_HTML, AGENT_ONBOARDING_HTML
from api.chat import AI_CHAT_HTML
from api.dashboard import DASHBOARD_HTML
from api.dependencies import get_agent_profile_service, get_crm_service, get_operations_workflow
from api.employer import EMPLOYER_HTML
from api.landing import LANDING_HTML
from api.login import LOGIN_HTML
from api.schemas import (
    AIChatRequest,
    AIMessageRequest,
    AgentOnboardingAnswer,
    AgentOnboardingComplete,
    AnalyticsEventCreate,
    CandidateCreate,
    EmployerCreate,
    LoginRequest,
    MatchRequest,
    StatusUpdate,
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

_AI_MESSAGE_RATE_LIMIT: dict[str, list[float]] = {}
AI_MESSAGE_LIMIT_PER_MINUTE = 20


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
    if request.cookies.get("atlas_role") not in {"owner", "admin", "coordinator"}:
        return LOGIN_HTML
    return DASHBOARD_HTML


@app.post("/api/login")
def api_login(payload: LoginRequest, response: Response) -> dict[str, str]:
    if payload.password != "atlas":
        raise HTTPException(status_code=401, detail="Invalid access code")
    response.set_cookie("atlas_role", "admin", httponly=True, samesite="lax")
    return {"status": "ok", "role": "admin"}


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "atlas_ewu"}


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
    prompt = build_structured_prompt(
        language=language,
        user_role=payload.role,
        current_step=payload.current_step,
        profile_data=payload.profile_data,
        recent_messages=payload.recent_messages,
        task=payload.task,
    )
    prompt = f"{prompt}\n\nUser message:\n{message}"
    service = GeminiService()
    try:
        result = service.generate_json(prompt, language=language)
        return {
            "success": True,
            "message": result.message,
            "next_field": result.next_field,
            "profile_updates": result.profile_updates,
            "warnings": result.warnings,
            "confidence": result.confidence,
            "provider": "gemini",
            "model": service.model,
            "fallback_used": False,
        }
    except Exception as error:
        return {
            "success": False,
            "message": fallback_message(language),
            "next_field": None,
            "profile_updates": {},
            "warnings": ["ai_unavailable"],
            "provider": "gemini",
            "model": service.model,
            "fallback_used": True,
            "error_type": getattr(error, "error_type", "unknown"),
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
    return get_agent_profile_service().complete_onboarding(payload.user_id)


@app.get("/api/agent/dashboard/{user_id}")
def get_agent_dashboard(user_id: str) -> dict:
    return get_agent_profile_service().agent_dashboard(user_id)


@app.get("/api/subscriptions/features/{plan}")
def get_subscription_features(plan: str) -> dict:
    from services.agent_profile_service import load_subscription_features

    return {"plan": plan, "features": load_subscription_features(plan)}


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
    return {
        "reply": assistant_reply,
        "ai": ai_response,
        "profile": profile,
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
def get_dashboard() -> dict:
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
def list_candidates() -> list[dict]:
    return [candidate.to_dict() for candidate in get_crm_service().candidates.list()]


@app.post("/api/candidates")
def create_candidate(payload: CandidateCreate) -> dict:
    candidate = Candidate(**payload.model_dump())
    return get_operations_workflow().onboard_candidate(candidate)


@app.patch("/api/candidates/{candidate_id}/status")
def update_candidate_status(candidate_id: str, payload: StatusUpdate) -> dict:
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
def mark_candidate_documents_received(candidate_id: str, payload: StatusUpdate | None = None) -> dict:
    request = payload or StatusUpdate(status="ready_for_matching", note="Documents received")
    try:
        candidate = get_crm_service().mark_candidate_documents_received(
            candidate_id,
            actor_id=request.actor_id,
            note=request.note or "Documents received",
        )
        return {"candidate": candidate.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/api/employers")
def list_employers() -> list[dict]:
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
def verify_employer(employer_id: str, payload: VerificationUpdate | None = None) -> dict:
    request = payload or VerificationUpdate()
    try:
        employer = get_crm_service().set_employer_verified(
            employer_id,
            verified=request.verified,
            actor_id=request.actor_id,
            note=request.note,
        )
        return {"employer": employer.to_dict()}
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/api/vacancies")
def list_vacancies() -> list[dict]:
    return [vacancy.to_dict() for vacancy in get_crm_service().vacancies.list()]


@app.post("/api/vacancies")
def create_vacancy(payload: VacancyCreate) -> dict:
    vacancy = Vacancy(**payload.model_dump())
    return get_operations_workflow().publish_vacancy(vacancy)


@app.patch("/api/vacancies/{vacancy_id}/status")
def update_vacancy_status(vacancy_id: str, payload: StatusUpdate) -> dict:
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
def match_vacancy(vacancy_id: str, payload: MatchRequest | None = None) -> dict:
    request = payload or MatchRequest()
    try:
        return get_operations_workflow().run_matching_for_vacancy(
            vacancy_id,
            minimum_score=request.minimum_score,
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error


@app.get("/api/matches")
def list_matches() -> list[dict]:
    return [match.to_dict() for match in get_crm_service().matches.list()]


@app.patch("/api/matches/{match_id}/status")
def update_match_status(match_id: str, payload: StatusUpdate) -> dict:
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
def list_activity(limit: int = 50) -> list[dict]:
    return [event.to_dict() for event in get_crm_service().list_activity(limit=limit)]


def _require_admin(request: Request) -> None:
    role = request.cookies.get("atlas_role")
    token = request.headers.get("x-atlas-admin-token")
    expected_token = os.getenv("ATLAS_ADMIN_TOKEN")
    if role in {"owner", "admin"}:
        return
    if expected_token and token == expected_token:
        return
    raise HTTPException(status_code=403, detail="Admin access required")


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
