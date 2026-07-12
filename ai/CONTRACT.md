# ATLAS AI Contract

This contract keeps ATLAS stable when a real AI provider is connected.

## Boundary

Only `ai.ai_gateway.AIGateway` may call model providers.

Agents, API routes, CRM workflows, matching, document checks and public UI must not import OpenAI, Gemini, Claude or local model clients directly.

## Provider Input

Every provider receives an `AIRequest`:

- `request_id`
- `user_id`
- `agent_type`
- `context`
- `message`

The provider may use context to produce text, extraction or reasoning, but it must not mutate ATLAS memory, CRM, files or database records directly.

## Provider Output

Every provider must return `AIResponse` or a compatible dictionary:

```json
{
  "reply": "string",
  "action": "string or null",
  "confidence": 0.0,
  "handoff_required": false,
  "metadata": {}
}
```

The gateway normalizes this response:

- empty replies become safe fallback replies;
- confidence is clamped between `0.0` and `1.0`;
- replies are capped to 4000 characters;
- metadata receives `provider`, `request_id`, `latency_ms`, `fallback_used` and `gateway`.

## Failure Rule

Provider failure must never break public chat.

If the selected provider fails, the gateway calls the configured fallback provider. If fallback also fails, the gateway returns a safe handoff response.

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

1. Implement `send(request: AIRequest) -> AIResponse`.
2. Implement `health() -> dict`.
3. Register the provider in `get_default_ai_gateway()` or an application factory.
4. Keep provider credentials in environment variables.
5. Run `GET /api/ai/health`.
6. Run a candidate chat smoke test.
7. Run an employer chat smoke test.
8. Confirm fallback by temporarily forcing the provider to fail.
