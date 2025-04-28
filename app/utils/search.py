import logging
import requests
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

def google_search_links(wine_name: str, max_results: int = 20) -> list[str]:
    '''
    Custom Search API provides 100 search queries per day for free
    Each query returns maximum 10 results, can use pagination for more.
    Setting up max_results costs (max_results // 10) queries.
    '''
    api_key, cx = get_google_keys()
    query = f"{wine_name} wine review"
    
    def fetch_urls():
        seen_domains = set()
        results = []
        pages = (max_results + 9) // 10  # ceil(max_results / 10)

        for i in range(pages):
            start = 1 + i * 10
            params = {
                "key": api_key,
                "cx": cx,
                "q": query,
                "num": min(10, max_results - len(results)),
                "start": start
            }

            try:
                response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
                response.raise_for_status()
                for item in response.json().get("items", []):
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
                logger.exception(f"[Google API error page {i+1}]: {e}")
                raise GoogleSearchApiError(f"Google Search API failed: {e}")

        return results

    return get_cache_or_fetch("search", query, fetch_urls)