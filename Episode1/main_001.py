from anthropic import Anthropic
import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

client = Anthropic()

feedback = """
I've been using this platform for about 3 months now. Overall, I like 
the core functionality—it saves us time on repetitive tasks and the 
dashboard is intuitive. However, the performance has been a real issue. 
Our queries often take 2-3 minutes to run, which is frustrating when 
we're trying to iterate quickly. 

The pricing is also higher than competitors, but honestly, if the speed 
improved, I'd be willing to pay. The support team has been helpful 
when we had issues with setup, and they responded within 24 hours, 
which I appreciate. But we've had two outages in the last month, and 
there was no communication during the first one, which was concerning.

If you fix the performance and improve status page communication during 
incidents, this becomes a 5-star product.
"""

# ❌ BAD: Tells the model HOW to process
bad_prompt_1 = f"""
Summarize this feedback. Find main points.
write in a paragraph.

Feedback: {feedback}
"""

# ✓ GOOD: States WHAT you want
good_prompt_1 = f"""
Summarize this feedback in one paragraph, under 150 words, 
including: main issue, positive aspect, recommendation.

Feedback: {feedback}
"""

response = client.messages.create(
    model="claude-haiku-4-5",
    max_tokens=150,
    messages=[{"role": "user", "content": good_prompt_1}]
)

print(response.content[0].text)