"""Legal risk triage agent.

This agent does not provide final legal decisions. It flags risk and prepares
questions for a coordinator or qualified legal specialist.
"""

from typing import Any

from agents.base_agent import BaseAgent
from core.agent_context import AgentContext


class LegalAgent(BaseAgent):
    agent_type = "legal"

    def respond(self, message: str, context: AgentContext) -> dict[str, Any]:
        ai_response = self.ask_ai(message, context)
        case_data = context.metadata.get("case_data", {})
        assessment = self.assess(case_data)

        if assessment["level"] in {"warning", "critical"}:
            context.memory.risks.append(assessment)
            self.save_memory(context.memory)

        if assessment["level"] == "critical":
            handoff = self.handoff_to_human(context, "Critical legal risk needs coordinator review")
            assessment["handoff"] = handoff

        return {"agent": self.agent_type, "message": message, "ai": ai_response, **assessment}

    def assess(self, case_data: dict[str, Any]) -> dict[str, Any]:
        risks: list[str] = []
        questions: list[str] = []

        if not case_data.get("contract_type"):
            risks.append("missing_contract_type")
            questions.append("What contract type will be used?")

        if not case_data.get("work_permission_status"):
            risks.append("unknown_work_permission_status")
            questions.append("Does the worker have the required work permission?")

        if case_data.get("housing") is True and not case_data.get("housing_terms"):
            risks.append("housing_terms_not_defined")
            questions.append("What are the housing costs, address, and rules?")

        if case_data.get("salary_confirmed") is False:
            risks.append("salary_not_confirmed")
            questions.append("Is salary confirmed in writing by the employer?")

        level = self._level_for(risks)
        return {
            "level": level,
            "risks": risks,
            "questions": questions,
            "disclaimer": "This is risk triage, not final legal advice.",
            "handoff_required": level == "critical",
        }

    @staticmethod
    def _level_for(risks: list[str]) -> str:
        if len(risks) >= 3:
            return "critical"
        if risks:
            return "warning"
        return "normal"
