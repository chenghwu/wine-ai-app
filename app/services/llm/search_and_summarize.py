import asyncio
import httpx
import logging
import requests
import time
import re
from bs4 import BeautifulSoup
from app.exceptions import GoogleSearchApiError, GeminiApiError
from app.services.llm.gemini_engine import summarize_with_gemini
from app.utils.cache import get_cache_or_fetch_async
from app.utils.search import google_search_links_with_retry
from app.utils.text_cleaning import is_probably_binary, clean_aggressively
from app.utils.url_utils import is_valid_url

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# The main crawling part, to be improved
async def fetch_full_text_from_url_async(url: str) -> str:
    # Skip PDF files for now
    if url.lower().endswith(".pdf"):
        logger.info(f"[SKIPPED] PDF file not supported: {url}")
        return ""

    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=3.0),
            headers={"User-Agent": USER_AGENT}
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

            raw_html = response.text
            # Early Normalization — skip non-HTML or broken pages
            if "<html" not in raw_html.lower() or len(raw_html) < 300:
                logger.warning(f"[SKIPPED] Too short or invalid HTML at {url}")
                return ""

            soup = BeautifulSoup(response.text, "html.parser")

            # Heuristic: Trimmed soup selector — target main content areas
            for tag in ["article", "main", "section", "div"]:
                content = soup.select_one(tag)
                if content:
                    text = content.get_text(separator="\n")
                    if len(text.strip()) > 200:
                        return clean_aggressively(text)

            logger.info(f"No main tag found, using fallback for: {url}")

            # Fallback to whole page
            fallback_text = soup.get_text(separator="\n")
            if is_probably_binary(fallback_text):
                logger.warning(f"[SKIPPED] Binary-like content from {url}")
                return ""

            # Apply full cleaning pipeline to remove noisy info
            cleaned = clean_aggressively(fallback_text)
            if len(cleaned.strip()) < 100:
                logger.warning(f"Fetched content is too short from {url}")
                return ""
            
            return cleaned

    except httpx.TimeoutException:
        logger.warning(f"[TIMEOUT] URL timed out: {url}")
        return ""
    except Exception as e:
        logger.error(f"[ERROR] Failed to fetch {url}: {e}")
        return ""

# Function to concurrently crawl and aggregate page content from links
async def aggregate_page_content_async(
    search_links: list[str],
    wine_name: str,
    max_concurrent: int = 5,
    slow_threshold: float = 5.0  # seconds
) -> str:
    sem = asyncio.Semaphore(max_concurrent)  # limits concurrent fetches
    wine_name_tokens = set(wine_name.lower().split())   # Normalize wine name tokens

    async def get_text(url: str) -> str:
        async with sem:
            key = f"{wine_name}({url})"
            try:
                start = time.perf_counter()
                raw_text = await get_cache_or_fetch_async(
                    "html",
                    key,
                    lambda: fetch_full_text_from_url_async(url)
                )
                duration = time.perf_counter() - start
                logger.info(f"[FETCHED] {url} in {duration:.2f}s")
                if duration > slow_threshold:
                    logger.warning(f"[SLOW] {url} took {duration:.2f}s to fetch")

                return raw_text or ""
            except Exception as e:
                logger.error(f"Failed to fetch or cache {url}: {e}")
                return ""

    # Must contain at least 2 matching tokens from wine_name
    def is_relevant(text: str) -> bool:
        text_lower = text.lower()
        count = 0
        for token in wine_name_tokens:
            if token in text_lower:
                count += 1
                if count >= 2:
                    return True
        return False

    # Fetch all text
    tasks = [get_text(url) for url in search_links]
    raw_results = await asyncio.gather(*tasks)

    filtered_texts = [
        text.strip() for text in raw_results
        if isinstance(text, str) and is_relevant(text)]

    if not filtered_texts:
        return {"error": "No relevant content found for summarization."}

    joined = "\n".join(filtered_texts)
    return re.sub(r"\{2,}", " ", joined).strip()

# Function to call google search engine API and gemini API to summarize wine info
async def summarize_wine_info(wine_name: str) -> dict:
    try:
        timings = {}

        # Step 1: Get all links from google search engine
        t0 = time.perf_counter()
        search_links = google_search_links_with_retry(wine_name)
        timings["google_search"] = time.perf_counter() - t0

        # Step 2: Crawl the links and aggregate contents
        logger.info("Getting details for searched results links...")
        t1 = time.perf_counter()
        web_content = await aggregate_page_content_async(search_links, wine_name)
        timings["aggregate_pages"] = time.perf_counter() - t1

        # Step 3: Gemini analysis
        logger.info("Sending to Gemini for analysis...")
        t2 = time.perf_counter()
        summary = summarize_with_gemini(wine_name, web_content, search_links)
        timings["gemini"] = time.perf_counter() - t2

        # Step 4: Normalize reference sources to list
        t3 = time.perf_counter()
        existing_sources = summary.get("reference_source", [])

        # If Gemini returned it as a string, convert to list
        if isinstance(existing_sources, str):
            existing_sources = [existing_sources]
            
        # Only keep valid urls
        existing_sources = [s for s in existing_sources if is_valid_url(s)]
        
        # Combine with Google search links
        summary["reference_source"] = list(set(search_links + existing_sources))
        timings["final_merge"] = time.perf_counter() - t3

        total = time.perf_counter() - t0
        logger.info("\nTiming breakdown:")
        for stage, duration in timings.items():
            logger.info(f"{stage.ljust(20)}: {duration:.2f}s")
        logger.info(f"{'TOTAL'.ljust(20)}: {total:.2f}s\n")

        return summary
    
    except (GoogleSearchApiError, GeminiApiError) as e:
        logger.error(f"Summarization error: {e}")
        return {"error": str(e)}

    except Exception as e:
        logger.error(f"Unexpected summarization error: {e}")
        return {"error": "Unexpected error during summarization."}