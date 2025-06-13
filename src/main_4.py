import streamlit as st
import pandas as pd
import plotly.express as px
from auth import login
from utils import predict_attrition
from llm import generate_insights
from storage_logic import load_data

# Custom CSS for styling
st.set_page_config(page_title="Attrition Insight System", layout="wide", page_icon="📈")
st.title("🚀 AI-Powered Attrition Insight System")
st.markdown(
    """
<style>
    [data-testid="stAppViewContainer"] {
        background: #f8f9fa;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin: 10px 0;
        transition: transform 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-3px);
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 600;
        color: #2c3e50;
        margin: 0.5rem 0;
    }
    .metric-label {
        font-size: 1rem;
        color: #7f8c8d;
    }
    .risk-high {
        color: #e74c3c;
        font-weight: 700;
    }
    .risk-low {
        color: #2ecc71;
        font-weight: 700;
    }
    .stPlotlyChart {
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        background: white;
        padding: 1rem;
    }
    .department-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

if "logged_in" not in st.session_state:
    login()
    st.stop()

# Main tabs
tabs = st.tabs(["📊 Executive Dashboard", "🧑💼 Employee Insights", "📤 Export Report"])

with tabs[0]:
    st.subheader("Organizational Health Overview")

    df = load_data()

    if df is not None:
        if "EmployeeID" not in df.columns:
            df["EmployeeID"] = df.index + 1000

            pred_df = predict_attrition(df)
            at_risk = pred_df[pred_df["Attrition_Probability"] > 0.6]

        # Key Metrics
        cols = st.columns(4)
        metrics = [
            ("👥 Total Employees", len(pred_df), ""),
            ("⚠️ At-Risk Employees", len(at_risk), "risk-high"),
            (
                "📉 Avg. Risk Score",
                f"{pred_df['Attrition_Probability'].mean() * 100:.1f}%",
                "",
            ),
            ("🌟 Avg. Engagement", f"{pred_df['engagement_score'].mean():.1f}/5", ""),
        ]

        for col, (label, value, style) in zip(cols, metrics):
            with col:
                st.markdown(
                    f'<div class="metric-card">'
                    f'<div class="metric-label">{label}</div>'
                    f'<div class="metric-value {style}">{value}</div>'
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # Visualization Section
        st.markdown("---")
        st.subheader("Risk Analysis")

        col1, col2 = st.columns([2, 1])
        with col1:
            # Risk Distribution by Department
            dept_risk = (
                pred_df.groupby("department")["Attrition_Probability"]
                .mean()
                .reset_index()
            )
            fig = px.bar(
                dept_risk.sort_values("Attrition_Probability", ascending=False),
                x="department",
                y="Attrition_Probability",
                color="Attrition_Probability",
                color_continuous_scale="RdYlGn_r",
                title="Departmental Attrition Risk Levels",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Clear Risk Segmentation
            risk_counts = pred_df["Risk_Label"].value_counts().reset_index()
            fig = px.bar(
                risk_counts,
                x="count",
                y="Risk_Label",
                orientation="h",
                color="Risk_Label",
                color_discrete_map={"High Risk": "#e74c3c", "Low Risk": "#2ecc71"},
                title="Employee Risk Distribution",
                labels={"count": "Number of Employees", "Risk_Label": "Risk Category"},
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("Key Drivers Analysis")

        col1, col2 = st.columns(2)
        with col1:
            # Engagement vs Attrition
            fig = px.scatter(
                pred_df,
                x="engagement_score",
                y="Attrition_Probability",
                color="department",
                trendline="lowess",
                title="Engagement Score vs Attrition Risk",
                labels={"engagement_score": "Engagement Score (1-5)"},
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Tenure Impact Analysis
            tenure_bins = pd.cut(pred_df["tenure"], bins=5)
            tenure_bins_str = tenure_bins.astype(str)  # Convert intervals to string

            # Now, you can group by the tenure bins (which are strings now)
            tenure_risk = (
                pred_df.groupby(tenure_bins_str)["Attrition_Probability"]
                .mean()
                .reset_index()
            )

            fig = px.line(
                tenure_risk,
                x="tenure",
                y="Attrition_Probability",
                markers=True,
                title="Tenure Impact on Attrition Risk",
                labels={
                    "tenure": "Tenure Range (years)",
                    "Attrition_Probability": "Avg. Risk Score",
                },
            )
            fig.update_traces(line=dict(color="#e74c3c", width=2.5))
            st.plotly_chart(fig, use_container_width=True)

        # --- Departmental Analysis Section from main_2.py ---
        st.markdown("---")
        st.subheader("Departmental Analysis")

        # Department Metrics
        dept_df = (
            pred_df.groupby("department")
            .agg(
                {
                    "Attrition_Probability": "mean",
                    "EmployeeID": "count",
                    "engagement_score": "mean",
                }
            )
            .reset_index()
        )

        cols = st.columns(3)
        for idx, row in dept_df.sort_values(
            "Attrition_Probability", ascending=False
        ).iterrows():
            with cols[idx % 3]:
                st.markdown(
                    f'<div class="department-card">'
                    f'<h4>{row["department"]}</h4>'
                    f'<div style="margin: 1rem 0;">'
                    f'<div>👥 Employees: {row["EmployeeID"]}</div>'
                    f'<div>📉 Risk: {row["Attrition_Probability"]*100:.1f}%</div>'
                    f'<div>🌟 Engagement: {row["engagement_score"]:.1f}/5</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

        st.session_state["pred_df"] = pred_df
        st.session_state["at_risk"] = at_risk

with tabs[1]:
    # Preserved Employee Insights Tab
    st.subheader("🧑💼 Employee Risk Analysis")
    if "pred_df" in st.session_state:
        # Interactive Data Grid
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("### 🎯 Employee Risk Explorer")
            filtered_df = st.data_editor(
                st.session_state["pred_df"],
                column_config={
                    "Attrition_Probability": st.column_config.ProgressColumn(
                        "Risk Score",
                        help="Attrition Probability",
                        format="%.2f",
                        min_value=0,
                        max_value=1,
                    ),
                    "Risk_Flag": st.column_config.TextColumn(
                        "Risk Status",
                        help="Employee Risk Classification",
                    ),
                },
                hide_index=True,
                use_container_width=True,
            )

        with col2:
            st.markdown("### 🔍 Employee Detail View")
            selected_id = st.selectbox(
                "Select Employee ID", options=filtered_df["EmployeeID"].unique()
            )
            employee = filtered_df[filtered_df["EmployeeID"] == selected_id].iloc[0]

            st.markdown(
                f"""
            <div class="metric-card">
                <h4>Employee #{selected_id}</h4>
                <p>Department: {employee['department']}<br>
                Tenure: {employee['tenure']} years<br>
                Engagement: {employee['engagement_score']}/5<br>
                Risk Score: <span class="{'risk-high' if employee['Attrition_Probability'] > 0.6 else 'risk-low'}">
                {employee['Attrition_Probability']:.0%}</span></p>
            </div>
            """,
                unsafe_allow_html=True,
            )

            # Generate Insights# In your Employee Insights tab (tabs[1]):
            if st.button("🧠 Generate Retention Plan", type="primary"):
                with st.spinner("Generating AI insights..."):
                    insights = generate_insights(employee.to_dict())

                    st.markdown("### 📉 Diagnostic Insight")
                    st.markdown(insights["diagnostic"])

                    st.markdown("### ✅ Prescriptive Actions")
                    st.markdown(insights["prescriptive"])

                    st.markdown("### 🛡 Preventive Strategy")
                    st.markdown(insights["preventive"])

with tabs[2]:
    st.subheader("📤 Report Generation")
    if "pred_df" in st.session_state:
        # Professional Report Section
        st.markdown("### 📑 Executive Summary Report")

        with st.expander("🔧 Report Configuration"):
            col1, col2 = st.columns(2)
            with col1:
                report_scope = st.radio(
                    "Report Scope", ["Full Organization", "High Risk Employees Only"]
                )
            with col2:
                report_format = st.selectbox("Format", ["PDF", "PowerPoint", "Excel"])

        # Report Preview
        st.markdown("### 📋 Report Preview")
        with st.container(border=True):
            st.markdown("#### 🏢 Organization Attrition Overview")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Employees", len(st.session_state["pred_df"]))
                st.metric(
                    "Average Tenure",
                    f"{st.session_state['pred_df']['tenure'].mean():.1f} years",
                )
            with col2:
                st.metric("High Risk Employees", len(st.session_state["at_risk"]))
                st.metric(
                    "Average Engagement Score",
                    f"{st.session_state['pred_df']['engagement_score'].mean():.1f}/5",
                )

            st.divider()
            st.markdown("#### 📈 Key Findings")
            st.markdown("""
            - Detailed analysis of attrition patterns across departments
            - Correlation between engagement scores and attrition risk
            - Identification of high-risk employee segments
            """)

        # Export Controls
        st.download_button(
            label="📥 Download Full Report",
            data=st.session_state["pred_df"].to_csv(index=False),
            file_name="attrition_analysis_report.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary",
        )
