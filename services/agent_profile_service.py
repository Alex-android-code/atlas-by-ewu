"""Personal AI agent foundation for ATLAS users."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.models import (
    AgentAction,
    AgentMemoryRecord,
    AgentRecommendation,
    CareerGoal,
    ProfessionalDNA,
    Subscription,
    UserPreference,
    utc_now_iso,
)
from database.repositories import (
    AgentActionRepository,
    AgentMemoryRepository,
    AgentRecommendationRepository,
    CareerGoalRepository,
    ProfessionalDNARepository,
    SubscriptionRepository,
    UserPreferenceRepository,
)


ONBOARDING_FIELDS = [
    "full_name",
    "current_profession",
    "current_location",
    "work_experience",
    "skills",
    "certificates",
    "career_goal",
    "preferred_work",
    "salary_expectations",
    "relocation_readiness",
    "languages",
    "phone",
    "email",
    "profile_photo",
    "uploaded_cv",
]

MEMORY_TYPES = {
    "fact",
    "preference",
    "career_goal",
    "restriction",
    "document",
    "skill",
    "experience",
    "conversation_summary",
    "agent_observation",
}


class AgentProfileService:
    def __init__(
        self,
        profiles: ProfessionalDNARepository,
        memories: AgentMemoryRepository,
        actions: AgentActionRepository,
        recommendations: AgentRecommendationRepository,
        goals: CareerGoalRepository,
        preferences: UserPreferenceRepository,
        subscriptions: SubscriptionRepository,
    ) -> None:
        self.profiles = profiles
        self.memories = memories
        self.actions = actions
        self.recommendations = recommendations
        self.goals = goals
        self.preferences = preferences
        self.subscriptions = subscriptions

    def onboarding_schema(self, language: str = "uk") -> dict[str, Any]:
        return {
            "language": language,
            "mode": "agent_interview",
            "one_question_per_screen": True,
            "autosave": True,
            "fields": [
                {
                    "key": field,
                    "step": index + 1,
                    "total": len(ONBOARDING_FIELDS),
                    "question": _question_for(field, language),
                    "why": _why_for(field, language),
                }
                for index, field in enumerate(ONBOARDING_FIELDS)
            ],
        }

    def save_onboarding_answer(self, user_id: str, field: str, value: Any, language: str = "uk") -> dict[str, Any]:
        if field not in ONBOARDING_FIELDS:
            raise ValueError(f"Unknown onboarding field: {field}")
        profile = self.get_or_create_profile(user_id)
        _apply_onboarding_value(profile, field, value)
        profile.profile_completeness = self.calculate_completeness(profile)
        profile.updated_at = utc_now_iso()
        profile.metadata.setdefault("onboarding", {})[field] = {
            "value": value,
            "updated_at": profile.updated_at,
            "language": language,
        }
        self.profiles.update(profile)
        self._remember_onboarding_answer(user_id, field, value)
        return {
            "profile": profile.to_dict(),
            "progress": self.onboarding_progress(profile),
            "next_field": self.next_missing_field(profile),
            "completed": self.next_missing_field(profile) is None,
        }

    def complete_onboarding(self, user_id: str) -> dict[str, Any]:
        profile = self.get_or_create_profile(user_id)
        profile.profile_completeness = self.calculate_completeness(profile)
        profile.verification_status = "ready_for_review"
        profile.updated_at = utc_now_iso()
        self.profiles.update(profile)
        self._ensure_subscription(user_id)
        self._ensure_preferences(user_id)
        self._ensure_seed_recommendations(user_id, profile)
        self.actions.add(
            AgentAction(
                user_id=user_id,
                action_type="profile_map_started",
                title="Professional map formation started",
                status="test_mode",
                requires_user_confirmation=False,
            )
        )
        return {
            "message": "Ваш AI-агент створений. Тепер він починає формувати вашу професійну карту.",
            "dashboard": self.agent_dashboard(user_id),
        }

    def agent_dashboard(self, user_id: str) -> dict[str, Any]:
        profile = self.get_or_create_profile(user_id)
        subscription = self._ensure_subscription(user_id)
        recommendations = [item.to_dict() for item in self.recommendations.list() if item.user_id == user_id]
        actions = [item.to_dict() for item in self.actions.list() if item.user_id == user_id]
        memories = [item.to_dict() for item in self.memories.list() if item.user_id == user_id and item.is_active]
        return {
            "user_id": user_id,
            "agent": {
                "title": "Ваш AI-агент",
                "status": self.agent_status(profile),
                "activity": self.agent_activity(profile),
                "profile_completeness": profile.profile_completeness,
                "next_recommended_action": self.next_recommended_action(profile),
                "mode": "test_mode",
            },
            "professional_dna": profile.to_dict(),
            "recommendations": recommendations,
            "actions": actions[-10:],
            "memories": memories[-10:],
            "subscription": subscription.to_dict(),
            "feature_flags": subscription.feature_flags,
            "modules": self.dashboard_modules(subscription.plan),
        }

    def get_or_create_profile(self, user_id: str) -> ProfessionalDNA:
        for profile in self.profiles.list():
            if profile.user_id == user_id:
                return profile
        profile = ProfessionalDNA(user_id=user_id)
        self.profiles.add(profile)
        return profile

    def calculate_completeness(self, profile: ProfessionalDNA) -> int:
        completed = 0
        for field in ONBOARDING_FIELDS:
            if _profile_has_field(profile, field):
                completed += 1
        return round(completed / len(ONBOARDING_FIELDS) * 100)

    def onboarding_progress(self, profile: ProfessionalDNA) -> dict[str, int]:
        completed = sum(1 for field in ONBOARDING_FIELDS if _profile_has_field(profile, field))
        return {
            "completed": completed,
            "total": len(ONBOARDING_FIELDS),
            "percent": self.calculate_completeness(profile),
        }

    def next_missing_field(self, profile: ProfessionalDNA) -> str | None:
        for field in ONBOARDING_FIELDS:
            if not _profile_has_field(profile, field):
                return field
        return None

    def agent_status(self, profile: ProfessionalDNA) -> str:
        if profile.profile_completeness < 40:
            return "Формую вашу професійну карту"
        if profile.profile_completeness < 80:
            return "Аналізую ваш досвід"
        if profile.verification_status != "verified":
            return "Перевіряю повноту вашого профілю"
        return "Готую рекомендації для підвищення вашої ринкової цінності"

    def agent_activity(self, profile: ProfessionalDNA) -> str:
        if self.next_missing_field(profile):
            return "Очікую наступну відповідь в onboarding-інтерв'ю"
        return "Професійна карта сформована у тестовому режимі"

    def next_recommended_action(self, profile: ProfessionalDNA) -> str:
        next_field = self.next_missing_field(profile)
        if next_field:
            return f"Продовжити інтерв'ю: {next_field}"
        if profile.verification_status != "verified":
            return "Передати Professional DNA на перевірку координатору"
        return "Переглянути персональні рекомендації"

    def dashboard_modules(self, plan: str) -> list[dict[str, str]]:
        return [
            {"key": "my_ai_agent", "title": "Мій AI-агент", "status": "active"},
            {"key": "professional_dna", "title": "Professional DNA", "status": "active"},
            {"key": "opportunities", "title": "Мої можливості", "status": "test_mode"},
            {"key": "documents", "title": "Документи", "status": "test_mode"},
            {"key": "career_strategy", "title": "Кар'єрна стратегія", "status": "test_mode" if plan != "start" else "in_development"},
            {"key": "agent_settings", "title": "Налаштування агента", "status": "active"},
        ]

    def _remember_onboarding_answer(self, user_id: str, field: str, value: Any) -> None:
        memory_type = _memory_type_for(field)
        content = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
        self.memories.add(
            AgentMemoryRecord(
                user_id=user_id,
                memory_type=memory_type,
                content=f"{field}: {content}",
                source="onboarding",
                importance=3 if field in {"career_goal", "skills", "work_experience"} else 2,
            )
        )

    def _ensure_subscription(self, user_id: str) -> Subscription:
        for subscription in self.subscriptions.list():
            if subscription.user_id == user_id:
                return subscription
        subscription = Subscription(
            user_id=user_id,
            plan="start",
            feature_flags=load_subscription_features("start"),
        )
        self.subscriptions.add(subscription)
        return subscription

    def _ensure_preferences(self, user_id: str) -> UserPreference:
        for preference in self.preferences.list():
            if preference.user_id == user_id:
                return preference
        preference = UserPreference(user_id=user_id)
        self.preferences.add(preference)
        return preference

    def _ensure_seed_recommendations(self, user_id: str, profile: ProfessionalDNA) -> None:
        existing = [item for item in self.recommendations.list() if item.user_id == user_id]
        if existing:
            return
        self.recommendations.add(
            AgentRecommendation(
                user_id=user_id,
                recommendation_type="profile",
                title="Завершити перевірку Professional DNA",
                rationale="Агент має достатньо даних для першої професійної карти, але потрібна верифікація.",
            )
        )
        if profile.uploaded_cv:
            self.recommendations.add(
                AgentRecommendation(
                    user_id=user_id,
                    recommendation_type="document",
                    title="Перевірити CV перед рекомендаціями",
                    rationale="CV додано до профілю. Наступний крок - перевірка якості та відповідності цілі.",
                )
            )


def load_subscription_features(plan: str) -> dict[str, bool]:
    path = Path(__file__).resolve().parents[1] / "configs" / "subscriptions.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    return dict(data["plans"].get(plan, data["plans"]["start"])["features"])


def _apply_onboarding_value(profile: ProfessionalDNA, field: str, value: Any) -> None:
    if field == "full_name":
        profile.personal_information["full_name"] = value
    elif field == "current_profession":
        profile.professional_summary = str(value)
        profile.preferred_roles = profile.preferred_roles or [str(value)]
    elif field == "current_location":
        profile.current_location = _value_to_location(value)
    elif field == "work_experience":
        profile.work_experience = [{"summary": value}]
    elif field == "skills":
        profile.skills = _value_to_list(value)
    elif field == "certificates":
        profile.certificates = [{"title": item} for item in _value_to_list(value)]
    elif field == "career_goal":
        profile.career_goals = [{"title": value, "status": "active"}]
    elif field == "preferred_work":
        profile.relocation_preferences["preferred_work"] = value
    elif field == "salary_expectations":
        profile.salary_expectations["expected"] = value
    elif field == "relocation_readiness":
        profile.relocation_preferences["readiness"] = value
    elif field == "languages":
        profile.languages = [{"name": item} for item in _value_to_list(value)]
    elif field == "phone":
        profile.contact_information["phone"] = value
    elif field == "email":
        profile.contact_information["email"] = value
    elif field == "profile_photo":
        profile.profile_photo = {"status": "provided" if value else "missing", "value": value}
    elif field == "uploaded_cv":
        profile.uploaded_cv = {"status": "provided" if value else "missing", "value": value}


def _profile_has_field(profile: ProfessionalDNA, field: str) -> bool:
    checks = {
        "full_name": bool(profile.personal_information.get("full_name")),
        "current_profession": bool(profile.professional_summary),
        "current_location": bool(profile.current_location),
        "work_experience": bool(profile.work_experience),
        "skills": bool(profile.skills),
        "certificates": bool(profile.certificates),
        "career_goal": bool(profile.career_goals),
        "preferred_work": bool(profile.relocation_preferences.get("preferred_work")),
        "salary_expectations": bool(profile.salary_expectations),
        "relocation_readiness": bool(profile.relocation_preferences.get("readiness")),
        "languages": bool(profile.languages),
        "phone": bool(profile.contact_information.get("phone")),
        "email": bool(profile.contact_information.get("email")),
        "profile_photo": bool(profile.profile_photo),
        "uploaded_cv": bool(profile.uploaded_cv),
    }
    return checks[field]


def _value_to_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in str(value).split(",") if item.strip()]


def _value_to_location(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    parts = [part.strip() for part in str(value).split(",") if part.strip()]
    return {"country": parts[0] if parts else "", "city": parts[1] if len(parts) > 1 else ""}


def _memory_type_for(field: str) -> str:
    if field in {"career_goal", "preferred_work", "salary_expectations"}:
        return "career_goal"
    if field in {"skills", "languages", "certificates"}:
        return "skill"
    if field == "work_experience":
        return "experience"
    if field in {"profile_photo", "uploaded_cv"}:
        return "document"
    return "fact"


def _question_for(field: str, language: str) -> str:
    questions = {
        "full_name": "Як вас звати?",
        "current_profession": "Яка ваша поточна професія або головна компетенція?",
        "current_location": "У якій країні та місті ви зараз перебуваєте?",
        "work_experience": "Опишіть коротко ваш досвід роботи.",
        "skills": "Які ключові навички агент має запам'ятати?",
        "certificates": "Які сертифікати, дозволи або ліцензії у вас є?",
        "career_goal": "Яка ваша головна професійна ціль?",
        "preferred_work": "Яка країна або формат роботи вам цікаві?",
        "salary_expectations": "Який дохід ви очікуєте?",
        "relocation_readiness": "Чи готові ви до переїзду?",
        "languages": "Якими мовами ви володієте?",
        "phone": "Який номер телефону використати для зв'язку?",
        "email": "Яку електронну пошту додати до профілю?",
        "profile_photo": "Додайте фото профілю або пропустіть цей крок.",
        "uploaded_cv": "Завантажте CV, якщо воно вже є.",
    }
    return questions[field]


def _why_for(field: str, language: str) -> str:
    return "Агент використовує цю відповідь, щоб поступово сформувати вашу Professional DNA."
