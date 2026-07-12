"""Profiles used by personal agents.

Profiles are country-neutral. Country-specific documents and rules should come
from JSON configs and compliance services, not from hardcoded agent logic.
"""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class CandidateProfile:
    user_id: str
    profession_code: str
    experience_years: int
    current_country_code: str
    desired_country_code: str
    documents: list[str]
    desired_salary: float | None
    salary_currency: str | None
    ready_from: str | None
    languages: list[str]
    offered_vacancy_history: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EmployerProfile:
    user_id: str
    company_name: str
    country_code: str
    vacancies: list[str]
    people_needed: int
    rate: float | None
    rate_currency: str | None
    housing: bool
    contract_type: str
    requirements: list[str]
    candidate_history: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class VacancyProfile:
    vacancy_id: str
    employer_user_id: str
    profession_code: str
    country_code: str
    salary_min: float | None
    salary_max: float | None
    salary_currency: str | None
    required_languages: list[str]
    required_documents: list[str]
    contract_type: str
    housing: bool
    people_needed: int = 1
    requirements: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

