"""Persisted onboarding workflow for ATLAS employer/company profiles."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.models import ActivityEvent, Document, DocumentStatus, Employer, new_id, utc_now_iso
from database.json_database import JsonDatabase
from database.repositories import ActivityRepository, DocumentRepository, EmployerRepository


EMPLOYER_ONBOARDING_COLLECTION = "employer_onboarding_sessions"
EMPLOYER_STEPS = ["welcome", "company", "contact", "hiring_needs", "documents", "consents", "completed"]


@dataclass
class EmployerOnboardingWorkflowService:
    database: JsonDatabase
    employers: EmployerRepository
    documents: DocumentRepository
    activity: ActivityRepository

    def get_or_start(self, user_id: str) -> dict[str, Any]:
        session = self.database.get(EMPLOYER_ONBOARDING_COLLECTION, user_id)
        if not session:
            session = {
                "id": new_id("EONB"),
                "user_id": user_id,
                "status": "not_started",
                "current_step": "welcome",
                "completed_steps": [],
                "data": {},
                "employer_id": None,
                "audit_log": [_audit("session_created", "welcome")],
                "created_at": utc_now_iso(),
                "updated_at": utc_now_iso(),
                "completed_at": None,
            }
            self.database.insert(EMPLOYER_ONBOARDING_COLLECTION, user_id, session)
        return _with_progress(session)

    def patch_step(self, user_id: str, step: str, data: dict[str, Any] | None = None, next_step: str | None = None) -> dict[str, Any]:
        if step not in EMPLOYER_STEPS:
            raise ValueError(f"Unknown employer onboarding step: {step}")
        session = self.get_or_start(user_id)
        session["status"] = "completed" if session.get("status") == "completed" else "in_progress"
        normalized = _validate_step(step, data or {})
        session.setdefault("data", {})[step] = normalized
        if step not in session.setdefault("completed_steps", []):
            session["completed_steps"].append(step)
        if step == "documents":
            for file_data in normalized.get("files", []):
                self._ensure_document_record(user_id, file_data)
        session["current_step"] = next_step if next_step in EMPLOYER_STEPS else _next_step(step)
        session["updated_at"] = utc_now_iso()
        session.setdefault("audit_log", []).append(_audit("step_saved", step))
        self.database.update(EMPLOYER_ONBOARDING_COLLECTION, user_id, session)
        self._record_activity(user_id, "employer_onboarding_step_saved", step)
        return _with_progress(session)

    def complete(self, user_id: str) -> dict[str, Any]:
        session = self.get_or_start(user_id)
        if session.get("status") == "completed":
            self._record_activity(user_id, "employer_onboarding_completion_retry", "completed")
            employer = self._employer_for_session(session)
            return {
                "session": _with_progress(session),
                "employer": employer.to_dict() if employer else _draft_employer(session.get("data", {})),
                "dashboard": self.dashboard(user_id),
                "dashboard_route": "/employer/dashboard",
            }
        errors = self._completion_errors(session)
        if errors:
            session.setdefault("audit_log", []).append(_audit("completion_blocked", "completion"))
            session["updated_at"] = utc_now_iso()
            self.database.update(EMPLOYER_ONBOARDING_COLLECTION, user_id, session)
            self._record_activity(user_id, "employer_onboarding_completion_blocked", "completion")
            raise ValueError("; ".join(errors))
        employer = self._upsert_employer(user_id, session)
        session["employer_id"] = employer.id
        session["status"] = "completed"
        session["current_step"] = "completed"
        if "completed" not in session.setdefault("completed_steps", []):
            session["completed_steps"].append("completed")
        session["completed_at"] = session.get("completed_at") or utc_now_iso()
        session["updated_at"] = utc_now_iso()
        session.setdefault("audit_log", []).append(_audit("employer_onboarding_completed", "completed"))
        self.database.update(EMPLOYER_ONBOARDING_COLLECTION, user_id, session)
        self._record_activity(user_id, "employer_onboarding_completed", "completed")
        return {"session": _with_progress(session), "employer": employer.to_dict(), "dashboard": self.dashboard(user_id), "dashboard_route": "/employer/dashboard"}

    def dashboard(self, user_id: str) -> dict[str, Any]:
        session = self.get_or_start(user_id)
        data = session.get("data", {})
        employer = self._employer_for_session(session)
        documents = [item.to_dict() for item in self.documents.list() if item.owner_id == user_id and item.metadata.get("employer_onboarding_file_id")]
        readiness = _readiness(data, documents)
        actions = _actions(data, readiness)
        self._record_activity(user_id, "employer_dashboard_opened", "dashboard")
        return {
            "user": {"id": user_id},
            "employer": employer.to_dict() if employer else _draft_employer(data),
            "onboarding": {
                "status": session.get("status"),
                "currentStep": session.get("current_step"),
                "completedAt": session.get("completed_at"),
                "redirectTo": None if session.get("status") == "completed" else f"/employer/onboarding?step={session.get('current_step') or 'welcome'}",
            },
            "company": data.get("company", {}),
            "contact": data.get("contact", {}),
            "hiringNeeds": data.get("hiring_needs", {}),
            "readiness": readiness,
            "documents": documents,
            "recommendedActions": actions,
            "recentActivity": _activity(self.activity.list(), user_id),
            "quickActions": [
                {"id": "edit_company", "title": "Edit company profile", "route": "/employer/onboarding?step=company"},
                {"id": "edit_hiring", "title": "Update hiring needs", "route": "/employer/onboarding?step=hiring_needs"},
                {"id": "add_documents", "title": "Add company documents", "route": "/employer/onboarding?step=documents"},
                {"id": "consents", "title": "Consent settings", "route": "/employer/onboarding?step=consents"},
            ],
        }

    def _completion_errors(self, session: dict[str, Any]) -> list[str]:
        data = session.get("data", {})
        required = ["company", "contact", "hiring_needs", "consents"]
        missing = [step for step in required if step not in session.get("completed_steps", []) or not data.get(step)]
        errors = [f"Incomplete employer onboarding steps: {', '.join(missing)}"] if missing else []
        consents = data.get("consents", {})
        if not (consents.get("terms") and consents.get("privacy") and consents.get("businessProcessing")):
            errors.append("Required employer consents are missing")
        if not data.get("company", {}).get("company_name"):
            errors.append("Company name is missing")
        if not data.get("contact", {}).get("contact_email"):
            errors.append("Contact email is missing")
        if not data.get("hiring_needs", {}).get("profession"):
            errors.append("Hiring profession is missing")
        return errors

    def _upsert_employer(self, user_id: str, session: dict[str, Any]) -> Employer:
        data = session.get("data", {})
        company = data.get("company", {})
        contact = data.get("contact", {})
        existing = self._employer_for_session(session)
        metadata = {
            **(existing.metadata if existing else {}),
            "source": "employer_onboarding",
            "owner_user_id": user_id,
            "hiring_needs": data.get("hiring_needs", {}),
            "documents_count": len(data.get("documents", {}).get("files", [])),
            "onboarding_completed_at": utc_now_iso(),
        }
        if existing:
            existing.company_name = company["company_name"]
            existing.contact_email = contact["contact_email"]
            existing.contact_phone = contact.get("contact_phone", "")
            existing.country_code = company.get("country_code", "GLOBAL")
            existing.industry = company.get("industry", "general")
            existing.metadata = metadata
            return self.employers.update(existing)
        employer = Employer(
            company_name=company["company_name"],
            contact_email=contact["contact_email"],
            contact_phone=contact.get("contact_phone", ""),
            country_code=company.get("country_code", "GLOBAL"),
            industry=company.get("industry", "general"),
            verified=False,
            metadata=metadata,
        )
        return self.employers.add(employer)

    def _employer_for_session(self, session: dict[str, Any]) -> Employer | None:
        if session.get("employer_id"):
            return self.employers.get(session["employer_id"])
        for employer in self.employers.list():
            if employer.metadata.get("owner_user_id") == session.get("user_id"):
                return employer
        return None

    def _ensure_document_record(self, user_id: str, file_data: dict[str, Any]) -> None:
        if not file_data.get("id"):
            return
        if any(item.owner_id == user_id and item.metadata.get("employer_onboarding_file_id") == file_data["id"] for item in self.documents.list()):
            return
        self.documents.add(
            Document(
                owner_id=user_id,
                document_type=file_data.get("kind") or "employer_document",
                country_code="GLOBAL",
                status=DocumentStatus.SUBMITTED,
                file_path=file_data.get("stored_name"),
                metadata={"employer_onboarding_file_id": file_data["id"], "original_name": file_data.get("original_name")},
            )
        )

    def _record_activity(self, user_id: str, action: str, step: str) -> None:
        self.activity.add(ActivityEvent(entity_type="employer_onboarding", entity_id=user_id, action=action, old_value=None, new_value=step, note=f"Employer onboarding {step}", actor_id=user_id))


def _validate_step(step: str, data: dict[str, Any]) -> dict[str, Any]:
    if step in {"welcome", "documents", "consents"}:
        return data
    if step == "company":
        company_name = _trim(data.get("company_name") or data.get("companyName"), 180)
        if not company_name:
            raise ValueError("company_name is required")
        return {**data, "company_name": company_name, "country_code": _trim(data.get("country_code") or data.get("countryCode") or "GLOBAL", 8).upper(), "industry": _trim(data.get("industry") or "general", 120)}
    if step == "contact":
        email = _trim(data.get("contact_email") or data.get("email"), 180)
        if not _valid_email(email):
            raise ValueError("Valid contact email is required")
        return {**data, "contact_email": email, "contact_phone": _trim(data.get("contact_phone") or data.get("phone"), 32), "contact_person": _trim(data.get("contact_person") or data.get("contactPerson"), 160)}
    if step == "hiring_needs":
        profession = _trim(data.get("profession") or data.get("role"), 160)
        if not profession:
            raise ValueError("profession is required")
        return {**data, "profession": profession, "quantity": max(1, _safe_int(data.get("quantity"), 1)), "country_code": _trim(data.get("country_code") or data.get("countryCode") or "GLOBAL", 8).upper()}
    raise ValueError(f"Unsupported employer onboarding step: {step}")


def _readiness(data: dict[str, Any], documents: list[dict[str, Any]]) -> dict[str, str]:
    consents = data.get("consents", {})
    return {
        "companyProfileStatus": "complete" if data.get("company") and data.get("contact") else "incomplete",
        "hiringNeedsStatus": "complete" if data.get("hiring_needs", {}).get("profession") else "incomplete",
        "documentsStatus": "uploaded" if documents else "missing",
        "verificationStatus": "pending_review" if documents else "not_started",
        "businessProcessingConsent": "enabled" if consents.get("businessProcessing") else "disabled",
    }


def _actions(data: dict[str, Any], readiness: dict[str, str]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    if readiness["documentsStatus"] == "missing":
        actions.append({"id": "add_company_documents", "title": "Add company documents", "description": "Upload registration or tax documents before verification.", "priority": "high", "source": "document", "actionType": "open_onboarding_step", "route": "/employer/onboarding?step=documents"})
    if readiness["hiringNeedsStatus"] != "complete":
        actions.append({"id": "complete_hiring_needs", "title": "Complete hiring needs", "description": "Add role, quantity, location and salary range.", "priority": "high", "source": "profile", "actionType": "open_onboarding_step", "route": "/employer/onboarding?step=hiring_needs"})
    if readiness["businessProcessingConsent"] != "enabled":
        actions.append({"id": "accept_business_processing", "title": "Accept business processing consent", "description": "Required before ATLAS can operate the employer workspace.", "priority": "high", "source": "consent", "actionType": "open_onboarding_step", "route": "/employer/onboarding?step=consents"})
    if data.get("hiring_needs", {}).get("profession") and not data.get("hiring_needs", {}).get("salary_min"):
        actions.append({"id": "add_salary", "title": "Add salary range", "description": "Salary helps ATLAS assess vacancy quality without guessing.", "priority": "medium", "source": "profile", "actionType": "open_onboarding_step", "route": "/employer/onboarding?step=hiring_needs"})
    return actions[:5]


def _activity(events: list[ActivityEvent], user_id: str) -> list[dict[str, Any]]:
    return [
        {"id": item.id, "type": item.action, "title": item.action.replace("_", " ").title(), "createdAt": item.created_at, "source": item.new_value or ""}
        for item in sorted((event for event in events if event.entity_id == user_id and event.action != "employer_dashboard_opened"), key=lambda event: event.created_at, reverse=True)[:8]
    ]


def _draft_employer(data: dict[str, Any]) -> dict[str, Any]:
    company = data.get("company", {})
    contact = data.get("contact", {})
    return {"company_name": company.get("company_name", ""), "contact_email": contact.get("contact_email", ""), "contact_phone": contact.get("contact_phone", ""), "country_code": company.get("country_code", ""), "industry": company.get("industry", ""), "verified": False, "metadata": {"source": "employer_onboarding_draft"}}


def _with_progress(session: dict[str, Any]) -> dict[str, Any]:
    clean = dict(session)
    total = len(EMPLOYER_STEPS) - 1
    done = len([step for step in clean.get("completed_steps", []) if step != "completed"])
    clean["steps"] = EMPLOYER_STEPS
    clean["progress"] = {"completed": done, "total": total, "percent": round((done / total) * 100) if total else 0}
    return clean


def _next_step(step: str) -> str:
    index = EMPLOYER_STEPS.index(step)
    return EMPLOYER_STEPS[min(index + 1, len(EMPLOYER_STEPS) - 1)]


def _audit(action: str, step: str) -> dict[str, str]:
    return {"action": action, "step": step, "timestamp": utc_now_iso()}


def _trim(value: Any, max_length: int) -> str:
    return str(value or "").strip()[:max_length]


def _valid_email(value: str) -> bool:
    return bool(value and "@" in value and "." in value.rsplit("@", 1)[-1])


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
