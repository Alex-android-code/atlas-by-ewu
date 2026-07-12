"""Future AI provider adapter placeholders.

Do not instantiate these until the provider packages and credentials are added.
Each real provider should implement the AIProvider protocol from ai_gateway.py.
"""

from ai.ai_gateway import AIRequest, AIResponse


class OpenAIProvider:
    name = "openai"

    def send(self, request: AIRequest) -> AIResponse:
        raise NotImplementedError("OpenAIProvider is a future adapter placeholder.")


class GeminiProvider:
    name = "gemini"

    def send(self, request: AIRequest) -> AIResponse:
        raise NotImplementedError("GeminiProvider is a future adapter placeholder.")


class ClaudeProvider:
    name = "claude"

    def send(self, request: AIRequest) -> AIResponse:
        raise NotImplementedError("ClaudeProvider is a future adapter placeholder.")


class LocalAIProvider:
    name = "local"

    def send(self, request: AIRequest) -> AIResponse:
        raise NotImplementedError("LocalAIProvider is a future adapter placeholder.")

