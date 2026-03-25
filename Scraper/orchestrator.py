import asyncio
import json
import os
import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Callable, Awaitable

from typing import Any as _Any

from amazon_scraper import scrape_amazon
from croma_scraper import scrape_croma
from flipkart_scraper import scrape_flipkart
from jiomart_scraper import scrape_jiomart
from meesho_scraper import scrape_meesho
from myntra_scraper import scrape_myntra

from cache import RedisCache


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


SCRAPER_RETRY_MAX_ATTEMPTS = _int_env("SCRAPER_RETRY_MAX_ATTEMPTS", 3)
SCRAPER_RETRY_BASE_DELAY_SECONDS = _float_env("SCRAPER_RETRY_BASE_DELAY_SECONDS", 1.0)
SCRAPER_RETRY_MAX_DELAY_SECONDS = _float_env("SCRAPER_RETRY_MAX_DELAY_SECONDS", 10.0)


def _is_retryable_error(err: Exception) -> bool:
    msg = str(err).lower()
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
) -> List[Dict[str, Any]]:
    last_err: Optional[Exception] = None
    for attempt in range(1, SCRAPER_RETRY_MAX_ATTEMPTS + 1):
        try:
            res = await fn()
            if not isinstance(res, list):
                raise RuntimeError(f"{site_name} returned {type(res).__name__} (expected list)")
            if retry_on_empty and len(res) == 0:
                raise RuntimeError(f"{site_name} returned 0 items")
            return res
        except Exception as e:
            last_err = e

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


async def _run_sites_with_errors(tasks: List[tuple]) -> tuple:
    batches = await asyncio.gather(
        *[t[1] for t in tasks],
        return_exceptions=True,
    )

    errors: Dict[str, str] = {}
    for (site_name, _), batch in zip(tasks, batches):
        if isinstance(batch, Exception):
            errors[site_name] = str(batch)

    merged = _merge_batches(batches)
    return merged, errors


def normalize_query(q: str) -> str:
    """Lowercase, collapse whitespace, fold hyphens/underscores into spaces, strip punctuation."""
    import re as _re
    q = (q or "").strip().lower()
    # fold hyphens and underscores into spaces ("men-watch" → "men watch")
    q = q.replace("-", " ").replace("_", " ")
    # remove punctuation except spaces and alphanumerics
    q = _re.sub(r"[^\w\s]", "", q)
    # collapse multiple spaces
    return " ".join(q.split())


# Common articles/prepositions to strip when generating variants
_STRIP_WORDS = {"a", "an", "the", "for", "of", "in", "with", "and"}

# Trivial plural/singular pairs (extend as needed)
_PLURAL_RULES: list[tuple] = [
    ("watches", "watch"), ("phones", "phone"), ("shoes", "shoe"),
    ("laptops", "laptop"), ("tablets", "tablet"), ("heaters", "heater"),
    ("irons", "iron"), ("earphones", "earphone"), ("headphones", "headphone"),
    ("cameras", "camera"), ("tvs", "tv"), ("refrigerators", "refrigerator"),
    ("fridges", "fridge"), ("mixers", "mixer"), ("juicers", "juicer"),
    ("fans", "fan"), ("coolers", "cooler"), ("ovens", "oven"),
]


def generate_query_variants(q_norm: str) -> list[str]:
    """
    Return a de-duplicated list of plausible normalized query variants (including q_norm itself).
    Variants cover:
      - article/preposition stripping   ("watch for men" → "watch men")
      - plural ↔ singular              ("shoes" → "shoe", "shoe" → "shoes")
      - digit-word compaction          ("men s watch" → "mens watch")
    """
    seen: set[str] = set()
    variants: list[str] = []

    def _add(v: str) -> None:
        v = " ".join(v.split())
        if v and v not in seen:
            seen.add(v)
            variants.append(v)

    _add(q_norm)

    words = q_norm.split()

    # 1. Strip articles/prepositions (but only if > 1 word remains)
    stripped = [w for w in words if w not in _STRIP_WORDS]
    if len(stripped) > 1:
        _add(" ".join(stripped))

    # 2. Plural ↔ singular for every word
    for i, word in enumerate(words):
        for plural, singular in _PLURAL_RULES:
            if word == plural:
                new_words = words[:i] + [singular] + words[i + 1:]
                _add(" ".join(new_words))
            elif word == singular:
                new_words = words[:i] + [plural] + words[i + 1:]
                _add(" ".join(new_words))

    # 3. Same but on the stripped variant
    if stripped and len(stripped) != len(words):
        for i, word in enumerate(stripped):
            for plural, singular in _PLURAL_RULES:
                if word == plural:
                    new_words = stripped[:i] + [singular] + stripped[i + 1:]
                    _add(" ".join(new_words))
                elif word == singular:
                    new_words = stripped[:i] + [plural] + stripped[i + 1:]
                    _add(" ".join(new_words))

    # 4. "mens" → "men s" and "men s" → "mens"
    joined = q_norm.replace(" ", "")
    if joined != q_norm:
        _add(joined)
        # also try removing trailing 's' from compound: "womens" → "women"
        if joined.endswith("s") and len(joined) > 3:
            _add(joined[:-1])

    return variants


async def register_query_in_index(q_norm: str, cache: "RedisCache") -> None:
    """Record this normalized query in the Redis sorted-set index so future lookups can discover it."""
    await cache.register_query(q_norm)


async def get_cached_results_robust(
    *,
    q: str,
    cache: "RedisCache",
) -> Dict[str, Any]:
    """
    Like get_cached_results but tries all plausible variants of the query before giving up.
    Returns the first cache hit found (final > fast, exact > variant).
    """
    q_norm = normalize_query(q)
    variants = generate_query_variants(q_norm)

    # 1. Check exact match first (fast path, same as original get_cached_results)
    result = await get_cached_results(q=q, cache=cache)
    if result["stage"] != "none":
        return result

    # 2. Try each variant
    for variant in variants[1:]:  # variants[0] is q_norm (already tried above)
        final_key = f"comparitor:search:final:{variant}"
        fast_key = f"comparitor:search:fast:{variant}"
        status_key = f"comparitor:search:status:{variant}"
                                                                                                                                
        if isinstance(final, list) and final:
            return {"stage": "final", "results": final, "status": "complete", "matched_variant": variant}

        fast = await cache.get_json(fast_key)
        if isinstance(fast, list) and fast:
            status = await cache.get_str(status_key)
            return {"stage": "fast", "results": fast, "status": status or "running", "matched_variant": variant}

    return {"stage": "none", "results": None, "status": "none"}


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
    results, _errors = await run_fast_scrapers_with_errors(q)
    return results


async def run_fast_scrapers_with_errors(q: str) -> tuple[List[Dict[str, Any]], Dict[str, str]]:
    tasks = [
        ("Amazon", _run_with_retries(site_name="Amazon", fn=lambda: scrape_amazon(q))),
        ("JioMart", _run_with_retries(site_name="JioMart", fn=lambda: scrape_jiomart(q))),
        ("Croma", _run_with_retries(site_name="Croma", fn=lambda: scrape_croma(q))),
        ("Myntra", _run_with_retries(site_name="Myntra", fn=lambda: scrape_myntra(q))),
    ]
    return await _run_sites_with_errors(tasks)


async def run_llm_scrapers(q: str) -> List[Dict[str, Any]]:
    results, _errors = await run_llm_scrapers_with_errors(q)
    return results


async def run_llm_scrapers_with_errors(q: str) -> tuple[List[Dict[str, Any]], Dict[str, str]]:
    tasks = [
        ("Flipkart", _run_with_retries(site_name="Flipkart", fn=lambda: scrape_flipkart(q))),
        ("Meesho", _run_with_retries(site_name="Meesho", fn=lambda: scrape_meesho(q))),
    ]
    return await _run_sites_with_errors(tasks)


async def background_complete_and_persist(
    *,
    q: str,
    cache: RedisCache,
    mongo_collection: _Any,
    fast_results: Optional[List[Dict[str, Any]]] = None,
    fast_ttl_seconds: int = 10 * 60,
    final_ttl_seconds: int = 24 * 60 * 60,
    lock_ttl_seconds: int = 10 * 60,
    lock_already_acquired: bool = False,
) -> None:
    q_norm = normalize_query(q)
    lock_key = f"comparitor:search:lock:{q_norm}"
    status_key = f"comparitor:search:status:{q_norm}"
    fast_key = f"comparitor:search:fast:{q_norm}"
    final_key = f"comparitor:search:final:{q_norm}"
    error_key = f"comparitor:search:error:{q_norm}"

    got_lock = lock_already_acquired or await cache.acquire_lock(lock_key, ttl_seconds=lock_ttl_seconds)
    if not got_lock:
        return

    # Register this query in the index so robust lookups (and warmup) can discover it
    await register_query_in_index(q_norm, cache)

    await cache.set_status(status_key, "running_full", ttl_seconds=final_ttl_seconds)

    try:
        # Cache fast results (if provided) so future requests can use them
        if fast_results is not None:
            await cache.set_json(fast_key, fast_results, ttl_seconds=fast_ttl_seconds)

        llm_results, llm_errors = await run_llm_scrapers_with_errors(q)
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

        if llm_errors:
            await cache.set_status(status_key, "complete_partial", ttl_seconds=final_ttl_seconds)
            await cache.set_json(
                error_key,
                {"errors": llm_errors, "where": "llm_scrapers"},
                ttl_seconds=final_ttl_seconds,
            )
        else:
            await cache.set_status(status_key, "complete", ttl_seconds=final_ttl_seconds)
    except Exception as e:
        await cache.set_status(status_key, "failed", ttl_seconds=final_ttl_seconds)
        await cache.set_json(
            error_key,
            {"error": str(e), "where": "background_complete_and_persist"},
            ttl_seconds=final_ttl_seconds,
        )


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
