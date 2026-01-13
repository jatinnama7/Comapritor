import asyncio
import json
import os
import sys
import urllib.parse
from datetime import datetime
from datetime import timedelta
import time
from typing import List

from fastapi import FastAPI, Query, HTTPException, BackgroundTasks
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
    normalize_query,
    run_fast_scrapers,
)

load_dotenv()

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(title="Comparitor Aggregator")

cache = RedisCache()


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        val = int(raw)
        return val if val > 0 else default
    except Exception:
        return default


FAST_TTL_SECONDS = _int_env("REDIS_FAST_TTL_SECONDS", 10 * 60)
FINAL_TTL_SECONDS = _int_env("REDIS_FINAL_TTL_SECONDS", 24 * 60 * 60)
LOCK_TTL_SECONDS = _int_env("REDIS_LOCK_TTL_SECONDS", 10 * 60)


def _bucket_dir() -> str:
    now = datetime.now()
    bucket = now.replace(minute=(now.minute // 5) * 5, second=0, microsecond=0)
    return os.path.join("results", bucket.strftime("%Y%m%d_%H%M"))

# --- 2. MONGODB ATLAS SETUP ---
MONGO_URI = os.getenv("MONGODB_URI") 
client = MongoClient(MONGO_URI)
db = client["comparitor_db"]
collection = db["products"]

@app.get("/search")
async def search_and_aggregate(q: str = Query(..., description="Product to search")):
    start_time = time.perf_counter()
    print(f"📡 Starting parallel search for: {q}")
    
    try:
        results_batches = await asyncio.gather(
            scrape_amazon(q),
            scrape_flipkart(q),
            scrape_jiomart(q),
            scrape_meesho(q),
            scrape_croma(q),
            scrape_myntra(q),
            return_exceptions=True 
        )
    except Exception as e:
        print(f"❌ Aggregator Error: {e}")
        raise HTTPException(status_code=500, detail="Error during parallel execution")

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
        "status": "success",
        "total_results": len(enriched_data),
        "file_saved": filename,
        "elapsed_seconds": round(elapsed, 3),
        "results": enriched_data
    }

@app.get("/search_fast")
async def search_fast(
    background_tasks: BackgroundTasks,
    q: str = Query(..., description="Product to search"),
):
    start_time = time.perf_counter()
    q_norm = normalize_query(q)

    cached = await get_cached_results(q=q, cache=cache)
    if cached.get("stage") == "final" and isinstance(cached.get("results"), list):
        elapsed = time.perf_counter() - start_time
        return {
            "status": "success",
            "mode": "final_cache",
            "query": q,
            "query_normalized": q_norm,
            "total_results": len(cached["results"]),
            "elapsed_seconds": round(elapsed, 3),
            "results": cached["results"],
        }

    if cached.get("stage") == "fast" and isinstance(cached.get("results"), list):
        background_tasks.add_task(
            background_complete_and_persist,
            q=q,
            cache=cache,
            mongo_collection=collection,
            fast_results=cached["results"],
            fast_ttl_seconds=FAST_TTL_SECONDS,
            final_ttl_seconds=FINAL_TTL_SECONDS,
            lock_ttl_seconds=LOCK_TTL_SECONDS,
        )

        elapsed = time.perf_counter() - start_time
        return {
            "status": "partial",
            "mode": "fast_cache",
            "query": q,
            "query_normalized": q_norm,
            "total_results": len(cached["results"]),
            "elapsed_seconds": round(elapsed, 3),
            "results": cached["results"],
        }

    # No cache: run only the 4 non-LLM scrapers first
    await cache.set_status(
        f"comparitor:search:status:{q_norm}",
        "running_fast",
        ttl_seconds=FAST_TTL_SECONDS,
    )
    fast_results = await run_fast_scrapers(q)

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

    # Continue in background: run LLM scrapers, merge, write JSON, save to Atlas, cache final
    background_tasks.add_task(
        background_complete_and_persist,
        q=q,
        cache=cache,
        mongo_collection=collection,
        fast_results=fast_results,
        fast_ttl_seconds=FAST_TTL_SECONDS,
        final_ttl_seconds=FINAL_TTL_SECONDS,
        lock_ttl_seconds=LOCK_TTL_SECONDS,
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

if __name__ == "__main__":
    import uvicorn
    print("🚀 Comparitor Aggregator is running on http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)