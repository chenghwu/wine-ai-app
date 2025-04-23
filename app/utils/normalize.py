def to_title_case_wine_name(text: str) -> str:
    """
    Capitalize each word in a wine name, keeping numbers unchanged.
    Example: 'opus one 2015' → 'Opus One 2015'
    """
    parts = text.strip().split()
    return " ".join([p.capitalize() if not p.isdigit() else p for p in parts])