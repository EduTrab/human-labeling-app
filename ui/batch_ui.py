# ui/batch_ui.py

import os
import streamlit as st
from logic.save_logic import save_single_record  # <-- new small function you'll add in save_logic.py

def render_batch_form():
    batch = st.session_state.current_batch
    if not batch:
        return

    with st.form("human_form"):
        for i, rec in enumerate(batch):
            st.image(rec["image_path"], use_container_width=True)
            suffix = f"{i}_{st.session_state.form_reset_counter}"

            rec["not_relevant"] = st.checkbox("Mark as Not Relevant", key=f"not_relevant_{suffix}")

            if not rec["not_relevant"]:
                rec["question"] = st.text_input(f"Q (#{i+1})", key=f"q_{suffix}")
                opts = {}
                for L in ("A", "B", "C", "D", "E", "F"):
                    opts[L] = st.text_input(f"Option {L} (#{i+1})", key=f"opt_{L}_{suffix}")
                rec["options"] = opts
                rec["correct_answer"] = st.selectbox(
                    f"Correct (#{i+1})", list(opts.keys()), key=f"corr_{suffix}"
                )
                rec["explanation"] = st.text_area(f"Explanation (optional, #{i+1})", key=f"exp_{suffix}")
            else:
                # For not relevant, we don't ask any text fields
                rec["question"] = ""
                rec["options"] = {L: "" for L in ("A", "B", "C", "D", "E", "F")}
                rec["correct_answer"] = ""
                rec["explanation"] = ""

        submit = st.form_submit_button("Submit Batch")

    if submit:
        bad = [
            i for i, r in enumerate(batch)
            if not r.get("not_relevant") and (not r.get("question") or any(not v for v in r.get("options", {}).values()))
        ]
        if bad:
            st.error(f"⚠️ Fill all fields for images: {', '.join(str(i+1) for i in bad)}")
        else:
            to_save = [r for r in batch if not r.get("not_relevant")]
            to_discard = [r for r in batch if r.get("not_relevant")]

            # Save only good images
            for rec in to_save:
                save_single_record(rec)

            # Delete not relevant images
            for rec in to_discard:
                try:
                    os.remove(rec["image_path"])
                except Exception as e:
                    print(f"[WARNING] Could not delete {rec['image_path']}: {e}")

            # Reset UI state
            st.session_state.current_batch = []
            st.session_state.uploaded_files = []
            st.session_state.submitted = True
            st.session_state.just_submitted = True
            st.session_state.form_reset_counter += 1
            st.rerun()
