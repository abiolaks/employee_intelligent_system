# auth.py
import streamlit as st
from streamlit_extras.colored_header import colored_header
from streamlit_extras.stylable_container import stylable_container

# 1. ABSOLUTELY FIRST COMMAND - No exceptions


# 2. Then other imports if needed


# 3. Constants and configurations
USERS = {
    "hr_manager": "secure123",
    "stakeholder": "insight456",
    "executive": "vision789",
}


def login():
    """Main login function with proper command ordering"""
    # Custom CSS (must come after set_page_config)
    st.markdown(
        """
    <style>
        [data-testid="stAppViewContainer"] {
            background: #f9f5f0;
            background-image: radial-gradient(#e8e3dd 1px, transparent 0);
            background-size: 20px 20px;
        }
        .login-card {
            background: white;
            border-radius: 16px;
            padding: 2.5rem;
            box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
        }
        .stTextInput>div>div>input {
            border-radius: 12px !important;
            padding: 12px !important;
            border: 1px solid #e0e0e0 !important;
        }
        .stButton>button {
            border-radius: 12px !important;
            background: #5b7db1 !important;
        }
        header {visibility: hidden;}
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Main layout
    with st.container():
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            with stylable_container(
                key="login_card",
                css_styles="background: white; border-radius: 16px; padding: 2.5rem;",
            ):
                colored_header(
                    label="Welcome to Attrition Insight Pro",
                    description="AI-powered workforce analytics",
                    color_name="blue-70",
                )

                st.image(
                    "https://img.freepik.com/free-vector/business-people-analyzing-growth-charts_74855-5289.jpg",
                    use_container_width=True,
                )

                with st.form("auth_form"):
                    user = st.text_input(
                        "Username", placeholder="Your organizational ID"
                    )
                    pwd = st.text_input(
                        "Password", type="password", placeholder="••••••••"
                    )

                    if st.form_submit_button("Access Dashboard →", type="primary"):
                        if USERS.get(user) == pwd:
                            st.session_state["logged_in"] = True
                            st.rerun()
                        else:
                            st.error("Invalid credentials")

                st.markdown(
                    """
                <div style='text-align: center; margin-top: 1rem; color: #666;'>
                    <small>v2.1 | Secure HR Analytics</small>
                </div>
                """,
                    unsafe_allow_html=True,
                )


# 4. Execution control
if __name__ == "__main__":
    if "logged_in" not in st.session_state:
        login()
    else:
        st.switch_page("main_4.py")  # Your main app page
