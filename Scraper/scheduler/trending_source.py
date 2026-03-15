"""
trending_source.py
------------------
Ask an LLM (Cerebras primary, Groq fallback) to produce the top-N most-searched
Indian e-commerce product queries in English, then return them as a list of strings.

Retry behaviour is controlled by env vars:
  WARMUP_LLM_RETRY_MINUTES   - total minutes to keep retrying before giving up (default: 10)
  WARMUP_LLM_RETRY_BASE_SECS - base backoff in seconds for the first retry (default: 5)

If all retries are exhausted the module falls back to a curated static list.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from typing import List

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Static fallback list (used when all LLM retries fail)
# ---------------------------------------------------------------------------
_STATIC_FALLBACK: List[str] = [
    "smartphone", "laptop", "wireless earbuds", "smartwatch", "running shoes",
    "men watch", "women kurta", "electric iron", "air fryer", "water heater",
    "refrigerator", "washing machine", "LED TV", "bluetooth speaker", "power bank",
    "gaming mouse", "mechanical keyboard", "webcam", "external hard drive", "USB hub",
    "yoga mat", "protein powder", "water bottle", "backpack", "sunglasses",
    "face wash", "moisturizer", "hair dryer", "electric toothbrush", "trimmer",
    "coffee maker", "microwave oven", "induction cooktop", "mixer grinder", "juicer",
    "ceiling fan", "table fan", "air cooler", "room heater", "water purifier",
    "inverter battery", "solar lantern", "HDMI cable", "screen protector", "phone case",
    "gaming headset", "monitor", "printer", "router WiFi", "smart bulb",
    "baby diapers", "baby stroller", "school bag", "lunch box", "stationery set",
    "saree", "lehenga", "formal shirt men", "jeans men", "sneakers women",
    "gold earrings", "silver ring", "handbag women", "wallet men", "belt men",
    "bedsheet set", "pillow", "curtains", "cleaning mop", "vacuum cleaner",
    "cricket bat", "football", "badminton racket", "cycling helmet", "dumbbell set",
    "electric scooter", "cycle", "car phone holder", "car seat cover", "helmet bike",
    "plant pot", "garden tools", "seeds flower", "fertilizer", "insecticide",
    "dog food", "cat food", "pet collar", "aquarium fish tank", "bird cage",
    "charger fast", "type c cable", "laptop bag", "mouse pad", "pen drive",
    "DSLR camera", "action camera", "tripod", "memory card", "photo frame",
    "drawing tablet", "calculator", "projector", "universal remote", "smart plug",
    "board game", "puzzle", "fidget toy", "RC car", "lego set",
    "safety helmet construction", "first aid kit", "fire extinguisher",
    "blood pressure monitor", "glucometer", "pulse oximeter", "thermometer",
    "vitamin C tablets", "multivitamin", "fish oil capsule", "whey protein",
    "organic honey", "dry fruits", "green tea", "coffee beans", "instant noodles",
    "cooking oil", "spices combo", "rice cooker", "electric kettle",
    "perfume men", "deodorant", "lip balm", "sunscreen SPF50", "nail polish",
    "foundation makeup", "kajal", "mascara", "face mask", "hair serum",
]


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


_RETRY_MINUTES = _int_env("WARMUP_LLM_RETRY_MINUTES", 10)
_RETRY_BASE_SECS = _float_env("WARMUP_LLM_RETRY_BASE_SECS", 5.0)
_RETRY_MAX_SECS = 60.0


def _build_prompt(count: int) -> str:
    return (
        f"You are a market research assistant. List the top {count} most frequently searched "
        "product queries on Indian e-commerce websites (Amazon India, Flipkart, Meesho, Myntra, "
        "Croma, JioMart) right now. Respond ONLY with a valid JSON array of strings, no other "
        "text, no numbering, no markdown. Each entry should be a short product search phrase in "
        "English (2-5 words). Example: [\"wireless earbuds\", \"men running shoes\", ...]"
    )


async def _fetch_from_cerebras(prompt: str, count: int) -> List[str]:
    """Call Cerebras Inference API (llama3.1-8b) to get trending queries."""
    try:
        from cerebras.cloud.sdk import AsyncCerebras  # type: ignore
    except ImportError as exc:
        raise RuntimeError("cerebras-cloud-sdk not installed") from exc

    api_key = os.getenv("CEREBRAS_API_KEY1")
    if not api_key:
        raise RuntimeError("CEREBRAS_API_KEY1 not set")

    client = AsyncCerebras(api_key=api_key)
    response = await client.chat.completions.create(
        model="llama3.1-8b",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()
    return _parse_json_list(raw, count)


async def _fetch_from_groq(prompt: str, count: int) -> List[str]:
    """Call Groq API (llama3-8b-8192) to get trending queries."""
    try:
        from groq import AsyncGroq  # type: ignore
    except ImportError as exc:
        raise RuntimeError("groq package not installed") from exc

    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    client = AsyncGroq(api_key=api_key)
    response = await client.chat.completions.create(
        model="llama3-8b-8192",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=1024,
        temperature=0.3,
    )
    raw = response.choices[0].message.content.strip()
    return _parse_json_list(raw, count)


def _parse_json_list(raw: str, expected_count: int) -> List[str]:
    """Extract a JSON array from the LLM response and return clean strings."""
    # Strip markdown code fences if present
    if raw.startswith("```"):
        lines = raw.splitlines()
        raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError(f"Expected a JSON array, got {type(data).__name__}")

    queries = []
    for item in data:
        if isinstance(item, str):
            clean = item.strip().lower()
            if clean:
                queries.append(clean)

    if not queries:
        raise ValueError("LLM returned an empty list")

    return queries[:expected_count]


async def get_trending_queries(count: int = 100) -> List[str]:
    """
    Return up to `count` trending Indian product search queries.

    Tries Cerebras first, then Groq, retrying with exponential backoff
    for up to WARMUP_LLM_RETRY_MINUTES. Falls back to static list on timeout.
    """
    prompt = _build_prompt(count)
    deadline = time.monotonic() + (_RETRY_MINUTES * 60)
    attempt = 0
    delay = _RETRY_BASE_SECS

    providers = [
        ("Cerebras", _fetch_from_cerebras),
        ("Groq", _fetch_from_groq),
    ]
    # Try providers round-robin across retries
    num_providers = len(providers)

    while time.monotonic() < deadline:
        provider_name, fetch_fn = providers[attempt % num_providers]
        try:
            logger.info("[warmup] Requesting trending queries from %s (attempt %d)", provider_name, attempt + 1)
            queries = await fetch_fn(prompt, count)
            logger.info("[warmup] Got %d trending queries from %s", len(queries), provider_name)
            return queries
        except Exception as exc:
            logger.warning("[warmup] %s failed: %s", provider_name, exc)

        attempt += 1
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            break
        sleep_time = min(delay, remaining, _RETRY_MAX_SECS)
        logger.info("[warmup] Retrying in %.1fs...", sleep_time)
        await asyncio.sleep(sleep_time)
        delay = min(delay * 2, _RETRY_MAX_SECS)

    logger.warning(
        "[warmup] All LLM retries exhausted after %d attempts. Falling back to static list.", attempt
    )
    return _STATIC_FALLBACK[:count]
