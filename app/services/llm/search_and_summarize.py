import asyncio
import logging
import requests
import time
import re
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig, CacheMode
from app.exceptions import GoogleSearchApiError, GeminiApiError
from app.services.llm.gemini_engine import summarize_with_gemini
from app.utils.cache import get_cache_or_fetch_async
from app.utils.search import google_search_links_with_retry
from app.utils.url_utils import is_valid_url

logger = logging.getLogger(__name__)

# Function to concurrently crawl and aggregate page content from links
async def aggregate_page_content_async(
    search_links: list[str],
    wine_name: str,
    max_concurrent: int = 5, # This might be less relevant with Crawl4AI's pooling
    slow_threshold: float = 5.0
) -> str:
    wine_name_tokens = set(wine_name.lower().split())

    browser_config = BrowserConfig(
        headless=True,
        # Consider adding user_agent if needed, e.g. from a global constant
    )
    # Using default run_config for now. fit_markdown is default.
    # Disable Crawl4AI's own cache to rely on the project's existing cache mechanism first.
    run_config = CrawlerRunConfig(cache_mode=CacheMode.DISABLED)
    
    crawler = AsyncWebCrawler(config=browser_config)
    await crawler.start() # Start the crawler (browser pool)

    async def get_content_with_crawl4ai(url: str) -> str:
        try:
            # Assuming crawler.arun returns an object with a markdown attribute
            # (e.g., result.markdown.fit_markdown or result.markdown.raw_markdown)
            logger.info(f"Fetching with Crawl4AI: {url}")
            crawl_result = await crawler.arun(url=url, config=run_config)
            if crawl_result.success and crawl_result.markdown:
                # Using fit_markdown if available, else raw_markdown
                content = crawl_result.markdown.fit_markdown if crawl_result.markdown.fit_markdown else crawl_result.markdown.raw_markdown
                return content
            logger.warning(f"Crawl4AI failed or returned no markdown for {url}. Error: {crawl_result.error_message if crawl_result.error_message else 'No markdown content'}")
            return ""
        except Exception as e:
            logger.error(f"Exception during Crawl4AI fetch for {url}: {e}")
            return ""

    async def get_text_via_cache(url: str) -> str:
        # key uses wine_name and url, consistent with old approach
        key = f"{wine_name}({url})" 
        try:
            start = time.perf_counter()
            # The lambda now calls get_content_with_crawl4ai
            raw_text = await get_cache_or_fetch_async(
                "html_crawl4ai", # New cache type to avoid conflicts
                key,
                lambda: get_content_with_crawl4ai(url) 
            )
            duration = time.perf_counter() - start
            logger.info(f"[FETCHED_C4AI] {url} in {duration:.2f}s (via cache or fetch)")
            if duration > slow_threshold and raw_text: # Check if raw_text is not empty
                 logger.warning(f"[SLOW_C4AI] {url} took {duration:.2f}s to fetch/process")
            return raw_text or ""
        except Exception as e:
            logger.error(f"Failed to fetch or cache {url} with Crawl4AI: {e}")
            return ""

    def is_relevant(text: str) -> bool:
        if not text: return False # Handle empty text
        text_lower = text.lower()
        count = 0
        for token in wine_name_tokens:
            if token in text_lower:
                count += 1
                if count >= 2:
                    return True
        return False

    try:
        tasks = [get_text_via_cache(url) for url in search_links]
        raw_results = await asyncio.gather(*tasks)

        filtered_texts = [
            text.strip() for text in raw_results
            if isinstance(text, str) and is_relevant(text) # Apply relevance filter
        ]

        if not filtered_texts:
            return {"error": "No relevant content found for summarization after Crawl4AI processing."}

        joined = "\n\n".join(filtered_texts) # Using double newline to better separate documents
        return re.sub(r"\n{3,}", "\n\n", joined).strip() # Normalize multiple newlines
    finally:
        await crawler.stop() # Ensure crawler is stopped

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