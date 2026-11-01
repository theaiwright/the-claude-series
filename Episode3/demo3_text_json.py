"""
Episode 3 Demo - Part 1: ASKING FOR JSON IN PLAIN TEXT

We ask Claude for a JSON object in the prompt and then parse the reply
with json.loads. Nothing enforces the format. The reply may contain
extra prose, Markdown code fences, or a different key name, and the
parse step will then fail.

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY=your_key_here
  python3 demo3_text_json.py
"""

import json

from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

client = Anthropic()

ticket = "My payment failed twice today and I'm being charged extra fees. This is unacceptable."

prompt = f"""
Classify this customer support message. Return a JSON object with these keys:
- urgency: P1, P2, or P3
- category: BILL, TECH, or ACCT
- sentiment: POS, NEU, or NEG
- summary: one sentence

Message: "{ticket}"
"""

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=300,
    messages=[{"role": "user", "content": prompt}],
)

text = response.content[0].text

print("=" * 60)
print("RAW TEXT RETURNED BY CLAUDE")
print("=" * 60)
print(text)

print("\n" + "=" * 60)
print("ATTEMPTING TO PARSE")
print("=" * 60)

try:
    data = json.loads(text)
    print("Parsed successfully:")
    print(data)
    print("Urgency value:", data["urgency"])
except json.JSONDecodeError as error:
    print("PARSE FAILED:", error)
    print("Claude added text or formatting around the JSON.")
except KeyError as error:
    print("PARSE SUCCEEDED, BUT A KEY IS MISSING:", error)
