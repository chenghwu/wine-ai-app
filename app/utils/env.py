import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

def setup_gemini_env():
    env = os.getenv("ENV", "prod")
    api_key = os.getenv("GEMINI_API_KEY")

    if env == "prod" and (not api_key or not api_key.startswith("AIza")):
        raise ValueError("Missing or invalid GEMINI_API_KEY — check .env")

    model = None
    if env == "prod":
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.0-flash")

    return env, api_key, model

def get_google_keys():
    """Return (api_key, cx) for Google Custom Search"""
    google_api_key = os.getenv("GOOGLE_API_KEY")
    google_cx = os.getenv("GOOGLE_CX")
    
    return google_api_key, google_cx