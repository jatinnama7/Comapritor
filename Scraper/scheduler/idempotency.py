"""
idempotency.py
--------------
Day-level Redis lock for the warmup job so it runs at most once per calendar day
(IST timezone). Stale locks older than WARMUP_LOCK_STALE_MINUTES are automatically
removed so a crashed run doesn't block the next day's job.
"""

from __future__ import annotations

import logging
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

_IST = timezone(timedelta(hours=5, minutes=30))
_INDEX_KEY = "comparitor:search:index"

# How long before a locked warmup is considered stale (a previous run crashed)
_STALE_MINUTES = int(os.getenv("WARMUP_LOCK_STALE_MINUTES", "30"))
_LOCK_TTL_SECONDS = (_STALE_MINUTES + 1) * 60  # slightly longer than stale window


def _today_ist() -> str:
    return datetime.now(_IST).strftime("%Y-%m-%d")


def _lock_key(day: Optional[str] = None) -> str:
    return f"comparitor:warmup:lock:{day or _today_ist()}"


def _done_key(day: Optional[str] = None) -> str:
    return f"comparitor:warmup:done:{day or _today_ist()}"


async def is_warmup_done_today(cache) -> bool:
    """Return True if the warmup job has already completed successfully today."""
    client = await cache._get_client()
    if client is None:
        return False
    try:
        val = await client.get(_done_key())
        return val == "1"
    except Exception:
        return False


async def try_acquire_warmup_lock(cache) -> bool:
    """
    Try to acquire today's warmup lock.
    Returns True if acquired (we should proceed), False if another worker holds it.
    Also cleans up stale locks from crashed previous runs.
    """
    client = await cache._get_client()
    if client is None:
        # Redis unavailable: allow run (no coordination possible)
        return True

    key = _lock_key()
    try:
        # Check if a lock exists but is stale
        lock_val = await client.get(key)
        if lock_val is not None:
            try:
                locked_at = float(lock_val)
                age_minutes = (time.time() - locked_at) / 60
                if age_minutes > _STALE_MINUTES:
                    logger.warning("[warmup] Stale lock detected (%.1f min old). Deleting.", age_minutes)
                    await client.delete(key)
                else:
                    return False  # Legitimate active lock
            except (ValueError, TypeError):
                # Unexpected value — delete and re-acquire
                await client.delete(key)

        acquired = bool(await client.set(key, str(time.time()), nx=True, ex=_LOCK_TTL_SECONDS))
        return acquired
    except Exception as exc:
        logger.warning("[warmup] Lock acquisition error (proceeding): %s", exc)
        return True


async def mark_warmup_done(cache) -> None:
    """Mark today's warmup as complete. Persists for 25 hours to survive midnight edge cases."""
    client = await cache._get_client()
    if client is None:
        return
    try:
        await client.set(_done_key(), "1", ex=25 * 3600)
        await client.delete(_lock_key())
    except Exception:
        pass


async def release_warmup_lock(cache) -> None:
    """Release the warmup lock without marking it done (used on failure so next day retries)."""
    client = await cache._get_client()
    if client is None:
        return
    try:
        await client.delete(_lock_key())
    except Exception:
        pass
