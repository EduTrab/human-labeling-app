# ui/batch_ui.py

import streamlit as st
from logic.save_logic import handle_save_batch

def render_batch_form():
    batch = st.session_state.current_batch
    if not batch:
        return

    with st.form("human_form"):
        for i, rec in enumerate(batch):
            st.image(rec["image_path"], use_container_width=True)
            suffix = f"{i}_{st.session_state.form_reset_counter}"

            rec["question"] = st.text_input(f"Q (#{i+1})", key=f"q_{suffix}")
            opts = {}
            for L in ("A", "B", "C", "D", "E", "F"):
                opts[L] = st.text_input(f"Option {L} (#{i+1})", key=f"opt_{L}_{suffix}")
            rec["options"] = opts
            rec["correct_answer"] = st.selectbox(
                f"Correct (#{i+1})", list(opts.keys()), key=f"corr_{suffix}"
            )
            rec["explanation"] = st.text_area(f"Explanation (optional, #{i+1})", key=f"exp_{suffix}")

        submit = st.form_submit_button("Submit Batch")

    if submit:
        bad = [
            i for i, r in enumerate(batch)
            if not r["question"] or any(not v for v in r["options"].values())
        ]
        if bad:
            st.error(f"⚠️ Fill all fields for images: {', '.join(str(i+1) for i in bad)}")
        else:
            handle_save_batch()
            st.session_state.current_batch = []
            st.session_state.uploaded_files = []
            st.session_state.submitted = True
            st.session_state.just_submitted = True  # ← Add this flag
            st.session_state.form_reset_counter += 1
            st.rerun()  # ← Force UI to redraw clean
