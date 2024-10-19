import requests
from requests.adapters import HTTPAdapter

from scraper.config import retries, logging  # noqa: F401


class Property24Client:
    def __init__(self):
        self.session = requests.Session()
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        self.cache = {}
        self.suggestions = []

    def get_property_suggestions(self):
        pass

    def parse_response(self):
        pass
