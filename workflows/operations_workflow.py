"""End-to-end operations workflow for EWU.

The workflow coordinates CRM repositories, country configs, personal memory,
document checks, legal triage, matching, and coordinator summaries.
"""

from typing import Any

from agents.coordinator_agent import CoordinatorAgent
from agents.document_agent import DocumentAgent
from agents.legal_agent import LegalAgent
from core.models import Candidate, Employer, Vacancy
from crm.crm_service import CrmService
from memory.memory_store import MemoryStore
from services.country_config_loader import CountryConfigLoader


class OperationsWorkflow:
    def __init__(
        self,
        crm: CrmService,
        memory_store: MemoryStore,
        country_loader: CountryConfigLoader,
    ) -> None:
        self.crm = crm
        self.memory_store = memory_store
        self.country_loader = country_loader
        self.document_agent = DocumentAgent(memory_store)
        self.legal_agent = LegalAgent(memory_store)
        self.coordinator_agent = CoordinatorAgent(memory_store)

    def onboard_candidate(self, candidate: Candidate) -> dict[str, Any]:
        target_country = candidate.metadata.get("desired_country_code", candidate.country_code)
        country_config = self.country_loader.load_by_code(target_country)
        provided_documents = candidate.metadata.get("document_types", [])
        user_id = candidate.user_id or candidate.id

        document_context = self.document_agent.build_context(
            user_id=user_id,
            country_config=country_config,
            metadata={"provided_documents": provided_documents},
        )
        document_result = self.document_agent.respond(
            "Check candidate documents.",
            document_context,
        )

        candidate.status = "ready_for_matching"
        if document_result["missing_documents"]:
            candidate.status = "documents_pending"
            candidate.metadata["missing_documents"] = document_result["missing_documents"]

        saved_candidate = self.crm.create_candidate(candidate)
        return {
            "candidate": saved_candidate.to_dict(),
            "document_check": document_result,
        }

    def onboard_employer(self, employer: Employer) -> dict[str, Any]:
        saved_employer = self.crm.create_employer(employer)
        return {
            "employer": saved_employer.to_dict(),
            "verification_required": not saved_employer.verified,
            "duplicate_suppressed": saved_employer.id != employer.id,
        }

    def publish_vacancy(self, vacancy: Vacancy) -> dict[str, Any]:
        country_config = self.country_loader.load_by_code(vacancy.country_code)
        legal_case = {
            "contract_type": vacancy.metadata.get("contract_type"),
            "work_permission_status": vacancy.metadata.get("work_permission_status"),
            "housing": vacancy.metadata.get("housing"),
            "housing_terms": vacancy.metadata.get("housing_terms"),
            "salary_confirmed": vacancy.metadata.get("salary_confirmed"),
            "country_code": country_config["code"],
        }
        legal_context = self.legal_agent.build_context(
            user_id=vacancy.employer_id,
            country_config=country_config,
            metadata={"case_data": legal_case},
        )
        legal_result = self.legal_agent.respond("Run legal risk triage.", legal_context)

        vacancy.status = "pending_review"
        if legal_result["level"] == "critical":
            vacancy.metadata["legal_blocker"] = legal_result["risks"]
        elif legal_result["level"] == "warning":
            vacancy.metadata["legal_warning"] = legal_result["risks"]

        saved_vacancy = self.crm.create_vacancy(vacancy)
        return {
            "vacancy": saved_vacancy.to_dict(),
            "legal_triage": legal_result,
        }

    def run_matching_for_vacancy(
        self,
        vacancy_id: str,
        minimum_score: int = 60,
    ) -> dict[str, Any]:
        matches = self.crm.find_matches_for_vacancy(vacancy_id, minimum_score=minimum_score)
        return {
            "vacancy_id": vacancy_id,
            "matches": [match.to_dict() for match in matches],
        }

    def build_coordinator_summary(self, coordinator_user_id: str = "coordinator-main") -> dict[str, Any]:
        dashboard = self.crm.coordinator_dashboard()
        context = self.coordinator_agent.build_context(
            user_id=coordinator_user_id,
            metadata={"dashboard": dashboard},
        )
        return self.coordinator_agent.respond("Build coordinator operations summary.", context)

    def process_vacancy_pipeline(
        self,
        vacancy: Vacancy,
        minimum_score: int = 60,
    ) -> dict[str, Any]:
        vacancy_result = self.publish_vacancy(vacancy)
        matching_result: dict[str, Any] = {"matches": []}

        if vacancy_result["vacancy"]["status"] == "published":
            matching_result = self.run_matching_for_vacancy(
                vacancy_result["vacancy"]["id"],
                minimum_score=minimum_score,
            )

        coordinator_summary = self.build_coordinator_summary()
        return {
            "vacancy_result": vacancy_result,
            "matching_result": matching_result,
            "coordinator_summary": coordinator_summary["summary"],
        }
