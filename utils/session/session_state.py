import streamlit as st, uuid

def initialize_session_state():
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())[:8]
    if "batch_size" not in st.session_state:
        st.session_state.batch_size = 3
    if "dataset_source" not in st.session_state:
        st.session_state.dataset_source = "Default"
    if "current_batch" not in st.session_state:
        st.session_state.current_batch = []
    if "uploaded_files" not in st.session_state:
        st.session_state.uploaded_files = []
    if "local_records" not in st.session_state:
        st.session_state.local_records = []   # <-- ADD THIS
    if "processed_files" not in st.session_state:
        st.session_state.processed_files = set()  # <-- ADD THIS
    if "city_name" not in st.session_state:
        st.session_state.city_name = ""
    if "city_latlon" not in st.session_state:
        st.session_state.city_latlon = None
    if "submitted" not in st.session_state:
        st.session_state.submitted = False
    if "form_reset_counter" not in st.session_state:
        st.session_state.form_reset_counter = 0
    if "just_submitted" not in st.session_state:
        st.session_state.just_submitted = False
