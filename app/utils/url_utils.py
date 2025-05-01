import re

def is_valid_url(text: str) -> bool:
    return bool(re.match(r"^https?://", text)) or bool(re.match(r"^www\.", text))