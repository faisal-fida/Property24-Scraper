from web_scraper.scraper import WebScraper
from web_scraper.parser import PropertyParser

import pandas as pd
from utils.config import logging, base_url

scraper = WebScraper()
parser = PropertyParser()


async def scrape_properties(selected_suggestions: str, search_type: str) -> pd.DataFrame:
    logging.info(f"Scraping properties from the following suggestions: {selected_suggestions}")

    if not selected_suggestions:
        return pd.DataFrame()

    if not isinstance(selected_suggestions, list):
        selected_suggestions = [selected_suggestions]

    suggestion_ids = "%2c".join(str(id) for id in selected_suggestions)
    
    url = f"{base_url}/{search_type}/advanced-search/results?sp=cid%3d{suggestion_ids}%26s%3d3990"
    logging.info(f"Scraping properties from {url}")

<<<<<<< HEAD
# from web_scraper.main import scrape_properties; scrape_properties("https://www.property24.com/for-sale/advanced-search/results?sp=cid%3d2462")
=======
    properties = []
    try:
        properties = await scraper.scrape(parser, url)
    except Exception as e:
        logging.error(f"Error scraping properties from {url}: {e}")

    df = pd.DataFrame(properties)
    return df
    
>>>>>>> 54ea97b4cfd44e9e7270bca5f4715bebb5495c10
