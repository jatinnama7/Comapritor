"""
metrics.py
----------
Lightweight structured logging for each warmup run.
Writes a JSON summary to Scraper/scheduler/logs/ and also stores
the latest summary in Redis for the /admin/warmup/status endpoint.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_IST = timezone(timedelta(hours=5, minutes=30))
_METRICS_REDIS_KEY = "comparitor:warmup:last_run"
_LOG_DIR = Path(__file__).parent / "logs"


@dataclass
class WarmupMetrics:
    run_date: str = ""                    # YYYY-MM-DD in IST
    started_at: str = ""                  # ISO timestamp
    finished_at: str = ""
    total_queries: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped_cached: int = 0
    errors: List[Dict] = field(default_factory=list)
    llm_provider_used: str = ""
    used_static_fallback: bool = False
    duration_seconds: float = 0.0

    def record_error(self, query: str, error: str) -> None:
        self.failed += 1
        self.errors.append({"query": query, "error": error})

    def record_success(self) -> None:
        self.succeeded += 1

    def record_skipped(self) -> None:
        self.skipped_cached += 1

    def to_dict(self) -> dict:
        return asdict(self)


def _now_ist() -> str:
    return datetime.now(_IST).isoformat()


def make_metrics(run_date: Optional[str] = None) -> WarmupMetrics:
    from .idempotency import _today_ist
    return WarmupMetrics(
        run_date=run_date or _today_ist(),
        started_at=_now_ist(),
    )


async def save_metrics(metrics: WarmupMetrics, cache) -> None:
    """Write metrics to Redis (for /admin/warmup/status) and to a local JSON log file."""
    metrics.finished_at = _now_ist()
    data = metrics.to_dict()

    # --- Redis ---
    client = await cache._get_client()
    if client is not None:
        try:
            await client.set(_METRICS_REDIS_KEY, json.dumps(data), ex=48 * 3600)
        except Exception as exc:
            logger.warning("[warmup] Failed to write metrics to Redis: %s", exc)

    # --- Local file ---
    try:
        _LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_path = _LOG_DIR / f"warmup_{metrics.run_date}.json"
        with open(log_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2)
        logger.info("[warmup] Metrics saved to %s", log_path)
    except Exception as exc:
        logger.warning("[warmup] Failed to write metrics log file: %s", exc)


async def get_last_run_metrics(cache) -> Optional[dict]:
    """Retrieve the last warmup run summary from Redis."""
    client = await cache._get_client()
    if client is None:
        return None
    try:
        raw = await client.get(_METRICS_REDIS_KEY)
        if raw:
            return json.loads(raw)
    except Exception:
        pass
    return None
