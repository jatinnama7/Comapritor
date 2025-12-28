import asyncio
import json
import os
import sys
from datetime import datetime
from fastapi import FastAPI, Query
from dotenv import load_dotenv

# Crawl4AI Core
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

load_dotenv()

# Windows Event Loop Fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI(title="Structural Aggregator: Pure CSS")

# --- 1. MODULAR SELECTOR DEFINITIONS ---
# Each site has a unique structure. We define them individually for 100% accuracy.
SITE_SCHEMAS = {
    "Amazon": {
        "name": "Amazon India",
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
        "name": "Flipkart",
        "baseSelector": "div.t_9756, div._1AtV87, div.slp-item",
        "fields": [
            {"name": "title", "selector": "div.KzDlHZ, div._4rR01T, a.s1Q9rs", "type": "text"},
            {"name": "price", "selector": "div.Nx9Wp0, div._30jeq3", "type": "text"},
            {"name": "rating", "selector": "div.XQD_v7, div._3LWZlK", "type": "text"},
            {"name": "reviews", "selector": "span.Wphh3N, span._2_R_oE", "type": "text"},
            {"name": "thumbnail", "selector": "img.DByoH4, img._396cs4", "type": "attribute", "attribute": "src"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
        ]
    },
    "Myntra": {
        "name": "Myntra",
        "baseSelector": "li.product-base",
        "fields": [
            {"name": "title", "selector": "h4.product-product", "type": "text"},
            {"name": "price", "selector": "span.product-discountedPrice", "type": "text"},
            {"name": "rating", "selector": "div.product-ratingsContainer", "type": "text"},
            {"name": "reviews", "selector": "div.product-ratingsCount", "type": "text"},
            {"name": "thumbnail", "selector": "img", "type": "attribute", "attribute": "src"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
        ]
    },
    "Croma": {
        "name": "Croma",
        "baseSelector": "li.product-item",
        "fields": [
            {"name": "title", "selector": "h3.product-title", "type": "text"},
            {"name": "price", "selector": "span.amount", "type": "text"},
            {"name": "rating", "selector": ".cp-rating", "type": "text"},
            {"name": "thumbnail", "selector": "img", "type": "attribute", "attribute": "src"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
        ]
    },
    "Meesho": {
        "name": "Meesho",
        "baseSelector": "div[class*='ProductCard']",
        "fields": [
            {"name": "title", "selector": "p[class*='ProductTitle']", "type": "text"},
            {"name": "price", "selector": "h5[class*='PriceText']", "type": "text"},
            {"name": "thumbnail", "selector": "img", "type": "attribute", "attribute": "src"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
        ]
    },
    "JioMart": {
        "name": "JioMart",
        "baseSelector": "li.productCard",
        "fields": [
            {"name": "title", "selector": ".plp-card-title", "type": "text"},
            {"name": "price", "selector": ".jm-heading-xxs", "type": "text"},
            {"name": "thumbnail", "selector": "img", "type": "attribute", "attribute": "src"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"}
        ]
    }
}

# --- 2. EXTRACTION LOGIC ---
async def scrape_site(crawler, name, url):
    schema = SITE_SCHEMAS.get(name)
    strategy = JsonCssExtractionStrategy(schema)
    
    # Custom config per site to handle timeouts and JS rendering
    config = CrawlerRunConfig(
        extraction_strategy=strategy,
        cache_mode=CacheMode.BYPASS,
        magic=True,
        # Myntra/Amazon need lighter wait conditions to avoid timeouts
        wait_until="domcontentloaded" if name in ["Myntra", "Amazon"] else "networkidle",
        js_code="window.scrollBy(0, 1000);",
        page_timeout=80000
    )
    
    print(f"📡 Requesting: {name}...")
    result = await crawler.arun(url=url, config=config)
    
    if result.success and result.extracted_content:
        data = json.loads(result.extracted_content)
        # Post-processing: Tag source and fix links
        for item in data:
            item['source'] = name
            # Fix relative URLs
            if item.get('link') and not item['link'].startswith('http'):
                base = "https://www.amazon.in" if name=="Amazon" else "https://www.flipkart.com" if name=="Flipkart" else "https://www.myntra.com" if name=="Myntra" else ""
                item['link'] = base + item['link']
        return data
    return []

# --- 3. FASTAPI ENDPOINT ---
@app.get("/search")
async def search_all(q: str = Query(..., description="Search term")):
    urls = {
        "Amazon": f"https://www.amazon.in/s?k={q.replace(' ', '+')}",
        "Flipkart": f"https://www.flipkart.com/search?q={q.replace(' ', '%20')}",
        "Myntra": f"https://www.myntra.com/{q.replace(' ', '-')}",
        "Croma": f"https://www.croma.com/searchB?q={q.replace(' ', '%20')}",
        "Meesho": f"https://www.meesho.com/search?q={q.replace(' ', '%20')}",
        "JioMart": f"https://www.jiomart.com/search/{q.replace(' ', '%20')}"
    }
    
    final_results = []
    browser_cfg = BrowserConfig(headless=True, enable_stealth=True)

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        # Run all 6 scrapers in parallel
        tasks = [scrape_site(crawler, name, url) for name, url in urls.items()]
        batch_results = await asyncio.gather(*tasks)
        
        for res in batch_results:
            final_results.extend(res)

    # Save to JSON file
    filename = f"search_{q.replace(' ', '_')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=4)
        
    return {"status": "success", "count": len(final_results), "data": final_results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)