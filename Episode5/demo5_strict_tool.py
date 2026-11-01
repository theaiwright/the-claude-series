"""
Episode 5 Demo - Part 1: THE STRICT TOOL

Claude routes a support ticket by calling a tool. The tool is marked
strict, so the input follows the schema: required fields are present,
enum fields hold only the listed values, and no extra fields appear.
Our code runs the tool and sends the result back.

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY=your_key_here
  python3 demo5_strict_tool.py
"""

import json

from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
client = Anthropic()
MODEL = "claude-haiku-4-5"
MAX_STEPS = 3

TOOLS = [
    {
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
                "customer_id": {
                    "type": "string",
                    "description": "The customer id, for example C-42.",
                },
                "urgency": {
                    "type": "string",
                    "enum": ["P1", "P2", "P3"],
                    "description": "P1 is urgent. P3 is routine.",
                },
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
]


def route_ticket(args: dict) -> dict:
    # A real application would call the ticketing system here.
    return {"routed": True, "queue": args["queue"], "urgency": args["urgency"]}


def run(message: str) -> str:
    messages = [{"role": "user", "content": message}]

    for step in range(1, MAX_STEPS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason in ("max_tokens", "refusal"):
            raise RuntimeError(f"Stopped with reason {response.stop_reason}. Route to a person.")

        if response.stop_reason != "tool_use":
            return "".join(block.text for block in response.content if block.type == "text")

        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"  Step {step}: {block.name} input = {json.dumps(block.input)}")
            output = route_ticket(block.input)
            results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": json.dumps(output),
            })

        messages.append({"role": "user", "content": results})

    raise RuntimeError(f"No final answer after {MAX_STEPS} steps.")


message = "C-42 here. My card was charged twice this month, and I want the extra charge reversed today."

print("=" * 60)
print("Customer:", message)
print("Final reply:", run(message))
