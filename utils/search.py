import os
import json
from typing import List, Dict
from scraper.config import logging, suggest_file, norm_suggest_file


class SearchSuggestions:
    def __init__(self):
        self.cache = {}
        self.suggestions = []
        self.json_file_obj = None

    def read_json(self, file_path: str) -> Dict:
        with open(file_path, "r") as f:
            return json.load(f)

    def write_json(self, file_path: str, data: Dict):
        with open(file_path, "w") as f:
            json.dump(data, f)

    def load_suggestions(self):
        if not self.json_file_obj:
            if not os.path.exists(suggest_file):
                logging.error(f"{suggest_file} file not found")
                return {}

            if not os.path.exists(norm_suggest_file):
                self.json_file_obj = self.read_json(suggest_file)
                self.json_file_obj = [
                    {
                        "id": suggestion.get("id", ""),
                        "address": suggestion.get("name", "")
                        + ", "
                        + suggestion.get("parentName", ""),
                    }
                    for key, value in self.json_file_obj.items()
                    for suggestion in value
                ]
                self.write_json(norm_suggest_file, self.json_file_obj)
            else:
                self.json_file_obj = self.read_json(norm_suggest_file)

    def get_property_suggestions(
        self, search_text: str, search_type: str = "for-sale"
    ) -> List[Dict]:
        self.load_suggestions()

        if search_text in self.cache:
            logging.info("Returning cached suggestions.")
            return self.cache[search_text]

        try:
            logging.info(f"Fetching suggestions for {search_text}")
            self.suggestions = list(self.search_suggestions(search_text))
            self.cache[search_text] = self.suggestions
            return self.suggestions
        except Exception as e:
            logging.error(f"Failed to get suggestions: {e}")
            return []

    def search_suggestions(self, search_text: str) -> List[str]:
        for suggestion in self.json_file_obj:
            if search_text.lower() in suggestion.get("address", "").lower():
                yield suggestion
        return []
