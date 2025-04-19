import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)                 # 🔹 Configure Gemini only if ENV != dev

def parse_wine_query_with_llm(query: str) -> dict:
    prompt = f"""
You are a wine assistant. Extract structured wine fields from the user query: {query}
Return: JSON with wine_name, winery, year, region, style, flavor_notes[]
"""

    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)

    try:
        return eval(response.text.strip())
    except:
        return {"wine_name": "Unknown", "year": "Unknown"}