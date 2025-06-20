import google.generativeai as genai
import logging
import os
import time
from app.exceptions import GeminiApiError
from app.constants.aroma_lexicons import AROMA_LEXICONS
from app.utils.env import setup_gemini_env
from app.utils.llm_parsing import parse_json_from_text
from app.prompts.wine_prompts import get_sat_prompt, get_wine_from_query_prompt

logger = logging.getLogger(__name__)

def call_gemini_sync_with_retry(
    prompt: str,
    temperature: float = 0.7,
    max_retries: int = 5,
    delay_seconds: float = 2.0
) -> str:
    """
    Call Gemini synchronously using the GenerativeAI client.
    Temperature: 0 (more factual) - 1.0 (exploratory)
    """
    _, _, model = setup_gemini_env()
    
    for attempt in range(1, max_retries + 1):
        try:
            response = model.generate_content(
                prompt,
                generation_config={"temperature": temperature}
            )
            return response.text

        except Exception as e:
            if attempt == max_retries:
                raise GeminiApiError(f"Gemini API failed after {max_retries} retries: {e}")

            wait_time = delay_seconds * attempt     # linear backoff
            logger.warning(f"Gemini API call failed (attempt {attempt}), retrying in {wait_time}s... Error: {e}")
            time.sleep(wait_time)

def summarize_with_gemini(wine_name: str, content: str, sources: list[str]) -> dict:
    """
    Use Gemini to summarize wine info using SAT-style prompt and parse JSON output.
    """
    prompt = get_sat_prompt(wine_name, content, sources, AROMA_LEXICONS)
    try:
        raw_text = call_gemini_sync_with_retry(prompt, temperature=0.7)
        logger.info(f"Gemini raw output:\n{raw_text}")
        parsed = parse_json_from_text(raw_text)

        if "error" in parsed:
            raise GeminiApiError(f"Gemini error: {parsed['error']}, 'wine': {wine_name}")

        return parsed
    
    except Exception as e:
        raise GeminiApiError(f"Gemini API call for summary failed: {e}")

def parse_wine_query_with_gemini(query: str) -> dict:
    """
    Use Gemini to extract structured wine info (winery, name, vintage) from a free-form query.
    """
    prompt = get_wine_from_query_prompt(query)
    try:
        raw_text = call_gemini_sync_with_retry(prompt, temperature=0.3)
        parsed = parse_json_from_text(raw_text)

        # Ensure structure
        if not isinstance(parsed, dict):
            return {
                "winery": "",
                "wine_name": query.strip(),
                "vintage": ""
            }
        
        return {
            "winery": parsed.get("winery", ""),
            "wine_name": parsed.get("wine_name", query.strip()),
            "vintage": parsed.get("vintage", "")
        }

    except Exception as e:
        error_msg = "Gemeni failed to parse user query"
        logger.error(f"{error_msg}: {e}")
        raise GeminiApiError(f"{error_msg}: {e}")