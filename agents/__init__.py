"""Logical AI agent roles inside one ATLAS Core."""

from .base_agent import BaseAgent
from .candidate_agent import CandidateAgent
from .coordinator_agent import CoordinatorAgent
from .document_agent import DocumentAgent
from .employer_agent import EmployerAgent
from .legal_agent import LegalAgent
from .matching_agent import MatchingAgent

__all__ = [
    "BaseAgent",
    "CandidateAgent",
    "CoordinatorAgent",
    "DocumentAgent",
    "EmployerAgent",
    "LegalAgent",
    "MatchingAgent",
]

