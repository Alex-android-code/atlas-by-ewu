"""Repository interfaces and JSON-backed MVP repositories."""

from dataclasses import fields
from typing import Any, Generic, Protocol, TypeVar

from core.models import (
    ActivityEvent,
    AgentAction,
    AgentMemoryRecord,
    AgentRecommendation,
    Candidate,
    CareerGoal,
    ConsentRecord,
    DataSubjectRequest,
    Document,
    Employer,
    Match,
    Opportunity,
    ProfessionalDNA,
    Subscription,
    User,
    UserPreference,
    Vacancy,
)
from database.json_database import JsonDatabase

ModelT = TypeVar("ModelT")


class Repository(Protocol[ModelT]):
    def add(self, item: ModelT) -> ModelT:
        ...

    def get(self, item_id: str) -> ModelT | None:
        ...

    def list(self) -> list[ModelT]:
        ...


class JsonRepository(Generic[ModelT]):
    collection: str
    model_class: type[ModelT]

    def __init__(self, database: JsonDatabase) -> None:
        self.database = database

    def add(self, item: ModelT) -> ModelT:
        self.database.insert(self.collection, self._item_id(item), self._to_dict(item))
        return item

    def update(self, item: ModelT) -> ModelT:
        self.database.update(self.collection, self._item_id(item), self._to_dict(item))
        return item

    def get(self, item_id: str) -> ModelT | None:
        data = self.database.get(self.collection, item_id)
        if data is None:
            return None
        return self._from_dict(data)

    def list(self) -> list[ModelT]:
        return [self._from_dict(item) for item in self.database.list(self.collection)]

    @staticmethod
    def _item_id(item: ModelT) -> str:
        return str(getattr(item, "id"))

    @staticmethod
    def _to_dict(item: ModelT) -> dict[str, Any]:
        to_dict = getattr(item, "to_dict", None)
        if callable(to_dict):
            return to_dict()
        raise TypeError(f"{type(item).__name__} must provide to_dict()")

    def _from_dict(self, data: dict[str, Any]) -> ModelT:
        allowed = {field.name for field in fields(self.model_class)}
        cleaned = {key: value for key, value in data.items() if key in allowed}
        return self.model_class(**cleaned)


class CandidateRepository(JsonRepository[Candidate]):
    collection = "candidates"
    model_class = Candidate


class UserRepository(JsonRepository[User]):
    collection = "users"
    model_class = User


class EmployerRepository(JsonRepository[Employer]):
    collection = "employers"
    model_class = Employer


class VacancyRepository(JsonRepository[Vacancy]):
    collection = "vacancies"
    model_class = Vacancy


class MatchRepository(JsonRepository[Match]):
    collection = "matches"
    model_class = Match


class DocumentRepository(JsonRepository[Document]):
    collection = "documents"
    model_class = Document


class ActivityRepository(JsonRepository[ActivityEvent]):
    collection = "activity"
    model_class = ActivityEvent


class ProfessionalDNARepository(JsonRepository[ProfessionalDNA]):
    collection = "professional_profiles"
    model_class = ProfessionalDNA


class AgentMemoryRepository(JsonRepository[AgentMemoryRecord]):
    collection = "agent_memories"
    model_class = AgentMemoryRecord


class AgentActionRepository(JsonRepository[AgentAction]):
    collection = "agent_actions"
    model_class = AgentAction


class AgentRecommendationRepository(JsonRepository[AgentRecommendation]):
    collection = "agent_recommendations"
    model_class = AgentRecommendation


class CareerGoalRepository(JsonRepository[CareerGoal]):
    collection = "career_goals"
    model_class = CareerGoal


class OpportunityRepository(JsonRepository[Opportunity]):
    collection = "opportunities"
    model_class = Opportunity


class UserPreferenceRepository(JsonRepository[UserPreference]):
    collection = "user_preferences"
    model_class = UserPreference


class ConsentRepository(JsonRepository[ConsentRecord]):
    collection = "consents"
    model_class = ConsentRecord


class DataSubjectRequestRepository(JsonRepository[DataSubjectRequest]):
    collection = "data_subject_requests"
    model_class = DataSubjectRequest


class SubscriptionRepository(JsonRepository[Subscription]):
    collection = "subscriptions"
    model_class = Subscription
