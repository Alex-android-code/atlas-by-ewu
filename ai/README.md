# ATLAS/EWU AI Gateway

AI Gateway is the provider-neutral boundary between ATLAS agents and future AI models.

Agents must call `AIGateway.send_message_to_ai()` instead of importing OpenAI, Gemini, Claude, or a local model directly.

## Current Provider

The project currently uses `MockAIProvider`.

It does not call any external AI service. It returns deterministic test responses with this structure:

```json
{
  "reply": "string",
  "action": "string or null",
  "confidence": 0.72,
  "handoff_required": false,
  "metadata": {}
}
```

## Request Data Sent To AI

The gateway receives:

- `user_id` - the user or entity owner.
- `agent_type` - candidate, employer, coordinator, matching, legal, or document.
- `context` - serializable agent context, including profile, memory, country config, and metadata when available.
- `message` - the latest user or system message.

## Adding A Real Provider

Create an adapter that implements:

```python
class ProviderName:
    name = "provider_name"

    def send(self, request: AIRequest) -> AIResponse:
        ...
```

Then register it:

```python
registry = AIProviderRegistry()
registry.register(MockAIProvider())
registry.register(OpenAIProvider(...))
gateway = AIGateway(registry, default_provider="openai")
```

Do not add logic like `if provider == "openai"` inside agents.

Use the registry/adapter pattern so ATLAS can support:

- `OpenAIProvider`
- `GeminiProvider`
- `ClaudeProvider`
- `LocalAIProvider`

## Expected ATLAS Response Format

Every provider must return `AIResponse` with:

- `reply`
- `action`
- `confidence`
- `handoff_required`
- `metadata`

This keeps agent behavior stable when providers change.

## Stability Rules

The gateway protects ATLAS from provider instability:

- provider errors are caught inside `AIGateway`;
- the configured fallback provider is used automatically;
- empty replies are replaced with safe replies;
- confidence is clamped between `0.0` and `1.0`;
- replies are capped to 4000 characters;
- every response receives `request_id`, `provider`, `latency_ms`, `fallback_used`, and `gateway` metadata.

Use `GET /api/ai/health` to inspect the active AI layer before and after connecting a real provider.

See `ai/CONTRACT.md` before adding OpenAI, Gemini, Claude, or a local provider.
