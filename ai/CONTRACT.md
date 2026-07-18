# ATLAS AI Contract

This contract keeps ATLAS stable when a real AI provider is connected.

## Boundary

Only `ai.ai_gateway.MultiModelGateway` / `AIGateway` may call model providers.

Agents, API routes, CRM workflows, matching, document checks and public UI must not import OpenAI, Gemini, Claude or local model clients directly.

## Provider Input

Every provider receives separated system, context and user-message inputs:

```python
async def call_model(
    *,
    system_prompt: str,
    user_message: str,
    context: dict[str, Any],
    role: str,
    estimated_tokens: int,
) -> ModelResult:
    ...
```

The provider may use context to produce text, extraction or reasoning, but it must not mutate ATLAS memory, CRM, files or database records directly.
The user message must be sent as user content, never as a system instruction.

## Provider Output

Every provider must return `ModelResult`:

```python
ModelResult(
    content="string",
    provider="openai",
    model="configured-model",
    input_tokens=None,
    output_tokens=None,
    estimated_cost=None,
    latency_ms=0,
    cached=False,
)
```

The gateway returns a standardized agent response and keeps a legacy `AIResponse` wrapper for existing synchronous callers.

- empty provider replies become safe template replies;
- content is capped to 4000 characters;
- usage receives provider, model, request id, latency, token usage and fallback status;
- exact cache keys include tenant id, user id, role, language, country, profile version, prompt version, router version and model.

## Failure Rule

Provider failure must never break public chat.

If the selected provider fails, the gateway follows `RoutingDecision.fallback_order` and stops after the configured retry limit. If fallback also fails, the gateway returns a safe template response.

## Public Chat Rule

Public chat responses must remain human, calm and simple.

The API layer validates the one-question rule before showing AI-generated public replies. Providers should still follow it by design.

## Role Tone Rule

Providers receive `context.tone_profile` and must follow it.

For `candidate`, speak to the worker like a reliable friend and practical helper: warm, simple, supportive and direct.

For `employer`, speak to the employer like a business partner: professional, concise, precise and commercially useful.

The provider must not expose internal scoring, CRM labels, risk labels or extraction terms in public chat.

## Real Provider Checklist

Before switching `ATLAS_AI_PROVIDER` to a real provider:

1. Implement `call_model(...) -> ModelResult`.
2. Implement `health() -> dict`.
3. Register the provider in `get_default_ai_gateway()` or an application factory.
4. Keep provider credentials in environment variables.
5. Run `GET /api/ai/health`.
6. Run a candidate chat smoke test.
7. Run an employer chat smoke test.
8. Confirm fallback by temporarily forcing the provider to fail.
