def analyze_wine_profile(profile: dict) -> dict:
    appearance = profile.get("appearance", "").lower()
    nose = profile.get("nose", "").lower()
    palate = profile.get("palate", "").lower()

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
    # Full WSET Level 3 clusters and descriptors
    aroma_lexicon = {
        "floral": ["acacia", "honeysuckle", "chamomile", "elderflower", "geranium", "blossom", "rose", "violet"],
        "green fruit": ["apple", "pear", "gooseberry", "grape"],
        "citrus fruit": ["grapefruit", "lemon", "lime", "orange"],
        "stone fruit": ["peach", "apricot", "nectarine"],
        "tropical fruit": ["banana", "pineapple", "mango", "passion fruit", "melon"],
        "red fruit": ["strawberry", "raspberry", "red cherry", "cranberry"],
        "black fruit": ["blackcurrant", "blackberry", "bramble", "blueberry", "black cherry", "plum"],
        "dried fruit": ["fig", "raisin", "sultana", "kirsch", "jam", "cooked", "stewed"],
        "herbaceous": ["cut grass", "tomato leaf", "asparagus", "blackcurrant leaf"],
        "herbal": ["eucalyptus", "mint", "lavender", "fennel", "dill"],
        "spice": ["black pepper", "white pepper", "liquorice"],
        "yeast": ["biscuit", "bread", "toast", "pastry", "brioche", "bread dough", "cheese"],
        "malolactic": ["butter", "cream", "butterscotch"],
        "oak": ["vanilla", "clove", "nutmeg", "coconut", "cedar", "charred wood", "smoke", "chocolate", "coffee", "toast"],
        "oxidation": ["almond", "marzipan", "hazelnut", "walnut", "chocolate", "toffee", "fig"],
        "fruit development": ["dried apricot", "marmalade", "dried apple", "dried banana"],
        "bottle age (red)": ["forest floor", "mushroom", "game", "meat", "leather", "earthy", "farmyard"],
        "bottle age (white)": ["toast", "honey", "cereal", "hay", "dried fruit"]
    }

    all_text = f"{nose} {palate}"
    cluster_matches = set()
    descriptor_matches = []

    for cluster, descriptors in aroma_lexicon.items():
        for desc in descriptors:
            if desc in all_text:
                cluster_matches.add(cluster)
                descriptor_matches.append(desc)

    if len(cluster_matches) >= 3 and len(descriptor_matches) >= 6:
        score += 1
        criteria.append("Complexity")

    quality_map = {
        4: "Outstanding",
        3: "Very Good",
        2: "Good",
        1: "Acceptable",
        0: "Poor"
    }

    return {
        "score": score,
        "structured_quality": quality_map.get(score, "Unknown"),
        "criteria": criteria,
        "matched_clusters": sorted(cluster_matches),
        "matched_descriptors": sorted(descriptor_matches)
    }