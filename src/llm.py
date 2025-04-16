import openai
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")  # Update this


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

    response = openai.chat.completions.create(
        model="gpt-4", messages=[{"role": "user", "content": prompt}], temperature=0.7
    )

    text = response.choices[0].message.content
    output = {"diagnostic": "", "prescriptive": "", "preventive": ""}

    for line in text.split("\n"):
        if line.lower().startswith("diagnostic:"):
            output["diagnostic"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("prescriptive:"):
            output["prescriptive"] = line.split(":", 1)[1].strip()
        elif line.lower().startswith("preventive:"):
            output["preventive"] = line.split(":", 1)[1].strip()

    return output
