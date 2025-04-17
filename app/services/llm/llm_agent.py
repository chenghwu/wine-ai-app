import os
import google.generativeai as genai
from dotenv import load_dotenv
from app.utils.cache import get_cache_or_fetch
from app.utils.env import setup_gemini_env

def summarize_with_gemini(wine_name: str, content: str) -> dict:
    def fetch_gemini():
        env, _, model = setup_gemini_env()

        if env == "dev":
            print("Dev mode: returning mocked Gemini result")
            return {
                "wine": wine_name,
                "appearance": "Deep ruby",
                "nose": "Medium+ aromas of cassis, tobacco, mocha",
                "palate": "Full-bodied, high acidity, ripe tannins, long finish",
                "quality": "Very Good",
                "aging": "Can age 8–12 years"
            }

        prompt = f"""
Act as a certified wine expert trained in WSET Level 4 Systematic Approach to Tasting.
Based on the following information about the wine \"{wine_name}\", please provide a detailed SAT-style analysis.

Content:
{content}

Your response must include:
- Appearance (clarity, intensity, color)
- Nose (aromas, intensity)
- Palate (sweetness, acidity, tannin, alcohol, body, flavour intensity, flavour characteristics, finish)
- Quality level (Poor, Acceptable, Good, Very Good, Outstanding)
- Aging potential and why
- Average price
- Why and how do you get this conclusion

Output format must be structured like this JSON:
{{
"wine": "{wine_name}",
"appearance": "...",
"nose": "...",
"palate": "...",
"quality": "...",
"aging": "...",
"average price": "...",
"analysis": "...",
"reference source": "..."
}}
"""

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
                "quality": "N/A",
                "notes": "Gemini API error",
                "appearance": "N/A",
                "palate": "N/A",
                "aging": "N/A",
                "error": str(e)
            }

    return get_cache_or_fetch("summary", wine_name, fetch_gemini)