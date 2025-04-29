import shutil
import os
import streamlit as st
from utils.common.human_upload import save_human_record
from configs.config import TMP_UPLOAD_DIR

def handle_save_batch():
    for rec in st.session_state.current_batch:
        save_human_record(rec)  # <-- no user_id passed anymore!

    # Clean TMP_UPLOAD_DIR after save
    shutil.rmtree(TMP_UPLOAD_DIR, ignore_errors=True)
    os.makedirs(TMP_UPLOAD_DIR, exist_ok=True)
