import json
import re
from typing import Any

from agent_canary.llm.base import JsonObject, JsonSchema
from agent_canary.llm.exceptions import LLMProviderResponseError

JSON_FENCE_RE = re.compile(r"^```(?:json)?\s*(?P<body>.*?)\s*```$", re.DOTALL)


def structured_prompt(prompt: str, schema: JsonSchema) -> str:
    return (
        f"{prompt}\n\n"
        "Return only a valid JSON object that conforms to this JSON Schema:\n"
        f"{json.dumps(schema, sort_keys=True)}"
    )


def parse_json_object(text: str) -> JsonObject:
    stripped = text.strip()
    match = JSON_FENCE_RE.match(stripped)
    if match is not None:
        stripped = match.group("body").strip()

    try:
        parsed: Any = json.loads(stripped)
    except json.JSONDecodeError as exc:
        raise LLMProviderResponseError("LLM response was not valid JSON") from exc

    if not isinstance(parsed, dict):
        raise LLMProviderResponseError("LLM response JSON was not an object")
    return parsed

