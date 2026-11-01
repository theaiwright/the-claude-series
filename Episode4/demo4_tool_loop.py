"""
Episode 4 Demo - Part 1: THE TOOL LOOP

Claude receives two tools for an online store. Claude asks for a tool
when it needs one. Our code runs the tool and sends the result back.
The loop stops when Claude gives a final answer.

The data below stands in for a real database, so the file runs without
any other service.

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY=your_key_here
  python3 demo4_tool_loop.py
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


# ---------- Sample data (stands in for a database) ----------

ORDERS = {
    "A1001": {"status": "shipped", "carrier": "BlueDart", "eta": "2026-10-22"},
    "A1002": {"status": "processing", "carrier": None, "eta": None},
}

RETURN_POLICIES = {
    "electronics": "Returns accepted within 10 days. The item must be unused and in its original box.",
    "clothing": "Returns accepted within 30 days. Tags must still be attached.",
    "books": "Returns accepted within 14 days if the book is undamaged.",
}


# ---------- The real functions that our code runs ----------

def get_order_status(order_id: str) -> dict:
    order = ORDERS.get(order_id)
    if order is None:
        return {"error": f"No order found with id {order_id}."}
    return order


def get_return_policy(product_type: str) -> dict:
    policy = RETURN_POLICIES.get(product_type)
    if policy is None:
        return {"error": f"No policy for product type {product_type}."}
    return {"product_type": product_type, "policy": policy}


TOOL_FUNCTIONS = {
    "get_order_status": lambda args: get_order_status(args["order_id"]),
    "get_return_policy": lambda args: get_return_policy(args["product_type"]),
}


# ---------- The tool definitions that Claude sees ----------

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
    {
        "name": "get_return_policy",
        "description": (
            "Returns the return policy for a product category. "
            "Use this when the customer asks whether or how they can return an item. "
            "Does not start a return."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "product_type": {
                    "type": "string",
                    "enum": ["electronics", "clothing", "books"],
                    "description": "The product category.",
                }
            },
            "required": ["product_type"],
        },
    },
]


# ---------- The loop ----------

def ask(question: str) -> str:
    messages = [{"role": "user", "content": question}]

    for round_number in range(1, MAX_ROUNDS + 1):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,
            messages=messages,
        )

        # Save Claude's reply so the next request has the full history.
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "max_tokens":
            raise RuntimeError("Reply was cut off. Increase max_tokens.")

        # Claude has enough information. Return the text of the final answer.
        if response.stop_reason != "tool_use":
            return "".join(block.text for block in response.content if block.type == "text")

        # Claude asked for one or more tools. Run each one.
        results = []
        for block in response.content:
            if block.type == "tool_use":
                print(f"  Round {round_number}: Claude called {block.name} with {block.input}")
                output = TOOL_FUNCTIONS[block.name](block.input)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(output),
                })

        # Every tool result goes in one user message, and the results come first.
        messages.append({"role": "user", "content": results})

    raise RuntimeError(f"No final answer after {MAX_ROUNDS} rounds.")


# ---------- Run three questions ----------

questions = [
    "Where is order A1001, and when will it arrive?",
    "What is the return policy for electronics?",
    "Can you check the status of order A9999?",
]

for question in questions:
    print("=" * 60)
    print("Customer:", question)
    print("Final answer:", ask(question))
