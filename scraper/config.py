from requests.packages.urllib3.util.retry import Retry
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("app.log")],
)


base_url = "https://www.property24.com"

suggestion_url = base_url + "/autocomplete/area-suggestions?searchText={search_text}"

search_url = base_url + "/{search_type}/{suggestion.normalizedName}/{suggestion.id}"

search_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36"
}


retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])
