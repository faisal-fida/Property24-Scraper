import asyncio
from property_scraper import PropertyScraper
from config import logging, get_user_input


async def main():
    scraper = PropertyScraper()

    try:
        search_query, pages, search_type = await get_user_input()

        await scraper.scrape(search_query, search_type, pages)

        filename = scraper.save_results(filename=f"{search_query}_{search_type}_properties.csv")
        if filename:
            logging.info(f"Results saved to: {filename}")

        stats = scraper.get_stats()
        if stats.get("status") == "No data available":
            logging.warning("No properties were scraped")
        else:
            logging.info("Scraping Statistics:")
            for key, value in stats.items():
                logging.info(f"{key}: {value}")

    except Exception as e:
        logging.error(f"An error occurred during execution: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Operation cancelled by user")
    except Exception as e:
        logging.error(f"Program terminated with error: {str(e)}")
