"""
Episode 7 Demo - Part 1: DESCRIPTIONS DECIDE WHICH TOOL CLAUDE PICKS

We offer Claude the same two tools in two versions:
  - Vague: names and descriptions that say almost nothing.
  - Detailed: descriptions that say what the tool does, when to use it,
    what it returns, and what it does not do.

Each customer question has one correct tool. We ask Claude the same
questions with both versions, and we count how often it picks the
correct tool.

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY=your_key_here
  python3 demo7_descriptions.py
"""

from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
client = Anthropic()
MODEL = "claude-haiku-4-5"

VAGUE_TOOLS = [
    {
        "name": "get_data",
        "description": "Gets data.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string"}},
            "required": ["query"],
        },
    },
    {
        "name": "policy_lookup",
        "description": "Looks up policy.",
        "input_schema": {
            "type": "object",
            "properties": {"topic": {"type": "string"}},
            "required": ["topic"],
        },
    },
]

DETAILED_TOOLS = [
    {
        "name": "order_status",
        "description": (
            "Returns the current status, carrier, and estimated delivery date for one "
            "customer order, using its order id. Use this when a customer asks where an "
            "order is or when it will arrive. Does not change the order."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order id, for example A1001."}
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "return_policy",
        "description": (
            "Returns the return window and the conditions for one product category. "
            "Use this when a customer asks whether or how they can return an item. "
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

# Each test case: a customer question and the tool we expect Claude to pick.
TEST_CASES = [
    ("Where is my order A1001? I want to know when it arrives.", "order_status"),
    ("Can I return the electronics I bought last week?", "return_policy"),
]

RUNS_PER_CASE = 2


def chosen_tool(tools: list, question: str) -> str | None:
    """Return the name of the first tool Claude requests, or None if it requests none."""
    response = client.messages.create(
        model=MODEL,
        max_tokens=300,
        tools=tools,
        messages=[{"role": "user", "content": question}],
    )
    for block in response.content:
        if block.type == "tool_use":
            return block.name
    return None


def run_condition(label: str, tools: list) -> int:
    print("=" * 60)
    print(label)
    correct = 0
    for question, expected in TEST_CASES:
        for run in range(1, RUNS_PER_CASE + 1):
            picked = chosen_tool(tools, question)
            hit = picked == expected
            correct += hit
            print(f"  Run {run} | expected {expected:<14} | picked {str(picked):<14} | {'OK' if hit else 'MISS'}")
    total = len(TEST_CASES) * RUNS_PER_CASE
    print(f"  Correct picks: {correct} of {total}")
    return correct


vague_correct = run_condition("VAGUE descriptions", VAGUE_TOOLS)
detailed_correct = run_condition("DETAILED descriptions", DETAILED_TOOLS)

print("=" * 60)
print(f"Vague: {vague_correct} correct. Detailed: {detailed_correct} correct.")
