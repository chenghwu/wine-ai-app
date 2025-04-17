import pytest
from app.services import llm_search

@pytest.fixture
def sample_input():
    return {
        "wine_name": "Chateau Margaux",
        "winery": "Chateau Margaux",
        "year": "2015"
    }

def test_generate_wine_analysis_from_llm_in_dev_mode(sample_input, monkeypatch):
    """
    Functionally verify the mocked dev response:
    - Gemini API should NOT be called
    - Response should match mock logic
    - All values should be coherent and complete
    """

    # Protect against accidental API usage
    def fail_if_called(*args, **kwargs):
        raise AssertionError("Gemini API should not be called in dev mode")

    monkeypatch.setattr(llm_search, "genai", fail_if_called)

    response = llm_search.generate_wine_analysis_from_llm(sample_input)

    assert response["quality"] == "Very Good"
    assert response["price_estimate"] == "$120"
    assert "Mocked response" in response["notes"]
    assert "cassis" in response["notes"].lower()
    assert response["sources"] == ["Mocked: Wine Spectator", "Mocked: Decanter"]