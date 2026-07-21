"""Persisted user onboarding workflow for ATLAS AI agent profiles."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from core.models import ConsentRecord, Document, DocumentStatus, new_id, utc_now_iso
from database.json_database import JsonDatabase
from database.repositories import ActivityRepository, ConsentRepository, DocumentRepository
from services.agent_profile_service import AgentProfileService


ONBOARDING_STEPS = [
    "welcome",
    "agent",
    "profile_photo",
    "cv",
    "personal_data",
    "profession",
    "experience",
    "education",
    "languages",
    "preferences",
    "consents",
    "professional_dna",
    "completed",
]

SESSION_COLLECTION = "onboarding_sessions"
CV_JOB_COLLECTION = "cv_parse_jobs"
DNA_COLLECTION = "professional_dna_scores"


@dataclass
class OnboardingWorkflowService:
    database: JsonDatabase
    agent_profiles: AgentProfileService
    consents: ConsentRepository
    documents: DocumentRepository
    activity: ActivityRepository

    def get_or_start(self, user_id: str) -> dict[str, Any]:
        session = self.database.get(SESSION_COLLECTION, user_id)
        if not session:
            session = {
                "id": new_id("ONB"),
                "user_id": user_id,
                "status": "not_started",
                "current_step": "welcome",
                "completed_steps": [],
                "data": {},
                "parsed_cv": None,
                "consents": {},
                "professional_dna": None,
                "audit_log": [_audit("session_created", "welcome")],
                "created_at": utc_now_iso(),
                "updated_at": utc_now_iso(),
                "completed_at": None,
            }
            self.database.insert(SESSION_COLLECTION, user_id, session)
        return self._with_progress(session)

    def patch_step(
        self,
        user_id: str,
        *,
        step: str,
        data: dict[str, Any] | None = None,
        next_step: str | None = None,
    ) -> dict[str, Any]:
        self._validate_step(step)
        session = self.get_or_start(user_id)
        session["status"] = "completed" if session.get("status") == "completed" else "in_progress"
        session.setdefault("data", {})[step] = data or {}
        if step not in session.setdefault("completed_steps", []):
            session["completed_steps"].append(step)
        if step == "consents":
            session["consents"] = self._store_consents(user_id, data or {})
        if step == "profile_photo" and (data or {}).get("file"):
            self.agent_profiles.save_onboarding_answer(user_id, "profile_photo", data["file"])
        if step == "cv" and (data or {}).get("file"):
            self.agent_profiles.save_onboarding_answer(user_id, "uploaded_cv", data["file"])
            self._ensure_document_record(user_id, data["file"], "cv")
        self._sync_step_to_profile(user_id, step, data or {})
        session["current_step"] = next_step if next_step in ONBOARDING_STEPS else self._next_step(step)
        session["updated_at"] = utc_now_iso()
        session.setdefault("audit_log", []).append(_audit("step_saved", step))
        self.database.update(SESSION_COLLECTION, user_id, session)
        return self._with_progress(session)

    def parse_cv(self, user_id: str, file_id: str) -> dict[str, Any]:
        session = self.get_or_start(user_id)
        cv_data = session.get("data", {}).get("cv", {})
        file_data = cv_data.get("file") or {}
        if file_id != file_data.get("id"):
            raise ValueError("CV file is not attached to this onboarding session")
        parsed = _deterministic_cv_parse(file_data, session.get("data", {}))
        job = {
            "id": new_id("CVP"),
            "user_id": user_id,
            "file_id": file_id,
            "status": "completed",
            "result": parsed,
            "created_at": utc_now_iso(),
            "updated_at": utc_now_iso(),
        }
        self.database.insert(CV_JOB_COLLECTION, job["id"], job)
        session["parsed_cv"] = {"job_id": job["id"], "status": "completed", "result": parsed}
        session.setdefault("audit_log", []).append(_audit("cv_parse_completed", "cv"))
        session["updated_at"] = utc_now_iso()
        self.database.update(SESSION_COLLECTION, user_id, session)
        return job

    def get_parse_job(self, user_id: str, job_id: str) -> dict[str, Any]:
        job = self.database.get(CV_JOB_COLLECTION, job_id)
        if not job or job.get("user_id") != user_id:
            raise ValueError("CV parse job not found")
        return job

    def accept_cv_parse(self, user_id: str, accepted: dict[str, Any]) -> dict[str, Any]:
        session = self.get_or_start(user_id)
        session.setdefault("data", {}).setdefault("cv", {})["accepted_parsed_data"] = accepted
        session.setdefault("audit_log", []).append(_audit("cv_parse_accepted", "cv"))
        session["updated_at"] = utc_now_iso()
        self.database.update(SESSION_COLLECTION, user_id, session)
        self._sync_step_to_profile(user_id, "cv", {"accepted_parsed_data": accepted})
        return self._with_progress(session)

    def generate_dna(self, user_id: str) -> dict[str, Any]:
        session = self.get_or_start(user_id)
        dna = _score_professional_dna(session.get("data", {}))
        session["professional_dna"] = dna
        session.setdefault("data", {})["professional_dna"] = dna
        session["current_step"] = "professional_dna"
        session["updated_at"] = utc_now_iso()
        session.setdefault("audit_log", []).append(_audit("professional_dna_generated", "professional_dna"))
        self.database.update(SESSION_COLLECTION, user_id, session)
        self.database.update(DNA_COLLECTION, user_id, {"user_id": user_id, **dna})
        profile = self.agent_profiles.get_or_create_profile(user_id)
        profile.profile_completeness = int(dna["profileCompleteness"])
        profile.strengths = dna["strengths"]
        profile.development_areas = dna["gaps"]
        profile.metadata["professional_dna_v1"] = dna
        self.agent_profiles.profiles.update(profile)
        return dna

    def get_dna(self, user_id: str) -> dict[str, Any]:
        dna = self.database.get(DNA_COLLECTION, user_id)
        if dna:
            return dna
        return self.generate_dna(user_id)

    def complete(self, user_id: str) -> dict[str, Any]:
        session = self.get_or_start(user_id)
        if not session.get("professional_dna"):
            session["professional_dna"] = self.generate_dna(user_id)
        session["status"] = "completed"
        session["current_step"] = "completed"
        if "completed" not in session.setdefault("completed_steps", []):
            session["completed_steps"].append("completed")
        session["completed_at"] = session.get("completed_at") or utc_now_iso()
        session["updated_at"] = utc_now_iso()
        session.setdefault("audit_log", []).append(_audit("onboarding_completed", "completed"))
        self.database.update(SESSION_COLLECTION, user_id, session)
        dashboard = self.agent_profiles.complete_onboarding(user_id)
        return {"session": self._with_progress(session), "dashboard": dashboard.get("dashboard", {})}

    def _sync_step_to_profile(self, user_id: str, step: str, data: dict[str, Any]) -> None:
        if step == "agent":
            profile = self.agent_profiles.get_or_create_profile(user_id)
            profile.metadata["ai_agent"] = data
            profile.agent_memory.append(f"AI agent configured: {data.get('name') or 'ATLAS Agent'}")
            self.agent_profiles.profiles.update(profile)
        if step == "personal_data":
            for field, value in {
                "full_name": data.get("fullName") or data.get("full_name"),
                "email": data.get("email"),
                "phone": data.get("phone"),
                "current_location": data.get("location"),
            }.items():
                if value:
                    self.agent_profiles.save_onboarding_answer(user_id, field, value)
        if step == "profession":
            if data.get("headline") or data.get("profession"):
                self.agent_profiles.save_onboarding_answer(user_id, "current_profession", data.get("headline") or data.get("profession"))
            if data.get("skills"):
                self.agent_profiles.save_onboarding_answer(user_id, "skills", ", ".join(data.get("skills", [])))
        if step == "experience" and data.get("records"):
            self.agent_profiles.save_onboarding_answer(user_id, "work_experience", data["records"])
        if step == "education" and (data.get("records") or data.get("certificates")):
            self.agent_profiles.save_onboarding_answer(user_id, "certificates", data)
        if step == "languages" and data.get("records"):
            self.agent_profiles.save_onboarding_answer(user_id, "languages", data["records"])
        if step == "preferences":
            if data.get("careerGoal"):
                self.agent_profiles.save_onboarding_answer(user_id, "career_goal", data["careerGoal"])
            if data.get("countries"):
                self.agent_profiles.save_onboarding_answer(user_id, "relocation_readiness", data.get("countries"))
            if data.get("salary"):
                self.agent_profiles.save_onboarding_answer(user_id, "salary_expectations", data.get("salary"))

    def _store_consents(self, user_id: str, data: dict[str, Any]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        version = str(data.get("version") or "atlas-rodo-v1")
        language = str(data.get("language") or "uk")
        tech_id = _tech_id(user_id)
        for key, required in {"terms": True, "privacy": True, "aiProcessing": True, "marketing": False, "analytics": False}.items():
            accepted = bool(data.get(key))
            if required and not accepted:
                raise ValueError(f"Required consent is missing: {key}")
            consent = ConsentRecord(
                subject_id=user_id,
                consent_version=version,
                language=language,
                source="agent_onboarding",
                scopes=[key],
                accepted=accepted,
                metadata={"required": required, "technical_id": tech_id, "withdrawnAt": None},
            )
            self.consents.add(consent)
            result[key] = consent.to_dict()
        return result

    def _ensure_document_record(self, user_id: str, file_data: dict[str, Any], document_type: str) -> None:
        if not file_data.get("id"):
            return
        existing = [
            item
            for item in self.documents.list()
            if item.owner_id == user_id and item.metadata.get("onboarding_file_id") == file_data["id"]
        ]
        if existing:
            return
        self.documents.add(
            Document(
                owner_id=user_id,
                document_type=document_type,
                country_code="GLOBAL",
                status=DocumentStatus.SUBMITTED,
                file_path=file_data.get("stored_name"),
                metadata={"onboarding_file_id": file_data["id"], "original_name": file_data.get("original_name")},
            )
        )

    @staticmethod
    def _validate_step(step: str) -> None:
        if step not in ONBOARDING_STEPS:
            raise ValueError(f"Unknown onboarding step: {step}")

    @staticmethod
    def _next_step(step: str) -> str:
        index = ONBOARDING_STEPS.index(step)
        return ONBOARDING_STEPS[min(index + 1, len(ONBOARDING_STEPS) - 1)]

    @staticmethod
    def _with_progress(session: dict[str, Any]) -> dict[str, Any]:
        completed = len(set(session.get("completed_steps", [])) & set(ONBOARDING_STEPS[:-1]))
        total = len(ONBOARDING_STEPS) - 1
        return {
            **session,
            "steps": ONBOARDING_STEPS,
            "progress": {
                "completed": completed,
                "total": total,
                "percent": min(100, round((completed / total) * 100)),
            },
        }


def _deterministic_cv_parse(file_data: dict[str, Any], onboarding_data: dict[str, Any]) -> dict[str, Any]:
    personal = onboarding_data.get("personal_data", {})
    profession = onboarding_data.get("profession", {})
    filename = file_data.get("original_name", "")
    return {
        "fullName": _value(personal.get("fullName"), "personal_data.fullName"),
        "email": _value(personal.get("email"), "personal_data.email"),
        "phone": _value(personal.get("phone"), "personal_data.phone"),
        "location": _value(personal.get("location"), "personal_data.location"),
        "headline": _value(profession.get("headline") or profession.get("profession"), "profession.headline"),
        "summary": _value("", "not_found"),
        "professions": _list_value([profession.get("profession")] if profession.get("profession") else [], "profession.profession"),
        "skills": _list_value(profession.get("skills") or [], "profession.skills"),
        "workExperience": onboarding_data.get("experience", {}).get("records", []),
        "education": onboarding_data.get("education", {}).get("records", []),
        "certificates": onboarding_data.get("education", {}).get("certificates", []),
        "languages": onboarding_data.get("languages", {}).get("records", []),
        "source": {"fileId": file_data.get("id"), "fileName": filename},
        "confidence": "low" if not personal and not profession else "medium",
        "warnings": ["ATLAS extracted only confirmed onboarding facts and did not invent missing CV data."],
    }


def _score_professional_dna(data: dict[str, Any]) -> dict[str, Any]:
    scores = {
        "profileCompleteness": _completeness_score(data),
        "experienceScore": _presence_score(data.get("experience", {}).get("records"), 14),
        "skillsScore": _presence_score(data.get("profession", {}).get("skills"), 14),
        "educationScore": _presence_score(data.get("education", {}).get("records"), 10),
        "languagesScore": _presence_score(data.get("languages", {}).get("records"), 10),
        "mobilityScore": _presence_score(data.get("preferences", {}).get("countries"), 8),
        "documentReadinessScore": 10 if data.get("cv", {}).get("file") else 0,
        "marketReadinessScore": _presence_score(data.get("preferences", {}).get("careerGoal"), 10),
    }
    overall = min(100, round(sum(scores.values()) / 86 * 100))
    strengths: list[str] = []
    if scores["skillsScore"]:
        strengths.append("Skills are declared and ready for normalization.")
    if scores["documentReadinessScore"]:
        strengths.append("CV is attached to the candidate profile.")
    if scores["languagesScore"]:
        strengths.append("Language profile includes CEFR readiness.")
    gaps: list[str] = []
    if not scores["experienceScore"]:
        gaps.append("Add at least one work experience record.")
    if not scores["educationScore"]:
        gaps.append("Add education, courses, certificates, or licenses.")
    if not scores["mobilityScore"]:
        gaps.append("Set preferred countries and relocation model.")
    actions = [
        "Review parsed CV data before publishing the profile.",
        "Attach certificates or licenses if they are required for the target country.",
        "Keep GDPR/RODO consents current in the privacy center.",
    ]
    return {
        "overallScore": overall,
        **scores,
        "strengths": strengths or ["Profile foundation is created."],
        "gaps": gaps,
        "recommendedActions": actions,
        "generatedAt": utc_now_iso(),
        "version": "professional_dna_v1_rule_based",
    }


def _completeness_score(data: dict[str, Any]) -> int:
    required = [
        data.get("agent"),
        data.get("profile_photo", {}).get("file"),
        data.get("cv", {}).get("file"),
        data.get("personal_data"),
        data.get("profession"),
        data.get("experience", {}).get("records"),
        data.get("education", {}).get("records"),
        data.get("languages", {}).get("records"),
        data.get("preferences"),
        data.get("consents"),
    ]
    return round((sum(1 for item in required if item) / len(required)) * 100)


def _presence_score(value: Any, max_score: int) -> int:
    return max_score if value else 0


def _value(value: Any, source: str) -> dict[str, Any]:
    return {"value": value or "", "source": source, "confidence": "medium" if value else "low"}


def _list_value(value: list[Any], source: str) -> dict[str, Any]:
    return {"value": [item for item in value if item], "source": source, "confidence": "medium" if value else "low"}


def _audit(action: str, step: str) -> dict[str, Any]:
    return {"action": action, "step": step, "timestamp": utc_now_iso()}


def _tech_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:24]
