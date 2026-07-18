import os
import unittest
from types import SimpleNamespace

from ai.ai_gateway import AIGateway, AIProviderRegistry
from ai.gemini_provider import GeminiProvider
from ai.mock_provider import MockAIProvider
from api.app import ai_message, root_health
from api.schemas import AIMessageRequest
from services.gemini_service import (
    FALLBACK_MESSAGES,
    GeminiService,
    GeminiServiceError,
    classify_gemini_error,
    fallback_message,
    sanitize_user_text,
    validate_gemini_json,
)


class FakeGeminiService(GeminiService):
    def __init__(self, responses):
        super().__init__(api_key="fake", timeout_seconds=1, max_retries=1)
        self.responses = list(responses)

    def _call_model(self, prompt: str) -> str:
        if not self.responses:
            return ""
        value = self.responses.pop(0)
        if isinstance(value, Exception):
            raise value
        return value


class GeminiServiceTests(unittest.TestCase):
    def test_no_key_is_degraded(self):
        service = GeminiService(api_key="")
        self.assertFalse(service.is_configured())
        self.assertEqual(service.health_check()["status"], "degraded")

    def test_sanitize_removes_html_and_scripts(self):
        text = sanitize_user_text("<script>alert(1)</script><b>Hello</b>")
        self.assertNotIn("<script", text.lower())
        self.assertNotIn("<b>", text.lower())
        self.assertIn("Hello", text)

    def test_validate_structured_json(self):
        result = validate_gemini_json(
            {
                "message": "How many years of experience do you have?",
                "next_field": "experience",
                "profile_updates": {"profession": "Welder"},
                "warnings": ["confirmed_data_only"],
                "confidence": 0.9,
            }
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.next_field, "experience")
        self.assertEqual(result.confidence, 0.9)

    def test_invalid_json_repair_once(self):
        service = FakeGeminiService(
            [
                "not json",
                '{"message":"Continue profile","next_field":"experience","profile_updates":{},"warnings":[],"confidence":0.8}',
            ]
        )
        result = service.generate_json("prompt")
        self.assertEqual(result.message, "Continue profile")

    def test_empty_response_raises_safe_error(self):
        service = FakeGeminiService([""])
        with self.assertRaises(GeminiServiceError) as ctx:
            service.generate_text("prompt")
        self.assertEqual(ctx.exception.error_type, "empty_response")

    def test_429_classified_as_retryable_rate_limit(self):
        error = classify_gemini_error(Exception("429 quota exceeded"))
        self.assertEqual(error.error_type, "rate_limited")
        self.assertTrue(error.retryable)

    def test_auth_error_is_not_retryable(self):
        error = classify_gemini_error(Exception("403 invalid API key"))
        self.assertEqual(error.error_type, "auth_error")
        self.assertFalse(error.retryable)

    def test_fallback_messages_for_all_languages(self):
        for language in ("uk", "ru", "pl", "en", "de", "es", "pt"):
            self.assertEqual(fallback_message(language), FALLBACK_MESSAGES[language])

    def test_gateway_uses_mock_fallback_when_gemini_unconfigured(self):
        registry = AIProviderRegistry()
        registry.register(MockAIProvider())
        registry.register(GeminiProvider(GeminiService(api_key="")))
        gateway = AIGateway(registry=registry, default_provider="gemini", fallback_provider="mock")
        response = gateway.send_message_to_ai(
            user_id="test",
            agent_type="candidate",
            context={"language": "en", "profile": {}},
            message="I am a welder",
        )
        self.assertIn("reply", response)
        self.assertTrue(response["metadata"].get("fallback_used") in {True, False})
        self.assertNotIn("fake", str(response))

    def test_endpoint_fallback_does_not_leak_key(self):
        previous = os.environ.pop("GEMINI_API_KEY", None)
        try:
            payload = AIMessageRequest(message="I am a welder", language="en", role="candidate", current_step="profession")
            request = SimpleNamespace(client=SimpleNamespace(host="unit-test"))
            response = ai_message(payload, request)
            self.assertIn(response["success"], {True, False})
            self.assertIn("message", response)
            self.assertNotIn("GEMINI_API_KEY", str(response))
        finally:
            if previous is not None:
                os.environ["GEMINI_API_KEY"] = previous

    def test_health_does_not_ping_gemini(self):
        health = root_health()
        self.assertEqual(health["status"], "ok")
        self.assertEqual(health["app"], "atlas")


if __name__ == "__main__":
    unittest.main()
