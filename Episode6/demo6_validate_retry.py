"""
Episode 6 Demo - Part 1: VALIDATE AND RETRY

Claude classifies a support message with a schema. Our code then checks
two business rules. If a rule fails, our code sends the specific failure
back to Claude and asks for a corrected answer. The loop stops after
MAX_ATTEMPTS.

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY=your_key_here
  python3 demo6_validate_retry.py
"""

import json

from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

client = Anthropic()
MODEL = "claude-haiku-4-5"
MAX_ATTEMPTS = 3

SCHEMA = {
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


def validate(data: dict) -> list[str]:
    """Return a list of failed rules. An empty list means the answer passes."""
    errors = []

    # Business rule 1: the summary must be at most 20 words.
    word_count = len(data["summary"].split())
    if word_count > 20:
        errors.append(f"The summary has {word_count} words. The limit is 20 words.")

    # Business rule 2: a P1 ticket must have a negative sentiment.
    if data["urgency"] == "P1" and data["sentiment"] != "NEG":
        errors.append(
            f"The urgency is P1 but the sentiment is {data['sentiment']}. "
            "A P1 ticket must have sentiment NEG."
        )

    return errors


def classify(ticket: str) -> dict | None:
    messages = [{"role": "user", "content": f"Classify this customer support message:\n\n{ticket}"}]

    for attempt in range(1, MAX_ATTEMPTS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=300,
            messages=messages,
            extra_body={"output_config": {"format": {"type": "json_schema", "schema": SCHEMA}}},
        )

        if response.stop_reason in ("max_tokens", "refusal"):
            raise RuntimeError(f"Stopped with reason {response.stop_reason}. Route to a person.")

        text = response.content[0].text
        data = json.loads(text)
        errors = validate(data)
        print(f"Attempt {attempt}: {data}")

        if not errors:
            print("  All checks passed.")
            return data

        print("  Failed checks:")
        for error in errors:
            print("   -", error)

        # Keep Claude's answer in the history, then send the specific failures back.
        messages.append({"role": "assistant", "content": text})
        messages.append({
            "role": "user",
            "content": (
                "Your answer failed these checks:\n- "
                + "\n- ".join(errors)
                + "\nReturn a corrected answer that follows the same schema."
            ),
        })

    print("  Still failing after the attempt limit.")
    return None


ticket = "My payment failed twice today and I'm being charged extra fees. This is unacceptable."

print("=" * 60)
print("Message:", ticket)
result = classify(ticket)
print("=" * 60)
print("Final result:", result if result else "No valid answer. Send to a person.")
