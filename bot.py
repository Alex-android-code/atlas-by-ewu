"""Example launch for personal ATLAS agents.

This is not a Telegram bot per user. It is one application entry point that
routes messages to logical agent roles with separate memory per user_id.
"""

from core.agent_router import AgentRouter
from core.user_profile import CandidateProfile, VacancyProfile
from memory.memory_store import JsonMemoryStore
from services.country_config_loader import CountryConfigLoader


def main() -> None:
    memory_store = JsonMemoryStore()
    router = AgentRouter(memory_store)
    country_loader = CountryConfigLoader()

    candidate_profile = CandidateProfile(
        user_id="user-candidate-001",
        profession_code="welder",
        experience_years=5,
        current_country_code="UA",
        desired_country_code="PL",
        documents=["passport_or_id", "cv"],
        desired_salary=6200,
        salary_currency="PLN",
        ready_from="2026-07-15",
        languages=["uk", "pl"],
        offered_vacancy_history=[],
    )

    country_config = country_loader.load_by_code(candidate_profile.desired_country_code)
    candidate_agent = router.route("candidate")
    candidate_context = candidate_agent.build_context(
        user_id=candidate_profile.user_id,
        profile=candidate_profile,
        country_config=country_config,
    )
    candidate_result = candidate_agent.respond(
        "I am ready to work as a welder and can relocate in July.",
        candidate_context,
    )

    vacancy_profile = VacancyProfile(
        vacancy_id="vacancy-welder-001",
        employer_user_id="user-employer-001",
        profession_code="welder",
        country_code="PL",
        salary_min=5500,
        salary_max=7000,
        salary_currency="PLN",
        required_languages=["pl"],
        required_documents=["passport_or_id", "cv"],
        contract_type="umowa_o_prace",
        housing=True,
        people_needed=3,
        requirements=["mig_mag", "technical_drawing"],
    )

    matching_agent = router.route("matching")
    matching_context = matching_agent.build_context(
        user_id=candidate_profile.user_id,
        profile={"candidate": candidate_profile, "vacancy": vacancy_profile},
    )
    matching_result = matching_agent.respond("Compare candidate with vacancy.", matching_context)

    print(
        {
            "candidate_agent": candidate_result,
            "matching_agent": matching_result,
        }
    )


if __name__ == "__main__":
    main()
