def get_sat_prompt(wine_name: str, content: str, sources: list[str]) -> str:
    sources_section = ""
    if sources:
        formatted_sources = "\n".join(f"- {s}" for s in sources)
        sources_section = f"\nSources:\n{formatted_sources}"

    return f"""
You are a certified wine educator trained in WSET Level 4 Systematic Approach to Tasting (SAT). 
Based on the information provided below about the wine "{wine_name}", give a confident, hypothetical SAT-style analysis 
based on typical regional and varietal characteristics, even if the provided text is incomplete.

Be concise and decisive — NEVER include phrases like "I cannot ascertain...", "I expect..." or "based on limited info".
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

def get_wine_from_query_prompt(query: str) -> str:
    return f"""
You are a Master of Wine, an expert in wine classification and blind tasting.
Extract the **exact wine name** and **vintage (year)** from the following user query.
Only extract what's **clearly mentioned** in the query. Do **not guess** or substitute other wines.
If the vintage is not mentioned, return an empty string for vintage.
Do not include region, grape, or other descriptors unless part of the wine's official name.
Return in **strict JSON format** with "wine_name" and "vintage" keys.

---

User Query:
"{query}"

---

Output Format:
{{
  "wine_name": "...",
  "vintage": "..."
}}

Examples:
Input: "opus one 2015" → {{ "wine_name": "Opus One", "vintage": "2015" }}
Input: "opus one" → {{ "wine_name": "Opus One", "vintage": "" }}
Input: "1978 château margaux" → {{ "wine_name": "Château Margaux", "vintage": "1978" }}
Input: "any info about insignia phelps 2013?" → {{ "wine_name": "Insignia Phelps", "vintage": "2013" }}
""".strip()