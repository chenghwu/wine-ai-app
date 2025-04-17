import os
import pytest
from app.services.llm.llm_agent import summarize_with_gemini

@pytest.fixture
def dummy_wine_info():
    return {
        "wine_name": "Opus One 2015",
        "content": "Aromas of cassis, tobacco leaf, mocha. Firm tannins with a long finish."
    }


def test_summarize_with_gemini_in_dev(monkeypatch, dummy_wine_info):
    """
    Test that the Gemini function returns mock result in dev mode.
    We patch the ENV variable to 'dev' to avoid API call.
    """
    monkeypatch.setenv("ENV", "dev")

    result = summarize_with_gemini(
        dummy_wine_info["wine_name"],
        dummy_wine_info["content"]
    )

    assert result["wine"] == "Opus One 2015"
    assert result["appearance"] != "N/A"
    assert "palate" in result
    assert "quality" in result


def test_summarize_with_gemini_in_prod(monkeypatch, dummy_wine_info):
    """
    Simulate Gemini prod mode call with mocked response.
    """
    monkeypatch.setenv("ENV", "prod")

    class MockResponse:
        text = '{"wine": "Opus One 2015", "appearance": "Deep ruby", "nose": "Cassis", "palate": "Full body", "quality": "Outstanding", "aging": "15+ years"}'

    class MockModel:
        def generate_content(self, prompt):
            return MockResponse()

    monkeypatch.setattr("app.services.llm.llm_agent.genai.GenerativeModel", lambda _: MockModel())

    result = summarize_with_gemini(
        dummy_wine_info["wine_name"],
        dummy_wine_info["content"]
    )

    assert result["wine"] == "Opus One 2015"
    assert result["quality"] == "Outstanding"
    assert result["aging"].startswith("15")