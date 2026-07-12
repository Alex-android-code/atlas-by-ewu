"""CRM service for the first EWU operational engine."""

from datetime import datetime, timezone
from typing import Any

from agents.matching_agent import MatchingAgent
from core.user_profile import CandidateProfile, VacancyProfile
from database.repositories import (
    ActivityRepository,
    CandidateRepository,
    DocumentRepository,
    EmployerRepository,
    MatchRepository,
    VacancyRepository,
)
from memory.memory_store import MemoryStore
from core.models import ActivityEvent, Candidate, Document, Employer, Match, Vacancy
from services.analytics import analytics_summary, record_event
from services.demo_data import is_demo_record
from services.vacancy_control import (
    PUBLISHABLE_STATUSES,
    REJECTION_REASONS,
    VACANCY_STATUSES,
    first_vacancies_report,
    prepare_new_vacancy,
)


class CrmService:
    def __init__(
        self,
        candidates: CandidateRepository,
        employers: EmployerRepository,
        vacancies: VacancyRepository,
        matches: MatchRepository,
        documents: DocumentRepository,
        activity: ActivityRepository,
        memory_store: MemoryStore,
    ) -> None:
        self.candidates = candidates
        self.employers = employers
        self.vacancies = vacancies
        self.matches = matches
        self.documents = documents
        self.activity = activity
        self.matching_agent = MatchingAgent(memory_store)

    def create_candidate(self, candidate: Candidate) -> Candidate:
        candidate.status = candidate.status or "new"
        return self.candidates.add(candidate)

    def create_employer(self, employer: Employer) -> Employer:
        existing = self.find_existing_employer(employer)
        request_log = employer.metadata.get("request_log", {})
        if existing:
            existing.metadata.setdefault("duplicate_registration_attempts", []).append(
                {
                    "timestamp": employer.created_at,
                    "request_log": request_log,
                    "submitted_employer_id": employer.id,
                }
            )
            existing.metadata["last_duplicate_registration_at"] = employer.created_at
            self.employers.update(existing)
            self._log(
                "employer",
                existing.id,
                "employer_duplicate_registration_suppressed",
                existing.id,
                existing.id,
                actor_id=employer.metadata.get("actor_id", "employer"),
                note="Existing employer matched by normalized contact/company data",
                metadata={"request_log": request_log},
                dedupe_key=f"employer_duplicate:{existing.id}",
            )
            return existing

        saved = self.employers.add(employer)
        self._log(
            "employer",
            saved.id,
            "employer_created",
            None,
            saved.id,
            actor_id=employer.metadata.get("actor_id", "employer"),
            note="Employer registered",
            metadata={"request_log": request_log},
            dedupe_key=f"employer_created:{saved.id}",
        )
        return saved

    def find_existing_employer(self, employer: Employer) -> Employer | None:
        email = _normalize(employer.contact_email)
        phone = _normalize_phone(employer.contact_phone)
        company = _normalize(employer.company_name)
        country = _normalize(employer.country_code)
        for existing in self.employers.list():
            same_email = email and _normalize(existing.contact_email) == email
            same_phone = phone and _normalize_phone(existing.contact_phone) == phone
            same_company_country = company and _normalize(existing.company_name) == company and _normalize(existing.country_code) == country
            if same_email or same_phone or same_company_country:
                return existing
        return None

    def create_vacancy(self, vacancy: Vacancy) -> Vacancy:
        employer = self.employers.get(vacancy.employer_id)
        vacancy, report = prepare_new_vacancy(
            vacancy,
            existing_vacancies=self.vacancies.list(),
            employer=employer,
            source=vacancy.metadata.get("source", "employer_manual"),
        )
        saved = self.vacancies.add(vacancy)
        self._log(
            "vacancy",
            saved.id,
            "vacancy_created",
            None,
            saved.status,
            actor_id=vacancy.metadata.get("actor_id", "employer"),
            note="Vacancy created and sent to moderation",
            metadata={"source": saved.metadata.get("source"), "quality_report": report},
        )
        record_event(
            self.activity,
            "vacancy_created",
            {
                "page": "api",
                "user_role": "employer",
                "vacancy_id": saved.id,
                "vacancy_source": saved.metadata.get("source"),
                "profession": saved.profession_code,
                "country": saved.country_code,
                "city": saved.location,
            },
            actor_id=vacancy.metadata.get("actor_id", "employer"),
        )
        return saved

    def create_document(self, document: Document) -> Document:
        return self.documents.add(document)

    def update_candidate_status(
        self,
        candidate_id: str,
        status: str,
        actor_id: str = "coordinator",
        note: str = "",
    ) -> Candidate:
        candidate = self._require_candidate(candidate_id)
        old_status = candidate.status
        candidate.status = status
        self.candidates.update(candidate)
        self._log("candidate", candidate.id, "status_changed", old_status, status, actor_id, note)
        return candidate

    def mark_candidate_documents_received(
        self,
        candidate_id: str,
        actor_id: str = "coordinator",
        note: str = "Documents received",
    ) -> Candidate:
        candidate = self._require_candidate(candidate_id)
        old_status = candidate.status
        old_missing = ",".join(candidate.metadata.get("missing_documents", []))
        candidate.metadata["missing_documents"] = []
        candidate.status = "ready_for_matching"
        self.candidates.update(candidate)
        self._log(
            "candidate",
            candidate.id,
            "documents_received",
            old_missing,
            "complete",
            actor_id,
            note,
        )
        self._log("candidate", candidate.id, "status_changed", old_status, candidate.status, actor_id, note)
        return candidate

    def set_employer_verified(
        self,
        employer_id: str,
        verified: bool = True,
        actor_id: str = "coordinator",
        note: str = "",
    ) -> Employer:
        employer = self._require_employer(employer_id)
        old_value = str(employer.verified)
        employer.verified = verified
        self.employers.update(employer)
        self._log("employer", employer.id, "verification_changed", old_value, str(verified), actor_id, note)
        return employer

    def update_vacancy_status(
        self,
        vacancy_id: str,
        status: str,
        actor_id: str = "coordinator",
        note: str = "",
    ) -> Vacancy:
        if status not in VACANCY_STATUSES and status not in {"matching", "filled", "closed"}:
            raise ValueError(f"Vacancy status '{status}' is not supported")
        vacancy = self._require_vacancy(vacancy_id)
        if status == "published" and vacancy.status not in PUBLISHABLE_STATUSES:
            raise ValueError("Vacancy must be verified before publication")
        if status == "rejected":
            reason = vacancy.metadata.get("rejection_reason") or note
            if not reason:
                raise ValueError("Rejection reason is required")
        old_status = vacancy.status
        vacancy.status = status
        if status == "verified":
            vacancy.metadata["verification_status"] = "verified"
        if status == "published":
            vacancy.metadata["verification_status"] = "published"
        if status == "rejected":
            vacancy.metadata["verification_status"] = "rejected"
            vacancy.metadata["rejection_reason"] = note if note in REJECTION_REASONS else (note or "other")
        self.vacancies.update(vacancy)
        action = {
            "verified": "vacancy_verified",
            "published": "vacancy_published",
            "rejected": "vacancy_rejected",
            "archived": "vacancy_archived",
        }.get(status, "status_changed")
        self._log("vacancy", vacancy.id, action, old_status, status, actor_id, note)
        if status in {"published", "rejected"}:
            record_event(
                self.activity,
                f"vacancy_{status}",
                {
                    "page": "dashboard",
                    "user_role": "coordinator",
                    "vacancy_id": vacancy.id,
                    "vacancy_source": vacancy.metadata.get("source"),
                    "profession": vacancy.profession_code,
                    "country": vacancy.country_code,
                    "city": vacancy.location,
                },
                actor_id=actor_id,
            )
        return vacancy

    def update_match_status(
        self,
        match_id: str,
        status: str,
        actor_id: str = "coordinator",
        note: str = "",
    ) -> Match:
        match = self._require_match(match_id)
        old_status = str(match.status)
        match.status = status
        self.matches.update(match)
        self._log("match", match.id, "status_changed", old_status, status, actor_id, note)
        return match

    def list_activity(self, limit: int = 50) -> list[ActivityEvent]:
        events = sorted(self.activity.list(), key=lambda event: event.created_at, reverse=True)
        return events[:limit]

    def find_matches_for_vacancy(
        self,
        vacancy_id: str,
        minimum_score: int = 60,
    ) -> list[Match]:
        vacancy = self.vacancies.get(vacancy_id)
        if vacancy is None:
            raise ValueError(f"Vacancy '{vacancy_id}' was not found")

        saved_matches: list[Match] = []
        vacancy_profile = self._vacancy_profile(vacancy)

        for candidate in self.candidates.list():
            candidate_profile = self._candidate_profile(candidate, vacancy)
            context = self.matching_agent.build_context(
                user_id=candidate_profile.user_id,
                profile={"candidate": candidate_profile, "vacancy": vacancy_profile},
            )
            result = self.matching_agent.respond("CRM automatic matching.", context)

            if result["match_score"] >= minimum_score:
                match = Match(
                    candidate_id=candidate.id,
                    vacancy_id=vacancy.id,
                    score=float(result["match_score"]),
                    reasons=result["reasons"],
                    metadata={
                        "risks": result["risks"],
                        "recommendation": result["recommendation"],
                    },
                )
                self.matches.add(match)
                candidate.status = "matched"
                self.candidates.update(candidate)
                saved_matches.append(match)

        return saved_matches

    def coordinator_dashboard(self) -> dict[str, Any]:
        candidates = self.candidates.list()
        employers = self.employers.list()
        vacancies = self.vacancies.list()
        matches = self.matches.list()
        real_employers = [employer for employer in employers if not is_demo_record(employer)]
        real_vacancies = [vacancy for vacancy in vacancies if not is_demo_record(vacancy)]

        strong_matches = [
            match.to_dict()
            for match in matches
            if match.score >= 80 and not match.metadata.get("risks")
        ]
        risky_cases = [
            match.to_dict()
            for match in matches
            if match.metadata.get("risks") or match.metadata.get("recommendation") != "strong_match"
        ]
        manual_contact = [
            candidate.to_dict()
            for candidate in candidates
            if candidate.status in {"documents_pending", "matched"}
        ]

        return {
            "new_candidates": [candidate.to_dict() for candidate in candidates if candidate.status == "new"],
            "new_employers": [employer.to_dict() for employer in real_employers if not employer.verified],
            "open_vacancies": [vacancy.to_dict() for vacancy in real_vacancies if vacancy.status in {"open", "published"}],
            "pending_vacancies": [vacancy.to_dict() for vacancy in real_vacancies if vacancy.status == "pending_review"],
            "recent_vacancies": [vacancy.to_dict() for vacancy in sorted(real_vacancies, key=lambda item: item.created_at, reverse=True)[:20]],
            "demo_records": {
                "employers": [employer.to_dict() for employer in employers if is_demo_record(employer)],
                "vacancies": [vacancy.to_dict() for vacancy in vacancies if is_demo_record(vacancy)],
            },
            "strong_matches": strong_matches,
            "risky_cases": risky_cases,
            "manual_contact": manual_contact,
            "activity": [event.to_dict() for event in self.list_activity(limit=20)],
            "analytics": self.internal_analytics(days=1),
            "first_vacancies_report": self.first_vacancies_report(),
            "event_feed": self._event_feed(candidates, real_employers, strong_matches, risky_cases, manual_contact),
        }

    def internal_analytics(
        self,
        days: int = 1,
        country: str | None = None,
        language: str | None = None,
        profession: str | None = None,
        traffic_source: str | None = None,
        user_role: str | None = None,
    ) -> dict[str, Any]:
        return analytics_summary(
            candidates=self.candidates.list(),
            employers=self.employers.list(),
            vacancies=self.vacancies.list(),
            matches=self.matches.list(),
            activity=self.activity.list(),
            days=days,
            country=country,
            language=language,
            profession=profession,
            traffic_source=traffic_source,
            user_role=user_role,
        )

    def first_vacancies_report(self, limit: int = 5) -> list[dict[str, Any]]:
        return first_vacancies_report(self.vacancies.list(), self.employers.list(), limit=limit)

    @staticmethod
    def _candidate_profile(candidate: Candidate, vacancy: Vacancy) -> CandidateProfile:
        desired_country_code = candidate.metadata.get("desired_country_code", vacancy.country_code)
        documents = candidate.metadata.get("document_types", candidate.documents)
        return CandidateProfile(
            user_id=candidate.user_id or candidate.id,
            profession_code=candidate.profession_code,
            experience_years=candidate.years_of_experience,
            current_country_code=candidate.country_code,
            desired_country_code=desired_country_code,
            documents=documents,
            desired_salary=candidate.metadata.get("desired_salary"),
            salary_currency=candidate.metadata.get("salary_currency", vacancy.currency),
            ready_from=candidate.metadata.get("ready_from"),
            languages=candidate.languages,
            offered_vacancy_history=candidate.metadata.get("offered_vacancy_history", []),
            metadata=candidate.metadata,
        )

    @staticmethod
    def _vacancy_profile(vacancy: Vacancy) -> VacancyProfile:
        return VacancyProfile(
            vacancy_id=vacancy.id,
            employer_user_id=vacancy.employer_id,
            profession_code=vacancy.profession_code,
            country_code=vacancy.country_code,
            salary_min=vacancy.salary_min,
            salary_max=vacancy.salary_max,
            salary_currency=vacancy.currency,
            required_languages=vacancy.required_languages,
            required_documents=vacancy.required_documents,
            contract_type=vacancy.metadata.get("contract_type", "not_specified"),
            housing=bool(vacancy.metadata.get("housing", False)),
            people_needed=int(vacancy.metadata.get("people_needed", 1)),
            requirements=vacancy.metadata.get("requirements", []),
            metadata=vacancy.metadata,
        )

    def _log(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        old_value: str | None,
        new_value: str | None,
        actor_id: str,
        note: str,
        metadata: dict[str, Any] | None = None,
        dedupe_key: str | None = None,
        correlation_id: str | None = None,
    ) -> ActivityEvent:
        if dedupe_key and self._recent_duplicate_event(dedupe_key, seconds=10):
            existing = self._recent_duplicate_event(dedupe_key, seconds=10)
            if existing:
                return existing
        event = ActivityEvent(
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            actor_id=actor_id,
            note=note,
            metadata=metadata or {},
            correlation_id=correlation_id or (metadata or {}).get("correlation_id") or (metadata or {}).get("request_log", {}).get("request_id") or "",
        )
        if not event.correlation_id:
            event.correlation_id = event.event_id
        if dedupe_key:
            event.metadata["dedupe_key"] = dedupe_key
        return self.activity.add(event)

    def _recent_duplicate_event(self, dedupe_key: str, seconds: int) -> ActivityEvent | None:
        now = datetime.now(timezone.utc)
        for event in sorted(self.activity.list(), key=lambda item: item.created_at, reverse=True):
            if event.metadata.get("dedupe_key") != dedupe_key:
                continue
            try:
                created_at = datetime.fromisoformat(event.created_at)
            except ValueError:
                continue
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            if (now - created_at).total_seconds() <= seconds:
                return event
        return None

    def _require_candidate(self, candidate_id: str) -> Candidate:
        candidate = self.candidates.get(candidate_id)
        if candidate is None:
            raise ValueError(f"Candidate '{candidate_id}' was not found")
        return candidate

    def _require_employer(self, employer_id: str) -> Employer:
        employer = self.employers.get(employer_id)
        if employer is None:
            raise ValueError(f"Employer '{employer_id}' was not found")
        return employer

    def _require_vacancy(self, vacancy_id: str) -> Vacancy:
        vacancy = self.vacancies.get(vacancy_id)
        if vacancy is None:
            raise ValueError(f"Vacancy '{vacancy_id}' was not found")
        return vacancy

    def _require_match(self, match_id: str) -> Match:
        match = self.matches.get(match_id)
        if match is None:
            raise ValueError(f"Match '{match_id}' was not found")
        return match

    @staticmethod
    def _event_feed(
        candidates: list[Candidate],
        employers: list[Employer],
        strong_matches: list[dict[str, Any]],
        risky_cases: list[dict[str, Any]],
        manual_contact: list[dict[str, Any]],
    ) -> list[dict[str, str]]:
        feed: list[dict[str, str]] = []
        for candidate in candidates[-5:]:
            feed.append(
                {
                    "type": "user",
                    "label": "🔥 New user",
                    "text": f"{candidate.first_name} {candidate.last_name} joined as candidate",
                }
            )
            feed.append(
                {
                    "type": "candidate",
                    "label": "👷 New candidate",
                    "text": f"{candidate.first_name} {candidate.last_name} · {candidate.profession_code}",
                }
            )
        seen_employers: set[tuple[str, str, str, str]] = set()
        for employer in employers[-5:]:
            employer_key = (
                _normalize(employer.company_name),
                _normalize(employer.contact_email),
                _normalize_phone(employer.contact_phone),
                _normalize(employer.country_code),
            )
            if employer_key in seen_employers or employer.metadata.get("possible_duplicate_of"):
                continue
            seen_employers.add(employer_key)
            feed.append(
                {
                    "type": "employer",
                    "label": "🏢 New employer",
                    "text": f"{employer.company_name} · {employer.country_code}",
                }
            )
        for item in risky_cases[-5:]:
            feed.append(
                {
                    "type": "risk",
                    "label": "⚠ Document risk",
                    "text": f"{item.get('candidate_id')} · {item.get('metadata', {}).get('recommendation')}",
                }
            )
        for item in strong_matches[-5:]:
            feed.append(
                {
                    "type": "match",
                    "label": "✅ Strong match",
                    "text": f"{item.get('candidate_id')} · {item.get('score')}%",
                }
            )
        for item in manual_contact[-5:]:
            feed.append(
                {
                    "type": "contact",
                    "label": "📞 Manual contact needed",
                    "text": f"{item.get('first_name')} {item.get('last_name')} · {item.get('status')}",
                }
            )
        feed.append(
            {
                "type": "coordinator",
                "label": "⭐ Coordinator recommendation",
                "text": "Operations action list updated",
            }
        )
        return feed[-20:]


def _normalize(value: str | None) -> str:
    return (value or "").strip().casefold()


def _normalize_phone(value: str | None) -> str:
    return "".join(char for char in (value or "") if char.isdigit())
