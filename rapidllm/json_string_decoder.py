import json
from typing import Any, Dict


def clean_and_load_json(raw_text: str) -> Dict[str, Any]:
    """
    Cleans a raw string response from an LLM, which often includes Markdown
    markers (```json\n...\n```), and attempts to load the content as a JSON dictionary.

    Args:
        raw_text: The raw string received from the LLM response.

    Returns:
        A Python dictionary containing the parsed JSON data, or an empty
        dictionary if decoding fails.
    """
    # 1. Strip leading and trailing whitespace/newlines
    cleaned_json = raw_text.strip()

    # 2. Check and remove the starting Markdown fence
    marker_start = "```json\n"
    if cleaned_json.startswith(marker_start):
        cleaned_json = cleaned_json[len(marker_start) :]
    # Handle an alternative marker like '```\n'
    elif cleaned_json.startswith("```\n"):
        cleaned_json = cleaned_json[4:]

    # 3. Check and remove the trailing Markdown fence and strip again
    cleaned_json = cleaned_json.strip()
    if cleaned_json.endswith("```"):
        # Remove the last three characters
        cleaned_json = cleaned_json[:-3]

    # 4. Final cleanup of whitespace/newlines
    cleaned_json = cleaned_json.strip()

    # 5. Attempt to decode the cleaned string
    if not cleaned_json:
        # Avoid trying to decode an empty string
        print("Warning: Cleaned JSON string is empty.")
        return {}

    try:
        # Decode the string into a Python dictionary
        final_data = json.loads(cleaned_json)
        return final_data
    except json.JSONDecodeError as e:
        print(f"ERROR: Failed to decode JSON after cleaning: {e}")
        # Print the content that failed to decode for debugging
        print(f"Content that caused the error: [{cleaned_json}]")
        return {}  # Return an empty dictionary on failure
