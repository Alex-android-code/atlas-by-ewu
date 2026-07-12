"""Mock AI provider for local development and tests."""

from ai.ai_gateway import AIRequest, AIResponse


class MockAIProvider:
    name = "mock"

    def health(self) -> dict:
        return {"status": "ok", "mode": "deterministic"}

    def send(self, request: AIRequest) -> AIResponse:
        action = self._action_for(request.agent_type)
        reply = self._reply_for(request)
        return AIResponse(
            reply=reply,
            action=action,
            confidence=0.72,
            handoff_required=False,
            metadata={
                "provider": self.name,
                "agent_type": request.agent_type,
                "context_keys": sorted(request.context.keys()),
            },
        )

    @staticmethod
    def _action_for(agent_type: str) -> str | None:
        actions = {
            "candidate": "update_candidate_memory",
            "employer": "update_employer_memory",
            "matching": "explain_match",
            "legal": "triage_legal_risk",
            "document": "check_documents",
            "coordinator": "summarize_dashboard",
        }
        return actions.get(agent_type)

    @staticmethod
    def _reply_for(request: AIRequest) -> str:
        text = request.message.lower()
        translations = request.context.get("translations", {})

        def t(key: str) -> str:
            return translations.get(key, key)

        if request.agent_type == "employer":
            experience = request.context.get("employer_experience") or {}
            cards = experience.get("advice_cards") or []
            first_advice = t(cards[0]["key"]) if cards else t("advisor.vacancy_strong")
            return (
                f"{t('employer.response_ack')}\n\n"
                f"{t('employer.response_live_analysis')}\n"
                f"{first_advice}\n\n"
                f"{t('employer.response_next_question')}"
            )

        if any(word in text for word in ("звар", "свар", "welder")):
            return (
                f"{t('coordinator.ask_profession')}\n\n"
                f"{t('coordinator.ask_country')}"
            )
        if any(word in text for word in ("працівників", "работников", "employees", "workers", "людей")):
            return t("coordinator.ask_employer_need")
        if any(word in text for word in ("консульта", "consultation", "advice")):
            return t("coordinator.consultation_start")
        return t("coordinator.welcome")
