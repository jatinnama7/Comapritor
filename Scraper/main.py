import asyncio
import json
import os
import sys
import urllib.parse
from datetime import datetime
import time
from typing import List

from fastapi import FastAPI, Query, HTTPException
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

load_dotenv()

if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

app = FastAPI(title="Comparitor Aggregator")


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

if __name__ == "__main__":
    import uvicorn
    print("🚀 Comparitor Aggregator is running on http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)