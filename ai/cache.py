"""Exact and semantic cache interfaces for ATLAS AI calls."""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from typing import Protocol

from ai.models import PROMPT_VERSION, ROUTER_VERSION


class CacheStore(Protocol):
    async def get(self, key: str) -> str | None:
        ...

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        ...


class SemanticCacheStore(Protocol):
    async def search(self, payload: dict, threshold: float) -> str | None:
        ...

    async def set_embedding(self, payload: dict, value: str, ttl_seconds: int) -> None:
        ...


@dataclass
class _CacheItem:
    value: str
    expires_at: float


class MemoryTTLCache:
    """Small TTL cache for tests and single-process deployments."""

    def __init__(self) -> None:
        self._items: dict[str, _CacheItem] = {}

    async def get(self, key: str) -> str | None:
        item = self._items.get(key)
        if item is None:
            return None
        if item.expires_at <= time.time():
            self._items.pop(key, None)
            return None
        return item.value

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        self._items[key] = _CacheItem(value=value, expires_at=time.time() + max(1, ttl_seconds))


class RedisTTLCache:
    """Adapter for Redis-like async clients with get/setex methods."""

    def __init__(self, client) -> None:
        self.client = client

    async def get(self, key: str) -> str | None:
        value = await self.client.get(key)
        if isinstance(value, bytes):
            return value.decode("utf-8")
        return value

    async def set(self, key: str, value: str, ttl_seconds: int) -> None:
        await self.client.setex(key, ttl_seconds, value)


def normalize_message(message: str) -> str:
    return " ".join(str(message or "").strip().lower().split())


def build_exact_cache_key(
    *,
    tenant_id: str,
    user_id: str,
    role: str,
    language: str,
    country: str | None,
    message: str,
    profile_version: str | int | None,
    model: str,
    prompt_version: str = PROMPT_VERSION,
    router_version: str = ROUTER_VERSION,
) -> str:
    payload = {
        "tenant_id": tenant_id,
        "user_id": user_id,
        "role": role,
        "language": language,
        "country": country,
        "message": normalize_message(message),
        "profile_version": str(profile_version or "0"),
        "prompt_version": prompt_version,
        "router_version": router_version,
        "model": model,
    }
    serialized = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "atlas:ai:exact:" + hashlib.sha256(serialized.encode("utf-8")).hexdigest()


SEMANTIC_CACHE_FORBIDDEN_TASKS = {
    "legal_sensitive",
    "profile_extraction",
    "document_analysis",
    "matching_final",
}
