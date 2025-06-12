
def generate_food_pairing_prompt(wine_profile: dict) -> str:
    return f"""
You are a wine and food pairing expert.
Here is the wine's tasting profile (WSET-style):

{wine_profile}

Based on the flavor profile, acidity, tannin, body, sweetness, and intensity of this wine, suggest 3 food pairing ideas.
Each recommendation should include:
- A specific food name
- A short reason why it pairs well

Respond in this JSON format:
[
  {{
    "food": "Grilled duck breast with cherry glaze",
    "reason": "The wine's high acidity and red fruit notes complement the richness of duck and sweet cherry sauce."
  }},
  ...
]
"""