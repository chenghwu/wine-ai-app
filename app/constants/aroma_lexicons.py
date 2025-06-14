''' 
Full WSET Level 4 clusters and descriptors
'''
AROMA_LEXICONS = {
    "Floral": ["acacia", "honeysuckle", "chamomile", "elderflower", "geranium", "blossom", "rose", "violet", "jasmin"],
    "Green fruit": ["apple", "pear", "pear drop", "quince", "gooseberry", "grape"],
    "Citrus fruit": ["grapefruit", "lemon", "lime", "orange", "orange peel", "lemon peel", "yuzu", "bergamot"],
    "Stone fruit": ["peach", "apricot", "nectarine"],
    "Tropical fruit": ["banana", "lychee", "pineapple", "mango", "passion fruit", "melon", "papaya", "guava"],
    "Red fruit": ["redcurrant", "strawberry", "raspberry", "red cherry", "cranberry", "red plum", "morello cherry"],
    "Black fruit": ["blackcurrant", "blackberry", "bramble", "blueberry", "black cherry", "black plum"],
    "Dried/cooked fruit": ["fig", "prune", "raisin", "sultana", "kirsch", "jamminess", "baked fruits", "stewed fruits", "preserved fruit"],
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

if __name__ == "__main__":
    print(AROMA_LEXICONS.keys())
