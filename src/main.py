import streamlit as st
import pandas as pd
from auth import login
from utils import predict_attrition
from llm import generate_insights

if "logged_in" not in st.session_state:
    login()
    st.stop()

st.set_page_config(page_title="Attrition Insight System", layout="wide")
st.title("🧠 AI-Powered Attrition Insight System")

tabs = st.tabs(["📈 Dashboard", "📁 Upload & Predict", "🧠 LLM Insights"])

with tabs[0]:
    st.subheader("📊 Business Health Overview")

    uploaded = st.file_uploader("Upload Employee Dataset", type="csv")
    if uploaded:
        df = pd.read_csv(uploaded)
        if "EmployeeID" not in df.columns:
            df["EmployeeID"] = df.index + 1000  # Auto-generate ID if missing
        pred_df = predict_attrition(df)
        at_risk = pred_df[pred_df["Attrition_Probability"] > 0.6]

        st.markdown("### 🧑 Employees At Risk (> 60%)")

        for i, row in at_risk.iterrows():
            emp_id = row["EmployeeID"]
            with st.expander(
                f"🔍 Employee ID {emp_id} - Risk: {row['Attrition_Probability']:.2f}"
            ):
                st.write(row)

                if st.button(
                    f"🧠 Generate Insight for ID {emp_id}", key=f"insight_{i}"
                ):
                    insights = generate_insights(row.to_dict())
                    st.markdown(f"**Diagnostic:** {insights['diagnostic']}")
                    st.markdown(f"**Prescriptive:** {insights['prescriptive']}")
                    st.markdown(f"**Preventive:** {insights['preventive']}")

with tabs[1]:
    st.subheader("📁 Upload & Predict")
    uploaded_2 = st.file_uploader("Upload for Prediction", type="csv", key="upload2")
    if uploaded_2:
        df = pd.read_csv(uploaded_2)
        pred_df = predict_attrition(df)
        st.dataframe(pred_df)

with tabs[2]:
    st.subheader("🧠 LLM-Driven Insights")
    if uploaded_2:
        row = pred_df.iloc[0].to_dict()
        insights = generate_insights(row)
        st.markdown("### 🔍 Diagnostic Insight")
        st.info(insights["diagnostic"])

        st.markdown("### 💡 Prescriptive Insight")
        st.success(insights["prescriptive"])

        st.markdown("### 🛡️ Preventive Insight")
        st.warning(insights["preventive"])
