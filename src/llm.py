import openai
import re
import json
import streamlit as st
from dotenv import load_dotenv

import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")  # Update this


def generate_insights(employee_row):
    """Enhanced with error handling and better parsing"""
    try:
        prompt = f"""
        Analyze this employee data and provide insights in EXACTLY this format:
        
        Employee Profile:
        - Department: {employee_row.get('department', 'N/A')}
        - Tenure: {employee_row.get('tenure', 'N/A')} years
        - Engagement: {employee_row.get('engagement_score', 'N/A')}/5
        - Risk Score: {employee_row.get('Attrition_Probability', 'N/A'):.0%}
        
        Required insights:
        1. Diagnostic Analysis (why they might leave)
        2. Retention Recommendations (specific actions)
        3. Preventive Strategies (organizational improvements)
        
        Format exactly as:
        Diagnostic: ...
        Prescriptive: ...
        Preventive: ...
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,  # Reduced for more consistent HR recommendations
            max_tokens=500,
        )

        text = response.choices[0].message.content
        output = {"diagnostic": "", "prescriptive": "", "preventive": ""}

        # More robust parsing using regex
        patterns = {
            "diagnostic": r"Diagnostic:\s*(.*)",
            "prescriptive": r"Prescriptive:\s*(.*)",
            "preventive": r"Preventive:\s*(.*)",
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                output[key] = match.group(1).strip()

        return output

    except Exception as e:
        st.error(f"Insight generation failed: {str(e)}")
        return {
            "diagnostic": "Analysis unavailable",
            "prescriptive": "",
            "preventive": "",
        }


def nlp_query(query, dataframe):
    """Safer implementation with validation"""
    try:
        prompt = f"""
        Convert this HR query into data filters:
        Query: "{query}"
        
        Available columns: {list(dataframe.columns)}
        
        Return JSON format with column names as keys and conditions as values.
        Only use existing columns. Example:
        {{"department": "Engineering", "Attrition_Probability": ">0.7"}}
        
        Return ONLY the JSON object, no other text.
        """

        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,  # Lower for more precise filtering
            max_tokens=200,
        )

        # Safer JSON extraction
        json_str = re.search(r"\{[^}]*\}", response.choices[0].message.content).group()
        filters = json.loads(json_str)  # Safer than eval()

        # Validate filters
        valid_columns = set(dataframe.columns)
        filtered_df = dataframe.copy()

        for col, condition in filters.items():
            if col not in valid_columns:
                st.warning(f"Ignoring invalid column: {col}")
                continue

            # Handle numerical comparisons
            if isinstance(condition, str) and any(
                op in condition for op in [">", "<", "="]
            ):
                try:
                    filtered_df = filtered_df.query(f"{col}{condition}")
                except Exception as e:
                    st.error(f"Invalid condition: {col}{condition}. Error: {str(e)}")
            else:
                filtered_df = filtered_df[
                    filtered_df[col].astype(str) == str(condition)
                ]

        return filtered_df

    except Exception as e:
        st.error(f"Query processing error: {str(e)}")
        return dataframe
