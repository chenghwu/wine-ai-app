import os
import sys
import google.generativeai as genai
from app.config import ENV, GEMINI_API_KEY, GEMINI_MODEL, DATABASE_URL, GOOGLE_API_KEY, GOOGLE_CX
import logging

logger = logging.getLogger(__name__)

# Patch DATABASE_URL during local pytest to use localhost
if "pytest" in sys.modules and "postgres:5432" in DATABASE_URL:
        patched_url = DATABASE_URL.replace("postgres:5432", "localhost:5432")
        os.environ["DATABASE_URL"] = patched_url
        logger.info(f"\nPatched DATABASE_URL for local pytest: {patched_url}")

def setup_gemini_env():
    if ENV == "prod" and (not GEMINI_API_KEY or not GEMINI_API_KEY.startswith("AIza")):
        raise ValueError("Missing or invalid GEMINI_API_KEY — check .env")

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    logger.info(f"Using Gemini Model: {GEMINI_MODEL}")

    return ENV, GEMINI_API_KEY, model

def get_google_keys():
    """Return (api_key, cx) for Google Custom Search"""
    return GOOGLE_API_KEY, GOOGLE_CX