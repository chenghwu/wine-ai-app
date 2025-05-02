import sys
import json
from app.utils.text_cleaning import clean_aggressively
from pathlib import Path

SAMPLE_PATH = sys.argv[1] if len(sys.argv) > 1 else "cache/html/sample.json"

def load_text_from_json(path: str) -> str:
    with open(path, "r") as f:
        raw_json = json.load(f)
        if isinstance(raw_json, str):
            # Decode escaped \n, \t etc.
            return bytes(raw_json, "utf-8").decode("unicode_escape")
        raise ValueError("Expected a string in the JSON file")

def preview(text: str, limit: int = 1500) -> str:
    return text[:limit] + ("\n..." if len(text) > limit else "")

if __name__ == "__main__":
    raw_text = load_text_from_json(SAMPLE_PATH)
    print(f"Raw length: {len(raw_text)} characters")

    cleaned = clean_aggressively(raw_text)
    print(f"\nCleaned length: {len(cleaned)} characters")
    print(f"\nPreview:\n{preview(cleaned)}")
