import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, LLMConfig
from crawl4ai.extraction_strategy import LLMExtractionStrategy
from pydantic import BaseModel, Field, field_validator

class Product(BaseModel):
    name: str
    price: str
    link: str

    @field_validator('price')
    def validate_price(cls, v):
        if '₹' not in v and '$' not in v:
            return f"Check Price: {v}"
        return v

async def scrape_with_high_limits(urls):
    # SWITCHING TO GEMINI FOR 1M+ TOKEN LIMIT
    llm_config = LLMConfig(
        provider="gemini/gemini-2.5-flash", 
        api_token="Your_Gemini_API_Token_Here",
    )

    extraction_strategy = LLMExtractionStrategy(
        llm_config=llm_config,
        schema=Product.model_json_schema(),
        instruction="Extract products. Ensure the link is a full absolute URL."
    )

    config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        magic=True,
        cache_mode="bypass"
    )

    async with AsyncWebCrawler() as crawler:
        for url in urls:
            result = await crawler.arun(url=url, config=config)
            print(f"Data from {url}: {result.extracted_content}")
            await asyncio.sleep(5) # Stay safe

if __name__ == "__main__":
    asyncio.run(scrape_with_high_limits(["https://www.amazon.in/s?k=macbook"]))
