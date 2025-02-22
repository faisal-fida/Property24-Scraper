from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, BrowserContext, Browser
from config import logging, cookies, headers
import asyncio


class WebScraper:
    """A web scraper specifically designed for Property24 website"""

    def __init__(self, sleep_time: int = 0, max_concurrent_pages: int = 5):
        self.max_pages = 1
        self.sleep_time = sleep_time
        self.max_concurrent_pages = max_concurrent_pages
        self._browser_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--start-maximized",
            "--disable-javascript",
            "--blink-settings=imagesEnabled=false",
            "--disable-extensions",
            "--disable-notifications",
            "--disable-popup-blocking",
            "--disable-infobars",
            "--disable-background-networking",
            "--disable-background-timer-throttling",
            "--disable-backgrounding-occluded-windows",
        ]
        self._browser: Optional[Browser] = None

    async def _initialize_browser(self):
        """Initialize browser instance if not already initialized"""
        if not self._browser:
            playwright = await async_playwright().start()
            self._browser = await playwright.chromium.launch(
                headless=True, channel="chrome", args=self._browser_args
            )
        return self._browser

    @asynccontextmanager
    async def _browser_context(self) -> BrowserContext:
        """Create and manage browser context using context manager"""
        browser = await self._initialize_browser()
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}, ignore_https_errors=True
        )
        await context.set_extra_http_headers(headers)
        await context.add_cookies(cookies)

        try:
            yield context
        finally:
            await context.close()

    async def _fetch_page_content(self, context: BrowserContext, url: str) -> Optional[str]:
        """Fetch content from a single page"""
        page = await context.new_page()
        try:
            await page.goto(url, wait_until="networkidle", timeout=30000)
            await page.wait_for_selector("body", timeout=10000)
            content = await page.content()
            await page.close()
            return content
        except Exception as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            await page.close()
            return None

    def _construct_next_page_url(self, base_url: str, page_num: int) -> str:
        """Construct URL for the next page"""
        if "?" not in base_url:
            return base_url

        url_parts = base_url.split("/results?", 1)
        return f"{url_parts[0]}/results/p{page_num}?{url_parts[1]}"

    async def _scrape_batch(
        self, context: BrowserContext, urls: List[str], parser: Any
    ) -> List[Dict[str, Any]]:
        """Scrape a batch of URLs concurrently"""
        tasks = [self._fetch_page_content(context, url) for url in urls]
        contents = await asyncio.gather(*tasks)

        properties = []
        for content in contents:
            if content:
                page_properties = parser.parse(content)
                if page_properties:
                    properties.extend(page_properties)
        return properties

    async def scrape(self, parser: Any, start_url: str) -> List[Dict[str, Any]]:
        """
        Main scraping method that handles pagination and data collection
        """
        properties = []
        urls = [
            self._construct_next_page_url(start_url, page) if page > 1 else start_url
            for page in range(1, self.max_pages + 1)
        ]

        # Split URLs into batches for concurrent processing
        batch_size = self.max_concurrent_pages
        url_batches = [urls[i : i + batch_size] for i in range(0, len(urls), batch_size)]

        async with self._browser_context() as context:
            for batch_num, url_batch in enumerate(url_batches, 1):
                batch_properties = await self._scrape_batch(context, url_batch, parser)
                properties.extend(batch_properties)

                logging.info(
                    f"Batch {batch_num}: Scraped {len(batch_properties)} properties. "
                    f"Total: {len(properties)}"
                )

        return properties
