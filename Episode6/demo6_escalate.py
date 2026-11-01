"""
Episode 6 Demo - Part 2: VALIDATE THE INPUT AND ESCALATE

Before the model is called, our code checks the input. An empty or very
short message goes straight to a person. A valid message is classified
with a limit of two attempts. If the answer still fails the checks, the
case goes to the escalation queue with the reason.

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY=your_key_here
  python3 demo6_escalate.py
"""

import json

from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
client = Anthropic()
MODEL = "claude-haiku-4-5"
MAX_ATTEMPTS = 2

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

# A list in memory stands in for a real queue or ticket table.
ESCALATION_QUEUE = []


def check_input(ticket: str) -> str | None:
    """Return a reason to reject the input, or None if the input is acceptable."""
    if not ticket or not ticket.strip():
        return "The message is empty."
    if len(ticket.strip()) < 10:
        return "The message is too short to classify."
    return None


def validate_output(data: dict) -> list[str]:
    errors = []
    if len(data["summary"].split()) > 20:
        errors.append("The summary is longer than 20 words.")
    if data["urgency"] == "P1" and data["sentiment"] != "NEG":
        errors.append("A P1 ticket must have sentiment NEG.")
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
            return None

        text = response.content[0].text
        data = json.loads(text)
        errors = validate_output(data)
        print(f"  Attempt {attempt}: {data}")

        if not errors:
            return data

        print("  Failed checks:", errors)
        messages.append({"role": "assistant", "content": text})
        messages.append({
            "role": "user",
            "content": "Your answer failed these checks:\n- " + "\n- ".join(errors)
                       + "\nReturn a corrected answer that follows the same schema.",
        })

    return None


def handle_ticket(ticket: str) -> None:
    print("=" * 60)
    print("Message:", repr(ticket))

    reason = check_input(ticket)
    if reason:
        print("  Input rejected:", reason)
        ESCALATION_QUEUE.append({"message": ticket, "reason": reason})
        return

    result = classify(ticket)
    if result:
        print("  Classified:", result)
    else:
        reason = f"No valid answer after {MAX_ATTEMPTS} attempts."
        print("  Escalated:", reason)
        ESCALATION_QUEUE.append({"message": ticket, "reason": reason})


for ticket in [
    "My payment failed twice today and I'm being charged extra fees. This is unacceptable.",
    "   ",
]:
    handle_ticket(ticket)

print("\n" + "=" * 60)
print("Escalation queue for a person to review:")
print(json.dumps(ESCALATION_QUEUE, indent=2))
