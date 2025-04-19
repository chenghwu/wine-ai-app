import os
import requests
from bs4 import BeautifulSoup
from app.services.llm.llm_agent import summarize_with_gemini
from app.utils.cache import get_cache_or_fetch
from app.utils.search import google_search_links

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# The main crawling part, to be improved
def fetch_full_text_from_url(url: str) -> str:
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract main content heuristically
        for tag in ["article", "main", "section"]:
            content = soup.find(tag)
            if content and len(content.get_text(strip=True)) > 200:
                return content.get_text(separator="\n")

        return soup.get_text(separator="\n")  # fallback to full page text
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return ""


def summarize_wine_info(wine_name: str, use_mock: bool = False) -> dict:
    env = os.getenv("ENV", "prod")

    print(f"Searching for: {wine_name}")
    if env == "dev" and use_mock == True:
        print("Dev mode returning mock response:")
        return {
            "wine": wine_name,
            "appearance": "Deep ruby",
            "nose": "Medium+ aromas of cassis, tobacco, mocha",
            "palate": "Full-bodied, high acidity, ripe tannins, long finish",
            "aging": "Can age 8–12 years",
            "average_price": "$120",
            "quality": "Very Good",
            "analysis": f"""Based on the information available, it has complex aroma and flavor profile,
                            with red and black fruit, spice, and earthy notes.
                            The structure (tannins, acidity, alcohol) suggests good aging potential.""",
            "reference_source": ["wineSpectator.com"]
        }

    # Get all links from google search engine
    search_links = google_search_links(wine_name)
    
    # Crawl the links and aggregate contents
    def aggregate_page_content(search_links: list[str]) -> str:
        texts = []
        for url in search_links:
            key = f"{wine_name.lower()}({url})"
            cached = get_cache_or_fetch("html", key, lambda: fetch_full_text_from_url(url))
            if cached:
                texts.append(cached)
            
            ''' For now we want to retrieve as much info as possible
            if len(texts) >= 5:
                break  # limit to 5 good results
            '''
            
        combined_text = "\n\n".join(texts)
        if not combined_text.strip():
            return {"error": "No content found to summarize."}

        return combined_text

    print("Getting details for searched results links...")
    web_content = aggregate_page_content(search_links)

    print("Sending to Gemini for analysis...")
    summary = summarize_with_gemini(wine_name, web_content, search_links)

    # Normalize reference_source to list
    existing_sources = summary.get("reference_source", [])

    # If Gemini returned it as a string, convert to list
    if isinstance(existing_sources, str):
        existing_sources = [existing_sources]

    # Combine with Google search links
    summary["reference_source"] = list(set(search_links + existing_sources))

    return summary
