import json, re

def parse_json_from_text(text: str) -> dict:
    """
    Extract the first JSON object from LLM output.
    """
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except Exception:
        pass
    return {"raw_output": text.strip()}

