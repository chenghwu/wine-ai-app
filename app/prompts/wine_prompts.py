def get_sat_prompt(wine_name: str, content: str, sources: list[str]) -> str:
    sources_section = ""
    if sources:
        formatted_sources = "\n".join(f"- {s}" for s in sources)
        sources_section = f"\nSources:\n{formatted_sources}"

    return f"""
You are a certified wine educator trained in WSET Level 4 Systematic Approach to Tasting (SAT). 
Based on the information provided below about the wine "{wine_name}", give a confident, hypothetical SAT-style analysis 
based on typical regional and varietal characteristics, even if the provided text is incomplete.

Be concise and decisive — NEVER include phrases like "I cannot ascertain..." or "based on limited info".
Instead, **make the best educated expert assumption** using your knowledge and the content below.

--------------------------
Content to analyze:
{content}
{sources_section}
--------------------------

Your response **must follow this exact JSON format**, using key SAT descriptors and technical language.
DO NOT skip any field.
Each field MUST contain the required sub-elements as described.

{{
  "wine": "{wine_name}",
  "appearance": "clarity, intensity, color (e.g., clear, medium intensity, ruby)",
  "nose": "cleanliness, intensity, list of aroma characteristics (e.g., clean, pronounced, red cherry, blackcurrant, cedar, leather)",
  "palate": "sweetness, acidity, tannin, alcohol, body, flavor intensity, flavor characteristics, finish, balanced or not (e.g., dry, high acidity, medium+ tannin, full body, pronounced intensity, flavors of blackberry, vanilla, mushroom, long finish, balanced)",
  "aging": "Expected aging potential and why (e.g., Can age for 10–15 years due to high tannin, acidity, and concentration)",
  "quality": "Choose one: Poor, Acceptable, Good, Very Good, Outstanding",
  "average_price": "Estimated average market price (e.g., $120)",
  "analysis": "Brief summary of why you came to these conclusions using SAT criteria",
  "reference_source": ["A list of sources and links you used from the content"]
}}

Put "N/A" in value if unknown.
""".strip()

def old_get_prompt(wine_name: str, content: str) -> str:
    return f"""
Act as a certified wine expert trained in WSET Level 4 Systematic Approach to Tasting.
Based on the following information about the wine \"{wine_name}\", please provide a detailed SAT-style analysis.

Content:
{content}

Your response must include:
- Appearance (clarity, intensity, color)
- Nose (aromas, intensity)
- Palate (sweetness, acidity, tannin, alcohol, body, flavour intensity, flavour characteristics, finish, balance or not)
- Quality level (Poor, Acceptable, Good, Very Good, Outstanding)
- Aging potential and why
- Average price
- Why and how do you get this conclusion

Output format must be structured like this JSON, put "N/A" if unknown:
{{
"wine": "{wine_name}",
"appearance": "...",
"nose": "...",
"palate": "...",
"aging": "...",
"quality": "...",
"average_price": "...",
"analysis": "...",
"reference_source": "..."
}}
""".strip()