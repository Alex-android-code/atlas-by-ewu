"""Jobs, applications and recruitment pipeline workflow for ATLAS."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.models import ActivityEvent, Candidate, Vacancy, new_id, utc_now_iso
from database.json_database import JsonDatabase
from database.repositories import ActivityRepository, CandidateRepository, VacancyRepository
from services.employer_onboarding_workflow import (
    COMPANY_COLLECTION,
    COMPANY_MEMBERS_COLLECTION,
    EMPLOYER_CONSENTS_COLLECTION,
    HIRING_NEEDS_COLLECTION,
    HIRING_PROCESS_COLLECTION,
    ROLE_PERMISSIONS,
)


APPLICATIONS_COLLECTION = "job_applications"
APPLICATION_SNAPSHOTS_COLLECTION = "application_profile_snapshots"
APPLICATION_CONSENTS_COLLECTION = "application_consent_snapshots"
APPLICATION_TRANSITIONS_COLLECTION = "application_stage_transitions"
APPLICATION_NOTES_COLLECTION = "application_notes"
APPLICATION_INTERVIEWS_COLLECTION = "application_interviews"
APPLICATION_EVALUATIONS_COLLECTION = "application_evaluations"
APPLICATION_OFFERS_COLLECTION = "job_offers"
NOTIFICATIONS_COLLECTION = "notification_events"

VACANCY_STATUSES = {"draft", "pending_review", "published", "paused", "closed", "cancelled", "archived"}
APPLICATION_ACTIVE_STATUSES = {"submitted", "under_review", "screening", "qualified", "interview", "assessment", "offer"}
APPLICATION_FINAL_STATUSES = {"hired", "rejected", "withdrawn", "archived"}
PIPELINE_STAGE_TO_STATUS = {
    "new": "submitted",
    "screening": "screening",
    "qualified": "qualified",
    "interview": "interview",
    "technical_assessment": "assessment",
    "client_review": "under_review",
    "offer": "offer",
    "hired": "hired",
    "rejected": "rejected",
    "withdrawn": "withdrawn",
}
SAFE_REJECTION_CODES = {
    "requirements_not_met",
    "experience_mismatch",
    "skills_mismatch",
    "availability_mismatch",
    "location_mismatch",
    "salary_mismatch",
    "position_closed",
    "candidate_withdrew",
    "duplicate",
    "other",
}


class VacancyComplianceService:
    """Deterministic anti-discrimination guard for vacancy text."""

    BLOCKED_TERMS = {
        "female only": "gender",
        "male only": "gender",
        "women only": "gender",
        "men only": "gender",
        "under 30": "age",
        "young only": "age",
        "no disabled": "disability",
        "not pregnant": "pregnancy",
        "christian only": "religion",
        "white only": "race",
        "українці тільки": "ethnicity",
        "только мужчины": "gender",
        "только женщины": "gender",
        "до 30 лет": "age",
    }

    def check(self, vacancy: dict[str, Any]) -> dict[str, Any]:
        text = " ".join(
            [
                str(vacancy.get("title", "")),
                str(vacancy.get("description", "")),
                " ".join(_string_list(vacancy.get("responsibilities"))),
                " ".join(item.get("label", "") for item in _list_of_dicts(vacancy.get("requirements"))),
            ]
        ).lower()
        findings = [
            {"term": term, "category": category, "message": f"Potentially discriminatory requirement: {category}"}
            for term, category in self.BLOCKED_TERMS.items()
            if term in text
        ]
        return {"passed": not findings, "findings": findings}


@dataclass
class RecruitmentWorkflowService:
    database: JsonDatabase
    vacancies: VacancyRepository
    candidates: CandidateRepository
    activity: ActivityRepository
    compliance: VacancyComplianceService | None = None

    def __post_init__(self) -> None:
        if self.compliance is None:
            self.compliance = VacancyComplianceService()

    def create_vacancy(self, user_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        company_id = _trim(payload.get("companyId") or payload.get("company_id"))
        self._require_permission(user_id, company_id, "hiring:manage")
        source = "manual"
        if payload.get("hiringNeedId") or payload.get("hiring_need_id"):
            source = "hiring_need"
            payload = self._payload_from_hiring_need(company_id, payload)
        vacancy_data = _normalize_vacancy_payload(user_id, company_id, payload, source=source)
        vacancy = Vacancy(
            employer_id=company_id,
            title=vacancy_data["title"],
            country_code=vacancy_data.get("countryCode", "GLOBAL"),
            profession_code=vacancy_data.get("normalizedProfessionKey") or "general",
            salary_min=(vacancy_data.get("salary") or {}).get("minimum") or 0,
            salary_max=(vacancy_data.get("salary") or {}).get("maximum") or 0,
            currency=(vacancy_data.get("salary") or {}).get("currency") or "",
            required_languages=[item.get("language", item.get("label", "")) for item in vacancy_data.get("languageRequirements", [])],
            required_documents=[item.get("label", "") for item in vacancy_data.get("credentialRequirements", [])],
            location=", ".join(vacancy_data.get("locationIds", [])) or None,
            status=vacancy_data["status"],
            metadata={"recruitment": vacancy_data, "version_history": [_version("vacancy_created", None, vacancy_data, user_id)]},
        )
        saved = self.vacancies.add(vacancy)
        self._audit(user_id, "vacancy_created", "vacancy", {"company_id": company_id, "vacancy_id": saved.id})
        return self._vacancy_response(saved)

    def list_vacancies(self, user_id: str, filters: dict[str, Any]) -> dict[str, Any]:
        company_id = _trim(filters.get("companyId") or filters.get("company_id"))
        public_only = bool(filters.get("public"))
        items = []
        for vacancy in self.vacancies.list():
            data = _vacancy_data(vacancy)
            if public_only:
                if data.get("status") != "published":
                    continue
            else:
                self._require_permission(user_id, data.get("companyId"), "hiring:read", allow_manage=True)
                if company_id and data.get("companyId") != company_id:
                    continue
            if filters.get("status") and data.get("status") != filters["status"]:
                continue
            items.append(self._vacancy_response(vacancy, public=public_only))
        return _paginate(items, filters)

    def get_vacancy(self, user_id: str, vacancy_id: str) -> dict[str, Any]:
        vacancy = self._vacancy(vacancy_id)
        data = _vacancy_data(vacancy)
        self._require_permission(user_id, data.get("companyId"), "hiring:read", allow_manage=True)
        return self._vacancy_response(vacancy)

    def get_public_job(self, vacancy_id: str) -> dict[str, Any]:
        vacancy = self._vacancy(vacancy_id)
        data = _vacancy_data(vacancy)
        if data.get("status") != "published":
            raise ValueError("Published vacancy not found")
        company = self.database.get(COMPANY_COLLECTION, data.get("companyId")) or {}
        return {"job": self._vacancy_response(vacancy, public=True), "company": _public_company(company)}

    def update_vacancy(self, user_id: str, vacancy_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        vacancy = self._vacancy(vacancy_id)
        current = _vacancy_data(vacancy)
        self._require_permission(user_id, current.get("companyId"), "hiring:manage")
        updated = _normalize_vacancy_payload(user_id, current["companyId"], {**current, **payload}, source=current.get("source", "manual"), existing=current)
        updated["version"] = int(current.get("version", 1)) + 1
        updated["updatedAt"] = utc_now_iso()
        vacancy.title = updated["title"]
        vacancy.status = updated["status"]
        vacancy.profession_code = updated.get("normalizedProfessionKey") or vacancy.profession_code
        vacancy.salary_min = (updated.get("salary") or {}).get("minimum") or 0
        vacancy.salary_max = (updated.get("salary") or {}).get("maximum") or 0
        vacancy.currency = (updated.get("salary") or {}).get("currency") or ""
        vacancy.metadata["recruitment"] = updated
        vacancy.metadata.setdefault("version_history", []).append(_version("vacancy_updated", current, updated, user_id))
        self.vacancies.update(vacancy)
        self._audit(user_id, "vacancy_updated", "vacancy", {"company_id": current["companyId"], "vacancy_id": vacancy_id})
        return self._vacancy_response(vacancy)

    def publish_vacancy(self, user_id: str, vacancy_id: str) -> dict[str, Any]:
        vacancy = self._vacancy(vacancy_id)
        data = _vacancy_data(vacancy)
        self._require_permission(user_id, data.get("companyId"), "hiring:manage")
        errors = self._publication_errors(data)
        if errors:
            raise ValueError("; ".join(errors))
        compliance = self.compliance.check(data) if self.compliance else {"passed": True, "findings": []}
        if not compliance["passed"]:
            self._audit(user_id, "vacancy_compliance_blocked", "vacancy", {"company_id": data["companyId"], "vacancy_id": vacancy_id, "findings": compliance["findings"]})
            raise ValueError("Vacancy failed anti-discrimination guard")
        before = dict(data)
        data["status"] = "published"
        data["publishedAt"] = data.get("publishedAt") or utc_now_iso()
        data["updatedAt"] = utc_now_iso()
        vacancy.status = "published"
        vacancy.metadata["recruitment"] = data
        vacancy.metadata.setdefault("version_history", []).append(_version("vacancy_published", before, data, user_id))
        self.vacancies.update(vacancy)
        self._audit(user_id, "vacancy_published", "vacancy", {"company_id": data["companyId"], "vacancy_id": vacancy_id})
        return self._vacancy_response(vacancy)

    def pause_vacancy(self, user_id: str, vacancy_id: str) -> dict[str, Any]:
        return self._set_vacancy_status(user_id, vacancy_id, "paused", "vacancy_paused")

    def close_vacancy(self, user_id: str, vacancy_id: str) -> dict[str, Any]:
        vacancy = self._set_vacancy_status(user_id, vacancy_id, "closed", "vacancy_closed")
        vacancy["closedAt"] = vacancy.get("closedAt") or utc_now_iso()
        return vacancy

    def submit_application(self, candidate_user_id: str, vacancy_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        vacancy = self._vacancy(vacancy_id)
        data = _vacancy_data(vacancy)
        if data.get("status") != "published":
            raise ValueError("Application is available only for published vacancies")
        duplicate = self._active_application(candidate_user_id, vacancy_id)
        if duplicate:
            raise ValueError("Active application already exists")
        if not payload.get("consentAccepted"):
            raise ValueError("Application consent is required")
        snapshot = self._create_snapshot(candidate_user_id, vacancy_id, payload.get("sharedData", {}))
        consent = self._create_consent(candidate_user_id, vacancy_id, data["companyId"], payload)
        application = {
            "id": new_id("APP"),
            "vacancyId": vacancy_id,
            "companyId": data["companyId"],
            "candidateUserId": candidate_user_id,
            "candidateProfileSnapshotId": snapshot["id"],
            "status": "submitted",
            "pipelineStageId": "new",
            "source": _trim(payload.get("source") or "direct"),
            "coverLetter": _trim(payload.get("coverLetter"), 4000),
            "answers": _list_of_dicts(payload.get("answers")),
            "consentSnapshotId": consent["id"],
            "assignedRecruiterId": None,
            "assignedHiringManagerId": None,
            "submittedAt": utc_now_iso(),
            "updatedAt": utc_now_iso(),
        }
        self.database.insert(APPLICATIONS_COLLECTION, application["id"], application)
        self._transition(application["id"], None, "new", candidate_user_id, "submitted", "direct", "")
        self._notify("application_submitted", application)
        self._audit(candidate_user_id, "application_submitted", "application", {"company_id": data["companyId"], "vacancy_id": vacancy_id, "application_id": application["id"]})
        return self.application_detail(candidate_user_id, application["id"], candidate=True)

    def list_applications(self, user_id: str, filters: dict[str, Any], candidate: bool = False) -> dict[str, Any]:
        items = []
        for application in self.database.list(APPLICATIONS_COLLECTION):
            if candidate:
                if application.get("candidateUserId") != user_id:
                    continue
            else:
                self._require_application_access(user_id, application, write=False)
            if filters.get("vacancyId") and application.get("vacancyId") != filters["vacancyId"]:
                continue
            if filters.get("status") and application.get("status") != filters["status"]:
                continue
            items.append(self._application_summary(application, candidate=candidate))
        return _paginate(items, filters)

    def application_detail(self, user_id: str, application_id: str, candidate: bool = False) -> dict[str, Any]:
        application = self._application(application_id)
        if candidate:
            if application.get("candidateUserId") != user_id:
                raise PermissionError("Application is outside this candidate account")
        else:
            self._require_application_access(user_id, application, write=False)
        snapshot = self.database.get(APPLICATION_SNAPSHOTS_COLLECTION, application["candidateProfileSnapshotId"]) or {}
        notes = [note for note in self.database.list(APPLICATION_NOTES_COLLECTION) if note.get("applicationId") == application_id and (not candidate or note.get("visibility") == "candidate_visible")]
        return {
            "application": self._application_summary(application, candidate=candidate),
            "snapshot": snapshot,
            "consent": self.database.get(APPLICATION_CONSENTS_COLLECTION, application["consentSnapshotId"]),
            "transitions": [item for item in self.database.list(APPLICATION_TRANSITIONS_COLLECTION) if item.get("applicationId") == application_id],
            "notes": notes,
            "interviews": [item for item in self.database.list(APPLICATION_INTERVIEWS_COLLECTION) if item.get("applicationId") == application_id],
            "evaluations": [] if candidate else [item for item in self.database.list(APPLICATION_EVALUATIONS_COLLECTION) if item.get("applicationId") == application_id],
            "offers": [item for item in self.database.list(APPLICATION_OFFERS_COLLECTION) if item.get("applicationId") == application_id and (not candidate or item.get("status") in {"sent", "viewed", "accepted", "declined", "expired"})],
        }

    def withdraw_application(self, candidate_user_id: str, application_id: str) -> dict[str, Any]:
        application = self._application(application_id)
        if application.get("candidateUserId") != candidate_user_id:
            raise PermissionError("Application is outside this candidate account")
        if application.get("status") in APPLICATION_FINAL_STATUSES:
            raise ValueError("Application is already closed")
        before = application.get("pipelineStageId")
        application["status"] = "withdrawn"
        application["pipelineStageId"] = "withdrawn"
        application["withdrawnAt"] = utc_now_iso()
        application["updatedAt"] = utc_now_iso()
        self.database.update(APPLICATIONS_COLLECTION, application_id, application)
        self._transition(application_id, before, "withdrawn", candidate_user_id, "candidate_withdrew", "manual", "Candidate withdrew application")
        self._notify("application_withdrawn", application)
        self._audit(candidate_user_id, "application_withdrawn", "application", {"company_id": application["companyId"], "application_id": application_id})
        return self.application_detail(candidate_user_id, application_id, candidate=True)

    def transition_stage(self, user_id: str, application_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        application = self._application(application_id)
        self._require_application_access(user_id, application, write=True)
        if application.get("status") in {"withdrawn", "archived"}:
            raise ValueError("Closed application cannot be moved")
        target = _trim(payload.get("toStageId") or payload.get("stage") or payload.get("status"), 80)
        if not target:
            raise ValueError("Target stage is required")
        vacancy = self._vacancy(application["vacancyId"])
        vacancy_data = _vacancy_data(vacancy)
        self._stage_guard(application, vacancy_data, target, payload)
        before = application.get("pipelineStageId")
        application["pipelineStageId"] = target
        application["status"] = PIPELINE_STAGE_TO_STATUS.get(target, target)
        if application["status"] == "rejected":
            application["rejectedAt"] = utc_now_iso()
        if application["status"] == "hired":
            application["hiredAt"] = utc_now_iso()
        application["updatedAt"] = utc_now_iso()
        self.database.update(APPLICATIONS_COLLECTION, application_id, application)
        self._transition(application_id, before, target, user_id, _trim(payload.get("reasonCode"), 80), _trim(payload.get("source") or "manual", 40), _trim(payload.get("comment"), 1000))
        self._notify("application_stage_changed", application)
        self._audit(user_id, "application_stage_changed", "application", {"company_id": application["companyId"], "application_id": application_id, "from": before, "to": target})
        if application["status"] == "rejected":
            self._audit(user_id, "application_rejected", "application", {"company_id": application["companyId"], "application_id": application_id, "reason": payload.get("reasonCode")})
        if application["status"] == "hired":
            self._audit(user_id, "candidate_hired", "application", {"company_id": application["companyId"], "application_id": application_id})
        return self.application_detail(user_id, application_id)

    def add_note(self, user_id: str, application_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        application = self._application(application_id)
        self._require_application_access(user_id, application, write=True)
        content = _trim(payload.get("content"), 4000)
        if not content:
            raise ValueError("Note content is required")
        note = {"id": new_id("NOTE"), "applicationId": application_id, "authorUserId": user_id, "visibility": _trim(payload.get("visibility") or "team", 40), "content": content, "createdAt": utc_now_iso(), "updatedAt": None, "history": []}
        self.database.insert(APPLICATION_NOTES_COLLECTION, note["id"], note)
        self._audit(user_id, "application_note_created", "application", {"company_id": application["companyId"], "application_id": application_id})
        return note

    def schedule_interview(self, user_id: str, application_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        application = self._application(application_id)
        self._require_application_access(user_id, application, write=True)
        interview = {
            "id": new_id("INT"),
            "applicationId": application_id,
            "type": _trim(payload.get("type") or "screening", 80),
            "date": _trim(payload.get("date"), 40),
            "time": _trim(payload.get("time"), 20),
            "timezone": _trim(payload.get("timezone") or "UTC", 60),
            "durationMinutes": max(15, _safe_int(payload.get("durationMinutes"), 30)),
            "participants": _string_list(payload.get("participants")),
            "location": _trim(payload.get("location"), 220),
            "videoLink": _trim(payload.get("videoLink"), 300) if payload.get("videoIntegrationEnabled") else "",
            "description": _trim(payload.get("description"), 1000),
            "status": "scheduled",
            "reminders": _list_of_dicts(payload.get("reminders")),
            "feedback": [],
            "createdAt": utc_now_iso(),
            "updatedAt": utc_now_iso(),
        }
        if not interview["date"] or not interview["time"]:
            raise ValueError("Interview date and time are required")
        self.database.insert(APPLICATION_INTERVIEWS_COLLECTION, interview["id"], interview)
        self._notify("interview_scheduled", application)
        self._audit(user_id, "interview_scheduled", "interview", {"company_id": application["companyId"], "application_id": application_id, "interview_id": interview["id"]})
        return interview

    def list_interviews(self, user_id: str, application_id: str) -> list[dict[str, Any]]:
        application = self._application(application_id)
        self._require_application_access(user_id, application, write=False)
        return [item for item in self.database.list(APPLICATION_INTERVIEWS_COLLECTION) if item.get("applicationId") == application_id]

    def update_interview(self, user_id: str, interview_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        interview = self._interview(interview_id)
        application = self._application(interview["applicationId"])
        self._require_application_access(user_id, application, write=True)
        before_status = interview.get("status")
        for key in {"date", "time", "timezone", "durationMinutes", "participants", "location", "description", "status"}:
            if key in payload:
                interview[key] = payload[key]
        interview["updatedAt"] = utc_now_iso()
        self.database.update(APPLICATION_INTERVIEWS_COLLECTION, interview_id, interview)
        if before_status != interview.get("status"):
            self._notify("interview_rescheduled", application)
        return interview

    def cancel_interview(self, user_id: str, interview_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        interview = self._interview(interview_id)
        application = self._application(interview["applicationId"])
        self._require_application_access(user_id, application, write=True)
        interview["status"] = "cancelled"
        interview["cancelReason"] = _trim(payload.get("reason"), 500)
        interview["updatedAt"] = utc_now_iso()
        self.database.update(APPLICATION_INTERVIEWS_COLLECTION, interview_id, interview)
        return interview

    def add_interview_feedback(self, user_id: str, interview_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        interview = self._interview(interview_id)
        application = self._application(interview["applicationId"])
        self._require_application_access(user_id, application, write=True)
        feedback = {"id": new_id("FDB"), "authorUserId": user_id, "rating": _safe_int(payload.get("rating"), 0), "comments": _trim(payload.get("comments"), 2000), "createdAt": utc_now_iso()}
        interview.setdefault("feedback", []).append(feedback)
        interview["updatedAt"] = utc_now_iso()
        self.database.update(APPLICATION_INTERVIEWS_COLLECTION, interview_id, interview)
        return feedback

    def submit_evaluation(self, user_id: str, application_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        application = self._application(application_id)
        self._require_application_access(user_id, application, write=True)
        evaluation = {"id": new_id("EVL"), "applicationId": application_id, "evaluatorUserId": user_id, "stageId": application.get("pipelineStageId"), "scores": payload.get("scores", {}), "criteria": _list_of_dicts(payload.get("criteria")), "recommendation": _trim(payload.get("recommendation") or "neutral", 40), "comments": _trim(payload.get("comments"), 2000), "submittedAt": utc_now_iso()}
        self.database.insert(APPLICATION_EVALUATIONS_COLLECTION, evaluation["id"], evaluation)
        self._audit(user_id, "evaluation_submitted", "evaluation", {"company_id": application["companyId"], "application_id": application_id})
        return evaluation

    def create_offer(self, user_id: str, application_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        application = self._application(application_id)
        self._require_application_access(user_id, application, write=True)
        vacancy = self._vacancy(application["vacancyId"])
        vacancy_data = _vacancy_data(vacancy)
        offer = {
            "id": new_id("OFR"),
            "applicationId": application_id,
            "vacancyId": application["vacancyId"],
            "companyId": application["companyId"],
            "status": "draft",
            "positionTitle": _trim(payload.get("positionTitle") or vacancy_data.get("title"), 180),
            "salary": payload.get("salary") or vacancy_data.get("salary") or {},
            "employmentType": _trim(payload.get("employmentType") or (vacancy_data.get("employmentTypes") or [""])[0], 80),
            "locationId": _trim(payload.get("locationId"), 80),
            "startDate": _trim(payload.get("startDate"), 40),
            "probationPeriod": _trim(payload.get("probationPeriod"), 80),
            "benefits": _string_list(payload.get("benefits")),
            "conditions": _string_list(payload.get("conditions")),
            "expiresAt": _trim(payload.get("expiresAt"), 40),
            "createdByUserId": user_id,
            "approvedByUserId": None,
            "sentAt": None,
            "acceptedAt": None,
            "createdAt": utc_now_iso(),
            "updatedAt": utc_now_iso(),
        }
        _validate_salary(offer["salary"])
        self.database.insert(APPLICATION_OFFERS_COLLECTION, offer["id"], offer)
        self._audit(user_id, "offer_created", "offer", {"company_id": application["companyId"], "application_id": application_id, "offer_id": offer["id"]})
        return offer

    def update_offer(self, user_id: str, offer_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        offer = self._offer(offer_id)
        application = self._application(offer["applicationId"])
        self._require_application_access(user_id, application, write=True)
        if offer.get("status") not in {"draft", "pending_approval"}:
            raise ValueError("Only draft offers can be edited")
        for key in {"positionTitle", "salary", "employmentType", "locationId", "startDate", "probationPeriod", "benefits", "conditions", "expiresAt", "status"}:
            if key in payload:
                offer[key] = payload[key]
        _validate_salary(offer.get("salary") or {})
        offer["updatedAt"] = utc_now_iso()
        self.database.update(APPLICATION_OFFERS_COLLECTION, offer_id, offer)
        return offer

    def send_offer(self, user_id: str, offer_id: str) -> dict[str, Any]:
        offer = self._offer(offer_id)
        application = self._application(offer["applicationId"])
        self._require_application_access(user_id, application, write=True)
        if offer.get("status") not in {"draft", "pending_approval"}:
            raise ValueError("Offer cannot be sent from current status")
        offer["status"] = "sent"
        offer["sentAt"] = utc_now_iso()
        offer["updatedAt"] = utc_now_iso()
        self.database.update(APPLICATION_OFFERS_COLLECTION, offer_id, offer)
        self._notify("offer_sent", application)
        self._audit(user_id, "offer_sent", "offer", {"company_id": application["companyId"], "application_id": application["id"], "offer_id": offer_id})
        return offer

    def accept_offer(self, candidate_user_id: str, offer_id: str) -> dict[str, Any]:
        offer = self._offer(offer_id)
        application = self._application(offer["applicationId"])
        if application.get("candidateUserId") != candidate_user_id:
            raise PermissionError("Offer is outside this candidate account")
        if offer.get("status") != "sent":
            raise ValueError("Offer is not available for acceptance")
        offer["status"] = "accepted"
        offer["acceptedAt"] = utc_now_iso()
        offer["updatedAt"] = utc_now_iso()
        self.database.update(APPLICATION_OFFERS_COLLECTION, offer_id, offer)
        before = application.get("pipelineStageId")
        application["pipelineStageId"] = "hired"
        application["status"] = "hired"
        application["hiredAt"] = utc_now_iso()
        application["updatedAt"] = utc_now_iso()
        self.database.update(APPLICATIONS_COLLECTION, application["id"], application)
        self._transition(application["id"], before, "hired", candidate_user_id, "offer_accepted", "manual", "Candidate accepted offer")
        self._notify("offer_accepted", application)
        self._audit(candidate_user_id, "offer_accepted", "offer", {"company_id": application["companyId"], "application_id": application["id"], "offer_id": offer_id})
        self._audit(candidate_user_id, "candidate_hired", "application", {"company_id": application["companyId"], "application_id": application["id"]})
        return offer

    def decline_offer(self, candidate_user_id: str, offer_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        offer = self._offer(offer_id)
        application = self._application(offer["applicationId"])
        if application.get("candidateUserId") != candidate_user_id:
            raise PermissionError("Offer is outside this candidate account")
        if offer.get("status") != "sent":
            raise ValueError("Offer is not available for decline")
        offer["status"] = "declined"
        offer["declineReason"] = _trim(payload.get("reason"), 500)
        offer["updatedAt"] = utc_now_iso()
        self.database.update(APPLICATION_OFFERS_COLLECTION, offer_id, offer)
        self._notify("offer_declined", application)
        self._audit(candidate_user_id, "offer_declined", "offer", {"company_id": application["companyId"], "application_id": application["id"], "offer_id": offer_id})
        return offer

    def _publication_errors(self, vacancy: dict[str, Any]) -> list[str]:
        errors = []
        company = self.database.get(COMPANY_COLLECTION, vacancy.get("companyId")) or {}
        if not company:
            errors.append("Company is missing")
        if not vacancy.get("title") or not vacancy.get("description"):
            errors.append("Title and description are required")
        if _safe_int(vacancy.get("quantity"), 0) <= 0:
            errors.append("Quantity must be greater than zero")
        if not vacancy.get("pipelineId"):
            errors.append("Pipeline is required")
        if not vacancy.get("locationIds") and "remote" not in vacancy.get("workModes", []):
            errors.append("Location or remote mode is required")
        try:
            _validate_salary(vacancy.get("salary") or {})
        except ValueError as error:
            errors.append(str(error))
        if not self._required_consents_complete(vacancy.get("companyId")):
            errors.append("Required employer consents are missing")
        return errors

    def _set_vacancy_status(self, user_id: str, vacancy_id: str, status: str, event: str) -> dict[str, Any]:
        vacancy = self._vacancy(vacancy_id)
        data = _vacancy_data(vacancy)
        self._require_permission(user_id, data.get("companyId"), "hiring:manage")
        before = dict(data)
        data["status"] = status
        data["updatedAt"] = utc_now_iso()
        if status == "closed":
            data["closedAt"] = utc_now_iso()
        vacancy.status = status
        vacancy.metadata["recruitment"] = data
        vacancy.metadata.setdefault("version_history", []).append(_version(event, before, data, user_id))
        self.vacancies.update(vacancy)
        self._audit(user_id, event, "vacancy", {"company_id": data["companyId"], "vacancy_id": vacancy_id})
        return self._vacancy_response(vacancy)

    def _payload_from_hiring_need(self, company_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        hiring_need_id = _trim(payload.get("hiringNeedId") or payload.get("hiring_need_id"))
        source = None
        for item in self.database.list(HIRING_NEEDS_COLLECTION):
            if item.get("id") == hiring_need_id and item.get("companyId") == company_id:
                source = item
                break
        if not source:
            raise ValueError("Hiring need not found")
        salary = source.get("salary") or {}
        seeded = {
            "companyId": company_id,
            "hiringNeedId": hiring_need_id,
            "title": source.get("professionLabel"),
            "professionLabel": source.get("professionLabel"),
            "normalizedProfessionKey": source.get("professionKey"),
            "quantity": source.get("quantity"),
            "locationIds": source.get("locationIds", []),
            "targetStartDate": source.get("targetStartDate"),
            "employmentTypes": source.get("employmentTypes", []),
            "salary": salary,
            "languageRequirements": source.get("languageRequirements", []),
            "skillRequirements": source.get("skillRequirements", []),
            "credentialRequirements": source.get("credentialRequirements", []),
            "housing": {"provided": bool(source.get("housingProvided")), "paidBy": "unknown"},
            "transport": {"provided": bool(source.get("transportProvided")), "paidBy": "unknown"},
            "legalization": {"provided": bool(source.get("legalizationSupport")), "notes": ""},
        }
        return {**seeded, **payload}

    def _create_snapshot(self, candidate_user_id: str, vacancy_id: str, shared_data: dict[str, Any]) -> dict[str, Any]:
        candidate = next((item for item in self.candidates.list() if item.user_id == candidate_user_id), None)
        snapshot = {
            "id": new_id("SNP"),
            "candidateUserId": candidate_user_id,
            "vacancyId": vacancy_id,
            "allowedFields": sorted(shared_data.keys()),
            "data": shared_data or (candidate.to_dict() if candidate else {"candidateUserId": candidate_user_id}),
            "createdAt": utc_now_iso(),
            "immutable": True,
        }
        self.database.insert(APPLICATION_SNAPSHOTS_COLLECTION, snapshot["id"], snapshot)
        return snapshot

    def _create_consent(self, candidate_user_id: str, vacancy_id: str, company_id: str, payload: dict[str, Any]) -> dict[str, Any]:
        consent = {"id": new_id("ACON"), "candidateUserId": candidate_user_id, "companyId": company_id, "vacancyId": vacancy_id, "purpose": "recruitment_application", "retention": _trim(payload.get("retention") or "recruitment_period_plus_legal_retention", 120), "accepted": True, "sharedDataKeys": sorted((payload.get("sharedData") or {}).keys()), "createdAt": utc_now_iso()}
        self.database.insert(APPLICATION_CONSENTS_COLLECTION, consent["id"], consent)
        return consent

    def _stage_guard(self, application: dict[str, Any], vacancy: dict[str, Any], target: str, payload: dict[str, Any]) -> None:
        if _trim(payload.get("source") or "manual") == "ai_recommendation":
            raise ValueError("AI recommendation cannot move pipeline stage automatically")
        if target == "offer" and not (vacancy.get("salary") or {}).get("minimum") and not (vacancy.get("salary") or {}).get("maximum"):
            raise ValueError("Cannot move to offer without salary")
        if target == "rejected":
            reason = _trim(payload.get("reasonCode"), 80)
            if reason not in SAFE_REJECTION_CODES:
                raise ValueError("Safe rejection reason code is required")
        if target == "hired" and not (payload.get("decisionConfirmed") or payload.get("reasonCode") == "offer_accepted"):
            raise ValueError("Hired transition requires decision confirmation")

    def _required_consents_complete(self, company_id: str) -> bool:
        records = [item for item in self.database.list(EMPLOYER_CONSENTS_COLLECTION) if item.get("companyId") == company_id]
        required = {item["key"]: item.get("granted") for item in records if item.get("type") == "required"}
        return all(required.get(key) for key in {"termsForBusiness", "dataProcessing", "representativeAuthority", "lawfulCandidateUse", "nonDiscrimination"})

    def _require_permission(self, user_id: str, company_id: str, permission: str, allow_manage: bool = False) -> dict[str, Any]:
        member = next((item for item in self.database.list(COMPANY_MEMBERS_COLLECTION) if item.get("companyId") == company_id and item.get("userId") == user_id and item.get("status") == "active"), None)
        if not member:
            raise PermissionError("No active membership for company")
        permissions = ROLE_PERMISSIONS.get(member.get("role"), set())
        if permission in permissions or (allow_manage and "hiring:manage" in permissions):
            return member
        raise PermissionError("Insufficient company permission")

    def _require_application_access(self, user_id: str, application: dict[str, Any], write: bool) -> dict[str, Any]:
        vacancy = self._vacancy(application["vacancyId"])
        data = _vacancy_data(vacancy)
        member = self._require_permission(user_id, application["companyId"], "hiring:manage" if write else "hiring:read", allow_manage=True)
        if member.get("role") == "recruiter" and data.get("recruiterIds") and user_id not in data.get("recruiterIds", []):
            raise PermissionError("Recruiter is not assigned to this vacancy")
        if member.get("role") == "hiring_manager" and data.get("hiringManagerIds") and user_id not in data.get("hiringManagerIds", []):
            raise PermissionError("Hiring manager is not assigned to this vacancy")
        return member

    def _vacancy(self, vacancy_id: str) -> Vacancy:
        vacancy = self.vacancies.get(vacancy_id)
        if not vacancy:
            raise ValueError("Vacancy not found")
        return vacancy

    def _application(self, application_id: str) -> dict[str, Any]:
        application = self.database.get(APPLICATIONS_COLLECTION, application_id)
        if not application:
            raise ValueError("Application not found")
        return application

    def _interview(self, interview_id: str) -> dict[str, Any]:
        interview = self.database.get(APPLICATION_INTERVIEWS_COLLECTION, interview_id)
        if not interview:
            raise ValueError("Interview not found")
        return interview

    def _offer(self, offer_id: str) -> dict[str, Any]:
        offer = self.database.get(APPLICATION_OFFERS_COLLECTION, offer_id)
        if not offer:
            raise ValueError("Offer not found")
        return offer

    def _active_application(self, candidate_user_id: str, vacancy_id: str) -> dict[str, Any] | None:
        for application in self.database.list(APPLICATIONS_COLLECTION):
            if application.get("candidateUserId") == candidate_user_id and application.get("vacancyId") == vacancy_id and application.get("status") in APPLICATION_ACTIVE_STATUSES:
                return application
        return None

    def _transition(self, application_id: str, from_stage: str | None, to_stage: str, user_id: str, reason: str, source: str, comment: str) -> dict[str, Any]:
        transition = {"id": new_id("TRN"), "applicationId": application_id, "fromStageId": from_stage, "toStageId": to_stage, "changedByUserId": user_id, "reasonCode": reason, "comment": comment, "source": source, "createdAt": utc_now_iso()}
        self.database.insert(APPLICATION_TRANSITIONS_COLLECTION, transition["id"], transition)
        return transition

    def _notify(self, event_type: str, application: dict[str, Any]) -> None:
        event = {"id": new_id("NTF"), "type": event_type, "companyId": application.get("companyId"), "vacancyId": application.get("vacancyId"), "applicationId": application.get("id"), "createdAt": utc_now_iso(), "channels": []}
        self.database.insert(NOTIFICATIONS_COLLECTION, event["id"], event)

    def _audit(self, user_id: str, action: str, entity: str, metadata: dict[str, Any]) -> None:
        self.activity.add(ActivityEvent(entity_type=entity, entity_id=metadata.get("application_id") or metadata.get("vacancy_id") or metadata.get("company_id") or user_id, action=action, old_value=None, new_value=entity, actor_id=user_id, metadata=metadata))

    def _vacancy_response(self, vacancy: Vacancy, public: bool = False) -> dict[str, Any]:
        data = _vacancy_data(vacancy)
        base = {"id": vacancy.id, **data}
        if public:
            for key in ("ownerUserId", "recruiterIds", "hiringManagerIds", "pipelineId"):
                base.pop(key, None)
            base["requirements"] = [{key: value for key, value in item.items() if key not in {"weight"}} for item in base.get("requirements", [])]
        else:
            base["versionHistory"] = vacancy.metadata.get("version_history", [])
        return base

    def _application_summary(self, application: dict[str, Any], candidate: bool = False) -> dict[str, Any]:
        status = _candidate_status(application.get("status")) if candidate else application.get("status")
        snapshot = self.database.get(APPLICATION_SNAPSHOTS_COLLECTION, application.get("candidateProfileSnapshotId")) or {}
        snapshot_data = snapshot.get("data") if isinstance(snapshot.get("data"), dict) else {}
        return {**application, "candidateName": snapshot_data.get("name") or snapshot_data.get("fullName") or application.get("candidateUserId"), "displayStatus": status}


def _normalize_vacancy_payload(user_id: str, company_id: str, payload: dict[str, Any], source: str, existing: dict[str, Any] | None = None) -> dict[str, Any]:
    title = _trim(payload.get("title") or payload.get("professionLabel"), 180)
    if not title:
        raise ValueError("Vacancy title is required")
    salary = payload.get("salary") if isinstance(payload.get("salary"), dict) else {
        "visible": bool(payload.get("salaryVisible", True)),
        "minimum": _safe_float(payload.get("salary_min") or payload.get("salaryMinimum")),
        "maximum": _safe_float(payload.get("salary_max") or payload.get("salaryMaximum")),
        "currency": _trim(payload.get("currency") or ""),
        "period": _trim(payload.get("period") or "month"),
        "grossNet": _trim(payload.get("grossNet") or "unknown"),
        "negotiable": bool(payload.get("negotiable", False)),
        "notes": _trim(payload.get("salaryNotes"), 400),
    }
    _validate_salary(salary)
    now = utc_now_iso()
    status = _trim(payload.get("status") or (existing or {}).get("status") or "draft")
    if status not in VACANCY_STATUSES:
        raise ValueError("Unsupported vacancy status")
    return {
        "companyId": company_id,
        "hiringNeedId": _trim(payload.get("hiringNeedId") or payload.get("hiring_need_id")),
        "status": status,
        "title": title,
        "normalizedProfessionKey": _trim(payload.get("normalizedProfessionKey") or payload.get("professionKey") or title.lower().replace(" ", "_"), 120),
        "professionLabel": _trim(payload.get("professionLabel") or title, 180),
        "description": _trim(payload.get("description"), 5000),
        "responsibilities": _string_list(payload.get("responsibilities")),
        "requirements": [_normalize_requirement(item) for item in _list_of_dicts(payload.get("requirements"))],
        "preferredQualifications": [_normalize_requirement(item, required_default=False) for item in _list_of_dicts(payload.get("preferredQualifications"))],
        "employmentTypes": _string_list(payload.get("employmentTypes")),
        "workModes": _string_list(payload.get("workModes")) or ["onsite"],
        "locationIds": _string_list(payload.get("locationIds")) or _string_list(payload.get("locations")),
        "remoteCountries": _string_list(payload.get("remoteCountries")),
        "quantity": max(0, _safe_int(payload.get("quantity"), 1)),
        "applicationDeadline": _trim(payload.get("applicationDeadline"), 40),
        "targetStartDate": _trim(payload.get("targetStartDate"), 40),
        "salary": salary,
        "benefits": _list_of_dicts(payload.get("benefits")) or [{"label": item} for item in _string_list(payload.get("benefits"))],
        "schedule": payload.get("schedule") if isinstance(payload.get("schedule"), dict) else {},
        "housing": _support(payload.get("housing")),
        "transport": _support(payload.get("transport")),
        "meals": _support(payload.get("meals")),
        "legalization": _support(payload.get("legalization")),
        "training": _support(payload.get("training")),
        "insurance": _support(payload.get("insurance")),
        "relocation": _support(payload.get("relocation")),
        "languageRequirements": _list_of_dicts(payload.get("languageRequirements")),
        "skillRequirements": _list_of_dicts(payload.get("skillRequirements")),
        "credentialRequirements": _list_of_dicts(payload.get("credentialRequirements")),
        "workAuthorizationRequirements": _list_of_dicts(payload.get("workAuthorizationRequirements")),
        "experienceMinimumYears": _safe_int(payload.get("experienceMinimumYears"), 0),
        "educationRequirements": _list_of_dicts(payload.get("educationRequirements")),
        "pipelineId": _trim(payload.get("pipelineId") or f"PIPE-{company_id}", 120),
        "ownerUserId": _trim(payload.get("ownerUserId") or user_id, 120),
        "recruiterIds": _string_list(payload.get("recruiterIds")),
        "hiringManagerIds": _string_list(payload.get("hiringManagerIds")),
        "visibility": _trim(payload.get("visibility") or "public", 40),
        "source": source,
        "version": int((existing or {}).get("version", 0)) or 1,
        "publishedAt": (existing or {}).get("publishedAt"),
        "closedAt": (existing or {}).get("closedAt"),
        "createdAt": (existing or {}).get("createdAt") or now,
        "updatedAt": now,
        "screeningQuestions": [_normalize_question(item) for item in _list_of_dicts(payload.get("screeningQuestions"))],
    }


def _normalize_requirement(item: dict[str, Any], required_default: bool = True) -> dict[str, Any]:
    return {
        "id": item.get("id") or new_id("REQ"),
        "category": _trim(item.get("category") or "other", 40),
        "label": _trim(item.get("label"), 220),
        "normalizedKey": _trim(item.get("normalizedKey") or item.get("label", "").lower().replace(" ", "_"), 120),
        "required": bool(item.get("required", required_default)),
        "weight": max(0, _safe_int(item.get("weight"), 1)),
        "minimumLevel": _trim(item.get("minimumLevel"), 80),
        "minimumYears": _safe_int(item.get("minimumYears"), 0),
        "description": _trim(item.get("description"), 1000),
    }


def _normalize_question(item: dict[str, Any]) -> dict[str, Any]:
    if item.get("sensitive"):
        raise ValueError("Sensitive screening questions are not allowed")
    return {"id": item.get("id") or new_id("QST"), "type": _trim(item.get("type") or "text", 40), "label": _trim(item.get("label"), 300), "required": bool(item.get("required")), "options": _string_list(item.get("options")), "validation": item.get("validation") if isinstance(item.get("validation"), dict) else {}, "disqualifyingAnswer": item.get("disqualifyingAnswer"), "sensitive": False, "displayOrder": _safe_int(item.get("displayOrder"), 0)}


def _support(value: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    return {"provided": bool(value), "paidBy": "unknown"}


def _validate_salary(salary: dict[str, Any]) -> None:
    minimum = _safe_float(salary.get("minimum"))
    maximum = _safe_float(salary.get("maximum"))
    if minimum is not None and maximum is not None and minimum > maximum:
        raise ValueError("Salary minimum cannot exceed maximum")
    if (minimum is not None or maximum is not None) and not _trim(salary.get("currency")):
        raise ValueError("Salary currency is required when salary is provided")
    if _trim(salary.get("grossNet") or "unknown") not in {"gross", "net", "unknown"}:
        raise ValueError("Salary gross/net value is invalid")


def _vacancy_data(vacancy: Vacancy) -> dict[str, Any]:
    if isinstance(vacancy.metadata.get("recruitment"), dict):
        return vacancy.metadata["recruitment"]
    return {"companyId": vacancy.employer_id, "status": vacancy.status, "title": vacancy.title, "professionLabel": vacancy.title, "description": "", "quantity": 1, "salary": {"minimum": vacancy.salary_min, "maximum": vacancy.salary_max, "currency": vacancy.currency, "visible": True, "period": "month", "grossNet": "unknown", "negotiable": False}, "pipelineId": f"PIPE-{vacancy.employer_id}", "locationIds": [vacancy.location] if vacancy.location else [], "workModes": ["onsite"], "version": 1, "createdAt": vacancy.created_at, "updatedAt": vacancy.created_at}


def _public_company(company: dict[str, Any]) -> dict[str, Any]:
    return {"id": company.get("id"), "legalName": company.get("legal_name"), "tradingName": company.get("trading_name"), "verificationStatus": company.get("verification_status", "unverified"), "industry": company.get("industry")}


def _version(action: str, before: dict[str, Any] | None, after: dict[str, Any], user_id: str) -> dict[str, Any]:
    watched = {"salary", "locationIds", "requirements", "description", "quantity", "applicationDeadline", "status", "recruiterIds", "hiringManagerIds"}
    changes = {key: {"before": (before or {}).get(key), "after": after.get(key)} for key in watched if (before or {}).get(key) != after.get(key)}
    return {"id": new_id("VER"), "action": action, "changedByUserId": user_id, "changes": changes, "createdAt": utc_now_iso()}


def _candidate_status(status: str) -> str:
    if status in {"submitted", "screening", "qualified", "under_review", "assessment"}:
        return "under_review" if status != "submitted" else "submitted"
    if status == "interview":
        return "interview"
    if status == "offer":
        return "offer"
    if status in {"hired", "rejected", "withdrawn", "archived"}:
        return "closed" if status != "hired" else "decision"
    return "submitted"


def _paginate(items: list[dict[str, Any]], filters: dict[str, Any]) -> dict[str, Any]:
    limit = min(100, max(1, _safe_int(filters.get("limit"), 25)))
    offset = max(0, _safe_int(filters.get("offset"), 0))
    return {"items": items[offset : offset + limit], "page": {"limit": limit, "offset": offset, "returned": len(items[offset : offset + limit]), "total": len(items)}}


def _trim(value: Any, max_length: int = 200) -> str:
    return str(value or "").strip()[:max_length]


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any) -> float | None:
    try:
        if value in {None, ""}:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_trim(item, 160) for item in value if _trim(item, 160)]
    if isinstance(value, str):
        return [_trim(item, 160) for item in value.split(",") if _trim(item, 160)]
    return []


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []
