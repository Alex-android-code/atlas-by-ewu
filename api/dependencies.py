"""API dependency builders."""

from functools import lru_cache

from crm.crm_service import CrmService
from database.json_database import JsonDatabase
from database.repositories import (
    CandidateRepository,
    ActivityRepository,
    DocumentRepository,
    EmployerRepository,
    MatchRepository,
    VacancyRepository,
)
from memory.memory_store import JsonMemoryStore
from services.country_config_loader import CountryConfigLoader
from workflows.operations_workflow import OperationsWorkflow


@lru_cache(maxsize=1)
def get_memory_store() -> JsonMemoryStore:
    return JsonMemoryStore()


@lru_cache(maxsize=1)
def get_database() -> JsonDatabase:
    return JsonDatabase()


def get_crm_service() -> CrmService:
    database = get_database()
    return CrmService(
        candidates=CandidateRepository(database),
        employers=EmployerRepository(database),
        vacancies=VacancyRepository(database),
        matches=MatchRepository(database),
        documents=DocumentRepository(database),
        activity=ActivityRepository(database),
        memory_store=get_memory_store(),
    )


def get_operations_workflow() -> OperationsWorkflow:
    return OperationsWorkflow(
        crm=get_crm_service(),
        memory_store=get_memory_store(),
        country_loader=CountryConfigLoader(),
    )
