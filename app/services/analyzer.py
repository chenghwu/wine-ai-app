from typing import Dict, Any

def analyze_sat_profile(wine_input: Dict[str, Any]) -> Dict[str, Any]:
    notes = []
    quality_score = 0
    details = {}

    # Appearance
    appearance = wine_input.get("appearance", {})
    color = appearance.get("color", "").lower()
    clarity = appearance.get("clarity", "").lower()
    intensity = appearance.get("intensity", "").lower()

    if clarity == "clear":
        details["clarity"] = "Wine appears clear – free of faults."
    if intensity in ["medium", "deep"]:
        details["appearance_intensity"] = f"Intensity is {intensity} – good color extraction."
        quality_score += 1
    if color in ["ruby", "gold", "amber"]:
        details["color"] = f"Color '{color}' suggests maturity or grape typicity."
        quality_score += 1

    # Nose
    nose = wine_input.get("nose", {})
    nose_intensity = nose.get("intensity", "").lower()
    aroma_characteristics = nose.get("aromas", [])

    if nose_intensity in ["medium", "pronounced"]:
        details["nose_intensity"] = f"Nose intensity is {nose_intensity} – aromatic expression present."
        quality_score += 1
    if isinstance(aroma_characteristics, list) and len(aroma_characteristics) >= 3:
        details["nose_complexity"] = f"Aromas include {', '.join(aroma_characteristics)} – shows complexity."
        quality_score += 1

    # Palate
    palate = wine_input.get("palate", {})
    balance_count = 0

    if palate.get("acidity") in ["medium+", "high"]:
        balance_count += 1
        details["acidity"] = "Good acidity level – freshness and aging potential."
    if palate.get("tannin") in ["medium", "medium+", "high"]:
        balance_count += 1
        details["tannin"] = "Firm tannin structure – supports body and aging."
    if palate.get("body") in ["medium+", "full"]:
        balance_count += 1
        details["body"] = "Fuller body – intensity and richness."

    if balance_count >= 2:
        quality_score += 1
        details["balance"] = "Balance detected between structure and concentration."

    length = palate.get("finish", "").lower()
    if length in ["medium+", "long"]:
        quality_score += 1
        details["finish"] = f"Finish is {length} – contributes to quality."

    flavor_intensity = palate.get("intensity", "").lower()
    if flavor_intensity in ["medium+", "pronounced"]:
        quality_score += 1
        details["palate_intensity"] = f"Flavor intensity is {flavor_intensity} – expressive on the palate."

    complexity = aroma_characteristics + palate.get("flavors", [])
    if len(set(complexity)) >= 5:
        quality_score += 1
        details["complexity"] = f"Detected {len(set(complexity))} unique elements – wine is complex."

    # Quality Assessment Logic per WSET Level 3
    if quality_score >= 6:
        quality = "Outstanding"
    elif quality_score >= 5:
        quality = "Very Good"
    elif quality_score >= 3:
        quality = "Good"
    elif quality_score >= 1:
        quality = "Acceptable"
    else:
        quality = "Poor"

    notes.append("Scored based on WSET Level 3: Balance, Length, Intensity, Complexity.")
    notes.append("Highlights: " + "; ".join(details.values()))

    return {
        "quality": quality,
        "score": quality_score,
        "notes": " ".join(notes)
    }