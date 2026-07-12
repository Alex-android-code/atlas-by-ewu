"""Agent that compares candidate and vacancy profiles."""

from typing import Any

from agents.base_agent import BaseAgent
from core.agent_context import AgentContext
from core.user_profile import CandidateProfile, VacancyProfile


class MatchingAgent(BaseAgent):
    agent_type = "matching"

    def respond(self, message: str, context: AgentContext) -> dict[str, Any]:
        candidate, vacancy = self._profiles(context)
        ai_response = self.ask_ai(message, context)
        result = self.compare(candidate, vacancy)
        context.memory.last_offers.append(
            {
                "vacancy_id": vacancy.vacancy_id,
                "match_score": result["match_score"],
                "recommendation": result["recommendation"],
            }
        )
        self.save_memory(context.memory)
        return {"agent": self.agent_type, "message": message, "ai": ai_response, **result}

    def compare(self, candidate: CandidateProfile, vacancy: VacancyProfile) -> dict[str, Any]:
        score = 0
        reasons: list[str] = []
        risks: list[str] = []

        if candidate.profession_code == vacancy.profession_code:
            score += 35
            reasons.append("profession_match")
        else:
            risks.append("profession_mismatch")

        shared_languages = sorted(set(candidate.languages) & set(vacancy.required_languages))
        if shared_languages:
            score += 20
            reasons.append(f"language_match:{','.join(shared_languages)}")
        elif vacancy.required_languages:
            risks.append("no_required_language_match")

        if candidate.desired_country_code == vacancy.country_code:
            score += 15
            reasons.append("desired_country_match")

        if self._salary_matches(candidate, vacancy):
            score += 15
            reasons.append("salary_expectation_match")
        else:
            risks.append("salary_expectation_gap")

        missing_documents = [
            document for document in vacancy.required_documents if document not in candidate.documents
        ]
        if not missing_documents:
            score += 15
            reasons.append("documents_ready")
        else:
            risks.append(f"missing_documents:{','.join(missing_documents)}")

        country_missing_documents = candidate.metadata.get("missing_documents", [])
        if country_missing_documents:
            score -= 10
            risks.append(f"country_documents_pending:{','.join(country_missing_documents)}")

        score = max(0, min(100, score))
        return {
            "candidate_user_id": candidate.user_id,
            "vacancy_id": vacancy.vacancy_id,
            "match_score": score,
            "reasons": reasons,
            "risks": risks,
            "recommendation": self._recommendation(score, risks),
        }

    @staticmethod
    def _profiles(context: AgentContext) -> tuple[CandidateProfile, VacancyProfile]:
        if not isinstance(context.profile, dict):
            raise TypeError("MatchingAgent requires profile dict with candidate and vacancy")

        candidate = context.profile.get("candidate")
        vacancy = context.profile.get("vacancy")

        if not isinstance(candidate, CandidateProfile) or not isinstance(vacancy, VacancyProfile):
            raise TypeError("MatchingAgent requires CandidateProfile and VacancyProfile")

        return candidate, vacancy

    @staticmethod
    def _salary_matches(candidate: CandidateProfile, vacancy: VacancyProfile) -> bool:
        if candidate.desired_salary is None or vacancy.salary_max is None:
            return True
        if candidate.salary_currency and vacancy.salary_currency:
            if candidate.salary_currency != vacancy.salary_currency:
                return False
        return candidate.desired_salary <= vacancy.salary_max

    @staticmethod
    def _recommendation(score: int, risks: list[str]) -> str:
        if score >= 80 and not risks:
            return "strong_match"
        if score >= 60:
            return "review_with_coordinator"
        return "do_not_send_without_manual_review"
