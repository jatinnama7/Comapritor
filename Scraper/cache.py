import json
import logging
import os
import time
from urllib.parse import urlsplit, urlunsplit
from typing import Any, Optional

try:
    import redis.asyncio as redis  # type: ignore
except Exception:  # pragma: no cover
    redis = None  # type: ignore


_DEFAULT_REDIS_URL = "redis://localhost:6379/0"


def _safe_redis_url(url: str) -> str:
    try:
        parts = urlsplit(url)
        if "@" not in parts.netloc:
            return url
        auth, host = parts.netloc.rsplit("@", 1)
        if ":" in auth:
            user, _pwd = auth.split(":", 1)
            safe_auth = f"{user}:***"
        else:
            safe_auth = "***"
        return urlunsplit((parts.scheme, f"{safe_auth}@{host}", parts.path, parts.query, parts.fragment))
    except Exception:
        return "redis://***"


class RedisCache:
    def __init__(self, url: Optional[str] = None):
        self._url = url or os.getenv("REDIS_URL") or _DEFAULT_REDIS_URL
        self._client = None
        self._available: Optional[bool] = None
        self._last_ping_at: float = 0.0
        self._recheck_seconds: float = 5.0
        self._logger = logging.getLogger("comparitor.cache")
        self._safe_url = _safe_redis_url(self._url)

    async def _get_client(self):
        if redis is None:
            if self._available is not False:
                self._logger.warning("redis_client=unavailable reason=redis_package_missing")
            self._available = False
            return None

        if self._client is None:
            self._client = redis.from_url(self._url, encoding="utf-8", decode_responses=True)

        now = time.monotonic()
        should_ping = (
            self._available is None
            or self._available is True
            or (now - self._last_ping_at) >= self._recheck_seconds
        )

        if should_ping:
            try:
                await self._client.ping()
                was_available = self._available
                self._available = True
                self._last_ping_at = now
                if was_available is not True:
                    self._logger.info("redis_client=connected url=%s", self._safe_url)
            except Exception as exc:
                was_available = self._available
                self._available = False
                self._last_ping_at = now
                if was_available is not False:
                    self._logger.warning("redis_client=unreachable url=%s error=%s", self._safe_url, exc)

        return self._client if self._available else None

    async def health_check(self) -> dict:
        """Return a lightweight Redis connectivity status for startup diagnostics."""
        client = await self._get_client()
        if client is None:
            return {"available": False, "url": self._safe_url, "error": "redis_unavailable"}

        try:
            await client.ping()
            return {"available": True, "url": self._safe_url}
        except Exception as exc:
            self._available = False
            return {"available": False, "url": self._safe_url, "error": str(exc)}

    async def get_json(self, key: str) -> Optional[Any]:
        client = await self._get_client()
        if client is None:
            return None

        try:
            raw = await client.get(key)
            if raw is None:
                return None
            return json.loads(raw)
        except Exception:
            return None

    async def get_str(self, key: str) -> Optional[str]:
        client = await self._get_client()
        if client is None:
            return None

        try:
            return await client.get(key)
        except Exception:
            return None

    async def set_json(self, key: str, value: Any, ttl_seconds: int) -> bool:
        client = await self._get_client()
        if client is None:
            return False

        try:
            await client.set(key, json.dumps(value), ex=ttl_seconds)
            return True
        except Exception:
            return False

    async def set_status(self, key: str, status: str, ttl_seconds: int) -> bool:
        client = await self._get_client()
        if client is None:
            return False

        try:
            await client.set(key, status, ex=ttl_seconds)
            return True
        except Exception:
            return False

    async def acquire_lock(self, key: str, ttl_seconds: int) -> bool:
        client = await self._get_client()
        if client is None:
            return True  # if Redis is unavailable, don't block execution

        try:
            # SET NX with expiry (simple distributed lock)
            return bool(await client.set(key, "1", nx=True, ex=ttl_seconds))
        except Exception:
            return True

    async def register_query(self, q_norm: str, index_key: str = "comparitor:search:index", max_entries: int = 10_000) -> None:
        """Add a normalized query to the sorted-set index (score = unix timestamp)."""
        client = await self._get_client()
        if client is None:
            return
        try:
            import time as _time
            score = _time.time()
            await client.zadd(index_key, {q_norm: score})
            # Trim to the most recent max_entries to keep memory bounded
            await client.zremrangebyrank(index_key, 0, -(max_entries + 1))
        except Exception:
            pass

    async def get_all_indexed_queries(self, index_key: str = "comparitor:search:index") -> list:
        """Return all normalized queries stored in the index (newest first)."""
        client = await self._get_client()
        if client is None:
            return []
        try:
            return await client.zrevrangebyscore(index_key, "+inf", "-inf")
        except Exception:
            return []
