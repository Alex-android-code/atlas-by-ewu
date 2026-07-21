"""Persisted onboarding workflow for ATLAS employer/company workspaces."""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from core.models import ActivityEvent, Document, DocumentStatus, Employer, new_id, utc_now_iso
from database.json_database import JsonDatabase
from database.repositories import ActivityRepository, DocumentRepository, EmployerRepository


EMPLOYER_ONBOARDING_COLLECTION = "employer_onboarding_sessions"
COMPANY_COLLECTION = "companies"
COMPANY_MEMBERS_COLLECTION = "company_members"
COMPANY_INVITATIONS_COLLECTION = "company_invitations"
COMPANY_VERIFICATIONS_COLLECTION = "company_verifications"
COMPANY_LOCATIONS_COLLECTION = "company_locations"
HIRING_NEEDS_COLLECTION = "hiring_needs"
HIRING_PROCESS_COLLECTION = "hiring_processes"
EMPLOYER_CONSENTS_COLLECTION = "employer_consents"

EMPLOYER_STEPS = [
    "welcome",
    "employer_agent",
    "company_identity",
    "company_verification",
    "company_profile",
    "locations",
    "team",
    "hiring_needs",
    "hiring_process",
    "integrations",
    "consents",
    "completion",
]
OPTIONAL_STEPS = {"team", "integrations"}
REQUIRED_CONSENTS = {"termsForBusiness", "dataProcessing", "representativeAuthority", "lawfulCandidateUse", "nonDiscrimination"}
EMPLOYER_ROLES = {"company_owner", "company_admin", "hr_manager", "recruiter", "hiring_manager", "viewer"}
ROLE_PERMISSIONS = {
    "company_owner": {"company:read", "company:write", "company:delete", "members:manage", "subscription:manage", "verification:submit", "hiring:manage", "pipeline:manage", "consents:manage"},
    "company_admin": {"company:read", "company:write", "members:manage", "verification:submit", "hiring:manage", "pipeline:manage", "consents:manage"},
    "hr_manager": {"company:read", "members:read", "hiring:manage", "pipeline:manage", "reports:read"},
    "recruiter": {"company:read", "hiring:read", "candidates:manage", "pipeline:update"},
    "hiring_manager": {"company:read", "hiring:assigned", "interviews:manage", "decisions:limited"},
    "viewer": {"company:read"},
}
COMPLETENESS_WEIGHTS = {"identity": 20, "verification": 20, "profile": 15, "locations": 10, "team": 10, "hiring_needs": 10, "hiring_process": 10, "consents": 5}
DEFAULT_PIPELINE = ["new", "screening", "qualified", "interview", "technical_assessment", "client_review", "offer", "hired", "rejected", "withdrawn"]
FINAL_PIPELINE_STAGES = {"hired", "rejected", "withdrawn"}


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
                "company_id": None,
                "employer_id": None,
                "membership_id": None,
                "audit_log": [_audit("session_created", "welcome", user_id)],
                "created_at": utc_now_iso(),
                "updated_at": utc_now_iso(),
                "completed_at": None,
            }
            self.database.insert(EMPLOYER_ONBOARDING_COLLECTION, user_id, session)
        return _with_progress(session)

    def patch_step(self, user_id: str, step: str, data: dict[str, Any] | None = None, next_step: str | None = None) -> dict[str, Any]:
        step = _canonical_step(step)
        if step not in EMPLOYER_STEPS:
            raise ValueError(f"Unknown employer onboarding step: {step}")
        session = self.get_or_start(user_id)
        session["status"] = "completed" if session.get("status") == "completed" else "in_progress"
        normalized = self._validate_step(user_id, session, step, data or {})
        session.setdefault("data", {})[step] = normalized
        legacy_key = _legacy_step_key(step)
        if legacy_key != step:
            session["data"][legacy_key] = normalized
        if step not in session.setdefault("completed_steps", []):
            session["completed_steps"].append(step)
        self._apply_step_side_effects(user_id, session, step, normalized)
        target_next = _canonical_step(next_step) if next_step else None
        session["current_step"] = target_next if target_next in EMPLOYER_STEPS else _next_step(step)
        session["updated_at"] = utc_now_iso()
        session.setdefault("audit_log", []).append(_audit("step_saved", step, user_id))
        self.database.update(EMPLOYER_ONBOARDING_COLLECTION, user_id, session)
        self._record_activity(user_id, "employer_onboarding_step_saved", step, {"company_id": session.get("company_id")})
        return _with_progress(session)

    def complete(self, user_id: str) -> dict[str, Any]:
        session = self.get_or_start(user_id)
        if session.get("status") == "completed":
            employer = self._employer_for_session(session)
            return {
                "session": _with_progress(session),
                "employer": employer.to_dict() if employer else _draft_employer(session),
                "dashboard": self.dashboard(user_id),
                "dashboard_route": "/employer/dashboard",
            }
        errors = self._completion_errors(user_id, session)
        if errors:
            session.setdefault("audit_log", []).append(_audit("completion_blocked", "completion", user_id))
            session["updated_at"] = utc_now_iso()
            self.database.update(EMPLOYER_ONBOARDING_COLLECTION, user_id, session)
            self._record_activity(user_id, "employer_onboarding_completion_blocked", "completion", {"errors": errors})
            raise ValueError("; ".join(errors))
        company = self._ensure_company(user_id, session, session.get("data", {}).get("company_identity", {}))
        employer = self._upsert_employer(user_id, session, company)
        session["company_id"] = company["id"]
        session["employer_id"] = employer.id
        session["status"] = "completed"
        session["current_step"] = "completion"
        if "completion" not in session.setdefault("completed_steps", []):
            session["completed_steps"].append("completion")
        session["completed_at"] = session.get("completed_at") or utc_now_iso()
        session["updated_at"] = utc_now_iso()
        session.setdefault("audit_log", []).append(_audit("employer_onboarding_completed", "completion", user_id))
        self.database.update(EMPLOYER_ONBOARDING_COLLECTION, user_id, session)
        self._record_activity(user_id, "employer_onboarding_completed", "completion", {"company_id": company["id"]})
        return {"session": _with_progress(session), "employer": employer.to_dict(), "dashboard": self.dashboard(user_id), "dashboard_route": "/employer/dashboard"}

    def dashboard(self, user_id: str) -> dict[str, Any]:
        session = self.get_or_start(user_id)
        company = self._company_for_session(session)
        membership = self._membership_for_user(user_id, company["id"]) if company else None
        if company and not membership:
            raise PermissionError("No membership for company")
        documents = self._company_documents(company["id"] if company else None, user_id)
        verification = self._latest_verification(company["id"] if company else None)
        hiring_needs = self._hiring_needs(company["id"] if company else None)
        members = self._members(company["id"] if company else None)
        invitations = self._invitations(company["id"] if company else None)
        consents = self._consent_summary(company["id"] if company else None)
        agent = session.get("data", {}).get("employer_agent", {})
        readiness = _readiness(company, verification, hiring_needs, members, consents, documents)
        company_payload = _dashboard_company(company, readiness["profileCompleteness"]) if company else _draft_company(session)
        return {
            "user": {"id": user_id},
            "company": company_payload,
            "employer": self._employer_for_session(session).to_dict() if self._employer_for_session(session) else _draft_employer(session),
            "membership": _membership_payload(membership),
            "onboarding": {
                "status": session.get("status"),
                "currentStep": session.get("current_step"),
                "completedAt": session.get("completed_at"),
                "redirectTo": None if session.get("status") == "completed" else f"/employer/onboarding?step={session.get('current_step') or 'welcome'}",
            },
            "verification": verification or {"status": "unverified"},
            "agent": {"name": agent.get("name") or "ATLAS Employer Agent", "status": "configured" if agent else "not_configured", "enabledCapabilities": agent.get("enabled_capabilities", [])},
            "hiringNeeds": _hiring_summary(hiring_needs),
            "team": {"activeMembers": len([m for m in members if m.get("status") == "active"]), "pendingInvitations": len([i for i in invitations if i.get("status") == "pending"])},
            "consents": consents,
            "readiness": readiness,
            "documents": documents,
            "recommendedActions": _actions(session, readiness),
            "recentActivity": _activity(self.activity.list(), user_id, company["id"] if company else None),
            "quickActions": [
                {"id": "edit_company", "title": "Edit company profile", "route": "/employer/onboarding?step=company_profile"},
                {"id": "verification", "title": "Submit verification", "route": "/employer/onboarding?step=company_verification"},
                {"id": "team", "title": "Manage team", "route": "/employer/onboarding?step=team"},
                {"id": "hiring", "title": "Update hiring needs", "route": "/employer/onboarding?step=hiring_needs"},
            ],
        }

    def get_company(self, user_id: str, company_id: str) -> dict[str, Any]:
        self._require_permission(user_id, company_id, "company:read")
        company = self._company(company_id)
        if not company:
            raise ValueError("Company not found")
        return company

    def update_company(self, user_id: str, company_id: str, data: dict[str, Any]) -> dict[str, Any]:
        self._require_permission(user_id, company_id, "company:write")
        company = self._company(company_id)
        if not company:
            raise ValueError("Company not found")
        allowed = {"legal_name", "trading_name", "official_email", "phone", "website", "profile", "identity", "data_protection_roles"}
        for key in allowed:
            if key in data:
                company[key] = data[key]
        company["updated_at"] = utc_now_iso()
        self.database.update(COMPANY_COLLECTION, company_id, company)
        self._record_activity(user_id, "company_updated", "company", {"company_id": company_id})
        return company

    def submit_verification(self, user_id: str, company_id: str, data: dict[str, Any]) -> dict[str, Any]:
        self._require_permission(user_id, company_id, "verification:submit")
        file_ids = _string_list(data.get("documentFileIds") or data.get("document_file_ids"))
        if not file_ids:
            raise ValueError("Verification requires at least one document file")
        self._assert_files_owned(user_id, file_ids)
        verification = {
            "id": new_id("VRF"),
            "companyId": company_id,
            "status": "pending",
            "verificationType": _trim(data.get("verificationType") or "manual_document_review", 80),
            "source": _trim(data.get("source"), 160),
            "submittedBy": user_id,
            "documentFileIds": file_ids,
            "registryReference": _trim(data.get("registryReference"), 120),
            "rejectionReason": None,
            "reviewedBy": None,
            "submittedAt": utc_now_iso(),
            "reviewedAt": None,
            "expiresAt": None,
            "metadata": {"events": [_audit("company_verification_submitted", "company_verification", user_id)]},
        }
        self.database.insert(COMPANY_VERIFICATIONS_COLLECTION, verification["id"], verification)
        company = self._company(company_id)
        if company:
            company["verification_status"] = "pending"
            company["updated_at"] = utc_now_iso()
            self.database.update(COMPANY_COLLECTION, company_id, company)
        self._record_activity(user_id, "company_verification_submitted", "company_verification", {"company_id": company_id})
        return verification

    def list_verification(self, user_id: str, company_id: str) -> list[dict[str, Any]]:
        self._require_permission(user_id, company_id, "company:read")
        return [item for item in self.database.list(COMPANY_VERIFICATIONS_COLLECTION) if item.get("companyId") == company_id]

    def create_location(self, user_id: str, company_id: str, data: dict[str, Any]) -> dict[str, Any]:
        self._require_permission(user_id, company_id, "company:write")
        location = _normalize_location(company_id, data)
        self.database.insert(COMPANY_LOCATIONS_COLLECTION, location["id"], location)
        self._record_activity(user_id, "company_location_created", "locations", {"company_id": company_id, "location_id": location["id"]})
        return location

    def list_locations(self, user_id: str, company_id: str) -> list[dict[str, Any]]:
        self._require_permission(user_id, company_id, "company:read")
        return self._locations(company_id)

    def update_location(self, user_id: str, company_id: str, location_id: str, data: dict[str, Any]) -> dict[str, Any]:
        self._require_permission(user_id, company_id, "company:write")
        location = self.database.get(COMPANY_LOCATIONS_COLLECTION, location_id)
        if not location or location.get("companyId") != company_id:
            raise PermissionError("Location is outside this company")
        updated = {**location, **_normalize_location(company_id, {**location, **data}, location_id=location_id), "updated_at": utc_now_iso()}
        self.database.update(COMPANY_LOCATIONS_COLLECTION, location_id, updated)
        return updated

    def delete_location(self, user_id: str, company_id: str, location_id: str) -> dict[str, str]:
        self._require_permission(user_id, company_id, "company:write")
        location = self.database.get(COMPANY_LOCATIONS_COLLECTION, location_id)
        if not location or location.get("companyId") != company_id:
            raise PermissionError("Location is outside this company")
        location["active"] = False
        location["updated_at"] = utc_now_iso()
        self.database.update(COMPANY_LOCATIONS_COLLECTION, location_id, location)
        return {"status": "archived"}

    def list_members(self, user_id: str, company_id: str) -> list[dict[str, Any]]:
        self._require_permission(user_id, company_id, "members:read")
        return [_public_member(item) for item in self._members(company_id)]

    def invite_member(self, user_id: str, company_id: str, data: dict[str, Any]) -> dict[str, Any]:
        self._require_permission(user_id, company_id, "members:manage")
        email = _trim(data.get("email"), 180).lower()
        role = _trim(data.get("role") or "recruiter", 40)
        if not _valid_email(email):
            raise ValueError("Valid email is required")
        if role not in EMPLOYER_ROLES or role == "company_owner":
            raise ValueError("Unsupported invitation role")
        token = secrets.token_urlsafe(32)
        invitation = {
            "id": new_id("INV"),
            "companyId": company_id,
            "email": email,
            "role": role,
            "status": "pending",
            "tokenHash": _hash_token(token),
            "createdBy": user_id,
            "createdAt": utc_now_iso(),
            "expiresAt": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "acceptedAt": None,
            "revokedAt": None,
            "access": {"vacancyIds": _string_list(data.get("vacancyIds"))},
        }
        self.database.insert(COMPANY_INVITATIONS_COLLECTION, invitation["id"], invitation)
        self._record_activity(user_id, "company_member_invited", "team", {"company_id": company_id, "role": role})
        return {**_public_invitation(invitation), "token": token}

    def get_invitation_by_token(self, token: str) -> dict[str, Any]:
        invitation = self._invitation_for_token(token)
        if not invitation:
            raise ValueError("Invitation not found")
        return _public_invitation(invitation)

    def accept_invitation(self, user_id: str, token: str) -> dict[str, Any]:
        invitation = self._invitation_for_token(token)
        if not invitation:
            raise ValueError("Invitation not found")
        if invitation.get("status") != "pending":
            raise ValueError("Invitation is not active")
        if _expired(invitation.get("expiresAt")):
            invitation["status"] = "expired"
            self.database.update(COMPANY_INVITATIONS_COLLECTION, invitation["id"], invitation)
            raise ValueError("Invitation expired")
        invitation["status"] = "accepted"
        invitation["acceptedAt"] = utc_now_iso()
        self.database.update(COMPANY_INVITATIONS_COLLECTION, invitation["id"], invitation)
        member = self._create_member(invitation["companyId"], user_id, invitation["role"], invitation["email"], status="active", access=invitation.get("access", {}))
        self._record_activity(user_id, "company_member_joined", "team", {"company_id": invitation["companyId"], "role": invitation["role"]})
        return {"invitation": _public_invitation(invitation), "member": _public_member(member)}

    def revoke_invitation(self, user_id: str, company_id: str, invitation_id: str) -> dict[str, Any]:
        self._require_permission(user_id, company_id, "members:manage")
        invitation = self.database.get(COMPANY_INVITATIONS_COLLECTION, invitation_id)
        if not invitation or invitation.get("companyId") != company_id:
            raise PermissionError("Invitation is outside this company")
        invitation["status"] = "revoked"
        invitation["revokedAt"] = utc_now_iso()
        self.database.update(COMPANY_INVITATIONS_COLLECTION, invitation_id, invitation)
        self._record_activity(user_id, "company_member_invitation_revoked", "team", {"company_id": company_id})
        return _public_invitation(invitation)

    def update_member(self, user_id: str, company_id: str, member_id: str, data: dict[str, Any]) -> dict[str, Any]:
        self._require_permission(user_id, company_id, "members:manage")
        member = self.database.get(COMPANY_MEMBERS_COLLECTION, member_id)
        if not member or member.get("companyId") != company_id:
            raise PermissionError("Member is outside this company")
        role = _trim(data.get("role") or member.get("role"), 40)
        if role not in EMPLOYER_ROLES:
            raise ValueError("Unsupported role")
        if member.get("role") == "company_owner" and role != "company_owner":
            raise ValueError("Transfer ownership before changing owner role")
        member["role"] = role
        member["status"] = _trim(data.get("status") or member.get("status") or "active", 40)
        member["access"] = data.get("access", member.get("access", {}))
        member["updatedAt"] = utc_now_iso()
        self.database.update(COMPANY_MEMBERS_COLLECTION, member_id, member)
        self._record_activity(user_id, "company_member_role_changed", "team", {"company_id": company_id, "role": role})
        return _public_member(member)

    def remove_member(self, user_id: str, company_id: str, member_id: str) -> dict[str, str]:
        self._require_permission(user_id, company_id, "members:manage")
        member = self.database.get(COMPANY_MEMBERS_COLLECTION, member_id)
        if not member or member.get("companyId") != company_id:
            raise PermissionError("Member is outside this company")
        if member.get("role") == "company_owner":
            raise ValueError("Transfer ownership before removing owner")
        member["status"] = "deactivated"
        member["updatedAt"] = utc_now_iso()
        self.database.update(COMPANY_MEMBERS_COLLECTION, member_id, member)
        self._record_activity(user_id, "company_member_removed", "team", {"company_id": company_id})
        return {"status": "deactivated"}

    def _validate_step(self, user_id: str, session: dict[str, Any], step: str, data: dict[str, Any]) -> dict[str, Any]:
        if step == "welcome":
            return {"accepted_entry": bool(data.get("accepted_entry", True))}
        if step == "employer_agent":
            return _normalize_agent(data)
        if step == "company_identity":
            return self._normalize_company_identity(user_id, session, data)
        if step == "company_verification":
            return self._normalize_company_verification(user_id, session, data)
        if step == "company_profile":
            return _normalize_company_profile(data)
        if step == "locations":
            return {"locations": [_normalize_location(session.get("company_id") or "draft", item) for item in _list_of_dicts(data.get("locations"))]}
        if step == "team":
            return {"invitations": [_normalize_invitation_preview(item) for item in _list_of_dicts(data.get("invitations"))]}
        if step == "hiring_needs":
            return _normalize_hiring_need(session.get("company_id") or "draft", data)
        if step == "hiring_process":
            return _normalize_hiring_process(data)
        if step == "integrations":
            return {"enabled": bool(data.get("enabled", False)), "systems": _string_list(data.get("systems"))}
        if step == "consents":
            return _normalize_consents(data)
        if step == "completion":
            return data
        raise ValueError(f"Unsupported employer onboarding step: {step}")

    def _apply_step_side_effects(self, user_id: str, session: dict[str, Any], step: str, normalized: dict[str, Any]) -> None:
        if step == "company_identity":
            if normalized.get("duplicate_detected"):
                return
            company = self._ensure_company(user_id, session, normalized)
            session["company_id"] = company["id"]
            session["membership_id"] = self._membership_for_user(user_id, company["id"])["id"]
        elif step == "company_verification" and normalized.get("documentFileIds"):
            company_id = self._ensure_session_company(user_id, session)
            verification = self.submit_verification(user_id, company_id, normalized)
            normalized["verificationId"] = verification["id"]
        elif step == "company_profile":
            company_id = self._ensure_session_company(user_id, session)
            company = self._company(company_id)
            if company:
                company["profile"] = normalized
                company["industry"] = normalized.get("industry") or company.get("industry")
                company["updated_at"] = utc_now_iso()
                self.database.update(COMPANY_COLLECTION, company_id, company)
        elif step == "locations":
            company_id = self._ensure_session_company(user_id, session)
            for item in normalized.get("locations", []):
                location = {**item, "companyId": company_id}
                if not self.database.get(COMPANY_LOCATIONS_COLLECTION, location["id"]):
                    self.database.insert(COMPANY_LOCATIONS_COLLECTION, location["id"], location)
        elif step == "team":
            company_id = self._ensure_session_company(user_id, session)
            for invitation in normalized.get("invitations", []):
                existing = [item for item in self._invitations(company_id) if item.get("email") == invitation.get("email") and item.get("status") == "pending"]
                if not existing and invitation.get("email"):
                    self.invite_member(user_id, company_id, invitation)
        elif step == "hiring_needs":
            company_id = self._ensure_session_company(user_id, session)
            hiring_need = {**normalized, "companyId": company_id, "id": normalized.get("id") if normalized.get("id", "").startswith("HRN-") else new_id("HRN")}
            existing = self._first_hiring_need(company_id)
            if existing:
                hiring_need["id"] = existing["id"]
                hiring_need["created_at"] = existing.get("created_at")
                hiring_need["updated_at"] = utc_now_iso()
                self.database.update(HIRING_NEEDS_COLLECTION, hiring_need["id"], hiring_need)
            else:
                self.database.insert(HIRING_NEEDS_COLLECTION, hiring_need["id"], hiring_need)
                self._record_activity(user_id, "hiring_need_created", "hiring_needs", {"company_id": company_id})
        elif step == "hiring_process":
            company_id = self._ensure_session_company(user_id, session)
            process = {**normalized, "id": f"PIPE-{company_id}", "companyId": company_id, "updated_at": utc_now_iso()}
            self.database.update(HIRING_PROCESS_COLLECTION, process["id"], process)
            self._record_activity(user_id, "hiring_process_updated", "hiring_process", {"company_id": company_id})
        elif step == "consents":
            company_id = self._ensure_session_company(user_id, session)
            for key, granted in normalized.get("required", {}).items():
                self._save_consent(user_id, company_id, key, bool(granted), "required")
            for key, granted in normalized.get("optional", {}).items():
                self._save_consent(user_id, company_id, key, bool(granted), "optional")

    def _normalize_company_identity(self, user_id: str, session: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
        mode = _trim(data.get("mode") or data.get("identity_mode") or data.get("action") or "create_company", 40)
        if mode not in {"create_company", "join_existing_company"}:
            raise ValueError("Unsupported company identity mode")
        if mode == "join_existing_company":
            token = _trim(data.get("invitation_token") or data.get("token"), 200)
            if token:
                accepted = self.accept_invitation(user_id, token)
                session["company_id"] = accepted["member"]["companyId"]
                session["membership_id"] = accepted["member"]["id"]
                return {"mode": mode, "join_status": "accepted_invitation", "company_id": accepted["member"]["companyId"]}
            return {"mode": mode, "join_status": "manual_review_requested", "domain": _domain(data.get("corporate_domain"))}
        if not any(data.get(key) for key in ("legal_name", "company_name", "companyName")) and session.get("data", {}).get("company_identity"):
            existing = dict(session["data"]["company_identity"])
            existing.update({key: value for key, value in data.items() if value not in {None, ""}})
            data = existing
        legal_name = _trim(data.get("legal_name") or data.get("company_name") or data.get("companyName"), 180)
        if not legal_name:
            raise ValueError("legal_name is required")
        normalized = {
            "mode": mode,
            "legal_name": legal_name,
            "trading_name": _trim(data.get("trading_name") or data.get("tradingName") or legal_name, 180),
            "country_code": _trim(data.get("country_code") or data.get("countryCode") or "GLOBAL", 8).upper(),
            "registration_number": _trim(data.get("registration_number") or data.get("registrationNumber"), 80),
            "tax_number": _trim(data.get("tax_number") or data.get("vat_number") or data.get("nip"), 80),
            "ownership_form": _trim(data.get("ownership_form"), 80),
            "registration_date": _trim(data.get("registration_date"), 40),
            "official_email": _trim(data.get("official_email") or data.get("contact_email") or data.get("email"), 180).lower(),
            "phone": _trim(data.get("phone") or data.get("contact_phone"), 40),
            "website": _trim(data.get("website"), 220),
            "legal_address": _trim(data.get("legal_address") or data.get("address"), 260),
            "industry": _trim(data.get("industry") or "general", 120),
        }
        duplicate = self._duplicate_company(normalized)
        if duplicate and duplicate.get("owner_user_id") != user_id:
            return {**normalized, "duplicate_detected": True, "safe_join_required": True, "duplicate_hint": _safe_company_hint(duplicate)}
        return normalized

    def _normalize_company_verification(self, user_id: str, session: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
        file_ids = _string_list(data.get("documentFileIds") or data.get("document_file_ids") or [item.get("id") for item in _list_of_dicts(data.get("files"))])
        for file_data in _list_of_dicts(data.get("files")):
            self._ensure_document_record(user_id, file_data, session.get("company_id"))
        if file_ids:
            self._assert_files_owned(user_id, file_ids)
        return {"verificationType": _trim(data.get("verificationType") or "manual_document_review", 80), "documentFileIds": file_ids, "registryReference": _trim(data.get("registryReference"), 120)}

    def _ensure_company(self, user_id: str, session: dict[str, Any], identity: dict[str, Any]) -> dict[str, Any]:
        if session.get("company_id") and self._company(session["company_id"]):
            company = self._company(session["company_id"])
            if company:
                return company
        if identity.get("mode") == "join_existing_company" and identity.get("company_id"):
            company = self._company(identity["company_id"])
            if not company:
                raise ValueError("Company not found")
            return company
        if identity.get("duplicate_detected"):
            raise ValueError("Possible duplicate company found. Use join request or administrator approval.")
        company = {
            "id": new_id("CMP"),
            "owner_user_id": user_id,
            "legal_name": identity.get("legal_name") or identity.get("company_name"),
            "trading_name": identity.get("trading_name") or identity.get("legal_name") or identity.get("company_name"),
            "country_code": identity.get("country_code") or "GLOBAL",
            "registration_number": identity.get("registration_number", ""),
            "tax_number": identity.get("tax_number", ""),
            "ownership_form": identity.get("ownership_form", ""),
            "registration_date": identity.get("registration_date", ""),
            "official_email": identity.get("official_email", ""),
            "phone": identity.get("phone", ""),
            "website": identity.get("website", ""),
            "domain": _domain(identity.get("website") or identity.get("official_email")),
            "legal_address": identity.get("legal_address", ""),
            "industry": identity.get("industry", "general"),
            "profile": {},
            "verification_status": "unverified",
            "data_protection_roles": {"atlas": "processor", "company": "controller", "purposes": ["candidate_matching", "candidate_communication", "recruitment_management", "document_verification"]},
            "created_at": utc_now_iso(),
            "updated_at": utc_now_iso(),
        }
        self.database.insert(COMPANY_COLLECTION, company["id"], company)
        member = self._create_member(company["id"], user_id, "company_owner", identity.get("official_email", ""), status="active")
        session["membership_id"] = member["id"]
        self._record_activity(user_id, "company_created", "company_identity", {"company_id": company["id"]})
        return company

    def _completion_errors(self, user_id: str, session: dict[str, Any]) -> list[str]:
        data = session.get("data", {})
        missing = [step for step in ["company_identity", "consents"] if step not in session.get("completed_steps", []) or not data.get(step)]
        if not (session.get("company_id") or data.get("company_identity")):
            missing.append("company")
        errors = [f"Incomplete employer onboarding steps: {', '.join(sorted(set(missing)))}"] if missing else []
        company_id = session.get("company_id")
        membership = self._membership_for_user(user_id, company_id) if company_id else None
        if not membership:
            errors.append("Company membership is missing")
        consents = _normalize_consents(data.get("consents", {}))
        missing_consents = [key for key in REQUIRED_CONSENTS if not consents["required"].get(key)]
        if missing_consents:
            errors.append("Required employer consents are missing")
        return errors

    def _upsert_employer(self, user_id: str, session: dict[str, Any], company: dict[str, Any]) -> Employer:
        existing = self._employer_for_session(session)
        contact = session.get("data", {}).get("company_identity", {})
        metadata = {
            **(existing.metadata if existing else {}),
            "source": "employer_onboarding",
            "owner_user_id": user_id,
            "company_id": company["id"],
            "onboarding_completed_at": utc_now_iso(),
        }
        if existing:
            existing.company_name = company["trading_name"] or company["legal_name"]
            existing.contact_email = company.get("official_email") or contact.get("official_email") or existing.contact_email
            existing.contact_phone = company.get("phone") or existing.contact_phone
            existing.country_code = company.get("country_code", "GLOBAL")
            existing.industry = company.get("industry", "general")
            existing.verified = company.get("verification_status") == "verified"
            existing.metadata = metadata
            return self.employers.update(existing)
        return self.employers.add(
            Employer(
                company_name=company["trading_name"] or company["legal_name"],
                contact_email=company.get("official_email") or f"{user_id}@atlas.local",
                contact_phone=company.get("phone", ""),
                country_code=company.get("country_code", "GLOBAL"),
                industry=company.get("industry", "general"),
                verified=False,
                metadata=metadata,
            )
        )

    def _ensure_document_record(self, user_id: str, file_data: dict[str, Any], company_id: str | None = None) -> None:
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
                metadata={"company_id": company_id, "employer_onboarding_file_id": file_data["id"], "original_name": file_data.get("original_name")},
            )
        )

    def _assert_files_owned(self, user_id: str, file_ids: list[str]) -> None:
        owned = {item.metadata.get("employer_onboarding_file_id") for item in self.documents.list() if item.owner_id == user_id}
        missing = [file_id for file_id in file_ids if file_id not in owned]
        if missing:
            raise PermissionError("Verification file ownership check failed")

    def _require_permission(self, user_id: str, company_id: str, permission: str) -> dict[str, Any]:
        member = self._membership_for_user(user_id, company_id)
        if not member or member.get("status") != "active":
            raise PermissionError("No active membership for company")
        if permission not in ROLE_PERMISSIONS.get(member.get("role"), set()) and "company:write" not in ROLE_PERMISSIONS.get(member.get("role"), set()):
            raise PermissionError("Insufficient company permission")
        return member

    def _create_member(self, company_id: str, user_id: str, role: str, email: str = "", status: str = "active", access: dict[str, Any] | None = None) -> dict[str, Any]:
        existing = self._membership_for_user(user_id, company_id)
        if existing:
            return existing
        member = {"id": new_id("MBR"), "companyId": company_id, "userId": user_id, "email": email, "role": role, "status": status, "access": access or {}, "createdAt": utc_now_iso(), "updatedAt": utc_now_iso()}
        self.database.insert(COMPANY_MEMBERS_COLLECTION, member["id"], member)
        return member

    def _save_consent(self, user_id: str, company_id: str, key: str, granted: bool, consent_type: str) -> None:
        record_id = f"ECON-{company_id}-{key}"
        record = {"id": record_id, "companyId": company_id, "key": key, "type": consent_type, "granted": granted, "grantedBy": user_id, "role": self._membership_for_user(user_id, company_id).get("role"), "policyVersion": "2026-07", "timestamp": utc_now_iso()}
        self.database.update(EMPLOYER_CONSENTS_COLLECTION, record_id, record)
        self._record_activity(user_id, "employer_consent_changed", "consents", {"company_id": company_id, "key": key, "granted": granted})

    def _record_activity(self, user_id: str, action: str, step: str, metadata: dict[str, Any] | None = None) -> None:
        self.activity.add(ActivityEvent(entity_type="employer_company", entity_id=user_id, action=action, old_value=None, new_value=step, note=f"Employer {step}", actor_id=user_id, metadata=metadata or {}))

    def _company(self, company_id: str | None) -> dict[str, Any] | None:
        return self.database.get(COMPANY_COLLECTION, company_id) if company_id else None

    def _company_for_session(self, session: dict[str, Any]) -> dict[str, Any] | None:
        if session.get("company_id"):
            return self._company(session["company_id"])
        user_id = session.get("user_id")
        for member in self.database.list(COMPANY_MEMBERS_COLLECTION):
            if member.get("userId") == user_id and member.get("status") == "active":
                return self._company(member.get("companyId"))
        return None

    def _ensure_session_company(self, user_id: str, session: dict[str, Any]) -> str:
        company = self._company_for_session(session)
        if not company:
            identity = session.get("data", {}).get("company_identity") or {}
            company = self._ensure_company(user_id, session, identity)
            session["company_id"] = company["id"]
        return company["id"]

    def _duplicate_company(self, identity: dict[str, Any]) -> dict[str, Any] | None:
        identity_domain = _domain(identity.get("website") or identity.get("official_email"))
        for company in self.database.list(COMPANY_COLLECTION):
            if identity.get("country_code") and company.get("country_code") != identity.get("country_code"):
                continue
            if identity.get("registration_number") and company.get("registration_number") == identity.get("registration_number"):
                return company
            if identity.get("tax_number") and company.get("tax_number") == identity.get("tax_number"):
                return company
            if identity_domain and company.get("domain") == identity_domain:
                return company
            if _norm(company.get("legal_name")) and _norm(company.get("legal_name")) == _norm(identity.get("legal_name")):
                return company
        return None

    def _membership_for_user(self, user_id: str, company_id: str | None) -> dict[str, Any] | None:
        if not company_id:
            return None
        for member in self.database.list(COMPANY_MEMBERS_COLLECTION):
            if member.get("companyId") == company_id and member.get("userId") == user_id:
                return member
        return None

    def _members(self, company_id: str | None) -> list[dict[str, Any]]:
        return [item for item in self.database.list(COMPANY_MEMBERS_COLLECTION) if item.get("companyId") == company_id] if company_id else []

    def _invitations(self, company_id: str | None) -> list[dict[str, Any]]:
        return [item for item in self.database.list(COMPANY_INVITATIONS_COLLECTION) if item.get("companyId") == company_id] if company_id else []

    def _invitation_for_token(self, token: str) -> dict[str, Any] | None:
        token_hash = _hash_token(token)
        for invitation in self.database.list(COMPANY_INVITATIONS_COLLECTION):
            if invitation.get("tokenHash") == token_hash:
                return invitation
        return None

    def _latest_verification(self, company_id: str | None) -> dict[str, Any] | None:
        items = [item for item in self.database.list(COMPANY_VERIFICATIONS_COLLECTION) if item.get("companyId") == company_id] if company_id else []
        return sorted(items, key=lambda item: item.get("submittedAt", ""), reverse=True)[0] if items else None

    def _locations(self, company_id: str | None) -> list[dict[str, Any]]:
        return [item for item in self.database.list(COMPANY_LOCATIONS_COLLECTION) if item.get("companyId") == company_id and item.get("active", True)] if company_id else []

    def _hiring_needs(self, company_id: str | None) -> list[dict[str, Any]]:
        return [item for item in self.database.list(HIRING_NEEDS_COLLECTION) if item.get("companyId") == company_id] if company_id else []

    def _first_hiring_need(self, company_id: str) -> dict[str, Any] | None:
        items = self._hiring_needs(company_id)
        return items[0] if items else None

    def _company_documents(self, company_id: str | None, user_id: str) -> list[dict[str, Any]]:
        return [item.to_dict() for item in self.documents.list() if item.owner_id == user_id and (not company_id or item.metadata.get("company_id") in {company_id, None}) and item.metadata.get("employer_onboarding_file_id")]

    def _consent_summary(self, company_id: str | None) -> dict[str, Any]:
        records = [item for item in self.database.list(EMPLOYER_CONSENTS_COLLECTION) if item.get("companyId") == company_id] if company_id else []
        granted = {item["key"]: item.get("granted") for item in records}
        return {"requiredComplete": all(granted.get(key) for key in REQUIRED_CONSENTS), "aiMatchingEnabled": bool(granted.get("aiMatching")), "records": records}

    def _employer_for_session(self, session: dict[str, Any]) -> Employer | None:
        if session.get("employer_id"):
            return self.employers.get(session["employer_id"])
        company_id = session.get("company_id")
        for employer in self.employers.list():
            if employer.metadata.get("company_id") == company_id or employer.metadata.get("owner_user_id") == session.get("user_id"):
                return employer
        return None


def _canonical_step(step: str | None) -> str:
    aliases = {"company": "company_identity", "contact": "company_identity", "documents": "company_verification", "completed": "completion"}
    return aliases.get(str(step or "").strip(), str(step or "").strip())


def _legacy_step_key(step: str) -> str:
    return {"company_identity": "company", "company_verification": "documents", "completion": "completed"}.get(step, step)


def _normalize_agent(data: dict[str, Any]) -> dict[str, Any]:
    capabilities = _string_list(data.get("enabled_capabilities") or data.get("enabledCapabilities") or data.get("tasks"))
    return {
        "name": _trim(data.get("name") or "ATLAS Employer Agent", 80),
        "language": _trim(data.get("language") or "en", 8),
        "tone": _trim(data.get("tone") or "professional", 40),
        "autonomy_level": min(3, max(0, _safe_int(data.get("autonomy_level") or data.get("autonomyLevel"), 1))),
        "enabled_capabilities": capabilities,
        "guardrails": {
            "cannot_reject_without_rule": True,
            "cannot_send_offer": True,
            "cannot_change_salary": True,
            "cannot_export_data": True,
            "cannot_delete_candidate": True,
        },
    }


def _normalize_company_profile(data: dict[str, Any]) -> dict[str, Any]:
    return {
        "short_description": _trim(data.get("short_description") or data.get("shortDescription"), 500),
        "long_description": _trim(data.get("long_description") or data.get("longDescription"), 3000),
        "industry": _trim(data.get("industry") or "general", 120),
        "subindustry": _trim(data.get("subindustry"), 120),
        "company_size": _trim(data.get("company_size") or data.get("companySize"), 40),
        "employee_count": max(0, _safe_int(data.get("employee_count") or data.get("employeeCount"), 0)),
        "founded_year": max(0, _safe_int(data.get("founded_year") or data.get("foundedYear"), 0)),
        "employer_type": _trim(data.get("employer_type") or data.get("employerType"), 80),
        "communication_languages": _string_list(data.get("communication_languages") or data.get("communicationLanguages")),
        "operation_countries": _string_list(data.get("operation_countries") or data.get("operationCountries")),
        "website": _trim(data.get("website"), 220),
        "social_links": _list_of_dicts(data.get("social_links") or data.get("socialLinks")),
        "logo_file_id": _trim(data.get("logo_file_id") or data.get("logoFileId"), 80),
        "cover_file_id": _trim(data.get("cover_file_id") or data.get("coverFileId"), 80),
        "benefits": _string_list(data.get("benefits")),
        "work_environment": _trim(data.get("work_environment") or data.get("workEnvironment"), 1000),
        "culture": _trim(data.get("culture"), 1000),
        "value_proposition": _trim(data.get("value_proposition") or data.get("valueProposition"), 1000),
        "employment_types": _string_list(data.get("employment_types") or data.get("employmentTypes")),
        "foreigner_support": bool(data.get("foreigner_support") or data.get("foreignerSupport")),
        "housing": bool(data.get("housing")),
        "transport": bool(data.get("transport")),
        "legalization": bool(data.get("legalization")),
        "training": bool(data.get("training")),
        "insurance": bool(data.get("insurance")),
    }


def _normalize_location(company_id: str, data: dict[str, Any], location_id: str | None = None) -> dict[str, Any]:
    city = _trim(data.get("city"), 120)
    country = _trim(data.get("country") or data.get("country_code") or data.get("countryCode"), 8).upper()
    if not city or not country:
        raise ValueError("Location country and city are required")
    return {
        "id": location_id or data.get("id") or new_id("LOC"),
        "companyId": company_id,
        "type": _trim(data.get("type") or "office", 40),
        "country": country,
        "region": _trim(data.get("region"), 120),
        "city": city,
        "address": _trim(data.get("address"), 220),
        "postalCode": _trim(data.get("postalCode") or data.get("postal_code"), 30),
        "latitude": _safe_float(data.get("latitude")),
        "longitude": _safe_float(data.get("longitude")),
        "active": bool(data.get("active", True)),
        "publicAddress": bool(data.get("publicAddress", False)),
        "created_at": data.get("created_at") or utc_now_iso(),
        "updated_at": utc_now_iso(),
    }


def _normalize_invitation_preview(data: dict[str, Any]) -> dict[str, Any]:
    return {"email": _trim(data.get("email"), 180).lower(), "role": _trim(data.get("role") or "recruiter", 40), "vacancyIds": _string_list(data.get("vacancyIds"))}


def _normalize_hiring_need(company_id: str, data: dict[str, Any]) -> dict[str, Any]:
    profession = _trim(data.get("professionLabel") or data.get("profession") or data.get("role"), 160)
    if not profession:
        raise ValueError("profession is required")
    quantity = _safe_int(data.get("quantity"), 1)
    if quantity < 1:
        raise ValueError("quantity must be greater than zero")
    salary_min = _safe_float(data.get("salary_min") or data.get("salaryMinimum") or data.get("minimum"))
    salary_max = _safe_float(data.get("salary_max") or data.get("salaryMaximum") or data.get("maximum"))
    if salary_min and salary_max and salary_min > salary_max:
        raise ValueError("salary minimum cannot exceed maximum")
    return {
        "id": _trim(data.get("id"), 80),
        "companyId": company_id,
        "professionKey": _trim(data.get("professionKey") or profession.lower().replace(" ", "_"), 80),
        "professionLabel": profession,
        "quantity": quantity,
        "locationIds": _string_list(data.get("locationIds") or data.get("locations")),
        "urgency": _trim(data.get("urgency") or "medium", 20),
        "targetStartDate": _trim(data.get("targetStartDate") or data.get("start_date"), 40),
        "employmentTypes": _string_list(data.get("employmentTypes") or data.get("contract_type")),
        "schedule": data.get("schedule") if isinstance(data.get("schedule"), dict) else {"text": _trim(data.get("schedule"), 160)},
        "salary": {"minimum": salary_min, "maximum": salary_max, "currency": _trim(data.get("currency") or "PLN", 8), "period": _trim(data.get("period") or "month", 20), "grossNet": _trim(data.get("grossNet") or "unknown", 20)},
        "languageRequirements": _list_of_dicts(data.get("languageRequirements") or data.get("languages")),
        "skillRequirements": _list_of_dicts(data.get("skillRequirements") or data.get("skills")),
        "credentialRequirements": _list_of_dicts(data.get("credentialRequirements") or data.get("certificates")),
        "housingProvided": bool(data.get("housingProvided") or data.get("housing")),
        "transportProvided": bool(data.get("transportProvided") or data.get("transport")),
        "legalizationSupport": bool(data.get("legalizationSupport") or data.get("legalization")),
        "status": _trim(data.get("status") or "draft", 20),
        "created_at": data.get("created_at") or utc_now_iso(),
        "updated_at": utc_now_iso(),
    }


def _normalize_hiring_process(data: dict[str, Any]) -> dict[str, Any]:
    raw_stages = _list_of_dicts(data.get("stages"))
    if not raw_stages:
        raw_stages = [{"key": key, "label": key.replace("_", " ").title(), "enabled": True, "order": index} for index, key in enumerate(DEFAULT_PIPELINE)]
    stages = []
    keys = set()
    for index, item in enumerate(raw_stages):
        key = _trim(item.get("key") or item.get("id") or item.get("label"), 60).lower().replace(" ", "_")
        if not key:
            continue
        keys.add(key)
        stages.append({"key": key, "label": _trim(item.get("label") or key.replace("_", " ").title(), 80), "enabled": bool(item.get("enabled", True) or key in FINAL_PIPELINE_STAGES), "order": _safe_int(item.get("order"), index), "responsibleRole": _trim(item.get("responsibleRole") or "hr_manager", 40), "slaHours": max(0, _safe_int(item.get("slaHours"), 0)), "requiredFields": _string_list(item.get("requiredFields"))})
    missing_final = FINAL_PIPELINE_STAGES - keys
    if missing_final:
        raise ValueError(f"Final pipeline stages cannot be removed: {', '.join(sorted(missing_final))}")
    return {"stages": sorted(stages, key=lambda item: item["order"]), "guardRules": ["offer_requires_salary", "hired_requires_decision_confirmation", "rejected_requires_reason", "ai_recommendation_is_not_final_decision"]}


def _normalize_consents(data: dict[str, Any]) -> dict[str, Any]:
    required_source = data.get("required") if isinstance(data.get("required"), dict) else data
    optional_source = data.get("optional") if isinstance(data.get("optional"), dict) else data
    required = {
        "termsForBusiness": bool(required_source.get("termsForBusiness") or required_source.get("terms")),
        "dataProcessing": bool(required_source.get("dataProcessing") or required_source.get("privacy") or required_source.get("businessProcessing")),
        "representativeAuthority": bool(required_source.get("representativeAuthority") or required_source.get("authority")),
        "lawfulCandidateUse": bool(required_source.get("lawfulCandidateUse") or required_source.get("candidateData")),
        "nonDiscrimination": bool(required_source.get("nonDiscrimination")),
    }
    optional = {
        "aiMatching": bool(optional_source.get("aiMatching") or optional_source.get("matching")),
        "aiRanking": bool(optional_source.get("aiRanking")),
        "aiGeneratedVacancyContent": bool(optional_source.get("aiGeneratedVacancyContent")),
        "analytics": bool(optional_source.get("analytics")),
        "marketing": bool(optional_source.get("marketing")),
        "externalIntegrations": bool(optional_source.get("externalIntegrations")),
    }
    return {"required": required, "optional": optional, "policyVersion": _trim(data.get("policyVersion") or "2026-07", 20)}


def _readiness(company: dict[str, Any] | None, verification: dict[str, Any] | None, hiring_needs: list[dict[str, Any]], members: list[dict[str, Any]], consents: dict[str, Any], documents: list[dict[str, Any]]) -> dict[str, Any]:
    score = 0
    if company:
        score += COMPLETENESS_WEIGHTS["identity"]
    if verification and verification.get("status") in {"pending", "partially_verified", "verified"}:
        score += COMPLETENESS_WEIGHTS["verification"] if verification.get("status") == "verified" else 10
    if company and company.get("profile"):
        score += COMPLETENESS_WEIGHTS["profile"]
    if company:
        # Locations/team are optional for completion, but still count toward company completeness.
        score += COMPLETENESS_WEIGHTS["locations"] if company else 0
    if members:
        score += COMPLETENESS_WEIGHTS["team"]
    if hiring_needs:
        score += COMPLETENESS_WEIGHTS["hiring_needs"]
    score += COMPLETENESS_WEIGHTS["hiring_process"] if company else 0
    if consents.get("requiredComplete"):
        score += COMPLETENESS_WEIGHTS["consents"]
    return {
        "companyProfileStatus": "complete" if company else "incomplete",
        "verificationStatus": (verification or {}).get("status") or (company or {}).get("verification_status") or "unverified",
        "documentsStatus": "uploaded" if documents else "missing",
        "hiringNeedsStatus": "complete" if hiring_needs else "incomplete",
        "businessProcessingConsent": "enabled" if consents.get("requiredComplete") else "disabled",
        "profileCompleteness": min(100, score),
    }


def _actions(session: dict[str, Any], readiness: dict[str, Any]) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    if readiness["verificationStatus"] in {"unverified", "rejected"}:
        actions.append({"id": "submit_verification", "title": "Submit company verification", "description": "Upload corporate documents for ATLAS review.", "priority": "high", "route": "/employer/onboarding?step=company_verification"})
    if readiness["hiringNeedsStatus"] != "complete":
        actions.append({"id": "complete_hiring_needs", "title": "Define hiring needs", "description": "Add real role, quantity, location and salary data.", "priority": "high", "route": "/employer/onboarding?step=hiring_needs"})
    if readiness["businessProcessingConsent"] != "enabled":
        actions.append({"id": "accept_consents", "title": "Complete business consents", "description": "Required before using candidate data.", "priority": "high", "route": "/employer/onboarding?step=consents"})
    if readiness["profileCompleteness"] < 75:
        actions.append({"id": "complete_company_profile", "title": "Improve company profile", "description": "Add benefits, support and company description.", "priority": "medium", "route": "/employer/onboarding?step=company_profile"})
    return actions[:5]


def _dashboard_company(company: dict[str, Any] | None, completeness: int) -> dict[str, Any]:
    return {
        "id": company.get("id"),
        "legalName": company.get("legal_name", ""),
        "tradingName": company.get("trading_name", ""),
        "logoUrl": company.get("profile", {}).get("logo_file_id", ""),
        "verificationStatus": company.get("verification_status", "unverified"),
        "profileCompleteness": completeness,
        "industry": company.get("industry", ""),
    }


def _draft_company(session: dict[str, Any]) -> dict[str, Any]:
    identity = session.get("data", {}).get("company_identity") or session.get("data", {}).get("company") or {}
    return {"id": None, "legalName": identity.get("legal_name") or identity.get("company_name", ""), "tradingName": identity.get("trading_name", ""), "verificationStatus": "unverified", "profileCompleteness": 0}


def _draft_employer(session: dict[str, Any]) -> dict[str, Any]:
    identity = session.get("data", {}).get("company_identity") or session.get("data", {}).get("company") or {}
    return {"company_name": identity.get("trading_name") or identity.get("legal_name") or identity.get("company_name", ""), "contact_email": identity.get("official_email", ""), "contact_phone": identity.get("phone", ""), "country_code": identity.get("country_code", ""), "industry": identity.get("industry", ""), "verified": False, "metadata": {"source": "employer_onboarding_draft"}}


def _membership_payload(member: dict[str, Any] | None) -> dict[str, Any]:
    role = member.get("role") if member else "viewer"
    return {"id": member.get("id") if member else None, "role": role, "permissions": sorted(ROLE_PERMISSIONS.get(role, {"company:read"}))}


def _hiring_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    active = [item for item in items if item.get("status") in {"draft", "active"}]
    return {"active": len([item for item in items if item.get("status") == "active"]), "critical": len([item for item in items if item.get("urgency") == "critical"]), "totalOpenings": sum(_safe_int(item.get("quantity"), 0) for item in active), "items": items}


def _activity(events: list[ActivityEvent], user_id: str, company_id: str | None) -> list[dict[str, Any]]:
    filtered = [event for event in events if event.actor_id == user_id or (company_id and event.metadata.get("company_id") == company_id)]
    return [{"id": item.id, "type": item.action, "title": item.action.replace("_", " ").title(), "createdAt": item.created_at, "source": item.new_value or ""} for item in sorted(filtered, key=lambda event: event.created_at, reverse=True)[:10]]


def _with_progress(session: dict[str, Any]) -> dict[str, Any]:
    clean = dict(session)
    total = len(EMPLOYER_STEPS)
    done = len([step for step in clean.get("completed_steps", []) if step in EMPLOYER_STEPS])
    clean["steps"] = EMPLOYER_STEPS
    clean["progress"] = {"completed": done, "total": total, "percent": round((done / total) * 100) if total else 0}
    return clean


def _next_step(step: str) -> str:
    index = EMPLOYER_STEPS.index(step)
    return EMPLOYER_STEPS[min(index + 1, len(EMPLOYER_STEPS) - 1)]


def _audit(action: str, step: str, actor_id: str = "system") -> dict[str, str]:
    return {"action": action, "step": step, "actor_id": actor_id, "timestamp": utc_now_iso()}


def _trim(value: Any, max_length: int = 200) -> str:
    return str(value or "").strip()[:max_length]


def _valid_email(value: str) -> bool:
    return bool(value and "@" in value and "." in value.rsplit("@", 1)[-1])


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
        return [_trim(item, 120) for item in value if _trim(item, 120)]
    if isinstance(value, str):
        return [_trim(item, 120) for item in value.split(",") if _trim(item, 120)]
    return []


def _list_of_dicts(value: Any) -> list[dict[str, Any]]:
    return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []


def _domain(value: Any) -> str:
    text = _trim(value, 220).lower().replace("https://", "").replace("http://", "").replace("www.", "")
    if "@" in text:
        text = text.rsplit("@", 1)[-1]
    return text.split("/", 1)[0]


def _norm(value: Any) -> str:
    return "".join(char for char in _trim(value, 240).lower() if char.isalnum())


def _safe_company_hint(company: dict[str, Any]) -> dict[str, str]:
    return {"country_code": company.get("country_code", ""), "domain": company.get("domain", ""), "name_hint": (company.get("legal_name", "")[:2] + "***") if company.get("legal_name") else ""}


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _expired(value: str | None) -> bool:
    if not value:
        return True
    try:
        return datetime.fromisoformat(value) < datetime.now(timezone.utc)
    except ValueError:
        return True


def _public_invitation(invitation: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in invitation.items() if key != "tokenHash"}


def _public_member(member: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in member.items() if key in {"id", "companyId", "userId", "email", "role", "status", "access", "createdAt", "updatedAt"}}
