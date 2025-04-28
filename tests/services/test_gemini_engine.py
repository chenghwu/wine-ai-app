import pytest
from app.services.llm.gemini_engine import call_gemini_sync_with_retry

def test_call_gemini_sync_basic():
    prompt = "Extract wine name and vintage from 'Opus One 2015'"
    response = call_gemini_sync_with_retry(prompt)
    assert isinstance(response, str)