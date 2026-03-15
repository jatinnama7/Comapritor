"""
jobs.py
-------
Core warmup pipeline: fetch trending queries → batch-scrape → persist.

Env vars:
  WARMUP_QUERY_COUNT     - how many queries to fetch from the LLM (default: 100)
  WARMUP_BATCH_SIZE      - parallel scraping batch size (default: 5)
                           Keep this low to avoid hammering scrapers concurrently.
  WARMUP_SKIP_CACHED     - if "1", skip queries that already have a final result in Redis (default: 1)
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from typing import Any, List

logger = logging.getLogger(__name__)


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        val = int(raw)
        return val if val > 0 else default
    except Exception:
        return default


_QUERY_COUNT = _int_env("WARMUP_QUERY_COUNT", 100)
_BATCH_SIZE = _int_env("WARMUP_BATCH_SIZE", 5)
_SKIP_CACHED = os.getenv("WARMUP_SKIP_CACHED", "1") == "1"


async def _is_already_cached(q_norm: str, cache) -> bool:
    """Return True if a final result is already in Redis for this query."""
    if not _SKIP_CACHED:
        return False
    final_key = f"comparitor:search:final:{q_norm}"
    val = await cache.get_json(final_key)
    return isinstance(val, list) and len(val) > 0


async def _warmup_single_query(q: str, cache, mongo_collection: Any) -> str:
    """
    Run the full scraping pipeline for a single query and persist results.
    Returns "cached", "success", or "failed:<reason>".
    """
    # Import here to avoid circular import at module level
    from orchestrator import normalize_query, background_complete_and_persist  # noqa: E402

    q_norm = normalize_query(q)

    if await _is_already_cached(q_norm, cache):
        return "cached"

    from orchestrator import run_fast_scrapers_with_errors  # noqa: E402

    fast_ttl = int(os.getenv("REDIS_FAST_TTL_SECONDS", str(10 * 60)))
    final_ttl = int(os.getenv("REDIS_FINAL_TTL_SECONDS", str(24 * 60 * 60)))
    lock_ttl = int(os.getenv("REDIS_LOCK_TTL_SECONDS", str(10 * 60)))

    # Acquire lock — skip if another process is already doing this query
    lock_key = f"comparitor:search:lock:{q_norm}"
    got_lock = await cache.acquire_lock(lock_key, ttl_seconds=lock_ttl)
    if not got_lock:
        return "cached"  # treat as effectively handled

    try:
        fast_results, fast_errors = await run_fast_scrapers_with_errors(q)
        await cache.set_json(f"comparitor:search:fast:{q_norm}", fast_results, ttl_seconds=fast_ttl)
        await cache.set_status(f"comparitor:search:status:{q_norm}", "running_full", ttl_seconds=final_ttl)

        # Run background_complete_and_persist synchronously here
        # (we're already in a background scheduler job so we can await it directly)
        await background_complete_and_persist(
            q=q,
            cache=cache,
            mongo_collection=mongo_collection,
            fast_results=fast_results,
            fast_ttl_seconds=fast_ttl,
            final_ttl_seconds=final_ttl,
            lock_ttl_seconds=lock_ttl,
            lock_already_acquired=True,
        )
        return "success"
    except Exception as exc:
        return f"failed:{exc}"


async def run_warmup_job(cache, mongo_collection: Any) -> None:
    """
    Full warmup pipeline:
      1. Fetch top-N trending queries from LLM (with retry + static fallback)
      2. Scrape + persist them in batches
      3. Record metrics
    """
    from .idempotency import is_warmup_done_today, try_acquire_warmup_lock, mark_warmup_done, release_warmup_lock
    from .metrics import make_metrics, save_metrics
    from .trending_source import get_trending_queries

    logger.info("[warmup] Daily warmup job started.")

    # --- Idempotency: skip if already done today ---
    if await is_warmup_done_today(cache):
        logger.info("[warmup] Already completed today. Skipping.")
        return

    if not await try_acquire_warmup_lock(cache):
        logger.info("[warmup] Another warmup worker is running. Skipping.")
        return

    metrics = make_metrics()
    job_start = time.monotonic()

    try:
        # --- Step 1: Get trending queries ---
        queries = await get_trending_queries(count=_QUERY_COUNT)
        metrics.total_queries = len(queries)

        # Detect if static fallback was used (all queries match static list exactly)
        from .trending_source import _STATIC_FALLBACK as _static
        if set(queries) <= set(_static):
            metrics.used_static_fallback = True
            logger.warning("[warmup] Using static fallback list (%d queries).", len(queries))

        # --- Step 2: Process in batches ---
        for batch_start in range(0, len(queries), _BATCH_SIZE):
            batch = queries[batch_start: batch_start + _BATCH_SIZE]
            logger.info(
                "[warmup] Processing batch %d-%d of %d...",
                batch_start + 1, batch_start + len(batch), len(queries)
            )

            results = await asyncio.gather(
                *[_warmup_single_query(q, cache, mongo_collection) for q in batch],
                return_exceptions=True,
            )

            for q, result in zip(batch, results):
                if isinstance(result, Exception):
                    metrics.record_error(q, str(result))
                elif isinstance(result, str) and result.startswith("failed:"):
                    metrics.record_error(q, result[7:])
                elif result == "cached":
                    metrics.record_skipped()
                else:
                    metrics.record_success()

        # --- Step 3: Mark done & save metrics ---
        metrics.duration_seconds = round(time.monotonic() - job_start, 2)
        await mark_warmup_done(cache)
        await save_metrics(metrics, cache)

        logger.info(
            "[warmup] Done. success=%d skipped=%d failed=%d duration=%.1fs",
            metrics.succeeded, metrics.skipped_cached, metrics.failed, metrics.duration_seconds,
        )

    except Exception as exc:
        logger.exception("[warmup] Fatal error in warmup job: %s", exc)
        metrics.record_error("__job__", str(exc))
        metrics.duration_seconds = round(time.monotonic() - job_start, 2)
        await save_metrics(metrics, cache)
        await release_warmup_lock(cache)
