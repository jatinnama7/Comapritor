import asyncio
import json
import os
from datetime import datetime
from pydantic import BaseModel, Field
from typing import List, Optional
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from dotenv import load_dotenv
load_dotenv()

# 1. Define the Schema for the LLM to follow
class FlipkartProduct(BaseModel):
    title: str = Field(..., description="Full name of the product")
    price: str = Field(..., description="Current price with currency symbol")
    rating: str = Field("N/A", description="Numeric rating out of 5")
    reviews: str = Field("0", description="Number of reviews or ratings")
    thumbnail: str = Field(..., description="Image URL of the product")
    link: str = Field(..., description="Full URL to the product page")

async def scrape_flipkart(query: str):
    api_key = os.getenv("CEREBRAS_API_KEY1")
    if not api_key:
        print("⚠️ CEREBRAS_API_KEY missing; Flipkart skipped")
        return []

    llm_config = LLMConfig(
        provider="cerebras/gpt-oss-120b",
        api_token=api_key
    )

    extraction_strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        schema=FlipkartProduct.model_json_schema(),
        extraction_type="schema",
        instruction=(
            f"Extract the top 10 products from this Flipkart search page for '{query}'. "
            "Ignore sponsored 'Ad' results if they are not relevant. "
            "Ensure the link is a full URL. Capture the clean price and numeric rating."
        ),
        input_format="fit_markdown"
    )

    browser_cfg = BrowserConfig(headless=True, enable_stealth=True, user_agent_mode="random")

    run_config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        cache_mode=CacheMode.BYPASS,
        wait_for="css:div[data-id], ._cPHDOP",
        delay_before_return_html=3.0,
        magic=True
    )

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"🤖 LLM is analyzing Flipkart for: {query}...")
        result = await crawler.arun(
            url=f"https://www.flipkart.com/search?q={query.replace(' ', '%20')}",
            config=run_config
        )

    if not result.success or not result.extracted_content:
        print(f"❌ LLM Extraction Failed: {result.error_message}")
        return []

    try:
        extracted_data = json.loads(result.extracted_content)
    except Exception as e:
        print(f"❌ JSON Parsing Error: {e}")
        print("Raw Content:", result.extracted_content[:500])
        return []

    cleaned = []
    for item in extracted_data:
        if not item.get("link"):
            continue
        link = item["link"]
        if not link.startswith("http"):
            link = "https://www.flipkart.com" + link
        cleaned.append({
            "title": item.get("title", ""),
            "price": item.get("price", "N/A"),
            "rating": item.get("rating", "N/A"),
            "reviews": item.get("reviews", "0"),
            "thumbnail": item.get("thumbnail"),
            "link": link,
            "source": "Flipkart"
        })

    cleaned = cleaned[:10]
    now = datetime.now()
    bucket = now.replace(minute=(now.minute // 5) * 5, second=0, microsecond=0)
    out_dir = os.path.join("results", bucket.strftime("%Y%m%d_%H%M"))
    os.makedirs(out_dir, exist_ok=True)
    filename = f"flipkart_{query.replace(' ', '_').lower()}.json"
    out_path = os.path.join(out_dir, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=4)

    print(f"✅ SUCCESS: LLM saved {len(cleaned)} items to {filename}")
    return cleaned

if __name__ == "__main__":
    search_query = input("Enter search query for Flipkart: ")
    asyncio.run(scrape_flipkart(search_query))