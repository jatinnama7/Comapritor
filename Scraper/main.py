# import asyncio
# import httpx
# from fastapi import FastAPI
# from pydantic import BaseModel
# from typing import Optional
# from pymongo import MongoClient
# from dotenv import load_dotenv
# import os
# import datetime

# # load_dotenv()
# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# # ============================
# # API KEY ROTATION SETUP
# # ============================
# API_KEYS = os.getenv("SCRAPINGDOG_API_KEYS").split(",")
# current_index = 0

# def get_key():
#     global current_index
#     return API_KEYS[current_index].strip()

# def rotate_key():
#     global current_index
#     current_index = (current_index + 1) % len(API_KEYS)
#     print(f"🔄 API key rotated → index {current_index}")


# # ============================
# # MONGODB SETUP
# # ============================
# client = MongoClient(os.getenv("MONGODB_URI"))
# db = client["shopping_data"]

# def init_collections(db):
#     required_collections = {
#         "raw_products": [
#             ("query", 1),
#             ("timestamp", -1),
#         ],
#         "clean_products": [
#             ("query", 1),
#             ("timestamp", -1),
#         ]
#     }

#     existing = db.list_collection_names()

#     for col, indexes in required_collections.items():
#         if col not in existing:
#             print(f"✅ Creating collection: {col}")
#             db.create_collection(col)

#         for field, order in indexes:
#             db[col].create_index([(field, order)])
#             print(f"   → Index created on '{field}' ({order}) for {col}")

# init_collections(db)

# raw_collection = db["raw_products"]
# clean_collection = db["clean_products"]

# # ============================
# # FastAPI app
# # ============================
# app = FastAPI()


# class SearchRequest(BaseModel):
#     query: str
#     language: Optional[str] = "en"
#     country: Optional[str] = "in"


# # ============================
# # Async immersive fetch (with retry & light pacing)
# # ============================
# async def fetch_immersive_async(client, link: str, retries: int = 2):
#     if not link:
#         return None

#     for attempt in range(retries):
#         try:
#             r = await client.get(link, timeout=10)
#             if r.status_code == 200:
#                 return r.json()

#             # if rate limited → brief wait & retry
#             if r.status_code in [403, 429]:
#                 await asyncio.sleep(0.25)
#                 continue

#         except Exception as e:
#             print("❌ Immersive fetch error:", e)

#         # small jitter between attempts
#         await asyncio.sleep(0.1)

#     return None


# # ============================
# # Clean immersive data → STRICT (no outer fallbacks)
# # ============================
# def extract_clean_immersive(raw_immersive):
#     """
#     Returns a dict with strictly immersive-derived fields or None if required fields are missing.
#     Required: brand, thumbnails[0], stores[0].link
#     Optional: rating, reviews (if immersive includes them)
#     """
#     if not raw_immersive:
#         return None

#     brand = raw_immersive.get("brand")
#     thumbs = raw_immersive.get("thumbnails", [])
#     stores = raw_immersive.get("stores", [])

#     # enforce required keys from immersive
#     if not brand or not thumbs or not isinstance(thumbs, list) or not thumbs[0]:
#         return None
#     if not stores or not isinstance(stores, list) or not stores[0].get("link"):
#         return None

#     return {
#         "brand": brand,
#         "thumbnail": thumbs[0],
#         "link": stores[0]["link"],
#         # Optional: pass through immersive rating/reviews if you ever want them from immersive
#         # "rating_immersive": raw_immersive.get("rating"),
#         # "reviews_immersive": raw_immersive.get("reviews"),
#     }


# # ============================
# # MAIN SEARCH ENDPOINT (ASYNC)
# # ============================
# @app.post("/search")
# async def search_and_store(request: SearchRequest):

#     global current_index

#     base_url = "https://api.scrapingdog.com/google_shopping"

#     attempts = 0
#     max_attempts = len(API_KEYS)

#     async with httpx.AsyncClient() as client_http:

#         # =====================================
#         # Fetch main shopping results (single call)
#         # =====================================
#         while attempts < max_attempts:

#             params = {
#                 "api_key": get_key(),
#                 "query": request.query,
#                 "language": request.language,
#                 "country": request.country
#             }

#             response = await client_http.get(base_url, params=params)

#             if response.status_code == 200:
#                 break

#             if response.status_code in [403, 429]:
#                 rotate_key()
#                 attempts += 1
#                 continue

#             return {
#                 "error": f"API Error: {response.status_code}",
#                 "details": response.text
#             }

#         data = response.json()
#         shopping_results = data.get("shopping_results", [])

#         # ============================
#         # Save RAW data
#         # ============================
#         raw_entry_id = raw_collection.insert_one({
#             "query": request.query.lower(),
#             "raw_results": data,
#             "timestamp": datetime.datetime.utcnow()
#         }).inserted_id

#         # ============================
#         # Async immersive fetch (parallel)
#         # (optional) limit concurrency to avoid throttling
#         # ============================
#         immersive_links = [
#             item.get("scrapingdog_immersive_product_link")
#             for item in shopping_results
#         ]

#         # Simple parallel fetch; if you hit throttling often, we can batch with a semaphore
#         tasks = [fetch_immersive_async(client_http, link) for link in immersive_links]
#         immersive_results = await asyncio.gather(*tasks)

#         # ============================
#         # Clean + merge data (STRICT immersive only)
#         # ============================
#         cleaned_items = []

#         for item, immersive_raw in zip(shopping_results, immersive_results):
#             immersive_clean = extract_clean_immersive(immersive_raw)
#             if not immersive_clean:
#                 # Skip this product if immersive data is missing/invalid
#                 continue

#             # Outer-sourced fields: (title, source, reviews, rating, price) are still trusted per your spec.
#             # Immersive-sourced fields: brand, thumbnail, link (strictly from immersive)
#             cleaned_items.append({
#                 "title": item.get("title"),
#                 "source": item.get("source"),
#                 "reviews": item.get("reviews"),
#                 "rating": item.get("rating"),
#                 "price": item.get("price"),
#                 "brand": immersive_clean["brand"],
#                 "thumbnail": immersive_clean["thumbnail"],
#                 "link": immersive_clean["link"]
#             })

#         # ============================
#         # Save cleaned data
#         # ============================
#         clean_collection.insert_one({
#             "query": request.query.lower(),
#             "cleaned_products": cleaned_items,
#             "raw_reference_id": raw_entry_id,
#             "timestamp": datetime.datetime.utcnow()
#         })

#         # ✅ Return results
#         return {
#             "message": "Scraped & stored successfully",
#             "items_cleaned": len(cleaned_items),
#             "cleaned_products": cleaned_items
#         }
# import asyncio
# import httpx
# from fastapi import FastAPI
# from pydantic import BaseModel
# from typing import Optional
# from pymongo import MongoClient
# from dotenv import load_dotenv
# import os
# import datetime
# import json

# # ============================
# # Load Environment Variables
# # ============================
# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# api_keys_env = os.getenv("SCRAPINGDOG_API_KEYS")
# if not api_keys_env:
#     raise EnvironmentError("❌ SCRAPINGDOG_API_KEYS not found. Check your .env file path or content.")

# API_KEYS = api_keys_env.split(",")
# current_index = 0


# def get_key():
#     global current_index
#     return API_KEYS[current_index].strip()


# def rotate_key():
#     global current_index
#     current_index = (current_index + 1) % len(API_KEYS)
#     print(f"🔄 API key rotated → index {current_index}")


# # ============================
# # MongoDB Setup
# # ============================
# client = MongoClient(os.getenv("MONGODB_URI"))
# db = client["shopping_data"]


# def init_collections(db):
#     required_collections = {
#         "raw_products": [
#             ("query", 1),
#             ("timestamp", -1),
#         ],
#         "clean_products": [
#             ("query", 1),
#             ("timestamp", -1),
#         ]
#     }

#     existing = db.list_collection_names()

#     for col, indexes in required_collections.items():
#         if col not in existing:
#             print(f"✅ Creating collection: {col}")
#             db.create_collection(col)

#         for field, order in indexes:
#             db[col].create_index([(field, order)])
#             print(f"   → Index created on '{field}' ({order}) for {col}")


# init_collections(db)

# raw_collection = db["raw_products"]
# clean_collection = db["clean_products"]

# # ============================
# # FastAPI App
# # ============================
# app = FastAPI()


# @app.get("/")
# def home():
#     return {"message": "🚀 Scraper API is running! Use /search to query products."}


# class SearchRequest(BaseModel):
#     query: str
#     language: Optional[str] = "en"
#     country: Optional[str] = "in"


# # ============================
# # Async immersive fetch (with retry & pacing)
# # ============================
# async def fetch_immersive_async(client, link: str, retries: int = 2):
#     if not link:
#         return None

#     for attempt in range(retries):
#         try:
#             r = await client.get(link, timeout=10)
#             if r.status_code == 200:
#                 return r.json()

#             # rate limit → retry
#             if r.status_code in [403, 429]:
#                 await asyncio.sleep(0.25)
#                 continue

#         except Exception as e:
#             print("❌ Immersive fetch error:", e)

#         await asyncio.sleep(0.1)

#     return None


# # ============================
# # Clean immersive data
# # ============================
# def extract_clean_immersive(raw_immersive):
#     if not raw_immersive:
#         return None

#     brand = raw_immersive.get("brand")
#     thumbs = raw_immersive.get("thumbnails", [])
#     stores = raw_immersive.get("stores", [])

#     if not brand or not thumbs or not isinstance(thumbs, list) or not thumbs[0]:
#         return None
#     if not stores or not isinstance(stores, list) or not stores[0].get("link"):
#         return None

#     return {
#         "brand": brand,
#         "thumbnail": thumbs[0],
#         "link": stores[0]["link"],
#     }


# # ============================
# # MAIN SEARCH FUNCTION (Shared by API + Terminal)
# # ============================
# async def perform_search(query: str, language: str = "en", country: str = "in"):
#     global current_index

#     base_url = "https://api.scrapingdog.com/google_shopping"
#     attempts = 0
#     max_attempts = len(API_KEYS)

#     async with httpx.AsyncClient() as client_http:
#         # --- Fetch main search results ---
#         while attempts < max_attempts:
#             params = {
#                 "api_key": get_key(),
#                 "query": query,
#                 "language": language,
#                 "country": country,
#             }

#             response = await client_http.get(base_url, params=params)

#             if response.status_code == 200:
#                 break

#             if response.status_code in [403, 429]:
#                 rotate_key()
#                 attempts += 1
#                 continue

#             return {"error": f"API Error: {response.status_code}", "details": response.text}

#         data = response.json()
#         shopping_results = data.get("shopping_results", [])

#         # --- Save raw results ---
#         raw_entry_id = raw_collection.insert_one({
#             "query": query.lower(),
#             "raw_results": data,
#             "timestamp": datetime.datetime.utcnow()
#         }).inserted_id

#         # --- Fetch immersive details ---
#         immersive_links = [item.get("scrapingdog_immersive_product_link") for item in shopping_results]
#         tasks = [fetch_immersive_async(client_http, link) for link in immersive_links]
#         immersive_results = await asyncio.gather(*tasks)

#         # --- Clean and merge ---
#         cleaned_items = []
#         for item, immersive_raw in zip(shopping_results, immersive_results):
#             immersive_clean = extract_clean_immersive(immersive_raw)
#             if not immersive_clean:
#                 continue

#             cleaned_items.append({
#                 "title": item.get("title"),
#                 "source": item.get("source"),
#                 "reviews": item.get("reviews"),
#                 "rating": item.get("rating"),
#                 "price": item.get("price"),
#                 "brand": immersive_clean["brand"],
#                 "thumbnail": immersive_clean["thumbnail"],
#                 "link": immersive_clean["link"]
#             })

#         # --- Save cleaned results ---
#         clean_collection.insert_one({
#             "query": query.lower(),
#             "cleaned_products": cleaned_items,
#             "raw_reference_id": raw_entry_id,
#             "timestamp": datetime.datetime.utcnow()
#         })

#         return {
#             "message": "Scraped & stored successfully",
#             "items_cleaned": len(cleaned_items),
#             "cleaned_products": cleaned_items,
#         }


# # ============================
# # FastAPI Endpoint
# # ============================
# @app.post("/search")
# async def search_and_store(request: SearchRequest):
#     return await perform_search(request.query, request.language, request.country)


# # ============================
# # Terminal Search Runner
# # ============================
# if __name__ == "__main__":
#     async def terminal_search():
#         query = input("🔍 Enter product name to search: ").strip()
#         if not query:
#             print("⚠️ Please enter a valid product name.")
#             return

#         print("\n🔎 Searching, please wait...\n")
#         result = await perform_search(query)

#         if "error" in result:
#             print("❌ Error:", result["error"])
#             return

#         print(f"✅ Scraped & stored successfully!")
#         print(f"🧾 {result['items_cleaned']} products found.\n")

#         # Display top 5 cleaned products
#         for i, item in enumerate(result["cleaned_products"][:5], start=1):
#             print(f"🛍️  {i}. {item['title']}")
#             print(f"     💰 Price: {item.get('price')}")
#             print(f"     🏷️ Brand: {item.get('brand')}")
#             print(f"     🌐 Source: {item.get('source')}")
#             print(f"     🔗 Link: {item.get('link')}\n")

#     asyncio.run(terminal_search())
# import asyncio
# import httpx
# from fastapi import FastAPI
# from pydantic import BaseModel
# from typing import Optional
# from pymongo import MongoClient
# from dotenv import load_dotenv
# from fastapi.middleware.cors import CORSMiddleware
# import os
# import datetime

# # ============================
# # Load Environment Variables
# # ============================
# load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

# api_keys_env = os.getenv("SCRAPINGDOG_API_KEYS")
# if not api_keys_env:
#     raise EnvironmentError("❌ SCRAPINGDOG_API_KEYS not found. Check your .env file path or content.")

# API_KEYS = api_keys_env.split(",")
# current_index = 0


# def get_key():
#     global current_index
#     return API_KEYS[current_index].strip()


# def rotate_key():
#     global current_index
#     current_index = (current_index + 1) % len(API_KEYS)
#     print(f"🔄 API key rotated → index {current_index}")


# # ============================
# # MongoDB Setup
# # ============================
# client = MongoClient(os.getenv("MONGODB_URI"))
# db = client["shopping_data"]


# def init_collections(db):
#     required_collections = {
#         "raw_products": [("query", 1), ("timestamp", -1)],
#         "clean_products": [("query", 1), ("timestamp", -1)],
#     }

#     existing = db.list_collection_names()
#     for col, indexes in required_collections.items():
#         if col not in existing:
#             db.create_collection(col)
#         for field, order in indexes:
#             db[col].create_index([(field, order)])


# init_collections(db)
# raw_collection = db["raw_products"]
# clean_collection = db["clean_products"]

# # ============================
# # FastAPI App + CORS
# # ============================
# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # You can restrict to ["http://localhost:5173"] if using Vite
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.get("/")
# def home():
#     return {"message": "🚀 Scraper API is running! Use /search to query products."}


# class SearchRequest(BaseModel):
#     query: str
#     language: Optional[str] = "en"
#     country: Optional[str] = "in"


# # ============================
# # Async immersive fetch
# # ============================
# async def fetch_immersive_async(client, link: str, retries: int = 2):
#     if not link:
#         return None
#     for attempt in range(retries):
#         try:
#             r = await client.get(link, timeout=10)
#             if r.status_code == 200:
#                 return r.json()
#             if r.status_code in [403, 429]:
#                 await asyncio.sleep(0.25)
#                 continue
#         except Exception as e:
#             print("❌ Immersive fetch error:", e)
#         await asyncio.sleep(0.1)
#     return None


# # ============================
# # Clean immersive data
# # ============================
# def extract_clean_immersive(raw_immersive):
#     if not raw_immersive:
#         return None
#     brand = raw_immersive.get("brand")
#     thumbs = raw_immersive.get("thumbnails", [])
#     stores = raw_immersive.get("stores", [])
#     if not brand or not thumbs or not isinstance(thumbs, list) or not thumbs[0]:
#         return None
#     if not stores or not isinstance(stores, list) or not stores[0].get("link"):
#         return None
#     return {"brand": brand, "thumbnail": thumbs[0], "link": stores[0]["link"]}


# # ============================
# # Main search function
# # ============================
# async def perform_search(query: str, language: str = "en", country: str = "in"):
#     global current_index
#     base_url = "https://api.scrapingdog.com/google_shopping"
#     attempts = 0
#     max_attempts = len(API_KEYS)

#     async with httpx.AsyncClient() as client_http:
#         while attempts < max_attempts:
#             params = {
#                 "api_key": get_key(),
#                 "query": query,
#                 "language": language,
#                 "country": country,
#             }
#             response = await client_http.get(base_url, params=params)
#             if response.status_code == 200:
#                 break
#             if response.status_code in [403, 429]:
#                 rotate_key()
#                 attempts += 1
#                 continue
#             return {"error": f"API Error: {response.status_code}", "details": response.text}

#         data = response.json()
#         shopping_results = data.get("shopping_results", [])
#         raw_entry_id = raw_collection.insert_one({
#             "query": query.lower(),
#             "raw_results": data,
#             "timestamp": datetime.datetime.utcnow(),
#         }).inserted_id

#         immersive_links = [item.get("scrapingdog_immersive_product_link") for item in shopping_results]
#         tasks = [fetch_immersive_async(client_http, link) for link in immersive_links]
#         immersive_results = await asyncio.gather(*tasks)

#         cleaned_items = []
#         for item, immersive_raw in zip(shopping_results, immersive_results):
#             immersive_clean = extract_clean_immersive(immersive_raw)
#             if not immersive_clean:
#                 continue
#             availability = item.get("availability", "").lower()
#             in_stock = None
#             if "in stock" in availability:
#                 in_stock = True
#             elif "out" in availability or "unavailable" in availability:
#                 in_stock = False

#             cleaned_items.append({
#                 "title": item.get("title"),
#                 "source": item.get("source"),
#                 "reviews": item.get("reviews"),
#                 "rating": item.get("rating"),
#                 "price": item.get("price"),
#                 "brand": immersive_clean["brand"],
#                 "thumbnail": immersive_clean["thumbnail"],
#                 "link": immersive_clean["link"],
#                  "inStock": in_stock,
#             })

#         clean_collection.insert_one({
#             "query": query.lower(),
#             "cleaned_products": cleaned_items,
#             "raw_reference_id": raw_entry_id,
#             "timestamp": datetime.datetime.utcnow(),
#         })

#         return {"message": "Scraped & stored successfully", "items_cleaned": len(cleaned_items), "cleaned_products": cleaned_items}


# @app.post("/search")
# async def search_and_store(request: SearchRequest):
#     return await perform_search(request.query, request.language, request.country)
# main.py
import asyncio
import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from pymongo import MongoClient
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
import os
import datetime

# ============================
# Load Environment Variables
# ============================
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

api_keys_env = os.getenv("SCRAPINGDOG_API_KEYS")
if not api_keys_env:
    raise EnvironmentError("❌ SCRAPINGDOG_API_KEYS not found. Check your .env file path or content.")

API_KEYS = api_keys_env.split(",")
current_index = 0


def get_key():
    global current_index
    return API_KEYS[current_index].strip()


def rotate_key():
    global current_index
    current_index = (current_index + 1) % len(API_KEYS)
    print(f"🔄 API key rotated → index {current_index}")


# ============================
# MongoDB Setup
# ============================
client = MongoClient(os.getenv("MONGODB_URI"))
db = client["shopping_data"]


def init_collections(db):
    required_collections = {
        "raw_products": [("query", 1), ("timestamp", -1)],
        "clean_products": [("query", 1), ("timestamp", -1)],
    }

    existing = db.list_collection_names()
    for col, indexes in required_collections.items():
        if col not in existing:
            db.create_collection(col)
        for field, order in indexes:
            db[col].create_index([(field, order)])


init_collections(db)
raw_collection = db["raw_products"]
clean_collection = db["clean_products"]

# ============================
# FastAPI App + CORS
# ============================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production restrict to your frontend origin(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "🚀 Scraper API is running! Use /search to query products."}


class SearchRequest(BaseModel):
    query: str
    language: Optional[str] = "en"
    country: Optional[str] = "in"


# ============================
# Async immersive fetch
# ============================
async def fetch_immersive_async(client, link: str, retries: int = 2):
    if not link:
        return None
    for attempt in range(retries):
        try:
            r = await client.get(link, timeout=10)
            if r.status_code == 200:
                return r.json()
            if r.status_code in [403, 429]:
                await asyncio.sleep(0.25)
                continue
        except Exception as e:
            print("❌ Immersive fetch error:", e)
        await asyncio.sleep(0.1)
    return None


# ============================
# Clean immersive data
# ============================
def extract_clean_immersive(raw_immersive):
    if not raw_immersive:
        return None
    brand = raw_immersive.get("brand")
    thumbs = raw_immersive.get("thumbnails", [])
    stores = raw_immersive.get("stores", [])
    if not brand or not thumbs or not isinstance(thumbs, list) or not thumbs[0]:
        return None
    if not stores or not isinstance(stores, list) or not stores[0].get("link"):
        return None
    return {"brand": brand, "thumbnail": thumbs[0], "link": stores[0]["link"]}


# ============================
# Helper: normalize availability -> boolean
# ============================
def parse_availability_to_bool(raw_avail) -> bool:
    """
    Normalize availability information to a boolean.
    Returns True for in-stock/available signals, False otherwise.
    """
    if raw_avail is None:
        return False

    # If already boolean, return it
    if isinstance(raw_avail, bool):
        return raw_avail

    text = str(raw_avail).strip().lower()

    # tokens that indicate availability
    positive_tokens = (
        "in stock",
        "available",
        "instock",
        "ships",
        "usually dispatched",
        "usually dispatched in",
        "usually dispatched within",
        "in stock now",
        "in stock and ready",
    )

    # tokens that indicate unavailability
    negative_tokens = ("out of stock", "unavailable", "sold out", "not available")

    # if any positive token appears -> True
    if any(tok in text for tok in positive_tokens):
        return True

    # if any negative token appears -> False
    if any(tok in text for tok in negative_tokens):
        return False

    # fallback: if the string contains 'in' and not 'out', treat as available
    if "in" in text and "out" not in text:
        return True

    # default safe fallback
    return False


# ============================
# Main search function
# ============================
async def perform_search(query: str, language: str = "en", country: str = "in"):
    global current_index
    base_url = "https://api.scrapingdog.com/google_shopping"
    attempts = 0
    max_attempts = len(API_KEYS)

    async with httpx.AsyncClient() as client_http:
        while attempts < max_attempts:
            params = {
                "api_key": get_key(),
                "query": query,
                "language": language,
                "country": country,
            }
            response = await client_http.get(base_url, params=params)
            if response.status_code == 200:
                break
            if response.status_code in [403, 429]:
                rotate_key()
                attempts += 1
                continue
            return {"error": f"API Error: {response.status_code}", "details": response.text}

        data = response.json()
        shopping_results = data.get("shopping_results", [])

        raw_entry_id = raw_collection.insert_one({
            "query": query.lower(),
            "raw_results": data,
            "timestamp": datetime.datetime.utcnow(),
        }).inserted_id

        immersive_links = [item.get("scrapingdog_immersive_product_link") for item in shopping_results]
        tasks = [fetch_immersive_async(client_http, link) for link in immersive_links]
        immersive_results = await asyncio.gather(*tasks)

        cleaned_items = []
        for item, immersive_raw in zip(shopping_results, immersive_results):
            immersive_clean = extract_clean_immersive(immersive_raw)
            if not immersive_clean:
                continue

            # Normalize availability -> boolean (always True or False)
            raw_avail = item.get("availability") or ""
            in_stock = parse_availability_to_bool(raw_avail)

            

            cleaned_items.append({
                "title": item.get("title"),
                "source": item.get("source"),
                "reviews": item.get("reviews"),
                "rating": item.get("rating"),
                "price": item.get("price"),
                "brand": immersive_clean["brand"],
                "thumbnail": immersive_clean["thumbnail"],
                "link": immersive_clean["link"],

            })

        clean_collection.insert_one({
            "query": query.lower(),
            "cleaned_products": cleaned_items,
            "raw_reference_id": raw_entry_id,
            "timestamp": datetime.datetime.utcnow(),
        })

        return {"message": "Scraped & stored successfully", "items_cleaned": len(cleaned_items), "cleaned_products": cleaned_items}


@app.post("/search")
async def search_and_store(request: SearchRequest):
    return await perform_search(request.query, request.language, request.country)
