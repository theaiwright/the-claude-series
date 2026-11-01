"""
Episode 2 Demo - Part 1: ZERO-SHOT (revised)

Our team uses its own ticket codes:
  Urgency:   P1 (act today), P2 (act this week), P3 (no deadline)
  Category:  BILL, TECH, ACCT
  Sentiment: POS, NEU, NEG

The prompt below names the format but gives no examples.
Claude has no way to know our codes, so it invents its own.

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY=your_key_here
  python3 demo2_zero_shot_v2.py
"""

from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

client = Anthropic()


message = "My payment failed twice today and I'm being charged extra fees. This is unacceptable."

zero_shot_prompt = f"""
Convert this customer support message into a ticket code.
Use the format URGENCY-CATEGORY-SENTIMENT.

Message: "{message}"
"""

print("=" * 60)
print("ZERO-SHOT: format named, no examples")
print("Team format we need:  P1-BILL-NEG")
print("=" * 60)

for i in range(3):
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=20,
        messages=[{"role": "user", "content": zero_shot_prompt}]
    )
    print(f"Run {i + 1}: {response.content[0].text.strip()}")

print("\nIf the output is consistent but not our codes, that's the lesson:")
print("consistency is not the same as correctness.")
