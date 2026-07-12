"""Candidate registration workflow."""

from dataclasses import dataclass, field
from typing import Any

from core.models import Candidate, Document
from services.country_config_loader import CountryConfigLoader


@dataclass
class CandidateRegistrationResult:
    candidate: Candidate
    required_documents: list[Document]
    country_config: dict[str, Any] = field(repr=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate": self.candidate.to_dict(),
            "required_documents": [document.to_dict() for document in self.required_documents],
            "country": {
                "code": self.country_config["code"],
                "name": self.country_config["name"],
                "currency": self.country_config["currency"],
            },
        }


def register_candidate(
    candidate: Candidate,
    country_loader: CountryConfigLoader,
) -> CandidateRegistrationResult:
    country_config = country_loader.load_by_code(candidate.country_code)
    required_types = country_config.get("documents", {}).get("candidate_required", [])
    documents = [
        Document(
            owner_id=candidate.id,
            document_type=document_type,
            country_code=country_config["code"],
        )
        for document_type in required_types
    ]

    candidate.documents = [document.id for document in documents]
    candidate.status = "registered"
    candidate.metadata["country_name"] = country_config["name"]
    candidate.metadata["required_document_types"] = required_types

    return CandidateRegistrationResult(
        candidate=candidate,
        required_documents=documents,
        country_config=country_config,
    )

