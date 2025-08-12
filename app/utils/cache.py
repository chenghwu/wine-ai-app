import aiofiles
import json
import logging
import os
import time
from typing import Callable, Awaitable, Any, Optional
from hashlib import sha1, sha256

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


# Menu analysis specific cache functions
def cache_menu_analysis(image_hash: str, analysis_result: dict, ttl_minutes: int = 15) -> None:
    """
    Cache menu analysis result with TTL for temporary storage.
    Used to avoid reprocessing identical menu photos.
    """
    if IS_PROD:
        logger.debug(f"[Prod] Skipping menu analysis cache write for: {image_hash}")
        return

    cache_data = {
        "result": analysis_result,
        "cached_at": time.time(),
        "ttl_seconds": ttl_minutes * 60
    }
    
    path = get_cache_path("menu", image_hash)
    try:
        with open(path, "w") as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to cache menu analysis: {e}")


def get_cached_menu_analysis(image_hash: str) -> Optional[dict]:
    """
    Retrieve cached menu analysis if exists and not expired.
    Returns None if cache miss or expired.
    """
    if IS_PROD:
        logger.debug(f"[Prod] Skipping menu analysis cache read for: {image_hash}")
        return None

    path = get_cache_path("menu", image_hash)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r") as f:
            cache_data = json.load(f)
        
        cached_at = cache_data.get("cached_at", 0)
        ttl_seconds = cache_data.get("ttl_seconds", 900)  # default 15 min
        
        if time.time() - cached_at > ttl_seconds:
            logger.info(f"Menu analysis cache expired: {image_hash}")
            os.remove(path)  # cleanup expired cache
            return None
        
        return cache_data.get("result")
        
    except Exception as e:
        logger.warning(f"Failed to read menu analysis cache: {e}")
        return None


def generate_image_hash(image_data: bytes) -> str:
    """
    Generate consistent hash for image data.
    Used for caching menu analysis results.
    """
    return sha256(image_data).hexdigest()[:16]  # 16 chars for shorter file names


def cache_wine_recommendations(food_hash: str, recommendations: dict, ttl_minutes: int = 15) -> None:
    """
    Cache wine recommendations for food items with TTL.
    Used to avoid regenerating recommendations for similar food descriptions.
    """
    if IS_PROD:
        logger.debug(f"[Prod] Skipping wine recommendations cache write for: {food_hash}")
        return

    cache_data = {
        "recommendations": recommendations,
        "cached_at": time.time(),
        "ttl_seconds": ttl_minutes * 60
    }
    
    path = get_cache_path("pairing", food_hash)
    try:
        with open(path, "w") as f:
            json.dump(cache_data, f, indent=2)
    except Exception as e:
        logger.warning(f"Failed to cache wine recommendations: {e}")


def get_cached_wine_recommendations(food_hash: str) -> Optional[dict]:
    """
    Retrieve cached wine recommendations if exists and not expired.
    Returns None if cache miss or expired.
    """
    if IS_PROD:
        logger.debug(f"[Prod] Skipping wine recommendations cache read for: {food_hash}")
        return None

    path = get_cache_path("pairing", food_hash)
    if not os.path.exists(path):
        return None

    try:
        with open(path, "r") as f:
            cache_data = json.load(f)
        
        cached_at = cache_data.get("cached_at", 0)
        ttl_seconds = cache_data.get("ttl_seconds", 900)  # default 15 min
        
        if time.time() - cached_at > ttl_seconds:
            logger.info(f"Wine recommendations cache expired: {food_hash}")
            os.remove(path)  # cleanup expired cache
            return None
        
        return cache_data.get("recommendations")
        
    except Exception as e:
        logger.warning(f"Failed to read wine recommendations cache: {e}")
        return None


def cleanup_expired_cache() -> None:
    """
    Cleanup expired cache files for menu and pairing categories.
    Can be called periodically or on app startup.
    """
    if IS_PROD:
        return
    
    categories = ["menu", "pairing"]
    for category in categories:
        cache_dir = os.path.join(CACHE_ROOT, category)
        if not os.path.exists(cache_dir):
            continue
            
        for filename in os.listdir(cache_dir):
            if not filename.endswith(".json"):
                continue
                
            file_path = os.path.join(cache_dir, filename)
            try:
                with open(file_path, "r") as f:
                    cache_data = json.load(f)
                
                cached_at = cache_data.get("cached_at", 0)
                ttl_seconds = cache_data.get("ttl_seconds", 900)
                
                if time.time() - cached_at > ttl_seconds:
                    os.remove(file_path)
                    logger.info(f"Removed expired cache file: {file_path}")
                    
            except Exception as e:
                logger.warning(f"Failed to check cache file {file_path}: {e}")
                # Remove corrupted cache files


def clear_all_cache() -> dict:
    """
    Clear all cache files from all categories.
    This completely removes all cached data.
    """
    if IS_PROD:
        logger.warning("Cache clearing is disabled in production mode")
        return {"status": "disabled", "message": "Cache clearing is disabled in production mode"}
    
    cleared_files = 0
    cleared_categories = []
    errors = []
    
    try:
        if not os.path.exists(CACHE_ROOT):
            return {"status": "success", "message": "No cache directory found", "files_cleared": 0}
        
        # Get all cache categories
        for category in os.listdir(CACHE_ROOT):
            category_path = os.path.join(CACHE_ROOT, category)
            if not os.path.isdir(category_path):
                continue
                
            category_files = 0
            try:
                for filename in os.listdir(category_path):
                    file_path = os.path.join(category_path, filename)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                        category_files += 1
                        cleared_files += 1
                
                if category_files > 0:
                    cleared_categories.append(f"{category} ({category_files} files)")
                    logger.info(f"Cleared {category_files} files from {category} cache")
                    
            except Exception as e:
                error_msg = f"Failed to clear {category} cache: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        result = {
            "status": "success",
            "files_cleared": cleared_files,
            "categories_cleared": cleared_categories,
        }
        
        if errors:
            result["errors"] = errors
            
        logger.info(f"Cache clearing completed: {cleared_files} files cleared from categories: {cleared_categories}")
        return result
        
    except Exception as e:
        error_msg = f"Failed to clear cache: {str(e)}"
        logger.error(error_msg)
        return {"status": "error", "message": error_msg}