"""
Episode 4 Demo - Part 2: WHEN A TOOL FAILS

The order service is unavailable for order A2000. The tool raises an
error. Our code reports that failure to Claude with is_error set to
true, so Claude can explain the problem instead of guessing.

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY=your_key_here
  python3 demo4_tool_error.py
"""

import json

from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

client = Anthropic()
MODEL = "claude-haiku-4-5"
MAX_ROUNDS = 5

ORDERS = {
    "A1001": {"status": "shipped", "carrier": "BlueDart", "eta": "2026-10-22"},
}


def get_order_status(order_id: str) -> dict:
    # Simulated outage for one order. A real service might fail the same way.
    if order_id == "A2000":
        raise TimeoutError("order service did not respond within 5 seconds")
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": f"No order found with id {order_id}."}
    return order


TOOLS = [
    {
        "name": "get_order_status",
        "description": (
            "Looks up the current status of a customer order using its order id. "
            "Use this when the customer asks where an order is or when it will arrive. "
            "Returns the status, carrier, and estimated delivery date. "
            "Does not change the order."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "The order id, for example A1001.",
                }
            },
            "required": ["order_id"],
        },
    },
]


def ask(question: str) -> str:
    messages = [{"role": "user", "content": question}]

    for round_number in range(1, MAX_ROUNDS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "max_tokens":
            raise RuntimeError("Reply was cut off. Increase max_tokens.")

        if response.stop_reason != "tool_use":
            return "".join(block.text for block in response.content if block.type == "text")

        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            print(f"  Round {round_number}: Claude called {block.name} with {block.input}")
            try:
                output = get_order_status(block.input["order_id"])
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(output),
                })
            except Exception as error:
                # Report the failure clearly, and mark it as an error.
                print(f"  Tool failed: {type(error).__name__}: {error}")
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": (
                        f"{type(error).__name__}: {error}. "
                        "The order service is unavailable right now. "
                        "Tell the customer the status cannot be checked at the moment."
                    ),
                    "is_error": True,
                })

        messages.append({"role": "user", "content": results})

    raise RuntimeError(f"No final answer after {MAX_ROUNDS} rounds.")


for question in [
    "Where is order A2000?",
    "Where is order A1001?",
]:
    print("=" * 60)
    print("Customer:", question)
    print("Final answer:", ask(question))
