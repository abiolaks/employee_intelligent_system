from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# Initialize DeepSeek client
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)


def generate_insights(employee_row):
    prompt = f"""
You are an HR analytics assistant. For the following employee:

{employee_row}

Please return:
1. Diagnostic Insight - Why might this employee leave?
2. Prescriptive Insight - What can be done to retain them?
3. Preventive Insight - What company-wide policy might help prevent similar attrition?

Format the output exactly like this:
Diagnostic: ...
Prescriptive: ...
Preventive: ...
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )

    text = response.choices[0].message.content
    output = {"diagnostic": "", "prescriptive": "", "preventive": ""}

    for line in text.split("\n"):
        line = line.strip()
        if line.lower().startswith("diagnostic:"):
            output["diagnostic"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("prescriptive:"):
            output["prescriptive"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("preventive:"):
            output["preventive"] = line.split(":", 1)[1].strip()

    return output
