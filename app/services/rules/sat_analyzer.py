from app.utils.aroma_lexicon import aroma_lexicon

def analyze_wine_profile(profile: dict) -> dict:
    appearance = profile.get("appearance", "").lower()
    nose = profile.get("nose", "").lower()
    palate = profile.get("palate", "").lower()
    aroma = profile.get("aroma", {}) or {}

    score = 0
    criteria = []

    # === B: Balance ===
    if "balanced" in palate or "balance" in palate:
        score += 1
        criteria.append("Balance")

    # === L: Length ===
    if "long" in palate or "long finish" in palate:
        score += 1
        criteria.append("Length")

    # === I: Intensity (both must be pronounced) ===
    if "pronounced" in nose and "pronounced" in palate:
        score += 1
        criteria.append("Intensity")

    # === C: Complexity ===
    cluster_count = len(aroma)
    descriptor_count = sum(len(v) for v in aroma.values())

    if cluster_count >= 3 and descriptor_count >= 6:
        score += 1
        criteria.append("Complexity")

    quality_map = {
        4: "Outstanding",
        3: "Very Good",
        2: "Good",
        1: "Acceptable",
        0: "Poor"
    }

    clusters = sorted(aroma.keys())
    descriptors = sorted({desc for v in aroma.values() for desc in v})

    return {
        "criteria": criteria,
        "score": score,
        "quality": quality_map.get(score, "Unknown"),
        "aroma": aroma,
        "clusters": clusters,
        "descriptors": descriptors
    }