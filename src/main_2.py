# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from auth import login
from utils import predict_attrition
from llm import generate_insights

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

    uploaded = st.file_uploader(
        "Upload Employee Dataset", type="csv", key="dashboard_upload"
    )
    if uploaded:
        df = pd.read_csv(uploaded)
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
        st.subheader("Risk Distribution Analysis")

        # First Row of Visualizations
        col1, col2 = st.columns([2, 1])
        with col1:
            # Risk Distribution Heatmap
            fig = px.density_heatmap(
                pred_df,
                x="tenure",
                y="job_satisfaction",
                z="Attrition_Probability",
                title="Tenure vs Satisfaction Risk Heatmap",
                color_continuous_scale="Viridis",
                nbinsx=15,
                nbinsy=15,
            )
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Risk Segmentation Donut Chart
            fig = go.Figure()
            fig.add_trace(
                go.Pie(
                    values=pred_df["Risk_Label"].value_counts(),
                    labels=pred_df["Risk_Label"].unique(),
                    hole=0.5,
                    marker_colors=["#e74c3c", "#2ecc71"],
                    textinfo="percent+label",
                )
            )
            fig.update_layout(
                title="Risk Segmentation", showlegend=False, margin=dict(t=40, b=20)
            )
            st.plotly_chart(fig, use_container_width=True)

        # Second Row of Visualizations
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

        # Third Row of Visualizations
        col1, col2 = st.columns(2)
        with col1:
            # Attrition Distribution by Department
            fig = px.box(
                pred_df,
                x="department",
                y="Attrition_Probability",
                color="department",
                title="Department-wise Risk Distribution",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Engagement vs Risk Scatter
            fig = px.scatter(
                pred_df,
                x="engagement_score",
                y="Attrition_Probability",
                color="department",
                trendline="lowess",
                title="Engagement vs Attrition Risk",
                color_discrete_sequence=px.colors.qualitative.Pastel,
            )
            st.plotly_chart(fig, use_container_width=True)

        st.session_state["pred_df"] = pred_df
        st.session_state["at_risk"] = at_risk

with tabs[1]:
    # (Keep the existing Employee Insights tab implementation)
    pass

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
