# auth.py (updated)
import streamlit as st

USERS = {"hr_manager": "secure123", "stakeholder": "insight456"}


def login():
    st.markdown(
        """
    <style>
        .login-container {
            max-width: 400px;
            padding: 3rem;
            margin: 5% auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .stTextInput input {border-radius: 8px;}
    </style>
    """,
        unsafe_allow_html=True,
    )

    with st.container():
        col1, col2, col3 = st.columns([1, 3, 1])
        with col2:
            st.markdown('<div class="login-container">', unsafe_allow_html=True)
            st.image(
                "https://img.freepik.com/premium-photo/people-generating-images-using-artificial-intelligence-laptop_23-2150794312.jpg?w=996",
                use_container_width=True,
            )  # Updated parameter
            st.title("🔒 HR Analytics Portal")
            user = st.text_input("Username")
            pwd = st.text_input("Password", type="password")
            if st.button("Login →", type="primary", use_container_width=True):
                if USERS.get(user) == pwd:
                    st.session_state["logged_in"] = True
                    st.rerun()
                else:
                    st.error("Invalid credentials")
            st.markdown("</div>", unsafe_allow_html=True)
