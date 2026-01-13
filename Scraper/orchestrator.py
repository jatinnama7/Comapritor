import asyncio
import json
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from typing import Any as _Any

from amazon_scraper import scrape_amazon
from croma_scraper import scrape_croma
from flipkart_scraper import scrape_flipkart
from jiomart_scraper import scrape_jiomart
from meesho_scraper import scrape_meesho
from myntra_scraper import scrape_myntra

from cache import RedisCache


def normalize_query(q: str) -> str:
    return " ".join((q or "").strip().split()).lower()


def _bucket_dir() -> str:
    now = datetime.now()
    bucket = now.replace(minute=(now.minute // 5) * 5, second=0, microsecond=0)
    return os.path.join("results", bucket.strftime("%Y%m%d_%H%M"))


def _merge_batches(batches: List[Any], per_batch_limit: int = 10) -> List[Dict[str, Any]]:
    merged: List[Dict[str, Any]] = []
    for batch in batches:
        if isinstance(batch, list):
            merged.extend(batch[:per_batch_limit])
    return merged


def _enrich_for_mongo(items: List[Dict[str, Any]], q: str) -> List[Dict[str, Any]]:
    enriched: List[Dict[str, Any]] = []
    created_at = datetime.utcnow().isoformat()
    run_id = uuid.uuid4().hex
    for item in items:
        if not isinstance(item, dict):
            continue
        new_item = item.copy()
        new_item["search_query"] = q
        new_item["created_at"] = created_at
        new_item["run_id"] = run_id
        enriched.append(new_item)
    return enriched


def _strip_mongo_ids(items: List[Dict[str, Any]]) -> None:
    for item in items:
        if isinstance(item, dict):
            item.pop("_id", None)


async def run_fast_scrapers(q: str) -> List[Dict[str, Any]]:
    batches = await asyncio.gather(
        scrape_amazon(q),
        scrape_jiomart(q),
        scrape_croma(q),
        scrape_myntra(q),
        return_exceptions=True,
    )
    return _merge_batches(batches)


async def run_llm_scrapers(q: str) -> List[Dict[str, Any]]:
    batches = await asyncio.gather(
        scrape_flipkart(q),
        scrape_meesho(q),
        return_exceptions=True,
    )
    return _merge_batches(batches)


async def background_complete_and_persist(
    *,
    q: str,
    cache: RedisCache,
    mongo_collection: _Any,
    fast_results: Optional[List[Dict[str, Any]]] = None,
    fast_ttl_seconds: int = 10 * 60,
    final_ttl_seconds: int = 24 * 60 * 60,
    lock_ttl_seconds: int = 10 * 60,
) -> None:
    q_norm = normalize_query(q)
    lock_key = f"comparitor:search:lock:{q_norm}"
    status_key = f"comparitor:search:status:{q_norm}"
    fast_key = f"comparitor:search:fast:{q_norm}"
    final_key = f"comparitor:search:final:{q_norm}"

    got_lock = await cache.acquire_lock(lock_key, ttl_seconds=lock_ttl_seconds)
    if not got_lock:
        return

    await cache.set_status(status_key, "running_full", ttl_seconds=final_ttl_seconds)

    try:
        # Cache fast results (if provided) so future requests can use them
        if fast_results is not None:
            await cache.set_json(fast_key, fast_results, ttl_seconds=fast_ttl_seconds)

        llm_results = await run_llm_scrapers(q)
        merged = []
        if fast_results:
            merged.extend(fast_results)
        merged.extend(llm_results)

        if not merged:
            await cache.set_json(final_key, [], ttl_seconds=final_ttl_seconds)
            await cache.set_status(status_key, "complete_empty", ttl_seconds=final_ttl_seconds)
            return

        # Save aggregated JSON locally (single file)
        out_dir = _bucket_dir()
        os.makedirs(out_dir, exist_ok=True)
        filename = f"aggregated_{q.replace(' ', '_')}.json"
        out_path = os.path.join(out_dir, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=4)

        # Persist to MongoDB Atlas (ONLY final merged results)
        enriched = _enrich_for_mongo(merged, q)
        if enriched:
            mongo_collection.insert_many(enriched)
            _strip_mongo_ids(enriched)

        await cache.set_json(final_key, merged, ttl_seconds=final_ttl_seconds)
        await cache.set_status(status_key, "complete", ttl_seconds=final_ttl_seconds)
    except Exception:
        await cache.set_status(status_key, "failed", ttl_seconds=final_ttl_seconds)


async def get_cached_results(
    *,
    q: str,
    cache: RedisCache,
) -> Dict[str, Any]:
    q_norm = normalize_query(q)
    status_key = f"comparitor:search:status:{q_norm}"
    fast_key = f"comparitor:search:fast:{q_norm}"
    final_key = f"comparitor:search:final:{q_norm}"

    final = await cache.get_json(final_key)
    if isinstance(final, list):
        return {"stage": "final", "results": final, "status": "complete"}

    fast = await cache.get_json(fast_key)
    status = await cache.get_str(status_key)
    if isinstance(fast, list):
        return {"stage": "fast", "results": fast, "status": status or "running"}

    return {"stage": "none", "results": None, "status": status or "none"}
