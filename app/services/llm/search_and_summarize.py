import os
import requests
from bs4 import BeautifulSoup
from app.services.llm.llm_agent import summarize_with_gemini
from app.utils.cache import get_cache_or_fetch
from app.utils.search import google_search_links

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"


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


def summarize_wine_info(wine_name: str) -> dict:
    print(f"Searching for: {wine_name}")
    search_results = google_search_links(wine_name)

    print("Getting details for searched results links...")
    texts = []
    for url in search_results:
        key = f"{wine_name}:{url}"
        cached = get_cache_or_fetch("html", key, lambda: fetch_full_text_from_url(url))
        if cached:
            texts.append(cached)
        if len(texts) >= 5:
            break  # limit to 5 good results

    combined_text = "\n\n".join(texts)
    if not combined_text.strip():
        return {"error": "No content found to summarize."}

    print("Sending to Gemini for analysis...")
    return summarize_with_gemini(wine_name, combined_text)
