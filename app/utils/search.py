import requests
from app.utils.env import get_google_keys
from app.utils.cache import get_cache_or_fetch

TRUSTED_DOMAINS = [
    "wineenthusiast.com",
    "winespectator.com",
    "decanter.com",
    "jamessuckling.com",
    "jancisrobinson.com",
    "totalwine.com",
    "b-21.com",
    "vivino.com",
    "wine-searcher.com"
]

def google_search_links(wine_name: str, max_results: int = 10) -> list[str]:
    api_key, cx = get_google_keys()
    query = f"{wine_name} wine review"
    
    def fetch_urls():
        try:
            params = {
                "key": api_key,
                "cx": cx,
                "q": query,
                "num": max_results
            }
            response = requests.get("https://www.googleapis.com/customsearch/v1", params=params)
            response.raise_for_status()
            results = response.json()

            urls = []
            for item in results.get("items", []):
                link = item.get("link")
                if any(domain in link for domain in TRUSTED_DOMAINS):
                    print(f"Trusted link {link}")
                
                # Include not only trusted domain links for now
                urls.append(link)

            return urls

        except Exception as e:
            print(f"Google Search API failed: {e}")
            return []

    return get_cache_or_fetch("search", query, fetch_urls)