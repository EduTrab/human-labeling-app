import streamlit as st

def render_intro():
    st.title("🖋️ Human‑Created Q&A Builder")
    st.markdown("""
      1. Pick batch size & source (Default/City/Local).  
      2. Hit **Get Images**.  
      3. For each image fill in **question**, **options A–F**, **correct answer**, optional **explanation**.  
      4. Click **Submit Batch** to save & upload.
    """)
