from app.utils.cache import get_cache_or_fetch, get_cache_or_fetch_async

def test_get_cache_or_fetch_basic(tmp_path):
    result = get_cache_or_fetch(
        "test_category",
        "test_key",
        lambda: {"mock": "data"}
    )
    assert result["mock"] == "data"