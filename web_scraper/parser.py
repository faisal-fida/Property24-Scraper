from bs4 import BeautifulSoup


class PropertyParser:
    def __init__(self):
        self.data_selector = (
            ".js_listingResultsContainer [class*='js_resultTile p24_tileContainer']"
        )

    def parse_property(self, result):
        listing_number = result.get("data-listing-number")
        title_meta = result.find("meta", itemprop="name")
        title = title_meta.get("content") if title_meta else None
        price_span = result.find("span", class_="p24_price")
        price = price_span.get_text(strip=True) if price_span else None
        location_span = result.find("span", class_="p24_location")
        location = location_span.get_text(strip=True) if location_span else None
        description_span = result.find("span", class_="p24_excerpt")
        description = (
            description_span.get("title") + description_span.get_text(strip=True)
            if description_span
            else None
        )
        bedrooms_span = result.find("span", title="Bedrooms")
        bedrooms = (
            bedrooms_span.find("span").get_text(strip=True) if bedrooms_span else None
        )
        bathrooms_span = result.find("span", title="Bathrooms")
        bathrooms = (
            bathrooms_span.find("span").get_text(strip=True) if bathrooms_span else None
        )
        parking_spaces_span = result.find("span", title="Parking Spaces")
        parking_spaces = (
            parking_spaces_span.find("span").get_text(strip=True)
            if parking_spaces_span
            else None
        )
        erf_size_span = result.find("span", title="Erf Size")
        erf_size = (
            erf_size_span.find("span").get_text(strip=True) if erf_size_span else None
        )
        return {
            "listing_number": listing_number,
            "title": title,
            "price": price,
            "location": location,
            "description": description,
            "bedrooms": bedrooms,
            "bathrooms": bathrooms,
            "parking_spaces": parking_spaces,
            "erf_size": erf_size,
        }

    def parse(self, content):
        soup = BeautifulSoup(content, "html.parser")
        data = [
            self.parse_property(result) for result in soup.select(self.data_selector)
        ]
        return data
