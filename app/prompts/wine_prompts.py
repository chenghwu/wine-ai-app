def get_sat_prompt(
  wine_name: str,
  content: str,
  sources: list[str],
  aroma_lexicon: dict
) -> str:
    cluster_list_str = ", ".join(aroma_lexicon.keys())
    sources_section = ""
    if sources:
        formatted_sources = "\n".join(f"- {s}" for s in sources)
        sources_section = f"\nSources:\n{formatted_sources}"

    return f"""
You are a Master of Wine who has also completed the WSET Level 4 Diploma in Wines. 
Analyze the wine "{wine_name}" using the WSET Systematic Approach to Tasting (SAT), based on the content below.
Even with partial data, apply expert-level reasoning grounded in regional and varietal benchmarks.
Always present conclusions as factual and authoritative.
Be decisive and concise, using correct technical language and full SAT logic.

**Important rules:**
- "nose" and "palate" must include **intensity**
- "palate" must include: sweetness, acidity, alcohol, body, flavor intensity, flavor characteristics, **finish length**, and **whether it is balance**
- Only include "tannin" if the wine is red or contains red grape varieties
- In "aroma":
  - Extract and map **every aroma descriptor** mentioned in the "nose", "palate", or "analysis" to their correct cluster from the list below
  - Assign each descriptor to the **single most contextually appropriate aroma cluster**
  - **Omit all aroma clusters that do not contain at least one descriptor**
- **Do NOT** use speculative words (e.g., "probably", "might", "assuming")
- **Do NOT** include disclaimers like "based on limited info" or "I cannot ascertain"

--------------------------
Content to analyze:
{content}
{sources_section}
--------------------------

Your analysis must follow this exact JSON format below. Each field is REQUIRED.

{{
  "wine": "{wine_name}",
  "grape_varieties": "Grape varieties composition of the wine (e.g. 85% Cabernet Sauvignon, 15% Merlot)",
  "appearance": "Clarity, intensity, color (e.g., clear, medium intensity, ruby)",
  "nose": "Cleanliness, intensity, list of aroma characteristics (e.g., clean, pronounced, red cherry, blackcurrant, cedar, leather)",
  "palate": "Sweetness, acidity, tannin, alcohol, body, flavor intensity, flavor characteristics, finish length, and whether it is balanced (e.g., dry, high acidity, medium+ tannin, medium alcohol, full body, pronounced intensity, flavors of blackberry, vanilla, mushroom, long finish, balanced)",
  "aging": "Expected aging potential and why (e.g., Can age for 10–15 years due to high tannin, acidity, and concentration; or not suitable for bottle ageing)",
  "quality": "Choose one: Poor, Acceptable, Good, Very Good, Outstanding",
  "average_price": "Estimated average market price in U.S. dollars (e.g. US$120)",
  "analysis": "Brief summary of why you came to these conclusions using SAT criteria",
  "aroma": {{
    "Green fruit": ["apple", "pear"],
    "Yeast": ["biscuit"]
  }},
  "reference_source": ["A list of sources and links you used from the content"]
}}

Use this exact list of aroma clusters (case-sensitive):
{cluster_list_str}
""".strip()

def get_wine_from_query_prompt(query: str) -> str:
    return f"""
You are a Master of Wine, specializing in wine classification and blind tasting.
Your job is to extract structured information from unstructured user wine queries.

From the following query, extract:
- **winery** (producer or estate name)
- **wine name** (official product label name)
- **vintage** (year, if present)

If the **winery is not explicitly mentioned**, but the **wine name is unique or well-known**, 
return the correct winery based on established wine knowledge.
Do **not guess** if the wine name is too generic or uncertain.
If you're not sure, return the wine name and leave winery as an empty string.
Only extract what's **clearly mentioned** in the query. Do **not guess** or substitute other wines.
Avoid including grape, region, or descriptors unless they are part of the official wine name.

Respond strictly in the following JSON format:
{{
  "winery": "...",
  "wine_name": "...",
  "vintage": "..."
}}

---

User Query:
"{query}"

---

Examples:
Input: "opus one 2015" → {{ "winery": "Opus One", "wine_name": "Opus One", "vintage": "2015" }}
Input: "opus one" → {{ "winery": "Opus One", "wine_name": "Opus One", "vintage": "" }}
Input: "1978 château margaux" → {{ "winery": "Château Margaux", "wine_name": "Château Margaux", "vintage": "1978" }}
Input: "D2 2022" → {{ "winery": "DeLille Cellars", "wine_name": "D2", "vintage": "2022" }}
""".strip()