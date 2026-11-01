"""
Episode 2 Demo - Part 2: FEW-SHOT (revised)

Same task as demo2_zero_shot_v2.py. Three examples show our team's
codes, so Claude copies our scheme instead of inventing its own.
Then we test on a message the examples never covered.

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY=your_key_here
  python3 demo2_few_shot_v2.py
"""

from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

client = Anthropic()


def build_prompt(message: str) -> str:
    return f"""
Convert customer support messages into ticket codes using this exact format:
URGENCY-CATEGORY-SENTIMENT

Examples:

Message: "I was charged twice for my subscription this month!"
Code: P1-BILL-NEG

Message: "How do I reset my password?"
Code: P2-ACCT-NEU

Message: "Love the new update, everything works great now!"
Code: P3-TECH-POS

Now convert this message. Respond with only the code.

Message: "{message}"
Code:
"""


def classify(message: str) -> str:
    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=10,
        messages=[{"role": "user", "content": build_prompt(message)}]
    )
    return response.content[0].text.strip()


# --- Same message as the zero-shot demo, run 3 times ---
# message = "My payment failed twice today and I'm being charged extra fees. This is unacceptable."

# print("=" * 60)
# print("FEW-SHOT: 3 team examples given before the request")
# print("Team format we need:  P1-BILL-NEG")
# print("=" * 60)

# for i in range(3):
#     print(f"Run {i + 1}: {classify(message)}")

# --- A message the examples never covered ---
new_message = "The app crashes sometimes when I try to upload a photo."

print("\n" + "=" * 60)
print("Testing on an unseen message")
print("=" * 60)
print(f"Message: {new_message}")
print(f"Code:    {classify(new_message)}")
print("\nThe output follows our scheme, including a category the")
print("examples never showed (TECH with a negative sentiment).")
