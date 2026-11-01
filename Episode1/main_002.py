from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

client = Anthropic()

feedback = """
The product works well and I'm happy with the features. 
Only issue is the mobile app loads a bit slowly sometimes.
"""

# ❌ BAD: Tells the model HOW to process
bad_prompt = f"""
Classify this customer feedback.

Feedback: {feedback}

Tell me if it's positive, negative, or neutral.
"""

# ✓ GOOD: States WHAT you want
good_prompt = f"""
Classify this customer feedback as positive, negative, or neutral.
 
Use these criteria:
- Positive: The customer reports a working product and no serious complaints.
- Negative: The customer reports a broken feature, or multiple problems.
- Neutral: The customer has one minor complaint or mixes praise with criticism.
 
Feedback: {feedback}
 
Respond with only the label: POSITIVE, NEGATIVE, or NEUTRAL.
"""

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=100,
    messages=[{"role": "user", "content": good_prompt}]
)

print(response.content[0].text)