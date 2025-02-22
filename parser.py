from typing import Dict, List, Optional
from bs4 import BeautifulSoup, Tag
from dataclasses import dataclass
from config import logging


@dataclass
class PropertyData:
    """Data class to store property information"""

    listing_number: str
    title: Optional[str] = None
    price: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    bedrooms: Optional[str] = None
    bathrooms: Optional[str] = None
    parking_spaces: Optional[str] = None
    erf_size: Optional[str] = None


class PropertyParser:
    """Parser for Property24 listing results"""

    def __init__(self):
        self.data_selector = (
            ".js_listingResultsContainer [class*='js_resultTile p24_tileContainer']"
        )
        self._field_selectors = {
            "title": ("meta", {"itemprop": "name"}, "content"),
            "price": ("span", {"class_": "p24_price"}, None),
            "location": ("span", {"class_": "p24_location"}, None),
            "description": ("span", {"class_": "p24_excerpt"}, None),
            "bedrooms": ("span", {"title": "Bedrooms"}, None),
            "bathrooms": ("span", {"title": "Bathrooms"}, None),
            "parking_spaces": ("span", {"title": "Parking Spaces"}, None),
            "erf_size": ("span", {"class_": "p24_size"}, None),
        }

    def _extract_field(self, result: Tag, field_name: str) -> Optional[str]:
        """Extract field value from the HTML using predefined selectors"""
        tag_name, attrs, attr_name = self._field_selectors[field_name]
        element = result.find(tag_name, **attrs)

        if not element:
            return None

        if attr_name:
            return element.get(attr_name)

        if field_name == "description" and element:
            return element.get("title", "") + element.get_text(strip=True).replace("...", "")

        if field_name == "erf_size" and element:
            return element.get_text(strip=True).split(" ")[0]

        if field_name == "price" and element:
            return element.get_text(strip=True).replace("R", "").replace(" ", "")

        span = (
            element.find("span")
            if field_name in ["bedrooms", "bathrooms", "parking_spaces", "erf_size"]
            else element
        )
        return span.get_text(strip=True) if span else None

    def parse_property(self, result: Tag) -> PropertyData:
        """Parse single property listing"""
        try:
            listing_data = {
                "listing_number": result.get("data-listing-number", ""),
            }

            # Extract all other fields
            for field in self._field_selectors.keys():
                listing_data[field] = self._extract_field(result, field)

            return PropertyData(**listing_data)

        except Exception as e:
            logging.error(f"Error parsing property: {str(e)}")
            return PropertyData(listing_number="error")

    def parse(self, content: str) -> List[Dict]:
        """Parse all property listings from page content"""
        try:
            soup = BeautifulSoup(content, "html.parser")
            results = soup.select(self.data_selector)

            properties = [vars(self.parse_property(result)) for result in results]

            logging.info(f"Successfully parsed {len(properties)} properties")
            return properties

        except Exception as e:
            logging.error(f"Error parsing content: {str(e)}")
            return []
