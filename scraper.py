from playwright.sync_api import sync_playwright, Browser, BrowserContext
from utils.config import logging, cookies, headers


class WebScraper:
    def __init__(self, sleep_time=0):
        self.sleep_time = sleep_time
        self.browser = None
        self.context = None
        self.page_no = 1
        self.url_parts = None

    @staticmethod
    async def initialize_browser(playwright) -> tuple[BrowserContext, Browser]:
        browser = await playwright.chromium.launch(
            headless=True,
            channel="chrome",
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--start-maximized",
                "--disable-infobars",
                "--disable-background-networking",
                "--disable-default-apps",
                "--disable-extensions",
                "--disable-sync",
                "--disable-translate",
                "--metrics-recording-only",
                "--no-first-run",
                "--safebrowsing-disable-auto-update",
                "--disable-javascript",
                "--blink-settings=imagesEnabled=false",
            ],
        )
        context = await browser.new_context()
        await context.set_extra_http_headers(headers)
        await context.add_cookies(cookies)
        return context, browser

    async def scrape(self, parser, url):
        async with async_playwright() as playwright:
            self.context, self.browser = await self.initialize_browser(playwright)
            page = await self.context.new_page()
            try:
                return await self._scrape_pages(page, parser, url)
            finally:
                await self.context.close()
                await self.browser.close()

    async def _visit_url(self, url, page):
        try:
            await page.goto(url)
            await page.wait_for_selector("body")
            return await page.content()
        except Exception as e:
            logging.error(f"Error making request to {url}: {e}")
            return None

    async def _scrape_pages(self, page, parser, url):
        properties = []
        while url:
            response = await self._visit_url(url, page)
            if response:
                data = parser.parse(response)
                properties.extend(data)
                logging.info(f"Scraped {len(data)} properties from {url}. Total: {len(properties)}")
                url = self._get_next_page_url(url)
            else:
                break

        return properties

    def _get_next_page_url(self, current_url):
        try:
            if self.page_no < 2:
                self.url_parts = current_url.split("/results?")

            self.page_no += 1
            return f"{self.url_parts[0]}/results/p{self.page_no}?{self.url_parts[1]}"

        except Exception as e:
            logging.error(f"Current URL: {current_url} Error getting next page URL: {e}")
            return None
