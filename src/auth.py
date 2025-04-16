import streamlit as st

USERS = {"hr_manager": "secure123", "stakeholder": "insight456"}

def login():
    st.title("🔐 Login Portal")
    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")
    if st.button("Login"):
        if USERS.get(user) == pwd:
            st.session_state['logged_in'] = True
            st.rerun()
        else:
            st.error("Invalid credentials")
