import asyncio
import inquirer
from property_scraper import PropertyScraper


async def main():
    scraper = PropertyScraper()

    # Define the questions for user interaction
    questions = [
        inquirer.Text(
            "search_query",
            message="Enter location to search (e.g. cape town)",
        ),
        inquirer.List(
            "search_type",
            message="Select search type",
            choices=["for-sale", "to-rent"],
        ),
        inquirer.Text(
            "pages",
            message="Enter number of pages to scrape (e.g. 10)",
        ),
    ]

    # Get user input
    answers = inquirer.prompt(questions)

    if answers:  # Check if user didn't cancel
        search_query = answers["search_query"]
        search_type = answers["search_type"]
        pages = int(answers["pages"])

        print(f"\nSearching for properties {search_type} in {search_query} on {pages} pages...\n")
        await scraper.scrape(search_query, search_type, pages)

        scraper.save_results(filename=f"{search_query}_{search_type}_properties.csv")

        stats = scraper.get_stats()
        print("\nScraping Statistics:")
        for key, value in stats.items():
            print(f"{key}: {value}")
    else:
        print("Operation cancelled by user")


if __name__ == "__main__":
    asyncio.run(main())
