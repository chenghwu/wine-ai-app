import logging
import requests
import time
from urllib.parse import urlparse
from app.exceptions import GoogleSearchApiError
from app.utils.cache import get_cache_or_fetch
from app.utils.env import get_google_keys

logger = logging.getLogger(__name__)

TRUSTED_DOMAINS = [
    "wineenthusiast.com",
    "winespectator.com",
    "decanter.com",
    "jamessuckling.com",
    "jancisrobinson.com",
    "totalwine.com",
    "b-21.com",
    "vivino.com",
    "wine-searcher.com",
    "wine.com",
    "robertparker.com",
    "vinous.com",
    "thewinecellarinsider.com"
]

def google_search_links_with_retry(
    wine_name: str,
    max_results: int = 12,
    max_retries: int = 3,  # Reduced from 5 to 3 for faster failure recovery
    delay_seconds: float = 2.0
) -> list[str]:
    '''
    Custom Search API provides 100 search queries per day for free
    Each query returns maximum 10 results, can use pagination for more.
    Setting up max_results costs (max_results // 10) queries.
    '''
    api_key, cx = get_google_keys()
    query = f"{wine_name} wine review"
    
    def extract_google_spelling_correction(response_json: dict) -> str | None:
        """Extract spelling suggestion from Google Custom Search JSON."""
        try:
            return response_json["spelling"]["correctedQuery"]
        except KeyError:
            return None

    def fetch_urls(query: str) -> list[str]:
        seen_domains = set()
        results = []
        pages = (max_results + 9) // 10  # ceil(max_results / 10)

        for page in range(pages):
            start = 1 + page * 10
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                "key": api_key,
                "cx": cx,
                "q": query,
                "num": min(10, max_results - len(results)),
                "start": start
            }

            for attempt in range(1, max_retries + 1):
                try:
                    response = requests.get(url, params=params)
                    response.raise_for_status()
                    data = response.json()
                    items = data.get("items", [])

                    # Try spelling correction if no results
                    if not items:
                        if (suggested := extract_google_spelling_correction(data)):
                            logger.info(f"[Google API] No results, retrying with suggestion: {suggested}")
                            return fetch_urls(suggested)
                        return []

                    for item in items:
                        link = item.get("link")
                        if not link:
                            continue

                        domain = urlparse(link).netloc.replace("www.", "")
                        if domain not in seen_domains:
                            seen_domains.add(domain)
                            results.append(link)

                            # Include not only trusted domain links for now
                            if any(t in domain for t in TRUSTED_DOMAINS):
                                logger.info(f"Trusted link: {link}")

                        if len(results) >= max_results:
                            return results

                except Exception as e:
                    if attempt == max_retries:
                        logger.exception(f"[Google API error page {page+1}]: {e}")
                        raise GoogleSearchApiError(f"Google Search API failed: {e}")

                    wait_time = delay_seconds * attempt     #linear backoff
                    logger.warning(f"Google API call failed (attempt {attempt}), retrying in {wait_time:.1f}s... Error: {e}")
                    time.sleep(wait_time)

        return results

    return get_cache_or_fetch("search", query, lambda: fetch_urls(query))