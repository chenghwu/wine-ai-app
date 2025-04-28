import pytest
from app.services.handlers.wine_summary_handler import parse_wine_query_with_gemini

def test_parse_wine_query_with_gemini_success():
    query = "Opus One 2015"
    result = parse_wine_query_with_gemini(query)
    assert isinstance(result, dict)
    assert "wine_name" in result
    assert "vintage" in result