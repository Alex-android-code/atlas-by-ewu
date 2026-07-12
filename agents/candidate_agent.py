"""Personal agent for worker candidates."""

from typing import Any

from agents.base_agent import BaseAgent
from core.agent_context import AgentContext
from core.user_profile import CandidateProfile


class CandidateAgent(BaseAgent):
    agent_type = "candidate"

    def respond(self, message: str, context: AgentContext) -> dict[str, Any]:
        profile = self._profile(context)
        ai_response = self.ask_ai(message, context)
        memory = context.memory
        memory.profile_data.update(profile.to_dict())
        memory.conversation_summary = self._append_summary(memory.conversation_summary, message)
        memory.preferences.update(
            {
                "desired_country_code": profile.desired_country_code,
                "desired_salary": profile.desired_salary,
                "salary_currency": profile.salary_currency,
                "ready_from": profile.ready_from,
                "languages": profile.languages,
            }
        )
        memory.last_offers = [
            {"vacancy_id": vacancy_id, "status": "previously_offered"}
            for vacancy_id in profile.offered_vacancy_history[-10:]
        ]
        self.save_memory(memory)

        missing_documents = self._missing_documents(profile, context.country_config)
        response_text = "Candidate profile updated and ready for matching."
        if missing_documents:
            response_text = "Candidate profile updated. Missing documents should be requested."

        return {
            "agent": self.agent_type,
            "response": response_text,
            "ai": ai_response,
            "profile": profile.to_dict(),
            "missing_documents": missing_documents,
            "handoff_required": False,
        }

    @staticmethod
    def _profile(context: AgentContext) -> CandidateProfile:
        if not isinstance(context.profile, CandidateProfile):
            raise TypeError("CandidateAgent requires CandidateProfile")
        return context.profile

    @staticmethod
    def _append_summary(current: str, message: str) -> str:
        message = message.strip()
        if not message:
            return current
        return f"{current}\nCandidate: {message}".strip()

    @staticmethod
    def _missing_documents(
        profile: CandidateProfile,
        country_config: dict[str, Any] | None,
    ) -> list[str]:
        required = []
        if country_config:
            required = country_config.get("documents", {}).get("candidate_required", [])
        return [document for document in required if document not in profile.documents]
