import requests
from requests.adapters import HTTPAdapter
from pydantic import BaseModel, ValidationError
from typing import List, Dict

from scraper.config import suggestion_url, build_search_url, retries, logging  # noqa: F401


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
        self.suggestions = []

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
            self.suggestions = self.parse_response(response.json(), search_type)
            self.cache[search_text] = self.suggestions
            logging.info(f"Returning suggestions for {search_text}")
            return self.suggestions
        except (requests.RequestException, ValidationError) as e:
            logging.error(f"Failed to fetch suggestions for {search_text}: {e}")
            return []

    def parse_response(self, response_json: Dict, search_type: str) -> List[str]:
        try:
            self.suggestions = [
                Suggestion(**suggestion) for suggestion in response_json
            ]
            self.suggestions = [
                {
                    "id": suggestion.id,
                    "name": suggestion.name,
                    "search_type": search_type,
                }
                for suggestion in self.suggestions
            ]
            return self.suggestions
        except ValidationError as e:
            logging.error(f"Failed to parse response: {e}")
            return []
