# ui/username_gate.py

import streamlit as st
import random
import string

def ask_username():
    if "username" not in st.session_state:
        st.session_state.username = None

    if st.session_state.username:
        return

    st.title("🔐 Welcome to Human Q&A Builder")

    st.markdown("""
    Please fill your information to start:
    """)

    name = st.text_input("Name")
    surname = st.text_input("Surname")
    birthday = st.text_input("Birthday (optional, format: DDMMYYYY)")

    if st.button("Start Session"):
        if not name or not surname:
            st.error("Please enter both name and surname.")
            st.stop()

        parts = [name.strip(), surname.strip()]
        if birthday.strip():
            parts.append(birthday.strip())

        base_username = "_".join(parts)
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        full_username = f"{base_username}_{random_suffix}"

        st.session_state.username_base = base_username  # <- added clean base
        st.session_state.username = full_username  # <- with random

        st.success(f"✅ Session started for {base_username}")
        st.rerun()
