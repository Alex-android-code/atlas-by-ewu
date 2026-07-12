"""Router for selecting logical ATLAS agents."""

from typing import Type

from ai.ai_gateway import AIGateway, get_default_ai_gateway
from agents.base_agent import BaseAgent
from agents.candidate_agent import CandidateAgent
from agents.coordinator_agent import CoordinatorAgent
from agents.document_agent import DocumentAgent
from agents.employer_agent import EmployerAgent
from agents.legal_agent import LegalAgent
from agents.matching_agent import MatchingAgent
from memory.memory_store import MemoryStore


class AgentRouter:
    def __init__(self, memory_store: MemoryStore, ai_gateway: AIGateway | None = None) -> None:
        self.memory_store = memory_store
        self.ai_gateway = ai_gateway or get_default_ai_gateway()
        self._agent_classes: dict[str, Type[BaseAgent]] = {
            "candidate": CandidateAgent,
            "employer": EmployerAgent,
            "coordinator": CoordinatorAgent,
            "matching": MatchingAgent,
            "legal": LegalAgent,
            "document": DocumentAgent,
        }

    def route(self, agent_type: str) -> BaseAgent:
        normalized = agent_type.strip().lower()
        agent_class = self._agent_classes.get(normalized)

        if agent_class is None:
            available = ", ".join(sorted(self._agent_classes))
            raise ValueError(f"Unknown agent type '{agent_type}'. Available: {available}")

        return agent_class(self.memory_store, ai_gateway=self.ai_gateway)

    def available_agents(self) -> list[str]:
        return sorted(self._agent_classes)
