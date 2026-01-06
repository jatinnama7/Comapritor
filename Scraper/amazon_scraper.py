import asyncio
import json
import os
import re
from datetime import datetime
def _bucket_dir() -> str:
    now = datetime.now()
    bucket = now.replace(minute=(now.minute // 5) * 5, second=0, microsecond=0)
    return os.path.join("results", bucket.strftime("%Y%m%d_%H%M"))

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

async def scrape_amazon(query: str):
    schema = {
        "name": "Amazon",
        "baseSelector": "div.s-result-item[data-component-type='s-search-result']",
        "fields": [
            {"name": "title", "selector": ".a-text-normal", "type": "text"},
            {"name": "brand", "selector": "span.a-size-base-plus, span.a-size-base", "type": "text"},
            {"name": "price", "selector": ".a-price-whole", "type": "text"},
            {"name": "rating", "selector": "span.a-icon-alt", "type": "text"},
            {"name": "reviews", "selector": "span.a-size-base.s-underline-text", "type": "text"},
            {"name": "thumbnail", "selector": "img.s-image", "type": "attribute", "attribute": "src"},
            {"name": "link", "selector": "a.a-link-normal", "type": "attribute", "attribute": "href"}
        ]
    }

    async with AsyncWebCrawler(config=BrowserConfig(headless=True, enable_stealth=True)) as crawler:
        result = await crawler.arun(
            url=f"https://www.amazon.in/s?k={query}",
            config=CrawlerRunConfig(
                extraction_strategy=JsonCssExtractionStrategy(schema),
                wait_until="domcontentloaded",
                magic=True
            )
        )

    if not result.success or not result.extracted_content:
        print("⚠️ Amazon scrape returned no data")
        return []

    try:
        data = json.loads(result.extracted_content)
    except json.JSONDecodeError:
        print("⚠️ Amazon JSON decode failed")
        return []

    cleaned = []
    for item in data:
        if not item.get("link"):
            continue
        link = item["link"]
        if not link.startswith("http"):
            link = "https://www.amazon.in" + link

        title = item.get("title", "")
        brand_val = (item.get("brand") or "").strip()
        if brand_val.lower().find("bought") != -1:
            brand_val = ""
        if not brand_val and title:
            # pick first meaningful token
            tokens = re.split(r"\s+", title)
            for tok in tokens:
                tclean = re.sub(r"[^A-Za-z0-9&.-]", "", tok)
                if tclean and tclean.lower() not in {"pack", "set", "combo", "of", "for", "men", "women", "unisex", "kids", "boy", "girl", "girls", "boys"}:
                    brand_val = tclean
                    break

        price_raw = (item.get("price") or "N/A").strip()
        price_val = price_raw if price_raw.startswith("₹") or price_raw == "N/A" else f"₹{price_raw}"
        cleaned.append({
            "title": title,
            "brand": brand_val,
            "price": price_val,
            "rating": item.get("rating", "N/A"),
            "reviews": item.get("reviews", "0"),
            "thumbnail": item.get("thumbnail"),
            "link": link,
            "source": "Amazon"
        })

    cleaned = cleaned[:10]
    out_dir = _bucket_dir()
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "amazon_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(cleaned, f, indent=4)
    print(f"✅ Amazon Done: {len(cleaned)} items found.")
    return cleaned

if __name__ == "__main__":
    search_query = input("Enter search query for Amazon: ")
    asyncio.run(scrape_amazon(search_query))