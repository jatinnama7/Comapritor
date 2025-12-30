import asyncio
import json
import os
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def scrape_croma(query: str):
    encoded_query = query.replace(" ", "%20")
    url = f"https://www.croma.com/searchB?q={encoded_query}%3Arelevance&text={encoded_query}"
    
    schema = {
        "name": "Croma SearchB",
        "baseSelector": "li.product-item, .cp-product, [data-testid='product-card']",
        "fields": [
            {"name": "title", "selector": "h3, .plp-product-name, .product-title", "type": "text"},
            {"name": "price", "selector": ".amount, .new-price, .plp-srp-new-price", "type": "text"},
            {"name": "rating", "selector": ".cp-rating, .rating-stars", "type": "text"},
            {"name": "reviews", "selector": ".rating-count, .review-count", "type": "text"},
            {"name": "thumbnail", "selector": "img", "type": "attribute", "attribute": "src"},
            {"name": "link", "selector": "a[target='_blank']", "type": "attribute", "attribute": "href"}
        ]
    }

    browser_cfg = BrowserConfig(
        headless=True,
        enable_stealth=True,
        user_agent_mode="random",
        headers={"Referer": "https://www.google.com/", "Accept-Language": "en-US,en;q=0.9"}
    )

    # Retry with a lighter wait condition if the first attempt times out
    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        run_config_heavy = CrawlerRunConfig(
            extraction_strategy=JsonCssExtractionStrategy(schema),
            wait_until="networkidle",
            wait_for="css:ul.product-list, li.product-item",
            delay_before_return_html=5.0,
            magic=True,
            cache_mode=CacheMode.BYPASS,
            page_timeout=70000,
        )

        run_config_light = CrawlerRunConfig(
            extraction_strategy=JsonCssExtractionStrategy(schema),
            wait_until="domcontentloaded",
            wait_for="css:li.product-item, [data-testid='product-card']",
            delay_before_return_html=3.0,
            magic=True,
            cache_mode=CacheMode.BYPASS,
            page_timeout=45000,
        )

        result = await crawler.arun(url=url, config=run_config_heavy)
        if (not result.success or not result.extracted_content):
            print("⚠️ Croma first attempt timed out; retrying with lighter wait condition...")
            result = await crawler.arun(url=url, config=run_config_light)

    if not result.success or not result.extracted_content:
        print(f"❌ Croma Failed: {result.error_message}")
        return []

    try:
        raw_data = json.loads(result.extracted_content)
    except json.JSONDecodeError:
        print("⚠️ Croma JSON decode failed")
        return []

    cleaned = []
    for item in raw_data:
        link = item.get("link")
        if not link:
            continue
        if not link.startswith("http"):
            link = "https://www.croma.com" + link
        cleaned.append({
            "title": (item.get("title") or "").strip(),
            "price": (item.get("price") or "N/A").strip(),
            "rating": (item.get("rating") or "N/A").strip(),
            "reviews": (item.get("reviews") or "0").strip(),
            "thumbnail": item.get("thumbnail"),
            "link": link,
            "source": "Croma"
        })

    cleaned = cleaned[:10]
    now = datetime.now()
    bucket = now.replace(minute=(now.minute // 5) * 5, second=0, microsecond=0)
    out_dir = os.path.join("results", bucket.strftime("%Y%m%d_%H%M"))
    os.makedirs(out_dir, exist_ok=True)
    filename = f"croma_{query.replace(' ', '_').lower()}.json"
    out_path = os.path.join(out_dir, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=4)
    print(f"✅ SUCCESS: {len(cleaned)} items saved to {filename}")
    return cleaned

if __name__ == "__main__":
    search_query = input("Enter search query for Croma: ")
    asyncio.run(scrape_croma(search_query))