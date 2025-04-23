from app.models.mcp_model import MCPOutput

def generate_mock_summary() -> MCPOutput:
    mock_data = {
        "wine": "Mock Wine 2018",
        "appearance": "Deep ruby",
        "nose": "Medium+ aromas of cassis, tobacco, mocha",
        "palate": "Full-bodied, high acidity, ripe tannins, long finish",
        "aging": "Can age 8–12 years",
        "average_price": "$120",
        "quality": "Very Good",
        "analysis": (
            "Based on the information available, it has complex aroma and flavor profile, "
            "with red and black fruit, spice, and earthy notes. The structure (tannins, acidity, "
            "alcohol) suggests good aging potential."
        ),
        "sat": {
            "score": 3,
            "quality": "Very Good",
            "criteria": ["Balance", "Length", "Complexity"],
            "clusters": ["Black fruit"],
            "descriptors": ["Cassis", "Tobacco", "Mocha"]
        },
        "reference_source": ["Mock: winespectator.com"]
    }
    return MCPOutput(**mock_data)