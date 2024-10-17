import requests
from requests.adapters import HTTPAdapter
from pydantic import BaseModel, ValidationError
from typing import List, Dict

from scraper.config import suggestion_url, search_url, retries, logging


class Suggestion(BaseModel):
    id: int
    name: str
    type: int
    source: int
    normalizedName: str
    normalizedParentName: str


class Property24Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.cache = {}

    def get_property_suggestions(
        self, search_text: str, search_type: str = "for-sale"
    ) -> Dict[str, str]:
        if search_text in self.cache:
            logging.info(f"Returning cached suggestions for {search_text}")
            return self.cache[search_text]

        try:
            logging.info(f"Fetching suggestions for {search_text}")
            response = self.session.get(suggestion_url.format(search_text=search_text))
            response.raise_for_status()
            properties = self.parse_response(response.json(), search_type)
            self.cache[search_text] = properties
            logging.info(f"Returning suggestions for {search_text}")
            return properties
        except (requests.RequestException, ValidationError) as e:
            logging.error(f"Failed to fetch suggestions for {search_text}: {e}")
            return []

    def parse_response(self, response_json: Dict, search_type: str) -> List[str]:
        try:
            suggestions = [Suggestion(**suggestion) for suggestion in response_json]
            properties = [
                (suggestion.name, self.build_search_url(suggestion, search_type))
                for suggestion in suggestions
            ]
            return properties
        except ValidationError as e:
            logging.error(f"Failed to parse response: {e}")
            return []

    def build_search_url(self, suggestion: Suggestion, search_type: str) -> str:
        search_type = search_type.lower()

        if search_type not in ["for-sale", "to-rent"]:
            logging.error(f"Invalid search type: {search_type}")
            return ""

        return search_url.format(search_type=search_type, suggestion=suggestion)
