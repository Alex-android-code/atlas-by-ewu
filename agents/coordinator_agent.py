"""Coordinator agent for operational summaries."""

from typing import Any

from agents.base_agent import BaseAgent
from core.agent_context import AgentContext


class CoordinatorAgent(BaseAgent):
    agent_type = "coordinator"

    def respond(self, message: str, context: AgentContext) -> dict[str, Any]:
        ai_response = self.ask_ai(message, context)
        dashboard = context.metadata.get("dashboard", {})
        summary = self.build_summary(dashboard)
        context.memory.coordinator_notes.append(summary["text"])
        self.save_memory(context.memory)
        return {"agent": self.agent_type, "message": message, "ai": ai_response, "summary": summary}

    @staticmethod
    def build_summary(dashboard: dict[str, Any]) -> dict[str, Any]:
        new_candidates = dashboard.get("new_candidates", [])
        new_employers = dashboard.get("new_employers", [])
        strong_matches = dashboard.get("strong_matches", [])
        risky_cases = dashboard.get("risky_cases", [])
        manual_contact = dashboard.get("manual_contact", [])

        text = (
            f"New candidates: {len(new_candidates)}. "
            f"New employers: {len(new_employers)}. "
            f"Strong matches: {len(strong_matches)}. "
            f"Risky cases: {len(risky_cases)}. "
            f"Manual contact needed: {len(manual_contact)}."
        )

        return {
            "text": text,
            "new_candidates": new_candidates,
            "new_employers": new_employers,
            "strong_matches": strong_matches,
            "risky_cases": risky_cases,
            "manual_contact": manual_contact,
        }
