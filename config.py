import os

from dotenv import load_dotenv

load_dotenv()

DEFAULT_LEAGUE = "Mirage"
REQUEST_TIMEOUT = int(os.getenv("POE_REQUEST_TIMEOUT", "30"))

DEFAULT_HEADERS = {
    "User-Agent": os.getenv(
        "POE_USER_AGENT",
        (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/58.0.3029.110 Safari/537.36"
        ),
    ),
    "Content-Type": "application/json",
}

DEFAULT_COOKIES = {
    "POESESSID": os.getenv("POESESSID", ""),
    "cf_clearance": os.getenv("CF_CLEARANCE", ""),
}
