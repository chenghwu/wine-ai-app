def generate_food_pairing_prompt(wine_profile: dict) -> str:
    return f"""
You are a professional wine and food pairing expert.
Below is a wine's detailed tasting profile (based on WSET-style evaluation):

{wine_profile}

Your task:
- Identify 3 to 5 high-level food categories that pair well with this wine.
- For each category:
  - Give a clear category name (e.g., "Lamb", "Beef", "Hard cheese", "White fish", "Mushrooms").
  - Provide 2 specific example dishes that match this wine.
  - Explain briefly why each dish is a good pairing (1–2 sentences).

Output your answer as a **JSON array** in the following structure:

[
  {{
    "category": "Lamb",
    "examples": [
      {{
        "food": "Herb-crusted lamb rack with rosemary jus",
        "reason": "The wine's tannin and herbal complexity match the richness of lamb and herbs."
      }},
      {{
        "food": "Slow-braised lamb shank with red wine reduction",
        "reason": "The depth of flavor complements the wine's body and intensity."
      }}
    ]
  }},
  ...
]
"""