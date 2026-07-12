"""Personal agent for employers."""

from agents.base_agent import BaseAgent
from core.agent_context import AgentContext
from core.user_profile import EmployerProfile


class EmployerAgent(BaseAgent):
    agent_type = "employer"

    def respond(self, message: str, context: AgentContext) -> dict[str, object]:
        profile = self._profile(context)
        ai_response = self.ask_ai(message, context)
        memory = context.memory
        memory.profile_data.update(profile.to_dict())
        memory.conversation_summary = f"{memory.conversation_summary}\nEmployer: {message}".strip()
        memory.preferences.update(
            {
                "people_needed": profile.people_needed,
                "rate": profile.rate,
                "rate_currency": profile.rate_currency,
                "housing": profile.housing,
                "contract_type": profile.contract_type,
                "requirements": profile.requirements,
            }
        )
        memory.last_offers = [
            {"candidate_id": candidate_id, "status": "previously_suggested"}
            for candidate_id in profile.candidate_history[-10:]
        ]
        self.save_memory(memory)

        needs_human = profile.people_needed <= 0 or not profile.requirements
        if needs_human:
            return self.handoff_to_human(context, "Employer request needs manual clarification")

        return {
            "agent": self.agent_type,
            "response": "Employer profile updated and ready for candidate search.",
            "ai": ai_response,
            "profile": profile.to_dict(),
            "handoff_required": False,
        }

    @staticmethod
    def _profile(context: AgentContext) -> EmployerProfile:
        if not isinstance(context.profile, EmployerProfile):
            raise TypeError("EmployerAgent requires EmployerProfile")
        return context.profile
