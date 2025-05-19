import os
import sys
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Patch DATABASE_URL during local pytest to use localhost
if "pytest" in sys.modules:
    db_url = os.getenv("DATABASE_URL", "")
    if "postgres:5432" in db_url:
        patched_url = db_url.replace("postgres:5432", "localhost:5432")
        os.environ["DATABASE_URL"] = patched_url
        print(f"\nPatched DATABASE_URL for local pytest: {patched_url}")

def setup_gemini_env():
    env = os.getenv("ENV", "prod")
    api_key = os.getenv("GEMINI_API_KEY")

    if env == "prod" and (not api_key or not api_key.startswith("AIza")):
        raise ValueError("Missing or invalid GEMINI_API_KEY — check .env")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    return env, api_key, model

def get_google_keys():
    """Return (api_key, cx) for Google Custom Search"""
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cx = os.getenv("GOOGLE_CX")
    
    return google_api_key, google_cx