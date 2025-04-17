import os
import json
from typing import Callable, Any
from hashlib import sha1

CACHE_ROOT = "cache"


def get_cache_path(category: str, key: str) -> str:
    os.makedirs(os.path.join(CACHE_ROOT, category), exist_ok=True)
    hashed_key = sha1(key.encode()).hexdigest()[:10]
    return os.path.join(CACHE_ROOT, category, f"{hashed_key}.json")


def get_cache_or_fetch(category: str, key: str, fetch_func: Callable[[], Any]) -> Any:
    """
    Check if result is already cached. If not, fetch it and cache the result.
    """
    path = get_cache_path(category, key)
    if os.path.exists(path):
        with open(path, "r") as f:
            print(f"Cache hit: {path}")
            return json.load(f)

    print(f"Cache miss: {key} — calling fetch function...")
    result = fetch_func()
    with open(path, "w") as f:
        json.dump(result, f, indent=2)
    return result
