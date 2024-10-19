from web_scraper.scraper import WebScraper
from web_scraper.parser import PropertyParser

import json
from utils.config import logging


def save_properties(parser, scraper):
    logging.info("Saving properties to json file")
    with open("properties.json", "w") as file:
        for property in scraper.scrape(parser):
            json.dump(property, file)
            file.write("\n")


def scrape_properties(base_url: str) -> None:
    logging.info("Starting web scraper")
    scraper = WebScraper(base_url)
    parser = PropertyParser()
    save_properties(parser, scraper)


# from web_scraper.main import scrape_properties
# scrape_properties("https://www.property24.com/for-sale/advanced-search/results?sp=cid%3d755")