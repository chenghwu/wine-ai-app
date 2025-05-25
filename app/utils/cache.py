import aiofiles
import json
import logging
import os
from typing import Callable, Awaitable, Any
from hashlib import sha1

logger = logging.getLogger(__name__)

CACHE_ROOT = "cache"
IS_PROD = os.getenv("ENV") == "prod"

def get_cache_path(category: str, key: str) -> str:
    os.makedirs(os.path.join(CACHE_ROOT, category), exist_ok=True)
    hashed_key = sha1(key.encode()).hexdigest()[:10]
    return os.path.join(CACHE_ROOT, category, f"{hashed_key}.json")

def get_cache_or_fetch(category: str, key: str, fetch_func: Callable[[], Any]) -> Any:
    """
    Check if result is already cached.
    If not, fetch it and cache the result.
    Skip all caching in production.
    """
    if IS_PROD:
        logger.debug(f"[Prod] Skipping cache read/write for: {key}")
        return fetch_func()

    path = get_cache_path(category, key)
    if os.path.exists(path):
        with open(path, "r") as f:
            print(f"Cache hit: {path}")
            return json.load(f)

    logger.info(f"Cache miss: {key} — calling fetch function...")
    result = fetch_func()
    with open(path, "w") as f:
        json.dump(result, f, indent=2)
    return result

async def get_cache_or_fetch_async(category: str, key: str, fetch_func: Callable[[], Awaitable[Any]]) -> Any:
    """
    Checks if file exists, loads JSON if cached.
    Otherwise awaits fetch_func() and caches the result.
    Skip all caching in production.
    """
    if IS_PROD:
        logger.debug(f"[Prod] Skipping async cache read/write for: {key}")
        return await fetch_func()

    path = get_cache_path(category, key)

    if os.path.exists(path):
        async with aiofiles.open(path, "r") as f:
            logger.info(f"Cache hit: {path}")
            contents = await f.read()
            return json.loads(contents)

    logger.info(f"Cache miss: {key} — calling async fetch function...")
    result = await fetch_func()

    if not result:
        logger.warning(f"Empty result for {key}")
    elif isinstance(result, (str, dict)) and result:
        # Only cache if result is a non-empty string, valid JSON-like object, or dict-based
        async with aiofiles.open(path, "w") as f:
            await f.write(json.dumps(result, indent=2))
    else:
        logger.info(f"Skipping cache save: {key}")
    
    return result