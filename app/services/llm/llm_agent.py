import os
import google.generativeai as genai
from dotenv import load_dotenv
from app.utils.cache import get_cache_or_fetch
from app.utils.env import setup_gemini_env
from app.prompts.wine_prompts import get_sat_prompt

def summarize_with_gemini(wine_name: str, content: str, sources: list[str]) -> dict:
    def fetch_gemini():
        env, _, model = setup_gemini_env()

        # Change prompt for different possible results for metrics
        prompt = get_sat_prompt(wine_name, content, sources)

        try:
            response = model.generate_content(prompt)
            text = response.text
            print("Gemini raw output:\n", text)

            # Try to extract JSON-like structure
            import json, re
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))

            return {"raw_output": text.strip()}

        except Exception as e:
            print(f"Gemini API error: {e}")
            return {
                "wine": wine_name,
                "error": str(e)
            }

    return get_cache_or_fetch("summary", wine_name, fetch_gemini)