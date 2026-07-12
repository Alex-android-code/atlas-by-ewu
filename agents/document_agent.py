"""Document agent for config-driven document checklists."""

from typing import Any

from agents.base_agent import BaseAgent
from core.agent_context import AgentContext


class DocumentAgent(BaseAgent):
    agent_type = "document"

    def respond(self, message: str, context: AgentContext) -> dict[str, Any]:
        ai_response = self.ask_ai(message, context)
        provided = set(context.metadata.get("provided_documents", []))
        required = []
        if context.country_config:
            required = context.country_config.get("documents", {}).get("candidate_required", [])

        missing = [document for document in required if document not in provided]
        return {
            "agent": self.agent_type,
            "message": message,
            "ai": ai_response,
            "required_documents": required,
            "missing_documents": missing,
            "handoff_required": False,
        }
