from sentence_transformers import SentenceTransformer, util
from app.config import EMBEDDING_MODEL_NAME, WINE_NAME_SIM_THRESHOLD
from app.utils.cache import get_cache_path
from app.utils.logging import log_skipped
from typing import Awaitable, Callable
from pathlib import Path
import aiofiles
import asyncio
import json
import logging

logger = logging.getLogger(__name__)

_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
_embedding_cache = {}  # wine_name → tensor

async def get_relevant_text_and_cache(
    category: str,
    wine_name: str,
    url: str,
    fetch_func: Callable[[], Awaitable[str]]
) -> tuple[str, str]:
    """
    Fetch and cache content if semantically relevant to wine_name.
    """
    key = f"{wine_name}({url})"
    cache_path = Path(get_cache_path(category, key))
    if cache_path.exists():
        logger.info(f"[CACHE HIT] {key}")
        async with aiofiles.open(cache_path, "r") as f:
            cached = await f.read()
            return cached.strip(), url

    text = await fetch_func()
    if not text or len(text) < 100:
        log_skipped("Too short or empty", url)
        return "", url

    if wine_name not in _embedding_cache:
        _embedding_cache[wine_name] = _model.encode(wine_name, convert_to_tensor=True)
    query_embedding = _embedding_cache[wine_name]

    page_embedding = _model.encode(text, convert_to_tensor=True)
    score = util.cos_sim(query_embedding, page_embedding)[0].item()
    logger.info(f"[RELEVANCE] Cosine similarity for {url}: {score:.4f}")

    if score < WINE_NAME_SIM_THRESHOLD:
        log_skipped("Not relevant content", url)
        return "", url

    async with aiofiles.open(cache_path, "w") as f:
        await f.write(json.dumps(text, indent=2))

    return text, url

async def gather_in_chunks(tasks: list, chunk_size: int):
    """
    Runs a list of awaitable tasks in chunks to reduce memory pressure.

    Args:
        tasks: List of coroutines to run.
        chunk_size: Max number of coroutines to run at once.

    Returns:
        List of results from all tasks.
    """
    results = []
    for i in range(0, len(tasks), chunk_size):
        chunk = tasks[i:i + chunk_size]
        results.extend(await asyncio.gather(*chunk, return_exceptions=False))
    return results