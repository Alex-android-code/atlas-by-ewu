"""RODO/GDPR foundation service for consent and data-subject requests."""

from __future__ import annotations

import hashlib
from typing import Any

from core.models import ConsentRecord, DataSubjectRequest, utc_now_iso
from database.repositories import (
    CandidateRepository,
    ConsentRepository,
    DataSubjectRequestRepository,
    EmployerRepository,
    UserRepository,
)


PRIVACY_NOTICE_VERSION = "2026-07-18.v1"
DEFAULT_CONSENT_SCOPES = [
    "profile_storage",
    "contact_follow_up",
    "job_matching",
    "ai_assistance",
    "operations_crm",
]
DATA_SUBJECT_REQUEST_TYPES = {"export", "delete", "rectify", "restrict_processing"}
DATA_SUBJECT_REQUEST_STATUSES = {"pending", "verified", "completed", "rejected"}


class RodoService:
    def __init__(
        self,
        consents: ConsentRepository,
        data_subject_requests: DataSubjectRequestRepository,
        candidates: CandidateRepository,
        employers: EmployerRepository,
        users: UserRepository,
    ) -> None:
        self.consents = consents
        self.data_subject_requests = data_subject_requests
        self.candidates = candidates
        self.employers = employers
        self.users = users

    def privacy_notice(self, language: str = "uk") -> dict[str, Any]:
        return {
            "version": PRIVACY_NOTICE_VERSION,
            "language": language,
            "controller": "European Welding Union / ATLAS",
            "purposes": [
                "candidate and employer profile handling",
                "job matching and coordinator operations",
                "AI-assisted profile analysis and communication support",
                "legal, security, and audit obligations",
            ],
            "processors": ["Render", "Telegram", "Google Apps Script / Google Sheets", "Gemini / Google AI"],
            "rights": ["access", "export", "rectification", "deletion", "restriction", "objection"],
            "retention": "Retention periods are operational and must be finalized before enterprise rollout.",
            "contact": "Use the ATLAS/EWU official contact channel to submit privacy requests.",
        }

    def record_consent(
        self,
        subject_id: str,
        language: str,
        source: str,
        scopes: list[str] | None = None,
        accepted: bool = True,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> ConsentRecord:
        consent = ConsentRecord(
            subject_id=subject_id,
            consent_version=PRIVACY_NOTICE_VERSION,
            language=language,
            source=source,
            scopes=scopes or DEFAULT_CONSENT_SCOPES,
            accepted=accepted,
            revoked_at=None if accepted else utc_now_iso(),
            metadata={
                "ip_hash": _hash_value(ip_address),
                "user_agent": user_agent or "",
            },
        )
        return self.consents.add(consent)

    def create_data_subject_request(
        self,
        subject_id: str,
        request_type: str,
        contact: str,
        language: str = "uk",
        note: str = "",
    ) -> DataSubjectRequest:
        normalized_type = request_type.strip().lower()
        if normalized_type not in DATA_SUBJECT_REQUEST_TYPES:
            raise ValueError(f"Unsupported RODO request type: {request_type}")
        request = DataSubjectRequest(
            subject_id=subject_id,
            request_type=normalized_type,
            contact=contact,
            metadata={"language": language, "note": note},
        )
        return self.data_subject_requests.add(request)

    def list_data_subject_requests(self) -> list[DataSubjectRequest]:
        return self.data_subject_requests.list()

    def update_data_subject_request_status(self, request_id: str, status: str, note: str = "") -> DataSubjectRequest:
        normalized_status = status.strip().lower()
        if normalized_status not in DATA_SUBJECT_REQUEST_STATUSES:
            raise ValueError(f"Unsupported RODO request status: {status}")
        request = self.data_subject_requests.get(request_id)
        if request is None:
            raise ValueError(f"RODO request not found: {request_id}")
        request.status = normalized_status
        if normalized_status == "completed":
            request.completed_at = utc_now_iso()
        if note:
            request.metadata["admin_note"] = note
        return self.data_subject_requests.update(request)

    def export_subject_data(self, subject_id: str) -> dict[str, Any]:
        return {
            "subject_id": subject_id,
            "exported_at": utc_now_iso(),
            "consents": [item.to_dict() for item in self.consents.list() if item.subject_id == subject_id],
            "data_subject_requests": [
                item.to_dict() for item in self.data_subject_requests.list() if item.subject_id == subject_id
            ],
            "users": [item.to_dict() for item in self.users.list() if item.id == subject_id],
            "candidates": [
                item.to_dict()
                for item in self.candidates.list()
                if item.user_id == subject_id or item.email == subject_id or item.phone == subject_id
            ],
            "employers": [
                item.to_dict()
                for item in self.employers.list()
                if item.id == subject_id or item.contact_email == subject_id or item.contact_phone == subject_id
            ],
        }


def _hash_value(value: str | None) -> str:
    if not value:
        return ""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()
