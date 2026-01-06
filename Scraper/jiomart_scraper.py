import asyncio
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy

# --- 1. MANDATORY WINDOWS FIX ---
# This prevents the 'NotImplementedError' on Windows systems
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

async def scrape_jiomart(query: str):
    # --- 2. THE MAJOR FIX: Using the verified URL pattern ---
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.jiomart.com/search?q={encoded_query}"
    
    # --- 3. REFINED SELECTORS (2025 Layout) ---
    # We use multiple fallbacks for the base container and links
    schema = {
        "name": "JioMart Structural",
        "baseSelector": "li.productCard, .plp-card-container, .jm-col-4",
        "fields": [
            {"name": "title", "selector": ".plp-card-details-name, .plp-card-title", "type": "text"},
            {"name": "brand", "selector": ".plp-card-details-name .jm-body-xs, .plp-card-details-brand, .product-brand", "type": "text"},
            {"name": "price", "selector": ".jm-heading-xxs, .plp-card-details-price", "type": "text"},
            {"name": "rating", "selector": ".plp-card-details-rating, .product-rating-content-star-container.top-review-rating span, .product-rating-content-star-container span, [data-rating], [data-testid='rating'], [aria-label*='rating'], .rating-stars span", "type": "text"},
            {"name": "reviews", "selector": ".plp-card-details-rating-count, .jm-body-xs, [class*='rating-count']", "type": "text"},
            {"name": "thumbnail", "selector": "img.jm-aspect-ratio-item, img", "type": "attribute", "attribute": "src"},
            {"name": "link", "selector": "a.plp-card-main-container, a", "type": "attribute", "attribute": "href"}
        ]
    }

    browser_cfg = BrowserConfig(
        headless=True,
        enable_stealth=True,
        user_agent_mode="random"
    )

    async with AsyncWebCrawler(config=browser_cfg) as crawler:
        print(f"📡 Scraping JioMart: {url}")
        
        # Use 'domcontentloaded' to bypass long-running background scripts
        result = await crawler.arun(
            url=url,
            config=CrawlerRunConfig(
                extraction_strategy=JsonCssExtractionStrategy(schema),
                wait_until="domcontentloaded",
                # Wait for product cards (more stable than rating spans)
                wait_for="css:li.productCard, .plp-card-container", 
                delay_before_return_html=6.0, # allow rating text to hydrate
                magic=True,
                cache_mode=CacheMode.BYPASS,
                # Scroll to trigger lazy-loading of reviews and links
                js_code="window.scrollBy(0, 1000);"
            )
        )
        
        if not result.success:
            print(f"❌ JioMart Failed: {result.error_message}")
            return

    raw_data = json.loads(result.extracted_content) if result.extracted_content else []
    filtered_data = []
    keywords = query.lower().split()

    for item in raw_data:
        title = (item.get('title') or "").strip()
        price_raw = (item.get('price') or "").strip()
        rating_raw = (item.get('rating') or "").strip()
        reviews_raw = (item.get('reviews') or "").strip()
        brand_raw = (item.get('brand') or "").strip()
        
        if not title:
            continue

        title_lower = title.lower()
        is_match = all(kw in title_lower for kw in keywords)
        is_junk = any(j in title_lower for j in ["case", "cover", "glass", "adapter"])

        if is_match and not is_junk:
            price_match = re.findall(r'₹?\s?[\d,]+', price_raw)
            item['price'] = price_match[0].strip() if price_match else "N/A"
            
            rating_num = re.search(r'(\d+\.\d+|\d+)', rating_raw)
            
            item['rating'] = rating_num.group(1) if rating_num else "N/A"

            rev_num = re.search(r'\d+', reviews_raw)
            item['reviews'] = rev_num.group(0) if rev_num else "0"

            if brand_raw.lower() in {"men", "women", "unisex", "kids", "boy", "girl", "girls", "boys", "pack", "combo", "set", ""} and title:
                tokens = re.split(r"\s+", title)
                brand_candidate = ""
                for tok in tokens:
                    clean_tok = re.sub(r"[^A-Za-z0-9&.-]", "", tok)
                    if clean_tok and clean_tok.lower() not in {"men", "women", "unisex", "kids", "boy", "girl", "girls", "boys", "pack", "combo", "set", "of", "for"}:
                        brand_candidate = clean_tok
                        break
                brand_raw = brand_candidate
            item['brand'] = brand_raw
            
            if item.get('link') and not item['link'].startswith('http'):
                item['link'] = "https://www.jiomart.com" + item['link']
            
            if item.get('link'):
                item['source'] = "JioMart"
                filtered_data.append(item)

    filtered_data = filtered_data[:10]
    now = datetime.now()
    bucket = now.replace(minute=(now.minute // 5) * 5, second=0, microsecond=0)
    out_dir = os.path.join("results", bucket.strftime("%Y%m%d_%H%M"))
    os.makedirs(out_dir, exist_ok=True)
    filename = f"jiomart_{query.replace(' ', '_').lower()}.json"
    out_path = os.path.join(out_dir, filename)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(filtered_data, f, indent=4)
        
    print(f"✅ SUCCESS: {len(filtered_data)} authentic items saved to {filename}")
    return filtered_data

if __name__ == "__main__":
    # Test with your search query
    search_query = input("Enter search query for JioMart: ")
    asyncio.run(scrape_jiomart(search_query))