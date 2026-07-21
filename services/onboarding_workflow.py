"""Persisted user onboarding workflow for ATLAS AI agent profiles."""

from __future__ import annotations

import hashlib
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from xml.etree import ElementTree

from core.models import ActivityEvent, ConsentRecord, Document, DocumentStatus, new_id, utc_now_iso
from database.json_database import JsonDatabase
from database.repositories import ActivityRepository, ConsentRepository, DocumentRepository
from services.agent_profile_service import AgentProfileService


ONBOARDING_STEPS = [
    "welcome",
    "agent",
    "profile_photo",
    "cv",
    "cv_review",
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
            self._ensure_document_record(user_id, data["file"], "profile_photo")
        if step == "cv" and (data or {}).get("file"):
            self.agent_profiles.save_onboarding_answer(user_id, "uploaded_cv", data["file"])
            self._ensure_document_record(user_id, data["file"], "cv")
        if step == "cv_review":
            if (data or {}).get("accepted_parsed_data"):
                session.setdefault("data", {}).setdefault("cv", {})["accepted_parsed_data"] = data["accepted_parsed_data"]
                session.setdefault("data", {}).setdefault("cv", {})["parse_rejected"] = False
                self.accept_cv_parse(user_id, data["accepted_parsed_data"], action="accept_selected", job_id=(data or {}).get("job_id"))
            elif (data or {}).get("rejected"):
                session.setdefault("data", {}).setdefault("cv", {})["accepted_parsed_data"] = {}
                session.setdefault("data", {}).setdefault("cv", {})["parse_rejected"] = True
                self.accept_cv_parse(user_id, {}, action="reject", job_id=(data or {}).get("job_id"))
        self._sync_step_to_profile(user_id, step, data or {})
        session["current_step"] = next_step if next_step in ONBOARDING_STEPS else self._next_step(step)
        session["updated_at"] = utc_now_iso()
        session.setdefault("audit_log", []).append(_audit("step_saved", step))
        self.database.update(SESSION_COLLECTION, user_id, session)
        self._record_activity(user_id, "onboarding_step_saved", step)
        return self._with_progress(session)

    def parse_cv(self, user_id: str, file_id: str, file_path: Path | None = None) -> dict[str, Any]:
        session = self.get_or_start(user_id)
        cv_data = session.get("data", {}).get("cv", {})
        file_data = cv_data.get("file") or {}
        if file_id != file_data.get("id"):
            raise ValueError("CV file is not attached to this onboarding session")
        now = utc_now_iso()
        job = {
            "id": new_id("CVP"),
            "user_id": user_id,
            "file_id": file_id,
            "status": "processing",
            "progress": 35,
            "result": None,
            "error": None,
            "warnings": [],
            "created_at": now,
            "started_at": now,
            "completed_at": None,
            "updated_at": now,
        }
        self.database.insert(CV_JOB_COLLECTION, job["id"], job)
        cv_text = _extract_cv_text(file_path, file_data) if file_path else ""
        parsed = _deterministic_cv_parse(file_data, session.get("data", {}), cv_text)
        completed_at = utc_now_iso()
        job.update(
            {
                "status": "completed",
                "progress": 100,
                "result": parsed,
                "warnings": parsed.get("warnings", []),
                "completed_at": completed_at,
                "updated_at": completed_at,
            }
        )
        self.database.update(CV_JOB_COLLECTION, job["id"], job)
        session["parsed_cv"] = {"job_id": job["id"], "status": "completed", "progress": 100, "result": parsed}
        session.setdefault("audit_log", []).append(_audit("cv_parse_completed", "cv"))
        session["updated_at"] = utc_now_iso()
        self.database.update(SESSION_COLLECTION, user_id, session)
        self._record_activity(user_id, "cv_parse_completed", "cv")
        return job

    def get_parse_job(self, user_id: str, job_id: str) -> dict[str, Any]:
        job = self.database.get(CV_JOB_COLLECTION, job_id)
        if not job or job.get("user_id") != user_id:
            raise ValueError("CV parse job not found")
        return job

    def accept_cv_parse(
        self,
        user_id: str,
        accepted: dict[str, Any],
        *,
        action: str = "accept_selected",
        job_id: str | None = None,
    ) -> dict[str, Any]:
        if action not in {"accept_all", "accept_selected", "reject"}:
            raise ValueError(f"Unsupported CV parse action: {action}")
        session = self.get_or_start(user_id)
        cv_state = session.setdefault("data", {}).setdefault("cv", {})
        if action == "reject":
            cv_state["accepted_parsed_data"] = {}
            cv_state["parse_rejected"] = True
            audit_action = "cv_parse_rejected"
            job_status = "rejected"
        else:
            sanitized = _sanitize_confirmed_cv_fields(accepted)
            cv_state["accepted_parsed_data"] = sanitized
            cv_state["parse_rejected"] = False
            self._apply_accepted_cv_to_session(session, sanitized)
            self._sync_accepted_cv_to_profile(user_id, sanitized)
            accepted = sanitized
            audit_action = "cv_parse_accepted"
            job_status = "accepted"
        resolved_job_id = job_id or session.get("parsed_cv", {}).get("job_id")
        if resolved_job_id:
            job = self.database.get(CV_JOB_COLLECTION, resolved_job_id)
            if job and job.get("user_id") == user_id:
                job["status"] = job_status
                job["decision"] = {"action": action, "accepted_fields": sorted(accepted.keys())}
                job["updated_at"] = utc_now_iso()
                self.database.update(CV_JOB_COLLECTION, resolved_job_id, job)
                if session.get("parsed_cv", {}).get("job_id") == resolved_job_id:
                    session["parsed_cv"]["status"] = job_status
                    session["parsed_cv"]["decision"] = job["decision"]
        session.setdefault("audit_log", []).append(_audit(audit_action, "cv"))
        session["updated_at"] = utc_now_iso()
        self.database.update(SESSION_COLLECTION, user_id, session)
        self._record_activity(user_id, audit_action, "cv")
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
        self._record_activity(user_id, "onboarding_completed", "completed")
        return {"session": self._with_progress(session), "dashboard": dashboard.get("dashboard", {})}

    def dashboard(self, user_id: str) -> dict[str, Any]:
        session = self.get_or_start(user_id)
        profile = self.agent_profiles.get_or_create_profile(user_id).to_dict()
        dna = session.get("professional_dna") or self.database.get(DNA_COLLECTION, user_id)
        documents = [
            item.to_dict()
            for item in self.documents.list()
            if item.owner_id == user_id and item.metadata.get("onboarding_file_id")
        ]
        agent = profile.get("metadata", {}).get("ai_agent", {})
        recommendations = []
        if dna:
            recommendations = [
                {"type": "rule_based", "title": item, "source": dna.get("version", "professional_dna_v1_rule_based")}
                for item in dna.get("recommendedActions", [])
            ]
        return {
            "user_id": user_id,
            "onboarding": {
                "status": session.get("status"),
                "current_step": session.get("current_step"),
                "progress": session.get("progress"),
                "completed_at": session.get("completed_at"),
            },
            "agent": {
                "name": agent.get("name") or "ATLAS Agent",
                "language": agent.get("language") or "uk",
                "style": agent.get("style") or "professional",
                "goal": agent.get("goal") or "",
            },
            "profile": profile,
            "cv": session.get("data", {}).get("cv", {}),
            "photo": session.get("data", {}).get("profile_photo", {}),
            "documents": documents,
            "professional_dna": dna,
            "recommendations": recommendations,
            "unavailable_modules": [
                {"key": "vacancies", "title": "Vacancy matching", "reason": "No live recommendations generated yet."},
                {"key": "employer_messages", "title": "Employer messages", "reason": "Available after profile publication and employer contact."},
            ],
        }

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

    def _apply_accepted_cv_to_session(self, session: dict[str, Any], accepted: dict[str, Any]) -> None:
        data = session.setdefault("data", {})
        personal = data.setdefault("personal_data", {})
        for source, target in {"fullName": "fullName", "email": "email", "phone": "phone", "location": "location"}.items():
            value = _confirmed_value(accepted.get(source))
            if value and not personal.get(target):
                personal[target] = value
        profession = data.setdefault("profession", {})
        headline = _confirmed_value(accepted.get("headline"))
        if headline and not profession.get("headline"):
            profession["headline"] = headline
        professions = _confirmed_list(accepted.get("professions"))
        if professions and not profession.get("profession"):
            profession["profession"] = professions[0]
        skills = _confirmed_list(accepted.get("skills"))
        if skills and not profession.get("skills"):
            profession["skills"] = skills
        experience = _confirmed_records(accepted.get("workExperience"))
        if experience and not data.setdefault("experience", {}).get("records"):
            data["experience"]["records"] = experience
        education = _confirmed_records(accepted.get("education"))
        if education and not data.setdefault("education", {}).get("records"):
            data["education"]["records"] = education
        certificates = _confirmed_records(accepted.get("certificates"))
        if certificates and not data.setdefault("education", {}).get("certificates"):
            data["education"]["certificates"] = certificates
        languages = _confirmed_records(accepted.get("languages"))
        if languages and not data.setdefault("languages", {}).get("records"):
            data["languages"]["records"] = languages

    def _sync_accepted_cv_to_profile(self, user_id: str, accepted: dict[str, Any]) -> None:
        for cv_key, profile_key in {
            "fullName": "full_name",
            "email": "email",
            "phone": "phone",
            "location": "current_location",
        }.items():
            value = _confirmed_value(accepted.get(cv_key))
            if value:
                self.agent_profiles.save_onboarding_answer(user_id, profile_key, value)
        headline = _confirmed_value(accepted.get("headline"))
        professions = _confirmed_list(accepted.get("professions"))
        if headline or professions:
            self.agent_profiles.save_onboarding_answer(user_id, "current_profession", headline or professions[0])
        skills = _confirmed_list(accepted.get("skills"))
        if skills:
            self.agent_profiles.save_onboarding_answer(user_id, "skills", skills)
        languages = _confirmed_records(accepted.get("languages"))
        if languages:
            self.agent_profiles.save_onboarding_answer(user_id, "languages", [item.get("name") or item.get("title") or item for item in languages])
        certificates = _confirmed_records(accepted.get("certificates"))
        if certificates:
            self.agent_profiles.save_onboarding_answer(user_id, "certificates", [item.get("title") or item.get("name") or item for item in certificates])
        experience = _confirmed_records(accepted.get("workExperience"))
        if experience:
            profile = self.agent_profiles.get_or_create_profile(user_id)
            profile.work_experience = experience
            profile.metadata.setdefault("onboarding", {})["work_experience"] = {"value": experience, "updated_at": utc_now_iso(), "language": "cv"}
            profile.profile_completeness = self.agent_profiles.calculate_completeness(profile)
            profile.updated_at = utc_now_iso()
            self.agent_profiles.profiles.update(profile)

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

    def _record_activity(self, user_id: str, action: str, step: str) -> None:
        self.activity.add(
            ActivityEvent(
                entity_type="onboarding",
                entity_id=user_id,
                action=action,
                old_value=None,
                new_value=step,
                note=f"Agent onboarding {step}",
                actor_id=user_id,
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


def _deterministic_cv_parse(file_data: dict[str, Any], onboarding_data: dict[str, Any], cv_text: str = "") -> dict[str, Any]:
    personal = onboarding_data.get("personal_data", {})
    profession = onboarding_data.get("profession", {})
    experience = onboarding_data.get("experience", {})
    education = onboarding_data.get("education", {})
    languages = onboarding_data.get("languages", {})
    filename = file_data.get("original_name", "")
    extracted = _extract_basic_cv_fields(cv_text)
    result = {
        "fullName": _value(personal.get("fullName") or extracted.get("fullName"), "personal_data.fullName" if personal.get("fullName") else "cv_text"),
        "email": _value(personal.get("email") or extracted.get("email"), "personal_data.email" if personal.get("email") else "cv_text"),
        "phone": _value(personal.get("phone") or extracted.get("phone"), "personal_data.phone" if personal.get("phone") else "cv_text"),
        "location": _value(personal.get("location") or extracted.get("location"), "personal_data.location" if personal.get("location") else "cv_text"),
        "headline": _value(profession.get("headline") or profession.get("profession"), "profession.headline"),
        "summary": _value("", "not_found"),
        "professions": _list_value([profession.get("profession")] if profession.get("profession") else [], "profession.profession"),
        "skills": _list_value(profession.get("skills") or extracted.get("skills") or [], "profession.skills" if profession.get("skills") else "cv_text"),
        "workExperience": _record_value(experience.get("records", []), "experience.records"),
        "education": _record_value(education.get("records", []), "education.records"),
        "certificates": _record_value(education.get("certificates", []), "education.certificates"),
        "languages": _record_value(languages.get("records", []), "languages.records"),
        "source": {"fileId": file_data.get("id"), "fileName": filename, "textExtracted": bool(cv_text.strip())},
        "confidence": "medium" if (personal or profession or extracted) else "low",
        "warnings": ["ATLAS extracted only facts found in uploaded CV text or already confirmed onboarding data."],
        "notFoundFields": [],
        "parser": {"version": "cv_rule_based_v1", "mode": "deterministic", "aiGeneratedMissingData": False},
    }
    result["notFoundFields"] = [
        key
        for key, value in result.items()
        if isinstance(value, dict) and "value" in value and not value.get("value")
    ]
    return result


def _extract_cv_text(path: Path | None, file_data: dict[str, Any]) -> str:
    if not path or not path.exists():
        return ""
    suffix = path.suffix.lower()
    try:
        if suffix == ".pdf":
            return _extract_pdf_text(path)
        if suffix in {".docx", ".odt"}:
            return _extract_zip_xml_text(path)
        if suffix == ".rtf":
            return _strip_rtf(path.read_text(encoding="utf-8", errors="ignore"))
        if suffix == ".doc":
            return ""
    except Exception:
        return ""
    return ""


def _extract_pdf_text(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception:
        return ""
    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages[:6])


def _extract_zip_xml_text(path: Path) -> str:
    chunks: list[str] = []
    with zipfile.ZipFile(path) as archive:
        for name in archive.namelist():
            if not name.endswith(".xml"):
                continue
            if not (name.startswith("word/") or name.startswith("content.xml")):
                continue
            root = ElementTree.fromstring(archive.read(name))
            chunks.extend(text.strip() for text in root.itertext() if text and text.strip())
    return "\n".join(chunks)


def _strip_rtf(text: str) -> str:
    text = re.sub(r"\\'[0-9a-fA-F]{2}", " ", text)
    text = re.sub(r"\\[a-zA-Z]+\d* ?", " ", text)
    return re.sub(r"[{}]", " ", text)


def _extract_basic_cv_fields(text: str) -> dict[str, Any]:
    normalized = re.sub(r"\s+", " ", text or "").strip()
    if not normalized:
        return {}
    result: dict[str, Any] = {}
    email = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", normalized)
    if email:
        result["email"] = email.group(0)
    phone = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", normalized)
    if phone:
        result["phone"] = phone.group(0).strip()
    first_line = next((line.strip() for line in text.splitlines() if 4 <= len(line.strip()) <= 80), "")
    if first_line and not re.search(r"@|http|www|curriculum|resume|cv", first_line, re.I):
        result["fullName"] = first_line
    skills_match = re.search(r"(?:skills|навички|umiejętności|компетенции)\s*[:\-]\s*([^.;]{3,220})", normalized, re.I)
    if skills_match:
        result["skills"] = [item.strip() for item in re.split(r"[,/|;]", skills_match.group(1)) if item.strip()][:20]
    location_match = re.search(r"(?:location|місто|city|адреса)\s*[:\-]\s*([^.;]{3,80})", normalized, re.I)
    if location_match:
        result["location"] = location_match.group(1).strip()
    return result


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
        "formula": {
            "overallScore": "round(sum(component_scores) / 86 * 100)",
            "maxComponentTotal": 86,
            "components": {
                "profileCompleteness": "completed core sections / 10 * 100",
                "experienceScore": "14 when at least one experience record exists",
                "skillsScore": "14 when skills exist",
                "educationScore": "10 when education records exist",
                "languagesScore": "10 when language records exist",
                "mobilityScore": "8 when preferred countries exist",
                "documentReadinessScore": "10 when CV is attached",
                "marketReadinessScore": "10 when career goal exists",
            },
        },
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
    return {
        "value": value or "",
        "source": source if value else "not_found",
        "confidence": "medium" if value else "low",
        "editable": True,
        "selected": bool(value),
    }


def _list_value(value: list[Any], source: str) -> dict[str, Any]:
    clean = [item for item in value if item]
    return {
        "value": clean,
        "source": source if clean else "not_found",
        "confidence": "medium" if clean else "low",
        "editable": True,
        "selected": bool(clean),
    }


def _record_value(value: Any, source: str) -> dict[str, Any]:
    records = _normalise_records(value)
    return {
        "value": records,
        "source": source if records else "not_found",
        "confidence": "medium" if records else "low",
        "editable": True,
        "selected": bool(records),
    }


def _sanitize_confirmed_cv_fields(accepted: dict[str, Any]) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    for key, raw in (accepted or {}).items():
        value = _confirmed_value(raw)
        if isinstance(value, str) and not value.strip():
            continue
        if isinstance(value, list) and not value:
            continue
        if key in {"skills", "professions"}:
            value = _confirmed_list(raw)
        if key in {"workExperience", "education", "certificates", "languages"}:
            value = _confirmed_records(raw)
        if value:
            sanitized[key] = {
                "value": value,
                "source": str(raw.get("source") if isinstance(raw, dict) else "user_confirmed_cv_review"),
                "confidence": str(raw.get("confidence") if isinstance(raw, dict) else "medium"),
                "confirmed": True,
            }
    return sanitized


def _confirmed_value(raw: Any) -> Any:
    if isinstance(raw, dict) and "value" in raw:
        return raw.get("value")
    return raw


def _confirmed_list(raw: Any) -> list[str]:
    value = _confirmed_value(raw)
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if isinstance(value, str):
        return [item.strip() for item in re.split(r"[,/|;]", value) if item.strip()]
    return []


def _confirmed_records(raw: Any) -> list[dict[str, Any]]:
    return _normalise_records(_confirmed_value(raw))


def _normalise_records(value: Any) -> list[dict[str, Any]]:
    if not value:
        return []
    if isinstance(value, list):
        records: list[dict[str, Any]] = []
        for item in value:
            if isinstance(item, dict):
                clean = {str(key): val for key, val in item.items() if val not in (None, "", [])}
                if clean:
                    records.append(clean)
            elif str(item).strip():
                records.append({"title": str(item).strip()})
        return records
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return []
        return [{"title": item.strip()} for item in re.split(r"\n|;", text) if item.strip()]
    return [{"title": str(value)}]


def _audit(action: str, step: str) -> dict[str, Any]:
    return {"action": action, "step": step, "timestamp": utc_now_iso()}


def _tech_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:24]
