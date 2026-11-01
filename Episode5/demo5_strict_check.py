"""
Episode 5 Demo - Part 2: SHAPE AND MEANING

We send three messages, each with a label we chose in advance. For each
reply, we check two things:
  1. Shape: does the tool input follow the schema? With strict mode, this
     check should always pass.
  2. Meaning: does the queue match the label? Strict mode does not check
     this, so the check can fail.

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY=your_key_here
  python3 demo5_strict_check.py
"""

from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
client = Anthropic()
MODEL = "claude-haiku-4-5"

QUEUES = {"BILLING", "TECHNICAL", "ACCOUNT"}
URGENCY = {"P1", "P2", "P3"}

TOOL = {
    "name": "route_ticket",
    "description": (
        "Routes a customer support ticket to the correct team queue. "
        "Use this once you know the customer id, the urgency, and the queue. "
        "Does not reply to the customer."
    ),
    "strict": True,
    "input_schema": {
        "type": "object",
        "properties": {
            "customer_id": {"type": "string", "description": "The customer id, for example C-42."},
            "urgency": {"type": "string", "enum": ["P1", "P2", "P3"], "description": "P1 is urgent. P3 is routine."},
            "queue": {
                "type": "string",
                "enum": ["BILLING", "TECHNICAL", "ACCOUNT"],
                "description": "The team that should handle the ticket.",
            },
        },
        "required": ["customer_id", "urgency", "queue"],
        "additionalProperties": False,
    },
}

# Each test case has a message and the queue we expect for it.
TEST_CASES = [
    ("C-42 here. My card was charged twice this month.", "BILLING"),
    ("C-77 here. The app crashes every time I open the settings page.", "TECHNICAL"),
    ("C-91 here. I cannot log in since I changed my email address.", "ACCOUNT"),
]


def get_tool_input(message: str) -> dict | None:
    """Send one message. Return the tool input, or None if Claude did not call the tool."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=512,
        tools=[TOOL],
        messages=[{"role": "user", "content": message}],
    )
    if response.stop_reason in ("max_tokens", "refusal"):
        return None
    for block in response.content:
        if block.type == "tool_use":
            return block.input
    return None


def check_shape(data: dict) -> bool:
    """Check the rules from the schema. With strict mode, this should always pass."""
    required = {"customer_id", "urgency", "queue"}
    return (
        set(data.keys()) == required
        and isinstance(data["customer_id"], str)
        and data["urgency"] in URGENCY
        and data["queue"] in QUEUES
    )


shape_passes = 0
meaning_passes = 0
no_tool_call = 0

for message, expected_queue in TEST_CASES:
    print("=" * 60)
    print("Message:", message)
    print("Expected queue:", expected_queue)

    data = get_tool_input(message)
    if data is None:
        no_tool_call += 1
        print("  No tool call. Your code must handle this case.")
        continue

    shape_ok = check_shape(data)
    meaning_ok = data["queue"] == expected_queue
    shape_passes += shape_ok
    meaning_passes += meaning_ok

    print("  Tool input:", data)
    print("  Shape check:", "PASS" if shape_ok else "FAIL")
    print("  Meaning check:", "PASS" if meaning_ok else f"FAIL (got {data['queue']})")

print("\n" + "=" * 60)
print(f"Shape checks passed:   {shape_passes} of {len(TEST_CASES)}")
print(f"Meaning checks passed: {meaning_passes} of {len(TEST_CASES)}")
print(f"No tool call:          {no_tool_call}")
