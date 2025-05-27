import asyncio
import httpx
import logging
import os
import re
import time
from bs4 import BeautifulSoup
from app.exceptions import GoogleSearchApiError, GeminiApiError
from app.services.llm.gemini_engine import summarize_with_gemini
from app.utils.fetcher import get_relevant_text_and_cache
from app.utils.logging import log_skipped
from app.utils.search import google_search_links_with_retry
from app.utils.text_cleaning import is_probably_binary, clean_aggressively
from app.utils.url_utils import is_valid_url

logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
MAX_CONCURRENT_FETCHES = int(os.getenv("MAX_CONCURRENT_FETCHES", 5))
MAX_CONTENT_LENGTH = 2 * 1024 * 1024  # 2MB

# Helper: Extract and clean fallback text from full page soup
def extract_fallback_text(soup: BeautifulSoup, url: str) -> str:
    fallback_text = soup.get_text(separator="\n")
    if is_probably_binary(fallback_text):
        log_skipped("Binary-like content", url)
        return ""
    cleaned = clean_aggressively(fallback_text)
    if len(cleaned.strip()) < 100:
        log_skipped("Fetched content is too short", url)
        return ""
    return cleaned

def extract_clean_text_block(
    soup: BeautifulSoup,
    url: str,
    tags: tuple[str, ...] = ("article", "main", "section", "div"),
    min_len: int = 300
) -> str:
    """
    Extracts clean text from specified HTML tags.
    Falls back to full page if nothing sufficient is found.
    """
    for tag in tags:
        for section in soup.select(tag):
            text = section.get_text(separator="\n")
            if len(text.strip()) >= min_len:
                return clean_aggressively(text)

    log_skipped("No sufficient content in main tags", url)
    return extract_fallback_text(soup, url)

# The main crawling function
async def fetch_full_text_from_url_async(url: str) -> str:
    if url.lower().endswith(".pdf"):
        log_skipped("PDF file not supported", url)
        return ""

    # GET request for actual content
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(10.0, connect=3.0),
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True
        ) as client:
            response = await client.get(url)
            response.raise_for_status()

            headers = response.headers
            content_type = headers.get("content-type", "").lower()
            if not content_type.startswith(("text/html", "text/plain", "application/xhtml+xml", "application/xml")):
                log_skipped(f"Non-HTML content: {content_type}", url)
                return ""

            content_length_str = headers.get("content-length")
            if content_length_str:
                try:
                    content_length = int(content_length_str)
                    if content_length > MAX_CONTENT_LENGTH:
                        log_skipped(f"Content too large: {content_length}", url)
                        return ""
                except ValueError:
                    logger.warning(f"Invalid content-length: {content_length_str} from GET for {url}")

            raw_html = response.text
            if "<html" not in raw_html.lower() or len(raw_html) < 300:
                log_skipped("Too short or invalid HTML", url)
                return ""

            soup = BeautifulSoup(raw_html, "html.parser")
            return extract_clean_text_block(soup, url)

    except httpx.TimeoutException:
        logger.warning(f"[TIMEOUT] GET request timed out: {url}")
    except httpx.HTTPStatusError as e:
        logger.error(f"[HTTP ERROR] GET request failed for {url} with status {e.response.status_code}")
    except Exception as e:
        logger.error(f"[ERROR] GET request failed for {url}: {e}")

    return ""

# Function to concurrently crawl and aggregate page content from links
async def aggregate_page_content_async(
    search_links: list[str],
    wine_name: str,
    max_concurrent: int = MAX_CONCURRENT_FETCHES,
    slow_threshold: float = 5.0  # seconds
) -> str:
    logger.info(f"[SETUP] Using max_concurrent={max_concurrent} for fetching.")
    sem = asyncio.Semaphore(max_concurrent)  # limits concurrent fetches

    async def get_text(url: str) -> tuple[str, str]:
        async with sem:
            try:
                start = time.perf_counter()
                async def fetch():
                    return await fetch_full_text_from_url_async(url)

                raw_text, final_url = await get_relevant_text_and_cache("html", wine_name, url, fetch)
                duration = time.perf_counter() - start
                status = "SLOW" if duration > slow_threshold else "OK"
                logger.info(f"[FETCHED-{status}] {final_url} in {duration:.2f}s")

                return raw_text, final_url
            except Exception as e:
                logger.error(f"Failed to fetch or cache {url}: {e}")
                return "", url

    # Concurrently fetch all text
    tasks = [get_text(url) for url in search_links]
    raw_results = await asyncio.gather(*tasks, return_exceptions=False)
    #raw_results = await gather_in_chunks(tasks, max_concurrent)

    pairs = [result for result in raw_results if result is not None]
    if not pairs:
        return {"error": "No relevant content found for summarization."}

    texts, urls = zip(*pairs)
    joined = "\n".join(texts)
    return re.sub(r"\{2,}", " ", joined).strip()

# Function to call google search engine API and gemini API to summarize wine info
async def summarize_wine_info(wine_name: str) -> dict:
    try:
        timings = {}

        # Step 1: Get all links from google search engine
        t0 = time.perf_counter()
        search_links = google_search_links_with_retry(wine_name)
        if not isinstance(search_links, list):
            logger.error(f"Failed to retrieve search links for {wine_name}. Received: {search_links}")
            return {"error": "Failed to retrieve search links."}
        timings["google_search"] = time.perf_counter() - t0

        # Step 2: Crawl the links and aggregate contents
        logger.info("Getting details for searched results links...")
        t1 = time.perf_counter()
        web_content = await aggregate_page_content_async(search_links, wine_name)
        timings["aggregate_pages"] = time.perf_counter() - t1

        # CRITICAL FIX and check before Gemini call
        if isinstance(web_content, dict) and "error" in web_content:
            logger.error(f"Error during content aggregation for {wine_name}: {web_content['error']}")
            return web_content

        if not isinstance(web_content, str):
            logger.error(f"Web content is not a string after aggregation for {wine_name}: {type(web_content)}. Content: {web_content}")
            return {"error": "Failed to process web content for summarization."}

        # Step 3: Gemini analysis (proceed only if web_content is a valid string)
        logger.info(f"[GEMINI] Started summarizing web content (length: {len(web_content):,}) for {wine_name}...")
        t2 = time.perf_counter()
        summary = summarize_with_gemini(wine_name, web_content, search_links)
        timings["gemini"] = time.perf_counter() - t2

        # Step 4: Normalize reference sources to list and combine
        t3 = time.perf_counter()
        existing_sources = summary.get("reference_source", [])
        if isinstance(existing_sources, str):   # conver to list if returned as string
            existing_sources = [existing_sources]
        
        # Combine with Google search links
        summary["reference_source"] = list({*search_links, *filter(is_valid_url, existing_sources)})
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