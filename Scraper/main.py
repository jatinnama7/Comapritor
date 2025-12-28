import asyncio
import json
import os
import sys
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

# Crawl4AI Core Imports
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from crawl4ai.content_filter_strategy import PruningContentFilter

load_dotenv()

# Fix for Windows SSL/Event Loop crashes
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title="Tycoon Aggregator: True Hybrid")

# --- 1. KEY ROTATOR ---
# class GeminiKeyRotator:
#     def __init__(self, keys: List[str]):
#         self.keys = [k.strip() for k in keys if k.strip()]
#         self.index = 0
#     def get_key(self):
#         key = self.keys[self.index]
#         self.index = (self.index + 1) % len(self.keys)
#         return key

# keys_list = os.getenv("GEMINI_KEYS", "").split(",")
# rotator = GeminiKeyRotator(keys_list)

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from fastapi import FastAPI, Query
from dotenv import load_dotenv

# Crawl4AI Core
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy, LLMExtractionStrategy
from crawl4ai import LLMConfig

load_dotenv()

# Windows Event Loop Fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title="Pro Aggregator: CSS + LLM Fallback")

# --- 1. DATA SCHEMA ---
class ProductSchema(BaseModel):
    title: str = Field(..., description="Full name/title of the product")
    price: str = Field(..., description="Price with currency symbol")
    rating: Optional[str] = Field(None, description="Star rating (e.g., 4.5 out of 5)")
    reviews: Optional[str] = Field(None, description="Number of reviews or ratings")
    brand: Optional[str] = Field(None, description="Brand name of the product")
    thumbnail: Optional[str] = Field(None, description="Direct URL of the product image")
    link: str = Field(..., description="Full absolute URL to the product")
    source: str = Field(..., description="The website name (e.g., Amazon, Flipkart)")

# --- 2. MODULAR SITE SELECTORS ---
# We use specific CSS paths for each site to ensure speed and zero-token cost.
SITE_CONFIGS = {
    "Amazon": {
        "baseSelector": "div.s-result-item[data-component-type='s-search-result']",
        "fields": [
            {"name": "title", "selector": "h2 span", "type": "text"},
            {"name": "price", "selector": ".a-price-whole", "type": "text"},
            {"name": "rating", "selector": "span.a-icon-alt", "type": "text"},
            {"name": "reviews", "selector": "span.a-size-base.s-underline-text", "type": "text"},
            {"name": "thumbnail", "selector": "img.s-image", "type": "attribute", "attribute": "src"},
            {"name": "link", "selector": "a.a-link-normal", "type": "attribute", "attribute": "href"}
        ]
    },
    "Flipkart": {
        "baseSelector": "div[data-id]",
        "fields": [
            {"name": "title", "selector": "div.KzDlHZ, div.w_U96n, a.s1Q9rs", "type": "text"},
            {"name": "price", "selector": "div.Nx9Wp0, div._30jeq3", "type": "text"},
            {"name": "rating", "selector": "div.XQD_v7, div._3LWZlK", "type": "text"},
            {"name": "reviews", "selector": "span.Wphh3N, span._2_R_oE", "type": "text"},
            {"name": "thumbnail", "selector": "img.DByoH4, img._396cs4", "type": "attribute", "attribute": "src"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
        ]
    },
    "Myntra": {
        "baseSelector": "li.product-base",
        "fields": [
            {"name": "title", "selector": "h4.product-product", "type": "text"},
            {"name": "price", "selector": "span.product-discountedPrice", "type": "text"},
            {"name": "rating", "selector": "div.product-ratingsContainer", "type": "text"},
            {"name": "reviews", "selector": "div.product-ratingsCount", "type": "text"},
            {"name": "thumbnail", "selector": "img", "type": "attribute", "attribute": "src"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
        ]
    }
}

# --- 3. SCRAPING ENGINE WITH FALLBACK ---
async def scrape_with_logic(crawler, name, url, query):
    # Try CSS First
    schema = SITE_CONFIGS.get(name)
    css_strategy = JsonCssExtractionStrategy(schema)
    config = CrawlerRunConfig(
        extraction_strategy=css_strategy, 
        cache_mode=CacheMode.BYPASS, 
        magic=True,
        wait_until="domcontentloaded",
        remove_overlay_elements=True
    )
    
    print(f"⚡ Site: {name} | Strategy: CSS")
    result = await crawler.arun(url=url, config=config)
    
    try:
        data = json.loads(result.extracted_content) if result.extracted_content else []
    except:
        data = []

    # FALLBACK: If CSS fails, use Gemini (LLM)
    if not data or len(data) < 2:
        print(f"🚨 Site: {name} | Strategy: FALLBACK (Gemini)")


    # 1. Define Strategy
    llm_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider="cerebras/gpt-oss-120b", # Current stable version
            api_token=os.getenv("CEREBRAS_API_KEY")
        ),
        schema=ProductSchema.model_json_schema(),
        extraction_type="schema",
        instruction=f"Extract exactly 10 {query} products. Include title, price, rating, reviews, and thumbnail URL.",
        input_format="fit_markdown"
    )

    # 2. Define Run Config
    llm_run_config = CrawlerRunConfig(
        extraction_strategy=llm_strategy, 
        magic=True,
        wait_until="domcontentloaded",
        remove_overlay_elements=True
    )

    # 3. Execute
    result = await crawler.arun(url=url, config=llm_run_config)

    if result.success and result.extracted_content:
        try:
            data = json.loads(result.extracted_content)
        except json.JSONDecodeError as e:
            print(f"❌ JSON Parsing Error: {e}")
            data = []
    else:
        print(f"❌ Scrape Failed: {result.error_message}")
        data = []

    # NORMALIZATION: Clean up URLs and Sources
    base_urls = {
        "Amazon": "https://www.amazon.in",
        "Flipkart": "https://www.flipkart.com",
        "Myntra": "https://www.myntra.com",
        "Croma": f"https://www.croma.com",
        "Meesho": f"https://www.meesho.com",
        "JioMart": f"https://www.jiomart.com"
    }
    
    cleaned_data = []
    for item in data:
        # Prepend base URL if link is relative
        link = item.get('link', '')
        if link and not link.startswith('http'):
            link = base_urls.get(name, "") + link
        
        cleaned_data.append({
            "title": item.get("title", "Unknown"),
            "price": item.get("price", "N/A"),
            "rating": item.get("rating", "N/A"),
            "reviews": item.get("reviews", "0"),
            "thumbnail": item.get("thumbnail"),
            "link": link,
            "source": name
        })
            
    return cleaned_data

# --- 4. FASTAPI ENDPOINTS ---
@app.get("/search")
async def search_endpoint(q: str = Query(..., description="Product to search")):
    sources = {
        "Amazon": f"https://www.amazon.in/s?k={q.replace(' ', '+')}",
        "Flipkart": f"https://www.flipkart.com/search?q={q.replace(' ', '%20')}",
        "Croma": f"https://www.croma.com/searchB?q={q.replace(' ', '%20')}",
        "Meesho": f"https://www.meesho.com/search?q={q.replace(' ', '%20')}",
        "JioMart": f"https://www.jiomart.com/search/{q.replace(' ', '%20')}",
        "Myntra": f"https://www.myntra.com/{q.replace(' ', '-')}"
    }
    
    all_results = []
    # Using a single browser session for multiple tabs (faster)
    async with AsyncWebCrawler(config=BrowserConfig(headless=True, enable_stealth=True, 
    user_agent_mode="random")) as crawler:
        tasks = [scrape_with_logic(crawler, name, url, q) for name, url in sources.items()]
        batch_results = await asyncio.gather(*tasks)
        for res in batch_results:
            all_results.extend(res)

    # Save to JSON file named after query
    filename = f"search_{q.replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4)
        
    return {
        "status": "success",
        "file_saved": filename,
        "count": len(all_results),
        "data": all_results
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)