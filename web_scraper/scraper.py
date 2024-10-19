import time
from playwright.sync_api import sync_playwright, Browser, BrowserContext
from utils.config import logging, cookies, headers


class WebScraper:
    def __init__(self, base_url, sleep_time=1):
        self.base_url = base_url
        self.sleep_time = sleep_time
        self.browser = None
        self.context = None

    @staticmethod
    def initialize_browser(playwright) -> (BrowserContext, Browser):
        browser = playwright.chromium.launch(
            headless=False,
            channel="chrome",
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--start-maximized",
                "--disable-infobars",
            ],
        )
        context = browser.new_context()
        context.set_extra_http_headers(headers)
        context.add_cookies(cookies)
        return context, browser

    def make_request(self, url):
        try:
            page = self.context.new_page()
            page.goto(url)
            time.sleep(self.sleep_time)
            return page.content()
        except Exception as e:
            logging.error(f"Error making request to {url}: {e}")
            return None

    def scrape(self, parser):
        with sync_playwright() as playwright:
            self.context, self.browser = self.initialize_browser(playwright)
            try:
                url = self.base_url
                while url:
                    response = self.make_request(url)
                    if response:
                        data, url = parser.parse(response)
                        for item in data:
                            yield item
                    else:
                        break
            finally:
                self.browser.close()
