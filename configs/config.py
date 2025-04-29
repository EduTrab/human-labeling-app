import os
import streamlit as st

# Google Maps API Key
MAPS_API_KEY = st.secrets.get("google_maps_api_key", "")
if not MAPS_API_KEY:
    st.warning("⚠️ Google Maps API Key is missing; Street‑View will not work.")

# Local dirs
SAVE_DIR = "./data/saved_images/"
HUMAN_CREATED_DIR = "./data/human_created/"
TMP_UPLOAD_DIR = "./data/tmp_uploads/"

# Ensure all exist
for d in (SAVE_DIR, HUMAN_CREATED_DIR, TMP_UPLOAD_DIR):
    os.makedirs(d, exist_ok=True)
