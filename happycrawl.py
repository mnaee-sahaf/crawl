import asyncio
from typing import List
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from pathlib import Path

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_custom_urls(path="custom_urls.txt") -> List[str]:
    with open(path, "r") as f:
        return [line.strip() for line in f if line.strip()]

def safe_filename(url: str) -> str:
    from urllib.parse import urlparse
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_")
    return f"{parsed.netloc}_{path or 'index'}.md"

async def crawl_sequential(urls: List[str]):
    print("\n=== Sequential Crawling with Session Reuse ===")

    browser_config = BrowserConfig(
        headless=True,
        extra_args=["--disable-gpu", "--disable-dev-shm-usage", "--no-sandbox"],
    )

    crawl_config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator()
    )

    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start()

    try:
        session_id = "session1"
        for url in urls:
            result = await crawler.arun(
                url=url,
                config=crawl_config,
                session_id=session_id
            )
            if result.success and result.markdown:
                print(f"[✓] Crawled: {url} ({len(result.markdown.raw_markdown)} chars)")
                filename = safe_filename(url)
                with open(OUTPUT_DIR / filename, "w") as f:
                    f.write(result.markdown.raw_markdown)
            else:
                print(f"[!] Failed: {url} - Error: {result.error_message}")
    finally:
        await crawler.close()

async def main():
    urls = load_custom_urls()
    if urls:
        print(f"[✓] Loaded {len(urls)} URLs from custom_urls.txt")
        await crawl_sequential(urls)
    else:
        print("[!] No URLs found in custom_urls.txt")

if __name__ == "__main__":
    asyncio.run(main())
