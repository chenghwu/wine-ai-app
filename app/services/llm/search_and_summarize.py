import asyncio
import httpx
import logging
import requests
from bs4 import BeautifulSoup
from app.exceptions import WineAppError, GoogleSearchApiError, GeminiApiError
from app.services.llm.gemini_engine import summarize_with_gemini
from app.utils.cache import get_cache_or_fetch_async
from app.utils.search import google_search_links_with_retry
from app.db.session import get_async_session
from app.db.crud.wine_summary import get_wine_summary_by_name, save_wine_summary
from sqlalchemy.ext.asyncio import AsyncSession
import time

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# The main crawling part, to be improved
async def fetch_full_text_from_url_async(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=10, headers={"User-Agent": USER_AGENT}) as client:
            response = await client.get(url)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, "html.parser")

            # Heuristic: Try article/main/section first
            for tag in ["article", "main", "section"]:
                content = soup.find(tag)
                if content and len(content.get_text(strip=True)) > 200:
                    return content.get_text(separator="\n")

            # Fallback to entire visible text
            return soup.get_text(separator="\n")

    except Exception as e:
        logger.error(f"[ERROR] Failed to fetch {url}: {e}")
        return ""

# Function to concurrently crawl and aggregate page content from links
async def aggregate_page_content_async(
    search_links: list[str],
    wine_name: str,
    max_concurrent: int = 5
) -> str:
    sem = asyncio.Semaphore(max_concurrent)  # limits concurrent fetches

    async def get_text(url: str) -> str:
        async with sem:
            key = f"{wine_name}({url})"
            try:
                return await get_cache_or_fetch_async(
                    "html",
                    key,
                    lambda: fetch_full_text_from_url_async(url)
                )
            except Exception as e:
                logger.error(f"Failed to fetch or cache {url}: {e}")
                return ""

    tasks = [get_text(url) for url in search_links]
    results = await asyncio.gather(*tasks)

    texts = [text for text in results if isinstance(text, str) and text.strip()]
    combined_text = "\n\n".join(texts)

    if not combined_text.strip():
        return {"error": "No content found to summarize."}

    return combined_text

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