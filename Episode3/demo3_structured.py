"""
Episode 3 Demo - Part 2: STRUCTURED OUTPUT

We pass a JSON schema with the request. The schema restricts each field
to the allowed values, and every field is required. The response is then
checked for stop_reason before it is parsed.

The schema is sent in the output_config.format parameter. No beta header
is required for this parameter.

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY=your_key_here
  python3 demo3_structured.py
"""

import json

from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

client = Anthropic()

TICKET_SCHEMA = {
    "type": "object",
    "properties": {
        "urgency": {"type": "string", "enum": ["P1", "P2", "P3"]},
        "category": {"type": "string", "enum": ["BILL", "TECH", "ACCT"]},
        "sentiment": {"type": "string", "enum": ["POS", "NEU", "NEG"]},
        "summary": {"type": "string"},
    },
    "required": ["urgency", "category", "sentiment", "summary"],
    "additionalProperties": False,
}


def triage(message: str) -> dict:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=300,
        messages=[
            {
                "role": "user",
                "content": f"Classify this customer support message:\n\n{message}",
            }
        ],
        extra_body={
            "output_config": {
                "format": {"type": "json_schema", "schema": TICKET_SCHEMA}
            }
        },
    )

    # Check the stop reason before parsing. A truncated reply can be
    # incomplete, and a refusal may not follow the schema.
    if response.stop_reason == "max_tokens":
        raise RuntimeError("Reply was cut off. Increase max_tokens and retry.")
    if response.stop_reason == "refusal":
        raise RuntimeError("Claude declined the request. Route it to a person.")

    return json.loads(response.content[0].text)


messages = [
    "My payment failed twice today and I'm being charged extra fees. This is unacceptable.",
    "Love the new update, everything works great now!",
]

for message in messages:
    print("=" * 60)
    print("Message:", message)
    result = triage(message)
    print("Result: ", result)
    print("Urgency:", result["urgency"], "| Category:", result["category"])
