# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
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
        background: #f0f2f6;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    .risk-high {
        color: #ff4b4b;
        font-weight: bold;
    }
    .risk-low {
        color: #34a853;
        font-weight: bold;
    }
    .stPlotlyChart {
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
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
    st.subheader("📈 Organizational Health Dashboard")

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
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(
                '<div class="metric-card">📌 Total Employees<br><h2>{}</h2></div>'.format(
                    len(pred_df)
                ),
                unsafe_allow_html=True,
            )
        with col2:
            st.markdown(
                '<div class="metric-card">⚠️ At-Risk Employees<br><h2 class="risk-high">{}</h2></div>'.format(
                    len(at_risk)
                ),
                unsafe_allow_html=True,
            )
        with col3:
            st.markdown(
                '<div class="metric-card">📉 Avg. Attrition Risk<br><h2>{:.1f}%</h2></div>'.format(
                    pred_df["Attrition_Probability"].mean() * 100
                ),
                unsafe_allow_html=True,
            )
        with col4:
            st.markdown(
                '<div class="metric-card">🏆 Avg. Engagement<br><h2>{:.1f}/5</h2></div>'.format(
                    pred_df["engagement_score"].mean()
                ),
                unsafe_allow_html=True,
            )

        # Visualizations
        col_left, col_right = st.columns([2, 1])
        with col_left:
            # Attrition Probability Distribution
            fig = px.histogram(
                pred_df,
                x="Attrition_Probability",
                nbins=20,
                title="Attrition Risk Distribution",
                color_discrete_sequence=["#ff4b4b"],
            )
            fig.update_layout(bargap=0.1)
            st.plotly_chart(fig, use_container_width=True)

            # Department-wise Analysis
            dept_df = (
                pred_df.groupby("department")["Attrition_Probability"]
                .mean()
                .reset_index()
            )
            fig = px.bar(
                dept_df,
                x="department",
                y="Attrition_Probability",
                title="Department-wise Attrition Risk",
                color="Attrition_Probability",
                color_continuous_scale="RdYlGn_r",
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_right:
            # Risk Segmentation
            fig = px.pie(
                pred_df,
                names="Risk_Label",
                title="Risk Segmentation",
                color_discrete_map={"High Risk": "#ff4b4b", "Low Risk": "#34a853"},
            )
            st.plotly_chart(fig, use_container_width=True)

            # Tenure vs Satisfaction
            fig = px.scatter(
                pred_df,
                x="tenure",
                y="job_satisfaction",
                color="Attrition_Probability",
                title="Tenure vs Job Satisfaction",
                color_continuous_scale="RdYlGn_r",
            )
            st.plotly_chart(fig, use_container_width=True)

        st.session_state["pred_df"] = pred_df
        st.session_state["at_risk"] = at_risk

with tabs[1]:
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

            if st.button("🧠 Generate Retention Plan", type="primary"):
                with st.spinner("Generating AI insights..."):
                    insights = generate_insights(employee.to_dict())
                    st.markdown(f"""
                    **📉 Diagnostic Insight**  
                    {insights['diagnostic']}
                    
                    **✅ Prescriptive Action**  
                    {insights['prescriptive']}
                    
                    **🛡 Preventive Strategy**  
                    {insights['preventive']}
                    """)

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
            st.markdown("#### 📈 Key Visualizations")
            # In the Export Report tab (app.py)
            st.image(
                "https://via.placeholder.com/800x400.png?text=Risk+Distribution+Chart",
                use_container_width=True,
            )  # Updated parameter
            st.image(
                "https://via.placeholder.com/800x400.png?text=Department+Analysis",
                use_container_width=True,
            )  # Updated parameter

        # Export Controls
        st.download_button(
            label="📥 Download Full Report",
            data=st.session_state["pred_df"].to_csv(index=False),
            file_name="attrition_analysis_report.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary",
        )
