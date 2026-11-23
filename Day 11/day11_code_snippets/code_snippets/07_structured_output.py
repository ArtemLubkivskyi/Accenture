"""
Demo 07: Structured output with a JSON schema
Block 4 — Run from live_materials/: uv run python code_snippets/07_structured_output.py

Shows: response_format with a JSON schema on Ollama's OpenAI-compatible
endpoint. Ollama constrains generation to the schema; the result is still a
string, so it is parsed and checked here with the standard library only.
Day 8 did the same with Pydantic and client.responses.parse on the cloud.
"""
import json
import sys
sys.path.insert(0, ".")
from config import get_llm_client, LLM_BASE_URL, LLM_MODEL, TOKEN_LIMIT_PARAM

client = get_llm_client()

TEXT = """Employees may work remotely up to 3 days per week with manager approval.
Remote work from outside the EU requires written approval from HR and is
limited to 20 working days per calendar year."""

SCHEMA = {
    "type": "object",
    "properties": {
        "max_remote_days_per_week": {"type": "integer"},
        "needs_manager_approval": {"type": "boolean"},
        "outside_eu_days_per_year": {"type": "integer"},
        "outside_eu_approver": {"type": "string"},
    },
    "required": [
        "max_remote_days_per_week",
        "needs_manager_approval",
        "outside_eu_days_per_year",
        "outside_eu_approver",
    ],
    "additionalProperties": False,
}

PYTHON_TYPES = {"integer": int, "boolean": bool, "string": str}


def validate(data, schema):
    errors = []
    for key in schema["required"]:
        if key not in data:
            errors.append(f"missing: {key}")
    for key, value in data.items():
        if key not in schema["properties"]:
            errors.append(f"unexpected: {key}")
            continue
        expected = PYTHON_TYPES[schema["properties"][key]["type"]]
        # bool is a subclass of int in Python, so True would pass as an integer.
        if not isinstance(value, expected) or (expected is int and isinstance(value, bool)):
            errors.append(f"{key}: expected {expected.__name__}, got {type(value).__name__}")
    return errors


response = client.chat.completions.create(
    model=LLM_MODEL,
    messages=[
        {"role": "system", "content": "Extract the remote work rules from the text."},
        {"role": "user", "content": TEXT},
    ],
    response_format={
        "type": "json_schema",
        "json_schema": {"name": "remote_work_policy", "schema": SCHEMA, "strict": True},
    },
    temperature=0.0,
    reasoning_effort="none",
    **{TOKEN_LIMIT_PARAM: 300},
)

raw = response.choices[0].message.content
print(f"Endpoint: {LLM_BASE_URL}")
print(f"Model:    {LLM_MODEL}\n")
print("=== Raw content (a string) ===")
print(raw)
print()

data = json.loads(raw)
errors = validate(data, SCHEMA)

print("=== Parsed and checked ===")
for key, value in data.items():
    print(f"{key:<28} {value!r:<10} {type(value).__name__}")
print()
print("Schema check: " + ("passed" if not errors else "FAILED: " + "; ".join(errors)))
print("→ The schema fixes the shape. Whether the values are right is still your test set's job.")
