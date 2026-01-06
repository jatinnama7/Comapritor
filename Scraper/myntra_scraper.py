import asyncio
import json
import os
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def scrape_myntra(query: str):
    schema = {
        "name": "Myntra",
        "baseSelector": "li.product-base",
        "fields": [
            {"name": "title", "selector": "h4.product-product", "type": "text"},
            {"name": "brand", "selector": "h3.product-brand, .product-brand", "type": "text"},
            {"name": "price", "selector": "span.product-discountedPrice", "type": "text"},
            {"name": "rating", "selector": "div.product-ratingsContainer", "type": "text"},
            {"name": "thumbnail", "selector": "img", "type": "attribute", "attribute": "src"},
            {"name": "link", "selector": "a[target='_blank']", "type": "attribute", "attribute": "href"}
        ]
    }
    async with AsyncWebCrawler(config=BrowserConfig(headless=True, enable_stealth=True)) as crawler:
        result = await crawler.arun(
            url=f"https://www.myntra.com/{query}",
            config=CrawlerRunConfig(
                extraction_strategy=JsonCssExtractionStrategy(schema),
                wait_until="domcontentloaded",
                delay_before_return_html=3.0,
                magic=True
            )
        )

    if not result.success or not result.extracted_content:
        print("⚠️ Myntra scrape returned no data")
        return []

    try:
        data = json.loads(result.extracted_content)
    except json.JSONDecodeError:
        print("⚠️ Myntra JSON decode failed")
        return []

    cleaned = []
    for item in data:
        if not item.get('link'):
            continue
        link = item['link']
        if not link.startswith('http'):
            link = "https://www.myntra.com/" + link
        cleaned.append({
            "title": item.get("title", ""),
            "brand": (item.get("brand") or "").strip(),
            "price": item.get("price", "N/A"),
            "rating": item.get("rating", "N/A"),
            "reviews": item.get("reviews", "0"),
            "thumbnail": item.get("thumbnail"),
            "link": link,
            "source": "Myntra"
        })

    cleaned = cleaned[:10]
    now = datetime.now()
    bucket = now.replace(minute=(now.minute // 5) * 5, second=0, microsecond=0)
    out_dir = os.path.join("results", bucket.strftime("%Y%m%d_%H%M"))
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "myntra_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=4)
    print(f"✅ Myntra Done: {len(cleaned)} items found.")
    return cleaned

if __name__ == "__main__":
    search_query = input("Enter search query for Myntra: ")
    asyncio.run(scrape_myntra(search_query))