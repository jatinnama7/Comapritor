import asyncio
import json
import os
import sys
import urllib.parse
from contextlib import asynccontextmanager
from datetime import datetime
from datetime import timedelta
import time
from typing import List, Callable, Awaitable, Any, Optional

from fastapi import FastAPI, Query, HTTPException, BackgroundTasks, Header
from pymongo import MongoClient
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# --- 1. IMPORT YOUR EXISTING MODULES ---
from amazon_scraper import scrape_amazon
from flipkart_scraper import scrape_flipkart
from jiomart_scraper import scrape_jiomart
from meesho_scraper import scrape_meesho
from croma_scraper import scrape_croma
from myntra_scraper import scrape_myntra

from cache import RedisCache
from orchestrator import (
    background_complete_and_persist,
    get_cached_results,
    get_cached_results_robust,
    normalize_query,
    register_query_in_index,
    run_fast_scrapers,
    run_fast_scrapers_with_errors,
)

load_dotenv()

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

cache = RedisCache()

_ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "")

# --- 2. MONGODB ATLAS SETUP ---
MONGO_URI = os.getenv("MONGODB_URI")
_mongo_client = MongoClient(MONGO_URI)
_mongo_db = _mongo_client["comparitor_db"]
collection = _mongo_db["products"]


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Start the daily warmup scheduler on startup; stop it on shutdown."""
    try:
        from scheduler import start_scheduler
        start_scheduler(cache=cache, mongo_collection=collection)
    except Exception as _e:
        print(f"⚠️  Scheduler failed to start: {_e}")
    yield
    try:
        from scheduler import stop_scheduler
        stop_scheduler()
    except Exception:
        pass


app = FastAPI(title="Comparitor Aggregator", lifespan=_lifespan)


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        val = int(raw)
        return val if val > 0 else default
    except Exception:
        return default


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        val = float(raw)
        return val if val > 0 else default
    except Exception:
        return default


FAST_TTL_SECONDS = _int_env("REDIS_FAST_TTL_SECONDS", 10 * 60)
FINAL_TTL_SECONDS = _int_env("REDIS_FINAL_TTL_SECONDS", 24 * 60 * 60)
LOCK_TTL_SECONDS = _int_env("REDIS_LOCK_TTL_SECONDS", 10 * 60)

SCRAPER_RETRY_MAX_ATTEMPTS = _int_env("SCRAPER_RETRY_MAX_ATTEMPTS", 3)
SCRAPER_RETRY_BASE_DELAY_SECONDS = _float_env("SCRAPER_RETRY_BASE_DELAY_SECONDS", 1.0)
SCRAPER_RETRY_MAX_DELAY_SECONDS = _float_env("SCRAPER_RETRY_MAX_DELAY_SECONDS", 10.0)


def _is_retryable_error(err: Exception) -> bool:
    msg = str(err).lower()
    # Don't retry config mistakes
    if "missing" in msg and "key" in msg:
        return False
    if "invalid api key" in msg:
        return False

    retry_markers = [
        "timeout",
        "timed out",
        "rate limit",
        "too many requests",
        "429",
        "quota",
        "insufficient_quota",
        "connection reset",
        "connection aborted",
        "network",
        "502",
        "503",
        "504",
        "gateway",
        "server error",
    ]
    return any(m in msg for m in retry_markers)


async def _run_with_retries(
    *,
    site_name: str,
    fn: Callable[[], Awaitable[Any]],
    retry_on_empty: bool = False,
) -> List[dict]:
    last_err: Optional[Exception] = None
    for attempt in range(1, SCRAPER_RETRY_MAX_ATTEMPTS + 1):
        try:
            res = await fn()
            if not isinstance(res, list):
                raise RuntimeError(f"{site_name} returned {type(res).__name__} (expected list)")
            # By default: do NOT treat 0 items as an error (could be a genuine no-results query)
            if retry_on_empty and len(res) == 0:
                raise RuntimeError(f"{site_name} returned 0 items")
            return res
        except Exception as e:
            last_err = e

            # Only retry on genuine transient errors (timeouts/429/quota/network)
            if not _is_retryable_error(e):
                break

            if attempt >= SCRAPER_RETRY_MAX_ATTEMPTS:
                break

            delay = min(
                SCRAPER_RETRY_MAX_DELAY_SECONDS,
                SCRAPER_RETRY_BASE_DELAY_SECONDS * (2 ** (attempt - 1)),
            )
            print(f"⚠️ {site_name} retry {attempt}/{SCRAPER_RETRY_MAX_ATTEMPTS} after error: {e}")
            await asyncio.sleep(delay)

    raise RuntimeError(f"{site_name} failed after {attempt} attempts: {last_err}")


def _bucket_dir() -> str:
    now = datetime.now()
    bucket = now.replace(minute=(now.minute // 5) * 5, second=0, microsecond=0)
    return os.path.join("results", bucket.strftime("%Y%m%d_%H%M"))


@app.get("/search")
async def search_and_aggregate(q: str = Query(..., description="Product to search")):
    start_time = time.perf_counter()
    print(f"📡 Starting parallel search for: {q}")

    tasks = [
        ("Amazon", _run_with_retries(site_name="Amazon", fn=lambda: scrape_amazon(q))),
        ("Flipkart", _run_with_retries(site_name="Flipkart", fn=lambda: scrape_flipkart(q))),
        ("JioMart", _run_with_retries(site_name="JioMart", fn=lambda: scrape_jiomart(q))),
        ("Meesho", _run_with_retries(site_name="Meesho", fn=lambda: scrape_meesho(q))),
        ("Croma", _run_with_retries(site_name="Croma", fn=lambda: scrape_croma(q))),
        ("Myntra", _run_with_retries(site_name="Myntra", fn=lambda: scrape_myntra(q))),
    ]

    results_batches = await asyncio.gather(
        *[t[1] for t in tasks],
        return_exceptions=True,
    )

    failures = {}
    for (site_name, _), batch in zip(tasks, results_batches):
        if isinstance(batch, Exception):
            failures[site_name] = str(batch)

    # Less strict: return partial results if possible, but include per-site errors
    if failures:
        print(f"⚠️ Some scrapers failed (returning partial results): {failures}")

    # --- 3. FLATTEN EVERYTHING CAREFULLY ---
    all_products = []
    for i, batch in enumerate(results_batches):
        if isinstance(batch, list):
            limited = batch[:10]
            print(f"📦 Batch {i} returned {len(limited)} items")
            all_products.extend(limited)
        else:
            print(f"⚠️ Batch {i} failed or returned no list: {batch}")

    if not all_products:
        # If everything failed, surface the failures (otherwise it's ambiguous)
        if failures:
            raise HTTPException(
                status_code=502,
                detail={
                    "message": "No results returned (all scrapers failed or returned empty).",
                    "failures": failures,
                },
            )
        return {"status": "no_results", "data": []}

    # --- 4. SAVE TO SINGLE JSON FILE (TOTAL DATA) ---
    out_dir = _bucket_dir()
    os.makedirs(out_dir, exist_ok=True)
    filename = f"aggregated_{q.replace(' ', '_')}.json"
    out_path = os.path.join(out_dir, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=4)
    print(f"📁 Local JSON saved: {out_path} with {len(all_products)} items.")

    # --- 5. PREPARE & UPLOAD TO MONGODB ---
    # Create a deep copy for MongoDB to avoid modifying the original list prematurely
    enriched_data = []
    for item in all_products:
        # Create a new dict for each item to ensure no shared references
        new_item = item.copy() 
        new_item["search_query"] = q
        new_item["created_at"] = datetime.utcnow().isoformat()
        enriched_data.append(new_item)

    try:
        if enriched_data:
            # PUSH TOTAL DATA
            collection.insert_many(enriched_data)
            print(f"💾 Successfully uploaded {len(enriched_data)} total items to MongoDB Atlas.")
            
            # Remove the ObjectId before returning to FastAPI
            for item in enriched_data:
                item.pop('_id', None)
    except Exception as e:
        print(f"⚠️ MongoDB Upload Failed: {e}")

    elapsed = time.perf_counter() - start_time
    return {
        "status": "success" if not failures else "partial_success",
        "total_results": len(enriched_data),
        "file_saved": filename,
        "elapsed_seconds": round(elapsed, 3),
        "results": enriched_data,
        "site_errors": failures,
    }

@app.get("/search_fast")
async def search_fast(
    background_tasks: BackgroundTasks,
    q: str = Query(..., description="Product to search"),
):
    start_time = time.perf_counter()
    q_norm = normalize_query(q)

    # --- Robust cache lookup (tries variant forms before going to scrapers) ---
    cached = await get_cached_results_robust(q=q, cache=cache)
    if cached.get("stage") == "final" and isinstance(cached.get("results"), list):
        elapsed = time.perf_counter() - start_time
        return {
            "status": "success",
            "mode": "final_cache",
            "query": q,
            "query_normalized": q_norm,
            "matched_variant": cached.get("matched_variant"),
            "total_results": len(cached["results"]),
            "elapsed_seconds": round(elapsed, 3),
            "results": cached["results"],
        }

    if cached.get("stage") == "fast" and isinstance(cached.get("results"), list):
        # Fast cache hit means a scraping pipeline is already running from the original
        # request that populated this key. Never re-launch background here — doing so
        # causes duplicate scraping every time the same (or variant) query is repeated
        # within the fast-cache TTL window.
        elapsed = time.perf_counter() - start_time
        return {
            "status": "partial",
            "mode": "fast_cache",
            "query": q,
            "query_normalized": q_norm,
            "matched_variant": cached.get("matched_variant"),
            "total_results": len(cached["results"]),
            "elapsed_seconds": round(elapsed, 3),
            "results": cached["results"],
        }

    # --- Concurrency hardening: acquire the lock HERE (before touching scrapers) ---
    # If another request is already scraping the same query, return 202 immediately
    # instead of launching a duplicate scraping run.
    lock_key = f"comparitor:search:lock:{q_norm}"
    got_lock = await cache.acquire_lock(lock_key, ttl_seconds=LOCK_TTL_SECONDS)
    if not got_lock:
        # Another worker is already running; tell the caller to poll /search_status
        return {
            "status": "processing",
            "mode": "locked",
            "query": q,
            "query_normalized": q_norm,
            "message": "A scraping run for this query is already in progress. Poll /search_status for updates.",
            "retry_after": 5,
        }

    # We hold the lock — proceed with fast scrapers
    await cache.set_status(
        f"comparitor:search:status:{q_norm}",
        "running_fast",
        ttl_seconds=FAST_TTL_SECONDS,
    )
    fast_results, fast_errors = await run_fast_scrapers_with_errors(q)

    # Only fail the endpoint if we literally got nothing from the fast phase
    if not fast_results and fast_errors:
        await cache.set_status(
            f"comparitor:search:status:{q_norm}",
            "failed",
            ttl_seconds=FAST_TTL_SECONDS,
        )
        raise HTTPException(
            status_code=502,
            detail={"message": "Fast scrapers returned no results.", "failures": fast_errors},
        )

    await cache.set_json(
        f"comparitor:search:fast:{q_norm}",
        fast_results,
        ttl_seconds=FAST_TTL_SECONDS,
    )
    await cache.set_status(
        f"comparitor:search:status:{q_norm}",
        "running_full",
        ttl_seconds=FINAL_TTL_SECONDS,
    )

    # Continue in background: run LLM scrapers, merge, write JSON, save to Atlas, cache final.
    # Pass lock_already_acquired=True so the background task skips re-acquiring the lock.
    background_tasks.add_task(
        background_complete_and_persist,
        q=q,
        cache=cache,
        mongo_collection=collection,
        fast_results=fast_results,
        fast_ttl_seconds=FAST_TTL_SECONDS,
        final_ttl_seconds=FINAL_TTL_SECONDS,
        lock_ttl_seconds=LOCK_TTL_SECONDS,
        lock_already_acquired=True,
    )

    elapsed = time.perf_counter() - start_time
    return {
        "status": "partial",
        "mode": "fast_fresh",
        "query": q,
        "query_normalized": q_norm,
        "total_results": len(fast_results),
        "elapsed_seconds": round(elapsed, 3),
        "results": fast_results,
        "site_errors": fast_errors,
    }


@app.get("/search_final")
async def search_final(q: str = Query(..., description="Product to search")):
    q_norm = normalize_query(q)
    final_key = f"comparitor:search:final:{q_norm}"

    cached_final = await cache.get_json(final_key)
    if isinstance(cached_final, list):
        return {
            "status": "success",
            "mode": "final_cache",
            "query": q,
            "query_normalized": q_norm,
            "total_results": len(cached_final),
            "results": cached_final,
        }

    # Fallback to MongoDB: fetch the most recent saved run for this query
    latest = collection.find_one({"search_query": q}, sort=[("created_at", -1)])
    if not latest:
        return {
            "status": "not_found",
            "mode": "mongo_empty",
            "query": q,
            "query_normalized": q_norm,
            "total_results": 0,
            "results": [],
        }

    run_id = latest.get("run_id")
    results = []

    if run_id:
        cursor = collection.find({"search_query": q, "run_id": run_id}, {"_id": 0})
        results = list(cursor)
    else:
        # Backward compatibility with older inserts that didn't include run_id
        created_at = latest.get("created_at")
        if created_at:
            cursor = collection.find({"search_query": q, "created_at": created_at}, {"_id": 0})
            results = list(cursor)

            # If timestamps were unique per item, broaden to a small time window
            if len(results) < 3:
                try:
                    dt = datetime.fromisoformat(created_at)
                    start = (dt - timedelta(seconds=2)).isoformat()
                    end = (dt + timedelta(seconds=2)).isoformat()
                    cursor = collection.find(
                        {"search_query": q, "created_at": {"$gte": start, "$lte": end}},
                        {"_id": 0},
                    )
                    results = list(cursor)
                except Exception:
                    pass

    if results:
        # Best-effort: populate Redis final cache for subsequent calls
        await cache.set_json(final_key, results, ttl_seconds=FINAL_TTL_SECONDS)

    return {
        "status": "success" if results else "not_found",
        "mode": "mongo",
        "query": q,
        "query_normalized": q_norm,
        "total_results": len(results),
        "results": results,
    }


@app.get("/search_status")
async def search_status(q: str = Query(..., description="Product to search")):
    q_norm = normalize_query(q)
    status_key = f"comparitor:search:status:{q_norm}"
    fast_key = f"comparitor:search:fast:{q_norm}"
    final_key = f"comparitor:search:final:{q_norm}"

    # Redis-only status check; best-effort if Redis isn't available
    status_val = await cache.get_str(status_key)
    has_fast = isinstance(await cache.get_json(fast_key), list)
    has_final = isinstance(await cache.get_json(final_key), list)

    effective_status = status_val or "none"
    if has_final:
        effective_status = "complete"
    elif has_fast and effective_status == "none":
        effective_status = "running_full"

    return {
        "query": q,
        "query_normalized": q_norm,
        "status": effective_status,
        "has_fast": has_fast,
        "has_final": has_final,
    }


def _require_admin_key(x_admin_key: str = Header(default="")) -> None:
    """Dependency: reject requests that don't carry the correct X-Admin-Key header."""
    if not _ADMIN_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="Admin endpoints are disabled. Set ADMIN_API_KEY in your environment.",
        )
    if x_admin_key != _ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Forbidden: invalid admin key.")


@app.post("/admin/warmup/trigger")
async def admin_trigger_warmup(
    background_tasks: BackgroundTasks,
    x_admin_key: str = Header(default=""),
):
    """Manually trigger the warmup job in the background (admin only)."""
    _require_admin_key(x_admin_key)

    from scheduler.jobs import run_warmup_job
    background_tasks.add_task(run_warmup_job, cache=cache, mongo_collection=collection)
    return {"status": "triggered", "message": "Warmup job started in background."}


@app.get("/admin/warmup/status")
async def admin_warmup_status(x_admin_key: str = Header(default="")):
    """Return the last warmup run's metrics and scheduler state (admin only)."""
    _require_admin_key(x_admin_key)

    from scheduler.metrics import get_last_run_metrics
    from scheduler.background import get_scheduler_info
    from scheduler.idempotency import is_warmup_done_today

    metrics = await get_last_run_metrics(cache)
    done_today = await is_warmup_done_today(cache)
    scheduler_info = get_scheduler_info()

    return {
        "done_today": done_today,
        "scheduler": scheduler_info,
        "last_run": metrics,
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Comparitor Aggregator is running on http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)