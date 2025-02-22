from typing import Optional, List, Dict, Any
from contextlib import asynccontextmanager
from playwright.async_api import async_playwright, Page, BrowserContext
from config import logging, cookies, headers


class WebScraper:
    """A web scraper specifically designed for Property24 website"""

    def __init__(self, sleep_time: int = 0):
        self.max_pages = 1
        self.sleep_time = sleep_time
        self._browser_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--start-maximized",
            "--disable-javascript",
            "--blink-settings=imagesEnabled=false",
        ]

    @asynccontextmanager
    async def _browser_context(self) -> BrowserContext:
        """Create and manage browser context using context manager"""
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=True, channel="chrome", args=self._browser_args
            )
            context = await browser.new_context()
            await context.set_extra_http_headers(headers)
            await context.add_cookies(cookies)

            try:
                yield context
            finally:
                await context.close()
                await browser.close()

    async def _fetch_page_content(self, page: Page, url: str) -> Optional[str]:
        """Fetch content from a single page"""
        try:
            await page.goto(url, wait_until="networkidle")
            await page.wait_for_selector("body", timeout=10000)
            return await page.content()
        except Exception as e:
            logging.error(f"Error fetching {url}: {str(e)}")
            return None

    def _construct_next_page_url(self, base_url: str, page_num: int) -> str:
        """Construct URL for the next page"""
        if "?" not in base_url:
            return base_url

        url_parts = base_url.split("/results?", 1)
        return f"{url_parts[0]}/results/p{page_num}?{url_parts[1]}"

    async def scrape(self, parser: Any, start_url: str) -> List[Dict[str, Any]]:
        """
        Main scraping method that handles pagination and data collection

        Args:
            parser: Parser instance to process the HTML content
            start_url: Initial URL to start scraping from

        Returns:
            List of scraped property dictionaries
        """
        properties = []
        current_page = 1

        async with self._browser_context() as context:
            page = await context.new_page()

            while current_page <= self.max_pages:
                url = (
                    self._construct_next_page_url(start_url, current_page)
                    if current_page > 1
                    else start_url
                )

                content = await self._fetch_page_content(page, url)
                if not content:
                    break

                page_properties = parser.parse(content)
                if not page_properties:
                    break

                properties.extend(page_properties)
                logging.info(
                    f"Page {current_page}: Scraped {len(page_properties)} properties. "
                    f"Total: {len(properties)}"
                )

                current_page += 1

        return properties
