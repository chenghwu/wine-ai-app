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
You are a Master of Wine who has completed the WSET Level 4 Diploma in Wines. 
Analyze the wine "{wine_name}" using the WSET Systematic Approach to Tasting (SAT), referencing known regional and varietal benchmarks.

Follow these rules exactly:

- Use only official SAT structure terms (e.g., medium+ tannin, full body). Do **not** create terms like “medium-light”
- “nose” and “palate” must each include **intensity**
- “palate” must include: sweetness, acidity, alcohol, body, flavor intensity, flavor characteristics, **finish length**, and **balance**
- Include “tannin” only if the wine is red or contains red grape varieties
- Use **precise, layered descriptors** (e.g., cinnamon, black cherry jam). Avoid vague terms like “fruit”, “spice”, or “earth” unless no better alternative exists
- Nose and palate often share descriptors — include overlaps naturally. Add distinct ones only if clearly supported by the content (e.g., spice, texture, or deeper fruit). Do not exaggerate or invent complexity
- In "grape_varieties", include exact percentages if known. If not available, state the most plausible varietal composition using expert judgment — avoid speculative words like “likely”, “probably”, or “not specified”
- In "aroma":
  - Only include aroma descriptors that appear explicitly in the **nose**, **palate**, or **analysis** fields — no additions or inventions
  - Map each descriptor to its **most contextually appropriate cluster** from the list below
  - Use "Other aroma" only when no suitable cluster fits
  - Do **not** invent descriptors or include clusters with no descriptors

- In "analysis", interpret what the SAT attributes reveal about the wine’s **style, quality, and aging potential**, referencing regional or classification benchmarks. Write fluently and confidently, as if speaking to sommeliers or collectors. **Do not repeat SAT terms or fields already covered**

**Avoid speculative words** like “likely”, “probably”, or disclaimers such as “based on limited info”. Present conclusions with confident, expert phrasing.

**Do not copy the format examples below.** They are only reference structures — always replace them with real values from the content. Leave a field blank only if no trustworthy data is available.

--------------------------
Content to analyze:
{content}
{sources_section}
--------------------------

Return your output in this exact JSON format (but with real values):

{{
  "wine": "{wine_name}",
  "region": "The specific wine region, including country (e.g., Napa Valley, CA, USA or Pauillac, France). This field is mandatory. If the region cannot be determined from the context, provide \"Unknown\" as the value.",
  "grape_varieties": "Exact blend if known (e.g., 85% Cabernet Sauvignon, 15% Merlot). If not provided, use the most accurate composition based on content — no vague or speculative terms.",
  "appearance": "e.g., Clear, pale ruby",
  "nose": "e.g. Clean, pronounced, black cherry, vanilla, cedar",
  "palate": "e.g. Dry, high acidity, medium+ tannin, medium alcohol, full body, pronounced, black cherry, chocolate, long finish, balanced",
  "aging": "Expected aging potential and reason (e.g., Can age 10–15 years due to structure and concentration)",
  "quality": "Choose one: Poor, Acceptable, Good, Very Good, Outstanding",
  "average_price": "Estimated price in U.S. dollars (e.g., US$60–80)",
  "analysis": "Fluent expert commentary on structure, style, quality, and classification — do not repeat SAT terms",
  "aroma": {{
    "Green fruit": ["apple", "pear"],
    "Yeast": ["biscuit"]
  }},
  "reference_source": ["List of actual URLs used"]
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

If the winery is **not explicitly mentioned**, but the wine name is unique or recognizable,
infer the correct winery based on established wine knowledge.

If the query contains **misspellings or formatting issues**, interpret the intended wine using your wine expertise and correct it.

However, do **not guess** if the wine name is too generic or uncertain.
If you're not sure, return the wine name and leave winery as an empty string.

Only extract what is **reasonably clear** from the query. Do **not guess** or substitute other wines.
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
Input: "Dom Gauby Calcinaire's Cotes Catalan" → {{ "winery": "Domaine Gauby", "wine_name": "Calcinaires Côtes Catalanes", "vintage": "" }}
""".strip()