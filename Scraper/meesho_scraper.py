import asyncio
import json
import os
import sys
import urllib.parse
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from dotenv import load_dotenv

load_dotenv()

# --- 1. WINDOWS OS FIX ---
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# --- 2. DATA SCHEMA ---
class ProductSchema(BaseModel):
    title: str = Field(..., description="Full name/title of the product")
    price: str = Field(..., description="Price with currency symbol")
    rating: Optional[str] = Field(None, description="Star rating (e.g., 4.5)")
    reviews: Optional[str] = Field(None, description="Number of reviews or ratings")
    brand: Optional[str] = Field(None, description="Brand name of the product")
    thumbnail: Optional[str] = Field(None, description="Direct URL of the product image")
    link: str = Field(..., description="Full absolute URL to the product")
    source: str = Field(..., description="The website name (e.g., Meesho)")

# --- 3. MEESHO LLM SCRAPING LOGIC ---
async def scrape_meesho(search_query: str):
    current_key = os.getenv("CEREBRAS_API_KEY2")
    if not current_key:
        print("⚠️ CEREBRAS_API_KEY missing; Meesho skipped")
        return []
    
    llm_config = LLMConfig(
        provider="cerebras/gpt-oss-120b", 
        api_token=current_key
    )

    instruction = (
        f"Extract the TOP 10 product listings for exactly '{search_query}' from Meesho. "
        "IMPORTANT: Every product MUST have a link and a price. "
        "Find the link for each product (usually contains /p/). "
        "Capture the 'src' attribute of the main product image for the thumbnail. "
        "Include the brand when it is available. "
        "Ignore accessories like cases or chargers if they are not the main product."
    )

    # strategy = LLMExtractionStrategy(
    #     llm_config=llm_config,
    #     schema=ProductSchema.model_json_schema(),
    #     extraction_type="schema",
    #     instruction=instruction,
    #     input_format="fit_markdown"
    # )

    # 🎯 UPDATED CONFIG: Forcing "Human" behavior and HTML input
    config = CrawlerRunConfig(
        extraction_strategy=LLMExtractionStrategy(
            llm_config=llm_config,
            schema=ProductSchema.model_json_schema(),
            extraction_type="schema",
            instruction=instruction,
            # CHANGE: Use 'html' instead of 'fit_markdown' as Meesho's 
            # markdown often misses the lazy-loaded product URLs
            input_format="html" 
        ),
        cache_mode="bypass",
        magic=True,
        # IMPROVEMENT: Use 'networkidle' to ensure background API calls finish
        wait_until="networkidle",
        # ESSENTIAL: Meesho hides content until a real scroll happens
        js_code=[
            "window.scrollTo(0, 500);",
            "await new Promise(r => setTimeout(r, 1000));",
            "window.scrollTo(0, 1000);"
        ],
        delay_before_return_html=10.0, 
        remove_overlay_elements=True
    )

    # 🎯 UPDATED BROWSER: Higher resolution mobile to trigger the grid view
    browser_cfg = BrowserConfig(
        headless=True,
        enable_stealth=True
    )
    
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"🚀 Scraping Meesho for: {search_query}...")
        url = f"https://www.meesho.com/search?q={urllib.parse.quote(search_query)}"
        
        result = await crawler.arun(url=url, config=config)
        
        if result.success and result.extracted_content:
            data = json.loads(result.extracted_content)
            final_data = []
            for item in data:
                item['source'] = "Meesho"
                # Fix relative links
                if item.get('link') and not item['link'].startswith('http'):
                    item['link'] = "https://www.meesho.com" + item['link']
                final_data.append(item)
            
            # Save results
            final_data = final_data[:10]
            now = datetime.now()
            bucket = now.replace(minute=(now.minute // 5) * 5, second=0, microsecond=0)
            out_dir = os.path.join("results", bucket.strftime("%Y%m%d_%H%M"))
            os.makedirs(out_dir, exist_ok=True)
            filename = f"meesho_{search_query.replace(' ', '_').lower()}.json"
            out_path = os.path.join(out_dir, filename)
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(final_data, f, indent=4)
            
            print(f"✅ SUCCESS: Saved {len(final_data)} items from Meesho.")
            return final_data
            
    print("❌ Failed to extract data from Meesho.")
    return []

if __name__ == "__main__":
    search_query = input("Enter search query for Meesho: ")
    asyncio.run(scrape_meesho(search_query))