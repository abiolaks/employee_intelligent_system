from openai import OpenAI
from dotenv import load_dotenv
import os
import re

load_dotenv()

# Initialize DeepSeek client
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1",
)


def generate_insights(employee_row):
    # Extract key metrics with proper formatting
    risk_level = (
        "High Risk"
        if employee_row.get("Attrition_Probability", 0) > 0.6
        else "Low Risk"
    )

    # Build detailed employee profile string
    profile = "\n".join(
        [
            f"- **{key.replace('_', ' ').title()}**: {value}"
            for key, value in employee_row.items()
            if key
            not in ["EmployeeID", "Risk_Label", "Risk_Flag"]  # Exclude redundant fields
        ]
    )

    prompt = f"""
## Role
You are an HR analytics specialist analyzing employee retention risks. 
Generate data-driven insights for this employee classified as **{risk_level}**.

## Employee Profile
{profile}

## Task
Provide three insights in markdown format:
1. **DIAGNOSTIC**: Identify key retention factors based on SPECIFIC data points
2. **PRESCRIPTIVE**: Recommend personalized retention actions in bullet points
3. **PREVENTIVE**: Suggest one scalable policy for similar employees

## Rules
- For LOW RISK employees: Focus on strengthening retention factors
- For HIGH RISK employees: Focus on mitigating attrition risks
- Reference ACTUAL METRICS from the profile (e.g., "Job Satisfaction: 3")
- Provide CONCRETE action items, not generic advice
- Consider: Engagement, Compensation, Workload, Development, Work-Life Balance
- Use **bold** for metric references
- Output MUST contain exactly 3 sections with headers

## Output Format EXACTLY:
### Diagnostic Insight
[Concise analysis with data references]

### Prescriptive Actions
- [Action 1]
- [Action 2]
- [Action 3]

### Preventive Strategy
[One policy suggestion]
"""

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500,
            top_p=0.9,
        )

        raw_text = response.choices[0].message.content.strip()

        # Robust parsing using regex
        insights = {"diagnostic": "", "prescriptive": "", "preventive": ""}

        patterns = {
            "diagnostic": r"### Diagnostic Insight\n+(.*?)(?=\n### Prescriptive Actions|$)",
            "prescriptive": r"### Prescriptive Actions\n+(.*?)(?=\n### Preventive Strategy|$)",
            "preventive": r"### Preventive Strategy\n+(.*)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, raw_text, re.DOTALL | re.IGNORECASE)
            if match:
                insights[key] = match.group(1).strip()
            else:
                # Fallback to simple parsing
                if "Diagnostic Insight" in raw_text:
                    insights["diagnostic"] = (
                        raw_text.split("Diagnostic Insight")[1]
                        .split("Prescriptive Actions")[0]
                        .strip(": \n")
                    )
                if "Prescriptive Actions" in raw_text:
                    insights["prescriptive"] = (
                        raw_text.split("Prescriptive Actions")[1]
                        .split("Preventive Strategy")[0]
                        .strip(": \n")
                    )
                if "Preventive Strategy" in raw_text:
                    insights["preventive"] = raw_text.split("Preventive Strategy")[
                        1
                    ].strip(": \n")

                # Final fallback if still empty
                if not insights[key]:
                    insights[key] = (
                        f"⚠️ Insight generation failed for {key.replace('_', ' ').title()}"
                    )

        return insights

    except Exception as e:
        return {
            "diagnostic": f"**API Error**: {str(e)}",
            "prescriptive": "Please try again later",
            "preventive": "System maintenance in progress",
        }
