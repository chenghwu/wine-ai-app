import pytest
from app.services.llm.search_and_summarize import summarize_wine_info

@pytest.mark.asyncio
async def test_summarize_wine_info_success():
    result = await summarize_wine_info("Opus One 2015")
    assert isinstance(result, dict)
    assert "wine" in result or "error" in result