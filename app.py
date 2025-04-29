import streamlit as st
from configs.config import HUMAN_CREATED_DIR, TMP_UPLOAD_DIR
from utils.session.session_state import initialize_session_state
from ui.intro import render_intro
from ui.sidebar import render_sidebar_controls
from logic.get_images import handle_get_images
from ui.batch_ui import render_batch_form
from ui.username_gate import ask_username


def main():
    initialize_session_state()
    ask_username()
    render_intro()
    render_sidebar_controls()
    handle_get_images()

    if st.session_state.current_batch:
        render_batch_form()
    elif st.session_state.just_submitted:
        st.success("✅ Your questions and images have been saved!")
        st.info("Press **Get Images** to start a new batch.")
    else:
        st.info("No images yet. Choose source & hit **Get Images**.")


if __name__=="__main__":
    main()
