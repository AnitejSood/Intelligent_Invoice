"""JSON validator for Gemini responses."""

import json

def clean_json_string(raw_json: str) -> str:
    """Attempt basic cleanup of LLM output before passing to the parser or repair prompt."""
    cleaned = raw_json.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()

def is_valid_json(raw_json: str) -> bool:
    """Check if a string is valid JSON."""
    try:
        json.loads(clean_json_string(raw_json))
        return True
    except json.JSONDecodeError:
        return False
