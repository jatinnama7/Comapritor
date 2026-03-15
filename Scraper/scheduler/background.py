"""
background.py
-------------
APScheduler lifecycle management for the daily warmup cron job.

Env vars:
    SCHEDULER_RUN_HOUR    - Local hour in scheduler timezone (default: 2)
    SCHEDULER_RUN_MINUTE  - Local minute in scheduler timezone (default: 0)
    SCHEDULER_TIMEZONE    - IANA timezone string (default: "Asia/Kolkata")
  SCHEDULER_ENABLED     - set to "0" to disable the scheduler (default: "1")
"""

from __future__ import annotations

import logging
import os
from typing import Any, Optional

logger = logging.getLogger(__name__)


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        return int(raw)
    except Exception:
        return default


_RUN_HOUR = _int_env("SCHEDULER_RUN_HOUR", 2)
_RUN_MINUTE = _int_env("SCHEDULER_RUN_MINUTE", 0)
_TIMEZONE = os.getenv("SCHEDULER_TIMEZONE", "Asia/Kolkata")
_ENABLED = os.getenv("SCHEDULER_ENABLED", "1") == "1"

_scheduler: Optional[Any] = None


def start_scheduler(cache: Any, mongo_collection: Any) -> None:
    """Start the APScheduler background scheduler. Call once at app startup."""
    global _scheduler

    if not _ENABLED:
        logger.info("[scheduler] Warmup scheduler is disabled (SCHEDULER_ENABLED=0).")
        return

    try:
        from apscheduler.schedulers.asyncio import AsyncIOScheduler  # type: ignore
        from apscheduler.triggers.cron import CronTrigger  # type: ignore
    except ImportError:
        logger.warning(
            "[scheduler] apscheduler not installed — daily warmup job will not run. "
            "Install it with: pip install 'apscheduler>=3.10.0'"
        )
        return

    from .jobs import run_warmup_job

    _scheduler = AsyncIOScheduler()

    async def _job_wrapper() -> None:
        await run_warmup_job(cache=cache, mongo_collection=mongo_collection)

    _scheduler.add_job(
        _job_wrapper,
        trigger=CronTrigger(hour=_RUN_HOUR, minute=_RUN_MINUTE, timezone=_TIMEZONE),
        id="daily_warmup",
        name="Daily product warmup",
        max_instances=1,
        coalesce=True,
        replace_existing=True,
        misfire_grace_time=3600,  # tolerate up to 1h delay (e.g. app restart)
    )

    _scheduler.start()
    logger.info(
        "[scheduler] Daily warmup scheduler started. Fires daily at %02d:%02d (%s).",
        _RUN_HOUR,
        _RUN_MINUTE,
        _TIMEZONE,
    )


def stop_scheduler() -> None:
    """Gracefully stop the scheduler. Call at app shutdown."""
    global _scheduler
    if _scheduler is not None:
        try:
            _scheduler.shutdown(wait=False)
            logger.info("[scheduler] Scheduler stopped.")
        except Exception as exc:
            logger.warning("[scheduler] Error stopping scheduler: %s", exc)
        finally:
            _scheduler = None


def get_scheduler_info() -> dict:
    """Return current scheduler state for the status endpoint."""
    if _scheduler is None:
        return {"running": False, "enabled": _ENABLED}

    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": str(job.next_run_time) if job.next_run_time else None,
        })

    return {
        "running": _scheduler.running,
        "enabled": _ENABLED,
        "run_time": f"{_RUN_HOUR:02d}:{_RUN_MINUTE:02d}",
        "timezone": _TIMEZONE,
        "jobs": jobs,
    }
