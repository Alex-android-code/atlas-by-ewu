"""Persisted user onboarding workflow for ATLAS AI agent profiles."""

from __future__ import annotations

import hashlib
import json
import re
import time
import zipfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
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
PROFILE_COMPLETENESS_CONFIG = Path(__file__).resolve().parents[1] / "configs" / "profile_completeness.json"


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
        job = self.start_cv_parse_job(user_id, file_id)
        self.process_cv_parse_job(user_id, job["id"], file_path)
        return self.get_parse_job(user_id, job["id"])

    def start_cv_parse_job(self, user_id: str, file_id: str) -> dict[str, Any]:
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
            "status": "queued",
            "progress": 5,
            "result": None,
            "error": None,
            "warnings": [],
            "parser_version": "cv_rule_based_v2",
            "prompt_version": None,
            "model_identifier": "rule_based_local",
            "processing_time_ms": None,
            "extraction_errors": [],
            "delete_after": None,
            "created_at": now,
            "started_at": None,
            "completed_at": None,
            "updated_at": now,
        }
        self.database.insert(CV_JOB_COLLECTION, job["id"], job)
        session["parsed_cv"] = {"job_id": job["id"], "status": "queued", "progress": 5, "result": None}
        session.setdefault("audit_log", []).append(_audit("cv_parse_queued", "cv"))
        session["updated_at"] = utc_now_iso()
        self.database.update(SESSION_COLLECTION, user_id, session)
        self._record_activity(user_id, "cv_parse_queued", "cv")
        return job

    def process_cv_parse_job(self, user_id: str, job_id: str, file_path: Path | None = None) -> dict[str, Any]:
        started = _monotonic_ms()
        job = self.get_parse_job(user_id, job_id)
        if job.get("status") not in {"queued", "failed_extraction", "failed_parsing"}:
            return job
        session = self.get_or_start(user_id)
        file_data = session.get("data", {}).get("cv", {}).get("file") or {}
        self._update_cv_job(user_id, job_id, "extracting_text", 25)
        extraction = _extract_cv_text_with_metadata(file_path, file_data)
        if not extraction["text"] and extraction["fatal"]:
            failed = self._update_cv_job(
                user_id,
                job_id,
                "failed_extraction",
                100,
                error="Text extraction failed",
                extraction_errors=extraction["errors"],
                processing_time_ms=_monotonic_ms() - started,
            )
            self._record_activity(user_id, "cv_parse_failed_extraction", "cv")
            return failed
        self._update_cv_job(user_id, job_id, "parsing", 65, extraction_errors=extraction["errors"])
        try:
            parsed = _deterministic_cv_parse(file_data, session.get("data", {}), extraction["text"], extraction)
        except Exception as error:
            failed = self._update_cv_job(
                user_id,
                job_id,
                "failed_parsing",
                100,
                error="CV parsing failed",
                extraction_errors=extraction["errors"] + [str(error)],
                processing_time_ms=_monotonic_ms() - started,
            )
            self._record_activity(user_id, "cv_parse_failed_parsing", "cv")
            return failed
        completed = self._update_cv_job(
            user_id,
            job_id,
            "awaiting_review",
            100,
            result=parsed,
            warnings=parsed.get("warnings", []),
            extraction_errors=extraction["errors"],
            processing_time_ms=_monotonic_ms() - started,
            completed_at=utc_now_iso(),
        )
        session = self.get_or_start(user_id)
        session["current_step"] = "cv_review"
        session["parsed_cv"] = {"job_id": job_id, "status": "awaiting_review", "progress": 100, "result": parsed}
        session.setdefault("audit_log", []).append(_audit("cv_parse_awaiting_review", "cv"))
        session["updated_at"] = utc_now_iso()
        self.database.update(SESSION_COLLECTION, user_id, session)
        self._record_activity(user_id, "cv_parse_awaiting_review", "cv")
        return completed

    def get_parse_job(self, user_id: str, job_id: str) -> dict[str, Any]:
        job = self.database.get(CV_JOB_COLLECTION, job_id)
        if not job or job.get("user_id") != user_id:
            raise ValueError("CV parse job not found")
        return job

    def get_parse_result(self, user_id: str, job_id: str) -> dict[str, Any]:
        job = self.get_parse_job(user_id, job_id)
        if job.get("status") not in {"awaiting_review", "confirmed", "rejected"}:
            raise ValueError("CV parse result is not ready")
        return {
            "job_id": job["id"],
            "status": job["status"],
            "result": job.get("result"),
            "warnings": job.get("warnings", []),
            "parser_version": job.get("parser_version"),
            "processing_time_ms": job.get("processing_time_ms"),
            "extraction_errors": job.get("extraction_errors", []),
        }

    def accept_cv_parse(
        self,
        user_id: str,
        accepted: dict[str, Any],
        *,
        action: str = "accept_selected",
        job_id: str | None = None,
    ) -> dict[str, Any]:
        if action == "reject":
            return self.reject_cv_parse(user_id, job_id)
        return self.confirm_cv_parse(user_id, job_id, accepted_fields=accepted, edited_fields={}, rejected_fields=[], action=action)

    def confirm_cv_parse(
        self,
        user_id: str,
        job_id: str | None,
        *,
        accepted_fields: dict[str, Any],
        edited_fields: dict[str, Any],
        rejected_fields: list[str],
        action: str = "confirm",
    ) -> dict[str, Any]:
        if action not in {"confirm", "accept_all", "accept_selected"}:
            raise ValueError(f"Unsupported CV parse action: {action}")
        if not job_id:
            job_id = self.get_or_start(user_id).get("parsed_cv", {}).get("job_id")
        if not job_id:
            raise ValueError("CV parse job is required")
        job = self.get_parse_job(user_id, job_id)
        if job.get("status") not in {"awaiting_review", "confirmed", "accepted"}:
            raise ValueError("CV parse job is not ready for confirmation")
        session = self.get_or_start(user_id)
        cv_state = session.setdefault("data", {}).setdefault("cv", {})
        merged = {**(accepted_fields or {}), **_mark_edited_fields(edited_fields or {})}
        sanitized = _sanitize_confirmed_cv_fields(merged, rejected_fields=set(rejected_fields or []))
        cv_state["accepted_parsed_data"] = sanitized
        cv_state["parse_rejected"] = False
        self._apply_accepted_cv_to_session(session, sanitized)
        self._sync_accepted_cv_to_profile(user_id, sanitized)
        decision = {
            "action": action,
            "accepted_fields": sorted(sanitized.keys()),
            "edited_fields": sorted((edited_fields or {}).keys()),
            "rejected_fields": sorted(rejected_fields or []),
        }
        job["status"] = "confirmed"
        job["decision"] = decision
        job["updated_at"] = utc_now_iso()
        job["delete_after"] = job.get("delete_after") or _parse_result_delete_after()
        self.database.update(CV_JOB_COLLECTION, job_id, job)
        if session.get("parsed_cv", {}).get("job_id") == job_id:
            session["parsed_cv"]["status"] = "confirmed"
            session["parsed_cv"]["decision"] = decision
        session.setdefault("audit_log", []).append(_audit("cv_parse_confirmed", "cv"))
        session["updated_at"] = utc_now_iso()
        self.database.update(SESSION_COLLECTION, user_id, session)
        self._record_activity(user_id, "cv_parse_confirmed", "cv")
        return self._with_progress(session)

    def reject_cv_parse(self, user_id: str, job_id: str | None) -> dict[str, Any]:
        if not job_id:
            job_id = self.get_or_start(user_id).get("parsed_cv", {}).get("job_id")
        if not job_id:
            raise ValueError("CV parse job is required")
        job = self.get_parse_job(user_id, job_id)
        if job.get("status") not in {"awaiting_review", "confirmed", "accepted", "rejected"}:
            raise ValueError("CV parse job is not ready for rejection")
        session = self.get_or_start(user_id)
        cv_state = session.setdefault("data", {}).setdefault("cv", {})
        cv_state["accepted_parsed_data"] = {}
        cv_state["parse_rejected"] = True
        job["status"] = "rejected"
        job["decision"] = {"action": "reject", "accepted_fields": [], "edited_fields": [], "rejected_fields": ["*"]}
        job["updated_at"] = utc_now_iso()
        job["delete_after"] = job.get("delete_after") or _parse_result_delete_after()
        self.database.update(CV_JOB_COLLECTION, job_id, job)
        if session.get("parsed_cv", {}).get("job_id") == job_id:
            session["parsed_cv"]["status"] = "rejected"
            session["parsed_cv"]["decision"] = job["decision"]
        session.setdefault("audit_log", []).append(_audit("cv_parse_rejected", "cv"))
        session["updated_at"] = utc_now_iso()
        self.database.update(SESSION_COLLECTION, user_id, session)
        self._record_activity(user_id, "cv_parse_rejected", "cv")
        return self._with_progress(session)

    def retry_cv_parse(self, user_id: str, job_id: str) -> dict[str, Any]:
        job = self.get_parse_job(user_id, job_id)
        if job.get("status") not in {"failed_extraction", "failed_parsing", "rejected", "awaiting_review"}:
            raise ValueError("CV parse job cannot be retried from current status")
        now = utc_now_iso()
        job.update(
            {
                "status": "queued",
                "progress": 5,
                "result": None,
                "error": None,
                "warnings": [],
                "extraction_errors": [],
                "decision": None,
                "started_at": None,
                "completed_at": None,
                "updated_at": now,
            }
        )
        self.database.update(CV_JOB_COLLECTION, job_id, job)
        session = self.get_or_start(user_id)
        session["parsed_cv"] = {"job_id": job_id, "status": "queued", "progress": 5, "result": None}
        session.setdefault("audit_log", []).append(_audit("cv_parse_retry_queued", "cv"))
        session["updated_at"] = now
        self.database.update(SESSION_COLLECTION, user_id, session)
        self._record_activity(user_id, "cv_parse_retry_queued", "cv")
        return job

    def anonymize_parse_results_for_file(self, user_id: str, file_id: str) -> int:
        changed = 0
        for job in self.database.list(CV_JOB_COLLECTION):
            if job.get("user_id") != user_id or job.get("file_id") != file_id:
                continue
            job["result"] = None
            job["status"] = "deleted"
            job["decision"] = None
            job["error"] = "CV file deleted; parse result anonymized"
            job["updated_at"] = utc_now_iso()
            self.database.update(CV_JOB_COLLECTION, job["id"], job)
            changed += 1
        session = self.get_or_start(user_id)
        if session.get("data", {}).get("cv", {}).get("file", {}).get("id") == file_id:
            session.setdefault("data", {}).setdefault("cv", {})["accepted_parsed_data"] = {}
            session["parsed_cv"] = None
            session["updated_at"] = utc_now_iso()
            session.setdefault("audit_log", []).append(_audit("cv_parse_deleted_with_file", "cv"))
            self.database.update(SESSION_COLLECTION, user_id, session)
        if changed:
            self._record_activity(user_id, "cv_parse_deleted_with_file", "cv")
        return changed

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

    def profile(self, user_id: str) -> dict[str, Any]:
        profile = self.agent_profiles.get_or_create_profile(user_id)
        return {
            "profile": profile.to_dict(),
            "completeness": _profile_completeness(profile, self.get_or_start(user_id)),
        }

    def patch_profile_section(self, user_id: str, section: str, data: dict[str, Any]) -> dict[str, Any]:
        validators = {
            "personal_data": _validate_personal_data,
            "profession": _validate_profession_data,
            "preferences": _validate_preferences_data,
        }
        if section not in validators:
            raise ValueError(f"Unsupported profile section: {section}")
        normalized = validators[section](data)
        session = self.patch_step(user_id, step=section, data=normalized, next_step=section)
        profile = self.agent_profiles.get_or_create_profile(user_id)
        profile.metadata.setdefault("profile_field_sources", {})[section] = {"source": "manual", "updated_at": utc_now_iso()}
        profile.metadata.setdefault("profile_change_logs", []).append({"section": section, "action": "patch", "timestamp": utc_now_iso()})
        profile.profile_completeness = _profile_completeness(profile, session)["percent"]
        self.agent_profiles.profiles.update(profile)
        return {"section": section, "data": normalized, "profile": profile.to_dict(), "completeness": _profile_completeness(profile, session)}

    def list_profile_records(self, user_id: str, section: str) -> list[dict[str, Any]]:
        profile = self.agent_profiles.get_or_create_profile(user_id)
        return list(_profile_record_collection(profile, section))

    def add_profile_record(self, user_id: str, section: str, data: dict[str, Any]) -> dict[str, Any]:
        profile = self.agent_profiles.get_or_create_profile(user_id)
        record = _validate_profile_record(section, data)
        records = _profile_record_collection(profile, section)
        fingerprint = _record_fingerprint(record)
        for existing in records:
            if _record_fingerprint(existing) == fingerprint:
                return existing
        record["id"] = record.get("id") or new_id(_record_prefix(section))
        record["created_at"] = record.get("created_at") or utc_now_iso()
        record["updated_at"] = utc_now_iso()
        records.append(record)
        self._save_profile_records(user_id, section, records)
        return record

    def update_profile_record(self, user_id: str, section: str, record_id: str, data: dict[str, Any]) -> dict[str, Any]:
        records = self.list_profile_records(user_id, section)
        for index, record in enumerate(records):
            if record.get("id") == record_id:
                updated = _validate_profile_record(section, {**record, **data, "id": record_id})
                updated["updated_at"] = utc_now_iso()
                records[index] = updated
                self._save_profile_records(user_id, section, records)
                return updated
        raise ValueError("Profile record not found")

    def delete_profile_record(self, user_id: str, section: str, record_id: str) -> dict[str, Any]:
        records = self.list_profile_records(user_id, section)
        remaining = [record for record in records if record.get("id") != record_id]
        if len(remaining) == len(records):
            raise ValueError("Profile record not found")
        self._save_profile_records(user_id, section, remaining)
        return {"success": True, "deleted": record_id}

    def _save_profile_records(self, user_id: str, section: str, records: list[dict[str, Any]]) -> None:
        profile = self.agent_profiles.get_or_create_profile(user_id)
        if section == "experience":
            profile.work_experience = records
        elif section == "education":
            profile.education = records
        elif section == "credentials":
            profile.certificates = records
        elif section == "languages":
            profile.languages = records
        else:
            raise ValueError(f"Unsupported profile record section: {section}")
        session = self.get_or_start(user_id)
        profile.profile_completeness = _profile_completeness(profile, session)["percent"]
        profile.updated_at = utc_now_iso()
        profile.metadata.setdefault("profile_change_logs", []).append({"section": section, "action": "records_update", "timestamp": utc_now_iso()})
        self.agent_profiles.profiles.update(profile)
        self._record_activity(user_id, f"profile_{section}_updated", section)

    def _sync_step_to_profile(self, user_id: str, step: str, data: dict[str, Any]) -> None:
        if step == "agent":
            profile = self.agent_profiles.get_or_create_profile(user_id)
            profile.metadata["ai_agent"] = data
            profile.agent_memory.append(f"AI agent configured: {data.get('name') or 'ATLAS Agent'}")
            self.agent_profiles.profiles.update(profile)
        if step == "personal_data":
            for field, value in {
                "full_name": data.get("fullName") or data.get("full_name") or " ".join(part for part in [data.get("firstName"), data.get("lastName")] if part),
                "email": data.get("email"),
                "phone": data.get("phone"),
                "current_location": data.get("location") or ", ".join(part for part in [data.get("residenceCountry"), data.get("city")] if part),
            }.items():
                if value:
                    self.agent_profiles.save_onboarding_answer(user_id, field, value)
        if step == "profession":
            if data.get("headline") or data.get("profession"):
                self.agent_profiles.save_onboarding_answer(user_id, "current_profession", data.get("headline") or data.get("profession"))
            if data.get("skills"):
                skill_names = [item.get("name") if isinstance(item, dict) else str(item) for item in data.get("skills", [])]
                self.agent_profiles.save_onboarding_answer(user_id, "skills", skill_names)
        if step == "experience" and data.get("records"):
            profile = self.agent_profiles.get_or_create_profile(user_id)
            profile.work_experience = _merge_records(profile.work_experience, data["records"])
            profile.profile_completeness = self.agent_profiles.calculate_completeness(profile)
            profile.updated_at = utc_now_iso()
            self.agent_profiles.profiles.update(profile)
        if step == "education" and (data.get("records") or data.get("certificates")):
            profile = self.agent_profiles.get_or_create_profile(user_id)
            profile.education = _merge_records(profile.education, data.get("records", []))
            profile.certificates = _merge_records(profile.certificates, data.get("certificates", []))
            profile.profile_completeness = self.agent_profiles.calculate_completeness(profile)
            profile.updated_at = utc_now_iso()
            self.agent_profiles.profiles.update(profile)
        if step == "languages" and data.get("records"):
            profile = self.agent_profiles.get_or_create_profile(user_id)
            profile.languages = _merge_records(profile.languages, data["records"])
            profile.profile_completeness = self.agent_profiles.calculate_completeness(profile)
            profile.updated_at = utc_now_iso()
            self.agent_profiles.profiles.update(profile)
        if step == "preferences":
            if data.get("careerGoal"):
                self.agent_profiles.save_onboarding_answer(user_id, "career_goal", data["careerGoal"])
            if data.get("countries"):
                self.agent_profiles.save_onboarding_answer(user_id, "relocation_readiness", data.get("countries"))
            if data.get("salary"):
                self.agent_profiles.save_onboarding_answer(user_id, "salary_expectations", data.get("salary"))
            if data.get("format"):
                self.agent_profiles.save_onboarding_answer(user_id, "preferred_work", data.get("format"))

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

    def _update_cv_job(
        self,
        user_id: str,
        job_id: str,
        status: str,
        progress: int,
        **updates: Any,
    ) -> dict[str, Any]:
        job = self.get_parse_job(user_id, job_id)
        job["status"] = status
        job["progress"] = progress
        if status in {"extracting_text", "parsing"} and not job.get("started_at"):
            job["started_at"] = utc_now_iso()
        job.update({key: value for key, value in updates.items() if value is not None})
        job["updated_at"] = utc_now_iso()
        self.database.update(CV_JOB_COLLECTION, job_id, job)
        session = self.get_or_start(user_id)
        if session.get("parsed_cv", {}).get("job_id") == job_id:
            session["parsed_cv"]["status"] = status
            session["parsed_cv"]["progress"] = progress
            if "result" in updates:
                session["parsed_cv"]["result"] = updates["result"]
            session["updated_at"] = utc_now_iso()
            self.database.update(SESSION_COLLECTION, user_id, session)
        return job

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


def _deterministic_cv_parse(
    file_data: dict[str, Any],
    onboarding_data: dict[str, Any],
    cv_text: str = "",
    extraction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    personal = onboarding_data.get("personal_data", {})
    profession = onboarding_data.get("profession", {})
    experience = onboarding_data.get("experience", {})
    education = onboarding_data.get("education", {})
    languages = onboarding_data.get("languages", {})
    filename = file_data.get("original_name", "")
    extracted = _extract_basic_cv_fields(cv_text)
    result = {
        "fullName": _field(personal.get("fullName") or extracted.get("fullName", {}).get("value"), personal.get("fullName") or extracted.get("fullName", {}).get("sourceText"), 0.9 if personal.get("fullName") else extracted.get("fullName", {}).get("confidence", 0)),
        "email": _field(personal.get("email") or extracted.get("email", {}).get("value"), personal.get("email") or extracted.get("email", {}).get("sourceText"), 0.98 if personal.get("email") else extracted.get("email", {}).get("confidence", 0)),
        "phone": _field(personal.get("phone") or extracted.get("phone", {}).get("value"), personal.get("phone") or extracted.get("phone", {}).get("sourceText"), 0.92 if personal.get("phone") else extracted.get("phone", {}).get("confidence", 0)),
        "location": _field(personal.get("location") or extracted.get("location", {}).get("value"), personal.get("location") or extracted.get("location", {}).get("sourceText"), 0.86 if personal.get("location") else extracted.get("location", {}).get("confidence", 0)),
        "headline": _field(profession.get("headline") or profession.get("profession"), profession.get("headline") or profession.get("profession"), 0.82 if (profession.get("headline") or profession.get("profession")) else 0),
        "summary": _field(None, None, 0),
        "professions": _field_list([profession.get("profession")] if profession.get("profession") else [], 0.82),
        "skills": _field_list(profession.get("skills") or [item["value"] for item in extracted.get("skills", [])] or [], 0.84 if (profession.get("skills") or extracted.get("skills")) else 0),
        "workExperience": _cv_records(experience.get("records", []), "work_experience"),
        "education": _cv_records(education.get("records", []), "education"),
        "certificates": _cv_records(education.get("certificates", []), "certificate"),
        "languages": _cv_records(languages.get("records", []), "language"),
        "source": {
            "fileId": file_data.get("id"),
            "fileName": filename,
            "textExtracted": bool(cv_text.strip()),
            "method": (extraction or {}).get("method", "native_text"),
            "ocrFallbackUsed": bool((extraction or {}).get("ocr_fallback_used")),
        },
        "confidence": 0.7 if (personal or profession or extracted) else 0,
        "warnings": ["ATLAS extracted only facts found in uploaded CV text or already confirmed onboarding data."],
        "notFoundFields": [],
        "parser": {
            "version": "cv_rule_based_v2",
            "promptVersion": None,
            "modelIdentifier": "rule_based_local",
            "mode": "deterministic",
            "aiGeneratedMissingData": False,
        },
    }
    result["notFoundFields"] = [
        key
        for key, value in result.items()
        if isinstance(value, dict) and "value" in value and value.get("value") in (None, "", [])
    ]
    return result


def _extract_cv_text(path: Path | None, file_data: dict[str, Any]) -> str:
    return _extract_cv_text_with_metadata(path, file_data)["text"]


def _extract_cv_text_with_metadata(path: Path | None, file_data: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if path is None:
        return {"text": "", "method": "no_file_path_supplied", "ocr_fallback_used": False, "errors": ["text_source_unavailable"], "fatal": False}
    if not path.exists():
        return {"text": "", "method": "missing_file", "ocr_fallback_used": False, "errors": ["file_not_found"], "fatal": True}
    suffix = path.suffix.lower()
    try:
        if suffix == ".pdf":
            text = _extract_pdf_text(path)
            if text.strip():
                return {"text": text, "method": "native_pdf_text", "ocr_fallback_used": False, "errors": [], "fatal": False}
            fallback = _ocr_fallback(path, file_data)
            return {**fallback, "errors": ["native_pdf_text_empty", *fallback["errors"]], "fatal": False}
        if suffix in {".docx", ".odt"}:
            text = _extract_zip_xml_text(path)
            return {"text": text, "method": "zip_xml_text", "ocr_fallback_used": False, "errors": [] if text.strip() else ["document_text_empty"], "fatal": False}
        if suffix == ".rtf":
            text = _strip_rtf(path.read_text(encoding="utf-8", errors="ignore"))
            return {"text": text, "method": "rtf_text", "ocr_fallback_used": False, "errors": [] if text.strip() else ["document_text_empty"], "fatal": False}
        if suffix == ".doc":
            return {"text": "", "method": "legacy_doc_requires_external_parser", "ocr_fallback_used": False, "errors": ["legacy_doc_text_extraction_unavailable"], "fatal": False}
    except Exception as error:
        errors.append(type(error).__name__)
        return {"text": "", "method": "native_text_failed", "ocr_fallback_used": False, "errors": errors, "fatal": True}
    return {"text": "", "method": "unsupported_document", "ocr_fallback_used": False, "errors": ["unsupported_document"], "fatal": True}


def _ocr_fallback(path: Path, file_data: dict[str, Any]) -> dict[str, Any]:
    try:
        import pytesseract  # type: ignore  # noqa: F401
    except Exception:
        return {
            "text": "",
            "method": "ocr_unavailable",
            "ocr_fallback_used": True,
            "errors": ["ocr_engine_unavailable"],
            "fatal": False,
        }
    return {
        "text": "",
        "method": "ocr_no_pages_rendered",
        "ocr_fallback_used": True,
        "errors": ["ocr_pdf_rendering_not_configured"],
        "fatal": False,
    }


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
        result["email"] = {"value": email.group(0), "confidence": 0.98, "sourceText": _source_fragment(normalized, email.start(), email.end())}
    phone = re.search(r"(?:\+?\d[\d\s().-]{7,}\d)", normalized)
    if phone:
        result["phone"] = {"value": phone.group(0).strip(), "confidence": 0.9, "sourceText": _source_fragment(normalized, phone.start(), phone.end())}
    first_line = next((line.strip() for line in text.splitlines() if 4 <= len(line.strip()) <= 80), "")
    if first_line and not re.search(r"@|http|www|curriculum|resume|cv", first_line, re.I):
        result["fullName"] = {"value": first_line, "confidence": 0.66, "sourceText": first_line}
    skills_match = re.search(r"(?:skills|навички|umiejętności|компетенции)\s*[:\-]\s*([^.;]{3,220})", normalized, re.I)
    if skills_match:
        result["skills"] = [
            {"value": item.strip(), "confidence": 0.78, "sourceText": _source_fragment(normalized, skills_match.start(), skills_match.end())}
            for item in re.split(r"[,/|;]", skills_match.group(1))
            if item.strip()
        ][:20]
    location_match = re.search(r"(?:location|місто|city|адреса)\s*[:\-]\s*([^.;]{3,80})", normalized, re.I)
    if location_match:
        result["location"] = {"value": location_match.group(1).strip(), "confidence": 0.74, "sourceText": _source_fragment(normalized, location_match.start(), location_match.end())}
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


def _field(value: Any, source_text: str | None, confidence: float) -> dict[str, Any]:
    clean = None if value in (None, "", []) else value
    score = round(float(confidence or 0), 2) if clean is not None else 0
    return {
        "value": clean,
        "confidence": score,
        "sourceText": source_text or "",
        "selected": bool(clean and score >= 0.55),
        "edited": False,
    }


def _field_list(values: list[Any], confidence: float) -> list[dict[str, Any]]:
    return [_field(str(item).strip(), str(item).strip(), confidence) for item in values if str(item).strip()]


def _cv_records(value: Any, record_type: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in _normalise_records(value):
        item = dict(item)
        item.setdefault("type", record_type)
        item.setdefault("confidence", 0.78)
        item.setdefault("sourceText", " ".join(str(part) for part in item.values() if part)[:240])
        item.setdefault("selected", True)
        item.setdefault("edited", False)
        records.append(item)
    return records


def _mark_edited_fields(edited: dict[str, Any]) -> dict[str, Any]:
    marked: dict[str, Any] = {}
    for key, value in edited.items():
        if isinstance(value, dict):
            marked[key] = {**value, "edited": True}
        else:
            marked[key] = {"value": value, "edited": True, "confidence": 1, "sourceText": "user_edit"}
    return marked


def _sanitize_confirmed_cv_fields(accepted: dict[str, Any], rejected_fields: set[str] | None = None) -> dict[str, Any]:
    sanitized: dict[str, Any] = {}
    rejected_fields = rejected_fields or set()
    for key, raw in (accepted or {}).items():
        if key in rejected_fields:
            continue
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
                "sourceText": str(raw.get("sourceText") or raw.get("source") or "") if isinstance(raw, dict) else "",
                "confidence": _confidence_number(raw.get("confidence", 1) if isinstance(raw, dict) else 1),
                "edited": bool(raw.get("edited") if isinstance(raw, dict) else False),
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
        result: list[str] = []
        for item in value:
            if isinstance(item, dict):
                if item.get("selected") is False:
                    continue
                item_value = item.get("value")
            else:
                item_value = item
            if str(item_value).strip():
                result.append(str(item_value).strip())
        return result
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


def _merge_records(existing: list[dict[str, Any]], incoming: Any) -> list[dict[str, Any]]:
    result = list(existing or [])
    seen = {_record_fingerprint(item) for item in result}
    for item in _normalise_records(incoming):
        fingerprint = _record_fingerprint(item)
        if fingerprint and fingerprint not in seen:
            result.append(item)
            seen.add(fingerprint)
    return result


def _record_fingerprint(item: dict[str, Any]) -> str:
    parts = [str(item.get(key, "")).strip().lower() for key in ("title", "name", "organization", "period", "level", "note")]
    return "|".join(part for part in parts if part)


def _validate_personal_data(data: dict[str, Any]) -> dict[str, Any]:
    normalized = {key: _trim(value, 160) for key, value in data.items()}
    full_name = normalized.get("fullName") or " ".join(part for part in [normalized.get("firstName"), normalized.get("lastName")] if part)
    if full_name:
        parts = full_name.split()
        normalized.setdefault("firstName", parts[0])
        if len(parts) > 1:
            normalized.setdefault("lastName", " ".join(parts[1:]))
    for key in ("firstName", "lastName"):
        if normalized.get(key) and not re.search(r"[^\W\d_]", normalized[key], re.UNICODE):
            raise ValueError(f"{key} must contain letters")
    if normalized.get("birthDate") and normalized["birthDate"] > datetime.now(timezone.utc).date().isoformat():
        raise ValueError("birthDate cannot be in the future")
    if normalized.get("email") and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", normalized["email"]):
        raise ValueError("Invalid email")
    if normalized.get("phone"):
        normalized["phone"] = _normalize_phone(normalized["phone"])
    if normalized.get("workPermitCountries"):
        normalized["workPermitCountries"] = _string_list(normalized["workPermitCountries"])
    return normalized


def _validate_profession_data(data: dict[str, Any]) -> dict[str, Any]:
    normalized = {key: value for key, value in data.items()}
    profession = _trim(data.get("profession") or data.get("primaryProfession"), 120)
    normalized["profession"] = profession
    normalized["primaryProfession"] = profession
    normalized["normalizedProfession"] = _normalize_profession(profession)
    normalized["additionalProfessions"] = _string_list(data.get("additionalProfessions") or data.get("additionalProfessionsText"))
    normalized["skills"] = _normalize_skills(data.get("skills") or _string_list(data.get("skillsText")))
    normalized["tools"] = _string_list(data.get("tools") or data.get("toolsText"))
    normalized["industries"] = _string_list(data.get("industries") or data.get("industriesText"))
    normalized["qualificationLevel"] = str(data.get("qualificationLevel") or "").lower()
    if normalized["qualificationLevel"] and normalized["qualificationLevel"] not in {"trainee", "junior", "middle", "senior", "expert", "manager", "director", "owner/founder"}:
        raise ValueError("Invalid qualification level")
    return normalized


def _validate_preferences_data(data: dict[str, Any]) -> dict[str, Any]:
    normalized = {key: value for key, value in data.items()}
    normalized["desiredProfessions"] = _string_list(data.get("desiredProfessions") or data.get("desiredProfessionsText"))
    normalized["countries"] = _string_list(data.get("countries") or data.get("countriesText"))
    normalized["cities"] = _string_list(data.get("cities") or data.get("citiesText"))
    normalized["salaryExpectation"] = _salary_expectation(data)
    return normalized


def _validate_profile_record(section: str, data: dict[str, Any]) -> dict[str, Any]:
    if section == "experience":
        record = {**data, "source": data.get("source") or "manual"}
        record["position"] = _trim(data.get("position") or data.get("title"), 140)
        record["companyName"] = _trim(data.get("companyName") or data.get("organization"), 140)
        record["normalizedPosition"] = _normalize_profession(record["position"])
        record["responsibilities"] = _string_list(data.get("responsibilities") or data.get("note"))
        record["achievements"] = _string_list(data.get("achievements"))
        record["tools"] = _string_list(data.get("tools"))
        _validate_date_order(record.get("startDate"), None if record.get("isCurrent") else record.get("endDate"))
        return record
    if section == "education":
        record = {**data, "source": data.get("source") or "manual"}
        record["institution"] = _trim(data.get("institution") or data.get("organization") or data.get("title"), 160)
        record["degree"] = _trim(data.get("degree") or data.get("title"), 160)
        _validate_date_order(record.get("startDate"), None if record.get("isCurrent") else record.get("endDate"))
        return record
    if section == "credentials":
        record = {**data, "verified": bool(data.get("verified", False))}
        record["type"] = data.get("type") if data.get("type") in {"course", "certificate", "license", "permit"} else "certificate"
        record["name"] = _trim(data.get("name") or data.get("title"), 160)
        record["status"] = _credential_status(record.get("expiresAt"))
        return record
    if section == "languages":
        level = data.get("level") or data.get("organization") or "A1"
        if level not in {"A1", "A2", "B1", "B2", "C1", "C2", "native"}:
            raise ValueError("Invalid language level")
        return {
            **data,
            "languageCode": _trim(data.get("languageCode") or data.get("title") or data.get("name"), 24).lower(),
            "level": level,
            "source": data.get("source") or "manual",
            "verified": bool(data.get("verified", False)),
        }
    raise ValueError(f"Unsupported profile record section: {section}")


def _profile_record_collection(profile: Any, section: str) -> list[dict[str, Any]]:
    if section == "experience":
        return profile.work_experience
    if section == "education":
        return profile.education
    if section == "credentials":
        return profile.certificates
    if section == "languages":
        return profile.languages
    raise ValueError(f"Unsupported profile record section: {section}")


def _record_prefix(section: str) -> str:
    return {"experience": "EXP", "education": "EDU", "credentials": "CRD", "languages": "LAN"}[section]


def _trim(value: Any, max_length: int) -> str:
    return str(value or "").strip()[:max_length]


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [item.strip() for item in re.split(r"[,;\n|]", str(value or "")) if item.strip()]


def _normalize_phone(value: str) -> str:
    clean = re.sub(r"[^\d+]", "", value)
    if clean and not clean.startswith("+"):
        clean = "+" + clean
    if len(clean) > 18:
        raise ValueError("Phone is too long")
    return clean


def _normalize_profession(value: str) -> str:
    text = re.sub(r"\s+", " ", str(value or "").strip().lower())
    synonyms = {
        "hr coordinator": "hr_coordinator",
        "koordynator hr": "hr_coordinator",
        "координатор персоналу": "hr_coordinator",
    }
    if text in synonyms:
        return synonyms[text]
    return re.sub(r"[^a-z0-9а-яіїєґąćęłńóśźż]+", "_", text, flags=re.I).strip("_")


def _normalize_skills(value: Any) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in _string_list(value):
        key = _normalize_profession(item)
        if key in seen:
            continue
        seen.add(key)
        result.append({"id": new_id("SKL"), "name": item, "normalizedKey": key, "source": "manual", "verified": False})
    return result


def _validate_date_order(start: Any, end: Any) -> None:
    if start and end and str(start) > str(end):
        raise ValueError("Start date cannot be after end date")


def _credential_status(expires_at: Any) -> str:
    if not expires_at:
        return "unknown"
    today = datetime.now(timezone.utc).date()
    try:
        expiry = datetime.fromisoformat(str(expires_at)).date()
    except ValueError:
        return "unknown"
    if expiry < today:
        return "expired"
    if expiry <= today + timedelta(days=90):
        return "expiring"
    return "valid"


def _salary_expectation(data: dict[str, Any]) -> dict[str, Any]:
    minimum = data.get("minimumSalary") or data.get("salary")
    return {
        "minimum": float(minimum) if str(minimum or "").replace(".", "", 1).isdigit() else None,
        "preferred": float(data["preferredSalary"]) if str(data.get("preferredSalary") or "").replace(".", "", 1).isdigit() else None,
        "currency": str(data.get("currency") or "PLN"),
        "period": data.get("salaryPeriod") if data.get("salaryPeriod") in {"hour", "month", "year"} else "month",
        "grossNet": data.get("grossNet") if data.get("grossNet") in {"gross", "net", "unknown"} else "unknown",
    }


def _profile_completeness(profile: Any, session: dict[str, Any]) -> dict[str, Any]:
    weights = json.loads(PROFILE_COMPLETENESS_CONFIG.read_text(encoding="utf-8"))
    checks = {
        "personal_data": bool(profile.personal_information.get("full_name") or profile.contact_information.get("email")),
        "profession": bool(profile.professional_summary or profile.preferred_roles),
        "skills": bool(profile.skills),
        "experience": bool(profile.work_experience),
        "education_credentials": bool(profile.education or profile.certificates),
        "languages": bool(profile.languages),
        "preferences": bool(profile.career_goals or profile.relocation_preferences),
        "photo_cv": bool(profile.profile_photo) and bool(profile.uploaded_cv),
    }
    percent = sum(weight for key, weight in weights.items() if checks.get(key))
    missing = [key for key, complete in checks.items() if not complete]
    next_best = max(missing, key=lambda key: weights.get(key, 0), default=None)
    return {"percent": int(percent), "weights": weights, "missing_sections": missing, "next_best_section": next_best}


def _confidence_number(value: Any) -> float:
    if isinstance(value, (int, float)):
        return round(float(value), 2)
    mapping = {"high": 0.9, "medium": 0.7, "low": 0.35}
    return mapping.get(str(value).lower(), 1.0)


def _source_fragment(text: str, start: int, end: int, radius: int = 70) -> str:
    return text[max(0, start - radius) : min(len(text), end + radius)].strip()


def _monotonic_ms() -> int:
    return round(time.perf_counter() * 1000)


def _parse_result_delete_after() -> str:
    return (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()


def _value(value: Any, source: str) -> dict[str, Any]:
    return _field(value, source, 0.8 if value else 0)


def _list_value(value: list[Any], source: str) -> dict[str, Any]:
    clean = [item for item in value if item]
    return {"value": clean, "sourceText": source, "confidence": 0.8 if clean else 0, "selected": bool(clean), "edited": False}


def _record_value(value: Any, source: str) -> dict[str, Any]:
    records = _normalise_records(value)
    return {"value": records, "sourceText": source, "confidence": 0.8 if records else 0, "selected": bool(records), "edited": False}


def _audit(action: str, step: str) -> dict[str, Any]:
    return {"action": action, "step": step, "timestamp": utc_now_iso()}


def _tech_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:24]
