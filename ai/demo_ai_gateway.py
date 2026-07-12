"""Demo: CandidateAgent uses AI Gateway with MockAIProvider."""

import sys
import tempfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from agents.candidate_agent import CandidateAgent
from ai.ai_gateway import AIGateway, AIProviderRegistry
from ai.mock_provider import MockAIProvider
from core.user_profile import CandidateProfile
from memory.memory_store import JsonMemoryStore
from services.country_config_loader import CountryConfigLoader


def main() -> None:
    registry = AIProviderRegistry()
    registry.register(MockAIProvider())
    gateway = AIGateway(registry=registry, default_provider="mock")
    memory_store = JsonMemoryStore(Path(tempfile.mkdtemp(prefix="atlas_ewu_ai_memory_")))

    profile = CandidateProfile(
        user_id="candidate-ai-demo",
        profession_code="welder",
        experience_years=5,
        current_country_code="UA",
        desired_country_code="PL",
        documents=["passport_or_id", "cv"],
        desired_salary=6200,
        salary_currency="PLN",
        ready_from="2026-08-01",
        languages=["uk", "pl"],
    )

    agent = CandidateAgent(memory_store=memory_store, ai_gateway=gateway)
    country_config = CountryConfigLoader().load_by_code(profile.desired_country_code)
    context = agent.build_context(
        user_id=profile.user_id,
        profile=profile,
        country_config=country_config,
    )
    result = agent.respond(
        "I am ready to work as a welder in Poland.",
        context,
    )
    updated_memory = memory_store.load(profile.user_id)

    print(
        {
            "agent_result": result,
            "updated_memory": updated_memory.to_dict(),
        }
    )


if __name__ == "__main__":
    main()

