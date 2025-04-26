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
        "Floral": ["acacia", "honeysuckle", "chamomile", "elderflower", "geranium", "blossom", "rose", "violet", "jasmin"],
        "Green fruit": ["apple", "pear", "pear drop", "quince", "gooseberry", "grape"],
        "Citrus fruit": ["grapefruit", "lemon", "lime", "orange", "organe peel", "lemon peel"],
        "Stone fruit": ["peach", "apricot", "nectarine"],
        "Tropical fruit": ["banana", "lychee", "pineapple", "mango", "passion fruit", "melon"],
        "Red fruit": ["redcurrant", "strawberry", "raspberry", "red cherry", "cranberry", "red plum"],
        "Black fruit": ["blackcurrant", "blackberry", "bramble", "blueberry", "black cherry", "black plum"],
        "Dried/cooked fruit": ["fig", "prune", "raisin", "sultana", "kirsch", "jamminess", "baked fruits" "stewed fruits", "preserved fruit"],
        "Herbaceous": ["green bell pepper", "capsicum", "grass", "tomato leaf", "asparagus", "blackcurrant leaf"],
        "Herbal": ["eucalyptus", "mint", "medicinal", "lavender", "fennel", "dill", "dried herbs", "thyme", "oregano"],
        "Spice": ["black pepper", "white pepper", "liquorice", "cinnamon"],
        "Other aroma": ["flint", "wet stones", "wet wool", "candy"],
        "Yeast": ["biscuit", "graham cracker", "bread", "toast", "pastry", "brioche", "bread dough", "cheese", "yogurt", "acetaldehyde"],
        "Malolactic": ["butter", "cheese", "cream"],
        "Oak": ["vanilla", "clove", "nutmeg", "coconut", "butterscotch", "toast", "cedar", "charred wood", "smoke", "chocolate", "coffee", "resinous"],
        "Oxidation": ["almond", "marzipan", "hazelnut", "walnut", "chocolate", "coffee", "toffee", "caramel"],
        "Fruit development (White)": ["dried fruit", "dried apricot", "raisin", "orange marmalade", "marmalade", "dried apple", "dried banana"],
        "Fruit development (Red)": ["fig", "prune", "raisin" "tar", "dried fruit", "dried blackberry", "dried cranberry", "cooked fruit", "cooked blackberry", "cooked plum", "cooked cherry"],
        "Bottle age (White)": ["petrol", "gasoline", "kerosene", "cinnamon", "ginger", "nutmeg", "toast", "nutty", "mushroom", "hay", "honey"],
        "Bottle age (Red)": ["forest floor", "mushroom", "game", "tobacco", "vegetal", "wet leaves", "savoury", "meat", "leather", "earth", "farmyard"],
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
        "criteria": criteria,
        "score": score,
        "quality": quality_map.get(score, "Unknown"),
        "clusters": sorted(cluster_matches),
        "descriptors": sorted(descriptor_matches)
    }