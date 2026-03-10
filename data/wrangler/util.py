import logging

from requests import Session
from requests.adapters import HTTPAdapter
from urllib3 import Retry

MAX_RETRIES = 5

# https://wikitech.wikimedia.org/wiki/Robot_policy
HEADERS = {
    "User-Agent": "SetSearch/0.0 (2975645S@student.gla.ac.uk) requests/2.32.5",
    "Accept-Encoding": "gzip"
}

def get_logger() -> logging.Logger:
    """Get a logger with a consistent format."""
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
    return logging.getLogger(__name__)

def get_http() -> Session:
    """Get a requests session with retry logic and sane headers."""
    adapter = HTTPAdapter(
        max_retries=Retry(total=MAX_RETRIES, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504],
                          raise_on_status=False), pool_connections=100, pool_maxsize=100)
    session = Session()
    session.mount("https://", adapter)
    session.headers.update(HEADERS)

    return session
