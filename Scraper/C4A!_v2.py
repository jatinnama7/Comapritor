# import asyncio
# import json
# import os
# import sys
# from fastapi import FastAPI, Query
# from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, LLMConfig
# from crawl4ai.extraction_strategy import LLMExtractionStrategy
# from pydantic import BaseModel, Field
# from typing import List, Optional
# from dotenv import load_dotenv

# load_dotenv()


# # --- 1. PROACTOR EVENT LOOP FIX (Windows SSL Errors) ---
# if sys.platform == 'win32':
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# app = FastAPI(title="Comparitor Aggregator")

# # --- 2. DATA SCHEMA ---
# class ProductSchema(BaseModel):
#     title: str = Field(..., description="Full name/title of the product")
#     price: str = Field(..., description="Price with currency symbol")
#     rating: Optional[str] = Field(None, description="Star rating (e.g., 4.5 out of 5)")
#     reviews: Optional[str] = Field(None, description="Number of reviews or ratings")
#     brand: Optional[str] = Field(None, description="Brand name of the product")
#     thumbnail: Optional[str] = Field(None, description="Complete URL of the product image")
#     link: str = Field(..., description="Full absolute URL to the product")
#     source: str = Field(..., description="The website name (e.g., Amazon, Flipkart)")

# # --- 3. SCRAPING LOGIC ---
# async def run_aggregator_scrape(search_query: str):
#     # Get Gemini Key from environment or paste here (Google AI Studio)
#     # GEMINI_API_KEY = "AIzaSyB-YQRBYry8NKphGS92_95Hm-7O9ao-8qU" 
#     GROQ_API_KEY = os.getenv("GROQ_API_KEY")
#     GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
#     if not GEMINI_API_KEY:
#         raise ValueError("Please set the GEMINI_API_KEY environment variable.")
    
#     llm_config = LLMConfig(
#         provider="gemini/gemini-2.5-flash",
#         api_token= GEMINI_API_KEY,

#     )

#     extraction_instruction = (
#         f"Extract only the TOP 10 product listings for exactly '{search_query}'. "
#         "Strictly ignore 'Plus', 'Max', or 'Pro' variants unless specified in the query. "
#         "You MUST find the 'src' or 'data-src' attribute for the product image and return it as 'thumbnail'. "
#         "Return the data as a JSON list."
#     )

#     extraction_strategy = LLMExtractionStrategy(
#         llm_config=llm_config,
#         schema=ProductSchema.model_json_schema(),   
#         extraction_type="schema",
#         instruction=extraction_instruction
#     )

#     # Magic mode handles bot detection; CSS-based simplification reduces tokens
#     config = CrawlerRunConfig(
#         extraction_strategy=extraction_strategy,
#         cache_mode="bypass",
#         magic=True,
#         word_count_threshold=10,
#         remove_overlay_elements=True
#     )

#     # Define URLs for Page 1 and Page 2
#     # Note: We append the source to the instruction for accuracy
#     sources = {
#         "Amazon": f"https://www.amazon.in/s?k={search_query}",
#         "Flipkart": f"https://www.flipkart.com/search?q={search_query}",
#         "Croma": f"https://www.croma.com/searchB?q={search_query}",
#         "Meesho": f"https://www.meesho.com/search?q={search_query}",
#         "JioMart": f"https://www.jiomart.com/search/{search_query}",
#         "Myntra": f"https://www.myntra.com/{search_query}"
#     }


#     all_results = []
#     async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
#         for name, url in sources.items():
#             print(f"Fetching from {name}...")
#             # We limit to 1 page to save tokens
#             result = await crawler.arun(url=url, config=config)
            
#             if result.success and result.extracted_content:
#                 data = json.loads(result.extracted_content)
#                 # Filter locally as a second layer of protection
#                 if isinstance(data, list):
#                     all_results.extend(data[:10]) # Force limit to top 10
            
#             await asyncio.sleep(3) # Small gap between stores

#     # Save Results
#     file_name = f"search_{search_query.replace(' ', '_')}.json"
#     with open(file_name, "w", encoding="utf-8") as f:
#         json.dump(all_results, f, indent=4)
#     print(f"Scraping completed. Data saved to {file_name}")
#     return all_results

# @app.get("/search")
# async def search_products(q: str = Query(..., description="Product to search for")):
#     data = await run_aggregator_scrape(q)
#     return {"status": "success", "count": len(data), "data": data}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)

## OLDER LOGIC FOR REFERENCE ##

# import asyncio
# import json
# import os
# import sys
# from fastapi import FastAPI, Query
# from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, LLMConfig
# from crawl4ai.extraction_strategy import LLMExtractionStrategy
# from pydantic import BaseModel, Field
# from typing import List, Optional
# from dotenv import load_dotenv

# load_dotenv()

# # --- 1. PROACTOR EVENT LOOP FIX (Windows SSL Errors) ---
# if sys.platform == 'win32':
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# app = FastAPI(title="Comparitor Aggregator")

# # --- 2. KEY ROTATOR ---
# class GeminiKeyRotator:
#     def __init__(self, keys: List[str]):
#         self.keys = [k.strip() for k in keys if k.strip()]
#         self.index = 0
#         if not self.keys:
#             raise ValueError("No Gemini API keys found in .env")

#     def get_key(self):
#         key = self.keys[self.index]
#         self.index = (self.index + 1) % len(self.keys)
#         return key

# keys_list = os.getenv("GEMINI_KEYS", "").split(",")
# rotator = GeminiKeyRotator(keys_list)

# # --- 3. DATA SCHEMA ---


# # --- 3. SCRAPING LOGIC ---
# async def run_aggregator_scrape(search_query: str):
#     GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
#     if not GEMINI_API_KEY:
#         raise ValueError("Please set the GEMINI_API_KEY environment variable.")
    
#     # FIX: Corrected model name to gemini-2.0-flash
#     llm_config = LLMConfig(
#         provider="gemini/gemini-2.0-flash",
#         api_token=GEMINI_API_KEY,
#     )

#     extraction_instruction = (
#         f"Extract only the TOP 10 product listings for exactly '{search_query}'. "
#         "Strictly ignore 'Plus', 'Max', or 'Pro' variants unless specified in the query. "
#         "IMPORTANT: You MUST capture the 'src' or 'data-src' attribute of the main product image for the thumbnail. "
#         "Return the data as a JSON list."
#     )

#     extraction_strategy = LLMExtractionStrategy(
#         llm_config=llm_config,
#         schema=ProductSchema.model_json_schema(),   
#         extraction_type="schema",
#         instruction=extraction_instruction
#     )

#     # FIX: Added wait_for_images and js_code scroll to fix null thumbnails
#     config = CrawlerRunConfig(
#         extraction_strategy=extraction_strategy,
#         cache_mode="bypass",
#         magic=True,
#         wait_for_images=True,          # Ensures images are loaded before extraction
#         wait_until="networkidle",
#         js_code="window.scrollBy(0, 1000);", # Triggers lazy-loading for thumbnails
#         word_count_threshold=10,
#         remove_overlay_elements=True
#     )

#     sources = {
#         "Amazon": f"https://www.amazon.in/s?k={search_query}",
#         "Flipkart": f"https://www.flipkart.com/search?q={search_query}",
#         "Croma": f"https://www.croma.com/searchB?q={search_query}",
#         "Meesho": f"https://www.meesho.com/search?q={search_query}",
#         "JioMart": f"https://www.jiomart.com/search/{search_query}",
#         "Myntra": f"https://www.myntra.com/{search_query}"
#     }

#     all_results = []
#     browser_cfg = BrowserConfig(headless=True, viewport_width=1280, viewport_height=720)
#     async with AsyncWebCrawler(config=browser_cfg) as crawler:
#         for name, url in sources.items():
#             print(f"Fetching from {name}...")
#             result = await crawler.arun(url=url, config=config)
            
#             if result.success and result.extracted_content:
#                 try:
#                     data = json.loads(result.extracted_content)
#                     if isinstance(data, list):
#                         # Force tag the source in Python to ensure it's correct
#                         for item in data:
#                             item['source'] = name
#                         all_results.extend(data[:10]) 
#                 except Exception as e:
#                     print(f"Error processing {name}: {e}")
            
#             await asyncio.sleep(3) 

#     file_name = f"search_{search_query.replace(' ', '_')}.json"
#     with open(file_name, "w", encoding="utf-8") as f:
#         json.dump(all_results, f, indent=4)
    
#     print(f"Scraping completed. Data saved to {file_name}")
#     return all_results

# @app.get("/search")
# async def search_products(q: str = Query(..., description="Product to search for")):
#     data = await run_aggregator_scrape(q)
#     return {"status": "success", "count": len(data), "data": data}

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)



import asyncio
import json
import os
import sys
from fastapi import FastAPI, Query
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

# --- 1. WINDOWS OS FIX ---
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title="Comparitor Aggregator Pro")

# --- 2. KEY ROTATOR ---
class GeminiKeyRotator:
    def __init__(self, keys: List[str]):
        self.keys = [k.strip() for k in keys if k.strip()]
        self.index = 0
        if not self.keys:
            raise ValueError("No Gemini API keys found in .env")

    def get_key(self):
        key = self.keys[self.index]
        self.index = (self.index + 1) % len(self.keys)
        return key

keys_list = os.getenv("GEMINI_KEYS", "").split(",")
rotator = GeminiKeyRotator(keys_list)

# --- 3. DATA SCHEMA ---
class ProductSchema(BaseModel):
    title: str = Field(..., description="Full name/title of the product")
    price: str = Field(..., description="Price with currency symbol")
    rating: Optional[str] = Field(None, description="Star rating (e.g., 4.5 out of 5)")
    reviews: Optional[str] = Field(None, description="Number of reviews or ratings")
    brand: Optional[str] = Field(None, description="Brand name of the product")
    thumbnail: Optional[str] = Field(None, description="Direct URL of the product image")
    link: str = Field(..., description="Full absolute URL to the product")
    source: str = Field(..., description="The website name (e.g., Amazon, Flipkart)")

# --- 4. PARALLEL SCRAPING LOGIC ---
async def scrape_source(name: str, url: str, crawler: AsyncWebCrawler, search_query: str):
    """Function to handle a single website scrape."""
    
    # Get a fresh key for this specific request
    current_key = rotator.get_key()
    
    llm_config = LLMConfig(
        provider="gemini/gemini-2.5-flash",
        api_token=current_key
    )

    instruction = (
        f"Extract only the TOP 10 product listings for exactly '{search_query}'. "
        "Strictly ignore 'Plus', 'Max', or 'Pro' variants unless specified in the query. "
        "IMPORTANT: You MUST capture the 'src' or 'data-src' attribute of the main product image for the thumbnail. "
        "Return the data as a JSON list."
    )

    strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        schema=ProductSchema.model_json_schema(),
        extraction_type="schema",
        instruction=instruction
    )

    # Optimized for speed and image fetching
    config = CrawlerRunConfig(
        extraction_strategy=strategy,
        cache_mode="bypass",
        magic=True,
        wait_for_images=True,
        wait_until="domcontentloaded",  # Faster than networkidle
        js_code="window.scrollBy(0, 600);", # Trigger lazy-load images
        word_count_threshold=5,
        remove_overlay_elements=True
    )

    try:
        print(f"🚀 Scraping {name}...")
        result = await crawler.arun(url=url, config=config)
        
        if result.success and result.extracted_content:
            data = json.loads(result.extracted_content)
            if isinstance(data, list):
                for item in data:
                    item['source'] = name
                return data[:10]
    except Exception as e:
        print(f"❌ Error scraping {name}: {str(e)}")
    return []

async def run_aggregator_scrape(search_query: str):
    sources = {
        "Amazon": f"https://www.amazon.in/s?k={search_query}",
        "Flipkart": f"https://www.flipkart.com/search?q={search_query}",
        "Croma": f"https://www.croma.com/searchB?q={search_query}",
        "Meesho": f"https://www.meesho.com/search?q={search_query}",
        "JioMart": f"https://www.jiomart.com/search/{search_query}",
        "Myntra": f"https://www.myntra.com/{search_query}"
    }

    browser_cfg = BrowserConfig(headless=True, viewport_width=1280, viewport_height=720)
    
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # Create all tasks to run in parallel
        tasks = [scrape_source(name, url, crawler, search_query) for name, url in sources.items()]
        
        # Execute all tasks concurrently
        all_results_batches = await asyncio.gather(*tasks)
        
        # Flatten the list of lists
        final_results = [item for batch in all_results_batches for item in batch]

    # Save to JSON locally
    file_name = f"search_{search_query.replace(' ', '_')}.json"
    with open(file_name, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=4)
        
    return final_results

# --- 5. FASTAPI ENDPOINT ---
@app.get("/search")
async def search_products(q: str = Query(..., description="Product to search for")):
    results = await run_aggregator_scrape(q)
    return {"status": "success", "count": len(results), "data": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)