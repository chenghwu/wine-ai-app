import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict

# Load environment variables (for local dev)
if "GEMINI_API_KEY" not in os.environ:
    load_dotenv()

env = os.getenv("ENV", "prod")  # Optional: control dev vs prod behavior
api_key = os.getenv("GEMINI_API_KEY")

if not api_key or not api_key.startswith("AIza"):
    raise ValueError("Missing or invalid GEMINI_API_KEY — make sure it's set in your .env")

# Configure Gemini
genai.configure(api_key=api_key)

# Gemini LLM model setup
model = genai.GenerativeModel("gemini-2.0-flash")

def generate_wine_analysis_from_llm(wine_query: Dict[str, str]) -> Dict:
    if env == "dev":
        # Return mocked data for local testing
        return {
            "quality": "Very Good",
            "notes": "Mocked: Deep ruby color, cassis, cedar, balanced acidity",
            "price_estimate": "$120",
            "sources": ["Mocked: Wine Spectator"]
        }

    # Step 1: Build prompt from wine query
    prompt = f"""
Analyze the following wine review snippets and generate a professional tasting note summary.

Wine: {wine_query['wine_name']}

Snippets:
{wine_query.get('raw_search_snippets', 'No snippets provided.')}

Please output:
- Quality rating
- Style & flavor notes
- Price estimate
- Sources if mentioned
"""

    # Step 2: Generate result using Gemini
    try:
        response = model.generate_content(prompt)
        return {
            "quality": "TBD",
            "notes": response.text.strip(),
            "price_estimate": "TBD",
            "sources": ["Gemini-generated"]
        }
    except Exception as e:
        return {
            "quality": "N/A",
            "notes": "Gemini API error",
            "price_estimate": "N/A",
            "sources": [],
            "error": str(e)
        }