import pandas as pd
from datetime import datetime
from typing import Optional


from scraper import WebScraper
from parser import PropertyParser
from config import logging, build_url


class PropertyScraper:
    def __init__(self):
        self.scraper = WebScraper()
        self.parser = PropertyParser()
        self.properties_df = pd.DataFrame()

    async def scrape(self, search_query: str, search_type: str = "for-sale", pages: int = 1):
        """Scrape properties for given search query"""
        url = build_url(search_query, search_type)
        logging.info(f"Scraping properties from: {url}")
        self.scraper.max_pages = pages

        try:
            properties = await self.scraper.scrape(self.parser, url)
            self.properties_df = pd.DataFrame(properties)
        except Exception as e:
            logging.error(f"Error scraping properties: {e}")

    def save_results(self, filename: Optional[str] = None) -> str:
        """Save scraped results to CSV with timestamp"""
        if self.properties_df.empty:
            logging.warning("No data to save")
            return ""

        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"properties_{timestamp}.csv"

        self.properties_df.to_csv(filename, index=False)
        logging.info(f"Saved {len(self.properties_df)} properties to {filename}")
        return filename

    def get_stats(self) -> dict:
        """Get basic statistics about scraped properties"""
        if self.properties_df.empty:
            return {"status": "No data available"}

        return {
            "total_properties": len(self.properties_df),
            "locations": self.properties_df["location"].nunique(),
            "avg_bedrooms": self.properties_df["bedrooms"].astype(float).mean(),
            "price_range": {
                "min": self.properties_df["price"].min(),
                "max": self.properties_df["price"].max(),
            },
        }
