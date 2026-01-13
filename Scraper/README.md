
# 📦 Compareon

FastAPI + Crawl4AI backend that scrapes six Indian e-commerce sites (Amazon, Flipkart, Croma, Meesho, JioMart, Myntra), normalizes results, caps to top 10 per site, writes per-run JSONs into 5-minute buckets, and stores enriched copies in MongoDB.

It now also supports a **fast-first** mode with **Redis/Memurai caching** so the frontend can get non-LLM results quickly and retrieve final results later.

---

## 🔍 Current approach (concise)
- `/search` FastAPI route triggers all six scrapers concurrently via `asyncio.gather`.
- CSS-first extraction everywhere; Flipkart and Meesho use Cerebras LLM extraction (Crawl4AI `LLMExtractionStrategy`).
- Links normalized to absolute, prices cleaned; each scraper truncates to top 10 items.
- Outputs land in `results/YYYYMMDD_HHMM/` (5-minute buckets): one aggregated JSON plus per-site JSONs.
- MongoDB insert adds `search_query` and `created_at`; response returns enriched data (without `_id`) and elapsed seconds.
- Windows event-loop policy set for asyncio compatibility.

---

## ⚡ Fast-first + Redis (new)
- **Fast path:** runs the 4 non-LLM scrapers first (Amazon + JioMart + Croma + Myntra) and returns immediately.
- **Background completion:** continues with the 2 LLM scrapers (Flipkart + Meesho), merges everything, then saves **only the final merged results** to MongoDB Atlas.
- **Redis/Memurai cache (optional):** stores fast results, final results, status, and a short lock to prevent duplicate runs for the same query.
- Implemented as **additive endpoints** so the existing `/search` behavior remains intact.

---

## 🧱 Architecture
- Entrypoint: FastAPI app (main.py)
  - Existing: `/search`
  - New: `/search_fast`, `/search_status`, `/search_final`
- Workers: six async scraper functions (amazon, flipkart, jiomart, meesho, croma, myntra)
- Orchestration:
  - `orchestrator.py` runs fast scrapers first and schedules background completion
  - `cache.py` provides Redis/Memurai cache helpers + simple locking
- Storage:
  - MongoDB Atlas (`comparitor_db.products`) via PyMongo
  - Redis/Memurai cache (optional)
- Filesystem outputs: timestamp buckets per 5 minutes under results/

---

## 📦 Repository layout (live paths)
- Scraper/main.py – FastAPI app, endpoints.
- Scraper/orchestrator.py – fast-first orchestration + background completion + Mongo persist.
- Scraper/cache.py – Redis helper (JSON cache, status keys, simple lock).
- Scraper/amazon_scraper.py – Amazon CSS scraper.
- Scraper/flipkart_scraper.py – Flipkart LLM scraper (Cerebras).
- Scraper/jiomart_scraper.py – JioMart CSS scraper with junk filtering.
- Scraper/meesho_scraper.py – Meesho LLM scraper (Cerebras).
- Scraper/croma_scraper.py – Croma CSS scraper with retry fallback.
- Scraper/myntra_scraper.py – Myntra CSS scraper.

---

## 🛠 Tech stack and external APIs
- FastAPI (HTTP server)
- Crawl4AI (AsyncWebCrawler, JsonCssExtractionStrategy, LLMExtractionStrategy)
- Playwright (browser automation used by Crawl4AI)
- Cerebras LLM API (provider `cerebras/gpt-oss-120b` via Crawl4AI) for Flipkart/Meesho
- MongoDB Atlas (PyMongo client)
- Redis (via Memurai/Redis) for caching + locking (optional)
- Python 3.10+

---

## 🔐 Configuration (.env in Scraper/)
```
MONGODB_URI=your_mongodb_uri
CEREBRAS_API_KEY=your_cerebras_api_key
GROQ_API_KEY=optional_if_used_elsewhere
GEMINI_API_KEY=optional_if_used_elsewhere
GEMINI_KEYS=optional_if_used_elsewhere
 
# Redis (optional but recommended)
# Memurai default works without setting this:
# REDIS_URL=redis://localhost:6379/0
REDIS_URL=redis://localhost:6379/0

# Cache TTLs (seconds)
# fast results cache (4 non-LLM sources)
REDIS_FAST_TTL_SECONDS=600
# final merged results cache (all sources)
REDIS_FINAL_TTL_SECONDS=86400
# lock TTL to prevent stampedes per query
REDIS_LOCK_TTL_SECONDS=600
```
Keep Scraper/.env out of git; rotate any key that was ever committed.

---

## ⚙️ Setup
1) Create and activate a virtual environment
```
python -m venv .venv
.venv\Scripts\activate
```
2) (Optional but recommended) Run Redis / Memurai

This enables caching + locking for the fast-first endpoints. The API still works without Redis, but you lose caching and `/search_status` will likely show `none`.

### Option A: Memurai (Windows, easiest)
- Install Memurai.
- Ensure the **Memurai** Windows service is **Running** (`services.msc` → Memurai → Start).
- Default connection used by this project: `redis://localhost:6379/0`

### Option B: Docker (cross-platform)
```
docker run --name comparitor-redis -p 6379:6379 -d redis:7-alpine
```

### Option C: WSL (Ubuntu)
```
sudo apt update
sudo apt install redis-server
sudo service redis-server start
```

### Quick verification (optional)
```
python -c "import redis; r=redis.Redis(host='localhost', port=6379, db=0); r.ping(); print('REDIS_OK')"
```

2) Install dependencies and Playwright browsers
```
pip install -r requirements.txt
python -m playwright install
```
3) Create Scraper/.env with the values above.

---

## ▶️ Run the API
From Scraper/:
```
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Recommended on Windows (avoids import-path issues)
If you start Uvicorn from outside the Scraper folder, use `--app-dir`:
```
python -m uvicorn main:app --app-dir "c:\\path\\to\\Comapritor\\Scraper" --host 127.0.0.1 --port 8000
```

Docs:
- http://127.0.0.1:8000/docs
Request example:
```
GET http://localhost:8000/search?q=iphone 16
```
Response shape (truncated):
```
{
  "status": "success",
  "total_results": 42,
  "file_saved": "aggregated_iphone_16.json",
  "elapsed_seconds": 12.345,
  "results": [ { "title": "...", "price": "₹...", "source": "Amazon", ... } ]
}
```

---

## 📤 Outputs and storage
- Files: results/YYYYMMDD_HHMM/
  - aggregated_<query>.json (all merged items)
  - amazon_results.json, croma_<query>.json, flipkart_<query>.json, jiomart_<query>.json, meesho_<query>.json, myntra_results.json
- Database: comparitor_db.products with added fields `search_query`, `created_at`.
  - For fast-first background saves, inserted items also include a shared `run_id` (used by `/search_final` to fetch a complete run reliably).

### Redis cache keys (optional)
- `comparitor:search:fast:<normalized_query>` – cached fast results
- `comparitor:search:final:<normalized_query>` – cached final merged results
- `comparitor:search:status:<normalized_query>` – status string
- `comparitor:search:lock:<normalized_query>` – lock to avoid duplicate runs

---

## 🌐 API endpoints (updated)

### 1) Full (existing)
- `GET /search?q=...`
  - Runs all 6 scrapers concurrently and returns after completion.
  - Saves the final merged data to MongoDB and writes an aggregated JSON locally.

### 2) Fast-first (new)
- `GET /search_fast?q=...`
  - Returns quickly with results from the 4 non-LLM sources.
  - Schedules background completion for the 2 LLM sources; merges, caches final, and saves to MongoDB.

### 3) Status/progress (new)
- `GET /search_status?q=...`
  - Redis-only progress check.
  - Returns `status` (`running_fast`, `running_full`, `complete`, `failed`, `none`) and booleans `has_fast`/`has_final`.

### 4) Fetch final results later (new)
- `GET /search_final?q=...`
  - Returns final results from Redis if available.
  - Otherwise falls back to MongoDB and returns the most recent completed run for that query (and backfills Redis).

---

## ✅ Test the full flow (recommended)
1) Ensure Memurai/Redis is running (optional but recommended)
2) Start the API
3) Trigger fast-first:
   - `GET http://127.0.0.1:8000/search_fast?q=water%20heater`
4) Poll status:
   - `GET http://127.0.0.1:8000/search_status?q=water%20heater`
5) Fetch final:
   - `GET http://127.0.0.1:8000/search_final?q=water%20heater`

---

## 🧠 Per-site scraper behavior
- Amazon: CSS extraction; prefixes price with ₹ when missing.
- Flipkart: Cerebras LLM extraction; requires CEREBRAS_API_KEY.
- JioMart: CSS extraction; filters junk (case/cover/glass/adapter); normalizes links.
- Meesho: Cerebras LLM extraction with scroll JS; requires CEREBRAS_API_KEY.
- Croma: CSS extraction with retry (networkidle -> domcontentloaded fallback).
- Myntra: CSS extraction; normalizes links.
All write into the shared 5-minute bucket.

---

## 🔒 Security and hygiene
- Secrets are only read from environment variables; avoid logging them.

---

## 🧭 Troubleshooting
- Playwright browsers missing: run `python -m playwright install`.
- Cerebras key missing: Flipkart/Meesho skip with a warning.
- Empty results: check site reachability/selectors; some sites throttle or alter markup.
- Mongo issues: verify MONGODB_URI and network access to Atlas.


