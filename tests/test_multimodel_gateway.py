import asyncio
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from ai.ai_gateway import AIProviderRegistry, MultiModelGateway
from ai.cache import MemoryTTLCache, build_exact_cache_key
from ai.constitutional_guard import ConstitutionalGuard
from ai.escalation import JsonEscalationService
from ai.models import MatchingEvaluation, ModelResult, TaskType
from ai.mock_provider import MockAIProvider
from ai.privacy import build_safe_ai_context, mask_document_number, mask_email, mask_phone
from ai.providers import OpenAIProvider
from ai.router import ModelRouter
from ai.structured_outputs import deterministic_top_n
from ai.usage_tracker import UsageTracker


class CaptureProvider:
    name = "capture"
    model = "capture-model"

    def __init__(self, content: str = "captured") -> None:
        self.content = content
        self.calls: list[dict[str, Any]] = []

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "model": self.model}

    async def close(self) -> None:
        self.closed = True

    async def call_model(self, *, system_prompt: str, user_message: str, context: dict[str, Any], role: str, estimated_tokens: int) -> ModelResult:
        self.calls.append({"system_prompt": system_prompt, "user_message": user_message, "context": context, "role": role})
        return ModelResult(self.content, self.name, self.model, estimated_tokens, 3, 0.0, 1, False)


class FailingProvider(CaptureProvider):
    async def call_model(self, **kwargs) -> ModelResult:
        raise TimeoutError("timeout")


class BrokenEscalationService:
    async def create_case(self, **kwargs):
        raise RuntimeError("storage down")


class MultiModelGatewayTests(unittest.IsolatedAsyncioTestCase):
    async def test_user_message_reaches_provider_as_user_message(self):
        provider = CaptureProvider("ok")
        registry = AIProviderRegistry()
        registry.register(provider)
        gateway = MultiModelGateway(registry=registry)
        await gateway.call_model(system_prompt="sys", user_message="hello user", context={"x": 1}, role="candidate", estimated_tokens=5, provider_name="capture")
        self.assertEqual(provider.calls[0]["user_message"], "hello user")
        self.assertNotIn("hello user", provider.calls[0]["system_prompt"])

    async def test_exact_cache_is_user_isolated(self):
        cache = MemoryTTLCache()
        key1 = build_exact_cache_key(tenant_id="t", user_id="u1", role="candidate", language="en", country="PL", message="same", profile_version="1", model="m")
        key2 = build_exact_cache_key(tenant_id="t", user_id="u2", role="candidate", language="en", country="PL", message="same", profile_version="1", model="m")
        await cache.set(key1, "u1 answer", 30)
        self.assertEqual(await cache.get(key1), "u1 answer")
        self.assertIsNone(await cache.get(key2))

    async def test_missing_openai_key_is_degraded_and_does_not_raise(self):
        provider = OpenAIProvider(api_key="")
        self.assertEqual(provider.health()["status"], "degraded")

    async def test_timeout_fallback_uses_next_provider(self):
        failing = FailingProvider()
        failing.name = "openai"
        failing.model = "openai-model"
        fallback = CaptureProvider("fallback answer")
        fallback.name = "anthropic"
        fallback.model = "anthropic-model"
        registry = AIProviderRegistry()
        registry.register(failing)
        registry.register(fallback)
        gateway = MultiModelGateway(registry=registry)
        result = await gateway.ask(user_id="u", role="candidate", context={"user_id": "u", "role": "candidate", "task": "chat"}, message="Hello")
        self.assertEqual(result["content"], "fallback answer")
        self.assertTrue(gateway.usage_tracker.records[-1].fallback_used)

    async def test_sensitive_request_creates_real_case(self):
        with TemporaryDirectory() as tmp:
            service = JsonEscalationService(Path(tmp) / "cases.jsonl")
            registry = AIProviderRegistry()
            registry.register(MockAIProvider())
            gateway = MultiModelGateway(registry=registry, escalation_service=service)
            result = await gateway.ask(user_id="u", role="candidate", context={"user_id": "u", "role": "candidate"}, message="Роботодавець забрав мої документи і не дозволяє піти.")
            self.assertTrue(result["requires_human_review"])
            self.assertTrue((Path(tmp) / "cases.jsonl").exists())

    async def test_escalation_failure_does_not_claim_success(self):
        registry = AIProviderRegistry()
        registry.register(MockAIProvider())
        gateway = MultiModelGateway(registry=registry, escalation_service=BrokenEscalationService())
        result = await gateway.ask(user_id="u", role="candidate", context={"user_id": "u", "role": "candidate"}, message="Не дозволяє піти і забрали паспорт.")
        self.assertEqual(result["status"], "escalation_failed")
        self.assertNotIn("передано координатору", result["content"])

    async def test_budget_limit_uses_template(self):
        previous = os.environ.get("AI_DAILY_BUDGET_EUR")
        os.environ["AI_DAILY_BUDGET_EUR"] = "0"
        try:
            registry = AIProviderRegistry()
            registry.register(CaptureProvider("should not call"))
            tracker = UsageTracker()
            gateway = MultiModelGateway(registry=registry, usage_tracker=tracker)
            result = await gateway.ask(user_id="u", role="candidate", context={"user_id": "u", "role": "candidate"}, message="Hello")
            self.assertEqual(result["status"], "budget_limited")
        finally:
            if previous is None:
                os.environ.pop("AI_DAILY_BUDGET_EUR", None)
            else:
                os.environ["AI_DAILY_BUDGET_EUR"] = previous

    async def test_close_closes_providers(self):
        provider = CaptureProvider()
        registry = AIProviderRegistry()
        registry.register(provider)
        gateway = MultiModelGateway(registry=registry)
        await gateway.close()
        self.assertTrue(getattr(provider, "closed", False))

    async def test_router_prefers_gemini_when_other_keys_are_missing(self):
        previous = {name: os.environ.get(name) for name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY")}
        os.environ.pop("OPENAI_API_KEY", None)
        os.environ.pop("ANTHROPIC_API_KEY", None)
        os.environ["GEMINI_API_KEY"] = "test-gemini"
        try:
            router = ModelRouter()
            chat = router.route(task_type=TaskType.CHAT, role="candidate", message="hello", context={})
            legal = router.route(task_type=TaskType.LEGAL_SENSITIVE, role="legal", message="passport issue", context={})
            employer = router.route(task_type=TaskType.EMPLOYER_ANALYSIS, role="employer", message="b2b", context={})
            self.assertEqual(chat.provider, "gemini")
            self.assertEqual(legal.provider, "gemini")
            self.assertEqual(employer.provider, "gemini")
            self.assertEqual(chat.fallback_order[0], "gemini")
        finally:
            for name, value in previous.items():
                if value is None:
                    os.environ.pop(name, None)
                else:
                    os.environ[name] = value


class GuardPrivacyAndStructuredTests(unittest.TestCase):
    def test_old_injury_is_not_urgent_escalation(self):
        decision = ConstitutionalGuard().evaluate("Десять років тому я мав травму руки.")
        self.assertFalse(decision.requires_human)

    def test_passport_retention_is_high_or_urgent(self):
        decision = ConstitutionalGuard().evaluate("Роботодавець забрав мої документи і не дозволяє піти.")
        self.assertTrue(decision.requires_human)
        self.assertIn(decision.level.value, {"high", "urgent", "emergency"})

    def test_personal_fields_are_masked_or_removed(self):
        context = build_safe_ai_context(
            {
                "profession": "welder",
                "email": "name@example.com",
                "phone": "+48123123123",
                "passport_number": "AB1234567",
                "documents": ["passport AB1234567"],
            },
            role="candidate",
            purpose="job_search",
        )
        self.assertEqual(context["profession"], "welder")
        self.assertNotIn("email", context)
        self.assertIn("***67", str(context))
        self.assertIn("***", mask_email("name@example.com"))
        self.assertIn("***", mask_phone("+48123123123"))
        self.assertIn("***", mask_document_number("AB1234567"))

    def test_structured_output_validates(self):
        item = MatchingEvaluation.model_validate(
            {
                "candidate_id": "c1",
                "vacancy_id": "v1",
                "hard_requirements_met": True,
                "compatibility_score": 80,
                "skill_score": 80,
                "location_score": 70,
                "language_score": 60,
                "document_score": 90,
                "salary_score": 75,
                "risks": [],
                "strengths": ["experience"],
                "missing_requirements": [],
                "recommendation": "human review",
                "requires_human_review": True,
            }
        )
        self.assertEqual(item.compatibility_score, 80)

    def test_final_matching_only_top_n(self):
        candidates = [{"id": "a", "score": 1}, {"id": "b", "score": 5}, {"id": "c", "score": 3}]
        self.assertEqual([item["id"] for item in deterministic_top_n(candidates, top_n=2)], ["b", "c"])

    def test_no_asyncio_run_in_repository_code(self):
        root = Path(__file__).resolve().parents[1]
        offenders = []
        for path in root.rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            needle = "asyncio" + ".run("
            if needle in text:
                offenders.append(str(path.relative_to(root)))
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
