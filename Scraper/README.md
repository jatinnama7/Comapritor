
# 📦 Compareon
FastAPI + Crawl4AI backend that scrapes six Indian e-commerce sites (Amazon, Flipkart, Croma, Meesho, JioMart, Myntra), normalizes results, caps to top 10 per site, writes per-run JSONs into 5-minute buckets, and stores enriched copies in MongoDB.

---

## 🔍 Current approach (concise)
- `/search` FastAPI route triggers all six scrapers concurrently via `asyncio.gather`.
- CSS-first extraction everywhere; Flipkart and Meesho use Cerebras LLM extraction (Crawl4AI LLMExtractionStrategy).
- Links normalized to absolute, prices cleaned; each scraper truncates to 10 items.
- Outputs land in `results/YYYYMMDD_HHMM/` (5-minute buckets): one aggregated JSON plus per-site JSONs.
- MongoDB insert adds `search_query` and `created_at`; response returns enriched data (without `_id`) and elapsed seconds.
- Windows event-loop policy set for asyncio compatibility.

---

## 🧱 Architecture
- Entrypoint: FastAPI app (main.py) exposes `/search`.
- Workers: six async scraper functions (amazon, flipkart, jiomart, meesho, croma, myntra).
- Extraction: Crawl4AI AsyncWebCrawler
  - CSS selectors for Amazon, Croma, JioMart, Myntra
  - LLMExtractionStrategy (Cerebras) for Flipkart, Meesho
- Storage: MongoDB Atlas (comparitor_db.products) via PyMongo.
- Filesystem outputs: timestamp buckets per 5 minutes under results/.

---

## 📦 Repository layout (live paths)
- Scraper/main.py – FastAPI app, aggregator, Mongo writes, bucketed output.
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
- Python 3.10+

---

## 🔐 Configuration (.env in Scraper/)
```
MONGODB_URI=your_mongodb_uri
CEREBRAS_API_KEY=your_cerebras_api_key
GROQ_API_KEY=optional_if_used_elsewhere
GEMINI_API_KEY=optional_if_used_elsewhere
GEMINI_KEYS=optional_if_used_elsewhere
```
Keep Scraper/.env out of git; rotate any key that was ever committed.

---

## ⚙️ Setup
1) Create and activate a virtual environment
```
python -m venv .venv
.venv\Scripts\activate
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


