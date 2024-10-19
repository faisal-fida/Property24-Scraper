from requests.packages.urllib3.util.retry import Retry
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("app.log")],
)


base_url = "https://www.property24.com"

suggest_file = "scraper/input/suggestions.json"
norm_suggest_file = "scraper/input/norm_suggestions.json"

cookies = {
    "P24UUEYED": "Id%3Dkpcghzvgv1ekcbsov5lfet2z%26Date%3D638646147517108882",
    "P24CPA": "2021-06-29T00:27:41.2870000",
    "P24U": "%7B%22CityId%22%3A246%2C%22AutomaticallySendReportedListingConfirmationEmail%22%3Atrue%2C%22UserNotificationUIState%22%3A0%2C%22ExpectedUnreadNotificationCount%22%3A0%7D",
    "P24SEYED": "13904585-d743-44d9-ada0-1659bd208883",
    "__RequestVerificationToken": "CfDJ8JEQbpTk1lRChYiZH2_9kOWUjHRxqwxXKotpFxaryVNoA5WxNILIwf3R45Eb9B-757Bb8vQnGqCLQ3u3qMG9_3sL2eWanHkqRQd9sgfcTzy1LkUb5Nl3kRGxsFCFD1tm1MwhFfNIArvdmAXe3NUIvXw",
}

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "priority": "u=0, i",
    "sec-ch-ua": '"Chromium";v="130", "Google Chrome";v="130", "Not?A_Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
}


retries = Retry(total=5, backoff_factor=0.1, status_forcelist=[500, 502, 503, 504])